from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Orbital Risk Authority API",
    description="API for the Orbital Risk Index (ORI) prototype",
    version="0.1.0",
)


class OrbitBandRisk(BaseModel):
    band_name: str  # e.g. "LEO", "MEO", "GEO"
    risk_score: float  # 0-100
    risk_level: str  # e.g. "Low", "Moderate", "High", "Critical"
    notes: str


class GlobalRiskSummary(BaseModel):
    overall_risk_score: float  # 0-100
    overall_risk_level: str
    orbit_bands: List[OrbitBandRisk]
    methodology_version: str


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
            notes="Dense operational satellite population and debris concentration."
        ),
        OrbitBandRisk(
            band_name="MEO",
            risk_score=45.2,
            risk_level="Moderate",
            notes="Navigation constellations dominate; moderate debris risk."
        ),
        OrbitBandRisk(
            band_name="GEO",
            risk_score=38.7,
            risk_level="Moderate",
            notes="Crowding in key slots, but lower debris density than LEO."
        ),
    ]

    return GlobalRiskSummary(
        overall_risk_score=61.3,
        overall_risk_level="Elevated",
        orbit_bands=orbit_bands,
        methodology_version="ORI-0.1-MOCK",
    )

