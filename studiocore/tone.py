# -*- coding: utf-8 -*-
"""
ToneSyncEngine — связывает эмоции с аудио- и визуальными параметрами:
цвет, движение, баланс и синхронизация.
"""
import math
from typing import Dict, Any, List

class ToneSyncEngine:
    """Создаёт аудио-визуальный профиль по эмоциональной карте текста."""

    def colors_for_primary(self, emo: Dict[str, float]) -> List[str]:
        """Возвращает 2-цветную палитру по доминирующей эмоции."""
        primary = max(emo, key=emo.get) if emo else "peace"
        cmap = {
            "joy": ["#FFD700", "#FF6B6B"],
            "sadness": ["#4169E1", "#87CEEB"],
            "anger": ["#DC143C", "#8B0000"],
            "love": ["#FF69B4", "#FF1493"],
            "peace": ["#98FB98", "#F0FFF0"],
            "epic": ["#FFA500", "#FF4500"],
            "fear": ["#6A5ACD", "#2F4F4F"]
        }
        return cmap.get(primary, ["#808080", "#A9A9A9"])

    def audio_profile(self, emo: Dict[str, float]) -> Dict[str, float]:
        """Создаёт аудио-профиль эмоций."""
        return {
            "brightness": emo.get("joy", 0) + emo.get("truth", 0),
            "warmth": emo.get("love", 0) + emo.get("peace", 0),
            "depth": emo.get("sadness", 0) + emo.get("fear", 0),
            "intensity": emo.get("anger", 0) + emo.get("epic", 0)
        }

    def visual_profile(self, emo: Dict[str, float]) -> Dict[str, Any]:
        """Формирует визуальный профиль: палитра, движение, баланс."""
        return {
            "palette": self.colors_for_primary(emo),
            "movement": (
                "sharp" if emo.get("anger", 0) > 0.3
                else ("flow" if emo.get("joy", 0) > 0.3 else "calm")
            ),
            "balance": 1.0 - (
                sum(abs(v - (sum(emo.values()) / max(1, len(emo))))
                    for v in emo.values()) / max(1, len(emo))
            )
        }

    def sync_score(self, audio: Dict[str, float], visual: Dict[str, Any]) -> float:
        """Вычисляет синхронность аудио- и визуальных параметров (0-1)."""
        a = [audio["brightness"], audio["warmth"], audio["depth"], audio["intensity"]]
        mv = visual["movement"]
        b = [
            1.0 if mv == "flow" else 0.6,
            1.0 if mv == "flow" else 0.6,
            0.8 if mv == "calm" else 0.6,
            1.0 if mv == "sharp" else 0.6
        ]
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(x * x for x in b)) or 1.0
        return max(0.0, min(1.0, dot / (na * nb)))
