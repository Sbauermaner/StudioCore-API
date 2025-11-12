# -*- coding: utf-8 -*-
"""
StudioCore v5.2.3 — Adaptive StyleMatrix Hybrid (USER-MODE + Auto Voice Detection)
Интеграция автоматического распознавания вокальных описаний в текстах.
Позволяет ядру StudioCore адаптировать жанр, стиль, атмосферу и вокальные техники
в зависимости от Truth/Love/Pain, Conscious Frequency и пользовательских описаний вокала.

ИСПРАВЛЕНИЕ v5 (ФИНАЛ): Перестроена логика if/elif для
корректного определения LOVE/JOY/PAIN. (PAIN > LOVE)
"""

import re
from typing import Dict, Any, Tuple
from statistics import mean


# ==========================================================
# 🗣️ Автоматическое распознавание вокального описания
# ==========================================================
def detect_voice_profile(text: str) -> str | None:
    """
    Автоматически определяет вокальные подсказки из текста.
    Возвращает строку с описанием (например, "под хриплый мужской вокал")
    или None, если ничего не найдено.
    """
    text_low = text.lower()
    # Типичные шаблоны описаний вокала
    patterns = [
        r"под\s+[а-яa-z\s,]+вокал",          # под хриплый мужской вокал
        r"\(.*(вокал|voice|growl|scream).*\)",   # (soft female growl)
        r"(мужск\w+|женск\w+)\s+вокал",
        r"(soft|airy|raspy|grit|growl|scream|whisper)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            hint = match.group(0).strip("() ")
            print(f"🎙️ [AutoDetect] Найдено описание вокала: {hint}")
            return hint
    return None


# ==========================================================
# 🧠 Новый адаптивный резолвер стиля (с поддержкой USER-MODE)
# ==========================================================
def resolve_style_and_form(
    tlp: Dict[str, float],
    cf: float,
    mood: str, # 'mood' - это dominant emotion
    narrative: Tuple[str, str, str] | None = None,
    key_hint: str | None = None,
    voice_hint: str | None = None,
) -> Dict[str, str]:
    love = tlp.get("love", 0.0)
    pain = tlp.get("pain", 0.0)
    truth = tlp.get("truth", 0.0)

    user_mode = bool(voice_hint)
    if user_mode:
        hint = voice_hint.lower()
        if any(k in hint for k in ["growl", "scream", "хрип", "крич", "grit"]):
            genre = "metal adaptive"
            style, key_mode = "aggressive growl", "minor"
        elif any(k in hint for k in ["soft", "airy", "whisper", "пескляв", "тихо"]):
            genre = "ambient lyrical"
            style, key_mode = "soft whisper tone", "major"
        elif any(k in hint for k in ["female", "женск"]):
            genre = "pop emotional"
            style, key_mode = "bright major", "major"
        elif any(k in hint for k in ["male", "мужск"]):
            genre = "rock narrative"
            style, key_mode = "warm baritone", "minor"
        else:
            genre = "cinematic adaptive"
            style, key_mode = "neutral modal", "modal"
    else:
        # AUTO-MODE (эмоциональный анализ)
        
        # --- ИСПРАВЛЕНИЕ ЛОГИКИ ЖАНРА v5 ---
        if cf > 0.9 or pain >= 0.04 or mood in ("intense", "angry", "dramatic"):
            genre = "cinematic adaptive"
        # Сначала проверяем LOVE/JOY
        elif (love >= 0.05 or mood == "joy") and (love > pain):
            genre = "lyrical adaptive"
        # Потом проверяем PAIN
        elif (pain >= 0.01 or mood in ("melancholy", "sad")) and (pain > love):
            genre = "lyrical adaptive"
        # Иначе - default
        else:
            genre = "cinematic narrative"

        # --- ИСПРАВЛЕНИЕ ЛОГИКИ СТИЛЯ v5 ---
        if cf >= 0.92 or (pain >= 0.04 and truth >= 0.05) or mood in ("intense", "angry", "dramatic"):
            style, key_mode = "dramatic harmonic minor", "minor"
        # Сначала проверяем LOVE/JOY (love > pain)
        elif (love >= 0.05 or mood == "joy") and (love > pain):
            style, key_mode = "majestic major", "major"
        # Потом проверяем PAIN (pain > love)
        elif (pain >= 0.01 or mood in ("melancholy", "sad")) and (pain > love):
            style, key_mode = "melancholic minor", "minor"
        # Иначе - default
        else:
            style, key_mode = "neutral modal", "modal"

    # Атмосфера
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
    elif style == "neutral modal":
        atmosphere = "balanced and reflective"
    else:
        atmosphere = "mystic and suspenseful" if cf >= 0.88 else "balanced and reflective"

    # Нарратив
    if narrative:
        phases = "→".join(narrative)
        if "struggle" in phases and "transformation" in phases and cf >= 0.9:
            if not genre.startswith("cinematic"):
                genre = "cinematic narrative"

    return {
        "genre": genre,
        "style": style,
        "key_mode": key_mode,
        "atmosphere": atmosphere,
        "user_mode": user_mode,
    }


# ==========================================================
# 🎨 PatchedStyleMatrix (v5.2.3) с автоопределением вокала
# ==========================================================
class PatchedStyleMatrix:
    """Adaptive emotional-to-style mapping engine (hybrid v5.2.3, USER-MODE + AutoDetect)."""

    def build(
        self,
        emo: Dict[str, float],
        tlp: Dict[str, float],
        text: str,
        bpm: int,
        overlay: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        cf = tlp.get("conscious_frequency", 0.0)
        dominant = max(emo, key=emo.get) if emo else "neutral"

        # 🔹 Определяем вокальный намёк (из overlay или автоматически)
        voice_hint = None
        if overlay and "voice_profile_hint" in overlay:
            voice_hint = overlay["voice_profile_hint"]
        else:
            voice_hint = detect_voice_profile(text)

        narrative = ("search", "struggle", "transformation")
        # Передаем 'dominant' (эмоцию) в резолвер
        resolved = resolve_style_and_form(tlp, cf, dominant, narrative, voice_hint=voice_hint)

        # 🎼 Ключ
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        scale = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        index_shift = int(((bpm / 10) + (l * 6) - (p * 4) + cf * 5) % 12)
        key = f"{scale[index_shift]} ({scale[index_shift]} {resolved['key_mode']})"

        # 🎨 Визуал
        visuals = {
            "majestic major": "warm light, sunrise reflections, hands touching",
            "melancholic minor": "rain, fog, silhouettes, slow motion",
            "dramatic harmonic minor": "light and shadow interplay, emotional contrasts, dynamic framing",
            "aggressive growl": "fire, smoke, chaos, sharp cuts",
            "soft whisper tone": "blurred lights, feathers, close-up breathing",
            "neutral modal": "shifting colors, abstract transitions"
        }
        visual = visuals.get(resolved["style"], "shifting colors, abstract transitions")

        # 🎤 Вокальные техники
        techniques = []
        if resolved["user_mode"] and voice_hint:
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
            if emo.get("anger", 0) > 0.4 or resolved["style"].startswith("dramatic"):
                techniques += ["belt", "rasp", "grit"]
            if emo.get("sadness", 0) > 0.3 or p > 0.4:
                techniques += ["vibrato", "soft cry"]
            if emo.get("joy", 0) > 0.3 or l > 0.3:
                techniques += ["falsetto", "bright tone"]
            if not techniques:
                techniques += ["resonant layering", "harmonic blend"]

        complexity_score = round(mean([emo[k] for k in emo]) * 10, 2) if emo else 0.5
        color_temperature = "warm" if l >= p else "cold"
        adaptive_mode = "USER-MODE" if resolved["user_mode"] else ("stable" if cf > 0.6 else "transient")

        return {
            "genre": resolved["genre"],
            "style": resolved["style"],
            "key": key,
            "structure": "intro-verse-chorus-outro",
            "visual": visual,
            "narrative": "→".join(narrative),
            "atmosphere": resolved["atmosphere"],
            "techniques": techniques,
            "complexity_score": complexity_score,
            "color_temperature": color_temperature,
            "adaptive_mode": adaptive_mode,
        }


# ==========================================================
# ✅ Meta
# ==========================================================
STYLE_VERSION = "v5.2.3 adaptive hybrid (USER-MODE + AutoDetect)"
print(f"🎨 [PatchedStyleMatrix {STYLE_VERSION}] loaded successfully.")


# ==========================================================
# 🔄 Compatibility alias for older Monolith imports
# ==========================================================
try:
    StyleMatrix
except NameError:
    try:
        StyleMatrix = PatchedStyleMatrix
        print("🎨 [StyleMatrix alias] PatchedStyleMatrix → StyleMatrix (compat mode active)")
    except Exception as e:
        print(f"⚠️ [StyleMatrix alias] failed: {e}")