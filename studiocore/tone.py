# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
# -*- coding: utf-8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""
StudioCore v5 — ToneSyncEngine
Unified color–resonance engine for emotional frequency visualization.
"""

import math
import re
from typing import Any, Dict
from studiocore.color_engine_adapter import (
    EMOTION_COLOR_MAP,
    KEY_COLOR_PALETTE,
    get_emotion_colors,
)
from studiocore.emotion_profile import EmotionVector


class ToneSyncEngine:
    """
    Converts emotional frequency (Truth × Love × Pain) + Key
    into a synesthetic visual–resonant signature.
    
    ВАЖНО: Этот класс используется как LegacyToneSyncEngine для обратной совместимости.
    Основной ToneSyncEngine находится в tone_sync.py.
    """

    RIFT_MARKERS = (
        "сегодня я",
        "теперь года прошли",
    )

    BASE_COLOR_MAP = {
        "C": KEY_COLOR_PALETTE["red"],
        "C#": KEY_COLOR_PALETTE["orange-red"],
        "D": KEY_COLOR_PALETTE["golden"],
        "D#": KEY_COLOR_PALETTE["amber"],
        "E": KEY_COLOR_PALETTE["yellow"],
        "F": KEY_COLOR_PALETTE["green"],
        "F#": KEY_COLOR_PALETTE["turquoise"],
        "G": KEY_COLOR_PALETTE["blue"],
        "G#": KEY_COLOR_PALETTE["indigo"],
        "A": KEY_COLOR_PALETTE["violet"],
        "A#": KEY_COLOR_PALETTE["magenta"],
        "B": KEY_COLOR_PALETTE["crimson"],
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

    KEY_STEPS = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    def shift_key(self, key: str, steps: int) -> str:
        """Shift a key by a number of semitone steps, preserving mode suffix if present."""

        if not key or key == "auto":
            return key

        # Separate root and optional mode (e.g., "C# minor")
        parts = key.split(maxsplit=1)
        root = parts[0]
        suffix = f" {parts[1]}" if len(parts) > 1 else ""

        try:
            idx = self.KEY_STEPS.index(root)
        except ValueError:
            return key

        new_root = self.KEY_STEPS[(idx + steps) % len(self.KEY_STEPS)]
        return f"{new_root}{suffix}"

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
            return KEY_COLOR_PALETTE["white"]
        base = key.replace(" minor", "").replace(" major", "").replace(" modal", "").strip()
        base_color = self.BASE_COLOR_MAP.get(base, "#FFFFFF")
        # cf-modulated blend toward complementary hue
        if cf > 0.5:
            blend_target = (
                KEY_COLOR_PALETTE["violet"]
                if base_color in (KEY_COLOR_PALETTE["red"], KEY_COLOR_PALETTE["orange-red"])
                else KEY_COLOR_PALETTE["red"]
            )
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

        dom = max(emo, key=emo.get) if emo else "neutral"
        accent_palette = get_emotion_colors(dom, default=EMOTION_COLOR_MAP["neutral"])
        accent = accent_palette[-1]

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

    def detect_key(self, text: str) -> Dict[str, Any]:
        """
        Определяет тональность из текста.
        ВАЖНО: Не использует цвета из лирики, только явные указания тональности.
        Ищет только музыкальные обозначения (C, D, E, F, G, A, B с возможными диезами).
        """
        if not text:
            return {"key": "auto", "confidence": 0.0}

        # Ищем только явные музыкальные обозначения тональности
        # Паттерн: начало строки или пробел, затем нота (C, D, E, F, G, A, B), опционально #, затем пробел или конец
        # Также ищем в квадратных скобках [C minor], [F# major] и т.д.
        key_pattern = re.compile(
            r'(?:^|[\s\[(])([CDEFGAB]#?)\s*(?:minor|major|maj|min|m|M)?(?=[\s\]),.!?]|$)',
            re.IGNORECASE
        )
        
        matches = key_pattern.findall(text)
        if matches:
            # Берем первую найденную ноту и нормализуем
            base_note = matches[0].upper()
            # Проверяем, что это валидная нота из нашего списка
            if base_note in self.KEY_STEPS or base_note.replace('#', '') in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
                # Ищем mode (minor/major) рядом с нотой
                mode_match = re.search(
                    r'(?:^|[\s\[(])' + re.escape(base_note) + r'\s*(minor|major|maj|min|m|M)',
                    text,
                    re.IGNORECASE
                )
                mode = ""
                if mode_match:
                    mode_text = mode_match.group(1).lower()
                    if mode_text in ('minor', 'min', 'm'):
                        mode = " minor"
                    elif mode_text in ('major', 'maj', 'M'):
                        mode = " major"
                
                return {"key": f"{base_note}{mode}", "confidence": 0.75}
        
        # Если ничего не найдено - возвращаем auto
        return {"key": "auto", "confidence": 0.0}

    def apply_emotion_modulation(self, key_payload, emotion_vector):
        """
        Modulate key & mode based on emotion + COLOR WAVE.
        Emotion now includes: valence, arousal, tlp AND color spectrum.
        """

        base_key = key_payload.get("key", "C")
        base_mode = key_payload.get("mode", "major")

        valence = emotion_vector.valence
        arousal = emotion_vector.arousal

        # === NEW: COLOR WAVE INPUT ===
        color_hex = emotion_vector.extra.get("color_hex", None)
        color_name = emotion_vector.extra.get("color_name", None)

        # Default to original key if no color
        new_key = base_key
        new_mode = base_mode

        # === COLOR → MODE / FEEL MODULATION ===
        if color_name:
            c = color_name.lower()

            if c in ("red", "crimson", "scarlet"):
                new_mode = "minor"
                new_key = self.shift_key(base_key, -2)   # darker
            elif c in ("blue", "navy", "cyan"):
                new_mode = "minor"
                new_key = self.shift_key(base_key, -1)
            elif c in ("yellow", "gold", "amber"):
                new_mode = "major"
                new_key = self.shift_key(base_key, +2)   # brighter
            elif c in ("green", "emerald"):
                new_mode = base_mode                     # neutral
            elif c in ("purple", "violet"):
                new_mode = "phrygian"                    # dramatic
            elif c in ("black", "gray"):
                new_mode = "minor"
                new_key = self.shift_key(base_key, -3)   # darkest

        # === EMOTION INFLUENCE (legacy) ===
        if valence > 0.3:
            new_mode = "major"
        elif valence < -0.3:
            new_mode = "minor"

        # === AROUSAL SEMITONE SHIFT ===
        if arousal > 0.6:
            new_key = self.shift_key(new_key, +1)
        elif arousal < 0.3:
            new_key = self.shift_key(new_key, -1)

        return {
            "key": new_key,
            "mode": new_mode,
            "color": color_name,
            "color_hex": color_hex,
        }

    def has_rhetorical_rift(self, paragraph: str) -> bool:
        if not paragraph:
            return False
        normalized = paragraph.strip().lower()
        return any(normalized.startswith(marker) for marker in self.RIFT_MARKERS)

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
