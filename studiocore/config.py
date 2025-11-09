# -*- coding: utf-8 -*-
"""
Configuration and defaults for StudioCore Engine.
"""

import os, json

STUDIOCORE_VERSION = "v4.3"
VERSION_LIMITS = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}

DEFAULT_CONFIG = {
    "suno_version": "v5",
    "safety": {
        "max_peak_db": -1.0,
        "max_rms_db": -14.0,
        "avoid_freq_bands_hz": [18.0, 30.0],
        "safe_octaves": [2, 3, 4, 5],
        "max_session_minutes": 20,
        "fade_in_ms": 1000,
        "fade_out_ms": 1500
    }
}

def load_config(path: str = "studio_config.json") -> dict:
    """Load studio configuration or create default one."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
