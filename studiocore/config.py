# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
StudioCore Configuration Loader
Совместим с ядром v4.3.1-adaptive и выше.
"""

import os
import json
from dataclasses import dataclass

# Canonical StudioCore version. Legacy labels kept for backward compatibility only.
STUDIOCORE_VERSION = "v6.4-maxi"
# Deprecated: retained for older tooling that still expects the adaptive label.
# STUDIOCORE_VERSION_LEGACY = "v4.3.1-adaptive"

VERSION_LIMITS = {
    "v3": 200,
    "v3.5": 200,
    "v4": 500,
    "v5": 1000
}

class ConfigAccessor(dict):
    """Dict helper that also exposes attribute access for config keys."""

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:  # pragma: no cover - attribute passthrough
            raise AttributeError(item) from exc


DEFAULT_CONFIG = ConfigAccessor(
    {
        "suno_version": "v5",
        "MAX_INPUT_LENGTH": 16000,
        "EMOTION_MIN_SIGNAL": 0.05,
        "EMOTION_HIGH_SIGNAL": 0.65,
        "TLP_CLAMP_MIN": 0.0,
        "TLP_CLAMP_MAX": 1.0,
        "AGGRESSION_KEYWORDS": (
            "убей",
            "убивать",
            "расстрелять",
            "зарежь",
            "уничтожь",
            "kill",
            "murder",
            "slaughter",
            "execute",
        ),
        "FALLBACK_NEUTRAL_TEXT": "Конфликт описывается в тексте, но мы выбираем говорить о примирении и выходе из насилия.",
        "FALLBACK_NEUTRAL_STYLE": "cinematic narrative",
        "ERROR_INVALID_INPUT_TYPE": "invalid_input_type",
        "ERROR_EMPTY_INPUT": "empty_input",
        "safety": {
            "max_peak_db": -1.0,        # ограничение на пиковый уровень
            "max_rms_db": -14.0,        # средний RMS-уровень
            "avoid_freq_bands_hz": [18.0, 30.0],  # суб-НЧ диапазон, исключаемый из анализа
            "safe_octaves": [2, 3, 4, 5],
            "max_session_minutes": 20,
            "fade_in_ms": 1000,
            "fade_out_ms": 1500,
        },
        "safety_rns": {                 # модуль Resonance–Nervous–Safety
            "min_resonance_hz": 20.0,
            "max_resonance_hz": 20000.0,
            "safe_energy_threshold": 0.85,
        },
        "integrity": {                  # структура IntegrityScanEngine
            "max_repetition_ratio": 0.35,
            "min_unique_lines": 3,
            "enable_auto_repair": True,
        },
        # Fallback messages, avoids hardcoding inside core
        "FALLBACK_STYLE": "cinematic narrative",
        "FALLBACK_KEY": "C minor",
        "FALLBACK_BPM": 85,
        "FALLBACK_VISUAL": "soft light, calm atmosphere",
        "FALLBACK_NARRATIVE": "introspection → tension → release",
        "FALLBACK_STRUCTURE": "intro-verse-chorus-outro",
        "FALLBACK_EMOTION": "neutral",
    }
)


@dataclass
class StudioCoreConfig:
    # Soft input protection
    MAX_INPUT_LENGTH: int = 16000
    # Emotion & TLP thresholds
    EMOTION_MIN_SIGNAL: float = 0.05
    EMOTION_HIGH_SIGNAL: float = 0.65
    TLP_CLAMP_MIN: float = 0.0
    TLP_CLAMP_MAX: float = 1.0

    # Aggression / violence lexicon (for filters, not for prompts)
    AGGRESSION_KEYWORDS: tuple[str, ...] = (
        "убей",
        "убивать",
        "расстрелять",
        "зарежь",
        "уничтожь",
        "kill",
        "murder",
        "slaughter",
        "execute",
    )

    # Neutral fallback phrases (instead of aggressive ones)
    FALLBACK_NEUTRAL_TEXT: str = "Конфликт описывается в тексте, но мы выбираем говорить о примирении и выходе из насилия."
    FALLBACK_NEUTRAL_STYLE: str = "cinematic narrative"

    # Error messages
    ERROR_INVALID_INPUT_TYPE: str = "invalid_input_type"
    ERROR_EMPTY_INPUT: str = "empty_input"
    # Fallback messages, avoids hardcoding inside core
    FALLBACK_STYLE: str = "cinematic narrative"
    FALLBACK_KEY: str = "C minor"
    FALLBACK_BPM: int = 85
    FALLBACK_VISUAL: str = "soft light, calm atmosphere"
    FALLBACK_NARRATIVE: str = "introspection → tension → release"
    FALLBACK_STRUCTURE: str = "intro-verse-chorus-outro"
    FALLBACK_EMOTION: str = "neutral"


def load_config(path: str = "studio_config.json") -> dict:
    """
    Загружает конфигурацию StudioCore или создаёт новую.
    При наличии старого файла — обновляет недостающие поля.
    """
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 🔄 автообновление при старом конфиге
    updated = False
    for k, v in DEFAULT_CONFIG.items():
        if k not in data:
            data[k] = v
            updated = True
        elif isinstance(v, dict):
            for sk, sv in v.items():
                if sk not in data[k]:
                    data[k][sk] = sv
                    updated = True

    if updated:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return data

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
