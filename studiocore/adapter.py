# -*- coding: utf-8 -*-
"""
StudioCore v5.2 — Suno/Studio Adaptive Adapter (v3 - NameError ИСПРАВЛЕН)
Semantic compression · RNS safety · Dynamic prompt formatting
"""

import re
import hashlib
from typing import Dict, Any, List
import logging

log = logging.getLogger(__name__)

# === ИСПРАВЛЕНИЕ (NameError) ===
# Эта константа была потеряна при рефакторинге
VERSION_LIMITS: Dict[str, int] = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}
# === Конец исправления ===

# -----------------------------------------------------------
# ✂️ Semantic compression engine (без изменений)
# -----------------------------------------------------------
def semantic_compress(text: str, max_len: int = 1000, preserve_last_line: bool = True) -> str:
    if len(text) <= max_len:
        return text.strip()
    noise_pattern = (
        r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful|great|awesome|nice|so|such|quite|pretty)\b"
    )
    text = re.sub(noise_pattern, "", text, flags=re.I)
    text = re.sub(r"[\[\]{}()]+", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    parts = re.split(r"[|;]", text)
    compressed, total = [], 0
    for p in parts:
        p = p.strip()
        if not p:
            continue
        weight = len(re.findall(r"[A-Za-zА-Яа-я]", p)) / max(1, len(p))
        if weight < 0.2:
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
            if len(compressed_text) + len(last_line) + 1 < max_len:
                compressed_text += "\n" + last_line
    result = compressed_text[:max_len].strip()
    if not result.endswith("…") and len(text) > max_len:
        result += "…"
    return result

# -----------------------------------------------------------
# 🎧 RNS safety tag (без изменений)
# -----------------------------------------------------------
def rns_safety_tag(bpm: int, key: str) -> str:
    safe_keys = ["A", "E", "D", "G"]
    base = key.split()[0] if key else "A"
    level = "safe" if base in safe_keys and bpm < 120 else "watch"
    return f"RNS:{level}:{base}@{bpm}"

# -----------------------------------------------------------
# 🧠 Prompt builder (v2 - раздельные)
# -----------------------------------------------------------
def build_suno_prompt(
    style_data: Dict[str, Any],
    vocals: List[str] | None,
    instruments: List[str] | None,
    bpm: int,
    philosophy: str,
    version: str,
    mode: str = "suno_style",
) -> str:
    log.debug(f"Вызов функции: build_suno_prompt (Mode: {mode})")

    genre = style_data.get("genre", "adaptive emotional")
    style = style_data.get("style", "free-form tonal flow")
    key = style_data.get("key", "auto")
    atmosphere = style_data.get("atmosphere", "")
    narrative = style_data.get("narrative", "")
    visual = style_data.get("visual", "")

    vocal_form = style_data.get("vocal_form", "solo_auto")
    techniques = style_data.get("techniques", [])
    vocals = vocals or []
    instruments = instruments or []
    
    safety_tag = rns_safety_tag(bpm, key)
    emotion_balance = round(abs(style_data.get("complexity_score", 0.5) / 10), 2)
    prompt_id = hashlib.md5(f"{genre}{key}{bpm}{vocal_form}{philosophy}".encode()).hexdigest()[:8]

    if mode == "suno_style":
        prompt_parts = [
            genre,
            style,
            key,
            f"{bpm} BPM",
            atmosphere,
            f"({', '.join(instruments)})",
            narrative,
            visual
        ]
        prompt = ", ".join(filter(None, prompt_parts))
        # === ИСПРАВЛЕНИЕ (NameError) ===
        max_len = VERSION_LIMITS.get(version.lower(), 1000)
        # === Конец исправления ===
        return semantic_compress(prompt, max_len, preserve_last_line=False)

    elif mode == "suno_lyrics":
        clean_vocals = sorted(list(set(v for v in vocals if v not in [
            "male","female","duet","trio","quartet","quintet","choir","solo"
        ])))
        
        prompt_parts = [
            vocal_form,
            f"({', '.join(clean_vocals)})",
            f"({', '.join(techniques)})",
        ]
        prompt = ", ".join(filter(None, prompt_parts))
        # === ИСПРАВЛЕНИЕ (NameError) ===
        max_len = VERSION_LIMITS.get(version.lower(), 1000)
        # === Конец исправления ===
        return semantic_compress(prompt, max_len, preserve_last_line=False)

    else: # "full", "report", "video"
        base_prompt = (
            f"Genre: {genre} | Style: {style} | Key: {key} | BPM: {bpm} | Structure: {style_data.get('structure', 'intro-verse-chorus-outro')}\n"
            f"Vocal Form: {vocal_form} | Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)}\n"
            f"Instruments: {', '.join(instruments)} | Atmosphere: {atmosphere}\n"
            f"Visual: {visual} | Narrative: {narrative}\n"
            f"Philosophy: {philosophy}\n"
            f"Safety: {safety_tag} | Emotion Balance: {emotion_balance} | Engine: StudioCore {version}\n"
            f"Prompt ID: {prompt_id}"
        )
        max_len = 5000 if mode == "full" else 1200
        return semantic_compress(base_prompt, max_len, preserve_last_line=True)