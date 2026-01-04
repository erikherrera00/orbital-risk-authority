from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from typing import List, Optional
import catalog
import traceback
from fastapi import HTTPException

app = FastAPI(
    title="Orbital Risk Authority API",
    description="API for the Orbital Risk Index (ORI) prototype",
    version="0.1.0",
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


@app.get("/ori/global-summary", response_model=GlobalRiskSummary)
def get_global_risk_summary():
    """
    Prototype global ORI summary.
    Now uses approximate object counts per orbital regime and derives
    a Population Pressure Index (0–100) relative to the most crowded band.
    """
    band_definitions = [
        (
            "LEO",
            72.5,
            "High",
            "Dense operational satellite population and debris concentration.",
        ),
        (
            "MEO",
            45.2,
            "Moderate",
            "Navigation constellations dominate; moderate debris risk.",
        ),
        (
            "GEO",
            38.7,
            "Moderate",
            "Crowding in key slots, but lower debris density than LEO.",
        ),
    ]
    
    objects = catalog.load_active_catalog_cached()
    regime_counts = catalog.count_active_regimes(objects)

    label_map = {
        "Low Earth Orbit (LEO)": "LEO",
        "Medium Earth Orbit (MEO)": "MEO",
        "Geosynchronous Orbit (GEO)": "GEO",
    }

    orbit_bands = []

    for band_name, risk_score, risk_level, notes in band_definitions:
        key = band_to_key(band_name)
        obj_count = regime_counts.get(key, 0) if key else 0
        
        ppi = compute_population_pressure(obj_count)
        ppi = max(0.0, min(100.0, ppi))

        orbit_bands.append(
            GlobalRiskSummary(
                orbit_band_name=band_name,
                ori_score=float(risk_score),
                ori_level=str(risk_level),
                object_count=int(obj_count),
                population_pressure_index=float(ppi),
                notes=str(notes),
            )
        )
        

    return GlobalRiskSummary(
        data_source="CelesTrak active satellites CSV snapshot (GROUP=active, FORMAT=csv)",        
        Snapshot_time_utc=snapshot_time_utc,
        overall_risk_score=61.3,
        overall_risk_level="Elevated",
        orbit_bands=orbit_bands,
    )
except Exception as e:
    print("GLOBAL-SUMMARY ERROR:", repr(e))
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


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

