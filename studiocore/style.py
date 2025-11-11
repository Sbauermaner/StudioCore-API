# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Adaptive StyleMatrix Hybrid
Интеграция нового резолвера стиля (CF + TLP + Mood) в PatchedStyleMatrix.
Позволяет StudioCore Monolith и Suno адаптировать жанр, стиль, атмосферу и нарратив
в зависимости от Truth/Love/Pain и Conscious Frequency.
"""

import re
from typing import Dict, Any, Tuple
from statistics import mean


# ==========================================================
# 🧠 Новый адаптивный резолвер стиля (из StudioCore v5.2.1)
# ==========================================================
def resolve_style_and_form(
    tlp: Dict[str, float],
    cf: float,
    mood: str,
    narrative: Tuple[str, str, str] | None = None,
    key_hint: str | None = None,
) -> Dict[str, str]:
    love = tlp.get("love", 0.0)
    pain = tlp.get("pain", 0.0)
    truth = tlp.get("truth", 0.0)

    # жанр
    if cf > 0.9 or pain >= 0.08 or mood in ("intense", "angry", "dramatic"):
        genre = "cinematic adaptive"
    elif love >= 0.18 and pain < 0.04 and mood in ("peaceful", "hopeful", "romantic"):
        genre = "lyrical adaptive"
    elif mood in ("melancholy", "sad") or (pain >= 0.05 and love < 0.15):
        genre = "lyrical adaptive"
    else:
        genre = "cinematic narrative"

    # стиль и тональность
    if cf >= 0.92 or (pain >= 0.08 and truth >= 0.05):
        style, key_mode = "dramatic harmonic minor", "minor"
    elif pain >= 0.05 and love < 0.15:
        style, key_mode = "melancholic minor", "minor"
    elif love >= 0.18 and pain < 0.04:
        style, key_mode = "majestic major", "major"
    else:
        style, key_mode = "neutral modal", "modal"

    # атмосфера
    if style == "majestic major":
        atmosphere = "serene and hopeful"
    elif style == "melancholic minor":
        atmosphere = "introspective and melancholic"
    elif style == "dramatic harmonic minor":
        atmosphere = "intense and cathartic"
    else:
        atmosphere = "mystic and suspenseful" if cf >= 0.88 else "balanced and reflective"

    if narrative:
        phases = "→".join(narrative)
        if "struggle" in phases and "transformation" in phases and cf >= 0.9:
            if not genre.startswith("cinematic"):
                genre = "cinematic narrative"

    return {
        "genre": genre,
        "style": style,
        "key_mode": key_mode,
        "atmosphere": atmosphere,
    }


# ==========================================================
# 🎨 Классический PatchedStyleMatrix + интеграция резолвера
# ==========================================================
class PatchedStyleMatrix:
    """Adaptive emotional-to-style mapping engine (hybrid v5.2.1)."""

    def build(self, emo: Dict[str, float], tlp: Dict[str, float], text: str, bpm: int) -> Dict[str, Any]:
        cf = tlp.get("conscious_frequency", 0.0)
        dominant = max(emo, key=emo.get) if emo else "neutral"

        # 🔹 Используем новый резолвер
        narrative = ("search", "struggle", "transformation")
        resolved = resolve_style_and_form(tlp, cf, dominant, narrative)

        # 🎼 Формирование ключа
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        scale = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        index_shift = int(((bpm / 10) + (l * 6) - (p * 4) + cf * 5) % 12)
        key = f"{scale[index_shift]} ({scale[index_shift]} {resolved['key_mode']})"

        # 🎨 Визуальный слой
        if resolved["style"] == "majestic major":
            visual = "warm light, sunrise reflections, hands touching"
        elif resolved["style"] == "melancholic minor":
            visual = "rain, fog, silhouettes, slow motion"
        elif resolved["style"] == "dramatic harmonic minor":
            visual = "light and shadow interplay, emotional contrasts, dynamic framing"
        else:
            visual = "shifting colors, abstract transitions"

        # 🎤 Техники вокала
        techniques = []
        if emo.get("anger", 0) > 0.4 or resolved["style"].startswith("dramatic"):
            techniques += ["belt", "rasp", "grit"]
        if emo.get("sadness", 0) > 0.3 or p > 0.4:
            techniques += ["vibrato", "soft cry"]
        if emo.get("joy", 0) > 0.3 or l > 0.3:
            techniques += ["falsetto", "bright tone"]
        if not techniques:
            techniques += ["resonant layering", "harmonic blend"]

        complexity_score = round(mean([emo[k] for k in emo]) * 10, 2) if emo else 0.5
        color_temperature = "warm" if l >= p else "cold"
        adaptive_mode = "stable" if cf > 0.6 else "transient"

        return {
            "genre": resolved["genre"],
            "style": resolved["style"],
            "key": key,
            "structure": "intro-verse-chorus-outro",
            "visual": visual,
            "narrative": "→".join(narrative),
            "atmosphere": resolved["atmosphere"],
            "techniques": techniques,
            "complexity_score": complexity_score,
            "color_temperature": color_temperature,
            "adaptive_mode": adaptive_mode,
        }


# ==========================================================
# ✅ Meta
# ==========================================================
STYLE_VERSION = "v5.2.1 adaptive hybrid"
print(f"🎨 [PatchedStyleMatrix {STYLE_VERSION}] loaded successfully.")
