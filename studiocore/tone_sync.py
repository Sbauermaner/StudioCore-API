# -*- coding: utf-8 -*-
"""
ToneSyncEngine v1
Связка эмоций, тональности, BPM и цветовых профилей.

Используется для:
- вывода tone_profile в diagnostics/backend_payload
- стабилизации "атмосферы" трека
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class ToneProfile:
    name: str
    mood: str
    color_hex: str
    density: str
    recommended_bpms: tuple[int, int]
    preferred_keys: tuple[str, ...]


class ToneSyncEngine:
    """Stateless-движок: на вход — эмоции/TLP/BPM/тональность, на выход — tone_profile.
    
    ВАЖНО: Этот класс используется как основной ToneSyncEngine.
    Класс с тем же именем в tone.py используется как LegacyToneSyncEngine для обратной совместимости.
    """

    def __init__(self) -> None:
        self._profiles: Dict[str, ToneProfile] = {
            "warm_minor": ToneProfile(
                name="warm_minor",
                mood="hopeful_sadness",
                color_hex="#3A4D7A",
                density="mid",
                recommended_bpms=(70, 100),
                preferred_keys=("D minor", "G minor", "A minor"),
            ),
            "cold_minor": ToneProfile(
                name="cold_minor",
                mood="deep_tragedy",
                color_hex="#222244",
                density="high",
                recommended_bpms=(60, 90),
                preferred_keys=("B minor", "F# minor", "C# minor"),
            ),
            "bright_major": ToneProfile(
                name="bright_major",
                mood="joy_light",
                color_hex="#FFE17A",
                density="mid_low",
                recommended_bpms=(90, 130),
                preferred_keys=("C major", "G major", "D major"),
            ),
            "dramatic_epic": ToneProfile(
                name="dramatic_epic",
                mood="heroic_conflict",
                color_hex="#8B1E3F",
                density="high",
                recommended_bpms=(80, 120),
                preferred_keys=("E minor", "B minor", "C minor"),
            ),
            "introspective": ToneProfile(
                name="introspective",
                mood="calm_reflection",
                color_hex="#5A7F7A",
                density="low",
                recommended_bpms=(60, 90),
                preferred_keys=("F minor", "E minor", "A minor"),
            ),
            "chaotic_dark": ToneProfile(
                name="chaotic_dark",
                mood="anger_fear",
                color_hex="#260000",
                density="very_high",
                recommended_bpms=(100, 160),
                preferred_keys=("G minor", "C minor", "F minor"),
            ),
        }

    def pick_profile(
        self,
        bpm: int,
        key: str | None,
        tlp: Dict[str, float] | None,
        emotion_matrix: Dict[str, float] | None,
    ) -> Dict[str, Any]:
        """Возвращает dict с выбранным tone_profile."""
        key = key or "C minor"
        tlp = tlp or {}
        emotion_matrix = emotion_matrix or {}

        truth = float(tlp.get("truth", 0.0))
        love = float(tlp.get("love", 0.0))
        pain = float(tlp.get("pain", 0.0))

        joy = float(emotion_matrix.get("joy", 0.0))
        sadness = float(emotion_matrix.get("sadness", 0.0))
        anger = float(emotion_matrix.get("anger", 0.0))

        cf = (truth + love + pain) / 3 if (truth or love or pain) else 0.0

        # Простая, но предсказуемая эвристика
        if sadness > 0.5 and bpm <= 100:
            profile = self._profiles["warm_minor"]
        elif anger > 0.5 or bpm >= 120:
            profile = self._profiles["chaotic_dark"]
        elif joy > 0.5 and bpm >= 90:
            profile = self._profiles["bright_major"]
        elif cf >= 0.7 and sadness > 0.3:
            profile = self._profiles["dramatic_epic"]
        elif cf <= 0.3 and sadness > 0.3:
            profile = self._profiles["cold_minor"]
        else:
            profile = self._profiles["introspective"]

        data: Dict[str, Any] = {
            "name": profile.name,
            "mood": profile.mood,
            "color_hex": profile.color_hex,
            "density": profile.density,
            "recommended_bpms": list(profile.recommended_bpms),
            "preferred_keys": list(profile.preferred_keys),
            "cf": round(cf, 4),
            "bpm": int(bpm),
            "key": key,
        }
        return data
