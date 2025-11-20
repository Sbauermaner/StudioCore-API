# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from __future__ import annotations

from typing import List

from studiocore.emotion_profile import EmotionVector


class EmotionMapEngine:
    """
    Converts smoothed emotional vectors into a visual color gradient.
    Produces a color wave (#RRGGBB) for each line and a global gradient summary.
    """

    def __init__(self):
        pass

    def _map_value(self, x: float) -> int:
        # clamp to 0–255
        return max(0, min(255, int((x + 1) / 2 * 255)))

    def vector_to_color(self, v: EmotionVector) -> str:
        """
        Convert EmotionVector → color hex.
        valence  → red / blue
        arousal → brightness
        pain    → darkness shift
        """
        r = self._map_value(v.valence)
        g = self._map_value(1.0 - v.pain)
        b = self._map_value(-v.valence)

        # brightness shift from arousal
        brightness = v.arousal * 0.4
        r = int(r * (0.8 + brightness))
        g = int(g * (0.8 + brightness))
        b = int(b * (0.8 + brightness))

        return f"#{r:02X}{g:02X}{b:02X}"

    def build_map(self, vectors: List[EmotionVector]) -> dict:
        """
        Produce:
        - per-line color wave
        - global average color
        """
        if not vectors:
            return {"wave": [], "global": "#000000"}

        wave = [self.vector_to_color(v) for v in vectors]

        # compute global average color
        avg_r = sum(int(c[1:3], 16) for c in wave) // len(wave)
        avg_g = sum(int(c[3:5], 16) for c in wave) // len(wave)
        avg_b = sum(int(c[5:7], 16) for c in wave) // len(wave)

        global_color = f"#{avg_r:02X}{avg_g:02X}{avg_b:02X}"

        return {
            "wave": wave,
            "global": global_color,
        }

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
