import re
from typing import Dict, Any


def semantic_compress(text: str, max_len: int = 1000, preserve_last_line: bool = True) -> str:
    """
    Compresses text meaningfully, keeping structure and key context.
    Does NOT trim blindly — removes redundancy, keeps essence.
    """
    if len(text) <= max_len:
        return text.strip()

    # 1️⃣ Убираем избыточные слова и шум
    text = re.sub(
        r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful)\b",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"[\[\]{}()]+", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # 2️⃣ Разделяем по логическим частям
    parts = re.split(r"[|;]", text)
    compressed, total = [], 0
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if total + len(p) < max_len - 50:
            compressed.append(p)
            total += len(p)
        else:
            break

    compressed_text = " | ".join(compressed).strip()
    if preserve_last_line and "\n" in text:
        last_line = text.strip().splitlines()[-1]
        if last_line not in compressed_text:
            compressed_text += "\n" + last_line
    return compressed_text[:max_len].strip() + "…"


def build_suno_prompt(
    style_data: Dict[str, Any],
    vocals: list | None,
    instruments: list | None,
    bpm: int,
    philosophy: str,
    version: str,
    mode: str = "full",
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
    vocal_form = style_data.get("vocal_form", "solo_auto")

    vocals = vocals or []
    instruments = instruments or []

    prompt = (
        f"Genre: {genre} | Style: {style} | Vocal Form: {vocal_form} | Key: {key} | BPM: {bpm} | Structure: {structure}\n"
        f"Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)} | "
        f"Instruments: {', '.join(instruments)}\n"
        f"Visual: {visual}\n"
        f"Narrative: {narrative}\n"
        f"Atmosphere: {atmosphere}\n"
        f"Philosophy: {philosophy}\n"
        f"Engine: StudioCore {version} adaptive emotional system"
    )

    # === Suno-режим: безопасное сжатие без потери последней строки
    if mode == "suno":
        return semantic_compress(prompt, 1000, preserve_last_line=True)
    return prompt
