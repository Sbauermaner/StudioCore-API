# -*- coding: utf-8 -*-
"""
StudioCore v5.2.3 — Adaptive StyleMatrix Hybrid
v13: Внедрен централизованный логгер
"""
import logging
from typing import Dict, Any, Tuple
from statistics import mean

# Получаем логгер для этого модуля
log = logging.getLogger(__name__)

# ==========================================================
# 🧠 Адаптивный резолвер стиля (v12)
# ==========================================================
def resolve_style_and_form(
    tlp: Dict[str, float],
    cf: float,
    mood: str,
    bpm: int,
    narrative: Tuple[str, str, str] | None = None,
    key_hint: str | None = None,
    voice_hint: str | None = None,
) -> Dict[str, str]:
    
    log.debug(f"Вызов функции: resolve_style_and_form. Mood={mood}, BPM={bpm}, CF={cf:.2f}, VoiceHint={voice_hint}")
    log.debug(f"TLP: {tlp}")

    love = tlp.get("love", 0.0)
    pain = tlp.get("pain", 0.0)
    truth = tlp.get("truth", 0.0)

    user_mode = bool(voice_hint)
    if user_mode:
        # USER-MODE (на основе вокальных подсказок)
        log.debug("Режим: USER-MODE (по хинту)")
        hint = voice_hint.lower()
        if any(k in hint for k in ["growl", "scream", "хрип", "крич", "grit"]):
            genre, style, key_mode = "metal adaptive", "aggressive growl", "minor"
        elif any(k in hint for k in ["soft", "airy", "whisper", "пескляв", "тихо"]):
            genre, style, key_mode = "ambient lyrical", "soft whisper tone", "major"
        elif any(k in hint for k in ["female", "женск"]):
            genre, style, key_mode = "pop emotional", "bright major", "major"
        elif any(k in hint for k in ["male", "мужск"]):
            genre, style, key_mode = "rock narrative", "warm baritone", "minor"
        else:
            genre, style, key_mode = "cinematic adaptive", "neutral modal", "modal"
    else:
        # AUTO-MODE (на основе TLP, настроения и BPM)
        log.debug("Режим: AUTO-MODE (по TLP/Mood/BPM)")

        # 1. Определение Жанра (v11)
        if (pain >= 0.04 and truth >= 0.05) or cf > 0.9 or mood in ("fear", "anger", "epic"):
            genre = "cinematic adaptive"
        elif bpm >= 120 and pain < 0.2 and (love > 0.1 or mood == "joy"):
            genre = "electronic dance music (EDM)"
        elif (love >= 0.05 and love > pain) or mood == "joy":
            genre = "lyrical adaptive"
        elif (pain >= 0.01 and pain > love) or mood == "sadness":
            genre = "lyrical adaptive"
        else:
            genre = "cinematic narrative" # Запасной вариант

        # 2. Определение Стиля (тональности) (v11)
        if (pain >= 0.04 and truth >= 0.05) or cf > 0.9 or mood == "fear":
            style, key_mode = "dramatic harmonic minor", "minor"
        elif (pain >= 0.01 and pain > love) or mood == "sadness":
            style, key_mode = "melancholic minor", "minor"
        elif (love >= 0.05 and love > pain) or mood == "joy":
            style, key_mode = "majestic major", "major"
        elif genre == "electronic dance music (EDM)":
            style, key_mode = "rhythmic synth lead", "minor"
        else:
            style, key_mode = "neutral modal", "modal"

    log.debug(f"Результат резолвера: Genre={genre}, Style={style}, KeyMode={key_mode}")

    # 3. Атмосфера
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
    elif style == "rhythmic synth lead":
        atmosphere = "energetic and euphoric"
    else:
        atmosphere = "mystic and suspenseful" if cf >= 0.88 else "balanced and reflective"
    log.debug(f"Атмосфера: {atmosphere}")

    # 4. Нарратив
    if narrative:
        phases = "→".join(narrative)
        if "struggle" in phases and "transformation" in phases and cf >= 0.9:
            if not genre.startswith("cinematic"):
                log.debug("Нарратив (struggle→transformation) принудительно включает 'cinematic narrative'")
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
    """Adaptive emotional-to-style mapping engine (v13, +EDM, +Logging)."""

    def build(
        self,
        emo: Dict[str, float],
        tlp: Dict[str, float],
        text: str,
        bpm: int,
        overlay: Dict[str, Any] | None = None,
        voice_hint: str | None = None, # v4.3: хинт приходит из монолита
    ) -> Dict[str, Any]:
        
        log.debug(f"Вызов функции: PatchedStyleMatrix.build. BPM={bpm}")
        cf = tlp.get("conscious_frequency", 0.0)
        dominant = max(emo, key=emo.get) if emo else "neutral"

        # 🔹 v4.3: Вокальный намёк теперь приходит из monolith_v4_3_1
        # (в monolith он берется из overlay ИЛИ auto-detect)
        log.debug(f"Получен вокальный хинт: {voice_hint}")
        
        narrative = ("search", "struggle", "transformation")
        
        resolved = resolve_style_and_form(
            tlp, cf, dominant, bpm, narrative, voice_hint=voice_hint
        )

        # 🎼 Ключ
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        scale = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        index_shift = int(((bpm / 10) + (l * 6) - (p * 4) + cf * 5) % 12)
        key_name = scale[index_shift]
        key = f"{key_name} ({key_name} {resolved['key_mode']})"
        log.debug(f"Ключ: {key} (на основе BPM={bpm}, L={l}, P={p}, CF={cf})")

        # 🎨 Визуал
        visuals = {
            "majestic major": "warm light, sunrise reflections, hands touching",
            "melancholic minor": "rain, fog, silhouettes, slow motion",
            "dramatic harmonic minor": "light and shadow interplay, emotional contrasts, dynamic framing",
            "aggressive growl": "fire, smoke, chaos, sharp cuts",
            "soft whisper tone": "blurred lights, feathers, close-up breathing",
            "rhythmic synth lead": "neon lights, strobing, crowd dancing, fast motion"
        }
        visual = visuals.get(resolved["style"], "shifting colors, abstract transitions")

        # 🎤 Вокальные техники
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
            else:
                techniques += ["neutral blend", "harmonic balance"]
        else:
            log.debug("Применяем AUTO-MODE техники")
            if resolved["style"] == "rhythmic synth lead":
                techniques += ["processed vocal", "melodic rap", "layered harmonies"]
            elif emo.get("anger", 0) > 0.4 or resolved["style"].startswith("dramatic"):
                techniques += ["belt", "rasp", "grit"]
            if emo.get("sadness", 0) > 0.3 or p > 0.4:
                techniques += ["vibrato", "soft cry"]
            if emo.get("joy", 0) > 0.3 or l > 0.3:
                techniques += ["falsetto", "bright tone"]
            if not techniques:
                techniques += ["resonant layering", "harmonic blend"]
        
        log.debug(f"Техники: {techniques}")

        complexity_score = round(mean([emo[k] for k in emo]) * 10, 2) if emo else 0.5
        color_temperature = "warm" if l >= p else "cold"
        adaptive_mode = "USER-MODE" if resolved["user_mode"] else ("stable" if cf > 0.6 else "transient")

        # Финальный результат
        result_dict = {
            "genre": resolved["genre"],
            "style": resolved["style"],
            "key": key,
            "structure": "intro-verse-chorus-outro",
            "visual": visual,
            "narrative": "→".join(narrative),
            "atmosphere": resolved["atmosphere"],
            "techniques": sorted(list(set(techniques))), # Убираем дубликаты
            "complexity_score": complexity_score,
            "color_temperature": color_temperature,
            "adaptive_mode": adaptive_mode,
        }
        log.debug(f"Style.build завершен: {result_dict}")
        return result_dict


# ==========================================================
# ✅ Meta
# ==========================================================
STYLE_VERSION = "v5.2.3 adaptive hybrid (USER-MODE + AutoDetect)"
log.info(f"🎨 [PatchedStyleMatrix {STYLE_VERSION}] loaded successfully.")


# ==========================================================
# 🔄 Compatibility alias for older Monolith imports
# ==========================================================
try:
    StyleMatrix # type: ignore
except NameError:
    try:
        StyleMatrix = PatchedStyleMatrix
        log.info("🎨 [StyleMatrix alias] PatchedStyleMatrix → StyleMatrix (compat mode active)")
    except Exception as e:
        log.warning(f"⚠️ [StyleMatrix alias] failed: {e}")