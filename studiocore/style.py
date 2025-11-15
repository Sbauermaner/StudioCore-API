# -*- coding: utf-8 -*-
"""
StudioCore v5.2.3 — Adaptive StyleMatrix Hybrid (v12 - NameError ИСПРАВЛЕН)
v12: Исправлена ошибка NameError: 'energy' is not defined.
     Логика EDM временно упрощена (только по BPM).
"""

from typing import Dict, Any, Tuple, List
from statistics import mean
import logging

log = logging.getLogger(__name__)

# ==========================================================
# 🧠 Адаптивный резолвер стиля (v12)
# ==========================================================
def resolve_style_and_form(
    tlp: Dict[str, float],
    cf: float,
    mood: str, # Доминирующая эмоция из AutoEmotionalAnalyzer
    bpm: int,
    narrative: Tuple[str, str, str] | None = None,
    key_hint: str | None = None,
    voice_hint: str | None = None,
) -> Dict[str, str]:
    """
    v12: Исправлена ошибка NameError: 'energy' is not defined.
    """
    log.debug(f"Вызов функции: resolve_style_and_form. Mood={mood}, BPM={bpm}, CF={cf:.2f}, VoiceHint={voice_hint}")
    log.debug(f"TLP: {tlp}")
    
    love = tlp.get("love", 0.0)
    pain = tlp.get("pain", 0.0)
    truth = tlp.get("truth", 0.0)

    user_mode = bool(voice_hint)
    
    # ---------------------------------
    # 1. USER-MODE (Прямые хинты)
    # ---------------------------------
    if user_mode and voice_hint:
        log.debug("Режим: USER-MODE (по хинту)")
        hint = voice_hint.lower()
        
        if any(k in hint for k in ["growl", "scream", "хрип", "крич", "grit", "metal"]):
            genre, style, key_mode = "metal adaptive", "aggressive growl", "minor"
        elif any(k in hint for k in ["soft", "airy", "whisper", "шепот", "тихо"]):
            genre, style, key_mode = "ambient lyrical", "soft whisper tone", "major"
        elif any(k in hint for k in ["female", "женск"]):
            genre, style, key_mode = "pop emotional", "bright major", "major"
        elif any(k in hint for k in ["male", "мужск"]):
            genre, style, key_mode = "rock narrative", "warm baritone", "minor"
        elif any(k in hint for k in ["rap", "рэп", "хип-хоп"]):
            genre, style, key_mode = "hip-hop", "rhythmic flow", "minor"
        elif any(k in hint for k in ["edm", "dance", "house", "trance"]):
             genre, style, key_mode = "edm", "uplifting electronic", "minor"
        else:
            genre, style, key_mode = "cinematic adaptive", "neutral modal", "modal"
    
    # ---------------------------------
    # 2. AUTO-MODE (Анализ TLP/Mood/BPM)
    # ---------------------------------
    else:
        log.debug("Режим: AUTO-MODE (по TLP/Mood/BPM)")
        
        # --- Определение СТИЛЯ (v11-logic) ---
        # СНАЧАЛА проверяем PAIN (v8 fix)
        if (pain >= 0.01 and pain > love) or mood in ("sadness", "melancholy"): 
            style, key_mode = "melancholic minor", "minor"
            log.debug("Стиль: 'melancholic minor' (Pain > Love или Mood=sadness)")
            
        elif (love >= 0.01 and love >= pain) or mood in ("joy", "peace", "awe"):
            style, key_mode = "majestic major", "major"
            log.debug("Стиль: 'majestic major' (Love >= Pain или Mood=joy/peace)")

        elif (cf > 0.6 and truth > 0.1) or mood in ("anger", "fear", "epic"):
            style, key_mode = "dramatic harmonic minor", "minor"
            log.debug("Стиль: 'dramatic harmonic minor' (CF/Truth или Mood=anger/fear/epic)")
            
        else:
            style, key_mode = "neutral modal", "modal"
            log.debug("Стиль: 'neutral modal' (по умолчанию)")

        # --- Определение ЖАНРА (v12-logic) ---
        
        # v12: Исправлен NameError. Убрана 'energy'.
        if bpm > 115 and pain < 0.2 and mood not in ("sadness", "anger", "fear"):
             genre = "edm"
             log.debug("Жанр: 'edm' (Высокий BPM + Низкий Pain/Fear)")
        
        elif style == "melancholic minor":
            genre = "lyrical adaptive"
            log.debug("Жанр: 'lyrical adaptive' (Стиль=melancholic)")

        elif style == "majestic major":
            genre = "lyrical adaptive"
            log.debug("Жанр: 'lyrical adaptive' (Стиль=majestic)")
            
        elif style == "dramatic harmonic minor":
            genre = "cinematic adaptive"
            log.debug("Жанр: 'cinematic adaptive' (Стиль=dramatic)")
            
        else: # neutral modal
            genre = "cinematic narrative"
            log.debug("Жанр: 'cinematic narrative' (Стиль=neutral)")

    log.debug(f"Результат резолвера: Genre={genre}, Style={style}, KeyMode={key_mode}")

    # ---------------------------------
    # 3. Атмосфера
    # ---------------------------------
    if style == "majestic major":
        atmosphere = "serene and hopeful"
    elif style == "melancholic minor":
        atmosphere = "introspective and melancholic"
    elif style == "dramatic harmonic minor":
        atmosphere = "intense and cathartic"
    elif style == "aggressive growl":
        atmosphere = "tense and raw"
    elif style == "soft whisper tone":
        atmosphere = "fragile and ethereal"
    elif genre == "edm":
        atmosphere = "energetic and uplifting"
    else:
        atmosphere = "mystic and suspenseful" if cf >= 0.88 else "balanced and reflective"
    
    log.debug(f"Атмосфера: {atmosphere}")

    # ---------------------------------
    # 4. Нарратив (без изменений)
    # ---------------------------------
    if narrative:
        phases = "→".join(narrative)
        if "struggle" in phases and "transformation" in phases and cf >= 0.9:
            if not genre.startswith("cinematic"):
                log.debug("Нарратив 'struggle→transformation' привел к смене жанра на 'cinematic narrative'")
                genre = "cinematic narrative"

    return {
        "genre": genre,
        "style": style,
        "key_mode": key_mode,
        "atmosphere": atmosphere,
        "user_mode": user_mode,
    }


