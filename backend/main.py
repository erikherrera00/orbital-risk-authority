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
    TEMP: mocked data until we integrate real orbital datasets.
    This is just to power the first dashboard + show structure.
    """
        orbit_bands = [
        OrbitBandRisk(
            band_name="LEO",
            risk_score=72.5,
            risk_level="High",
            object_count=6000,  # placeholder; to be replaced with real data
            population_pressure_index=85.0,  # 0–100; placeholder
            notes="Dense operational satellite population and debris concentration.",
        ),
        OrbitBandRisk(
            band_name="MEO",
            risk_score=45.2,
            risk_level="Moderate",
            object_count=1500,  # placeholder
            population_pressure_index=55.0,  # placeholder
            notes="Navigation constellations dominate; moderate debris risk.",
        ),
        OrbitBandRisk(
            band_name="GEO",
            risk_score=38.7,
            risk_level="Moderate",
            object_count=500,  # placeholder
            population_pressure_index=40.0,  # placeholder
            notes="Crowding in key slots, but lower debris density than LEO.",
        ),
    ]


    return GlobalRiskSummary(
        overall_risk_score=61.3,
        overall_risk_level="Elevated",
        orbit_bands=orbit_bands,
        methodology_version="ORI-0.1-MOCK",
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

