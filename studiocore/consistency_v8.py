# -*- coding: utf - 8 -*-
"""
Consistency Layer v8 for StudioCore IMMORTAL

Checks coherence and agreement between:
- BPM ↔ TLP
- BPM ↔ ToneSync
- Genre ↔ RDE
- Emotion ↔ Style
- Narrative structure ↔ Rhythm
"""

from __future__ import annotations
from typing import Any, Dict


class ConsistencyLayerV8:
    """Evaluates cross - engine consistency and produces a structured block."""

    def __init__(self, diagnostics: Dict[str, Any]) -> None:
        self.d = diagnostics or {}

    # --- Helpers ------------------------------------------------------------

    def _calc_bpm_tlp_match(self) -> bool:
        """Check if BPM fits emotional intensity."""
        bpm = self.d.get("bpm")
        tlp = self.d.get("tlp") or {}
        pain = tlp.get("pain") or 0
        truth = tlp.get("truth") or 0

        if bpm is None:
            return True

        # Simple heuristic:
        if bpm >= 130 and pain + truth < 0.3:
            return False
        if bpm <= 95 and pain > 0.6:
            return False
        return True

    def _calc_genre_rde_match(self) -> bool:
        """Check if dynamics is compatible with genre tendencies."""
        genre = self.d.get("genre") or ""
        rde = self.d.get("rde") or {}

        dyn = rde.get("dynamic") or 0
        # emo = rde.get("emotional") or 0  # noqa: F841

        if "gothic" in str(genre).lower():
            return dyn < 0.8
        if "drum" in str(genre).lower():
            return dyn > 0.5
        return True

    def _calc_tone_bpm_coherence(self) -> float:
        """Return 0..1 score for tone ↔ bpm match."""
        bpm = self.d.get("bpm")
        tone = self.d.get("tone_profile") or {}

        if bpm is None:
            return 1.0

        # Minor keys accept wide bpm ranges, major more narrow.
        is_minor = tone.get("is_minor") is True

        if is_minor:
            return 0.9
        if bpm > 140:
            return 0.6
        return 0.8

    def _calc_structure_score(self) -> float:
        """Structure coherence heuristic."""
        sections = self.d.get("sections") or []
        if not sections:
            return 1.0

        score = 1.0
        if any("intro" in s.lower() for s in sections) and any(
            "chorus" in s.lower() for s in sections
        ):
            score += 0.1

        return min(score, 1.0)

    # --- Public -------------------------------------------------------------

    def build(self) -> Dict[str, Any]:
        return {
            "bpm_matches_tlp": self._calc_bpm_tlp_match(),
            "genre_matches_emotion": self._calc_genre_rde_match(),
            "tone_bpm_coherence": self._calc_tone_bpm_coherence(),
            "structure_coherence": self._calc_structure_score(),
        }
