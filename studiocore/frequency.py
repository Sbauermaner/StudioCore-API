import math
from typing import Dict, Any, List


class RNSSafety:
    """
    Resonance–Nervous–Safety filter
    Ограничивает диапазоны частот и октав для защиты слуха и психоакустической стабильности.
    """
    def __init__(self, cfg: Dict[str, Any]):
        s = cfg.get("safety", {})
        self.max_peak_db = s.get("max_peak_db", -1.0)
        self.max_rms_db = s.get("max_rms_db", -14.0)
        self.avoid_freq_bands_hz = s.get("avoid_freq_bands_hz", [18.0, 30.0])
        self.safe_octaves = s.get("safe_octaves", [2, 3, 4, 5])

    def clamp_octaves(self, octaves: List[int]) -> List[int]:
        """Ограничивает диапазон в пределах разрешённых октав."""
        return [o for o in octaves if o in self.safe_octaves]


class UniversalFrequencyEngine:
    """
    Переводит Truth–Love–Pain в частотную модель резонанса.
    Возвращает:
      - base_hz: частота основного резонанса
      - harmonic_shift: смещение октавы
      - consciousness_level: коэффициент когнитивного согласования (0..1)
      - recommended_octaves: список безопасных октав
    """

    BASE_HZ = 432.0  # гармоническая база Земли
    MAX_MULT = 2.5   # максимум усиления для эмоций

    def _mix(self, t: float, l: float, p: float) -> float:
        """Смешивает три оси (Truth, Love, Pain) в одно гармоническое значение."""
        # весовая формула: любовь — стабилизатор, боль — модулятор, истина — фазовый сдвиг
        base = (0.6 * t + 0.9 * l + 0.4 * p)
        harmonics = 1 + 0.5 * math.sin(math.pi * (t - p))
        return max(0.1, min(base * harmonics, self.MAX_MULT))

    def resonance_profile(self, tlp: Dict[str, float]) -> Dict[str, Any]:
        """Вычисляет резонансную частоту и безопасные октавы."""
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        mix = self._mix(t, l, p)

        base_hz = self.BASE_HZ * mix
        harmonic_shift = round(12 * (mix - 1), 2)
        consciousness_level = min(1.0, (t + l + p) / 3)

        # безопасные октавы в зависимости от эмоций:
        if p > 0.6:
            octaves = [2, 3]
        elif l > 0.7:
            octaves = [3, 4, 5]
        else:
            octaves = [3, 4]

        return {
            "base_hz": round(base_hz, 2),
            "harmonic_shift": harmonic_shift,
            "consciousness_level": round(consciousness_level, 3),
            "recommended_octaves": octaves
        }
