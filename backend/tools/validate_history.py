#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


HISTORY_DIR = Path(__file__).resolve().parents[1] / "data" / "history"


def parse_iso_z(dt: str) -> datetime:
    # Accepts "2026-01-07T06:54:22Z"
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))


@dataclass
class Problem:
    file: str
    message: str


def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def main() -> int:
    problems: list[Problem] = []

    if not HISTORY_DIR.exists():
        problems.append(Problem(str(HISTORY_DIR), "History directory does not exist."))
        return report(problems)

    files = sorted(HISTORY_DIR.glob("*.json"))
    if not files:
        problems.append(Problem(str(HISTORY_DIR), "No history snapshots found (*.json)."))
        return report(problems)

    seen_times: dict[str, str] = {}  # snapshot_time_utc -> filename

    for p in files:
        try:
            data = read_json(p)
        except Exception as e:
            problems.append(Problem(p.name, f"Invalid JSON: {type(e).__name__}: {e}"))
            continue

        # Required: snapshot_time_utc
        st = data.get("snapshot_time_utc")
        if not isinstance(st, str) or not st.strip():
            problems.append(Problem(p.name, "Missing or invalid 'snapshot_time_utc' (must be non-empty string)."))
        else:
            # Validate ISO timestamp
            try:
                parse_iso_z(st)
            except Exception as e:
                problems.append(Problem(p.name, f"Invalid snapshot_time_utc format: {st!r} ({type(e).__name__}: {e})"))
            # Active regimes validation (required)
            ar = data.get("active_regimes")
            if not isinstance(ar, dict):
                problems.append(Problem(p.name, "Missing or invalid 'active_regimes' (must be an object)."))
            else:
                for k in ("LEO", "MEO", "GEO"):
                    if k not in ar:
                        problems.append(Problem(p.name, f"active_regimes missing key {k!r}."))
                    else:
                        v = ar.get(k)
                        if not is_number(v) or int(v) < 0:
                            problems.append(Problem(p.name, f"active_regimes[{k}] must be a non-negative number."))
      
            # Prevent duplicates
            if st in seen_times:
                problems.append(
                    Problem(
                        p.name,
                        f"Duplicate snapshot_time_utc {st!r} (already used in {seen_times[st]}).",
                    )
                )
            else:
                seen_times[st] = p.name

        # LEO zones validation (supports either "leo_zones" or "zones")
        zones = data.get("leo_zones", None)
        if zones is None:
            zones = data.get("zones", None)

        if zones is None:
            problems.append(Problem(p.name, "Missing 'leo_zones' (preferred) or 'zones' array."))
            continue

        if not isinstance(zones, list) or len(zones) == 0:
            problems.append(Problem(p.name, "'leo_zones'/'zones' must be a non-empty list."))
            continue

        required_zone_keys = {"zone_label", "count", "zpi"}
        labels_seen: set[str] = set()

        for i, z in enumerate(zones):
            if not isinstance(z, dict):
                problems.append(Problem(p.name, f"zones[{i}] must be an object/dict."))
                continue

            # Required keys
            missing = [k for k in required_zone_keys if k not in z]
            if missing:
                problems.append(Problem(p.name, f"zones[{i}] missing keys: {missing}"))
                continue

            label = z.get("zone_label")
            if not isinstance(label, str) or not label.strip():
                problems.append(Problem(p.name, f"zones[{i}].zone_label must be a non-empty string."))
            else:
                if label in labels_seen:
                    problems.append(Problem(p.name, f"Duplicate zone_label {label!r} in zones array."))
                labels_seen.add(label)

            count = z.get("count")
            zpi = z.get("zpi")

            if not is_number(count):
                problems.append(Problem(p.name, f"zones[{i}].count must be a number (got {type(count).__name__})."))

            if not is_number(zpi):
                problems.append(Problem(p.name, f"zones[{i}].zpi must be a number (got {type(zpi).__name__})."))
            else:
                # Soft bounds check
                if float(zpi) < 0 or float(zpi) > 100:
                    problems.append(Problem(p.name, f"zones[{i}].zpi out of range 0..100 (got {zpi})."))

        # Optional: encourage consistent labels
        # (not fatal) — leave as informational if you want later.

    return report(problems)


def report(problems: list[Problem]) -> int:
    if not problems:
        print(f"✅ History validation OK ({HISTORY_DIR})")
        return 0

    print("❌ History validation FAILED")
    for pr in problems:
        print(f" - {pr.file}: {pr.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

