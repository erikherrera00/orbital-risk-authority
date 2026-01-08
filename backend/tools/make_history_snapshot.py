#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import math
import sys

# Allow "import catalog" from repo root execution
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "backend"))

import catalog  # type: ignore


EARTH_RADIUS_KM = 6378.137
MU_EARTH_KM3_S2 = 398600.4418


# --- LEO zone definitions (km altitude)
ZONES: List[Tuple[str, int, int]] = [
    ("LEO-1", 300, 500),
    ("LEO-2", 500, 800),
    ("LEO-3", 800, 1200),
    ("LEO-4", 1200, 2000),
]


@dataclass
class ZoneRow:
    zone_label: str
    count: int
    zpi: float


def mean_motion_to_altitude_km(mean_motion_rev_per_day: float) -> float | None:
    """
    Convert mean motion (rev/day) to approximate altitude (km) using
    circular-orbit approximation:
      n = mean_motion * 2π / 86400 (rad/s)
      a = (mu / n^2)^(1/3)
      altitude = a - EarthRadius
    Returns None if mean motion invalid.
    """
    try:
        mm = float(mean_motion_rev_per_day)
        if mm <= 0:
            return None
        n = mm * 2.0 * math.pi / 86400.0  # rad/s
        a = (MU_EARTH_KM3_S2 / (n * n)) ** (1.0 / 3.0)  # km
        alt = a - EARTH_RADIUS_KM
        return float(alt)
    except Exception:
        return None


def compute_leo_zones_from_active_catalog() -> List[ZoneRow]:
    """
    Load active catalog rows (cached) and bin objects into LEO altitude zones.
    ZPI normalized within LEO by max zone count.
    """
    objs = catalog.load_active_catalog_cached()

    counts: Dict[str, int] = {z[0]: 0 for z in ZONES}

    for o in objs:
        alt = mean_motion_to_altitude_km(getattr(o, "mean_motion", 0.0))
        if alt is None:
            continue

        # We only consider objects that fall in our defined LEO zone ranges
        for label, lo, hi in ZONES:
            if alt >= lo and alt < hi:
                counts[label] += 1
                break

    max_count = max(counts.values()) if counts else 0

    rows: List[ZoneRow] = []
    for label, lo, hi in ZONES:
        c = int(counts.get(label, 0))
        zpi = 0.0 if max_count == 0 else (100.0 * c / max_count)
        rows.append(ZoneRow(zone_label=label, count=c, zpi=round(zpi, 1)))

    return rows


def compute_active_regimes() -> Dict[str, int]:
    """
    Uses your existing catalog.count_active_regimes() to compute
    LEO/MEO/GEO counts.
    """
    objs = catalog.load_active_catalog_cached()
    regime_counts = catalog.count_active_regimes(objs)

    # Your API already uses LEO/MEO/GEO. Normalize keys defensively.
    out = {
        "LEO": int(regime_counts.get("LEO", 0)),
        "MEO": int(regime_counts.get("MEO", 0)),
        "GEO": int(regime_counts.get("GEO", 0)),
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ORA history snapshot JSON.")
    parser.add_argument(
        "--date",
        default=None,
        help="Output filename date in YYYY-MM-DD (default: UTC today).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path. Default: backend/data/history/YYYY-MM-DD.json",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    args = parser.parse_args()

    # Pick date for filename
    utc_now = datetime.now(timezone.utc)
    date_str = args.date or utc_now.strftime("%Y-%m-%d")

    # Determine output path
    history_dir = REPO_ROOT / "backend" / "data" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    out_path = Path(args.out) if args.out else (history_dir / f"{date_str}.json")

    if out_path.exists() and not args.force:
        print(f"❌ Refusing to overwrite existing file: {out_path}")
        print("   Use --force to overwrite, or choose a different --date/--out.")
        return 2

    # Snapshot time comes from the cached CSV file timestamp
    snapshot_time_utc = catalog.get_snapshot_timestamp_iso()

    active_regimes = compute_active_regimes()
    leo_zones = compute_leo_zones_from_active_catalog()

    payload = {
        "snapshot_time_utc": snapshot_time_utc,
        "active_regimes": active_regimes,
        "leo_zones": [asdict(z) for z in leo_zones],
    }

    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("✅ Wrote history snapshot:")
    print(f"   path: {out_path}")
    print(f"   snapshot_time_utc: {snapshot_time_utc}")
    print(f"   active_regimes: {active_regimes}")
    print("   leo_zones:", ", ".join([f"{z.zone_label}={z.count}" for z in leo_zones]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

