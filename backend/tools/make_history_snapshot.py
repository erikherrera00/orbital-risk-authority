from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Paths (repo-relative) ---
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
HISTORY_DIR = BACKEND_DIR / "data" / "history"
TRACKED_TOTAL_PATH = BACKEND_DIR / "data" / "tracked_total.json"

# Import backend modules by adding backend/ to sys.path
import sys
sys.path.insert(0, str(BACKEND_DIR))

import catalog  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create daily ORA history snapshot JSON")
    p.add_argument("--date", help="UTC date for filename YYYY-MM-DD (default: today UTC)", default=None)
    p.add_argument("--out", help="Output path (overrides --date)", default=None)
    p.add_argument("--force", help="Overwrite output file / bypass unchanged-data guard", action="store_true")
    return p.parse_args()


def _list_history_files() -> List[Path]:
    if not HISTORY_DIR.exists():
        return []
    return sorted([p for p in HISTORY_DIR.glob("*.json") if p.is_file()])


def read_latest_history_snapshot() -> Optional[Dict[str, Any]]:
    files = _list_history_files()
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def write_snapshot_file(snapshot: Dict[str, Any], date: Optional[str], out: Optional[str], force: bool) -> Path:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    if out:
        out_path = Path(out)
        if not out_path.is_absolute():
            out_path = (REPO_ROOT / out_path).resolve()
    else:
        if date:
            fname = f"{date}.json"
        else:
            fname = datetime.now(timezone.utc).date().isoformat() + ".json"
        out_path = HISTORY_DIR / fname

    if out_path.exists() and not force:
        raise SystemExit(
            f"❌ Refusing to overwrite existing file: {out_path}\n"
            f"   Use --force to overwrite, or choose a different --date/--out."
        )

    out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def compute_active_regimes() -> Dict[str, int]:
    objs = catalog.load_active_catalog_cached()
    counts = catalog.count_active_regimes(objs)
    # Normalize to LEO/MEO/GEO keys
    return {
        "LEO": int(counts.get("LEO", 0)),
        "MEO": int(counts.get("MEO", 0)),
        "GEO": int(counts.get("GEO", 0)),
    }


def compute_leo_zones_from_active_catalog() -> List[Any]:
    # Your catalog.py already supports LEO zones used by /ori/leo-zones-real in main.py
    # We'll reuse the same function if present; otherwise fall back cleanly.
    if hasattr(catalog, "compute_leo_zones_from_active_catalog"):
        return catalog.compute_leo_zones_from_active_catalog()  # type: ignore
    if hasattr(catalog, "leo_zones_from_active_catalog"):
        return catalog.leo_zones_from_active_catalog()  # type: ignore

    # Last-resort: mimic backend/main.py behavior by calling the same helper if you have it there
    raise SystemExit("❌ catalog.py is missing a LEO zones computation helper (expected compute_leo_zones_from_active_catalog)")


def load_tracked_totals() -> Dict[str, int]:
    if not TRACKED_TOTAL_PATH.exists():
        return {"tracked_total": 0, "active_total": 0, "inactive_total": 0}
    try:
        raw = json.loads(TRACKED_TOTAL_PATH.read_text(encoding="utf-8"))
        return {
            "tracked_total": int(raw.get("tracked_total", 0)),
            "active_total": int(raw.get("active_total", 0)),
            "inactive_total": int(raw.get("inactive_total", 0)),
        }
    except Exception:
        return {"tracked_total": 0, "active_total": 0, "inactive_total": 0}


def _load_tracked_totals_block() -> dict:
    if not TRACKED_TOTAL_PATH.exists():
        return {
            "tracked_objects_total": 0,
            "tracked_objects_on_orbit": 0,
            "payloads_on_orbit": 0,
            "debris_on_orbit": 0,
        }
    base = json.loads(TRACKED_TOTAL_PATH.read_text(encoding="utf-8"))
    return {
        "tracked_objects_total": int(base.get("tracked_objects_total", 0) or 0),
        "tracked_objects_on_orbit": int(base.get("tracked_objects_on_orbit", 0) or 0),
        "payloads_on_orbit": int(base.get("payloads_on_orbit", 0) or 0),
        "debris_on_orbit": int(base.get("debris_on_orbit", 0) or 0),
    }


def main() -> int:
    args = parse_args()

    # Underlying data timestamp from cached active CSV (this is what should gate history snapshots)
    data_snapshot_time_utc = catalog.get_snapshot_timestamp_iso()

    latest = read_latest_history_snapshot()
    if latest and latest.get("data_snapshot_time_utc") == data_snapshot_time_utc and not args.force:
        print("❌ Refusing to write: underlying data snapshot has not changed.")
        print(f"   latest data_snapshot_time_utc: {latest.get('data_snapshot_time_utc')}")
        print(f"   current data_snapshot_time_utc: {data_snapshot_time_utc}")
        print("   Use --force to write anyway.")
        return 2

    # This is the timeline timestamp for the history file itself
    snapshot_time_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    active_regimes = compute_active_regimes()
    leo_zones = compute_leo_zones_from_active_catalog()
    tracked_objects = _load_tracked_totals_block()

    snapshot: Dict[str, Any] = {
        "snapshot_time_utc": snapshot_time_utc,
        "data_snapshot_time_utc": data_snapshot_time_utc,
        "active_regimes": active_regimes,
        "leo_zones": [
            z if isinstance(z, dict) else asdict(z)
            for z in leo_zones
        ],
        "tracked_objects": tracked_objects,
    }

    out_path = write_snapshot_file(snapshot, date=args.date, out=args.out, force=args.force)

    print("✅ Wrote history snapshot:")
    print(f"   path: {out_path}")
    print(f"   snapshot_time_utc: {snapshot['snapshot_time_utc']}")
    print(f"   data_snapshot_time_utc: {snapshot['data_snapshot_time_utc']}")
    print(f"   active_regimes: {snapshot['active_regimes']}")
    print(
        "   leo_zones:", 
        ", ".join([
            f"{(z.get('zone_label') if isinstance(z, dict) else z.zone_label)}="
            f"{(z.get('count') if isinstance(z, dict) else z.count)}"
            for z in leo_zones
        ])
    )
    print(f"   tracked_objects: {snapshot['tracked_objects']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
