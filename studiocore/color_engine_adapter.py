# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


KEY_COLOR_PALETTE: Dict[str, str] = {
    "red": "#FF0000",
    "orange-red": "#FF4500",
    "golden": "#DAA520",
    "amber": "#FFBF00",
    "yellow": "#FFFF00",
    "green": "#2E8B57",
    "turquoise": "#40E0D0",
    "blue": "#1E90FF",
    "indigo": "#4B0082",
    "violet": "#8A2BE2",
    "magenta": "#FF00FF",
    "crimson": "#DC143C",
    "white": "#FFFFFF",
}


EMOTION_COLOR_MAP: Dict[str, List[str]] = {
    # --- Rhythmic/Structural States (New) ---
    "calm_flow": ["#9FD3FF"],
    "warm_pulse": ["#F5B56B"],
    "cold_pulse": ["#4D7EA8"],
    "frantic": ["#FF4E4E"],
    "trembling": ["#A8A6FF"],
    "escalating": ["#E06C75"],
    "descending": ["#7A6D6F"],
    "pressure": ["#332F2F"],
    "static_tension": ["#645A5A"],
    "breathless": ["#8BB9E3"],
    # --- Deep Pain Spectrum (New) ---
    "deep_pain": ["#2A0000"],
    "phantom_pain": ["#3A1A1A"],
    "burning_pain": ["#660000"],
    "soul_pain": ["#400021"],
    "silent_pain": ["#2E1A27"],
    "explosive_pain": ["#7F0000"],
    "collapsing_pain": ["#1A0000"],
    # --- Deep Love Spectrum (New) ---
    "infinite_love": ["#FF6FA8"],
    "healing_love": ["#FF9CCB"],
    "maternal_love": ["#FFB7DA"],
    "radiant_love": ["#FFD1E8"],
    "longing_love": ["#E88AB7"],
    "gentle_love": ["#FFCEDA"],
    "unconditional_love": ["#FFA3C4"],
    # --- Deep Truth Spectrum (New) ---
    "clear_truth": ["#AEE3FF"],
    "cold_truth": ["#6DA8C8"],
    "sharp_truth": ["#3A5E73"],
    "brutal_honesty": ["#1A3F56"],
    "revelation": ["#8FE1FF"],
    "righteous_truth": ["#0099CC"],
    # --- Core Emotions (Overridden with new values) ---
    "truth": [KEY_COLOR_PALETTE["indigo"], "#6C1BB1", "#5B3FA8"],
    "love": ["#FF7AA2"],
    "pain": [KEY_COLOR_PALETTE["crimson"], "#2F1B25", "#0A1F44"],
    "joy": ["#FFD93D"],
    "sadness": ["#4A6FA5"],
    "anger": ["#FF3232", "#8B0000"],
    "fear": ["#002F63"],
    # --- Detailed Negative Emotions (New/Overridden) ---
    "sorrow": ["#3E5C82"],
    "loneliness": ["#475674"],
    "grief": ["#2D3A55"],
    "regret": ["#55637A"],
    "guilt": ["#4C4F6B"],
    "shame": ["#735D78"],
    "anxiety": ["#8CA6DB"],
    "panic": ["#001A33"],
    "disgust": ["#4E6D39"],
    "aversion": ["#5E7D4C"],
    "confusion": ["#8EA3B7"],
    "frustration": ["#C75146"],
    "rage": ["#990000"],
    "bitterness": ["#733131"],
    "jealousy": ["#629A49"],
    "envy": ["#6BAD49"],
    "betrayal": ["#764C6D"],
    "resentment": ["#923D3D"],
    "resolve": ["#DDB27F"],
    "determination": ["#C78E4A"],
    # --- Detailed Positive Emotions (New/Overridden) ---
    "happiness": ["#FFE97F"],
    "delight": ["#FFF2A6"],
    "serenity": ["#A8D8FF"],
    "calm": ["#8FC1E3"],
    "hope": ["#C7FF8F"],
    "trust": ["#8FE6C2"],
    "affection": ["#FF9EBF"],
    "compassion": ["#FFADC7"],
    "warmth": ["#F7B267"],
    "admiration": ["#DDB3F8"],
    "relief": ["#B8E986"],
    # --- Base/Cluster Emotions (Retained original/V6.4) ---
    "peace": [KEY_COLOR_PALETTE["turquoise"], "#E0F7FA", KEY_COLOR_PALETTE["white"]],
    "epic": [KEY_COLOR_PALETTE["violet"], "#4B0082", KEY_COLOR_PALETTE["magenta"]],
    "awe": [KEY_COLOR_PALETTE["turquoise"], "#7DF9FF", "#C0C0C0"],
    "neutral": [KEY_COLOR_PALETTE["white"], "#B0BEC5", "#ECEFF1"],
    "nostalgia": ["#D8BFD8", "#E6E6FA", "#C3B1E1"],
    "irony": ["#800080", KEY_COLOR_PALETTE["magenta"], "#C71585"],
    "conflict": [KEY_COLOR_PALETTE["orange-red"], KEY_COLOR_PALETTE["amber"], KEY_COLOR_PALETTE["crimson"]],
    "joy_bright": ["#FFD700", KEY_COLOR_PALETTE["yellow"], "#FFF59D"],
    "love_soft": ["#FFC0CB", "#FFB6C1", "#FFE4E1"],
    "love_deep": ["#C2185B", "#880E4F", KEY_COLOR_PALETTE["crimson"]],
    "disappointment": ["#708090", "#A9A9A9", "#6C6C6C"],
    "melancholy": ["#596E94"],
    "rage_extreme": ["#8B0000", "#4A0000", "#2A0000"],
    "aggression": ["#8B0000", KEY_COLOR_PALETTE["crimson"], KEY_COLOR_PALETTE["orange-red"]],
    "wonder": ["#7DF9FF", KEY_COLOR_PALETTE["turquoise"], "#E0FFFF"],
    "gothic_dark": ["#2C1A2E", "#1B1B2F", "#000000"],
    "dark_poetic": ["#2C1A2E", "#3F2A44", "#1B1B2F"],
    "dark_romantic": ["#4A192C", "#2C0F1A", "#6A1B3F"],
    "hiphop_conflict": ["#6C7E42", KEY_COLOR_PALETTE["orange-red"], KEY_COLOR_PALETTE["amber"]],
    "street_power": ["#8B4513", "#FF8C00", KEY_COLOR_PALETTE["amber"]],
    "dark": ["#111111", "#2F2F2F", "#0B0B0B"],
    "melancholic": ["#4B5D67", "#243447", "#1A2633"],
    "epic_cluster": [KEY_COLOR_PALETTE["violet"], "#4B0082", KEY_COLOR_PALETTE["magenta"]],
    "hope_cluster": ["#9ACD32", KEY_COLOR_PALETTE["turquoise"], "#C5E1A5"],
    "neutral_cluster": ["#B0BEC5", "#CFD8DC", "#ECEFF1"],
}


