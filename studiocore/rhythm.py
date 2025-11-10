# -*- coding: utf-8 -*-
"""
StudioCore v5 LyricMeter — адаптивный анализ ритма текста
BPM = f(слоговая плотность, пунктуация, эмоциональная энергия)
"""

import re
from typing import Dict

PUNCT_WEIGHTS = {
    "!": 0.6, "?": 0.4, ".": 0.1, ",": 0.05, "…": 0.5, "—": 0.2, ":": 0.15, ";": 0.1
}


class LyricMeter:
    """
    Расчёт BPM на основе плотности слогов, пунктуации и эмоций.
    Диапазон 60..172 BPM. Подходит для адаптивных музыкальных движков (Suno, StudioCore).
    """

    vowels = set("aeiouyауоыиэяюёеAEIOUYАУОЫИЭЯЮЁЕ")

    def _syllables(self, s: str) -> int:
        return max(1, sum(1 for ch in s if ch in self.vowels))

    def _punct_energy(self, text: str) -> float:
        return sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in text)

    def _line_stats(self, text: str):
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return 0.0, 0
        syl = [self._syllables(l) for l in lines]
        avg = sum(syl) / len(lines)
        return avg, len(lines)

    def bpm_from_density(self, text: str, emotions: Dict[str, float] | None = None) -> int:
        """
        Если emotions переданы, учитывает эмоциональную энергию:
        anger/epic → ускоряют, sadness/fear → замедляют, joy/peace → мягко поднимают.
        """
        emotions = emotions or {}
        avg_syll, n_lines = self._line_stats(text)

        # базовая логистическая кривая вместо линейной
        # (гладкая адаптация для вокальных текстов)
        base = 60 + 120 / (1 + pow(2.718, (avg_syll - 8) / 2.5 * 0.8))

        # пунктуационная энергия
        p_energy = self._punct_energy(text)
        base += min(18, p_energy * 3.5)

        # эмоции
        anger = emotions.get("anger", 0.0)
        epic = emotions.get("epic", 0.0)
        joy = emotions.get("joy", 0.0)
        sadness = emotions.get("sadness", 0.0)
        fear = emotions.get("fear", 0.0)
        peace = emotions.get("peace", 0.0)

        energy_factor = max(0.8, min(1.4, 1 + (anger + epic + joy - sadness - fear) * 0.6))

        accel = 10.0 * (0.7 * anger + 0.6 * epic + 0.3 * joy)
        brake = 10.0 * (0.6 * sadness + 0.5 * fear + 0.2 * peace)

        bpm = (base + accel - brake) * energy_factor

        # коррекция по длине
        if n_lines <= 4:
            bpm += 4
        elif n_lines > 16:
            bpm -= 3

        # диапазон
        return max(60, min(172, int(round(bpm))))
