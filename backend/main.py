from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

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


class OrbitBandRisk(BaseModel):
    band_name: str  # e.g. "LEO", "MEO", "GEO"
    risk_score: float  # 0-100 overall ORI band score
    risk_level: str  # e.g. "Low", "Moderate", "High", "Critical"
    object_count: int  # approximate tracked objects in this band
    population_pressure_index: float  # 0-100, derived from object_count
    notes: str


class GlobalRiskSummary(BaseModel):
    overall_risk_score: float  # 0-100
    overall_risk_level: str
    orbit_bands: List[OrbitBandRisk]
    methodology_version: str


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

    orbit_bands = []

    for band_name, risk_score, risk_level, notes in band_definitions:
        obj_count = BAND_OBJECT_COUNTS.get(band_name, 0)
        ppi = compute_population_pressure(obj_count)

        orbit_bands.append(
            OrbitBandRisk(
                band_name=band_name,
                risk_score=risk_score,
                risk_level=risk_level,
                object_count=obj_count,
                population_pressure_index=ppi,
                notes=notes,
            )
        )

    return GlobalRiskSummary(
        overall_risk_score=61.3,
        overall_risk_level="Elevated",
        orbit_bands=orbit_bands,
        methodology_version="ORI-0.2-PPI",
    )


class OperatorRisk(BaseModel):
    operator_name: str
    risk_score: float
    risk_level: str
    fleet_size: int
    notes: str


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

