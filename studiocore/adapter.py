# -*- coding: utf-8 -*-
"""
StudioCore v5.2 — Suno/Studio Adaptive Adapter
Semantic compression · RNS safety · Dynamic prompt formatting (Lyrics / Style / Philosophy)
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
            compressed_text += "\n" + last_line

    result = compressed_text[:max_len].strip()
    if not result.endswith("…"):
        result += "…"
    return result


# -----------------------------------------------------------
# 🎧 RNS safety tag
# -----------------------------------------------------------
def rns_safety_tag(bpm: int, key: str) -> str:
    """Returns safety classification tag for frequency compliance."""
    safe_keys = ["A", "E", "D", "G"]
    base = key.split()[0] if key else "A"
    level = "safe" if base in safe_keys and bpm < 120 else "watch"
    return f"RNS:{level}:{base}@{bpm}"


# -----------------------------------------------------------
# 🧠 Prompt builder (adaptive)
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
        - "suno": ≤1000 chars → compact emotional summary (Style Prompt)
        - "full": ≤5000 chars → extended lyrical/structural analysis
        - "video": cinematic variant (ToneSync visuals)
        - "report": extended diagnostic (internal use)
    """

    genre = style_data.get("genre", "adaptive emotional")
    style = style_data.get("style", "free-form tonal flow")
    key = style_data.get("key", "auto")
    structure = style_data.get("structure", "intro-verse-chorus-outro")
    vocal_form = style_data.get("vocal_form", "solo_auto")
    techniques = style_data.get("techniques", [])
    atmosphere = style_data.get("atmosphere", "")
    visual = style_data.get("visual", "")
    narrative = style_data.get("narrative", "")

    vocals = vocals or []
    instruments = instruments or []

    safety_tag = rns_safety_tag(bpm, key)
    emotion_balance = round(abs(style_data.get("complexity_score", 0.5) / 10), 2)
    prompt_id = hashlib.md5(f"{genre}{key}{bpm}{vocal_form}".encode()).hexdigest()[:8]

    base_prompt = (
        f"Genre: {genre} | Style: {style} | Key: {key} | BPM: {bpm} | Structure: {structure}\n"
        f"Vocal Form: {vocal_form} | Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)}\n"
        f"Instruments: {', '.join(instruments)} | Atmosphere: {atmosphere}\n"
        f"Visual: {visual} | Narrative: {narrative}\n"
        f"Philosophy: {philosophy}\n"
        f"Safety: {safety_tag} | Emotion Balance: {emotion_balance} | Engine: StudioCore {version}\n"
        f"Prompt ID: {prompt_id}"
    )

    # === режимы вывода ===
    if mode == "suno":  # короткий style prompt
        return semantic_compress(base_prompt, 1000, preserve_last_line=True)
    elif mode == "full":  # полный 5k lyrical diagnostic prompt
        return semantic_compress(
            f"[FULL STUDIO REPORT]\n{base_prompt}\nExtended lyrical diagnostics active.",
            5000,
            preserve_last_line=True,
        )
    elif mode == "video":
        return semantic_compress(
            f"[CINEMATIC MODE]\n{base_prompt}\nToneSync visuals linked.",
            1200,
            preserve_last_line=True,
        )
    elif mode == "report":
        return base_prompt
    else:
        return semantic_compress(base_prompt, 1000, preserve_last_line=True)
