from __future__ import annotations
from typing import List
from studiocore.emotion_profile import EmotionVector


class EmotionFieldEngine:
    """
    Smooths emotional spikes across lines (rolling window) to prevent chaos.
    Produces a safe emotional field used by BPM/Genre/Vocal engines.
    """

    def __init__(self, window: int = 4) -> None:
        self.window = window

    def smooth(self, vectors: List[EmotionVector]) -> List[EmotionVector]:
        if not vectors:
            return []

        smoothed = []
        for i in range(len(vectors)):
            start = max(0, i - self.window + 1)
            window = vectors[start : i + 1]
            avg = EmotionVector.average(window)
            smoothed.append(avg)
        return smoothed
