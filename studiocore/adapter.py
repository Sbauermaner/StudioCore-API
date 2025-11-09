# -*- coding: utf-8 -*-
"""
StudioCore v5 — Adaptive Prompt Adapter
Converts analytical data into Suno-compatible text prompts.
Preserves semantics even when compressed to 1000 chars.
"""

import re
from typing import Dict, Any

def semantic_compress(text: str, max_len: int = 1000) -> str:
    """
    Compresses text meaningfully, keeping structure and key context.
    Does NOT trim blindly — removes redundancy, keeps essence.
    """
    if len(text) <= max_len:
        return text.strip()

    # 1️⃣ убираем избыточные слова, усиливающие, но не несущие смысла
    text = re.sub(r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful)\b", "", text, flags=re.I)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # 2️⃣ если текст длиннее лимита — оставляем логические блоки по смыслу
    parts = re.split(r"[|;]", text)
    compressed = []
    total = 0
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if total + len(p) < max_len - 50:
            compressed.append(p)
            total += len(p)
        else:
            break

    return " | ".join(compressed).strip() + "…"


def build_suno_prompt(
    style_data: Dict[str, Any],
    vocals: list,
    instruments: list,
    bpm: int,
    philosophy: str,
    version: str,
    mode: str = "full"
) -> str:
    """
    Builds a detailed or compact adaptive prompt from full StudioCore analysis.
    Mode:
      - "full" → для визуализаций, отчётов, AI-композеров
      - "suno" → для музыкальных генераторов (≤1000 символов)
    """

    genre = style_data.get("genre", "adaptive emotional")
    style = style_data.get("style", "free-form tonal flow")
    key = style_data.get("key", "auto")
    structure = style_data.get("structure", "intro-verse-chorus-outro")
    visual = style_data.get("visual", "")
    narrative = style_data.get("narrative", "")
    atmosphere = style_data.get("atmosphere", "")
    techniques = style_data.get("techniques", [])

    # === Полная форма ===
    prompt = (
        f"Genre: {genre} | Style: {style} | Key: {key} | BPM: {bpm} | Structure: {structure}\n"
        f"Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)} | "
        f"Instruments: {', '.join(instruments)}\n"
        f"Visual: {visual}\n"
        f"Narrative: {narrative}\n"
        f"Atmosphere: {atmosphere}\n"
        f"Philosophy: {philosophy}\n"
        f"Engine: StudioCore {version} adaptive emotional system"
    )

    # === Если требуется Suno-режим — сжимаем, не обрезаем ===
    if mode == "suno":
        return semantic_compress(prompt, 1000)
    return prompt
