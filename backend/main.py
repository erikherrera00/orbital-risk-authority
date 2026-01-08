from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import List, Optional
import catalog
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import os
from contracts import TrackedObjectsSummary
from fastapi import Query
from contracts import ActiveRegimesHistory, ActiveRegimesHistoryPoint

from contracts import (
    VersionInfo,
    OrbitBandSummary,
    GlobalRiskSummary,
    OperatorRisk,
    OperatorRiskList,
    LEOZoneRisk,
    LEOZonesResponse,
    ActiveLEOSummary,
    ActiveRegimes,
    Methodology,
    TotalRegimes,
    LEOZonesHistory,
    LEOZonesHistoryPoint,
    LEOZoneHistoryRow,
)


app = FastAPI(
    title="Orbital Risk Authority API",
    description="API for the Orbital Risk Index (ORI) prototype",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://erikherrera00.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS: allow your GitHub Pages site to call this API
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Replace this with your actual GitHub Pages URL:
    "https://erikherrera00.github.io",
    "https://erikherrera00.github.io/orbital-risk-authority",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Approximate tracked object counts per band (prototype values, to be refined)
BAND_OBJECT_COUNTS = {
    "LEO": 36000,
    "MEO": 4000,
    "GEO": 3000,
}

MAX_OBJECTS = max(BAND_OBJECT_COUNTS.values())


def compute_population_pressure(count: int) -> float:
    """
    Simple 0–100 population pressure index based on relative object counts.
    100 corresponds to the most crowded band in this mapping.
    """
    if MAX_OBJECTS <= 0:
        return 0.0
    return round(min(100.0, (count / MAX_OBJECTS) * 100.0), 1)




def compute_fleet_pressure(fleet_size: int, max_size: int) -> float:
    if max_size <= 0:
        return 0.0
    return round(min(100.0, (fleet_size / max_size) * 100.0), 1)


def band_to_key(name: str) -> str | None:
    n = name.lower()
    if "leo" in n: return "LEO"
    if "meo" in n: return "MEO"
    if "geo" in n: return "GEO"
    return None


class VersionInfo(BaseModel):
    version: str
    commit: str
    status: str


class OrbitBandRisk(BaseModel):
    band_name: str  # e.g. "LEO", "MEO", "GEO"
    risk_score: float  # 0-100 overall ORI band score
    risk_level: str  # e.g. "Low", "Moderate", "High", "Critical"
    object_count: int  # approximate tracked objects in this band
    population_pressure_index: float  # 0-100, derived from object_count
    notes: str


class OrbitBandSummary(BaseModel):
    orbit_band: str
    ori_score: float
    ori_level: str
    object_count: int
    population_pressure_index: float
    notes: str


class GlobalRiskSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    overall_risk_score: float 
    overall_risk_level: str
    orbit_bands: list[OrbitBandSummary]


class OperatorRisk(BaseModel):
    operator_name: str
    orbit_band: str
    fleet_size: int
    fleet_pressure_index: float  # 0-100 scale
    notes: str


class LEOZoneRisk(BaseModel):
    zone_label: str
    altitude_range_km: str
    estimated_object_count: int
    zone_pressure_index: float  # 0-100
    notes: str


class ActiveLEOSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active_count: int


class LEOZoneRealSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    zones: List[LEOZoneRisk]


BAND_DEFINITIONS = [
    ("Low Earth Orbit (LEO)", 72.5, "Elevated", "High density + conjunction growth; disposal compliance varies."),
    ("Medium Earth Orbit (MEO)", 48.0, "Moderate", "Moderate density; critical navigation assets; long persistence."),
    ("Geosynchronous Orbit (GEO)", 41.0, "Moderate", "Stable slots but high-value assets; end-of-life graveyard practices."),
]

def band_to_key(name: str):
    n = name.lower()
    if "leo" in n: return "LEO"
    if "meo" in n: return "MEO"
    if "geo" in n: return "GEO"
    return None


@app.get("/debug/history-files", tags=["debug"])
def debug_history_files():
    history_dir = Path(__file__).parent / "data" / "history"
    files = sorted(history_dir.glob("*.json"))
    out = []
    for p in files:
        try:
            raw = p.read_text(encoding="utf-8")
            data = json.loads(raw)
            out.append({
                "file": p.name,
                "bytes": len(raw),
                "snapshot_time_utc": data.get("snapshot_time_utc"),
                "keys": sorted(list(data.keys())),
            })
        except Exception as e:
            out.append({
                "file": p.name,
                "error": f"{type(e).__name__}: {e}",
            })
    return {"count": len(files), "files": out}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


@app.get("/ori/history/leo-zones", response_model=LEOZonesHistory, tags=["ori"])
def ori_history_leo_zones(limit: int = Query(30, ge=1, le=365)):
    snapshots = _load_history_files()
    if not snapshots:
        return LEOZonesHistory(
            data_source="ORA history snapshots (backend/data/history/*.json)",
            points=[],
            notes="No history snapshots found yet. Add files under backend/data/history/.",
        )

    snaps = snapshots[-limit:]

    points: list[LEOZonesHistoryPoint] = []

    # Track previous snapshot's zone values by label so we can compute deltas
    prev_map: dict[str, dict[str, float]] | None = None

    for s in snaps:
        t = str(s.get("snapshot_time_utc", "unknown"))
        zones_raw = s.get("leo_zones", []) or []

        # Build current map
        curr_map: dict[str, dict[str, float]] = {}
        for z in zones_raw:
            label = str(z.get("zone_label", "")).strip()
            if not label:
                continue
            curr_map[label] = {
                "count": float(z.get("count", 0)),
                "zpi": float(z.get("zpi", 0.0)),
            }

        # Create stable ordering (LEO-1, LEO-2, ...)
        labels = sorted(curr_map.keys())

        zone_rows: list[LEOZoneHistoryRow] = []
        for label in labels:
            c_count = int(curr_map[label]["count"])
            c_zpi = float(curr_map[label]["zpi"])

            if prev_map and label in prev_map:
                d_count = c_count - int(prev_map[label]["count"])
                d_zpi = c_zpi - float(prev_map[label]["zpi"])
            else:
                d_count = 0
                d_zpi = 0.0

            zone_rows.append(
                LEOZoneHistoryRow(
                    zone_label=label,
                    count=c_count,
                    zpi=c_zpi,
                    delta_count=d_count,
                    delta_zpi=float(round(d_zpi, 3)),
                )
            )

        points.append(
            LEOZonesHistoryPoint(
                snapshot_time_utc=t,
                zones=zone_rows,
            )
        )

        prev_map = curr_map

    return LEOZonesHistory(
        data_source="ORA history snapshots (backend/data/history/*.json)",
        points=points,
        notes="Zone deltas are computed relative to the immediately previous snapshot in the returned series.",
    )


@app.get("/ori/all-regimes", response_model=TotalRegimes, tags=["ori"])
def ori_all_regimes():
    # Dummy placeholder to lock routing + contract first
    snapshot_time = catalog.get_snapshot_timestamp_iso()
    return TotalRegimes(
        data_source="Placeholder (wiring in total objects next)",
        snapshot_time_utc=snapshot_time,
        leo_total=0,
        meo_total=0,
        geo_total=0,
    )


HISTORY_DIR = Path(__file__).parent / "data" / "history"

def _load_history_files() -> list[dict]:
    """
    Load all history snapshot JSON files from backend/data/history/*.json
    """
    if not HISTORY_DIR.exists():
        return []

    files = sorted(HISTORY_DIR.glob("*.json"))  # filename order (YYYY-MM-DD.json works great)
    snapshots: list[dict] = []
    for fp in files:
        try:
            payload = json.loads(fp.read_text(encoding="utf-8"))
            # minimal validation
            if "snapshot_time_utc" in payload and "active_regimes" in payload:
                snapshots.append(payload)
        except Exception:
            # skip bad files (never kill the API for one bad snapshot)
            continue
    return snapshots


@app.get("/ori/history/active-regimes", response_model=ActiveRegimesHistory, tags=["ori"])
def ori_history_active_regimes(limit: int = Query(30, ge=1, le=365)):
    snapshots = _load_history_files()
    if not snapshots:
        return ActiveRegimesHistory(
            data_source="ORA history snapshots (backend/data/history/*.json)",
            points=[],
            notes="No history snapshots found yet. Add files under backend/data/history/.",
        )

    # take most recent `limit` snapshots
    snaps = snapshots[-limit:]

    points: list[ActiveRegimesHistoryPoint] = []
    prev = None

    for s in snaps:
        t = str(s.get("snapshot_time_utc", "unknown"))
        ar = s.get("active_regimes", {}) or {}
        leo = int(ar.get("LEO", 0))
        meo = int(ar.get("MEO", 0))
        geo = int(ar.get("GEO", 0))

        if prev is None:
            d_leo = d_meo = d_geo = 0
        else:
            d_leo = leo - prev["leo"]
            d_meo = meo - prev["meo"]
            d_geo = geo - prev["geo"]

        points.append(
            ActiveRegimesHistoryPoint(
                snapshot_time_utc=t,
                leo_active=leo,
                meo_active=meo,
                geo_active=geo,
                delta_leo=d_leo,
                delta_meo=d_meo,
                delta_geo=d_geo,
            )
        )

        prev = {"leo": leo, "meo": meo, "geo": geo}

    return ActiveRegimesHistory(
        data_source="ORA history snapshots (backend/data/history/*.json)",
        points=points,
        notes="Deltas are computed relative to the immediately previous snapshot in the returned series.",
    )


@app.get("/", tags=["system"])
def root():
    return {
        "service": "Orbital Risk Authority API",
        "status": "ok",
        "endpoints": ["/health", "/ori/global-summary"],
    }


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "service": "Orbital Risk Authority API"}


