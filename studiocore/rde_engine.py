# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Rhythm × Dynamics × Emotion integration utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Sequence

from studiocore.emotion_profile import EmotionVector, EmotionAggregator
from studiocore.tlp_engine import TruthLovePainEngine  # Import required engine


@dataclass(frozen=True)
class RDESnapshot:
    """Summary describing how rhythm, dynamics and emotions align."""

    dominant_emotion: str | None
    target_bpm: float | None
    breath_sync: float | None
    target_energy: float | None
    palette: Sequence[str] | None


class RhythmDynamicsEmotionEngine:
    """Compute high-level synthesis metrics for diagnostics and UI layers."""

    def compose(
        self,
        *,
        bpm_payload: Dict[str, Any],
        breathing_profile: Dict[str, Any],
        emotion_profile: Dict[str, float],
        instrumentation_payload: Dict[str, Any],
    ) -> RDESnapshot:
        dominant = max(emotion_profile, key=emotion_profile.get) if emotion_profile else None
        palette = instrumentation_payload.get("palette")
        if isinstance(palette, dict):
            palette = palette.get("primary") or palette.get("palette")
        if isinstance(palette, str):
            palette = [palette]
        elif isinstance(palette, set):
            palette = sorted(palette)
        snapshot = RDESnapshot(
            dominant_emotion=dominant,
            target_bpm=bpm_payload.get("estimate"),
            breath_sync=breathing_profile.get("sync_score"),
            target_energy=bpm_payload.get("emotion_map", {}).get(dominant)
            if dominant
            else bpm_payload.get("target_energy"),
            palette=palette,
        )
        return snapshot

    def export_emotion_vector(self, text: str) -> EmotionVector:
        """
        Passive hook. Returns a neutral EmotionVector until dynamic mode is enabled.
        """
        return TruthLovePainEngine().export_emotion_vector(text)  # Delegate to TLP Engine

    def calc_resonance(self, text: str) -> float:
        if not text:
            return 0.0
        sentences = re.split(r"[.!?]+", text)
        density = sum(len(s.strip()) for s in sentences if s.strip())
        normalized = min(1.0, max(0.0, density / 500.0))
        return round(normalized, 4)

    def calc_fracture(self, text: str) -> float:
        if not text:
            return 0.0
        fractures = len(re.findall(r"(\.{3}|--|—)", text)) + text.count("!")
        tokens = max(1, len(re.findall(r"\b\w+\b", text)))
        return round(min(1.0, fractures / tokens), 4)

    def calc_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        tokens = re.findall(r"\b\w+\b", text.lower())
        unique = len(set(tokens))
        total = max(1, len(tokens))
        return round(min(1.0, unique / total), 4)


__all__ = ["RDESnapshot", "RhythmDynamicsEmotionEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
