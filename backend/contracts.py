# backend/contracts.py
from __future__ import annotations

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ---------------------------
# Meta / Version
# ---------------------------

class VersionInfo(BaseModel):
    version: str = Field(..., description="Semantic version of the API")
    commit: str = Field(..., description="Short git commit hash (or build id)")
    status: str = Field(..., description="Deployment status label, e.g. stable/dev")


RiskLevel = Literal["Low", "Moderate", "Elevated", "High", "Critical"]


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


class TotalRegimes(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_total: int
    meo_total: int
    geo_total: int


class TrackedObjectsSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str

    # SATCAT boxscore totals (real once update_tracked_totals.py runs)
    tracked_objects_total: int
    tracked_objects_on_orbit: int
    payloads_on_orbit: int
    debris_on_orbit: int

    # CelesTrak active catalog (real)
    active_satellites: int

    # Simple derived estimate (optional but useful for narrative)
    inactive_or_debris_estimate: int

    # Optional notes (keep flexible)
    notes: str | None = None


class ActiveRegimesHistoryPoint(BaseModel):
    snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int
    delta_leo: int
    delta_meo: int
    delta_geo: int


class ActiveRegimes(BaseModel):
    data_source: str
    snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int


class ActiveRegimesHistory(BaseModel):
    data_source: str
    points: list[ActiveRegimesHistoryPoint]
    notes: str


class ActiveRegimesDelta(BaseModel):
    data_source: str
    current_snapshot_time_utc: str
    previous_snapshot_time_utc: str
    leo_active: int
    meo_active: int
    geo_active: int
    delta_leo: int
    delta_meo: int
    delta_geo: int
    notes: str


class LEOZoneHistoryRow(BaseModel):
    zone_label: str
    count: int
    zpi: float
    delta_count: int
    delta_zpi: float


class LEOZonesHistoryPoint(BaseModel):
    snapshot_time_utc: str
    zones: list[LEOZoneHistoryRow]


class LEOZonesHistory(BaseModel):
    data_source: str
    points: list[LEOZonesHistoryPoint]
    notes: str


class OperatorWatchlistEntry(BaseModel):
    operator_slug: str
    operator_name: str
    primary_orbit: str  # e.g., "LEO", "MEO", "GEO"
    fleet_size: int
    disposal_posture: Optional[str] = None  # "Good", "Mixed", "Unknown"
    notes: Optional[str] = None


class OperatorCard(BaseModel):
    operator_slug: str
    operator_name: str
    primary_orbit: str
    fleet_size: int
    risk_flags: List[str]
    ora_posture: str
    notes: str

    # Framework metrics (prototype, not predictive)
    fleet_pressure_index: float  # 0–100
    risk_level: Literal["Low", "Moderate", "Elevated", "High", "Systemic"]

    disposal_posture: Optional[str] = None
    notes: Optional[str] = None


class OperatorCards(BaseModel):
    data_source: str
    snapshot_time_utc: str
    operators: List[OperatorCard]


class OperatorCardsResponse(BaseModel):
    data_source: str
    snapshot_time_utc: Optional[str] = None
    count: int
    card: List[OperatorCard]


class OperatorDetailCard(BaseModel):
    operator_slug: str
    operator_name: str
    primary_orbit: str
    fleet_size: int
    fleet_pressure_index: float
    risk_level: str
    disposal_posture: Optional[str] = None
    notes: Optional[str] = None


class TrackedObjectsSummary(BaseModel):
    data_source: str
    snapshot_time_utc: str
    tracked_objects_total: int
    active_satellites: int
    inactive_or_debris_estimate: int
    notes: Optional[str] = None

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


class LEOZoneHistoryRow(BaseModel):
    zone_label: str
    count: int
    zpi: float
    delta_count: int = 0
    delta_zpi: float = 0.0

class LEOZonesHistoryPoint(BaseModel):
    snapshot_time_utc: str
    zones: List[LEOZoneHistoryRow]

class LEOZonesHistory(BaseModel):
    data_source: str
    points: List[LEOZonesHistoryPoint]
    notes: Optional[str] = None


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

