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
}


EMOTION_COLOR_MAP: Dict[str, List[str]] = {
    "truth": [KEY_COLOR_PALETTE["indigo"], "#6C1BB1"],
    "love": ["#FF0000", "#FF69B4", "#FFFFFF"],
    "pain": ["#0A1F44", "#2F4F4F", "#000000"],
    "joy": [KEY_COLOR_PALETTE["golden"], "#FFD54F", "#FFF8E1"],
    "sadness": ["#0A1F44", KEY_COLOR_PALETTE["blue"], "#2F4F4F"],
    "anger": ["#8B0000", KEY_COLOR_PALETTE["crimson"], "#000000"],
    "fear": ["#2A0038", "#000000"],
    "peace": ["#F5F5F5", "#E0F7FA"],
    "epic": [KEY_COLOR_PALETTE["violet"], "#4B0082"],
    "awe": ["#008080", "#C0C0C0", "#2F4F4F"],
    "neutral": ["#B0BEC5", "#ECEFF1"],
    "hope": ["#9ACD32", "#C5E1A5"],
    "calm": [KEY_COLOR_PALETTE["turquoise"], "#A7FFEB"],
    "nostalgia": ["#D8BFD8", "#E6E6FA"],
    "irony": ["#800080", "#C71585"],
    "conflict": [KEY_COLOR_PALETTE["orange-red"], KEY_COLOR_PALETTE["amber"]],
    "joy_bright": ["#FFD700", "#FFF59D"],
    "love_soft": ["#FFC0CB", "#FFE4E1"],
    "love_deep": ["#C2185B", "#880E4F"],
    "disappointment": ["#708090", "#A9A9A9"],
    "melancholy": ["#4B6C9C", "#2F4F4F"],
    "rage": ["#B22222", "#8B0000"],
    "rage_extreme": ["#8B0000", "#4A0000"],
    "aggression": ["#C62828", "#B71C1C"],
    "anxiety": ["#6A5ACD", "#2F4F4F"],
    "wonder": ["#7DF9FF", KEY_COLOR_PALETTE["turquoise"]],
    "gothic_dark": ["#1B1B2F", "#000000"],
    "dark_poetic": ["#2C1A2E", "#3F2A44"],
    "dark_romantic": ["#4A192C", "#2C0F1A"],
    "hiphop_conflict": [KEY_COLOR_PALETTE["orange-red"], KEY_COLOR_PALETTE["green"]],
    "street_power": ["#8B4513", "#FF8C00"],
    "dark": ["#111111", "#2F2F2F"],
    "melancholic": ["#4B5D67", "#243447"],
    "epic_cluster": [KEY_COLOR_PALETTE["violet"], KEY_COLOR_PALETTE["magenta"]],
    "hope_cluster": ["#9ACD32", KEY_COLOR_PALETTE["turquoise"]],
    "neutral_cluster": ["#B0BEC5", "#CFD8DC"],
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
