# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
"""
StudioCore Monolith (v6 - Suno Аннотации)
- Исправлена ошибка f - string (строка 259)
- Внедрено централизованное логирование
- Внедрена Suno - аннотация в 'annotate_text'
- Task 6.2: Version now imported from config.py
"""

import re
import time
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import logging

# === 1. Импорт ядра ===
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

# AI_TRAINING_PROHIBITED: Redistribution or training of AI models on this codebase
# without explicit written permission from the Author is prohibited.

from .config import DEFAULT_CONFIG, load_config

# Task 6.2: Import version from config instead of hardcoding
MONOLITH_VERSION = DEFAULT_CONFIG.MONOLITH_VERSION
STUDIOCORE_VERSION = DEFAULT_CONFIG.STUDIOCORE_VERSION

# v16: ИСПРАВЛЕН ImportError
from .text_utils import normalize_text_preserve_symbols, extract_raw_blocks

# v15: Исправлен ImportError (возвращаем оригинальные имена)
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from .tone import ToneSyncEngine
from .vocals import VocalProfileRegistry
from .integrity import (
    IntegrityScanEngine as FullIntegrityScanEngine,
)  # Импорт движка V6
from .rhythm import LyricMeter

# v11: 'PatchedStyleMatrix' - это наш 'StyleMatrix'
from .style import PatchedStyleMatrix
from .color_engine_adapter import ColorEngineAdapter
from .rde_engine import RhythmDynamicsEmotionEngine
# Task 18.1: Import conflict resolution classes
from .consistency_v8 import ConsistencyLayerV8
from .genre_conflict_resolver import GenreConflictResolver

# === 2. Настройка логгера ===
log = logging.getLogger(__name__)

# ==========================================================
# 🗣️ Утилиты определения вокала (v2 - перенесено из style.py)
# ==========================================================


