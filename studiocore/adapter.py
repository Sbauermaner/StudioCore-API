# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""
StudioCore v5.2 — Suno / Studio Adaptive Adapter (v5 - NameError ИСПРАВЛЕН)
Semantic compression · RNS safety · Dynamic prompt formatting
"""

import re
import hashlib
from typing import Dict, Any, List, Optional
import logging

log = logging.getLogger(__name__)

# === ИСПРАВЛЕНИЕ (NameError) ===
# Эта константа была потеряна при рефакторинге
VERSION_LIMITS: Dict[str, int] = {"v3": 200, "v3.5": 200, "v4": 500, "v5": 1000}
# === Конец исправления ===

# -----------------------------------------------------------
# ✂️ Semantic compression engine
# -----------------------------------------------------------


def semantic_compress(
    text: str, max_len: int = 1000, preserve_last_line: bool = True
) -> str:
    """
    Сжимает текст, сохраняя структуру и эмоциональный контекст.
    """
    log.debug(f"Вызов semantic_compress: max_len={max_len}")
    if len(text) <= max_len:
        return text.strip()

    # 1. Удаляем "шумные" слова
    noise_pattern = r"\b(beautiful|amazing|very|extremely|really|truly|highly|deeply|incredibly|wonderful|great|awesome|nice|so|such|quite|pretty)\b"
    text = re.sub(noise_pattern, "", text, flags=re.I)
    text = re.sub(r"[\[\]{}()]+", "", text)  # Удаляем скобки
    text = re.sub(r"\s{2,}", " ", text).strip()  # Сжимаем пробелы

    # 2. Разделяем по ключевым разделителям
    parts = re.split(r"[|;]", text)
    compressed, total = [], 0

    for p in parts:
        p = p.strip()
        if not p:
            continue

        # 3. Отбрасываем "мусорные" сегменты (например, " | | | ")
        weight = len(re.findall(r"[A - Za - zА - Яа - я]", p)) / max(1, len(p))
        if weight < 0.2:
            continue

        # 4. Собираем, пока не достигнем лимита
        if total + len(p) < max_len - 50:  # Оставляем буфер
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
        except (ValueError, IndexError, AttributeError) as e:
            # Task 14.1: Log error instead of silent pass
            log.debug(f"Ошибка при сжатии текста: {e}")
            # Возвращаем исходный текст, если сжатие не удалось
            # Continue with compressed_text as is

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
    safe_keys = ["A", "E", "D", "G"]  # A=432Hz, D=288Hz, и т.д.
    base = key.split()[0].upper().replace("♯", "  #").replace("♭", "B") if key else "A"
    level = "safe" if base in safe_keys and bpm < 120 else "watch"
    return f"RNS:{level}:{base}@{bpm}"


# -----------------------------------------------------------
# 🧠 Prompt builder (v5 - Suno Формат)
# -----------------------------------------------------------


def build_suno_prompt(
    style_data: Dict[str, Any],
    vocals: Optional[List[str]],
    instruments: Optional[List[str]],
    bpm: int,
    philosophy: str,
    version: str,
    prompt_variant: str = "suno_style",
) -> str:
    """
    v5: Генерирует промпты в формате [TAG: value], как просил пользователь.
    """
    log.debug(f"Вызов функции: build_suno_prompt (Variant: {prompt_variant})")

    style_data = dict(style_data or {})
    genre = style_data.get("genre", "adaptive emotional")
    style = style_data.get("style", "free - form tonal flow")
    key = style_data.get("key", "auto")
    atmosphere = style_data.get("atmosphere", "")
    visual = style_data.get("visual", "clean mix")
    production = visual  # Используем 'visual' как 'production'
    vocal_form = style_data.get("vocal_form", "solo_auto")
    techniques = style_data.get("techniques", [])

    vocals = vocals or []
    instruments = instruments or []

    # Очищаем вокал от тегов формы (solo, duet...)
    clean_vocals = sorted(
        list(
            set(
                v
                for v in vocals
                if v
                not in [
                    "male",
                    "female",
                    "duet",
                    "trio",
                    "quartet",
                    "quintet",
                    "choir",
                    "solo",
                ]
            )
        )
    )

    # Инициализируем vocal_desc
    vocal_desc = None
    
    # Определяем vocal на основе эмоций и TLP (если доступны)
    emotions = style_data.get("emotions")
    tlp = style_data.get("tlp")
    vocal_result = style_data.get("vocal_result") or {}
    
    # Используем vocal_result если доступен
    if isinstance(vocal_result, dict):
        vocal_gender = vocal_result.get("gender", "auto")
        vocal_style = vocal_result.get("style", "standard")
        vocal_tone = vocal_result.get("tone", "neutral")
    else:
        vocal_gender = "auto"
        vocal_style = "standard"
        vocal_tone = "neutral"
    
    # Если есть эмоции и TLP, используем их для определения vocal
    if emotions and isinstance(emotions, dict) and len(emotions) > 0:
        try:
            from .suno_annotations import emotion_to_vocal
            
            # Находим доминирующую эмоцию
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Получаем vocal описание на основе эмоции
            emotion_vocal = emotion_to_vocal(dominant_emotion)
            
            # Если emotion_to_vocal вернул что-то кроме "auto", используем это
            if emotion_vocal and emotion_vocal != "auto":
                # Определяем gender на основе техник
                if "female" in emotion_vocal.lower() or "soprano" in emotion_vocal.lower() or "alto" in emotion_vocal.lower():
                    vocal_gender = "female"
                elif "male" in emotion_vocal.lower() or "tenor" in emotion_vocal.lower() or "baritone" in emotion_vocal.lower() or "bass" in emotion_vocal.lower():
                    vocal_gender = "male"
                
                # Используем emotion_vocal как основу для vocal_desc
                if clean_vocals:
                    vocal_desc = f"{emotion_vocal} ({', '.join(clean_vocals)})"
                else:
                    vocal_desc = emotion_vocal
            else:
                # Fallback на TLP если emotion_to_vocal не дал результата
                if tlp and isinstance(tlp, dict):
                    love = tlp.get("love", 0.0)
                    pain = tlp.get("pain", 0.0)
                    truth = tlp.get("truth", 0.0)
                    
                    if love > 0.6:
                        vocal_gender = "female"
                        vocal_style = "soft"
                        vocal_tone = "warm"
                    elif pain > 0.6:
                        vocal_gender = "male"
                        vocal_style = "harsh"
                        vocal_tone = "dark"
                    elif truth > 0.6:
                        vocal_gender = "male"
                        vocal_style = "clear"
                        vocal_tone = "clear"
        except (ImportError, AttributeError, Exception) as e:
            log.debug(f"[Adapter] Could not use emotions/TLP for vocal: {e}")
    
    # Формируем vocal_desc на основе определенных параметров (если еще не определен)
    if not vocal_desc:
        # Используем определенные параметры
        gender_part = ""
        if vocal_gender == "female":
            gender_part = "female"
        elif vocal_gender == "male":
            gender_part = "male"
        
        style_part = vocal_style if vocal_style != "standard" else ""
        tone_part = vocal_tone if vocal_tone != "neutral" else ""
        
        if "mf" in vocal_form:
            vocal_desc = "male and female duet"
        elif "_m" in vocal_form or vocal_gender == "male":
            vocal_desc = "male vocal"
        elif "_f" in vocal_form or vocal_gender == "female":
            vocal_desc = "female vocal"
        else:
            vocal_desc = f"{gender_part or 'auto'} vocal" if gender_part else "auto vocal"
        
        # Добавляем style и tone
        if style_part or tone_part:
            style_tone = ", ".join([p for p in [style_part, tone_part] if p])
            vocal_desc += f", {style_tone}"
        
        # Добавляем clean_vocals если есть
        if clean_vocals:
            vocal_desc += f" ({', '.join(clean_vocals)})"

    # === [Style of Music] Prompt ===
    if prompt_variant == "suno_style":
        prompt_parts = [
            f"[GENRE: {genre}]",
            f"[MOOD: {atmosphere}]",
            f"[INSTRUMENTATION: {', '.join(instruments)}]",
            f"[VOCAL: {vocal_desc}]",
            f"[PRODUCTION: {production}]",
            f"[BPM: {bpm}]",
            f"[KEY: {key}]",
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
        prompt_id = hashlib.md5(
            f"{genre}{key}{bpm}{vocal_form}{philosophy}".encode()
        ).hexdigest()[:8]

        base_prompt = (
            f"Genre: {genre} | Style: {style} | Key: {key} | BPM: {bpm} | Structure: {style_data.get('structure', 'intro - verse - chorus - outro')}\n"
            f"Vocal Form: {vocal_form} | Vocals: {', '.join(vocals)} | Techniques: {', '.join(techniques)}\n"
            f"Instruments: {', '.join(instruments)} | Atmosphere: {atmosphere}\n"
            f"Visual: {visual} (Production) | Narrative: {style_data.get('narrative', 'N / A')}\n"
            f"Philosophy: {philosophy}\n"
            f"Safety: {safety_tag} | Emotion Balance: {emotion_balance} | Engine: StudioCore {version}\n"
            f"Prompt ID: {prompt_id}"
        )
        max_len = 5000 if prompt_variant == "full" else 1200
        return semantic_compress(base_prompt, max_len, preserve_last_line=True)


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
