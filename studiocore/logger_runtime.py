# -*- coding: utf - 8 -*-
"""
Runtime logger for StudioCore IMMORTAL.
Writes per - call diagnostics and payload traces to main / studiocore_runtime.log.
"""

from __future__ import annotations
import json
import datetime
from typing import Any, Dict


LOG_PATH = "main / studiocore_runtime.log"


def write_runtime_log(entry: Dict[str, Any]) -> None:
    """Append an entry to the master runtime log."""
    try:
        with open(LOG_PATH, "a", encoding="utf - 8") as f:
            timestamp = datetime.datetime.utcnow().isoformat()
            packed = {
                "timestamp": timestamp,
                "entry": entry,
            }
            f.write(json.dumps(packed, ensure_ascii=False) + "\n")
    except Exception:
        # Fail silently — diagnostics must not crash runtime
        pass
