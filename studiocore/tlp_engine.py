# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Public wrapper for the Truth × Love × Pain engine."""

from __future__ import annotations

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

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return EmotionVector(
            truth=0.0,
            love=0.0,
            pain=0.0,
            valence=0.0,
            arousal=0.0,
            weight=1.0,
        )


__all__ = ["TruthLovePainEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
