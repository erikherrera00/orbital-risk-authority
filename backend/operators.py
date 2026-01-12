# backend/operators.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

WATCHLIST_PATH = Path(__file__).parent / "data" / "operators_watchlist.json"


def load_watchlist() -> dict[str, Any]:
    """
    Load the operator watchlist from JSON.

    Returns a dict like:
    {
        "operators": [ ... ]
    }
    """
    if not WATCHLIST_PATH.exists():
        return {"operators": []}

    return json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))

