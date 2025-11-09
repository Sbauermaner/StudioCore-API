# -*- coding: utf-8 -*-
"""
Resonance and frequency mapping (RNS safety layer).
"""
from typing import Dict, Any, List
from .config import load_config

class UniversalFrequencyEngine:
    base = 24.5  # Hz

    mapping = {
        0: ("16-32Hz", "Subconscious", "Deep meditation", "#000080"),
        1: ("33-65Hz", "Body awareness", "Physical presence", "#4169E1"),
        2: ("66-130Hz","Emotional base","Feeling foundation","#00BFFF"),
        3: ("131-261Hz","Heart center","Emotional expression","#FF69B4"),
        4: ("262-523Hz","Voice of truth","Authentic communication","#FFD700"),
        5: ("524-1046Hz","Higher mind","Mental clarity","#90EE90"),
        6: ("1047-2093Hz","Intuitive wisdom","Inner knowing","#9370DB"),
        7: ("2094-4186Hz","Spiritual connection","Universal awareness","#FF4500"),
        8: ("4187-7902Hz","Cosmic unity","Transcendence","#FFFFFF")
    }

    def consciousness_info(self, f: float) -> Dict[str, Any]:
        for octv, (rng, cons, state, color) in self.mapping.items():
            mn, mx = map(float, rng.replace("Hz","").split("-"))
            if mn <= f <= mx:
                return {"octave": octv,"range": rng,"consciousness": cons,"state": state,"color": color}
        return {"octave": -1,"range": "Unknown","consciousness": "Unknown","state": "Unknown","color": "#000000"}

    def resonance_profile(self, tlp: Dict[str, float]) -> Dict[str, Any]:
        base = self.base * (1.0 + tlp["truth"])
        spread = tlp["love"] * 2000.0
        mod = 1.0 + tlp["pain"] * 0.5
        info = self.consciousness_info(base)
        if tlp["conscious_frequency"] > 0.7:
            rec = [4,5,6,7]
        elif tlp["conscious_frequency"] > 0.3:
            rec = [2,3,4,5]
        else:
            rec = [1,2,3,4]
        return {"base_frequency": base,"harmonic_range": spread,"modulation_depth": mod,"info": info,"recommended_octaves": rec}

class RNSSafety:
    def __init__(self, config: dict = None):
        self.cfg = (config or load_config())["safety"]

    def clamp_octaves(self, rec: List[int]) -> List[int]:
        safe = set(self.cfg["safe_octaves"])
        filt = [o for o in rec if o in safe]
        return filt or [2,3,4]

    def mix_notes(self) -> Dict[str, Any]:
        return {
            "max_peak_db": self.cfg["max_peak_db"],
            "max_rms_db": self.cfg["max_rms_db"],
            "fade_in_ms": self.cfg["fade_in_ms"],
            "fade_out_ms": self.cfg["fade_out_ms"],
            "avoid_freq_bands_hz": self.cfg["avoid_freq_bands_hz"]
        }
