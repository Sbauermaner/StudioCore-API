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
import random
import time
from typing import Dict, Any, List, Tuple, Optional
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

# Legacy Bridge: Import Suno prompt builder
try:
    from .adapter import build_suno_prompt
    LEGACY_SUNO_AVAILABLE = True
except ImportError:
    LEGACY_SUNO_AVAILABLE = False
    log.warning("[Legacy Bridge] build_suno_prompt not available, will use fallback")

# Fusion Engine: Import FusionEngineV64 and GenreRoutingEngineV64
try:
    from .fusion_engine_v64 import FusionEngineV64
    from .genre_routing_engine import GenreRoutingEngineV64
    FUSION_ENGINE_AVAILABLE = True
except ImportError:
    FUSION_ENGINE_AVAILABLE = False
    log.warning("[Fusion Engine] FusionEngineV64 not available, will skip fusion")

# Hybrid Genre Engine: Import HybridGenreEngine
try:
    from .hybrid_genre_engine import HybridGenreEngine
    HYBRID_GENRE_ENGINE_AVAILABLE = True
except ImportError:
    HYBRID_GENRE_ENGINE_AVAILABLE = False
    log.warning("[Hybrid Genre Engine] HybridGenreEngine not available, will skip hybrid genre resolution")

# Suno Prompt Engine: Import SunoPromptEngine for advanced tags
try:
    from .suno_advanced_prompts import SunoPromptEngine
    SUNO_PROMPT_ENGINE_AVAILABLE = True
except ImportError:
    SUNO_PROMPT_ENGINE_AVAILABLE = False
    log.warning("[Suno Prompt Engine] SunoPromptEngine not available, will skip advanced tags")

# Emotion-Driven Suno Adapter: Import for emotion-based annotations
try:
    from .suno_annotations import EmotionDrivenSunoAdapter, build_suno_annotations
    EMOTION_SUNO_ADAPTER_AVAILABLE = True
except ImportError:
    EMOTION_SUNO_ADAPTER_AVAILABLE = False
    log.warning("[Emotion Suno Adapter] EmotionDrivenSunoAdapter not available, will skip emotion-driven annotations")

# Suno Annotation Engine: Import for safe annotations
try:
    from .suno_annotations import SunoAnnotationEngine
    SUNO_ANNOTATION_ENGINE_AVAILABLE = True
except ImportError:
    SUNO_ANNOTATION_ENGINE_AVAILABLE = False
    log.warning("[Suno Annotation Engine] SunoAnnotationEngine not available, will skip safe annotations")

# Dynamic Emotion Engine: Import for normalized emotion profile
try:
    from .dynamic_emotion_engine import DynamicEmotionEngine
    DYNAMIC_EMOTION_ENGINE_AVAILABLE = True
except ImportError:
    DYNAMIC_EMOTION_ENGINE_AVAILABLE = False
    log.warning("[Dynamic Emotion Engine] DynamicEmotionEngine not available, will skip normalized emotion profile")

# Genre Database Loader: Import for expanded genre database
try:
    from .genre_database_loader import GenreDatabaseLoader
    GENRE_DATABASE_LOADER_AVAILABLE = True
except ImportError:
    GENRE_DATABASE_LOADER_AVAILABLE = False
    log.warning("[Genre Database Loader] GenreDatabaseLoader not available, will skip expanded genre database")

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
        
        # Определяем gender на основе эмоций и TLP
        gender = "auto"
        if emo and isinstance(emo, dict) and len(emo) > 0:
            try:
                from .vocal_techniques import get_vocal_for_emotion
                
                # Находим доминирующую эмоцию
                dominant_emotion = max(emo, key=emo.get)
                intensity = emo[dominant_emotion]
                
                # Получаем вокальные техники для эмоции
                vocal_techniques = get_vocal_for_emotion(dominant_emotion, intensity)
                
                # Определяем тип голоса на основе техник
                female_keywords = ["soprano", "mezzo", "contralto", "female", "head_voice", "falsetto", "whistle", "coloratura", "lyric_soprano", "soft_female", "airy", "ethereal", "angelic"]
                male_keywords = ["tenor", "baritone", "bass", "male", "chest_voice", "guttural", "dramatic", "warm_baritone", "lyric_tenor", "gentle_male"]
                
                # Подсчитываем женские и мужские техники
                female_count = sum(1 for tech in vocal_techniques if any(kw in tech.lower() for kw in female_keywords))
                male_count = sum(1 for tech in vocal_techniques if any(kw in tech.lower() for kw in male_keywords))
                
                # Выбираем gender на основе техник
                if female_count > male_count:
                    gender = "female"
                elif male_count > female_count:
                    gender = "male"
                else:
                    # Если равное количество, используем TLP для определения
                    if tlp and isinstance(tlp, dict):
                        love = tlp.get("love", 0.0)
                        pain = tlp.get("pain", 0.0)
                        truth = tlp.get("truth", 0.0)
                        
                        # Love -> female, Pain/Truth -> male
                        if love > pain and love > truth:
                            gender = "female"
                        elif pain > love or truth > love:
                            gender = "male"
                        else:
                            # Fallback на эмоции
                            joy_peace = emo.get("joy", 0) + emo.get("peace", 0) + emo.get("love", 0) + emo.get("awe", 0)
                            anger_epic = emo.get("anger", 0) + emo.get("epic", 0) + emo.get("rage", 0) + emo.get("fear", 0)
                            gender = "female" if joy_peace > anger_epic else "male"
            except (ImportError, AttributeError, Exception) as e:
                log.debug(f"[Vocal Allocator] Could not determine gender from emotions/TLP: {e}, using auto")
                # Fallback на простую логику
                if emo and isinstance(emo, dict):
                    joy_peace = emo.get("joy", 0) + emo.get("peace", 0) + emo.get("love", 0)
                    anger_epic = emo.get("anger", 0) + emo.get("epic", 0) + emo.get("rage", 0)
                    gender = "female" if joy_peace > anger_epic else "male"
        
        # Определяем vocal style на основе эмоций и TLP
        vocal_style = "standard"
        if emo and isinstance(emo, dict) and len(emo) > 0:
            dominant_emotion = max(emo, key=emo.get) if emo else "neutral"
            
            # Маппинг эмоций к стилям
            emotion_to_style = {
                "joy": "bright",
                "happiness": "bright",
                "love": "soft",
                "peace": "gentle",
                "sadness": "melancholic",
                "melancholy": "melancholic",
                "anger": "aggressive",
                "rage": "harsh",
                "fear": "tense",
                "awe": "epic",
                "epic": "epic",
            }
            vocal_style = emotion_to_style.get(dominant_emotion, "standard")
        
        # Определяем vocal tone на основе TLP
        vocal_tone = "neutral"
        if tlp and isinstance(tlp, dict):
            love = tlp.get("love", 0.0)
            pain = tlp.get("pain", 0.0)
            truth = tlp.get("truth", 0.0)
            
            if love > 0.6:
                vocal_tone = "warm"
            elif pain > 0.6:
                vocal_tone = "dark"
            elif truth > 0.6:
                vocal_tone = "clear"
            else:
                # Определяем по доминирующей оси
                dominant_axis = max(("love", love), ("pain", pain), ("truth", truth), key=lambda x: x[1])
                if dominant_axis[1] > 0.3:
                    vocal_tone = {"love": "warm", "pain": "dark", "truth": "clear"}.get(dominant_axis[0], "neutral")

        return {
            "vocal_form": vocal_form,
            "gender": gender,
            "vocal_count": vocal_count or 1,
            "style": vocal_style,  # Добавляем style
            "tone": vocal_tone,  # Добавляем tone
        }


# ==========================================================
# 🚀 StudioCore Monolith (v4.3.11)
# ==========================================================


