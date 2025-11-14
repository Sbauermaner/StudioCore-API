# -*- coding: utf-8 -*-
"""
StudioCore v6 — ToneSyncEngine
Unified color–resonance engine for emotional frequency visualization.
"""

import math
from typing import Dict, Any


class ToneSyncEngine:
    """
    Converts emotional frequency (Truth × Love × Pain) + Key
    into a synesthetic visual–resonant signature.
    """

    BASE_COLOR_MAP = {
        "C": "red",
        "C#": "orange-red",
        "D": "golden",
        "D#": "amber",
        "E": "yellow",
        "F": "green",
        "F#": "turquoise",
        "G": "blue",
        "G#": "indigo",
        "A": "violet",
        "A#": "magenta",
        "B": "crimson",
    }

    RESONANCE_MAP = {
        "C": 256.0,
        "C#": 271.0,
        "D": 288.0,
        "D#": 305.0,
        "E": 324.0,
        "F": 341.0,
        "F#": 360.0,
        "G": 384.0,
        "G#": 405.0,
        "A": 432.0,   # Earth harmony
        "A#": 455.0,
        "B": 480.0,
    }

    # -------------------------------------------------------
    # 🌡️ Emotional temperature
    # -------------------------------------------------------
    def _derive_mood_temperature(self, tlp: Dict[str, float]) -> str:
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0.0)
        if cf > 0.65:
            return "radiant"
        if love >= max(pain, truth):
            return "warm"
        elif pain > love:
            return "cold"
        return "neutral"

    # -------------------------------------------------------
    # 🎨 Dual-hue color selector
    # -------------------------------------------------------
    def _select_key_color(self, key: str, cf: float = 0.0) -> str:
        if not key or key == "auto":
            return "white"
        base = key.replace(" minor", "").replace(" major", "").replace(" modal", "").strip()
        base_color = self.BASE_COLOR_MAP.get(base, "white")
        # cf-modulated blend toward complementary hue
        if cf > 0.5:
            blend_target = "violet" if base_color in ("red", "orange-red") else "red"
            return f"{base_color}-{blend_target}"
        return base_color

    # -------------------------------------------------------
    # 🔊 Resonance with adaptive shift
    # -------------------------------------------------------
    def _resonance_from_key(self, key: str, tlp: Dict[str, float]) -> float:
        if not key or key == "auto":
            return 432.0
        base = key.replace(" minor", "").replace(" major", "").replace(" modal", "").strip()
        base_freq = self.RESONANCE_MAP.get(base, 432.0)

        # adaptive shift ±8 Hz
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        balance = (love - pain) * 8
        shift = (truth - 0.5) * 6
        return round(base_freq + balance + shift, 2)

    # -------------------------------------------------------
    # 🌈 Primary color composition
    # -------------------------------------------------------
    def colors_for_primary(self, emo: Dict[str, float], tlp: Dict[str, float], key: str = "auto") -> Dict[str, Any]:
        cf = tlp.get("conscious_frequency", 0.0)
        color = self._select_key_color(key, cf)
        resonance = self._resonance_from_key(key, tlp)
        temp = self._derive_mood_temperature(tlp)

        dom = max(emo, key=emo.get)
        accent = {
            "joy": "golden glow",
            "sadness": "blue haze",
            "anger": "red flash",
            "fear": "gray mist",
            "peace": "soft white aura",
            "epic": "purple light",
        }.get(dom, "silver reflection")

        harmony_score = round(min(1.0, (tlp.get("love", 0) + tlp.get("truth", 0)) / 2), 3)
        brightness = round(0.5 + cf / 2, 2)
        contrast = round(abs(tlp.get("love", 0) - tlp.get("pain", 0)), 2)
        signature_id = f"{color[:2]}-{int(resonance)}-{temp[:2]}-{int(harmony_score*100)}"

        return {
            "primary_color": color,
            "accent_color": accent,
            "mood_temperature": temp,
            "resonance_hz": resonance,
            "harmony_score": harmony_score,
            "brightness": brightness,
            "contrast_level": contrast,
            "synesthetic_signature": f"{color} + {accent} ({temp}, {resonance} Hz)",
            "signature_id": signature_id,
        }
