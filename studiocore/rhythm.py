import re
from typing import Dict

# те же веса, что и в emotion.py (короткая копия, чтобы не тянуть импортов)
PUNCT_WEIGHTS = {
    "!": 0.6, "?": 0.4, ".": 0.1, ",": 0.05, "…": 0.5, "—": 0.2, ":": 0.15, ";": 0.1
}

class LyricMeter:
    """
    BPM = f(слоговая плотность, энергия пунктуации, эмоции)
    Возвращает целочисленный BPM в диапазоне 60..168
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
        Если emotions переданы (из AutoEmotionalAnalyzer), учитываем «энергию»:
        anger/epic → ускоряют, sadness/fear → замедляют, joy/peace → мягкий сдвиг вверх.
        """
        emotions = emotions or {}
        avg_syll, n_lines = self._line_stats(text)

        # базовая кривая: чем больше слогов в строке — тем медленнее
        # 8 слогов ~ 140 BPM, 16 слогов ~ 100 BPM, 4 слога ~ 160 BPM
        base = 140 - min(60, (avg_syll - 8) * 5)

        # энергия пунктуации
        p_energy = self._punct_energy(text)  # обычно 0..3
        base += min(18, p_energy * 4.0)

        # эмоциональные коэффициенты (0..1)
        anger = emotions.get("anger", 0.0)
        epic  = emotions.get("epic", 0.0)
        joy   = emotions.get("joy", 0.0)
        sadness = emotions.get("sadness", 0.0)
        fear    = emotions.get("fear", 0.0)
        peace   = emotions.get("peace", 0.0)

        # ускоряющие факторы
        accel = 10.0 * (0.7*anger + 0.6*epic + 0.3*joy)
        # замедляющие факторы
        brake = 10.0 * (0.6*sadness + 0.5*fear + 0.2*peace)

        bpm = base + accel - brake

        # коррекция по длине (очень короткие тексты чуть быстрее, длинные — стабильнее)
        if n_lines <= 4:
            bpm += 4
        elif n_lines > 16:
            bpm -= 3

        return max(60, min(168, int(round(bpm))))