def detect_voice_profile(text: str) -> Optional[str]:
    """
    Автоматически определяет вокальные подсказки из текста.
    """
    log.debug("Вызов функции: detect_voice_profile")
    text_low = text.lower()
    patterns = [
        r"под\s+[а - яa - z\s,]+вокал",  # под хриплый мужской вокал
        # (soft female growl)
        r"\([\s\S]*?(вокал|voice|growl|scream|ш[её]пот|крик)[\s\S]*?\)",
        r"(мужск\w+|женск\w+)\s + вокал",
        r"(soft|airy|raspy|grit|growl|scream|whisper)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            hint = match.group(0).strip("() ")
            log.debug(f"Описание вокала найдено: {hint}")
            return hint

    log.debug("Описание вокала не найдено.")
    return None


def detect_gender_from_grammar(text: str) -> Optional[str]:
    """
    Определяет пол по грамматике ("я шел" / "я шла")
    """
    log.debug("Вызов функции: detect_gender_from_grammar")
    male_verbs = len(re.findall(r"\b(я\s+\w + л)\b", text, re.I))
    female_verbs = len(re.findall(r"\b(я\s+\w + ла)\b", text, re.I))
    log.debug(
        f"Грамматический анализ: Male хиты={male_verbs}, Female хиты={female_verbs}"
    )

    if male_verbs > female_verbs:
        log.debug("Грамматика определена: male")
        return "male"
    if female_verbs > male_verbs:
        log.debug("Грамматика определена: female")
        return "female"
    if male_verbs > 0 and male_verbs == female_verbs:
        log.debug("Грамматика определена: mixed")
        return "mixed"

    log.debug("Грамматика не определена (auto)")
    return "auto"


# ==========================================================
# 🔹 Локальные подсистемы
# (Мы используем их, чтобы не импортировать rhythm.py и т.д. в тестах)
# ==========================================================


class PatchedLyricMeter:
    """Обёртка над новым LyricMeter для обратной совместимости."""

    def __init__(self) -> None:
        self._engine = LyricMeter()

    def analyze(
        self,
        text: str,
        *,
        emotions: Optional[Dict[str, float]] = None,
        cf: Optional[float] = None,
        tlp: Optional[Dict[str, float]] = None,
        header_bpm: Optional[float] = None,
    ):
        log.debug("Вызов функции: PatchedLyricMeter.analyze")
        tlp = tlp or {}
        if cf is None:
            cf = tlp.get("conscious_frequency")
        return self._engine.analyze(
            text,
            emotions=emotions,
            cf=cf,
            tlp=tlp,
            header_bpm=header_bpm,
        )

    def bpm_from_density(
        self,
        text: str,
        emo: Optional[Dict[str, float]] = None,
        cf: Optional[float] = None,
        tlp: Optional[Dict[str, float]] = None,
    ) -> int:
        log.debug("Вызов функции: PatchedLyricMeter.bpm_from_density")
        analysis = self.analyze(text, emotions=emo, cf=cf, tlp=tlp)
        bpm = int(round(analysis["global_bpm"]))
        log.debug(
            "Расчет BPM (patched): resolved=%s, header=%s, estimated=%s",
            bpm,
            analysis.get("header_bpm"),
            analysis.get("estimated_bpm"),
        )
        return bpm


class PatchedUniversalFrequencyEngine:
    def resonance_profile(self, tlp: Dict[str, float]) -> Dict[str, Any]:
        cf = tlp.get("conscious_frequency", 0.0)
        if cf > 0.7:
            rec = [4, 5, 6, 7]
        elif cf > 0.3:
            rec = [2, 3, 4, 5]
        else:
            rec = [1, 2, 3, 4]
        return {"recommended_octaves": rec}


class PatchedRNSSafety:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg.get("safety", {"safe_octaves": [2, 3, 4, 5]})

    def clamp_octaves(self, octaves: List[int]) -> List[int]:
        safe = set(self.cfg.get("safe_octaves", [2, 3, 4, 5]))
        arr = [o for o in octaves if o in safe]
        return arr or [2, 3, 4]


class PatchedIntegrityScanEngine:
    def __init__(self):
        self._engine = FullIntegrityScanEngine()

    def analyze(
        self, 
        text: str,
        # Task 2.3: Добавлены параметры для устранения повторных анализов
        emotions: Optional[Dict[str, float]] = None,
        tlp: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Заменяет заглушку на полноценный анализ целостности (V6 Logic)."""
        return self._engine.analyze(text, emotions=emotions, tlp=tlp)


class AdaptiveVocalAllocator:
    def __init__(self):
        self._vocal_registry = VocalProfileRegistry()

    def analyze(
        self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, text: str
    ) -> Dict[str, Any]:
        """Заменяет заглушку на полноценный аллокатор вокала (V6 Logic)."""
        # Task 2.3: Передаем emotions и tlp в get() для устранения повторных анализов
        # Используем V6 логику для определения формы на основе эмоций / TLP
        vox, _, vocal_form = self._vocal_registry.get("default", "auto", text, [], [], emotions=emo, tlp=tlp)
        vocal_count = len(
            [
                v
                for v in vox
                if v in ["solo", "duet", "trio", "quartet", "quintet", "choir"]
            ]
        )

        return {
            "vocal_form": vocal_form,
            "gender": "auto",
            "vocal_count": vocal_count or 1,
        }


# ==========================================================
# 🚀 StudioCore Monolith (v4.3.11)
# ==========================================================


class StudioCore:
    def __init__(self, config_path: Optional[str] = None):
        log.debug("Инициализация StudioCore...")
        self.cfg = load_config(config_path or "studio_config.json")

        log.debug("Загрузка: AutoEmotionalAnalyzer")
        self.emotion = AutoEmotionalAnalyzer()
        log.debug("Загрузка: TruthLovePainEngine")
        self.tlp = TruthLovePainEngine()

        log.debug("Загрузка: PatchedLyricMeter")
        self.rhythm = PatchedLyricMeter()
        log.debug("Загрузка: PatchedUniversalFrequencyEngine")
        self.freq = PatchedUniversalFrequencyEngine()
        log.debug("Загрузка: PatchedRNSSafety")
        self.safety = PatchedRNSSafety(self.cfg)
        log.debug("Загрузка: PatchedIntegrityScanEngine")
        self.integrity = PatchedIntegrityScanEngine()
        log.debug("Загрузка: VocalProfileRegistry")
        self.vocals = VocalProfileRegistry()

        log.debug("Загрузка: PatchedStyleMatrix")
        try:
            # (PatchedStyleMatrix - это наш StyleMatrix v11)
            self.style = PatchedStyleMatrix()
            log.info(
                "🎨 [StyleMatrix] Используется патчированная версия (PatchedStyleMatrix)."
            )
        except ImportError as e:
            log.error(f"НЕ УДАЛОСЬ загрузить PatchedStyleMatrix: {e}")
            self.style = None  # type: ignore

        log.debug("Загрузка: ToneSyncEngine")
        self.tone = ToneSyncEngine()
        log.debug("Загрузка: AdaptiveVocalAllocator")
        self.vocal_allocator = AdaptiveVocalAllocator()
        
        log.debug("Загрузка: ColorEngineAdapter")
        self.color_engine = ColorEngineAdapter()
        
        log.debug("Загрузка: RhythmDynamicsEmotionEngine")
        self.rde_engine = RhythmDynamicsEmotionEngine()

        log.info(
            f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section - Aware Duet Mode v2)."
        )

    # -------------------------------------------------------
    # 🎤 (v4) Анализ вокала по секциям
    # -------------------------------------------------------

    def _analyze_sections(
        self, text_blocks: List[str], ui_gender: str
    ) -> Dict[str, Any]:
        """
        v4: Прогоняет каждый блок текста через грамматику и хинты,
        возвращает общий профиль вокала.
        """
        log.debug("Вызов функции: _analyze_sections")

        section_profiles: List[Dict[str, Optional[str]]] = []
        final_gender = "auto"
        user_voice_hint = None  # Хинт, заданный пользователем

        # 1. Анализ каждого блока
        for block_text in text_blocks:
            # 1a. Ищем грамматику ("я шел" / "я ждала")
            g_gender = detect_gender_from_grammar(block_text)

            # 1b. Ищем хинты ("(шепотом)", "(мужской вокал)")
            v_hint = detect_voice_profile(block_text)

            if v_hint and not user_voice_hint:
                user_voice_hint = v_hint  # Сохраняем первый найденный хинт

            section_profiles.append({"gender": g_gender, "hint": v_hint})
            # v5: Исправлена ошибка f - string (убрано троеточие)
            log.debug(f"Блок [{block_text[:20]}...] -> Пол: {g_gender}, Хинт: {v_hint}")

        # 2. Определение финального пола (Приоритеты)
        genders_found = {p["gender"] for p in section_profiles if p["gender"]}

        if ui_gender != "auto":
            final_gender = ui_gender  # 1. Приоритет UI
            log.debug("Используется пол из UI")
        elif "male" in genders_found and "female" in genders_found:
            final_gender = "mixed"  # 2. Грамматический дуэт
            log.debug("Грамматика определила 'mixed' (M / F)")
        elif "male" in genders_found:
            final_gender = "male"  # 3. Только мужской
            log.debug("Грамматика определила 'male'")
        elif "female" in genders_found:
            final_gender = "female"  # 4. Только женский
            log.debug("Грамматика определила 'female'")
        # (else: остается 'auto')

        log.debug(f"Итог по вокалу (все блоки): {genders_found}")
        return {
            "final_gender_preference": final_gender,
            "user_voice_hint": user_voice_hint,
            "section_profiles": section_profiles,
        }

    # -------------------------------------------------------
    # 🎼 (v6) Генератор семантических секций
    # -------------------------------------------------------

    def _build_semantic_layers(
        self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, style_key: str
    ) -> Dict[str, Any]:
        """v6: Генерирует 'energy', 'arrangement' и использует 'key'"""
        log.debug("Вызов функции: _build_semantic_layers")

        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0)
        # avg_emo reserved for future use

        key = style_key  # Берем тональность из style.py

        def get_focus(mood: str, energy: str) -> str:
            if energy == "high":
                return "climax"
            if energy == "low":
                return "minimal"
            if mood == "dramatic":
                return "contrast"
            if mood == "narrative":
                return "story_flow"
            return "flow"

        # (v6) Логика основана на шаблонах Suno
        intro = {
            "tag": "Intro",
            "mood": "mystic" if cf >= 0.5 else "calm",
            "energy": "low",
            "arrangement": "minimal",
            "bpm": int(bpm * 0.8),
            "key": key,
        }
        verse = {
            "tag": "Verse",
            "mood": "narrative" if love >= truth else "reflective",
            "energy": "mid",
            "arrangement": "standard",
            "bpm": bpm,
            "key": key,
        }
        bridge = {
            "tag": "Bridge",
            "mood": "dramatic" if pain > 0.3 else "dreamlike",
            "energy": "mid - high",
            "arrangement": "building",
            "bpm": int(bpm * 1.05),
            "key": key,
        }
        chorus = {
            "tag": "Chorus",
            "mood": "uplifting" if love >= pain else "tense",
            "energy": "high",
            "arrangement": "full arrangement",
            "bpm": int(bpm * 1.1),
            "key": key,
        }
        outro = {
            "tag": "Outro",
            "mood": "peaceful" if cf > 0.6 else "fading",
            "energy": "low",
            "arrangement": "minimal",
            "bpm": int(bpm * 0.7),
            "key": key,
        }

        # Добавляем 'focus' на основе mood / energy
        for s in [intro, verse, bridge, chorus, outro]:
            s["focus"] = get_focus(s["mood"], s["energy"])

        # v6: BPM теперь зависит от TLP (более простой расчет)
        bpm_adj = int(bpm + (love * 10) - (pain * 15) + (truth * 5))
        bpm_adj = max(60, min(180, bpm_adj))
        log.debug(f"BPM скорректирован до {bpm_adj}")

        return {
            "bpm_suggested": bpm_adj,
            "layers": {
                "depth": round((truth + pain) / 2, 2),
                "warmth": round(love, 2),
                "clarity": round(cf, 2),
                "sections": [intro, verse, bridge, chorus, outro],
            },
        }

    # -------------------------------------------------------
    # ✍️ (v6) Аннотатор текста
    # -------------------------------------------------------

    def annotate_text(
        self,
        text_blocks: List[str],
        section_profiles: List[Dict[str, Optional[str]]],
        semantic_sections: List[Dict[str, Any]],
    ) -> Tuple[str, str]:
        """
        v6: Полностью переписан. Генерирует 2 версии:
        1.  `annotated_text_ui`: Расширенный (для Gradio)
        2.  `annotated_text_suno`: Чистый (для Suno Lyrics)
        """
        log.debug("Вызов функции: annotate_text (v6)")

        ui_blocks = []
        suno_blocks = []

        num_blocks = len(text_blocks)

        # --- (v6) Улучшенная логика мэппинга секций ---
        # intro, verse1, chorus1, verse2, chorus2, bridge, chorus3, outro
        semantic_map = []
        if num_blocks <= 5:
            semantic_map = ["Intro", "Verse", "Bridge", "Chorus", "Outro"]
        elif num_blocks == 6:
            semantic_map = ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Outro"]
        elif num_blocks == 7:
            semantic_map = [
                "Intro",
                "Verse",
                "Pre - Chorus",
                "Chorus",
                "Verse",
                "Bridge",
                "Outro",
            ]
        else:  # 8+
            semantic_map = [
                "Intro",
                "Verse",
                "Pre - Chorus",
                "Chorus",
                "Verse",
                "Bridge",
                "Chorus",
                "Outro",
            ]

        # Дополняем карту, если блоков больше 8
        if num_blocks > len(semantic_map):
            semantic_map.extend(["Verse", "Chorus"] * (num_blocks - len(semantic_map)))

        # Находим определения секций
        sec_defs = {s["tag"].lower(): s for s in semantic_sections}
        # Запасные определения
        sec_defs.setdefault("pre - chorus", sec_defs["bridge"])
        sec_defs.setdefault("verse 2", sec_defs["verse"])
        # --- Конец логики мэппинга ---

        # FIX: Use the calculated Chorus BPM as the final tag BPM for
        # consistency (semantic_sections[3] = Chorus)
        final_bpm = semantic_sections[3].get("bpm", 120)  # (BPM припева)
        final_key = semantic_sections[3].get("key", "auto")
        # final_vocal_form reserved for future use

        for i, block_text in enumerate(text_blocks):
            if not block_text.strip():
                continue

            # 1. Берем семантику (Intro, Verse...)
            tag_name = semantic_map[i].lower()
            # Fallback на 'verse'
            sem = sec_defs.get(tag_name, sec_defs["verse"])

            # 2. Берем вокальный профиль (Male, Female...)
            profile = section_profiles[i]
            # MALE, FEMALE, MIXED, AUTO
            gender_tag = profile.get("gender", "auto").upper()

            # 3. Собираем теги
            suno_tag_parts = [
                tag_name.upper(),
                f"vocal: {gender_tag}" if gender_tag != "AUTO" else None,
                f"mood: {sem['mood']}",
                f"energy: {sem['energy']}",
                f"arrangement: {sem['arrangement']}",
            ]
            suno_tag = f"[{' - '.join(filter(None, suno_tag_parts))}]"

            # UI - тег (более детальный)
            ui_tag = f"[{tag_name.upper()} - {gender_tag} - {sem['mood']}, {sem['energy']}, {sem['arrangement']}, BPM≈{sem['bpm']}]"

            # Обновляем финальный BPM / Key (берем из припева, если он есть)
            if "chorus" in tag_name:
                final_bpm = sem["bpm"]
                final_key = sem["key"]

            ui_blocks.append(ui_tag)
            ui_blocks.append(block_text)
            ui_blocks.append("")

            suno_blocks.append(suno_tag)
            suno_blocks.append(block_text)
            suno_blocks.append("")

        # Финальный тег
        # (vocal_form будет добавлен в 'analyze')
        end_tag_ui = f"[End – BPM≈{final_bpm}, Tone={final_key}]"
        end_tag_suno = f"[{final_bpm} BPM, {final_key}]"

        ui_blocks.append(end_tag_ui)
        suno_blocks.append(end_tag_suno)

        return "\n".join(ui_blocks).strip(), "\n".join(suno_blocks).strip()

    # -------------------------------------------------------
    # 🚀 Главный Пайплайн
    # -------------------------------------------------------

    def _check_safety(self, text: str) -> str:
        """
        Task 1.1: Safety check method that validates input length and checks for aggression keywords.
        Returns the text (possibly replaced with neutral text if aggression detected).
        """
        # Input type validation
        if not text or not isinstance(text, str):
            raise ValueError("Text input is required and must be a string")
        
        # Length validation
        if len(text) > DEFAULT_CONFIG.MAX_INPUT_LENGTH:
            raise ValueError(
                f"Text length ({len(text)}) exceeds maximum allowed length ({DEFAULT_CONFIG.MAX_INPUT_LENGTH})"
            )
        
        # Aggression filter
        aggression_keywords = DEFAULT_CONFIG.AGGRESSION_KEYWORDS
        text_lower = text.lower()
        found_keywords = [kw for kw in aggression_keywords if kw.lower() in text_lower]
        if found_keywords:
            log.warning(
                f"Aggression keywords detected: {found_keywords}. Replacing with neutral text."
            )
            text = DEFAULT_CONFIG.FALLBACK_NEUTRAL_TEXT
        
        return text

    def _infer_gender_from_text(self, text: str) -> Optional[str]:
        """
        Infer gender from Russian text grammar (past tense verb endings).
        Returns 'male', 'female', or None if unclear.
        """
        # Russian past tense patterns: "л" (male) vs "ла" (female)
        male_patterns = [
            r'\b\w+л\b',  # Words ending with "л" (past tense, male)
            r'\b\w+лся\b',  # Reflexive verbs ending with "лся" (male)
        ]
        female_patterns = [
            r'\b\w+ла\b',  # Words ending with "ла" (past tense, female)
            r'\b\w+лась\b',  # Reflexive verbs ending with "лась" (female)
        ]
        
        male_matches = []
        female_matches = []
        for pattern in male_patterns:
            male_matches.extend(re.findall(pattern, text, re.IGNORECASE))
        for pattern in female_patterns:
            female_matches.extend(re.findall(pattern, text, re.IGNORECASE))
        
        male_count = len(male_matches)
        female_count = len(female_matches)
        
        if male_count > female_count and male_count > 0:
            return "male"
        elif female_count > male_count and female_count > 0:
            return "female"
        elif male_count == female_count and male_count > 0:
            # If equal, check which appears first in text
            first_male_pos = min((text.lower().find(m) for m in male_matches), default=len(text))
            first_female_pos = min((text.lower().find(m) for m in female_matches), default=len(text))
            if first_male_pos < first_female_pos:
                return "male"
            elif first_female_pos < first_male_pos:
                return "female"
        return None

    def _infer_texture_from_mood(self, mood: str, emotions: Dict[str, float]) -> str:
        """
        Infer vocal texture based on mood and emotions.
        """
        mood_lower = (mood or "").lower()
        emotion_keys = [k.lower() for k in emotions.keys()] if emotions else []
        
        # Reflective/introspective moods -> breathy/intimate
        if any(word in mood_lower for word in ["reflective", "introspective", "melancholic", "nostalgic", "peaceful"]):
            return "breathy/intimate"
        if any(word in emotion_keys for word in ["peace", "nostalgia", "melancholy"]):
            return "breathy/intimate"
        
        # Uplifting/energetic moods -> resonant
        if any(word in mood_lower for word in ["uplifting", "energetic", "joyful", "triumphant"]):
            return "resonant"
        if any(word in emotion_keys for word in ["joy", "triumph", "energy"]):
            return "resonant"
        
        # Default
        return "dynamic"

    def _generate_color_signature_from_emotions(self, emotions: Dict[str, float]) -> str:
        """
        Generate color signature from primary emotion.
        """
        if not emotions:
            return "neutral"
        
        dominant = max(emotions, key=emotions.get)
        
        # Emotion to color mapping
        emotion_color_map = {
            "nostalgia": "sepia/orange",
            "pain": "grey/blue",
            "joy": "yellow/gold",
            "peace": "green/teal",
            "love": "pink/rose",
            "melancholy": "blue/grey",
            "triumph": "red/orange",
            "anger": "red/dark",
            "fear": "purple/dark",
            "sadness": "blue/indigo",
        }
        
        return emotion_color_map.get(dominant.lower(), "neutral")

    def _generate_resonance_hz_from_key(self, key: str) -> float:
        """
        Generate mock resonance_hz based on key.
        """
        # Base frequencies for common keys (approximate)
        key_freq_map = {
            "c": 130.81,
            "c#": 138.59,
            "d": 146.83,
            "d#": 155.56,
            "e": 164.81,
            "f": 174.61,
            "f#": 185.00,
            "g": 196.00,
            "g#": 207.65,
            "a": 220.00,
            "a#": 233.08,
            "b": 246.94,
        }
        
        # Extract key root (first letter, case-insensitive)
        key_lower = (key or "").lower().strip()
        key_root = key_lower.split()[0] if key_lower else "c"
        
        # Remove # and b (sharp/flat) for matching
        key_root = key_root.replace("#", "").replace("b", "")
        
        base_freq = key_freq_map.get(key_root, 130.81)
        
        # Minor keys typically ~10Hz lower
        if "minor" in key_lower:
            base_freq -= 10.0
        
        return round(base_freq, 2)

    def _generate_breathing_map_from_punctuation(self, text: str) -> Dict[str, Any]:
        """
        Generate simple breathing map based on punctuation.
        Commas = short breath, periods = long breath.
        """
        breathing_points = []
        text_length = len(text)
        
        for i, char in enumerate(text):
            if char == ',':
                breathing_points.append({
                    "position": i,
                    "type": "short",
                    "duration_ms": 200,
                })
            elif char in '.!?':
                breathing_points.append({
                    "position": i,
                    "type": "long",
                    "duration_ms": 500,
                })
        
        return {
            "breathing_points": breathing_points,
            "total_points": len(breathing_points),
            "inhale_points": [p["position"] for p in breathing_points if p["type"] == "long"],
            "exhale_points": [p["position"] for p in breathing_points if p["type"] == "short"],
        }

    def _enrich_result_with_smart_defaults(
        self, result: Dict[str, Any], text: str, preferred_gender: str
    ) -> Dict[str, Any]:
        """
        Enrich result dictionary with smart defaults for missing fields.
        """
        # 1. Vocal Inference
        vocal = result.get("vocal", {})
        if isinstance(vocal, dict):
            # Infer gender if auto and not set
            if preferred_gender == "auto" and vocal.get("gender") == "auto":
                inferred_gender = self._infer_gender_from_text(text)
                if inferred_gender:
                    vocal["gender"] = inferred_gender
                    log.debug(f"Inferred gender from text: {inferred_gender}")
            
            # Set texture based on mood if missing
            if not vocal.get("texture"):
                style = result.get("style", {})
                mood = style.get("mood") or style.get("atmosphere") or "neutral"
                emotions = result.get("emotions", {})
                texture = self._infer_texture_from_mood(mood, emotions)
                vocal["texture"] = texture
                log.debug(f"Inferred texture from mood: {texture}")
            
            result["vocal"] = vocal
        
        # 2. Color & Resonance
        style = result.get("style", {})
        if isinstance(style, dict):
            # Add color_signature if missing
            if not style.get("color_signature"):
                emotions = result.get("emotions", {})
                color_sig = self._generate_color_signature_from_emotions(emotions)
                style["color_signature"] = color_sig
                log.debug(f"Generated color_signature: {color_sig}")
            
            result["style"] = style
        
        # Add resonance_hz to RDE if missing
        rde = result.get("rde", {})
        if isinstance(rde, dict) and not rde.get("resonance_hz"):
            key = result.get("key", "C major")
            resonance_hz = self._generate_resonance_hz_from_key(key)
            rde["resonance_hz"] = resonance_hz
            log.debug(f"Generated resonance_hz from key: {resonance_hz}")
            result["rde"] = rde
        
        # 3. ZeroPulse / Breathing
        if not result.get("breathing") and not result.get("zeropulse"):
            breathing_map = self._generate_breathing_map_from_punctuation(text)
            result["breathing"] = breathing_map
            # ZeroPulse is typically derived from breathing
            result["zeropulse"] = {
                "breathing_sync": breathing_map.get("total_points", 0) > 0,
                "points": breathing_map.get("breathing_points", []),
            }
            log.debug(f"Generated breathing map with {breathing_map.get('total_points', 0)} points")
        
        # 4. Genre - Ensure secondary is populated
        style = result.get("style", {})
        if isinstance(style, dict) and not style.get("secondary"):
            genre = style.get("genre", "")
            # If genre contains "hybrid", try to extract secondary from it
            if genre and "hybrid" in str(genre).lower():
                # Split hybrid genre (e.g., "folk rock hybrid" -> ["folk", "rock"])
                genre_parts = str(genre).lower().replace(" hybrid", "").split()
                if len(genre_parts) >= 2:
                    # Use the second part as secondary
                    style["secondary"] = genre_parts[1]
                    log.debug(f"Extracted secondary genre from hybrid: {style['secondary']}")
            # If genre_source indicates hybrid_genre_engine was used, we can infer secondary
            elif style.get("genre_source") == "hybrid_genre_engine" and genre:
                # Try to extract from genre name if it has multiple words
                genre_words = str(genre).split()
                if len(genre_words) >= 2:
                    style["secondary"] = genre_words[1]
                    log.debug(f"Inferred secondary genre: {style['secondary']}")
            
            result["style"] = style
        
        return result

    def analyze(
        self,
        text: str,
        preferred_gender: str = "auto",
        version: Optional[str] = None,
        semantic_hints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Task 10.2: Start timer for runtime metrics
        start_time = time.time()
        
        log.debug(f"--- ЗАПУСК АНАЛИЗА (v{STUDIOCORE_VERSION}) ---")
        log.debug(f"Preferred Gender: {preferred_gender}, Text: {text[:40]}...")

        # Task 1.1: Safety check at the start of analyze
        text = self._check_safety(text)

        raw = normalize_text_preserve_symbols(text)
        text_blocks = extract_raw_blocks(raw)

        # Task 1.2: Section Analysis
        section_result = self._analyze_sections(text_blocks, preferred_gender)
        section_profiles = section_result.get("section_profiles", [])
        voice_hint = section_result.get("user_voice_hint")

        # Task 10.1: Run independent engines in parallel using ThreadPoolExecutor
        # emotion and tone are independent, so they can run in parallel
        emotions = None
        tone_hint = None
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit independent tasks (emotion and tone don't depend on each other)
            future_emotion = executor.submit(self.emotion.analyze, raw)
            future_tone = executor.submit(self.tone.detect_key, raw)
            
            # Wait for results
            emotions = future_emotion.result()
            tone_hint = future_tone.result()
        
        # Initialize integrity_result to None (will be set later after tlp is available)
        integrity_result = None
        
        log.debug(f"Результат EMO (до фильтрации): {emotions}")
        
        # Task 3.1: Использование EMOTION_HIGH_SIGNAL для фильтрации слабых эмоций
        emotion_high_signal = DEFAULT_CONFIG.EMOTION_HIGH_SIGNAL
        if emotions:
            # Фильтруем эмоции, которые ниже порога EMOTION_HIGH_SIGNAL
            # Оставляем только значимые эмоции для дальнейшей обработки
            filtered_emotions = {
                k: v for k, v in emotions.items() 
                if v >= emotion_high_signal or k == max(emotions, key=emotions.get)
            }
            # Если после фильтрации осталась только доминирующая эмоция, 
            # перераспределяем веса для сохранения нормализации
            if len(filtered_emotions) < len(emotions) and len(filtered_emotions) > 0:
                total_filtered = sum(filtered_emotions.values())
                if total_filtered > 0:
                    # Нормализуем отфильтрованные эмоции
                    emotions = {k: v / total_filtered for k, v in filtered_emotions.items()}
                    log.debug(f"Эмоции отфильтрованы по EMOTION_HIGH_SIGNAL ({emotion_high_signal}): {emotions}")
                else:
                    # Если все отфильтрованы, оставляем доминирующую
                    dominant = max(emotions, key=emotions.get)
                    emotions = {dominant: 1.0}
                    log.debug(f"Все эмоции ниже порога, оставлена доминирующая: {dominant}")
            else:
                log.debug(f"Эмоции не требуют фильтрации (все выше порога {emotion_high_signal})")
        
        log.debug(f"Результат EMO (после фильтрации): {emotions}")

        # Task 1.1: TLP Analysis
        tlp = self.tlp.analyze(raw)
        cf = tlp.get("conscious_frequency")
        log.debug(f"Результат TLP: {tlp}, CF: {cf}")

        rhythm_analysis = self.rhythm.analyze(raw, emotions=emotions, tlp=tlp, cf=cf)
        bpm = int(round(rhythm_analysis.get("global_bpm", DEFAULT_CONFIG.FALLBACK_BPM)))
        log.debug(
            "Базовый BPM: %s (header=%s, estimated=%s)",
            bpm,
            rhythm_analysis.get("header_bpm"),
            rhythm_analysis.get("estimated_bpm"),
        )
        
        # Task 18.1: Auto-resolve BPM-TLP conflicts
        consistency = ConsistencyLayerV8({"bpm": bpm, "tlp": tlp})
        suggested_bpm, was_resolved = consistency.resolve_bpm_tlp_conflict(bpm, tlp)
        if was_resolved:
            log.debug(f"BPM-TLP Konflikt aufgelöst: {bpm} → {suggested_bpm}")
            bpm = int(round(suggested_bpm))

        # Task 9.1: tone_hint already obtained from parallel execution
        key = tone_hint.get("key") if tone_hint else DEFAULT_CONFIG.FALLBACK_KEY
        if not key or key == "auto":
            key = DEFAULT_CONFIG.FALLBACK_KEY

        # Task 1.3: Style.build() вместо FALLBACK значений
        if self.style:
            style_result = self.style.build(
                emotions, tlp, raw, bpm, semantic_hints, voice_hint
            )
            style = style_result
        else:
            # Fallback если style engine недоступен
            style = {
                "genre": DEFAULT_CONFIG.FALLBACK_STYLE,
                "style": DEFAULT_CONFIG.FALLBACK_STYLE,
                "bpm": bpm,
                "key": key,
                "visual": DEFAULT_CONFIG.FALLBACK_VISUAL,
                "narrative": DEFAULT_CONFIG.FALLBACK_NARRATIVE,
                "structure": DEFAULT_CONFIG.FALLBACK_STRUCTURE,
                "emotion": emotions.get("dominant") or DEFAULT_CONFIG.FALLBACK_EMOTION,
            }
            log.warning("Style engine недоступен, используются FALLBACK значения")

        # Task 1.4: Semantic Layers
        semantic_layers = self._build_semantic_layers(emotions, tlp, bpm, key)
        semantic_sections = semantic_layers.get("layers", {}).get("sections", [])

        # Определяем layout из semantic_sections или используем fallback
        layout = DEFAULT_CONFIG.FALLBACK_STRUCTURE
        if semantic_sections and len(semantic_sections) > 0:
            layout = semantic_sections[0].get("tag", DEFAULT_CONFIG.FALLBACK_STRUCTURE)

        structure = {
            "sections": text_blocks,
            "section_count": len(text_blocks),
            "layout": layout,
        }

        # Task 1.6: Vocal Allocator
        vocal_result = self.vocal_allocator.analyze(emotions, tlp, bpm, raw)
        log.debug(f"Результат Vocal: {vocal_result}")

        # Task 1.6: Integrity Scan
        # Task 2.3: Передаем emotions и tlp для устранения повторных анализов
        # Note: integrity requires emotions and tlp, so it runs after they are available (not in parallel)
        integrity_result = self.integrity.analyze(raw, emotions=emotions, tlp=tlp)
        log.debug(f"Результат Integrity: {integrity_result}")

        # Task 1.5: Text Annotation
        annotated_text_ui, annotated_text_suno = self.annotate_text(
            text_blocks, section_profiles, semantic_sections
        )

        # Дополнительно: Color Resolution
        # Собираем промежуточный результат для Color Engine
        intermediate_result = {
            "emotions": emotions,
            "tlp": tlp,
            "style": style,
        }
        color_resolution = self.color_engine.resolve_color_wave(intermediate_result)
        color_wave = color_resolution.colors if color_resolution else []
        
        # Task 18.2: Auto-resolve Color-Key conflicts
        resolver = GenreConflictResolver()
        suggested_key, was_resolved = resolver.resolve_color_key_conflict(
            key, color_wave, style
        )
        if was_resolved:
            log.debug(f"Color-Key Konflikt aufgelöst: {key} → {suggested_key}")
            key = suggested_key
            # Update style dict with new key
            style["key"] = key

        # Дополнительно: RDE Analysis
        # RDE требует bpm_payload, breathing_profile, emotion_profile, instrumentation_payload
        rde_result = {
            "resonance": self.rde_engine.calc_resonance(raw),
            "fracture": self.rde_engine.calc_fracture(raw),
            "entropy": self.rde_engine.calc_entropy(raw),
        }
        # Если есть TLP, используем его для экспорта emotion vector
        if tlp:
            try:
                rde_emotion_vector = self.rde_engine.export_emotion_vector(raw)
                rde_result["emotion_vector"] = {
                    "valence": rde_emotion_vector.valence,
                    "arousal": rde_emotion_vector.arousal,
                }
            except Exception as e:
                log.warning(f"Не удалось экспортировать RDE emotion vector: {e}")
        
        # Task 18.1: Auto-resolve Genre-RDE conflicts
        genre = style.get("genre", "")
        adjusted_rde, was_resolved = consistency.resolve_genre_rde_conflict(genre, rde_result)
        if was_resolved:
            log.debug(f"Genre-RDE Konflikt aufgelöst: {rde_result} → {adjusted_rde}")
            rde_result = adjusted_rde

        # Task 10.2: Calculate runtime and add to result
        runtime_ms = int((time.time() - start_time) * 1000)
        log.debug(f"--- АНАЛИЗ УСПЕШНО ЗАВЕРШЕН (runtime: {runtime_ms}ms) ---")

        # Task 1.7: Обновленный return словарь с всеми рассчитанными данными
        result = {
            "emotions": emotions,
            "tlp": tlp,
            "bpm": bpm,
            "key": key,
            "structure": structure,
            "style": style,
            "vocal": vocal_result,
            "semantic_layers": semantic_layers,
            "integrity": integrity_result,
            "annotated_text_ui": annotated_text_ui,
            "annotated_text_suno": annotated_text_suno,
            "color_wave": color_wave,
            "rde": rde_result,
            # Task 10.2: Add runtime metrics for diagnostics
            "runtime_ms": runtime_ms,
        }
        
        # Enrich result with smart defaults for missing fields
        result = self._enrich_result_with_smart_defaults(result, text, preferred_gender)
        
        return result


class StudioCoreV5:
    """Compatibility wrapper exposing the v5 API expected by legacy tools."""

    def __init__(self, *args, **kwargs):
        self._core = StudioCore(*args, **kwargs)

    def analyze(self, *args, **kwargs):
        return self._core.analyze(*args, **kwargs)

    def emotion(self, text: str):
        return self._core.emotion.analyze(text)

    def style(
        self,
        emo: Dict[str, float],
        tlp: Dict[str, float],
        text: str,
        bpm: int,
        semantic_hints: Optional[Dict[str, Any]] = None,
        voice_hint: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self._core.style:
            raise RuntimeError("Style subsystem is unavailable.")
        return self._core.style.build(emo, tlp, text, bpm, semantic_hints, voice_hint)

    def tone(
        self,
        emo: Dict[str, float],
        tlp: Dict[str, float],
        key_hint: Optional[str] = None,
    ):
        return self._core.tone.colors_for_primary(emo, tlp, key_hint or "auto")

    def rhythm(
        self,
        text: str,
        *,
        emotions: Optional[Dict[str, float]] = None,
        tlp: Optional[Dict[str, float]] = None,
        cf: Optional[float] = None,
        header_bpm: Optional[float] = None,
    ):
        return self._core.rhythm.analyze(
            text,
            emotions=emotions,
            tlp=tlp,
            cf=cf,
            header_bpm=header_bpm,
        )

    def __getattr__(self, item: str):
        return getattr(self._core, item)


# ==========================================================
# Task 6.2: Version is now imported from config.py
log.info(
    f"🔹 [StudioCore {MONOLITH_VERSION}] Monolith loaded (Section - Aware Duet Mode v2)."
)

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
