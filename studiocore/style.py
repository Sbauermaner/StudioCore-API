# -*- coding: utf-8 -*-
"""
StudioCore v5 — StyleMatrix
Формирует полное стилевое описание из лирики и эмоций (адаптивное ядро).
"""

import re
from typing import Dict, Any
from statistics import mean


class StyleMatrix:
    """Adaptive emotional-to-style mapping engine."""

    EMO_GROUPS = {
        "soft": ["love", "peace", "joy"],
        "dark": ["sadness", "pain", "fear"],
        "epic": ["anger", "epic"],
    }

    # -------------------------------------------------------
    # 1️⃣ Тональный профиль
    # -------------------------------------------------------
    def _tone_profile(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        dominant = max(emo, key=emo.get)
        cf = tlp.get("conscious_frequency", 0.0)
        love, pain = tlp.get("love", 0.0), tlp.get("pain", 0.0)

        if 0.45 < cf < 0.55:
            return "adaptive dual-mode"
        if dominant in ("joy", "peace") and love > pain:
            return "majestic major"
        elif dominant in ("sadness", "pain"):
            return "melancholic minor"
        elif dominant in ("anger", "epic") and cf > 0.5:
            return "dramatic harmonic minor"
        return "neutral modal"

    # -------------------------------------------------------
    # 2️⃣ Определение жанра
    # -------------------------------------------------------
    def _derive_genre(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        word_count = len(re.findall(r"\b\w+\b", text))
        sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
        avg_sent_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        density = min(word_count / 100.0, 10)
        emotional_range = (tlp.get("love", 0) + tlp.get("pain", 0) + tlp.get("truth", 0)) / 3

        complexity_score = round((density * 0.2 + avg_sent_len * 0.05), 2)
        emotion_balance = round(1 - abs(tlp.get("love", 0) - tlp.get("pain", 0)), 2)

        if emotional_range > 0.7 and density < 2:
            base = "orchestral poetic"
        elif density > 6 and tlp.get("pain", 0) > 0.4:
            base = "dark rhythmic"
        elif density > 5 and tlp.get("love", 0) > 0.4:
            base = "dynamic emotional"
        elif avg_sent_len > 12:
            base = "cinematic narrative"
        else:
            base = "lyrical adaptive"

        dominant = max(emo, key=emo.get)
        mood = {
            "anger": "dramatic",
            "fear": "mystic",
            "joy": "uplifting",
            "sadness": "melancholic",
            "epic": "heroic",
        }.get(dominant, "reflective")

        return f"{base} {mood}".strip()

    # -------------------------------------------------------
    # 3️⃣ Автоматический подбор тональности (Key)
    # -------------------------------------------------------
    def _derive_key(self, tlp: Dict[str, float], bpm: int) -> str:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        cf = tlp.get("conscious_frequency", 0.0)

        if l > p and l > 0.4:
            mode = "major"
        elif p > l and p > 0.3:
            mode = "minor"
        elif p > 0.4 and t > 0.2:
            mode = "harmonic minor"
        else:
            mode = "modal"

        scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        index_shift = int(((bpm / 10) + (l * 6) - (p * 4) + cf * 5) % 12)
        key = scale[index_shift]
        short = f"{key}{'m' if 'minor' in mode else ''}"

        return f"{short} ({key} {mode})"

    # -------------------------------------------------------
    # 4️⃣ Визуальный слой (ToneSync)
    # -------------------------------------------------------
    def _derive_visual(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        contrast = abs(l - p)
        if contrast > 0.4:
            return "light and shadow interplay, emotional contrasts, dynamic framing"
        if p > l and p > t:
            return "rain, fog, silhouettes, slow motion"
        elif l > p and l > t:
            return "warm light, sunrise reflections, hands touching"
        elif t > 0.4:
            return "clear sky, horizon, open perspective"
        else:
            return "shifting colors, abstract transitions"

    # -------------------------------------------------------
    # 5️⃣ Нарратив
    # -------------------------------------------------------
    def _derive_narrative(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        if tlp.get("pain", 0) > 0.6:
            return "suffering → awakening → transcendence"
        elif tlp.get("love", 0) > 0.6:
            return "loneliness → connection → unity"
        elif tlp.get("truth", 0) > 0.6:
            return "ignorance → revelation → wisdom"
        else:
            return "search → struggle → transformation"

    # -------------------------------------------------------
    # 6️⃣ Вокальные техники
    # -------------------------------------------------------
    def _derive_techniques(self, emo: Dict[str, float], tlp: Dict[str, float]) -> list[str]:
        tech = []
        if emo.get("anger", 0) > 0.4:
            tech += ["belt", "rasp", "grit"]
        if emo.get("sadness", 0) > 0.3 or tlp.get("pain", 0) > 0.4:
            tech += ["vibrato", "soft cry"]
        if emo.get("joy", 0) > 0.3:
            tech += ["falsetto", "bright tone"]
        if emo.get("epic", 0) > 0.4:
            tech += ["choral layering"]
        if tlp.get("conscious_frequency", 0) > 0.6 and not tech:
            tech += ["resonant layering", "harmonic blend"]
        return tech or ["neutral tone"]

    # -------------------------------------------------------
    # 7️⃣ Атмосфера
    # -------------------------------------------------------
    def _derive_atmosphere(self, emo: Dict[str, float]) -> str:
        dominant = max(emo, key=emo.get)
        if dominant in ("joy", "peace", "love"):
            return "serene and hopeful"
        elif dominant in ("sadness", "pain"):
            return "introspective and melancholic"
        elif dominant == "anger":
            return "intense and cathartic"
        elif dominant == "epic":
            return "monumental and triumphant"
        elif dominant == "fear":
            return "mystic and suspenseful"
        else:
            return "mysterious and reflective"

    # -------------------------------------------------------
    # 8️⃣ Основной метод
    # -------------------------------------------------------
    def build(self, emo: Dict[str, float], tlp: Dict[str, float], text: str, bpm: int) -> Dict[str, Any]:
        genre = self._derive_genre(text, emo, tlp)
        style = self._tone_profile(emo, tlp)
        key = self._derive_key(tlp, bpm)
        visual = self._derive_visual(emo, tlp)
        narrative = self._derive_narrative(text, emo, tlp)
        atmosphere = self._derive_atmosphere(emo)
        techniques = self._derive_techniques(emo, tlp)

        complexity_score = round(mean([emo[k] for k in emo]) * 10, 2)
        color_temperature = "warm" if tlp.get("love", 0) >= tlp.get("pain", 0) else "cold"
        adaptive_mode = "stable" if tlp.get("conscious_frequency", 0) > 0.6 else "transient"

        return {
            "genre": genre,
            "style": style,
            "key": key,
            "structure": "intro-verse-chorus-outro",
            "visual": visual,
            "narrative": narrative,
            "atmosphere": atmosphere,
            "techniques": techniques,
            "complexity_score": complexity_score,
            "color_temperature": color_temperature,
            "adaptive_mode": adaptive_mode,
        }
