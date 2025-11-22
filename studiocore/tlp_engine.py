# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Public wrapper for the Truth × Love × Pain engine."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from studiocore.emotion_profile import EmotionVector, EmotionAggregator

from .emotion import TruthLovePainEngine as _TruthLovePainEngine


class TruthLovePainEngine(_TruthLovePainEngine):
    """Adds convenience helpers on top of the base TLP engine."""

    def describe(self, text: str) -> Dict[str, Any]:
        profile = self.analyze(text)
        ordered: List[Tuple[str, float]] = sorted(profile.items(), key=lambda item: item[1], reverse=True)
        dominant = ordered[0][0] if ordered else "truth"
        profile["dominant_axis"] = dominant
        profile["balance"] = round((profile.get("truth", 0.0) + profile.get("love", 0.0)) - profile.get("pain", 0.0), 3)
        return profile

    def truth_score(self, text: str) -> float:
        return float(self.analyze(text).get("truth", 0.0))

    def love_score(self, text: str) -> float:
        return float(self.analyze(text).get("love", 0.0))

    def pain_score(self, text: str) -> float:
        return float(self.analyze(text).get("pain", 0.0))

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Calculates dynamic Valence and Arousal based on TLP scores.
        """
        profile = self.analyze(text)
        truth = profile.get("truth", 0.0)
        love = profile.get("love", 0.0)
        pain = profile.get("pain", 0.0)
        weight = profile.get("conscious_frequency", 0.5)

        # Valence (V): Positivity/Negativity (Love - Pain). Clamped to [-1, 1].
        valence = love - pain

        # Arousal (A): Intensity/Energy (Average of all axes). Clamped to [0, 1].
        arousal = (love + pain + truth) / 3.0

        return EmotionVector(
            truth=truth,
            love=love,
            pain=pain,
            valence=valence,
            arousal=arousal,
            weight=weight,
            extra={},
        )


__all__ = ["TruthLovePainEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
