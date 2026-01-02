from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


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

