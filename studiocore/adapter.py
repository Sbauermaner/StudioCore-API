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
StudioCore v5.2 — Suno/Studio Adaptive Adapter (v5 - NameError ИСПРАВЛЕН)
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
# ✂️ Semantic compression engine
# -----------------------------------------------------------
def semantic_compress(text: str, max_len: int = 1000, preserve_last_line: bool = True) -> str:
    """
    Сжимает текст, сохраняя структуру и эмоциональный контекст.
    """
    log.debug(f"Вызов semantic_compress: max_len={max_len}")
    if len(text) <= max_len:
        return text.strip()

    # 1. Удаляем "шумные" слова
    noise_pattern = (
        r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful|great|awesome|nice|so|such|quite|pretty)\b"
    )
    text = re.sub(noise_pattern, "", text, flags=re.I)
    text = re.sub(r"[\[\]{}()]+", "", text) # Удаляем скобки
    text = re.sub(r"\s{2,}", " ", text).strip() # Сжимаем пробелы

    # 2. Разделяем по ключевым разделителям
    parts = re.split(r"[|;]", text)
    compressed, total = [], 0

    for p in parts:
        p = p.strip()
        if not p:
            continue
        
        # 3. Отбрасываем "мусорные" сегменты (например, " | | | ")
        weight = len(re.findall(r"[A-Za-zА-Яа-я]", p)) / max(1, len(p))
        if weight < 0.2:
            continue
            
        # 4. Собираем, пока не достигнем лимита
        if total + len(p) < max_len - 50: # Оставляем буфер
            compressed.append(p)
            total += len(p)
        else:
            break

    compressed_text = " | ".join(compressed).strip()

    # 5. (Опционально) Пытаемся сохранить последнюю строку, если она важна
    if preserve_last_line and "\n" in text:
        try:
            last_line = text.strip().splitlines()[-1]
            if last_line not in compressed_text:
                if len(compressed_text) + len(last_line) + 1 < max_len:
                    compressed_text += "\n" + last_line
        except Exception:
            pass # Игнорируем, если что-то пошло не так

    result = compressed_text[:max_len].strip()
    if not result.endswith("…") and len(text) > max_len:
        result += "…"
        
    log.debug(f"Сжатие: {len(text)} -> {len(result)} символов")
    return result


# -----------------------------------------------------------
# 🎧 RNS safety tag
# -----------------------------------------------------------
def rns_safety_tag(bpm: int, key: str) -> str:
    """Возвращает тег RNS (Resonance–Nervous–Safety) для compliance."""
    safe_keys = ["A", "E", "D", "G"] # A=432Hz, D=288Hz, и т.д.
    base = key.split()[0].upper().replace("♯", "#").replace("♭", "B") if key else "A"
    level = "safe" if base in safe_keys and bpm < 120 else "watch"
    return f"RNS:{level}:{base}@{bpm}"


# -----------------------------------------------------------
# 🧠 Prompt builder (v5 - Suno Формат)
# -----------------------------------------------------------
def build_suno_prompt(
    style_data: Dict[str, Any],
    vocals: List[str] | None,
    instruments: List[str] | None,
    bpm: int,
    philosophy: str,
    version: str,
    prompt_variant: str = "suno_style",
) -> str:
    """
    v5: Генерирует промпты в формате [TAG: value], как просил пользователь.
    """
    log.debug(f"Вызов функции: build_suno_prompt (Variant: {prompt_variant})")

    genre = style_data.get("genre", "adaptive emotional")
    style = style_data.get("style", "free-form tonal flow")
    key = style_data.get("key", "auto")
    atmosphere = style_data.get("atmosphere", "")
    production = style_data.get("visual", "clean mix") # Используем 'visual' как 'production'
    vocal_form = style_data.get("vocal_form", "solo_auto")
    
    vocals = vocals or []
    instruments = instruments or []
    
    # Очищаем вокал от тегов формы (solo, duet...)
    clean_vocals = sorted(list(set(v for v in vocals if v not in [
        "male","female","duet","trio","quartet","quintet","choir","solo"
    ])))
    
    # Добавляем M/F на основе формы
    if "mf" in vocal_form:
        vocal_desc = f"male and female duet ({', '.join(clean_vocals)})"
    elif "_m" in vocal_form:
        vocal_desc = f"male vocal ({', '.join(clean_vocals)})"
    elif "_f" in vocal_form:
        vocal_desc = f"female vocal ({', '.join(clean_vocals)})"
    else: # auto или mixed
        vocal_desc = f"mixed vocals ({', '.join(clean_vocals)})"

    # === [Style of Music] Prompt ===
    if prompt_variant == "suno_style":
        prompt_parts = [
            f"[GENRE: {genre}]",
            f"[MOOD: {atmosphere}]",
            f"[INSTRUMENTATION: {', '.join(instruments)}]",
            f"[VOCAL: {vocal_desc}]",
            f"[PRODUCTION: {production}]",
            f"[BPM: {bpm}]",
            f"[KEY: {key}]"
        ]
        prompt = "\n".join(filter(None, prompt_parts))
        
        max_len = VERSION_LIMITS.get(version.lower(), 1000)
        return semantic_compress(prompt, max_len, preserve_last_line=False)

    # === [Lyrics] Prompt (Vocal Hints) ===
    # (Этот режим больше не используется app.py v8, но мы его оставим)
    elif prompt_variant == "suno_lyrics":
        techniques = style_data.get("techniques", [])
        prompt_parts = [
            vocal_form,
            f"({', '.join(clean_vocals)})",
            f"({', '.join(techniques)})",
        ]
        prompt = ", ".join(filter(lambda x: x != "()" and x, prompt_parts))
        max_len = VERSION_LIMITS.get(version.lower(), 1000)
        return semantic_compress(prompt, max_len, preserve_last_line=False)

    # === [Full Report] Prompt ===
    else: 
        safety_tag = rns_safety_tag(bpm, key)
        emotion_balance = round(abs(style_data.get("complexity_score", 0.5) / 10), 2)
        prompt_id = hashlib.md5(f"{genre}{key}{bpm}{vocal_form}{philosophy}".encode()).hexdigest()[:8]
        
        base_prompt = (
            f"Genre: {genre} | Style: {style} | Key: {key} | BPM: {bpm} | Structure: {style_data.get('structure', 'intro-verse-chorus-outro')}\n"
            f"Vocal Form: {vocal_form} | Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)}\n"
            f"Instruments: {', '.join(instruments)} | Atmosphere: {atmosphere}\n"
            f"Visual: {visual} (Production) | Narrative: {style_data.get('narrative', 'N/A')}\n"
            f"Philosophy: {philosophy}\n"
            f"Safety: {safety_tag} | Emotion Balance: {emotion_balance} | Engine: StudioCore {version}\n"
            f"Prompt ID: {prompt_id}"
        )
        max_len = 5000 if prompt_variant == "full" else 1200
        return semantic_compress(base_prompt, max_len, preserve_last_line=True)

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
