# -*- coding: utf-8 -*-
"""
LyricalEmotionEngine v1.0

Объединяет:
- RDE (Raw Dramatic Emotion: joy/sadness/anger/fear/epic/peace/hope/etc.)
- TLP (Truth/Love/Pain)
- PoeticDensity (плотность образов)
- EmotionalGradient (как растёт/спадает эмоция по тексту)

Отдаёт сводный эмоциональный профиль для лирики
и используется доменом LYRICAL/COMEDY в жанровом анализе.
"""

from __future__ import annotations
from typing import Dict, Any


class LyricalEmotionEngine:
    """Комбайн для вычисления осевой эмоции лирики."""

    def __init__(self) -> None:
        # Коэффициенты можно калибровать позже
        self.weights = {
            "rde": 0.35,
            "tlp": 0.35,
            "poetic_density": 0.20,
            "emotional_gradient": 0.10,
        }

    def from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        analysis — объединённый результат работы других движков:
        {
          "rde": {"joy": ..., "sadness": ..., ...},
          "tlp": {"truth": ..., "love": ..., "pain": ...},
          "poetic_density": 0.0-1.0,
          "emotional_gradient": 0.0-1.0,
        }
        """
        rde = analysis.get("rde", {})
        tlp = analysis.get("tlp", {})
        pd = float(analysis.get("poetic_density", 0.0))
        grad = float(analysis.get("emotional_gradient", 0.0))

        # Примитивный агрегат — можно усложнить позже
        rde_scalar = float(rde.get("epic", 0.0) + rde.get("hope", 0.0) +
                           rde.get("pain", 0.0) + rde.get("sadness", 0.0)) / 4.0 or 0.0
        tlp_scalar = float(tlp.get("truth", 0.0) * 0.4 +
                           tlp.get("love", 0.0) * 0.3 +
                           tlp.get("pain", 0.0) * 0.3)

        final_score = (
            rde_scalar * self.weights["rde"] +
            tlp_scalar * self.weights["tlp"] +
            pd * self.weights["poetic_density"] +
            grad * self.weights["emotional_gradient"]
        )

        return {
            "rde_scalar": rde_scalar,
            "tlp_scalar": tlp_scalar,
            "poetic_density": pd,
            "emotional_gradient": grad,
            "lyrical_emotion_score": max(0.0, min(1.0, final_score)),
        }
