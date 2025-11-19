# -*- coding: utf-8 -*-
"""
StudioCore v4.3.11 — Monolith (v6 - Suno Аннотации)
- Исправлена ошибка f-string (строка 259)
- Внедрено централизованное логирование
- Внедрена Suno-аннотация в 'annotate_text'
"""

from __future__ import annotations
import re
import json
from statistics import mean
from typing import Dict, Any, List, Tuple, Optional
import logging

# === 1. Импорт ядра ===
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

# AI_TRAINING_PROHIBITED: Redistribution or training of AI models on this codebase
# without explicit written permission from the Author is prohibited.

from .config import load_config
# v16: ИСПРАВЛЕН ImportError
from .text_utils import normalize_text_preserve_symbols, extract_raw_blocks
# v15: Исправлен ImportError (возвращаем оригинальные имена)
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from .tone import ToneSyncEngine
from .adapter import build_suno_prompt
from .vocals import VocalProfileRegistry
from .rhythm import LyricMeter
# v11: 'PatchedStyleMatrix' - это наш 'StyleMatrix'
from .style import PatchedStyleMatrix, STYLE_VERSION 

# === 2. Настройка логгера ===
log = logging.getLogger(__name__)

# ==========================================================
# 🗣️ Утилиты определения вокала (v2 - перенесено из style.py)
# ==========================================================

