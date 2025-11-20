# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


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

        # --- Значения по умолчанию ---
        truth = float(tlp.get("truth", 0.0))
        love = float(tlp.get("love", 0.0))
        pain = float(tlp.get("pain", 0.0))

        # Основные эмоциональные коэффициенты
        hate = float(emo.get("anger", 0.0))
        sadness = float(emo.get("sadness", 0.0))
        joy = float(emo.get("joy", 0.0))
        awe = float(emo.get("awe", 0.0))
        fear = float(emo.get("fear", 0.0))

        # --- Цветовые базовые правила (упрощённая версия) ---
        # Боль / Печаль → синий → тёмный серый
        if pain > 0.6 or sadness > 0.6:
            return ColorResolution(
                colors=["#0A1F44", "#2F4F4F", "#000000"],
                source="tlp_rules",
            )

        # Гнев / Ненависть → чёрный → красный → чёрный
        if hate > 0.7:
            return ColorResolution(
                colors=["#000000", "#8B0000", "#000000"],
                source="emotion_map",
            )

        # Любовь → красный → розовый → белый
        if love > 0.6 or joy > 0.6:
            return ColorResolution(
                colors=["#FF0000", "#FF69B4", "#FFFFFF"],
                source="tlp_rules",
            )

        # Awe / mystic → бирюза → серебро → тень
        if awe > 0.6:
            return ColorResolution(
                colors=["#008080", "#C0C0C0", "#2F4F4F"],
                source="emotion_map",
            )

        # Fear → тёмно-фиолетовый → чёрный
        if fear > 0.6:
            return ColorResolution(
                colors=["#2A0038", "#000000"],
                source="emotion_map",
            )

        # --- Fallback (если эмоция непонятна) ---
        return ColorResolution(
            colors=["#222222", "#555555"],
            source="fallback",
        )

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
