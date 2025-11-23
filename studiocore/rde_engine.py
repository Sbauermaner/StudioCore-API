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


class ResonanceDynamicsEngine:
    # keep existing code but add:

    def calc_resonance(self, text: str) -> float:
        """Псевдо-резонанс: повторяемость ключевых слов и ритмических паттернов."""
        low = text.lower()
        repeats = 0
        tokens = low.split()
        seen: Dict[str, int] = {}
        for t in tokens:
            seen[t] = seen.get(t, 0) + 1
        for cnt in seen.values():
            if cnt > 1:
                repeats += cnt - 1

        resonance = min(1.0, repeats / max(len(tokens), 1))
        return round(resonance, 4)

    def calc_fracture(self, text: str) -> float:
        """Грубая фрактурность: скачки длины строк и пунктуации."""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if len(lines) < 2:
            return 0.1

        lens = [len(ln) for ln in lines]
        avg = sum(lens) / len(lens)
        variance = sum((l - avg) ** 2 for l in lens) / len(lens)
        fracture = min(1.0, variance / max(avg**2, 1.0))
        return round(fracture, 4)

    def calc_entropy(self, text: str) -> float:
        """Символная энтропия (очень упрощённая)."""
        low = text.lower()
        length = max(len(low), 1)
        freq: Dict[str, int] = {}
        for ch in low:
            freq[ch] = freq.get(ch, 0) + 1
        entropy = 0.0
        for cnt in freq.values():
            p = cnt / length
            import math
            entropy -= p * (0 if p <= 0 else math.log2(p) if p > 0 else 0)  # используем логарифм вместо bit_length
        entropy = min(1.0, max(0.0, entropy / 10.0))
        return round(entropy, 4)


__all__ = ["RDESnapshot", "RhythmDynamicsEmotionEngine", "ResonanceDynamicsEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