def detect_voice_profile(text: str) -> str | None:
    """
    Автоматически определяет вокальные подсказки из текста.
    """
    log.debug("Вызов функции: detect_voice_profile")
    text_low = text.lower()
    patterns = [
        r"под\s+[а-яa-z\s,]+вокал",         # под хриплый мужской вокал
        r"\([\s\S]*?(вокал|voice|growl|scream|ш[её]пот|крик)[\s\S]*?\)", # (soft female growl)
        r"(мужск\w+|женск\w+)\s+вокал",
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

def detect_gender_from_grammar(text: str) -> str | None:
    """
    Определяет пол по грамматике ("я шел" / "я шла")
    """
    log.debug("Вызов функции: detect_gender_from_grammar")
    male_verbs = len(re.findall(r"\b(я\s+\w+л)\b", text, re.I))
    female_verbs = len(re.findall(r"\b(я\s+\w+ла)\b", text, re.I))
    log.debug(f"Грамматический анализ: Male хиты={male_verbs}, Female хиты={female_verbs}")

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
        emotions: Dict[str, float] | None = None,
        cf: float | None = None,
        tlp: Dict[str, float] | None = None,
        header_bpm: float | None = None,
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
        emo: Dict[str, float] | None = None,
        cf: float | None = None,
        tlp: Dict[str, float] | None = None,
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
        if cf > 0.7: rec = [4, 5, 6, 7]
        elif cf > 0.3: rec = [2, 3, 4, 5]
        else: rec = [1, 2, 3, 4]
        return {"recommended_octaves": rec}

class PatchedRNSSafety:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg.get("safety", {"safe_octaves": [2, 3, 4, 5]})
    def clamp_octaves(self, octaves: List[int]) -> List[int]:
        safe = set(self.cfg.get("safe_octaves", [2, 3, 4, 5]))
        arr = [o for o in octaves if o in safe]
        return arr or [2, 3, 4]

class PatchedIntegrityScanEngine:
    def analyze(self, text: str) -> Dict[str, Any]:
        return {"status": "OK"} # Заглушка

class AdaptiveVocalAllocator:
    def analyze(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, text: str) -> Dict[str, Any]:
        # (Логика v2... без изменений)
        return {"vocal_form": "auto", "gender": "auto", "vocal_count": 1}

# ==========================================================
# 🚀 StudioCore Monolith (v4.3.11)
# ==========================================================
class StudioCore:

    def __init__(self, config_path: str | None = None):
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
            log.info(f"🎨 [StyleMatrix] Используется патчированная версия (PatchedStyleMatrix).")
        except ImportError as e:
            log.error(f"НЕ УДАЛОСЬ загрузить PatchedStyleMatrix: {e}")
            self.style = None # type: ignore

        log.debug("Загрузка: ToneSyncEngine")
        self.tone = ToneSyncEngine()
        log.debug("Загрузка: AdaptiveVocalAllocator")
        self.vocal_allocator = AdaptiveVocalAllocator()
        
        log.info(f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section-Aware Duet Mode v2).")


    # -------------------------------------------------------
    # 🎤 (v4) Анализ вокала по секциям
    # -------------------------------------------------------
    def _analyze_sections(self, text_blocks: List[str], ui_gender: str) -> Dict[str, Any]:
        """ 
        v4: Прогоняет каждый блок текста через грамматику и хинты,
        возвращает общий профиль вокала.
        """
        log.debug("Вызов функции: _analyze_sections")
        
        section_profiles: List[Dict[str, str | None]] = []
        final_gender = "auto"
        user_voice_hint = None # Хинт, заданный пользователем
        
        # 1. Анализ каждого блока
        for block_text in text_blocks:
            # 1a. Ищем грамматику ("я шел" / "я ждала")
            g_gender = detect_gender_from_grammar(block_text)
            
            # 1b. Ищем хинты ("(шепотом)", "(мужской вокал)")
            v_hint = detect_voice_profile(block_text)
            
            if v_hint and not user_voice_hint:
                user_voice_hint = v_hint # Сохраняем первый найденный хинт
            
            section_profiles.append({
                "gender": g_gender,
                "hint": v_hint
            })
            # v5: Исправлена ошибка f-string (убрано троеточие)
            log.debug(f"Блок [{block_text[:20]}...] -> Пол: {g_gender}, Хинт: {v_hint}")


        # 2. Определение финального пола (Приоритеты)
        genders_found = {p["gender"] for p in section_profiles if p["gender"]}
        
        if ui_gender != "auto":
            final_gender = ui_gender # 1. Приоритет UI
            log.debug("Используется пол из UI")
        elif "male" in genders_found and "female" in genders_found:
            final_gender = "mixed" # 2. Грамматический дуэт
            log.debug("Грамматика определила 'mixed' (M/F)")
        elif "male" in genders_found:
            final_gender = "male" # 3. Только мужской
            log.debug("Грамматика определила 'male'")
        elif "female" in genders_found:
            final_gender = "female" # 4. Только женский
            log.debug("Грамматика определила 'female'")
        # (else: остается 'auto')
            
        log.debug(f"Итог по вокалу (все блоки): {genders_found}")
        return {
            "final_gender_preference": final_gender,
            "user_voice_hint": user_voice_hint,
            "section_profiles": section_profiles
        }

    # -------------------------------------------------------
    # 🎼 (v6) Генератор семантических секций
    # -------------------------------------------------------
    def _build_semantic_layers(self, emo: Dict[str,float], tlp: Dict[str,float], bpm: int, style_key: str) -> Dict[str, Any]:
        """ v6: Генерирует 'energy', 'arrangement' и использует 'key' """
        log.debug("Вызов функции: _build_semantic_layers")
        
        love, pain, truth = tlp.get("love",0), tlp.get("pain",0), tlp.get("truth",0)
        cf = tlp.get("conscious_frequency",0)
        avg_emo = mean(abs(v) for v in emo.values()) if emo else 0.0
        
        key = style_key # Берем тональность из style.py

        def get_focus(mood: str, energy: str) -> str:
            if energy == "high": return "climax"
            if energy == "low": return "minimal"
            if mood == "dramatic": return "contrast"
            if mood == "narrative": return "story_flow"
            return "flow"

        # (v6) Логика основана на шаблонах Suno
        intro = {
            "tag": "Intro", "mood": "mystic" if cf >= 0.5 else "calm", "energy": "low", 
            "arrangement": "minimal", "bpm": int(bpm*0.8), "key": key
        }
        verse = {
            "tag": "Verse", "mood": "narrative" if love >= truth else "reflective", "energy": "mid",
            "arrangement": "standard", "bpm": bpm, "key": key
        }
        bridge = {
            "tag": "Bridge", "mood": "dramatic" if pain > 0.3 else "dreamlike", "energy": "mid-high",
            "arrangement": "building", "bpm": int(bpm * 1.05), "key": key
        }
        chorus = {
            "tag": "Chorus", "mood": "uplifting" if love >= pain else "tense", "energy": "high",
            "arrangement": "full arrangement", "bpm": int(bpm * 1.1), "key": key
        }
        outro = {
            "tag": "Outro", "mood": "peaceful" if cf > 0.6 else "fading", "energy": "low",
            "arrangement": "minimal", "bpm": int(bpm*0.7), "key": key
        }
        
        # Добавляем 'focus' на основе mood/energy
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
        section_profiles: List[Dict[str, str | None]], 
        semantic_sections: List[Dict[str, Any]]
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
            semantic_map = ["Intro", "Verse", "Pre-Chorus", "Chorus", "Verse", "Bridge", "Outro"]
        else: # 8+
            semantic_map = ["Intro", "Verse", "Pre-Chorus", "Chorus", "Verse", "Bridge", "Chorus", "Outro"]
            
        # Дополняем карту, если блоков больше 8
        if num_blocks > len(semantic_map):
            semantic_map.extend(["Verse", "Chorus"] * (num_blocks - len(semantic_map)))
        
        # Находим определения секций
        sec_defs = {s["tag"].lower(): s for s in semantic_sections}
        # Запасные определения
        sec_defs.setdefault("pre-chorus", sec_defs["bridge"])
        sec_defs.setdefault("verse 2", sec_defs["verse"])
        # --- Конец логики мэппинга ---

        final_bpm = semantic_sections[0].get("bpm", 120) # (BPM припева)
        final_key = semantic_sections[0].get("key", "auto")
        final_vocal_form = "solo_auto" # Будет перезаписан

        for i, block_text in enumerate(text_blocks):
            if not block_text.strip():
                continue

            # 1. Берем семантику (Intro, Verse...)
            tag_name = semantic_map[i].lower()
            sem = sec_defs.get(tag_name, sec_defs["verse"]) # Fallback на 'verse'
            
            # 2. Берем вокальный профиль (Male, Female...)
            profile = section_profiles[i]
            gender_tag = profile.get("gender", "auto").upper() # MALE, FEMALE, MIXED, AUTO
            
            # 3. Собираем теги
            suno_tag_parts = [
                tag_name.upper(),
                f"vocal: {gender_tag}" if gender_tag != "AUTO" else None,
                f"mood: {sem['mood']}",
                f"energy: {sem['energy']}",
                f"arrangement: {sem['arrangement']}",
            ]
            suno_tag = f"[{' - '.join(filter(None, suno_tag_parts))}]"
            
            # UI-тег (более детальный)
            ui_tag = f"[{tag_name.upper()} - {gender_tag} - {sem['mood']}, {sem['energy']}, {sem['arrangement']}, BPM≈{sem['bpm']}]"
            
            # Обновляем финальный BPM/Key (берем из припева, если он есть)
            if "chorus" in tag_name:
                final_bpm = sem['bpm']
                final_key = sem['key']

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
    def analyze(
        self,
        text: str,
        preferred_gender: str = "auto",
        version: Optional[str] = None,
        semantic_hints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        
        log.debug(f"--- ЗАПУСК АНАЛИЗА (v{STUDIOCORE_VERSION}) ---")
        log.debug(f"Preferred Gender: {preferred_gender}, Text: {text[:40]}...")
        
        if not self.style:
            return {"error": "StyleMatrix не загружен."}

        version = version or self.cfg.get("suno_version", "v5")
        
        # 1. Базовый анализ
        log.debug("Вызов: normalize_text_preserve_symbols")
        raw = normalize_text_preserve_symbols(text)
        
        log.debug("Вызов: self.emotion.analyze")
        emo = self.emotion.analyze(raw)
        log.debug(f"Результат EMO: {emo}")
        
        log.debug("Вызов: self.tlp.analyze")
        tlp = self.tlp.analyze(raw)
        log.debug(f"Результат TLP: {tlp}")
        
        log.debug("Вызов: self.rhythm.analyze")
        rhythm_analysis = self.rhythm.analyze(
            raw,
            emotions=emo,
            tlp=tlp,
            cf=tlp.get("conscious_frequency"),
        )
        bpm_base = int(round(rhythm_analysis.get("global_bpm", 120)))
        log.debug(
            "Базовый BPM: %s (header=%s, estimated=%s)",
            bpm_base,
            rhythm_analysis.get("header_bpm"),
            rhythm_analysis.get("estimated_bpm"),
        )

        # 2. Анализ вокала по секциям
        log.debug("Вызов: self._analyze_sections")
        text_blocks = extract_raw_blocks(raw) # (из text_utils)
        vocal_analysis = self._analyze_sections(text_blocks, preferred_gender)
        
        final_gender_preference = vocal_analysis["final_gender_preference"]
        user_voice_hint = vocal_analysis["user_voice_hint"]
        
        log.debug(f"Статус вокального выбора: {'USER-DEFINED' if user_voice_hint else 'AUTO-DETECT'}")

        # 3. Стиль (Style)
        log.debug("Вызов: self.style.build")
        # Передаем хинт в style.build
        style = self.style.build(emo, tlp, raw, bpm_base, semantic_hints, user_voice_hint)
        log.debug(f"Результат Style: Genre={style['genre']}, Style={style['style']}")

        # 4. Семантические секции (Suno)
        # (Используем BPM из style.build и ключ из style.build)
        log.debug("Вызов: self._build_semantic_layers")
        semantic_layers = self._build_semantic_layers(emo, tlp, style.get('bpm', bpm_base), style.get('key'))
        bpm_adj = semantic_layers["bpm_suggested"]
        semantic_sections = semantic_layers["layers"]["sections"]
        
        # 5. Вокал и Инструменты
        log.debug("Вызов: self.vocals.get")
        vox, inst, vocal_form = self.vocals.get(
            style["genre"],
            final_gender_preference,
            raw,
            [], # (sections больше не нужны, используем vocal_profile_tags)
            vocal_analysis["section_profiles"]
        )
        style["vocal_form"] = vocal_form # Обновляем стиль финальной формой
        style["vocal_count"] = vocal_analysis.get("vocal_count", 1) # (из allocator, если он есть)
        
        log.debug(f"Результат Vocals: Form={vocal_form}, Vox={vox}, Inst={inst}, Count={style['vocal_count']}")

        # 6. Остальные движки
        log.debug("Вызов: self.freq.resonance_profile")
        freq = self.freq.resonance_profile(tlp)
        freq["recommended_octaves"] = self.safety.clamp_octaves(freq["recommended_octaves"])
        
        log.debug("Вызов: self.integrity.analyze")
        integ = self.integrity.analyze(raw)
        
        log.debug("Вызов: self.tone.colors_for_primary")
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))
        
        philosophy = (f"T={tlp.get('truth', 0):.2f}, L={tlp.get('love', 0):.2f}, "
                      f"P={tlp.get('pain', 0):.2f}, CF={tlp.get('conscious_frequency', 0):.2f}")

        # 7. Аннотация (v6 - Suno)
        log.debug("Вызов: self.annotate_text")
        annotated_text_ui, annotated_text_suno = self.annotate_text(
            text_blocks, 
            vocal_analysis["section_profiles"], 
            semantic_sections
        )

        # 8. Финальные Промпты
        log.debug("Вызов: build_suno_prompt (STYLE)")
        prompt_suno_style = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, prompt_variant="suno_style")

        log.debug("Вызов: build_suno_prompt (LYRICS)")
        prompt_suno_lyrics = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, prompt_variant="suno_lyrics")

        log.debug("--- АНАЛИЗ УСПЕШНО ЗАВЕРШЕН ---")

        return {
            "emotions": emo, "tlp": tlp, "bpm": bpm_adj, "frequency": freq,
            "style": style, "vocals": vox, "instruments": inst,
            "vocal_form": vocal_form, "final_gender_preference": final_gender_preference,
            "integrity": integ, "tone_sync": tone,
            "rhythm": rhythm_analysis,

            "annotated_text_ui": annotated_text_ui,     # v6: Для Gradio UI
            "annotated_text_suno": annotated_text_suno, # v6: Для Suno Lyrics
            "prompt_suno_style": prompt_suno_style,   # v6: Для Suno Style
            "prompt_suno_lyrics": prompt_suno_lyrics, # v6: (Legacy)

            "semantic_layers": semantic_layers,
            "version": version,
            "vocal_detection_state": "AUTO-DETECT" if not user_voice_hint else "USER-DEFINED",
        }


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
        semantic_hints: Dict[str, Any] | None = None,
        voice_hint: str | None = None,
    ) -> Dict[str, Any]:
        if not self._core.style:
            raise RuntimeError("Style subsystem is unavailable.")
        return self._core.style.build(emo, tlp, text, bpm, semantic_hints, voice_hint)

    def tone(self, emo: Dict[str, float], tlp: Dict[str, float], key_hint: str | None = None):
        return self._core.tone.colors_for_primary(emo, tlp, key_hint or "auto")

    def rhythm(
        self,
        text: str,
        *,
        emotions: Dict[str, float] | None = None,
        tlp: Dict[str, float] | None = None,
        cf: float | None = None,
        header_bpm: float | None = None,
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
STUDIOCORE_VERSION = "v4.3.11"
log.info(f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section-Aware Duet Mode v2).")