class StudioCore:
    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация StudioCore согласно ACTIVATION_BLUEPRINT.
        Модули загружаются в строгом порядке согласно init_sequence.
        """
        log.debug("Инициализация StudioCore...")
        
        # === PHASE 0: ConfigLoader ===
        log.debug("Загрузка: ConfigLoader")
        self.cfg = load_config(config_path or "studio_config.json")

        # === PHASE 1: EmotionEngine ===
        log.debug("Загрузка: EmotionEngine (AutoEmotionalAnalyzer)")
        self.emotion = AutoEmotionalAnalyzer()
        
        # === PHASE 2: TLPEngine ===
        log.debug("Загрузка: TLPEngine (TruthLovePainEngine)")
        self.tlp = TruthLovePainEngine()

        # === PHASE 3: RhythmEngine ===
        log.debug("Загрузка: RhythmEngine (PatchedLyricMeter)")
        self.rhythm = PatchedLyricMeter()
        
        # === PHASE 4: FrequencyEngine ===
        log.debug("Загрузка: FrequencyEngine (PatchedUniversalFrequencyEngine)")
        self.freq = PatchedUniversalFrequencyEngine()
        
        # === PHASE 5: SafetyEngine ===
        log.debug("Загрузка: SafetyEngine (PatchedRNSSafety)")
        self.safety = PatchedRNSSafety(self.cfg)
        
        # === PHASE 6: IntegrityScan ===
        log.debug("Загрузка: IntegrityScan (PatchedIntegrityScanEngine)")
        self.integrity = PatchedIntegrityScanEngine()
        
        # === PHASE 7: VocalRegistry ===
        log.debug("Загрузка: VocalRegistry (VocalProfileRegistry)")
        self.vocals = VocalProfileRegistry()

        # === PHASE 8: StyleMatrix ===
        log.debug("Загрузка: StyleMatrix (PatchedStyleMatrix)")
        try:
            # (PatchedStyleMatrix - это наш StyleMatrix v11)
            self.style = PatchedStyleMatrix()
            log.info(
                "🎨 [StyleMatrix] Используется патчированная версия (PatchedStyleMatrix)."
            )
        except ImportError as e:
            log.error(f"НЕ УДАЛОСЬ загрузить PatchedStyleMatrix: {e}")
            self.style = None  # type: ignore

        # === PHASE 9: ToneEngine ===
        log.debug("Загрузка: ToneEngine (ToneSyncEngine)")
        self.tone = ToneSyncEngine()
        
        # === PHASE 10: VocalAllocator ===
        log.debug("Загрузка: VocalAllocator (AdaptiveVocalAllocator)")
        self.vocal_allocator = AdaptiveVocalAllocator()
        
        # === PHASE 11: ColorEngine ===
        log.debug("Загрузка: ColorEngine (ColorEngineAdapter)")
        self.color_engine = ColorEngineAdapter()
        
        # === PHASE 12: RDEEngine ===
        log.debug("Загрузка: RDEEngine (RhythmDynamicsEmotionEngine)")
        self.rde_engine = RhythmDynamicsEmotionEngine()
        
        # === PHASE 13: GenreDatabase ===
        log.debug("Загрузка: GenreDatabase (GenreDatabaseLoader)")
        self.genre_database = None
        if GENRE_DATABASE_LOADER_AVAILABLE:
            try:
                self.genre_database = GenreDatabaseLoader()
                log.info("✅ [Genre Database Loader] GenreDatabaseLoader loaded")
            except (ImportError, AttributeError, TypeError) as e:
                log.warning(f"[Genre Database Loader] Failed to initialize: {e}")
                self.genre_database = None
            except Exception as e:
                log.error(f"[Genre Database Loader] Unexpected error during initialization: {e}", exc_info=True)
                self.genre_database = None

        # === PHASE 14: FusionEngine ===
        log.debug("Загрузка: FusionEngine (FusionEngineV64, GenreRoutingEngineV64)")
        self.fusion_engine = None
        self.genre_routing_engine = None
        if FUSION_ENGINE_AVAILABLE:
            try:
                self.fusion_engine = FusionEngineV64()
                self.genre_routing_engine = GenreRoutingEngineV64()
                log.info("✅ [Fusion Engine] FusionEngineV64 and GenreRoutingEngineV64 loaded")
            except (ImportError, AttributeError, TypeError) as e:
                log.warning(f"[Fusion Engine] Failed to initialize: {e}")
                self.fusion_engine = None
                self.genre_routing_engine = None
            except Exception as e:
                log.error(f"[Fusion Engine] Unexpected error during initialization: {e}", exc_info=True)
                self.fusion_engine = None
                self.genre_routing_engine = None

        # --- HYBRID GENRE ENGINE SUPPORT (Optional) ---
        self.hybrid_genre_engine = None
        if HYBRID_GENRE_ENGINE_AVAILABLE:
            try:
                self.hybrid_genre_engine = HybridGenreEngine()
                log.info("✅ [Hybrid Genre Engine] HybridGenreEngine loaded")
            except (ImportError, AttributeError, TypeError) as e:
                log.warning(f"[Hybrid Genre Engine] Failed to initialize: {e}")
                self.hybrid_genre_engine = None
            except Exception as e:
                log.error(f"[Hybrid Genre Engine] Unexpected error during initialization: {e}", exc_info=True)
                self.hybrid_genre_engine = None

        # --- SUNO PROMPT ENGINE SUPPORT (Optional) ---
        self.suno_prompt_engine = None
        if SUNO_PROMPT_ENGINE_AVAILABLE:
            try:
                self.suno_prompt_engine = SunoPromptEngine()
                log.info("✅ [Suno Prompt Engine] SunoPromptEngine loaded")
            except (ImportError, AttributeError, TypeError) as e:
                log.warning(f"[Suno Prompt Engine] Failed to initialize: {e}")
                self.suno_prompt_engine = None
            except Exception as e:
                log.error(f"[Suno Prompt Engine] Unexpected error during initialization: {e}", exc_info=True)
                self.suno_prompt_engine = None

        # --- EMOTION-DRIVEN SUNO ADAPTER SUPPORT (Optional) ---
        self.emotion_suno_adapter_available = EMOTION_SUNO_ADAPTER_AVAILABLE
        if EMOTION_SUNO_ADAPTER_AVAILABLE:
            log.info("✅ [Emotion Suno Adapter] EmotionDrivenSunoAdapter available")

        # --- SUNO ANNOTATION ENGINE SUPPORT (Optional) ---
        self.suno_annotation_engine = None
        if SUNO_ANNOTATION_ENGINE_AVAILABLE:
            try:
                self.suno_annotation_engine = SunoAnnotationEngine()
                log.info("✅ [Suno Annotation Engine] SunoAnnotationEngine loaded")
            except (ImportError, AttributeError, TypeError) as e:
                log.warning(f"[Suno Annotation Engine] Failed to initialize: {e}")
                self.suno_annotation_engine = None
            except Exception as e:
                log.error(f"[Suno Annotation Engine] Unexpected error during initialization: {e}", exc_info=True)
                self.suno_annotation_engine = None

        # --- DYNAMIC EMOTION ENGINE SUPPORT (Optional) ---
        self.dynamic_emotion_engine = None
        if DYNAMIC_EMOTION_ENGINE_AVAILABLE:
            try:
                self.dynamic_emotion_engine = DynamicEmotionEngine()
                log.info("✅ [Dynamic Emotion Engine] DynamicEmotionEngine loaded")
            except (ImportError, AttributeError, TypeError) as e:
                log.warning(f"[Dynamic Emotion Engine] Failed to initialize: {e}")
                self.dynamic_emotion_engine = None
            except Exception as e:
                log.error(f"[Dynamic Emotion Engine] Unexpected error during initialization: {e}", exc_info=True)
                self.dynamic_emotion_engine = None

        # --- MATRIX ARCHITECTURE SUPPORT (Optional) ---
        self.matrix_enabled = False
        self.matrix_genre_engine = None
        self.matrix_instrument_engine = None
        self.matrix_serendipity = None
        self.matrix_breathing_engine = None
        
        try:
            from .engines.universal_matrix import UniversalMatrixGenreEngine
            from .engines.instrument_engine import InstrumentEngine
            from .engines.serendipity_engine import SerendipityEngine
            from .engines.rhythm_breathing import RhythmBreathingEngine
            
            self.matrix_genre_engine = UniversalMatrixGenreEngine()
            self.matrix_instrument_engine = InstrumentEngine()
            self.matrix_serendipity = SerendipityEngine()
            self.matrix_breathing_engine = RhythmBreathingEngine()
            self.matrix_enabled = True
            log.info("✅ [Matrix Architecture] New engines loaded: UniversalMatrix, InstrumentEngine, SerendipityEngine, RhythmBreathingEngine")
        except ImportError as e:
            log.debug(f"[Matrix Architecture] Not available (fallback to legacy): {e}")
            self.matrix_enabled = False

        log.info(
            f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section - Aware Duet Mode v2)."
            + (f" [Matrix: {'ENABLED' if self.matrix_enabled else 'LEGACY'}]" if hasattr(self, 'matrix_enabled') else "")
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

    def _enhance_suno_annotations(
        self,
        annotated_text: str,
        emotions: Dict[str, float],
        vocal_result: Dict[str, Any],
        style: Dict[str, Any]
    ) -> str:
        """
        Enhance Suno annotations with advanced tags from SunoPromptEngine.
        Adds voice tags, emotion tags, and FX tags where appropriate.
        """
        if not self.suno_prompt_engine or not annotated_text:
            return annotated_text
        
        try:
            lines = annotated_text.split('\n')
            enhanced_lines = []
            
            # Get dominant emotion for voice tags
            dominant_emotion = max(emotions, key=emotions.get) if emotions and isinstance(emotions, dict) else "neutral"
            intensity = emotions.get(dominant_emotion, 1.0) if emotions and isinstance(emotions, dict) else 1.0
            
            # Map emotions to voice tags using detailed mapping
            try:
                from .vocal_techniques import get_vocal_for_emotion
                
                # Получаем вокальные техники для эмоции
                vocal_techniques = get_vocal_for_emotion(dominant_emotion, intensity)
                
                # Преобразуем техники в теги
                if vocal_techniques:
                    # Берем первую технику и преобразуем в тег
                    primary_technique = vocal_techniques[0]
                    
                    # Маппинг техник к тегам
                    technique_to_tag = {
                        "harsh": "[Aggressive]",
                        "scream": "[Gritty]",
                        "guttural": "[Gritty]",
                        "rasp": "[Gritty]",
                        "melancholy": "[Melancholic]",
                        "soft": "[Melancholic]",
                        "vibrato": "[Emotional]",
                        "emotional": "[Emotional]",
                        "ethereal": "[Angelic]",
                        "angelic": "[Angelic]",
                        "breathy": "[Soulful]",
                        "warm": "[Soulful]",
                        "belting": "[Powerful]",
                        "powerful": "[Powerful]",
                        "dramatic": "[Dramatic]",
                    }
                    
                    # Ищем подходящий тег
                    voice_tag = ""
                    for tech_key, tag in technique_to_tag.items():
                        if tech_key in primary_technique.lower():
                            voice_tag = tag
                            break
                    
                    # Если не нашли, используем общий тег на основе эмоции
                    if not voice_tag:
                        emotion_to_voice_fallback = {
                            "anger": "[Aggressive]",
                            "rage": "[Gritty]",
                            "sadness": "[Melancholic]",
                            "joy": "[Emotional]",
                            "peace": "[Angelic]",
                            "love": "[Soulful]",
                            "fear": "[Tense]",
                            "awe": "[Epic]",
                            "epic": "[Epic]",
                        }
                        voice_tag = emotion_to_voice_fallback.get(dominant_emotion, "")
            except (ImportError, AttributeError, Exception) as e:
                log.debug(f"Не удалось использовать детальный маппинг голосов для тегов: {e}, используется упрощенный маппинг")
                # Fallback на старый маппинг
            emotion_to_voice = {
                "anger": "[Aggressive]",
                "rage": "[Gritty]",
                "sadness": "[Melancholic]",
                "joy": "[Emotional]",
                "peace": "[Angelic]",
                "love": "[Soulful]",
            }
            voice_tag = emotion_to_voice.get(dominant_emotion, "")
            
            # Add voice tag at the beginning if not present
            if voice_tag and voice_tag not in annotated_text:
                enhanced_lines.append(voice_tag)
            
            # Process each line and enhance sections using construct_section
            current_section_type = None
            for line in lines:
                # Check if line is a section tag
                if line.strip().startswith('[') and line.strip().endswith(']'):
                    section_tag = line.strip()[1:-1].upper()
                    # Try to extract section type (Intro, Verse, Chorus, etc.)
                    for section_type in ["INTRO", "VERSE", "CHORUS", "BRIDGE", "OUTRO", "PRE-CHORUS"]:
                        if section_type in section_tag:
                            current_section_type = section_type
                            # Use construct_section with modifiers based on emotions
                            modifiers = []
                            if dominant_emotion in ["anger", "rage"]:
                                modifiers.append("Aggressive")
                            elif dominant_emotion in ["sadness", "melancholy"]:
                                modifiers.append("Melancholic")
                            elif dominant_emotion in ["joy", "love"]:
                                modifiers.append("Emotional")
                            
                            # Use construct_section for better structure
                            if modifiers:
                                enhanced_section = self.suno_prompt_engine.construct_section(
                                    current_section_type, modifiers=modifiers, lyrics=""
                                )
                                enhanced_lines.append(enhanced_section.strip())
                            else:
                                enhanced_lines.append(line)
                            break
                    else:
                        enhanced_lines.append(line)
                else:
                    enhanced_lines.append(line)
                
                # Add FX tags for dramatic pauses using experimental_stack
                if line.strip() and not line.strip().startswith('['):
                    # Check if line ends with punctuation that suggests pause
                    if line.strip().endswith(('.', '!', '?')):
                        # Add pause tag occasionally for dramatic effect
                        if len(enhanced_lines) % 3 == 0:  # Every 3rd section
                            pause_tag = self.suno_prompt_engine.experimental_stack("Pause", "Dramatic")
                            enhanced_lines.append(pause_tag)
            
            return '\n'.join(enhanced_lines)
        except Exception as e:
            log.warning(f"[Suno Prompt Engine] Error enhancing annotations: {e}")
            return annotated_text

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
        # 🔧 ИСПРАВЛЕНИЕ: Инициализируем breathing_map из result, если он уже существует
        breathing_map = result.get("breathing", {})
        if not isinstance(breathing_map, dict):
            breathing_map = {}
        
        if not result.get("breathing") and not result.get("zeropulse"):
            # Use RhythmBreathingEngine if available (Matrix Architecture), otherwise fallback to legacy method
            if self.matrix_breathing_engine:
                try:
                    breathing_map = self.matrix_breathing_engine.create_map(text)
                    log.debug(f"[Matrix Breathing] Generated breathing map with {breathing_map.get('total_points', 0)} points")
                except (AttributeError, TypeError, ValueError) as e:
                    log.warning(f"[Matrix Breathing] Failed to use RhythmBreathingEngine, falling back to legacy: {e}")
                    breathing_map = self._generate_breathing_map_from_punctuation(text)
                except Exception as e:
                    log.error(f"[Matrix Breathing] Unexpected error: {e}", exc_info=True)
                    breathing_map = self._generate_breathing_map_from_punctuation(text)
            else:
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

    def _apply_quantum_jitter(self, value: float, intensity: float = 0.08) -> float:
        """
        Adds random variation to break static analysis loops.
        This introduces 'Creative Noise' to prevent deterministic results.
        """
        jitter = random.uniform(-intensity, intensity)
        return max(0.0, min(1.0, value + jitter))

    def analyze(
        self,
        text: str,
        preferred_gender: str = "auto",
        version: Optional[str] = None,
        semantic_hints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Главный метод анализа согласно ACTIVATION_BLUEPRINT.
        Выполняет анализ в строгом порядке фаз:
        - Phase 0: PREPARE (валидация, безопасность, нормализация)
        - Phase 1: PARALLEL_BATCH_A (независимые модули)
        - Phase 2: SEQUENTIAL_DEPENDENT (rhythm после emotions/tlp)
        - Phase 3: PARALLEL_BATCH_B (зависимые модули)
        - Phase 4: CORE_LOGIC (фильтрация, разрешение конфликтов)
        - Phase 5: FUSION_AND_FINALIZE (финальная сборка)
        """
        # ============================================================
        # PHASE 0: PREPARE
        # ============================================================
        log.debug(f"--- ЗАПУСК АНАЛИЗА (v{STUDIOCORE_VERSION}) ---")
        log.debug(f"Preferred Gender: {preferred_gender}, Text: {text[:40]}...")
        
        # Task 10.2: Start timer for runtime metrics
        start_time = time.time()
        
        # 0.1: validate_input_length
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from security_patches import validate_text_input
        
        try:
            text = validate_text_input(text)
        except ValueError as e:
            log.error(f"[Security] Invalid text input: {e}")
            return {
                "ok": False,
                "error": str(e),
                "result": {}
            }
        
        # 0.2: check_safety
        text = self._check_safety(text)

        # 0.3: normalize_text
        raw = normalize_text_preserve_symbols(text)
        
        # 0.4: extract_blocks
        text_blocks = extract_raw_blocks(raw)

        # Section Analysis (выполняется после extract_blocks)
        section_result = self._analyze_sections(text_blocks, preferred_gender)
        section_profiles = section_result.get("section_profiles", [])
        voice_hint = section_result.get("user_voice_hint")

        # ============================================================
        # PHASE 1: PARALLEL_BATCH_A
        # Независимые движки. Запускать одновременно.
        # ============================================================
        from .parallel_module_executor import ParallelModuleExecutor
        from .result_deduplicator import ResultDeduplicator
        
        executor = ParallelModuleExecutor(max_workers=8, timeout=30.0)
        deduplicator = ResultDeduplicator(similarity_threshold=0.85)
        
        log.debug("[Phase 1] Запуск PARALLEL_BATCH_A: emotion, tone, tlp, rde_resonance, rde_fracture, rde_entropy")
        
        # Собираем модули для параллельного выполнения
        parallel_batch_a_modules = []
        parallel_batch_a_modules.append(("emotion", self.emotion.analyze, (raw,), {}))
        parallel_batch_a_modules.append(("tone", self.tone.detect_key, (raw,), {}))
        parallel_batch_a_modules.append(("tlp", self.tlp.analyze, (raw,), {}))
        parallel_batch_a_modules.append(("rde_resonance", self.rde_engine.calc_resonance, (raw,), {}))
        parallel_batch_a_modules.append(("rde_fracture", self.rde_engine.calc_fracture, (raw,), {}))
        parallel_batch_a_modules.append(("rde_entropy", self.rde_engine.calc_entropy, (raw,), {}))
        
        # Выполняем параллельно
        batch_a_results = executor.execute_independent_modules(parallel_batch_a_modules)
        
        # Извлекаем результаты
        emotions = batch_a_results.get("emotion", {"neutral": 1.0})
        tone_hint = batch_a_results.get("tone", None)
        tlp = batch_a_results.get("tlp", {})
        
        # Собираем RDE результаты
        rde_result = {
            "resonance": batch_a_results.get("rde_resonance", 0.5),
            "fracture": batch_a_results.get("rde_fracture", 0.5),
            "entropy": batch_a_results.get("rde_entropy", 0.5),
        }
        
        log.debug(f"[Phase 1] PARALLEL_BATCH_A завершен: emotions={bool(emotions)}, tlp={bool(tlp)}, rde={bool(rde_result)}")
        
        # ============================================================
        # PHASE 2: SEQUENTIAL_DEPENDENT
        # Критическая зависимость. Ждем данные из Batch A.
        # Rhythm запускается ТОЛЬКО после завершения Emotion и TLP.
        # ============================================================
        log.debug("[Phase 2] Запуск SEQUENTIAL_DEPENDENT: rhythm (требует emotions и tlp)")
        
        cf = tlp.get("conscious_frequency") if tlp else None
        
        # Rhythm требует emotions и tlp из Phase 1
        rhythm_analysis = self.rhythm.analyze(
            raw,
            emotions=emotions,
            tlp=tlp,
            cf=cf
        )
        
        bpm = int(round(rhythm_analysis.get("global_bpm", DEFAULT_CONFIG.FALLBACK_BPM)))
        log.debug(f"[Phase 2] SEQUENTIAL_DEPENDENT завершен: bpm={bpm}")
        
        # Извлечение key из tone_hint (нужно для Phase 3)
        if tone_hint and isinstance(tone_hint, dict):
            key = tone_hint.get("key") or DEFAULT_CONFIG.FALLBACK_KEY
        else:
            key = DEFAULT_CONFIG.FALLBACK_KEY
        
        if not key or key == "auto":
            key = DEFAULT_CONFIG.FALLBACK_KEY
        
        # ============================================================
        # PHASE 3: PARALLEL_BATCH_B
        # Зависимые от ритма и эмоций движки. Запускать одновременно.
        # ============================================================
        log.debug("[Phase 3] Запуск PARALLEL_BATCH_B: vocal, integrity, annotation, color, dynamic_emotion")
        
        # Собираем модули для параллельного выполнения
        parallel_batch_b_modules = []
        
        # Vocal Allocator
        parallel_batch_b_modules.append(("vocal", self.vocal_allocator.analyze, (emotions, tlp, bpm, raw), {}))
        
        # Integrity Scan
        parallel_batch_b_modules.append(("integrity", self.integrity.analyze, (raw,), {"emotions": emotions, "tlp": tlp}))
        
        # Text Annotation: УДАЛЕНО из Phase 3 - будет вызван в Phase 4 после построения semantic_sections
        # Это устраняет двойную работу и улучшает производительность
        
        # Color Resolution
        intermediate_result = {"emotions": emotions, "tlp": tlp, "style": {}}
        parallel_batch_b_modules.append(("color", self.color_engine.resolve_color_wave, (intermediate_result,), {}))
        
        # Dynamic Emotion Engine
        if self.dynamic_emotion_engine:
            parallel_batch_b_modules.append(("dynamic_emotion", self.dynamic_emotion_engine.emotion_profile, (raw,), {}))
        
        # Выполняем параллельно
        batch_b_results = executor.execute_independent_modules(parallel_batch_b_modules)
        
        # Извлекаем результаты
        vocal_result = batch_b_results.get("vocal", {})
        if not isinstance(vocal_result, dict):
            vocal_result = {}
        
        # Обогащаем vocal_result дополнительными данными
        if emotions and isinstance(emotions, dict) and len(emotions) > 0:
            # Определяем доминирующую эмоцию для texture
            dominant_emotion = max(emotions, key=emotions.get)
            intensity = emotions[dominant_emotion]
            
            # Добавляем texture если отсутствует
            if not vocal_result.get("texture"):
                mood = dominant_emotion
                texture = self._infer_texture_from_mood(mood, emotions)
                vocal_result["texture"] = texture
            
            # Добавляем section_techniques если есть semantic_sections
            # (будет добавлено позже в Phase 4, когда semantic_sections будут готовы)
        
        integrity_result = batch_b_results.get("integrity", {})
        # Annotation будет вызван в Phase 4 после построения semantic_sections
        annotated_text_ui, annotated_text_suno = "", ""
        
        color_resolution = batch_b_results.get("color", None)
        emotion_profile_7axis = batch_b_results.get("dynamic_emotion", None)
        
        # Извлечение color_wave
        if color_resolution and hasattr(color_resolution, 'colors') and color_resolution.colors:
            color_wave = color_resolution.colors
        else:
            color_wave = ["#FFFFFF", "#B0BEC5"]
        
        log.debug(f"[Phase 3] PARALLEL_BATCH_B завершен: vocal={bool(vocal_result)}, integrity={bool(integrity_result)}, color={bool(color_wave)}")
        
        # ============================================================
        # PHASE 4: CORE_LOGIC
        # Последовательная обработка: фильтрация, разрешение конфликтов, построение стиля
        # ============================================================
        log.debug("[Phase 4] Запуск CORE_LOGIC: filter_emotions, resolve_conflicts, determine_matrix_mode, hybrid_genre_refinement, build_semantic_layers")
        
        # 4.1: filter_emotions
        emotion_high_signal = DEFAULT_CONFIG.EMOTION_HIGH_SIGNAL
        if emotions:
            filtered_emotions = {
                k: v for k, v in emotions.items() 
                if v >= emotion_high_signal or k == max(emotions, key=emotions.get)
            }
            if len(filtered_emotions) < len(emotions) and len(filtered_emotions) > 0:
                total_filtered = sum(filtered_emotions.values())
                if total_filtered > 0:
                    emotions = {k: v / total_filtered for k, v in filtered_emotions.items()}
                    log.debug(f"[Phase 4.1] Эмоции отфильтрованы: {emotions}")
                else:
                    dominant = max(emotions, key=emotions.get)
                    emotions = {dominant: 1.0}
                    log.debug(f"[Phase 4.1] Оставлена доминирующая эмоция: {dominant}")

        # 4.2: resolve_bpm_conflict
        consistency = ConsistencyLayerV8({"bpm": bpm, "tlp": tlp})
        suggested_bpm, was_resolved = consistency.resolve_bpm_tlp_conflict(bpm, tlp)
        if was_resolved:
            log.debug(f"[Phase 4.2] BPM-TLP конфликт разрешен: {bpm} → {suggested_bpm}")
            bpm = int(round(suggested_bpm))

        # 4.3: resolve_key_conflict
        # Key уже извлечен из tone_hint в Phase 2, но можем проверить конфликты
        resolver = GenreConflictResolver()
        suggested_key, was_key_resolved = resolver.resolve_color_key_conflict(key, color_wave, {})
        if was_key_resolved:
            log.debug(f"[Phase 4.3] Color-Key конфликт разрешен: {key} → {suggested_key}")
            key = suggested_key
        
        # 4.4: build_semantic_layers (нужно для annotation и structure)
        semantic_layers = self._build_semantic_layers(emotions, tlp, bpm, key)
        semantic_sections = semantic_layers.get("layers", {}).get("sections", [])
        
        layout = DEFAULT_CONFIG.FALLBACK_STRUCTURE
        if semantic_sections and len(semantic_sections) > 0:
            layout = semantic_sections[0].get("tag", DEFAULT_CONFIG.FALLBACK_STRUCTURE)
        
        structure = {
            "sections": text_blocks,
            "section_count": len(text_blocks),
            "layout": layout,
        }
        
        # Обновляем annotation с правильными semantic_sections
        if semantic_sections:
            annotation_result = self.annotate_text(text_blocks, section_profiles, semantic_sections)
        if isinstance(annotation_result, tuple) and len(annotation_result) == 2:
            annotated_text_ui, annotated_text_suno = annotation_result
        
        # 4.5: determine_matrix_mode_or_legacy
        # Task 1.3: Style.build() с поддержкой Matrix Architecture
        style = None
        # Variables for Matrix Mode data (for GUI)
        quantum_jitter_data = None
        serendipity_data = None
        fibonacci_data = None
        
        if self.matrix_enabled and self.matrix_genre_engine:
            # === MATRIX MODE: Use UniversalMatrixGenreEngine ===
            try:
                # Extract pain, energy, density from TLP and text analysis
                pain_score = tlp.get("pain", 0.0)
                # Calculate energy from text structure
                text_lines = [l for l in raw.split('\n') if l.strip()]
                avg_line_len = sum(len(l) for l in text_lines) / len(text_lines) if text_lines else 50
                energy_score = min(1.0, (avg_line_len / 60.0) + (bpm / 200.0))
                density_score = min(1.0, len(text_lines) / 10.0)
                
                # Apply Quantum Jitter (Creative Noise) to prevent deterministic results
                j_pain = self._apply_quantum_jitter(pain_score)
                j_energy = self._apply_quantum_jitter(energy_score)
                j_density = self._apply_quantum_jitter(density_score)
                
                # Save Quantum Jitter data for GUI
                quantum_jitter_data = {
                    "pain": {"original": pain_score, "jittered": j_pain},
                    "energy": {"original": energy_score, "jittered": j_energy},
                    "density": {"original": density_score, "jittered": j_density},
                }
                
                # Force Fibonacci Rotation (increment counter to rotate sunflower)
                fibonacci_counter = None
                if self.matrix_serendipity:
                    # Explicitly increment counter to ensure rotation on every run
                    self.matrix_serendipity.counter += 1
                    fibonacci_counter = self.matrix_serendipity.counter
                    # Also call fibonacci_select to maintain internal state
                    self.matrix_serendipity.fibonacci_select(["dummy"])
                    # Save Fibonacci Rotation data for GUI
                    fibonacci_data = {"counter": fibonacci_counter}
                
                # Resolve genre using Matrix Engine with jittered values
                matrix_genre, confidence = self.matrix_genre_engine.resolve_genre(
                    pain=j_pain, energy=j_energy, density=j_density
                )
                
                # Apply Serendipity (luck factor)
                serendipity_applied = False
                final_genre = matrix_genre
                if self.matrix_serendipity:
                    final_genre = self.matrix_serendipity.roll_for_serendipity(matrix_genre)
                    serendipity_applied = (final_genre != matrix_genre)
                
                # Save Serendipity data for GUI
                serendipity_data = {
                    "applied": serendipity_applied,
                    "original_genre": matrix_genre,
                    "final_genre": final_genre,
                }
                
                # Select instruments
                # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: EMOTIONS → STYLE (в Matrix Mode)
                # Безопасное получение primary_emotion
                if emotions and isinstance(emotions, dict) and len(emotions) > 0:
                    try:
                        primary_emotion = max(emotions, key=emotions.get)
                    except (ValueError, TypeError):
                        primary_emotion = list(emotions.keys())[0] if emotions else "neutral"
                else:
                    primary_emotion = "neutral"
                    log.debug("[Chain Fix] emotions invalid in Matrix Mode, using neutral")
                
                instruments = self.matrix_instrument_engine.select_instruments(
                    genre_profile=final_genre,
                    energy=energy_score,
                    mood=primary_emotion
                ) if self.matrix_instrument_engine else []
                
                # Get top genres for GUI (alternative genres)
                top_genres_list = []
                try:
                    # Try to get alternative genres from matrix engine if available
                    if hasattr(self.matrix_genre_engine, 'get_top_genres'):
                        top_genres_list = self.matrix_genre_engine.get_top_genres(
                            pain=j_pain, energy=j_energy, density=j_density, top_n=5
                        )
                    else:
                        # Fallback: create list with current genre
                        top_genres_list = [(final_genre, confidence)]
                except Exception as e:
                    log.debug(f"[Matrix] Could not get top genres: {e}")
                    top_genres_list = [(final_genre, confidence)]
                
                # Build style result with Matrix data
                style = {
                    "genre": final_genre,
                    "style": final_genre,
                    "bpm": bpm,
                    "key": key,
                    "confidence": confidence,
                    "instruments": instruments,
                    "genre_source": "universal_matrix_fibonacci",
                    "matrix_mode": True,
                    "visual": DEFAULT_CONFIG.FALLBACK_VISUAL,
                    "narrative": DEFAULT_CONFIG.FALLBACK_NARRATIVE,
                    "structure": DEFAULT_CONFIG.FALLBACK_STRUCTURE,
                    "emotion": primary_emotion,
                    "top_genres": top_genres_list,  # Add top genres for GUI
                }
                log.debug("[Matrix] Genre resolved: %s (confidence: %.2f)", final_genre, confidence)
            except (AttributeError, TypeError, ValueError, KeyError) as e:
                log.warning("[Matrix] Error in Matrix mode, falling back to legacy: %s", e)
                # Fall through to legacy mode
                style = None
            except Exception as e:
                # Catch-all для неожиданных ошибок
                log.error("[Matrix] Unexpected error in Matrix mode: %s", e, exc_info=True)
                style = None
        
        # === LEGACY MODE: Use PatchedStyleMatrix (if Matrix didn't work) ===
        if style is None:
            if self.style:
                style_result = self.style.build(
                    emotions, tlp, raw, bpm, semantic_hints, voice_hint
                )
                style = style_result
                
                # 🎯 ИСПОЛЬЗОВАНИЕ РАСШИРЕННОЙ БАЗЫ ДАННЫХ: Обогащаем жанр данными из GENRE_DATABASE_EXPANDED.json
                if style and self.genre_database:
                    try:
                        genre_from_style = style.get("genre", "")
                        if genre_from_style:
                            genre_key_normalized = genre_from_style.lower().replace(" ", "_").replace("-", "_")
                            expanded_genre_data = self.genre_database.get_genre(genre_key_normalized)
                            
                            if expanded_genre_data:
                                log.debug(f"[Genre Database] Найден жанр в расширенной базе (Legacy Mode): {genre_key_normalized}")
                                
                                # Обновляем BPM из расширенной базы (если доступен)
                                db_bpm = self.genre_database.get_bpm(genre_key_normalized)
                                if db_bpm and isinstance(db_bpm, dict):
                                    style["bpm"] = db_bpm.get("default", style.get("bpm", bpm))
                                
                                # Обновляем Key из расширенной базы (если доступен)
                                db_keys = self.genre_database.get_key(genre_key_normalized)
                                if db_keys and isinstance(db_keys, list) and len(db_keys) > 0:
                                    style["key"] = db_keys[0]
                                
                                # Добавляем цвета из расширенной базы
                                db_colors = self.genre_database.get_colors(genre_key_normalized)
                                if db_colors and isinstance(db_colors, list):
                                    style["genre_colors"] = db_colors
                                    style["color_wave"] = db_colors
                                
                                # Обновляем источник
                                original_source = style.get("genre_source", "legacy")
                                style["genre_source"] = f"{original_source}_expanded_db"
                    except (AttributeError, TypeError, KeyError) as e:
                        log.warning(f"[Genre Database] Ошибка обогащения жанра (Legacy Mode): {e}")
                    except Exception as e:
                        log.error(f"[Genre Database] Unexpected error enriching genre (Legacy Mode): {e}", exc_info=True)
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
                    "emotion": (
                        max(emotions, key=emotions.get) 
                        if emotions and isinstance(emotions, dict) and len(emotions) > 0
                        else DEFAULT_CONFIG.FALLBACK_EMOTION
                    ),
                }
                log.warning("Style engine недоступен, используются FALLBACK значения")

        # 🛡️ ЗАЩИТА: Гарантируем, что style никогда не None перед использованием в Fusion Engine
        if style is None:
            log.error("[CRITICAL] Style остался None после всех попыток инициализации, используем минимальный fallback")
            style = {
                "genre": DEFAULT_CONFIG.FALLBACK_STYLE,
                "style": DEFAULT_CONFIG.FALLBACK_STYLE,
                "bpm": bpm if isinstance(bpm, (int, float)) else DEFAULT_CONFIG.FALLBACK_BPM,
                "key": key if key else DEFAULT_CONFIG.FALLBACK_KEY,
                "visual": DEFAULT_CONFIG.FALLBACK_VISUAL,
                "narrative": DEFAULT_CONFIG.FALLBACK_NARRATIVE,
                "structure": DEFAULT_CONFIG.FALLBACK_STRUCTURE,
                "emotion": DEFAULT_CONFIG.FALLBACK_EMOTION,
            }
        
        # 4.6: hybrid_genre_refinement
        if self.hybrid_genre_engine and style:
            try:
                genre = style.get("genre")
                if genre and genre not in ("auto", "unknown", ""):
                    context = {
                        "emotions": emotions or {},
                        "tlp": tlp or {},
                        "bpm": bpm,
                        "key": key,
                    }
                    resolved_genre = self.hybrid_genre_engine.resolve(genre=genre, context=context)
                    if resolved_genre and isinstance(resolved_genre, str) and resolved_genre != genre:
                        style["genre"] = resolved_genre
                        original_source = style.get("genre_source", "unknown")
                        style["genre_source"] = f"{original_source}_hybrid_refined"
                        log.debug(f"[Phase 4.6] Hybrid genre refined: {genre} → {resolved_genre}")
                        if "hybrid" in resolved_genre.lower():
                            genre_parts = resolved_genre.lower().replace(" hybrid", "").split()
                            if len(genre_parts) >= 2:
                                style["secondary_genre"] = genre_parts[1]
                                style["is_hybrid"] = True
            except (AttributeError, TypeError, ValueError) as e:
                log.warning(f"[Phase 4.6] Hybrid genre refinement failed: {e}")
            except Exception as e:
                log.error(f"[Phase 4.6] Unexpected error in hybrid genre refinement: {e}", exc_info=True)
        
        log.debug(f"[Phase 4] CORE_LOGIC завершен: style={bool(style)}, semantic_layers={bool(semantic_layers)}")

        # Semantic Layers, Vocal, Integrity, Annotation уже выполнены параллельно выше
        # Используем результаты из style_dependent_results
        
        # Обогащаем vocal_result section_techniques на основе semantic_sections
        if semantic_sections and isinstance(semantic_sections, list) and len(semantic_sections) > 0:
            try:
                from .vocal_techniques import get_vocal_for_section
                
                section_techniques_list = []
                for section in semantic_sections:
                    if isinstance(section, dict):
                        section_emotion = section.get("emotion") or dominant_emotion if emotions else "neutral"
                        section_intensity = section.get("intensity") or (emotions.get(section_emotion, 0.5) if emotions and isinstance(emotions, dict) else 0.5)
                        section_name = section.get("tag") or section.get("name") or "Verse"
                        genre_name = style.get("genre") if style else None
                        
                        # Получаем вокальную технику для секции
                        section_tech = get_vocal_for_section(
                            section_emotion=section_emotion,
                            section_intensity=section_intensity,
                            global_emotion=dominant_emotion if emotions else None,
                            genre=genre_name,
                            section_name=section_name
                        )
                        section_techniques_list.append(section_tech)
                
                if section_techniques_list:
                    vocal_result["section_techniques"] = section_techniques_list
                    log.debug(f"[Vocal] Added {len(section_techniques_list)} section techniques to vocal_result")
            except (ImportError, AttributeError, Exception) as e:
                log.debug(f"[Vocal] Could not add section techniques: {e}")
        
        # --- SUNO PROMPT ENGINE: Enhance annotations with advanced tags ---
        if self.suno_prompt_engine and annotated_text_suno:
            try:
                # Enhance annotated_text_suno with advanced Suno tags
                # This adds structure tags, voice tags, and FX tags where appropriate
                enhanced_suno = self._enhance_suno_annotations(
                    annotated_text_suno, 
                    emotions, 
                    vocal_result,
                    style
                )
                if enhanced_suno:
                    annotated_text_suno = enhanced_suno
                    log.debug("[Suno Prompt Engine] Annotations enhanced with advanced tags")
                
                # 📊 ДОПОЛНИТЕЛЬНЫЙ: Also use get_style_prompt as alternative style description
                # Это альтернативный формат от SunoPromptEngine, не основной источник
                if style and style.get("genre"):
                    genre = style.get("genre", "")
                    
                    # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: EMOTIONS → STYLE (в SunoPromptEngine)
                    # Безопасное получение vibe из emotions
                    if emotions and isinstance(emotions, dict) and len(emotions) > 0:
                        try:
                            vibe_from_emotions = max(emotions, key=emotions.get)
                        except (ValueError, TypeError):
                            vibe_from_emotions = list(emotions.keys())[0] if emotions else "neutral"
                    else:
                        vibe_from_emotions = "neutral"
                    
                    vibe = style.get("mood") or style.get("atmosphere") or vibe_from_emotions
                    
                    # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: STYLE → INSTRUMENTS
                    # Безопасное извлечение instruments из style
                    instruments_list = style.get("instruments", [])
                    if isinstance(instruments_list, list) and len(instruments_list) > 0:
                        instruments_str = instruments_list
                    else:
                        instruments_str = []
                        log.debug("[Chain Fix] instruments invalid in style, using empty list")
                    
                    style_prompt_alt = self.suno_prompt_engine.get_style_prompt(genre, vibe, instruments_str)
                    style["suno_style_prompt_alt"] = style_prompt_alt
                    log.debug(f"[Suno Prompt Engine] Alternative style prompt: {style_prompt_alt}")
            except (AttributeError, TypeError, KeyError) as e:
                log.warning(f"[Suno Prompt Engine] Failed to enhance annotations: {e}")
            except Exception as e:
                log.error(f"[Suno Prompt Engine] Unexpected error enhancing annotations: {e}", exc_info=True)

        # --- DYNAMIC EMOTION ENGINE: Get normalized emotion profile ---
        # ✅ УЖЕ ВЫПОЛНЕНО ПАРАЛЛЕЛЬНО ВЫШЕ (строка 1293, результат в emotion_profile_7axis)
        # emotion_profile_7axis уже извлечен из style_dependent_results (строка 1308)
        if emotion_profile_7axis:
            log.debug(f"[Dynamic Emotion Engine] 7-axis profile already generated (parallel)")

        # --- EMOTION-DRIVEN SUNO ADAPTER: Build emotion-based annotations ---
        emotion_driven_annotations = None
        if self.emotion_suno_adapter_available and structure:
            try:
                # Prepare emotion curve from emotions and TLP
                # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: EMOTIONS → STYLE (в EmotionDrivenSunoAdapter)
                # Безопасное получение dominant_cluster из emotions
                if emotions and isinstance(emotions, dict) and len(emotions) > 0:
                    try:
                        dominant_cluster = max(emotions, key=emotions.get)
                    except (ValueError, TypeError):
                        dominant_cluster = list(emotions.keys())[0] if emotions else "narrative"
                else:
                    dominant_cluster = "narrative"
                    log.debug("[Chain Fix] emotions invalid in EmotionDrivenSunoAdapter, using narrative")
                
                emotion_curve = {
                    "dominant_cluster": dominant_cluster,
                    "global_tlp": tlp or {},
                }
                
                # Prepare sections from structure
                # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: STRUCTURE → SECTIONS
                # Безопасное извлечение sections из structure
                sections_data = []
                if structure and isinstance(structure, dict):
                    structure_sections = structure.get("sections", [])
                    if isinstance(structure_sections, list) and len(structure_sections) > 0:
                        # Используем sections из structure
                        pass
                    else:
                        # Fallback на text_blocks если sections пустой
                        structure_sections = text_blocks if text_blocks else []
                        log.debug("[Chain Fix] structure.sections invalid, using text_blocks fallback")
                else:
                    # Fallback если structure невалидный
                    structure_sections = text_blocks if text_blocks else []
                    log.debug("[Chain Fix] structure invalid, using text_blocks fallback")
                
                for idx, section_text in enumerate(structure_sections):
                    # Безопасное получение intensity из emotions
                    intensity = 0.5
                    if emotions and isinstance(emotions, dict):
                        intensity = emotions.get("joy", emotions.get("happiness", 0.5))
                    
                    sections_data.append({
                        "section": f"section_{idx+1}",
                        "name": f"Section {idx+1}",
                        "intensity": intensity,
                        "hot_phrases": [],
                    })
                
                # Build emotion-driven annotations
                emotion_driven_annotations = build_suno_annotations(
                    raw, sections_data, emotion_curve
                )
                log.debug(f"[Emotion Suno Adapter] Built annotations: {emotion_driven_annotations.get('style', 'N/A')}")
            except (AttributeError, TypeError, KeyError, ValueError) as e:
                log.warning(f"[Emotion Suno Adapter] Failed to build annotations: {e}")
            except Exception as e:
                log.error(f"[Emotion Suno Adapter] Unexpected error building annotations: {e}", exc_info=True)

        # --- SUNO ANNOTATION ENGINE: Build safe annotations ---
        suno_safe_annotations = None
        if self.suno_annotation_engine and structure:
            try:
                # Get section texts
                # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: STRUCTURE → SECTIONS (в SunoAnnotationEngine)
                # Безопасное извлечение sections из structure
                if structure and isinstance(structure, dict):
                    section_texts = structure.get("sections", [])
                    if not isinstance(section_texts, list) or len(section_texts) == 0:
                        # Fallback на text_blocks если sections невалидный
                        section_texts = text_blocks if text_blocks else []
                        log.debug("[Chain Fix] structure.sections invalid in SunoAnnotationEngine, using text_blocks")
                else:
                    # Fallback если structure невалидный
                    section_texts = text_blocks if text_blocks else []
                    log.debug("[Chain Fix] structure invalid in SunoAnnotationEngine, using text_blocks")
                
                # Prepare diagnostics for annotation engine
                diagnostics_for_annotations = {
                    "legacy": {
                        "style": style,
                        "bpm": bpm,
                    },
                    "out": {
                        "emotions": emotions,
                        "tlp": tlp,
                        "bpm": {"estimate": bpm} if isinstance(bpm, (int, float)) else bpm,
                        "tone": {"key": key} if key else {},
                        "vocal": vocal_result,
                    },
                }
                
                # Build safe annotations
                suno_safe_annotations = self.suno_annotation_engine.build_suno_safe_annotations(
                    section_texts, diagnostics_for_annotations
                )
                log.debug(f"[Suno Annotation Engine] Built {len(suno_safe_annotations)} safe annotations")
            except (AttributeError, TypeError, KeyError) as e:
                log.warning(f"[Suno Annotation Engine] Failed to build safe annotations: {e}")
            except Exception as e:
                log.error(f"[Suno Annotation Engine] Unexpected error building safe annotations: {e}", exc_info=True)

        # Color Resolution уже выполнено параллельно выше
        # Обновляем intermediate_result с актуальным style для повторного использования
        if style and color_resolution:
            try:
                # ✅ УЖЕ ВЫПОЛНЕНО ПАРАЛЛЕЛЬНО ВЫШЕ (строка 1289, результат в color_resolution)
                # color_resolution уже извлечен из style_dependent_results (строка 1307)
                # color_wave уже извлечен из color_resolution (строка 1311-1314)
                # Если style изменился, можно пересчитать, но для оптимизации используем существующий результат
                if not color_wave or color_wave == ["#FFFFFF", "#B0BEC5"]:
                    # Только если color_wave не был установлен, пересчитываем
                    intermediate_result = {
                        "emotions": emotions,
                        "tlp": tlp,
                        "style": style,
                    }
                    color_resolution = self.color_engine.resolve_color_wave(intermediate_result)
                    if color_resolution and hasattr(color_resolution, 'colors') and color_resolution.colors:
                        color_wave = color_resolution.colors
            except Exception as e:
                log.warning(f"[Color Engine] Error recalculating with style: {e}")
                # Используем предыдущий результат
                pass
        
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

        # ============================================================
        # 🥇 ИЕРАРХИЯ СОЗДАНИЯ SUNO ПРОМПТОВ (ПОРЯДОК ВЫПОЛНЕНИЯ)
        # ============================================================
        # Порядок создания НЕ совпадает с приоритетом использования!
        # Сначала создаем базовые промпты, потом золотой стандарт.
        #
        # 1. 🥈 ВЫСОКИЙ: build_suno_prompt (Legacy Bridge) - создается первым
        #    - Профессиональный форматтер с Matrix Architecture данными
        #    - Результат: style["suno_ready_prompt"]
        # 2. 📊 ДОПОЛНИТЕЛЬНЫЙ: SunoPromptEngine.get_style_prompt() - создается в _enhance_suno_annotations
        #    - Альтернативный формат
        #    - Результат: style["suno_style_prompt_alt"]
        # 3. 🗺️ МАППИНГ: GenreRoutingEngine.SUNO_STYLE - создается в Fusion Engine секции
        #    - Suno стиль из маппинга жанров
        #    - Результат: style["suno_style_from_routing"]
        # 4. 🥇 ЗОЛОТОЙ СТАНДАРТ: FusionEngine - создается последним (использует все предыдущие данные)
        #    - Объединяет все источники (emotion, bpm, tonality, color, instrumentation, vocal)
        #    - Результат: fusion_summary["suno_style_prompt"] и fusion_summary["suno_lyrics_prompt"]
        #    - Также сохраняется в: style["suno_style_prompt_fusion"] и style["suno_lyrics_prompt_fusion"]
        # ============================================================
        
        # --- Legacy Bridge: Build Suno Prompt using legacy formatter ---
        # 🥈 ВЫСОКИЙ ПРИОРИТЕТ: Профессиональный форматтер (создается первым)
        if LEGACY_SUNO_AVAILABLE and style:
            try:
                # Prepare data for the legacy formatter
                genre = style.get("genre", "Unknown")
                # 🔧 ИСПРАВЛЕНИЕ: Проверка типа для instruments_list
                instruments_list = style.get("instruments", [])
                if isinstance(instruments_list, list) and len(instruments_list) > 0:
                    instruments_str = instruments_list
                else:
                    instruments_str = []
                    log.debug("[Type Check] instruments_list invalid, using empty list")
                
                # Get mood from emotions or style
                primary_mood = (
                    max(emotions, key=emotions.get) if emotions else "neutral"
                ) if isinstance(emotions, dict) and emotions else (
                    style.get("mood") or style.get("atmosphere") or "neutral"
                )
                
                # Get vocals from vocal_result
                # 🔧 ИСПРАВЛЕНИЕ ОБРЫВА ЦЕПИ: VOCAL_RESULT → VOCALS_LIST
                # Безопасное извлечение vocals из vocal_result
                vocals_list = []
                if vocal_result and isinstance(vocal_result, dict) and len(vocal_result) > 0:
                    vocal_form = vocal_result.get("vocal_form", "solo")
                    gender = vocal_result.get("gender", "auto")
                    if gender and gender != "auto":
                        vocals_list.append(gender)
                    if vocal_form and vocal_form != "solo":
                        vocals_list.append(vocal_form)
                else:
                    log.debug("[Chain Fix] vocal_result invalid, using empty vocals_list")
                
                # Get BPM (ensure it's an int)
                bpm_val = bpm if isinstance(bpm, int) else (int(bpm) if isinstance(bpm, (float, str)) and str(bpm).isdigit() else 120)
                
                # Get key
                key_val = style.get("key") or key or "auto"
                
                # Prepare style_data dict for build_suno_prompt
                style_data_for_prompt = {
                    "genre": genre,
                    "style": style.get("style", genre),
                    "key": key_val,
                    "atmosphere": primary_mood,
                    "visual": style.get("visual", DEFAULT_CONFIG.FALLBACK_VISUAL),
                    "vocal_form": vocal_result.get("vocal_form", "solo") if isinstance(vocal_result, dict) else "solo",
                    "techniques": [],
                    # Добавляем emotions, tlp и vocal_result для определения vocal
                    "emotions": emotions if emotions and isinstance(emotions, dict) else {},
                    "tlp": tlp if tlp and isinstance(tlp, dict) else {},
                    "vocal_result": vocal_result if isinstance(vocal_result, dict) else {},
                }
                
                # Call the legacy builder to get a professional Suno string
                suno_prompt_advanced = build_suno_prompt(
                    style_data=style_data_for_prompt,
                    vocals=vocals_list,
                    instruments=instruments_str,
                    bpm=bpm_val,
                    philosophy="Matrix Architecture + Legacy Bridge",
                    version=STUDIOCORE_VERSION,
                    prompt_variant="suno_style"
                )
                
                # Save into style result
                style["suno_ready_prompt"] = suno_prompt_advanced
                log.debug("[Legacy Bridge] Suno prompt generated successfully")
            except (AttributeError, TypeError, KeyError, ValueError) as e:
                log.warning(f"[Legacy Bridge] Prompt Builder failed: {e}")
            except Exception as e:
                log.error(f"[Legacy Bridge] Unexpected error in prompt builder: {e}", exc_info=True)
                # Fallback to simple format
                genre = style.get("genre", "Unknown")
                instruments_list = style.get("instruments", [])
                instruments_str = ", ".join(str(instr) for instr in instruments_list) if isinstance(instruments_list, list) and instruments_list else "None"
                primary_mood = max(emotions, key=emotions.get) if emotions and isinstance(emotions, dict) else "neutral"
                style["suno_ready_prompt"] = f"{genre} | {instruments_str} | {primary_mood} | {bpm} BPM | {key}"
        else:
            # Fallback if legacy adapter not available
            if style:
                genre = style.get("genre", "Unknown")
                instruments_list = style.get("instruments", [])
                instruments_str = ", ".join(str(instr) for instr in instruments_list) if isinstance(instruments_list, list) and instruments_list else "None"
                primary_mood = max(emotions, key=emotions.get) if emotions and isinstance(emotions, dict) else "neutral"
                style["suno_ready_prompt"] = f"{genre} | {instruments_str} | {primary_mood} | {bpm} BPM | {key}"
        
        # Ensure suno_ready_prompt is always set (final safety check)
        if style and "suno_ready_prompt" not in style:
            # Ultimate fallback
            genre = style.get("genre", "Unknown")
            instruments_str = "None"
            primary_mood = "neutral"
            style["suno_ready_prompt"] = f"{genre} | {instruments_str} | {primary_mood} | {bpm} BPM | {key}"

        # RDE Analysis уже выполнено параллельно выше (resonance, fracture, entropy)
        # Добавляем emotion_vector если TLP доступен
        if tlp and "emotion_vector" not in rde_result:
            try:
                rde_emotion_vector = self.rde_engine.export_emotion_vector(raw)
                rde_result["emotion_vector"] = {
                    "valence": rde_emotion_vector.valence,
                    "arousal": rde_emotion_vector.arousal,
                }
            except Exception as e:
                log.warning(f"Не удалось экспортировать RDE emotion vector: {e}")
        
        # Task 18.1: Auto-resolve Genre-RDE conflicts (part of Phase 4)
        genre = style.get("genre", "") if style else ""
        adjusted_rde, was_resolved = consistency.resolve_genre_rde_conflict(genre, rde_result)
        if was_resolved:
            log.debug(f"Genre-RDE Konflikt aufgelöst: {rde_result} → {adjusted_rde}")
            rde_result = adjusted_rde

        # ============================================================
        # PHASE 5: FUSION_AND_FINALIZE
        # Финальная сборка: suno_prompt_generation, fusion_engine_routing, deduplicate_results, assemble_final_json
        # ============================================================
        log.debug("[Phase 5] Запуск FUSION_AND_FINALIZE: suno_prompt_generation, fusion_engine_routing, deduplicate_results, assemble_final_json")
        
        # 5.1: suno_prompt_generation (Legacy Bridge)
        if LEGACY_SUNO_AVAILABLE and style:
            try:
                genre = style.get("genre", "Unknown")
                instruments_list = style.get("instruments", [])
                instruments_str = instruments_list if isinstance(instruments_list, list) and len(instruments_list) > 0 else []
                primary_mood = max(emotions, key=emotions.get) if emotions and isinstance(emotions, dict) else "neutral"
                vocals_list = []
                if vocal_result and isinstance(vocal_result, dict):
                    gender = vocal_result.get("gender", "auto")
                    if gender and gender != "auto":
                        vocals_list.append(gender)
                bpm_val = bpm if isinstance(bpm, int) else (int(bpm) if isinstance(bpm, (float, str)) and str(bpm).isdigit() else 120)
                key_val = style.get("key") or key or "auto"
                style_data_for_prompt = {
                    "genre": genre,
                    "style": style.get("style", genre),
                    "key": key_val,
                    "atmosphere": primary_mood,
                    "visual": style.get("visual", DEFAULT_CONFIG.FALLBACK_VISUAL),
                    "vocal_form": vocal_result.get("vocal_form", "solo") if isinstance(vocal_result, dict) else "solo",
                    "techniques": [],
                    # Добавляем emotions, tlp и vocal_result для определения vocal
                    "emotions": emotions if emotions and isinstance(emotions, dict) else {},
                    "tlp": tlp if tlp and isinstance(tlp, dict) else {},
                    "vocal_result": vocal_result if isinstance(vocal_result, dict) else {},
                }
                suno_prompt_advanced = build_suno_prompt(
                    style_data=style_data_for_prompt,
                    vocals=vocals_list,
                    instruments=instruments_str,
                    bpm=bpm_val,
                    philosophy="Matrix Architecture + Legacy Bridge",
                    version=STUDIOCORE_VERSION,
                    prompt_variant="suno_style"
                )
                style["suno_ready_prompt"] = suno_prompt_advanced
                log.debug("[Phase 5.1] Suno prompt generated (Legacy Bridge)")
            except Exception as e:
                log.warning(f"[Phase 5.1] Suno prompt generation failed: {e}")
                if style:
                    genre = style.get("genre", "Unknown")
                    style["suno_ready_prompt"] = f"{genre} | {bpm} BPM | {key}"
        
        # 5.2: fusion_engine_routing
        fusion_summary = None
        if self.fusion_engine and self.genre_routing_engine:
            try:
                # Get dominant emotion for genre routing
                dominant_emotion = max(emotions, key=emotions.get) if emotions and isinstance(emotions, dict) else "neutral"
                
                # Get genre route from GenreRoutingEngineV64
                genre_route = self.genre_routing_engine.route(emotions or {}, dominant_emotion)
                log.debug(f"[Fusion Engine] Genre route: {genre_route}")
                
                # 🗺️ МАППИНГ: Also use SUNO_STYLE mapping directly to enhance style
                # Это дополнительный источник для style, не основной
                if genre_route.get("suno_style") and style:
                    style["suno_style_from_routing"] = genre_route["suno_style"]
                    log.debug(f"[Genre Routing] Suno style from routing: {genre_route['suno_style']}")
                
                # Prepare payload in format expected by FusionEngine
                # FusionEngine expects: legacy, emotion, bpm, tonality, color, instrumentation, vocal, tlp
                fusion_payload = {
                    "legacy": {
                        "style": style,
                        "bpm": bpm,
                        "instruments": style.get("instruments", []),
                        "vocals": vocal_result.get("vocals", []) if isinstance(vocal_result, dict) else [],
                        "vocal_form": vocal_result.get("vocal_form", "solo") if isinstance(vocal_result, dict) else "solo",
                        "tlp": tlp,
                    },
                    "emotion": {
                        "profile": emotions or {},
                        "dominant": dominant_emotion,
                    },
                    "bpm": {
                        "estimate": bpm if isinstance(bpm, (int, float)) else 120,
                        "target_bpm": bpm if isinstance(bpm, (int, float)) else 120,
                    },
                    "tonality": {
                        "section_keys": [key] if key else [],
                        "fallback_key": key or "C (C minor)",
                    },
                    "color": {
                        "profile": {
                            "primary_color": color_wave[0] if color_wave else "soft light",
                            "accent_color": color_wave[-1] if len(color_wave) > 1 else "shadows",
                        },
                        "wave": color_wave,
                    },
                    "instrumentation": {
                        "selection": {
                            "selected": style.get("instruments", []),
                        },
                        "palette": style.get("instruments", []),
                    },
                    "vocal": {
                        "tone": vocal_result.get("tone", "neutral") if isinstance(vocal_result, dict) else "neutral",
                        "style": vocal_result.get("style", "standard") if isinstance(vocal_result, dict) else "standard",
                        "gender": vocal_result.get("gender", "auto") if isinstance(vocal_result, dict) else "auto",
                    },
                    "tlp": tlp,
                }
                
                # Call FusionEngine.fuse()
                fusion_summary = self.fusion_engine.fuse(fusion_payload, genre_route=genre_route)
                log.debug(f"[Fusion Engine] Fusion summary generated: {fusion_summary.get('final_genre', 'N/A')}")
                
                # 🥇 ЗОЛОТОЙ СТАНДАРТ: Update style with fusion results if available
                # Fusion Engine объединяет все источники и создает лучшие промпты
                if fusion_summary:
                    # Merge fusion results into style
                    if fusion_summary.get("final_genre"):
                        style["genre"] = fusion_summary["final_genre"]
                    if fusion_summary.get("final_subgenre"):
                        style["subgenre"] = fusion_summary["final_subgenre"]
                    if fusion_summary.get("mood"):
                        style["mood"] = fusion_summary["mood"]
                    if fusion_summary.get("suno_style_prompt"):
                        # Store fusion suno prompt (это золотой стандарт, но сохраняем как альтернативу для совместимости)
                        # Основной промпт будет в fusion_summary["suno_style_prompt"] и используется в app.py с приоритетом 1
                        style["suno_style_prompt_fusion"] = fusion_summary["suno_style_prompt"]
                    if fusion_summary.get("suno_lyrics_prompt"):
                        # Store fusion lyrics prompt (это золотой стандарт для lyrics)
                        style["suno_lyrics_prompt_fusion"] = fusion_summary["suno_lyrics_prompt"]
                    
                    log.debug("[Phase 5.2] Fusion Engine: Style updated with fusion results")
            except Exception as e:
                log.warning(f"[Phase 5.2] Fusion Engine failed: {e}")
                fusion_summary = None

        # Task 10.2: Calculate runtime
        runtime_ms = int((time.time() - start_time) * 1000)

        # 5.3: deduplicate_results
        breathing_map = {}
        all_module_results: List[Tuple[str, Dict[str, Any]]] = []
        
        # Собираем результаты от всех модулей
        all_module_results.append(("emotion_engine", {"emotions": emotions} if emotions else {}))
        all_module_results.append(("tone_engine", {"key": key, "tone_hint": tone_hint} if tone_hint else {"key": key}))
        all_module_results.append(("tlp_engine", {"tlp": tlp} if tlp else {}))
        all_module_results.append(("rhythm_engine", {"bpm": bpm, "rhythm_analysis": rhythm_analysis}))
        all_module_results.append(("rde_engine", {"rde": rde_result} if rde_result else {}))
        all_module_results.append(("semantic_layers", {"semantic_layers": semantic_layers} if semantic_layers else {}))
        all_module_results.append(("vocal_allocator", {"vocal": vocal_result} if vocal_result else {}))
        all_module_results.append(("integrity_engine", {"integrity": integrity_result} if integrity_result else {}))
        all_module_results.append(("text_annotation", {"annotated_text_ui": annotated_text_ui, "annotated_text_suno": annotated_text_suno}))
        all_module_results.append(("color_engine", {"color_wave": color_wave}))
        
        if style:
            style_source = "matrix_style" if style.get("matrix_mode") else "legacy_style"
            all_module_results.append((style_source, {"style": style}))
        
        if emotion_profile_7axis:
            all_module_results.append(("dynamic_emotion_engine", {"emotion_profile_7axis": emotion_profile_7axis}))
        
        if self.suno_prompt_engine and style and style.get("suno_style_prompt_alt"):
            all_module_results.append(("suno_prompt_engine", {"suno_style_prompt_alt": style.get("suno_style_prompt_alt")}))
        
        if emotion_driven_annotations:
            all_module_results.append(("emotion_suno_adapter", {"emotion_driven_annotations": emotion_driven_annotations}))
        
        if suno_safe_annotations:
            all_module_results.append(("suno_annotation_engine", {"suno_safe_annotations": suno_safe_annotations}))
        
        if fusion_summary:
            all_module_results.append(("fusion_engine", {"fusion": fusion_summary}))
        
        # Применяем дедупликацию
        deduplicated_result = deduplicator.deduplicate_results(all_module_results)
        log.debug(f"[Phase 5.3] Дедупликация завершена: {len(all_module_results)} модулей обработано")

        # 5.4: assemble_final_json
        log.debug("[Phase 5.4] Сборка финального JSON результата")
        result = {
            "emotions": deduplicated_result.get("emotions", emotions if emotions and isinstance(emotions, dict) else {}),
            "tlp": deduplicated_result.get("tlp", tlp if tlp and isinstance(tlp, dict) else {}),
            "bpm": deduplicated_result.get("bpm", bpm if isinstance(bpm, (int, float)) else DEFAULT_CONFIG.FALLBACK_BPM),
            "key": deduplicated_result.get("key", key if key and isinstance(key, str) else DEFAULT_CONFIG.FALLBACK_KEY),
            "structure": structure if structure and isinstance(structure, dict) else {},
            "style": deduplicated_result.get("style", style if style and isinstance(style, dict) else {}),
            "vocal": deduplicated_result.get("vocal", vocal_result if vocal_result and isinstance(vocal_result, dict) else {}),
            "semantic_layers": deduplicated_result.get("semantic_layers", semantic_layers if semantic_layers and isinstance(semantic_layers, dict) else {}),
            "integrity": deduplicated_result.get("integrity", integrity_result if integrity_result and isinstance(integrity_result, dict) else {}),
            "annotated_text_ui": deduplicated_result.get("annotated_text_ui", annotated_text_ui if annotated_text_ui and isinstance(annotated_text_ui, str) else ""),
            "annotated_text_suno": deduplicated_result.get("annotated_text_suno", annotated_text_suno if annotated_text_suno and isinstance(annotated_text_suno, str) else ""),
            "color_wave": deduplicated_result.get("color_wave", color_wave if isinstance(color_wave, list) else ["#FFFFFF", "#B0BEC5"]),
            "rde": deduplicated_result.get("rde", rde_result if rde_result and isinstance(rde_result, dict) else {}),
            "breathing_map": breathing_map if isinstance(breathing_map, dict) else {},
            "section_profiles": section_profiles if isinstance(section_profiles, list) else [],
            # Task 10.2: Add runtime metrics for diagnostics
            "runtime_ms": runtime_ms if isinstance(runtime_ms, (int, float)) else 0,
        }
        
        # Добавляем метаданные о дедупликации
        if "_deduplication_metadata" in deduplicated_result:
            result["_deduplication_metadata"] = deduplicated_result["_deduplication_metadata"]
        
        # Add fusion summary if available (enhances final result)
        if fusion_summary and isinstance(fusion_summary, dict):
            result["fusion"] = fusion_summary
            # Also add fusion prompts to style for easy access (if not already set)
            if fusion_summary.get("suno_style_prompt") and not style.get("suno_style_prompt_fusion"):
                style["suno_style_prompt_fusion"] = fusion_summary["suno_style_prompt"]
            if fusion_summary.get("suno_lyrics_prompt") and not style.get("suno_lyrics_prompt_fusion"):
                style["suno_lyrics_prompt_fusion"] = fusion_summary["suno_lyrics_prompt"]
        
        # Add emotion-driven annotations if available (с проверкой типов)
        if emotion_driven_annotations and isinstance(emotion_driven_annotations, dict):
            result["emotion_driven_annotations"] = emotion_driven_annotations
            # Also merge into style for easy access
            if emotion_driven_annotations.get("style"):
                style["emotion_driven_style"] = emotion_driven_annotations["style"]
            if emotion_driven_annotations.get("vocal_profile"):
                style["emotion_driven_vocal"] = emotion_driven_annotations["vocal_profile"]
            if emotion_driven_annotations.get("instrumentation"):
                style["emotion_driven_instruments"] = emotion_driven_annotations["instrumentation"]
        
        # Add safe annotations if available (с проверкой типов)
        if suno_safe_annotations and isinstance(suno_safe_annotations, list):
            result["suno_safe_annotations"] = suno_safe_annotations
        
        # Add 7-axis emotion profile if available (с проверкой типов)
        if emotion_profile_7axis and isinstance(emotion_profile_7axis, dict):
            result["emotion_profile_7axis"] = emotion_profile_7axis
        
        # Add Genre Selection Process data (clusters, genre_scores)
        genre_selection_data = {}
        # Try to get clusters and genre_scores from EmotionEngine
        # Note: self.emotion is AutoEmotionalAnalyzer, not EmotionEngine
        # We need to create EmotionEngine instance to get clusters and genre_scores
        try:
            from .emotion import EmotionEngine
            
            # Create EmotionEngine instance for getting clusters and genre_scores
            emotion_engine = EmotionEngine()
            emotion_profile = emotion_engine.build_emotion_profile(raw)
            
            if isinstance(emotion_profile, dict):
                clusters = emotion_profile.get("clusters", {})
                genre_scores = emotion_profile.get("genre_scores", {})
                
                if clusters or genre_scores:
                    genre_selection_data["clusters"] = clusters
                    genre_selection_data["genre_scores"] = genre_scores
                    log.debug(f"[Genre Selection] Got clusters: {len(clusters)}, genre_scores: {len(genre_scores)}")
                
                # Add top_genres to style if not already set (for Legacy Mode)
                if genre_scores and isinstance(genre_scores, dict) and not style.get("top_genres"):
                    sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                    top_genres_list = [(genre, score) for genre, score in sorted_genres if score > 0]
                    if top_genres_list:
                        style["top_genres"] = top_genres_list
                        log.debug(f"[Genre Selection] Added top_genres to style: {len(top_genres_list)} genres")
        except (ImportError, AttributeError, Exception) as e:
            log.debug(f"[Genre Selection] Could not get emotion profile from EmotionEngine: {e}")
            # Fallback: try to compute clusters and genre_scores manually if possible
            try:
                # If we have emotions, we can try to compute clusters manually
                if emotions and isinstance(emotions, dict) and len(emotions) > 0:
                    # This is a simplified fallback - not as accurate as EmotionEngine
                    log.debug("[Genre Selection] Using fallback method for clusters/genre_scores")
            except Exception as e2:
                log.debug(f"[Genre Selection] Fallback also failed: {e2}")
        
        if genre_selection_data:
            result["genre_selection"] = genre_selection_data
            log.debug(f"[Genre Selection] Saved genre_selection data: {bool(genre_selection_data.get('clusters'))}, {bool(genre_selection_data.get('genre_scores'))}")
        else:
            log.debug("[Genre Selection] No genre_selection data available")
        
        # If emotion_profile_7axis is available, try to compute genre_bias
        if emotion_profile_7axis and isinstance(emotion_profile_7axis, dict):
            try:
                from .emotion_genre_matrix import compute_genre_bias
                genre_bias = compute_genre_bias(emotion_profile_7axis)
                if genre_bias:
                    result["genre_bias"] = genre_bias
            except Exception as e:
                log.debug(f"[Genre Bias] Could not compute genre bias: {e}")
        
        # Add Genre Routing data
        if self.genre_routing_engine and emotions:
            try:
                dominant_emotion = max(emotions, key=emotions.get) if emotions and isinstance(emotions, dict) else "neutral"
                genre_route = self.genre_routing_engine.route(emotions or {}, dominant_emotion)
                if genre_route and isinstance(genre_route, dict):
                    result["genre_routing"] = genre_route
            except Exception as e:
                log.debug(f"[Genre Routing] Could not get genre route: {e}")
        
        # Add Matrix Mode specific data (Quantum Jitter, Serendipity, Fibonacci)
        if quantum_jitter_data:
            result["quantum_jitter"] = quantum_jitter_data
        if serendipity_data:
            result["serendipity"] = serendipity_data
        if fibonacci_data:
            result["fibonacci_rotation"] = fibonacci_data
        
        # Add Matrix Architecture metadata to result
        if self.matrix_enabled:
            result["matrix_architecture"] = {
                "enabled": True,
                "engines": {
                    "genre": self.matrix_genre_engine is not None,
                    "instruments": self.matrix_instrument_engine is not None,
                    "serendipity": self.matrix_serendipity is not None,
                    "breathing": self.matrix_breathing_engine is not None,
                }
            }
        
        # Add integration metadata (shows what engines are active) - с безопасными проверками
        result["integrations"] = {
            "fusion_engine": bool(self.fusion_engine),
            "hybrid_genre_engine": bool(self.hybrid_genre_engine),
            "suno_prompt_engine": bool(self.suno_prompt_engine),
            "emotion_suno_adapter": bool(self.emotion_suno_adapter_available),
            "suno_annotation_engine": bool(self.suno_annotation_engine),
            "dynamic_emotion_engine": bool(self.dynamic_emotion_engine),
            "legacy_suno_bridge": bool(LEGACY_SUNO_AVAILABLE),
            "matrix_architecture": bool(self.matrix_enabled),
            "genre_database_loader": bool(getattr(self, 'genre_database', None)),
        }
        
        # Enrich result with smart defaults for missing fields
        result = self._enrich_result_with_smart_defaults(result, text, preferred_gender)
        
        # 🔧 ИСПРАВЛЕНИЕ: Обновляем breathing_map в result после _enrich_result_with_smart_defaults
        # _enrich_result_with_smart_defaults устанавливает result["breathing"], 
        # поэтому мы обновляем result["breathing_map"] из result["breathing"]
        if isinstance(result, dict):
            breathing_data = result.get("breathing")
            if isinstance(breathing_data, dict):
                result["breathing_map"] = breathing_data
            elif not result.get("breathing_map"):
                # Если breathing_map еще не установлен, используем пустой словарь
                result["breathing_map"] = {}
        
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
