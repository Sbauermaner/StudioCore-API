# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Public BPM helper built on top of the logical engines module."""

from __future__ import annotations

from typing import Any, Dict, Sequence

from .emotion_profile import EmotionVector

from .logical_engines import BPMEngine as _CoreBPMEngine


class BPMEngine(_CoreBPMEngine):
    """Expose a concise helper API for rhythm-aware tooling."""

    def compute_bpm_v2(self, lines: Sequence[str]) -> int:
        """Грубый, но flow-aware расчёт BPM: длина строк + слоги + плотность."""
        text_lines = [ln.strip() for ln in lines if ln.strip()]
        if not text_lines:
            return 90

        def syllable_count(s: str) -> int:
            vowels = "aeiouyауоыиэяюёе"
            return max(1, sum(1 for ch in s.lower() if ch in vowels))

        total_syllables = 0
        total_words = 0
        for ln in text_lines:
            words = ln.split()
            total_words += len(words)
            total_syllables += syllable_count(ln)

        avg_syllables_per_word = total_syllables / max(total_words, 1)
        avg_len = sum(len(ln) for ln in text_lines) / max(len(text_lines), 1)

        # Базовый BPM
        bpm = 80

        # Ускоряем, если текст плотный и длинный
        if avg_syllables_per_word > 2.8:
            bpm += 10
        if avg_syllables_per_word > 3.3:
            bpm += 15

        if avg_len > 60:
            bpm += 10
        elif avg_len < 30:
            bpm -= 5

        bpm = max(40, min(200, int(bpm)))
        return bpm

    def describe(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        resolved_sections = list(sections) if sections else [text]
        joined_text = "\n\n".join(resolved_sections)
        estimate = float(self.text_bpm_estimation(joined_text))
        curve = self.meaning_bpm_curve(resolved_sections, base_bpm=estimate)
        mapping = self.emotion_bpm_mapping({}, base_bpm=int(estimate))
        poly = self.poly_rhythm_detection(curve)
        return {
            "estimate": estimate,
            "curve": curve,
            "poly_rhythm": poly,
            "target_energy": mapping.get("target_energy"),
        }

    def apply_emotional_microshift(self, bpm: float, emotion: EmotionVector) -> float:
        """
        Emotional BPM micro-adjustment.
        Soft shift: ±3% based on emotional arousal.
        """
        shift = (emotion.arousal - 0.5) * 0.06 * bpm
        return bpm + shift


__all__ = ["BPMEngine"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
