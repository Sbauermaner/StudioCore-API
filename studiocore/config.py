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


# ============================================================================
# Neutral / Low-Emotion defaults (MASTER-PATCH v3)
# ============================================================================
NEUTRAL_MOOD = "neutral, calm, observational"
NEUTRAL_COLOR_WAVE = ["#4A5568", "#718096"]  # холодный серый / стальной
LOW_EMOTION_BPM_MIN = 58
LOW_EMOTION_BPM_MAX = 70

# Пороговые значения для определения "низкоэмоционального" текста
LOW_EMOTION_TLP_PAIN_MAX = 0.10
LOW_EMOTION_TLP_TRUTH_MIN = 0.50
LOW_EMOTION_RDE_RESONANCE_MAX = 0.20
LOW_EMOTION_RDE_FRACTURE_MAX = 0.15
LOW_EMOTION_RDE_ENTROPY_MAX = 0.35


def load_config_weights(path: str = "config_weights.json") -> dict:
    """
    Load external genre weights and keywords configuration from JSON file.
    
    Args:
        path: Path to the JSON configuration file
        
    Returns:
        Dictionary with genre_weights, keywords, and thresholds
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    import json
    from pathlib import Path
    
    config_path = Path(path)
    if not config_path.exists():
        # Return empty dict if file doesn't exist (fallback to hardcoded values)
        logger.warning(f"Config weights file not found: {path}, using hardcoded values")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded config weights from {path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config weights file {path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading config weights from {path}: {e}")
        return {}


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

# === Imported from core_v6 (MAXI FIX v7 — Part 3) ===
KEYWORD_MAP = [
    ("melancholy_dark", ["готик", "darkwave", "мрак", "тьма", "темн"]),
    ("rage_extreme", ["убей", "уничтож", "ненавиж", "смерт", "rage"]),
    ("love_soft", ["люб", "поцел", "неж", "ласк", "тепл"]),
    ("joy_bright", ["солн", "чудо", "радост", "улыб", "свет"]),
    ("confidence", ["бит", "улиц", "флоу", "правда", "силой", "hiphop", "рэп"]),
]

FORCED_GENRES = {
    "melancholy_dark": "gothic adaptive darkwave",
    "rage_extreme": "ideological extreme adaptive rage",
    "love_soft": "lyrical love adaptive classic",
    "joy_bright": "pop adaptive light",
    "confidence": "hiphop adaptive",
}

# ============================================================================
# Algorithm Weighting Factors (MASTER-PATCH v7 - Externalized Magic Numbers)
# ============================================================================
ALGORITHM_WEIGHTS = {
    # TLP weighting factors
    "tlp_truth_weight": 0.4,
    "tlp_love_weight": 0.3,
    "tlp_pain_weight": 0.5,
    
    # Road narrative scoring weights
    "road_narrative_cf_weight": 0.25,
    "road_narrative_sorrow_weight": 0.25,
    "road_narrative_determination_weight": 0.20,
    
    # RDE smoothing factors for low-emotion texts
    "rde_resonance_smoothing": 0.4,
    "rde_fracture_smoothing": 0.3,
    "rde_entropy_smoothing": 0.7,
    
    # Emotion mode thresholds
    "rage_anger_threshold": 0.22,
    "rage_tension_threshold": 0.25,
    "epic_threshold": 0.35,
    
    # Section intensity defaults
    "default_section_intensity": 0.5,
    "default_confidence": 0.5,
}

# ============================================================================
# Genre Weights (V7 Extended Configuration - Externalized Genre Weighting)
# ============================================================================
GENRE_WEIGHTS = {
    "semantic_aggression": {
        "anger_multiplier": 0.4,
        "conflict_base": 1.0
    },
    "power_vector": {
        "bpm_divisor": 180.0,
        "intensity_multiplier": 0.3
    },
    "edge_factor": {
        "anger_multiplier": 0.6,
        "tone_intense_boost": 0.3,
        "tone_balanced_boost": 0.15
    },
    "rhythm_density": {
        "bpm_divisor": 200.0
    },
    "narrative_pressure": {
        "fracture_multiplier": 0.1
    },
    "poetic_density": {
        "imagery_multiplier": 2.2,
        "punctuation_multiplier": 0.4,
        "long_line_multiplier": 0.3,
        "motif_multiplier": 0.1
    },
    "swing_ratio": {
        "command_boost": 0.25,
        "poly_variance_divisor": 40.0,
        "keyword_weight": 0.6,
        "variance_weight": 0.4
    },
    "jazz_complexity": {
        "palette_weight": 0.35,
        "modal_weight": 0.35,
        "text_weight": 0.3
    },
    "electronic_pressure": {
        "palette_weight": 0.5,
        "text_weight": 0.3,
        "bpm_weight": 0.2
    },
    "comedy_factor": {
        "hits_weight": 0.6,
        "blob_weight": 0.15,
        "laughter_weight": 0.1
    },
    "gothic_factor": {
        "minor_lumen_multiplier": 0.1
    },
    "dramatic_weight": {
        "tension_weight": 0.5,
        "gradient_weight": 0.3,
        "pressure_weight": 0.2
    }
}

# ============================================================================
# Keyword Lists (MASTER-PATCH v7 - Externalized Hardcoded Lists)
# ============================================================================
ROAD_NARRATIVE_KEYWORDS = {
    "road": [
        "road", "back road", "backroad", "highway", "flyover state",
        "interstate", "dust", "truck stop"
    ],
    "death": [
        "bury me", "bury me on a back road", "grave", "no name on the stone",
        "my grave", "when i die", "reaper", "fate", "karma"
    ],
    "weight": [
        "chains", "gold", "weight", "carry that weight",
        "bridges i burned", "bridges i burned up", "tank full of gas"
    ],
}

# FOLK_BALLAD_KEYWORDS - Updated to match JSON structure (V7)
FOLK_BALLAD_KEYWORDS = {
    "ru": [
        "тропа", "дорог", "ветер", "луна", "ноч", "земл", "память",
        "возвращал", "шептал", "тихо", "тум", "природ", "пешком", "мимо",
        "поле", "степь", "село", "деревня", "печь", "предки"
    ],
    "en": [
        "trail", "field", "moon", "earth", "old roads", "road", "village",
        "wind", "grass", "legends", "sagas", "ancestors", "shepherd", "blizzard"
    ]
}

# Legacy flat list format (for backward compatibility)
FOLK_BALLAD_KEYWORDS_FLAT = [
    # Russian keywords
    "тропа", "тропе", "поле", "поля", "луна", "луной", "земля", "землёй",
    "старые дороги", "дорога", "дороге", "дорогами", "степь", "посевы",
    "отчий дом", "печь", "село", "деревня", "огни села", "ветер", "трава",
    "трава под ногами", "легенды", "саги", "предки", "пастух", "вьюга",
    # English equivalents
    "trail", "field", "moon", "earth", "old roads", "road", "village", "wind",
    "grass", "legends", "sagas", "ancestors", "shepherd", "blizzard"
]

FOLK_BALLAD_KEYWORDS_LEGACY = [
    'тропа', 'дорог', 'ветер', 'луна', 'ноч', 'земл', 'память',
    'возвращал', 'шептал', 'тихо', 'тум', 'природ', 'пешком', 'мимо'
]

# ============================================================================
# Extended Keyword Lists (V7 Extended Configuration)
# ============================================================================
# Note: ROAD_NARRATIVE_KEYWORDS already defined above with same structure
# The user's JSON matches the existing structure, so we keep it as is.

# Extended keyword categories
URBAN_ELECTRONIC_KEYWORDS = [
    "rap", "drill", "trap", "808", "club", "EDM", "techno", "rave",
    "bass", "beat", "MC", "рэп", "бит", "клуб", "техно", "хаус",
    "бас", "электро", "диджей"
]

POETIC_KEYWORDS = [
    "lyric", "poem", "ode", "sonnet", "haiku", "ballad", "serenade",
    "lullaby", "lyrical", "серд", "люб", "луна", "звезд", "тиши",
    "ветер", "лепест", "шеп", "сон", "dream", "soul", "moon", "star",
    "ocean", "tear", "rose"
]

COMEDY_KEYWORDS = [
    "comedy", "comic", "funny", "humor", "humour", "parody", "satire",
    "joke", "lol", "lmao", "haha", "rofl", "юмор", "юморист", "шутк",
    "смешн", "ирони", "сарказ", "парод", "анекдот", "комед", "угар"
]

GOTHIC_KEYWORDS = [
    "gothic", "готик", "dark", "тень", "мрак", "ноч", "grave", "cathedral"
]

# ============================================================================
# Genre Detection Thresholds (V7 Extended Configuration)
# ============================================================================
GENRE_THRESHOLDS = {
    "road_narrative_score_min": 0.45,
    "folk_ballad_confidence_min": 0.5,
    "rage_mode_anger_min": 0.22,
    "rage_mode_tension_min": 0.25,
    "epic_mode_min": 0.35
}

# ============================================================================
# External Configuration Loader (V7 - Auto-load from JSON)
# ============================================================================
# Try to load external configuration, fallback to hardcoded values
_external_config = load_config_weights("config_weights.json")

if _external_config and _external_config.get("meta", {}).get("auto_load"):
    # Override hardcoded values with external config if available
    if "genre_weights" in _external_config:
        GENRE_WEIGHTS.update(_external_config["genre_weights"])
    if "thresholds" in _external_config:
        GENRE_THRESHOLDS.update(_external_config["thresholds"])
    # Keywords are kept in separate variables, can be accessed via external config
    logger.info("External configuration loaded and merged with hardcoded values")

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
