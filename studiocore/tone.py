import math
from typing import Dict, Any

class ToneSyncEngine:
    """
    Converts emotional frequency (Truth × Love × Pain) and Key into
    visual–resonant color data for unified synesthetic representation.
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

    def _derive_mood_temperature(self, tlp: Dict[str, float]) -> str:
        """Defines 'warm' or 'cold' emotional temperature."""
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        if love >= max(pain, truth):
            return "warm"
        elif pain > love:
            return "cold"
        else:
            return "neutral"

    def _select_key_color(self, key: str) -> str:
        """Returns base color by musical key."""
        if not key or key == "auto":
            return "white"
        base = key.replace(" minor", "").replace(" major", "").replace(" modal", "").strip()
        return self.BASE_COLOR_MAP.get(base, "white")

    def _resonance_from_key(self, key: str) -> float:
        """Returns base frequency in Hz associated with the key."""
        if not key or key == "auto":
            return 432.0
        base = key.replace(" minor", "").replace(" major", "").replace(" modal", "").strip()
        return self.RESONANCE_MAP.get(base, 432.0)

    def colors_for_primary(self, emo: Dict[str, float], tlp: Dict[str, float], key: str = "auto") -> Dict[str, Any]:
        """
        Generates the full tone–color–frequency profile.
        """
        color = self._select_key_color(key)
        resonance = self._resonance_from_key(key)
        temp = self._derive_mood_temperature(tlp)

        dom = max(emo, key=emo.get)
        accent = {
            "joy": "golden glow",
            "sadness": "blue haze",
            "anger": "red flash",
            "fear": "gray mist",
            "peace": "soft white aura",
            "epic": "purple light"
        }.get(dom, "silver reflection")

        return {
            "primary_color": color,
            "accent_color": accent,
            "mood_temperature": temp,
            "resonance_hz": resonance,
            "synesthetic_signature": f"{color} + {accent} ({temp}, {resonance}Hz)"
        }
