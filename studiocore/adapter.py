# -*- coding: utf-8 -*-
"""
StudioCore v5 — Suno/Studio adapter
Semantic compression · RNS safety · Adaptive prompt formatting
"""

import re
import hashlib
from typing import Dict, Any, List


# -----------------------------------------------------------
# ✂️ Semantic compression engine
# -----------------------------------------------------------
def semantic_compress(text: str, max_len: int = 1000, preserve_last_line: bool = True) -> str:
    """
    Compresses text meaningfully, preserving structure & emotional context.
    """
    if len(text) <= max_len:
        return text.strip()

    # 1️⃣ Удаляем избыточные слова и стоп-слова
    noise_pattern = (
        r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful|great|awesome|nice)\b"
    )
    text = re.sub(noise_pattern, "", text, flags=re.I)
    text = re.sub(r"[\[\]{}()]+", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # 2️⃣ Семантическое разбиение
    parts = re.split(r"[|;]", text)
    compressed, total = [], 0
    for p in parts:
        p = p.strip()
        if not p:
            continue
        weight = len(re.findall(r"[A-Za-zА-Яа-я]", p)) / max(1, len(p))
        if weight < 0.2:  # шум
            continue
        if total + len(p) < max_len - 50:
            compressed.append(p)
            total += len(p)
        else:
            break

    compressed_text = " | ".join(compressed).strip()

    # 3️⃣ Сохраняем последнюю строку (если есть перенос)
    if preserve_last_line and "\n" in text:
        last_line = text.strip().splitlines()[-1]
        if last_line not in compressed_text:
            compressed_text += "\n" + last_line

    # 4️⃣ Финальная обрезка и метка
    result = compressed_text[:max_len].strip()
    if not result.endswith("…"):
        result += "…"
    return result


# -----------------------------------------------------------
# 🎧 RNS safety placeholder (упрощённая заглушка)
# -----------------------------------------------------------
def rns_safety_tag(bpm: int, key: str) -> str:
    """Returns safety classification tag."""
    safe_keys = ["A", "E", "D", "G"]
    base = key.split()[0] if key else "A"
    level = "safe" if base in safe_keys and bpm < 120 else "watch"
    return f"RNS:{level}:{base}@{bpm}"


# -----------------------------------------------------------
# 🧠 Prompt builder
# -----------------------------------------------------------
def build_suno_prompt(
    style_data: Dict[str, Any],
    vocals: List[str] | None,
    instruments: List[str] | None,
    bpm: int,
    philosophy: str,
    version: str,
    mode: str = "suno",
) -> str:
    """
    Builds adaptive prompt for Suno, video or report engines.
    Modes:
        - "suno": ≤1000 chars, compact emotional summary
        - "video": cinematic context (ToneSync/visual layer)
        - "report": extended diagnostic structure
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

    # RNS safety and meta-tags
    safety_tag = rns_safety_tag(bpm, key)
    emotion_balance = round(abs(style_data.get("complexity_score", 0.5) / 10), 2)
    prompt_id = hashlib.md5(f"{genre}{key}{bpm}{vocal_form}".encode()).hexdigest()[:8]

    prompt = (
        f"Genre: {genre} | Style: {style} | Vocal Form: {vocal_form} | Key: {key} | BPM: {bpm} | Structure: {structure}\n"
        f"Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)} | Instruments: {', '.join(instruments)}\n"
        f"Visual: {visual}\n"
        f"Narrative: {narrative}\n"
        f"Atmosphere: {atmosphere}\n"
        f"Philosophy: {philosophy}\n"
        f"Safety: {safety_tag} | Emotion Balance: {emotion_balance} | Engine: StudioCore {version}\n"
        f"Prompt ID: {prompt_id}"
    )

    # === режимы вывода ===
    if mode == "suno":
        return semantic_compress(prompt, 1000, preserve_last_line=True)
    elif mode == "video":
        return semantic_compress(
            f"[CINEMATIC MODE]\n{prompt}\nToneSync visuals linked.",
            1200,
            preserve_last_line=True,
        )
    elif mode == "report":
        return prompt
    else:
        return prompt
