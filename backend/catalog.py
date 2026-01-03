from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import math
from typing import Tuple

DATA_FILE = Path(__file__).parent / "data" / "active-satellites.csv"


@dataclass
class CatalogRow:
    object_name: str
    mean_motion: float
    eccentricity: float


def load_active_catalog() -> List[CatalogRow]:
    """
    Load the active satellites snapshot from CelesTrak CSV.

    Expects backend/data/active-satellites.csv to exist.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Active satellites file not found: {DATA_FILE}")

    rows: List[CatalogRow] = []

    with DATA_FILE.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            try:
                name = raw.get("OBJECT_NAME", "").strip()
                mm = float(raw.get("MEAN_MOTION", "0") or 0.0)
                ecc = float(raw.get("ECCENTRICITY", "0") or 0.0)
            except (ValueError, TypeError):
                continue

            if not name:
                continue

            rows.append(
                CatalogRow(
                    object_name=name,
                    mean_motion=mm,
                    eccentricity=ecc,
                )
            )

    return rows


def count_active_leo(objects: List[CatalogRow]) -> int:
    """
    Count active LEO satellites using a simple, published rule:

    LEO if:
    - orbital period <= 128 minutes
    - MEAN_MOTION >= 11.25 rev/day
    - ECCENTRICITY < 0.25
    """
    count = 0
    for obj in objects:
        if obj.mean_motion >= 11.25 and obj.eccentricity < 0.25:
            count += 1
    return count


def get_snapshot_timestamp_iso() -> str:
    """
    Return the last-modified time of the snapshot file in ISO 8601 UTC.
    """
    if not DATA_FILE.exists():
        return "unknown"

    mtime = DATA_FILE.stat().st_mtime
    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

# Earth constants (km, km^3/s^2)
EARTH_RADIUS_KM = 6378.137
MU_EARTH_KM3_S2 = 398600.4418


def mean_motion_to_altitude_km(mean_motion_rev_per_day: float) -> float | None:
    """
    Convert mean motion (rev/day) to approximate circular-orbit altitude (km).

    Steps:
    - n [rad/s] = mean_motion_rev_per_day * 2π / 86400
    - a [km] = (μ / n^2)^(1/3)
    - altitude = a - Earth_radius
    """
    if mean_motion_rev_per_day <= 0:
        return None

    n_rad_s = mean_motion_rev_per_day * 2.0 * math.pi / 86400.0
    if n_rad_s <= 0:
        return None

    a_km = (MU_EARTH_KM3_S2 / (n_rad_s**2)) ** (1.0 / 3.0)
    alt_km = a_km - EARTH_RADIUS_KM

    # sanity bounds
    if alt_km < 0 or alt_km > 100000:
        return None

    return alt_km


def leo_zone_for_altitude(alt_km: float) -> Tuple[str, str]:
    """
    Return (zone_label, altitude_range_string).
    """
    if 300 <= alt_km < 500:
        return ("LEO-1", "300–500 km")
    if 500 <= alt_km < 800:
        return ("LEO-2", "500–800 km")
    if 800 <= alt_km < 1200:
        return ("LEO-3", "800–1200 km")
    if 1200 <= alt_km < 2000:
        return ("LEO-4", "1200–2000 km")

    return ("OTHER", "outside defined LEO zones")


def count_active_leo_zones(objects: List[CatalogRow]) -> Dict[str, Dict[str, int]]:
    """
    Count active satellites by LEO sub-band zone.
    Returns:
      {
        "LEO-1": {"count": 123, "range": "300–500 km"},
        ...
      }
    Only counts objects that pass the same LEO filter used for active-leo:
      mean_motion >= 11.25 and ecc < 0.25
    """
    zones: Dict[str, Dict[str, int]] = {}

    for obj in objects:
        if not (obj.mean_motion >= 11.25 and obj.eccentricity < 0.25):
            continue

        alt = mean_motion_to_altitude_km(obj.mean_motion)
        if alt is None:
            continue

        label, rng = leo_zone_for_altitude(alt)
        if label == "OTHER":
            continue

        if label not in zones:
            zones[label] = {"count": 0, "range": rng}

        zones[label]["count"] += 1

    return zones