def _normalize_emotion_key(name: str | None) -> str:
    return (name or "").strip().lower()


def get_emotion_colors(emotion: str, *, default: List[str] | None = None) -> List[str]:
    key = _normalize_emotion_key(emotion)
    if key in EMOTION_COLOR_MAP:
        return EMOTION_COLOR_MAP[key]
    return default or EMOTION_COLOR_MAP["neutral"]


@dataclass
class ColorResolution:
    colors: List[str]
    source: str  # "tlp_rules" / "emotion_map" / "fallback"


class ColorEngineAdapter:
    """
    Лёгкая адаптация ColorEngine к результату анализа:
    — читает result["tlp"] и result["emotion"]
    — создает color_wave: список hex-цветов
    — не вмешивается в внутреннюю работу ColorEngine

    Это прослойка: безопасна, не хранит состояния, не ломает пайплайн.
    """

    def resolve_color_wave(self, result: Dict[str, Any]) -> ColorResolution:
        tlp = result.get("tlp", {}) or {}
        emo = result.get("emotion", {}) or {}
        scores: Dict[str, float] = {
            "truth": float(tlp.get("truth", 0.0)),
            "love": float(tlp.get("love", 0.0)),
            "pain": float(tlp.get("pain", 0.0)),
        }

        for name, value in emo.items():
            try:
                scores[_normalize_emotion_key(name)] = float(value)
            except (TypeError, ValueError):
                continue

        filtered_scores = {k: v for k, v in scores.items() if v is not None}
        if not filtered_scores:
            return ColorResolution(colors=get_emotion_colors("neutral"), source="fallback")

        dominant = max(filtered_scores, key=filtered_scores.get)
        return ColorResolution(
            colors=get_emotion_colors(dominant),
            source="emotion_map",
        )

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
