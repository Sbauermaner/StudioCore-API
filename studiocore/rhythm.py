# -*- coding: utf-8 -*-
"""
Lyric rhythm and BPM estimation.
"""
from typing import List
from .emotion import PUNCT_WEIGHTS

class LyricMeter:
    """
    Estimates syllable count and tempo (BPM) of lyrical text.
    Based on vowel density and punctuation boost.
    """
    vowels = set("aeiouyауоыиэяюёе")

    def syllables(self, line: str) -> int:
        return max(1, sum(1 for ch in line.lower() if ch in self.vowels))

    def bpm_from_density(self, text: str) -> int:
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines:
            return 100
        avg = sum(self.syllables(l) for l in lines) / len(lines)
        bpm = 140 - min(60, (avg - 8) * 6)
        punct_boost = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in text)
        bpm = bpm + min(20, punct_boost * 4.0)
        return max(60, min(160, int(bpm)))
