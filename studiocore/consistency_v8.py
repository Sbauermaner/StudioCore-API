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
from typing import Any, Dict, List, Optional, Tuple


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

    # --- Conflict Resolution Methods ----------------------------------------

    def resolve_bpm_tlp_conflict(
        self, bpm: Optional[float], tlp: Dict[str, Any]
    ) -> Tuple[Optional[float], bool]:
        """
        Task 17.1: Auto-correct BPM based on TLP intensity.
        
        Rules from KONFLIKTE_UND_PROZESSE.md:
        - If bpm >= 130 AND pain + truth < 0.3 → conflict (high BPM, low TLP)
        - If bpm <= 95 AND pain > 0.6 → conflict (low BPM, high Pain)
        - Priority: TLP → BPM (TLP determines expected BPM range)
        
        Returns:
            Tuple of (suggested_bpm, was_resolved)
        """
        if bpm is None:
            return None, False

        pain = float(tlp.get("pain", 0.0))
        truth = float(tlp.get("truth", 0.0))
        love = float(tlp.get("love", 0.0))
        tlp_intensity = pain + truth + love

        was_resolved = False
        suggested_bpm = bpm

        # Conflict 1: High BPM (>= 130) with low TLP intensity (< 0.3)
        if bpm >= 130 and tlp_intensity < 0.3:
            # Scale down BPM by 0.8x (20% reduction)
            suggested_bpm = bpm * 0.8
            was_resolved = True

        # Conflict 2: Low BPM (<= 95) with high Pain (> 0.6)
        elif bpm <= 95 and pain > 0.6:
            # Scale up BPM to match pain intensity
            # Target: around 100-110 for high pain
            suggested_bpm = max(100.0, bpm * 1.15)
            was_resolved = True

        # Conflict 3: Very high BPM (120-140) with very low TLP (< 0.2)
        elif 120 <= bpm < 140 and tlp_intensity < 0.2:
            # Scale down more aggressively
            suggested_bpm = bpm * 0.75
            was_resolved = True

        return suggested_bpm, was_resolved

    def resolve_genre_rde_conflict(
        self, genre: str, rde: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Task 17.2: Clamp RDE values for specific genres.
        
        Rules from KONFLIKTE_UND_PROZESSE.md:
        - If "gothic" in genre AND dynamic >= 0.8 → conflict (cap dynamic to 0.7)
        - If "drum" in genre AND dynamic <= 0.5 → conflict (raise dynamic to > 0.5)
        - Priority: Genre → RDE (genre determines expected dynamics)
        
        Returns:
            Tuple of (adjusted_rde, was_resolved)
        """
        if not rde:
            return rde, False

        genre_lower = str(genre).lower()
        adjusted_rde = rde.copy()
        was_resolved = False

        dynamic = float(rde.get("dynamic", 0.0))

        # Conflict 1: Gothic requires low dynamics (< 0.8)
        if "gothic" in genre_lower and dynamic >= 0.8:
            adjusted_rde["dynamic"] = 0.7
            was_resolved = True

        # Conflict 2: Drum requires high dynamics (> 0.5)
        elif "drum" in genre_lower and dynamic <= 0.5:
            adjusted_rde["dynamic"] = 0.55
            was_resolved = True

        return adjusted_rde, was_resolved

    # --- Validation Methods ------------------------------------------------

    def validate_color_bpm(
        self, color: Optional[str], bpm: Optional[float]
    ) -> Optional[str]:
        """
        Task 20.1: Check if BPM falls within the expected range for the given color.
        
        References EMOTION_COLOR_TO_BPM mapping from genre_colors.py.
        Returns a warning string if BPM is out of bounds, None otherwise.
        
        Args:
            color: Hex color code (e.g., "#FF7AA2")
            bpm: BPM value to validate
        
        Returns:
            Warning string if BPM is out of expected range, None if valid
        """
        if not color or bpm is None:
            return None
        
        # Import EMOTION_COLOR_TO_BPM mapping
        try:
            from .genre_colors import EMOTION_COLOR_TO_BPM
        except ImportError:
            # Fallback if import fails
            return None
        
        # Get expected BPM range for this color
        expected_range = EMOTION_COLOR_TO_BPM.get(color.upper())
        if not expected_range:
            # Color not in mapping, no validation possible
            return None
        
        min_bpm, max_bpm, _ = expected_range
        
        # Check if BPM is within expected range
        if bpm < min_bpm:
            return (
                f"BPM {bpm} is below expected range [{min_bpm}-{max_bpm}] "
                f"for color {color}. Consider increasing BPM to at least {min_bpm}."
            )
        elif bpm > max_bpm:
            return (
                f"BPM {bpm} is above expected range [{min_bpm}-{max_bpm}] "
                f"for color {color}. Consider decreasing BPM to at most {max_bpm}."
            )
        
        # BPM is within expected range
        return None

    def check_low_bpm_major_key(
        self, bpm: Optional[float], key: Optional[str]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Task 20.2: Check for Low BPM (< 60) + Major Key anti-pattern.
        
        This combination often sounds dissonant. Returns suggestions to either:
        - Switch to Minor key, or
        - Increase BPM to at least 60
        
        Args:
            bpm: BPM value
            key: Key string (e.g., "C major", "A minor")
        
        Returns:
            Tuple of (warning_message, suggestion)
        """
        if bpm is None or not key:
            return None, None
        
        # Check if BPM is very low
        if bpm >= 60:
            return None, None
        
        # Normalize key string to check if it's Major
        key_lower = str(key).lower().strip()
        is_major = (
            "major" in key_lower
            and "minor" not in key_lower
            and not key_lower.endswith("m")
        )
        
        # Also check for common major key patterns
        if not is_major:
            # Check if key is in format like "C" (defaults to major) or "C maj"
            major_patterns = ["maj", "major", "dur"]
            if any(pattern in key_lower for pattern in major_patterns):
                is_major = True
        
        if not is_major:
            # Not a major key, no conflict
            return None, None
        
        # Conflict detected: Low BPM + Major Key
        warning = (
            f"Low BPM ({bpm}) with Major Key ({key}) may sound dissonant. "
            "This combination is generally avoided in music production."
        )
        suggestion = (
            f"Consider switching to Minor key or increasing BPM to at least 60. "
            f"Suggested: {key.replace('major', 'minor').replace('Major', 'Minor')} "
            f"or BPM >= 60"
        )
        
        return warning, suggestion

    # --- Public -------------------------------------------------------------

    def build(self) -> Dict[str, Any]:
        return {
            "bpm_matches_tlp": self._calc_bpm_tlp_match(),
            "genre_matches_emotion": self._calc_genre_rde_match(),
            "tone_bpm_coherence": self._calc_tone_bpm_coherence(),
            "structure_coherence": self._calc_structure_score(),
        }
