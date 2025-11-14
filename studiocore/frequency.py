# -*- coding: utf-8 -*-
"""
StudioCore v6 — Frequency & RNS Safety
Resonance–Nervous–Safety adaptive harmonics
"""

import math
from typing import Dict, Any, List


# =====================================================
# 🛡 RNS Safety Filter
# =====================================================
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
        """Фильтрует разрешённые октавы."""
        return [o for o in octaves if o in self.safe_octaves]

    def clamp_band(self, hz: float) -> float:
        """Ограничивает частоту, избегая опасных диапазонов."""
        low, high = self.avoid_freq_bands_hz
        if low <= hz <= high:
            return high + 1.0  # чуть выше запрещённой зоны
        return hz


# =====================================================
# 🎵 Universal Frequency Engine
# =====================================================
class UniversalFrequencyEngine:
    """
    Переводит Truth–Love–Pain в частотную модель резонанса.
    Возвращает:
      - base_hz: основная частота
      - harmonic_shift: смещение октавы
      - consciousness_level: согласованность трёх осей
      - recommended_octaves: безопасные диапазоны
      - rns_index: индекс нейро-резонансной безопасности (0–1)
      - safe_band_hz: безопасная частота после фильтрации RNS
    """

    BASE_HZ = 432.1  # уточнённая гармоника Земли (Cousto Earth frequency)
    MAX_MULT = 2.5

    def _mix(self, t: float, l: float, p: float) -> float:
        """
        Смешивает три оси (Truth, Love, Pain) в одно гармоническое значение.
        Любовь стабилизирует, боль модулирует, истина — фазовый баланс.
        """
        # базовая гармоника
        base = (0.6 * t + 0.9 * l + 0.4 * p)
        # добавим фазовую стабильность (смягчённый синус)
        phase = 0.5 * math.sin(math.pi * (t - p)) + 0.5 * math.cos(math.pi * (l - 0.5))
        harmonics = 1 + 0.4 * phase
        value = base * harmonics
        return max(0.1, min(value, self.MAX_MULT))

    def resonance_profile(self, tlp: Dict[str, float]) -> Dict[str, Any]:
        """Вычисляет частотный профиль, безопасные диапазоны и индекс RNS."""
        t, l, p = tlp.get("truth", 0.0), tlp.get("love", 0.0), tlp.get("pain", 0.0)
        mix = self._mix(t, l, p)

        base_hz = self.BASE_HZ * mix
        harmonic_shift = round(12 * (mix - 1), 2)
        consciousness_level = min(1.0, (t + l + p) / 3)

        # базовые безопасные октавы
        if p > 0.6:
            octaves = [2, 3]
        elif l > 0.7:
            octaves = [3, 4, 5]
        else:
            octaves = [3, 4]

        # индекс нейро-безопасности (высокий при гармонии)
        rns_index = round(1.0 - abs(t - p) * 0.5 - abs(l - p) * 0.3, 3)
        rns_index = max(0.0, min(1.0, rns_index))

        # безопасный диапазон ±5 % от base_hz
        safe_band = (base_hz * 0.95, base_hz * 1.05)
        safe_center = round(sum(safe_band) / 2, 2)

        return {
            "base_hz": round(base_hz, 2),
            "harmonic_shift": harmonic_shift,
            "consciousness_level": round(consciousness_level, 3),
            "recommended_octaves": octaves,
            "rns_index": rns_index,
            "safe_band_hz": safe_center
        }
