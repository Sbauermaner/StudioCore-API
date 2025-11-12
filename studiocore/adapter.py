# -*- coding: utf-8 -*-
"""
StudioCore v5.2 — Suno/Studio Adaptive Adapter (v2 - Раздельные промпты)
Semantic compression · RNS safety · Dynamic prompt formatting
"""

import re
import hashlib
from typing import Dict, Any, List
import logging

log = logging.getLogger(__name__)

# -----------------------------------------------------------
# ✂️ Semantic compression engine (без изменений)
# -----------------------------------------------------------
def semantic_compress(text: str, max_len: int = 1000, preserve_last_line: bool = True) -> str:
    """
    Compresses text meaningfully, preserving structure & emotional context.
    """
    if len(text) <= max_len:
        return text.strip()

    # Убираем "шумные" слова-усилители
    noise_pattern = (
        r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful|great|awesome|nice|so|such|quite|pretty)\b"
    )
    text = re.sub(noise_pattern, "", text, flags=re.I)
    text = re.sub(r"[\[\]{}()]+", "", text) # Убираем скобки
    text = re.sub(r"\s{2,}", " ", text).strip() # Сжимаем пробелы

    # Разделяем по | или ;
    parts = re.split(r"[|;]", text)
    compressed, total = [], 0
    
    for p in parts:
        p = p.strip()
        if not p:
            continue
        
        # Отсеиваем "мусор" (например, "|||")
        weight = len(re.findall(r"[A-Za-zА-Яа-я]", p)) / max(1, len(p))
        if weight < 0.2:
            continue
            
        # Добавляем, пока не достигнем лимита
        if total + len(p) < max_len - 50: # Оставляем запас
            compressed.append(p)
            total += len(p)
        else:
            break

    compressed_text = " | ".join(compressed).strip()

    # (Логика preserve_last_line остается без изменений)
    if preserve_last_line and "\n" in text:
        last_line = text.strip().splitlines()[-1]
        if last_line not in compressed_text:
            # Убедимся, что не превышаем лимит
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
    """Returns safety classification tag for frequency compliance."""
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
    mode: str = "suno_style", # 'suno_style' или 'suno_lyrics'
) -> str:
    """
    v2: Строит ДВА разных промпта:
     - 'suno_style': Только музыка (жанр, инструменты, атмосфера)
     - 'suno_lyrics': Только вокал (форма, техники, тембр)
    """
    log.debug(f"Вызов функции: build_suno_prompt (Mode: {mode})")

    # --- Общие данные ---
    genre = style_data.get("genre", "adaptive emotional")
    style = style_data.get("style", "free-form tonal flow")
    key = style_data.get("key", "auto")
    atmosphere = style_data.get("atmosphere", "")
    narrative = style_data.get("narrative", "")
    visual = style_data.get("visual", "")

    # --- Специфичные данные ---
    vocal_form = style_data.get("vocal_form", "solo_auto")
    techniques = style_data.get("techniques", [])
    vocals = vocals or []
    instruments = instruments or []
    
    # --- Мета ---
    safety_tag = rns_safety_tag(bpm, key)
    emotion_balance = round(abs(style_data.get("complexity_score", 0.5) / 10), 2)
    prompt_id = hashlib.md5(f"{genre}{key}{bpm}{vocal_form}{philosophy}".encode()).hexdigest()[:8]

    # --------------------------------
    # РЕЖИМ 1: Промпт для [Style of Music]
    # --------------------------------
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
        # Собираем, фильтруем пустые строки, сжимаем
        prompt = ", ".join(filter(None, prompt_parts))
        max_len = VERSION_LIMITS.get(version.lower(), 1000)
        return semantic_compress(prompt, max_len, preserve_last_line=False)

    # --------------------------------
    # РЕЖИМ 2: Промпт для [Lyrics] (только вокал)
    # --------------------------------
    elif mode == "suno_lyrics":
        # Убираем общие слова (male/female)
        clean_vocals = sorted(list(set(v for v in vocals if v not in [
            "male","female","duet","trio","quartet","quintet","choir","solo"
        ])))
        
        prompt_parts = [
            vocal_form,
            f"({', '.join(clean_vocals)})",
            f"({', '.join(techniques)})",
        ]
        prompt = ", ".join(filter(None, prompt_parts))
        max_len = VERSION_LIMITS.get(version.lower(), 1000)
        return semantic_compress(prompt, max_len, preserve_last_line=False)

    # --------------------------------
    # РЕЖИМ 3: Полный отчет (старая логика)
    # --------------------------------
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