# ==========================================================
# 🎨 PatchedStyleMatrix (v5.2.3)
# ==========================================================
class PatchedStyleMatrix:
    """Adaptive emotional-to-style mapping engine (v12 Logged)."""

    def build(
        self,
        emo: Dict[str, float],
        tlp: Dict[str, float],
        text: str,
        bpm: int,
        semantic_hints: Dict[str, Any] | None = None,
        voice_hint: str | None = None, # v4.3: Принимает хинт от monolith
    ) -> Dict[str, Any]:
        
        log.debug(f"Вызов функции: PatchedStyleMatrix.build. BPM={bpm}")
        
        cf = tlp.get("conscious_frequency", 0.0)
        # v11: Mood (доминирующая эмоция) стал важнее
        dominant_mood = max(emo, key=emo.get) if emo else "peace"
        log.debug(f"Доминирующая эмоция: {dominant_mood}")

        log.debug(f"Получен вокальный хинт: {voice_hint}")

        # 1. 🧠 Вызов Резолвера
        narrative = ("search", "struggle", "transformation")
        resolved = resolve_style_and_form(
            tlp, cf, dominant_mood, bpm, narrative, 
            key_hint=None, voice_hint=voice_hint
        )

        # 2. 🎼 Определение Ключа (Тональности)
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        scale = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        # (v10) Упрощенная и более предсказуемая логика ключа
        
        # v12: Приоритет минора, если mood/style минорный
        if resolved['key_mode'] == "minor":
            index_shift = int(((bpm / 15) + (p * 5) + (t * 2)) % 12)
        else: # major или modal
            index_shift = int(((bpm / 12) + (l * 6) - (p * 2)) % 12)
            
        key = f"{scale[index_shift]} ({scale[index_shift]} {resolved['key_mode']})"
        log.debug(f"Ключ: {key} (на основе BPM={bpm}, L={l}, P={p}, CF={cf})")

        # 3. 🎨 Визуал
        visuals = {
            "majestic major": "warm light, sunrise reflections, hands touching",
            "melancholic minor": "rain, fog, silhouettes, slow motion",
            "dramatic harmonic minor": "light and shadow interplay, emotional contrasts, dynamic framing",
            "aggressive growl": "fire, smoke, chaos, sharp cuts",
            "soft whisper tone": "blurred lights, feathers, close-up breathing",
            "rhythmic flow": "city night lights, graffiti, street motion",
            "neutral modal": "shifting colors, abstract transitions",
            "uplifting electronic": "neon lights, fast motion, club atmosphere",
        }
        visual = visuals.get(resolved["style"], "shifting colors, abstract transitions")

        # 4. 🎤 Вокальные техники
        techniques = []
        if resolved["user_mode"] and voice_hint:
            log.debug("Применяем USER-MODE техники")
            hint = voice_hint.lower()
            if any(k in hint for k in ["growl", "scream", "хрип", "grit"]):
                techniques += ["growl", "scream", "chest drive"]
            elif any(k in hint for k in ["soft", "airy", "whisper", "пескляв"]):
                techniques += ["soft tone", "breathy", "close mic"]
            elif any(k in hint for k in ["female", "женск"]):
                techniques += ["falsetto", "head voice", "resonance control"]
            elif any(k in hint for k in ["male", "мужск"]):
                techniques += ["baritone layer", "grit", "projection"]
            elif any(k in hint for k in ["rap", "рэп"]):
                techniques += ["spoken word", "fast flow", "rhythmic delivery"]
            else:
                techniques += ["neutral blend", "harmonic balance"]
        else:
            log.debug("Применяем AUTO-MODE техники")
            # Основано на TLP и Emo
            if emo.get("anger", 0) > 0.3 or resolved["style"].startswith("dramatic"):
                techniques += ["belt", "rasp", "grit"]
            if emo.get("sadness", 0) > 0.3 or p > 0.3:
                techniques += ["vibrato", "soft cry"]
            if emo.get("joy", 0) > 0.3 or l > 0.3:
                techniques += ["falsetto", "bright tone"]
            if emo.get("epic", 0) > 0.3:
                techniques += ["choral layering", "powerful projection"]
            if resolved["genre"] == "edm":
                techniques += ["processed vocal", "staccato", "vocal chop"]
            if not techniques:
                techniques += ["resonant layering", "harmonic blend"]
        
        techniques = sorted(list(set(techniques))) # Убираем дубликаты
        log.debug(f"Техники: {techniques}")

        # 5. 📊 Мета-данные
        complexity_score = round(mean([emo[k] for k in emo]) * 10, 2) if emo else 0.5
        color_temperature = "warm" if l >= p else "cold"
        adaptive_mode = "USER-MODE" if resolved["user_mode"] else ("stable" if cf > 0.6 else "transient")
        
        # v12: Передаем BPM из резолвера, если он был изменен
        bpm_final = resolved.get("bpm", bpm) 

        result = {
            "genre": resolved["genre"],
            "style": resolved["style"],
            "key": key,
            "bpm": bpm_final, # v12
            "structure": "intro-verse-chorus-outro", 
            "visual": visual,
            "narrative": "→".join(narrative),
            "atmosphere": resolved["atmosphere"],
            "techniques": techniques,
            "complexity_score": complexity_score,
            "color_temperature": color_temperature,
            "adaptive_mode": adaptive_mode,
        }
        log.debug(f"Style.build завершен: {result}")
        return result


# ==========================================================
STYLE_VERSION = "v5.2.3 adaptive hybrid (USER-MODE + AutoDetect)"
log.info(f"🎨 [PatchedStyleMatrix {STYLE_VERSION}] loaded successfully.")

# ==========================================================
# 🔄 Compatibility alias
# ==========================================================
try:
    StyleMatrix # type: ignore
except NameError:
    try:
        StyleMatrix = PatchedStyleMatrix
        log.info("🎨 [StyleMatrix alias] PatchedStyleMatrix → StyleMatrix (compat mode active)")
    except Exception as e:
        log.warning(f"⚠️ [StyleMatrix alias] failed: {e}")