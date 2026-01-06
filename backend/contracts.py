# backend/contracts.py
from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------
# Meta / Version
# ---------------------------

class VersionInfo(BaseModel):
    version: str = Field(..., description="Semantic version of the API")
    commit: str = Field(..., description="Short git commit hash (or build id)")
    status: str = Field(..., description="Deployment status label, e.g. stable/dev")


# ---------------------------
# ORI / Global Summary
# ---------------------------

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
    orbit_bands: List[OrbitBandSummary]


# ---------------------------
# Operators
# ---------------------------

class OperatorRisk(BaseModel):
    operator_name: str
    orbit_band: str
    fleet_size: int
    fleet_pressure_index: float = Field(..., description="0–100 scale")
    notes: str


class OperatorRiskList(BaseModel):
    data_source: str
    snapshot_time_utc: str
    operators: List[OperatorRisk]


# ---------------------------
# LEO Zones / Congestion
# ---------------------------

class LEOZoneRisk(BaseModel):
    zone_label: str
    altitude_range_km: str
    estimated_object_count: int
    zone_pressure_index: float = Field(..., description="0–100 scale")
    notes: str


class LEOZonesResponse(BaseModel):
    data_source: str
    snapshot_time_utc: str
    zones: List[LEOZoneRisk]


# ---------------------------
# Active LEO / Active Regimes (Real data)
# ---------------------------

class ActiveLEOSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active_count: int


class ActiveRegimes(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int


# ---------------------------
# Docs / Methodology
# ---------------------------

class Methodology(BaseModel):
    version: str
    definitions: Dict[str, str]
    notes: List[str]


__all__ = [
    "VersionInfo",
    "OrbitBandSummary",
    "GlobalRiskSummary",
    "OperatorRisk",
    "OperatorRiskList",
    "LEOZoneRisk",
    "LEOZonesResponse",
    "ActiveLEOSummary",
    "ActiveRegimes",
    "Methodology",
]