@app.get("/ori/global-summary", response_model=GlobalRiskSummary, tags=["ori"])
def get_global_risk_summary():
    
    band_definitions = [
    ("Low Earth Orbit (LEO)", 72.5, "Elevated", "High density + conjunction growth; disposal compliance varies."),
    ("Medium Earth Orbit (MEO)", 48.0, "Moderate", "Moderate density; critical navigation assets; long persistence."),
    ("Geosynchronous Orbit (GEO)", 41.0, "Moderate", "Stable slots but high-value assets; end-of-life graveyard practices."),
    ]

    def band_to_key(name: str):
        n = name.lower()
        if "leo" in n:
            return "LEO"
        if "meo" in n:
            return "MEO"
        if "geo" in n:
            return "GEO"
        return None
    
    objects = catalog.load_active_catalog_cached()
    regime_counts = catalog.count_active_regimes(objects)
    snapshot_time_utc = catalog.get_snapshot_timestamp_iso()

    orbit_bands: list[OrbitBandSummary] = []
    
    for band_name, risk_score, risk_level, notes in band_definitions:
        key = band_to_key(band_name)
        obj_count = regime_counts.get(key, 0) if key else 0
        
        ppi = compute_population_pressure(obj_count)
        ppi = max(0.0, min(100.0, float(ppi)))

        orbit_bands.append(
            OrbitBandSummary(
                orbit_band=band_name,
                ori_score=float(risk_score),
                ori_level=str(risk_level),
                object_count=int(obj_count),
                population_pressure_index=float(ppi),
                notes=str(notes),
            )
        )
        

    return GlobalRiskSummary(
        data_source="CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",        
        snapshot_time_utc=snapshot_time_utc,
        overall_risk_score=61.3,
        overall_risk_level="Elevated",
        orbit_bands=orbit_bands,
    )


class ActiveRegimeSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int


class ActiveRegimes(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int


class OperatorRisk(BaseModel):
    operator_name: str
    risk_score: float
    risk_level: str
    fleet_size: int
    notes: str


class ActiveRegimeSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int


class OraVersion(BaseModel):
    api_version: str
    ori_version: str
    prototype_stage: str


@app.get("/ori/active-regimes", response_model=ActiveRegimes, tags=["ori"])
def get_active_regimes():
    objects = catalog.load_active_catalog_cached()
    snapshot_time = catalog.get_snapshot_timestamp_iso()
    counts = catalog.count_active_regimes(objects)

    return ActiveRegimeSummary(
        data_source="CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",
        snapshot_time_utc=snapshot_time,
        leo_active=counts["LEO"],
        meo_active=counts["MEO"],
        geo_active=counts["GEO"],
    )


@app.get("/ori/active-leo", response_model=ActiveLEOSummary, tags=["ori"])
def get_active_leo_summary():
    """
    Real-data snapshot: count of active LEO satellites based on CelesTrak CSV.
    """
    objects = catalog.load_active_catalog()
    leo_count = catalog.count_active_leo(objects)
    snapshot_time = catalog.get_snapshot_timestamp_iso()

    return ActiveLEOSummary(
        data_source="CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",
        snapshot_time_utc=snapshot_time,
        leo_active_count=leo_count,
    )


@app.get("/ori/activate-leo", include_in_schema=False)
def activate_leo_redirect():
    return RedirectResponse(
        url="/ori/active-leo",
        status_code=307
    )


@app.get("/docs/methodology", response_model=Methodology, tags=["docs"])
def docs_methodology():
    return Methodology(
        version="METH-0.5",
        definitions={
            "Data source": "CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",
            "Snapshot time": "Derived from local cached snapshot file timestamp (UTC ISO 8601).",
            "LEO/MEO/GEO regimes": "Regimes computed from mean motion / eccentricity rules in catalog module.",
            "PPI": "Population Pressure Index: normalized 0–100 based on active object count by regime.",
            "ORI": "Framework-driven risk score (not predictive) incorporating PPI and qualitative risk notes.",
        },
        notes=[
            "ORA is a public prototype and does not provide conjunction prediction or collision probability.",
            "All metrics are snapshot-based and may lag real-time conditions.",
            "Definitions may evolve; contract endpoints will maintain backward compatibility.",
        ],
    )


@app.get("/ori/operators", response_model=List[OperatorRisk], tags=["ori"])
def get_operator_risk():
    """
    Prototype operator-level ORI scores.
    Currently mocked; in future versions, this will be derived from
    fleet exposure, behavior, disposal performance, and transparency.
    """
    return [
        OperatorRisk(
            operator_name="MockSat Constellations Inc.",
            risk_score=78.0,
            risk_level="High",
            fleet_size=1200,
            notes="Large LEO constellation with aggressive deployment pace and mixed disposal performance.",
        ),
        OperatorRisk(
            operator_name="GeoComms Global",
            risk_score=42.5,
            risk_level="Moderate",
            fleet_size=50,
            notes="Primarily GEO assets with standard graveyard orbit disposal practices.",
        ),
    ]


@app.get("/version", response_model=OraVersion)
def get_version():
    return OraVersion(
        api_version="0.3.0",
        ori_version="ORI-0.3",
        prototype_stage="Public prototype – PPI, OFPI, and LEO sub-band congestion"
    )


APP_VERSION = os.getenv("ORA_VERSION", "0.5.0")
APP_COMMIT = os.getenv("ORA_COMMIT", "dev")

@app.get("/meta/version", response_model=VersionInfo, tags=["meta"])
def meta_version():
    return VersionInfo(
        version=APP_VERSION,
        commit=APP_COMMIT,
        status="stable",
    )


def compute_zone_pressure(count: int, max_count: int) -> float:
    if max_count <= 0:
        return 0.0
    return round(min(100.0, (count / max_count) * 100.0), 1)


@app.get("/ori/operators", response_model=List[OperatorRisk], tags=["ori"])
def get_operator_fleet_pressure():
    """
    Prototype operator-level Orbital Risk Index extension.
    Provides a simple Fleet Pressure Index (0–100) based on relative
    fleet dominance in orbit.
    """
    operator_fleets = [
        (
            "LEO Broadband Constellation A",
            "LEO",
            5500,
            "Large-scale LEO broadband constellation with aggressive deployment pace.",
        ),
        (
            "LEO Imaging & IoT Constellation B",
            "LEO",
            900,
            "Mixed imaging / IoT constellation with moderate fleet size.",
        ),
        (
            "Global Navigation System C",
            "MEO",
            180,
            "Core navigation constellation deployed in MEO.",
        ),
        (
            "GEO Comms Operator D",
            "GEO",
            80,
            "Commercial GEO communications operator with long-lived assets.",
        ),
    ]

    max_fleet = max(o[2] for o in operator_fleets)

    results = []

    for name, band, size, notes in operator_fleets:
        fpi = compute_fleet_pressure(size, max_fleet)

        results.append(
            OperatorRisk(
                operator_name=name,
                orbit_band=band,
                fleet_size=size,
                fleet_pressure_index=fpi,
                notes=notes,
            )
        )


@app.get("/ori/leo-zones-real", response_model=LEOZoneRealSummary, tags=["ori"])
def get_leo_zone_risk_real():
    """
    Real-data snapshot: active LEO satellites binned into altitude zones.
    Uses mean motion -> altitude approximation for near-circular orbits.
    """
    objects = catalog.load_active_catalog()
    snapshot_time = catalog.get_snapshot_timestamp_iso()
    zone_counts = catalog.count_active_leo_zones(objects)

    # Build list of zones in order
    ordered_labels = ["LEO-1", "LEO-2", "LEO-3", "LEO-4"]
    zones = []
    max_count = max((zone_counts.get(z, {}).get("count", 0) for z in ordered_labels), default=0)

    for label in ordered_labels:
        info = zone_counts.get(label, {"count": 0, "range": ""})
        count = info["count"]
        rng = info["range"]

        zpi = 0.0
        if max_count > 0:
            zpi = round(min(100.0, (count / max_count) * 100.0), 1)

        zones.append(
            LEOZoneRisk(
                zone_label=label,
                altitude_range_km=rng,
                estimated_object_count=count,
                zone_pressure_index=zpi,
                notes="Real-data binning from CelesTrak snapshot (approx altitude from mean motion).",
            )
        )

    return LEOZoneRealSummary(
        data_source="CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",
        snapshot_time_utc=snapshot_time,
        zones=zones,
    )


@app.get("/ori/active-regimes", response_model=ActiveRegimeSummary, tags=["ori"])
def get_active_regimes():
    objects = catalog.load_active_catalog()
    snapshot_time = catalog.get_snapshot_timestamp_iso()
    counts = catalog.count_active_regimes(objects)

    return ActiveRegimeSummary(
        data_source="CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",
        snapshot_time_utc=snapshot_time,
        leo_active=counts["LEO"],
        meo_active=counts["MEO"],
        geo_active=counts["GEO"],
    )


TRACKED_TOTALS_FILE = Path(__file__).parent / "data" / "tracked_totals.json"

@app.get("/ori/tracked-objects", response_model=TrackedObjectsSummary, tags=["ori"])
def ori_tracked_objects():
    if not TRACKED_TOTALS_FILE.exists():
        raise HTTPException(status_code=500, detail="tracked_totals.json missing on server")

    payload = json.loads(TRACKED_TOTALS_FILE.read_text(encoding="utf-8"))
    active = len(catalog.load_active_catalog_cached())

    total = int(payload.get("tracked_objects_total", 0))
    snapshot_time = payload.get("snapshot_time_utc", catalog.get_snapshot_timestamp_iso())

    return TrackedObjectsSummary(
        data_source=payload.get("data_source", "Tracked object totals snapshot"),
        snapshot_time_utc=snapshot_time,
        tracked_objects_total=total,
        active_satellites=active,
        inactive_or_debris_estimate=max(0, total - active),
        notes=payload.get("notes", "Macro totals; not used for regime classification without elements."),
    )


@app.get("/ori/leo-zones", response_model=List[LEOZoneRisk], tags=["ori"])
def get_leo_zone_risk():
    """
    Prototype breakdown of LEO congestion by sub-bands.
    Values are illustrative but directionally aligned with known clustering behavior.
    """

    zones = [
        ("LEO-1", "300–500 km", 14000, "Dense cluster region with significant constellation presence."),
        ("LEO-2", "500–800 km", 16000, "Highest object concentration region in LEO."),
        ("LEO-3", "800–1200 km", 6000, "Fewer spacecraft but slower orbital decay."),
    ]

    max_objects = max(z[2] for z in zones)

    results = []

    for label, alt, count, notes in zones:
        zpi = compute_zone_pressure(count, max_objects)

        results.append(
            LEOZoneRisk(
                zone_label=label,
                altitude_range_km=alt,
                estimated_object_count=count,
                zone_pressure_index=zpi,
                notes=notes,
            )
        )

    return results

