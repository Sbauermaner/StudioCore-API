# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""DynamicEmotionEngine v1.0.

This adapter normalises emotional readings into a 7-axis vector that can be
used by downstream biasing logic.  It wraps the existing high-level
``EmotionEngine`` heuristics to avoid duplicating lexicon logic while exposing
an explicit ``emotion_profile`` interface for the new dynamic genre router.
"""

from __future__ import annotations

from typing import Dict

from .logical_engines import EmotionEngine
from .emotion import TruthLovePainEngine


class DynamicEmotionEngine:
    """Bridge between heuristic emotion detection and the new 7-axis profile."""

    AXES = ("joy", "sadness", "anger", "fear", "awe", "love", "pain")

    def __init__(
        self,
        emotion_engine: EmotionEngine | None = None,
        tlp_engine: TruthLovePainEngine | None = None,
    ) -> None:
        self._emotion_engine = emotion_engine or EmotionEngine()
        self._tlp_engine = tlp_engine or TruthLovePainEngine()

    def emotion_profile(self, text: str) -> Dict[str, float]:
        """Return a normalised 7-axis emotion vector.

        Falls back to a uniform neutral vector when no signal is present to
        prevent downstream consumers from crashing.
        """

        text = text or ""
        emotion_scores = self._emotion_engine.emotion_detection(text) or {}
        tlp_scores = self._tlp_engine.analyze(text) if text.strip() else {}

        raw_vector = {
            "joy": float(emotion_scores.get("joy", 0.0)),
            "sadness": float(emotion_scores.get("sadness", 0.0)),
            "anger": float(emotion_scores.get("anger", 0.0)),
            "fear": float(emotion_scores.get("fear", 0.0)),
            "awe": float(emotion_scores.get("awe", 0.0)),
            "love": float(tlp_scores.get("love", 0.0)),
            "pain": float(tlp_scores.get("pain", 0.0)),
        }

        total = sum(raw_vector.values())
        if total <= 0:
            neutral_value = round(1.0 / len(self.AXES), 3)
            return {axis: neutral_value for axis in self.AXES}

        return {axis: round(max(score, 0.0) / total, 4) for axis, score in raw_vector.items()}


__all__ = ["DynamicEmotionEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
