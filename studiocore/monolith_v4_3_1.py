# -*- coding: utf-8 -*-
"""
StudioCore v4.3.11 — Monolith (Section-Aware Duet Mode v2)
v5: f-string syntax error fixed
"""

from __future__ import annotations
import re, json
from statistics import mean
from typing import Dict, Any, List, Tuple
import logging # <-- Импорт логгера

# --- Core imports ---
from .config import load_config
from .text_utils import normalize_text_preserve_symbols, extract_sections
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine 
from .tone import ToneSyncEngine
from .adapter import build_suno_prompt
from .vocals import VocalProfileRegistry
from .style import StyleMatrix  # безопасный импорт (патч или стандарт)

# Получаем логгер для этого модуля
log = logging.getLogger(__name__)

# ==========================================================
# 🗣️ Встроенные детекторы вокала
# ==========================================================

def detect_voice_profile(text: str) -> str | None:
    """
    Автоматически определяет вокальные подсказки из текста.
    """
    log.debug("Вызов функции: detect_voice_profile")
    text_low = text.lower()
    patterns = [
        r"под\s+[а-яa-z\s,]+вокал",
        r"\(.*(вокал|voice|growl|scream).*\)",
        r"(мужск\w+|женск\w+)\s+вокал",
        r"(soft|airy|raspy|grit|growl|scream|whisper)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_low)
        if match:
            hint = match.group(0).strip("() ")
            log.debug(f"Найдено описание вокала: {hint}")
            return hint
    log.debug("Описание вокала не найдено.")
    return None

def detect_gender_from_grammar(text: str) -> str | None:
    """
    Определяет грамматический пол (M/F) по глаголам в прошлом времени после "я".
    """
    log.debug("Вызов функции: detect_gender_from_grammar")
    male_verbs = len(re.findall(r"\bя\s+([а-яё]+л)\b", text, re.I))
    female_verbs = len(re.findall(r"\bя\s+([а-яё]+ла)\b", text, re.I))
    
    log.debug(f"Грамматический анализ: Male хиты={male_verbs}, Female хиты={female_verbs}")
    
    if male_verbs > female_verbs:
        log.debug("Грамматика определена как MALE")
        return "male"
    elif female_verbs > male_verbs:
        log.debug("Грамматика определена как FEMALE")
        return "female"
    
    log.debug("Грамматика не определена (auto)")
    return None

# Глобальная переменная для _AUTO_VOCAL_DETECT
_AUTO_VOCAL_DETECT = True
log.info("🎙️ [Monolith] Auto voice detection активен (detect_voice_profile встроен).")


# ==========================================================
# 🔹 Adaptive Vocal Allocation (без изменений)
# ==========================================================
class AdaptiveVocalAllocator:
    def analyze(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, text: str) -> Dict[str, Any]:
        love, pain, cf, truth = tlp.get("love", 0.0), tlp.get("pain", 0.0), tlp.get("conscious_frequency", 0.0), tlp.get("truth", 0.0)
        word_count = len(re.findall(r"[a-zA-Zа-яА-Яё]+", text))
        avg_line_len = word_count / max(1, len(text.split("\n")))

        if cf > 0.7 and love > pain and word_count > 80:
            form, gender, count = "choir", "mixed", 4
        elif pain >= 0.6 and cf < 0.6:
            form, gender, count = "duet", "female", 2
        elif truth > 0.5 and bpm > 130:
            form, gender, count = "trio", "male", 3
        elif avg_line_len < 6 and love < 0.3 and bpm < 100:
            form, gender, count = "solo", "male", 1
        elif bpm > 150 and love > 0.4:
            form, gender, count = "duet", "mixed", 2
        else:
            form, gender, count = "solo", "auto", 1
        return {"vocal_form": form, "gender": gender, "vocal_count": count}


# ==========================================================
# 🔸 Локальные подсистемы (без изменений)
# ==========================================================
class PatchedLyricMeter:
    vowels = set("aeiouyауоыиэяюёеAEIOUYАУОЫИЭЯЮЁЕ")
    def _syllables(self, line: str) -> int:
        return max(1, sum(1 for ch in line if ch in self.vowels))
    def bpm_from_density(self, text: str, emo: Dict[str, float]) -> int:
        log.debug("Вызов функции: PatchedLyricMeter.bpm_from_density")
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines: return 100
        avg_syll = sum(self._syllables(l) for l in lines) / max(1, len(lines))
        
        pain = emo.get("sadness", 0.0) + emo.get("fear", 0.0)
        energy = emo.get("joy", 0.0) + emo.get("anger", 0.0) + emo.get("epic", 0.0)

        bpm = 130 - (avg_syll * 3)
        bpm -= pain * 30 
        bpm += energy * 25 
        
        bpm_final = int(max(65, min(175, bpm)))
        log.debug(f"Расчет BPM: Cред. слогов={avg_syll:.2f}, Эмо-коррекция (Pain={pain:.2f}, Energy={energy:.2f}), Итог={bpm_final} BPM")
        return bpm_final


class PatchedUniversalFrequencyEngine:
    base = 24.5
    def resonance_profile(self, tlp: Dict[str, float]) -> Dict[str, Any]:
        cf = tlp.get("conscious_frequency", 0.0)
        base_f = self.base * (1.0 + tlp.get("truth", 0.0))
        spread = tlp.get("love", 0.0) * 2000.0
        mod = 1.0 + tlp.get("pain", 0.0) * 0.5
        if cf > 0.7: rec = [4, 5, 6, 7]
        elif cf > 0.3: rec = [2, 3, 4, 5]
        else: rec = [1, 2, 3, 4]
        return {
            "base_frequency": round(base_f, 3),
            "harmonic_range": round(spread, 3),
            "modulation_depth": round(mod, 3),
            "recommended_octaves": rec
        }

class PatchedRNSSafety:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg.get("safety", {
            "safe_octaves": [2, 3, 4, 5], "avoid_freq_bands_hz": [18.0, 30.0],
            "max_peak_db": -1.0, "max_rms_db": -14.0,
            "fade_in_ms": 1000, "fade_out_ms": 1500,
        })
    def clamp_octaves(self, octaves: List[int]) -> List[int]:
        safe = set(self.cfg.get("safe_octaves", [2, 3, 4, 5]))
        arr = [o for o in octaves if o in safe]
        return arr or [2, 3, 4]
    def safety_meta(self) -> Dict[str, Any]:
        return {
            "max_peak_db": self.cfg.get("max_peak_db", -1.0),
            "max_rms_db": self.cfg.get("max_rms_db", -14.0),
            "avoid_freq_bands_hz": self.cfg.get("avoid_freq_bands_hz", []),
            "fade_in_ms": self.cfg.get("fade_in_ms", 1000),
            "fade_out_ms": self.cfg.get("fade_out_ms", 1500),
        }

class PatchedIntegrityScanEngine:
    def analyze(self, text: str) -> Dict[str, Any]:
        words = re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text.lower())
        sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        lexical_div = len(set(words)) / max(1, len(words))
        avg_sent_len = len(words) / max(1, len(sents))
        reflection = len([w for w in words if w in ("я","i","me","my","меня","сам")]) / max(1, len(words))
        vib_coh = round((1 - abs(avg_sent_len - 14) / 14 + 1 - abs(lexical_div - 0.5) / 0.5) / 2, 3)
        return {
            "form": {"word_count": len(words), "avg_sentence_len": round(avg_sent_len, 2),
                     "lexical_diversity": round(lexical_div, 2)},
            "reflection": {"self_awareness_density": round(reflection, 2)},
            "vibrational_coherence": vib_coh, "flags": []
        }


# ==========================================================
# 🎶 StudioCore Monolith v4.3.11
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

        try:
            log.debug("Загрузка: PatchedStyleMatrix")
            from .style import PatchedStyleMatrix
            self.style = PatchedStyleMatrix()
            log.info("🎨 [StyleMatrix] Используется патчированная версия (PatchedStyleMatrix).")
        except ImportError:
            log.debug("Загрузка: StyleMatrix (стандартная)")
            self.style = StyleMatrix()
            log.info("🎨 [StyleMatrix] Используется стандартная версия (StyleMatrix).")

        log.debug("Загрузка: ToneSyncEngine")
        self.tone = ToneSyncEngine()
        log.debug("Загрузка: AdaptiveVocalAllocator")
        self.vocal_allocator = AdaptiveVocalAllocator()
        log.info(f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section-Aware Duet Mode v2).")

    # -------------------------------------------------------
    # v4.3 - АНАЛИЗАТОР СЕКЦИЙ (ДЛЯ ДУЭТОВ)
    # -------------------------------------------------------
    def _analyze_sections(self, text: str) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Разбивает текст на блоки и анализирует КАЖДЫЙ блок на 
        грамматический пол (M/F/Mixed/Auto) и хинты.
        Возвращает: (список блоков с тегами, общий итог по вокалу)
        """
        log.debug("Вызов функции: _analyze_sections")
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
        if not blocks:
            log.warning("Текст не содержит блоков, используется raw-анализ.")
            blocks = [text.strip()]

        tagged_blocks = []
        vocal_profile_tags = {"male": 0, "female": 0, "mixed": 0, "auto": 0}

        for block_text in blocks:
            # 1. Грамматика
            gender = detect_gender_from_grammar(block_text)
            
            # 2. Прямые хинты
            hint = detect_voice_profile(block_text)
            
            # 3. Намеки на дуэт/группу
            if any(k in block_text.lower() for k in ["мы", "we", "вместе", "duet", "choir"]):
                gender = "mixed"
            
            # Если ничего не найдено
            if not gender:
                gender = "auto"
                
            vocal_profile_tags[gender] += 1
            tagged_blocks.append({"text": block_text, "gender": gender, "hint": hint})
            
            # === ИСПРАВЛЕНИЕ ОШИБКИ v5 (f-string) ===
            # Было: log.debug(f"Блок [{block_text[:20]...}] -> Пол: {gender}, Хинт: {hint}")
            log.debug(f"Блок [{block_text[:20]}...] -> Пол: {gender}, Хинт: {hint}")
            # === Конец исправления ===

        log.debug(f"Итог по вокалу (все блоки): {vocal_profile_tags}")
        return tagged_blocks, vocal_profile_tags

    # -------------------------------------------------------
    # v4.3 - СЕМАНТИЧЕСКАЯ РАЗМЕТКА СЕКЦИЙ (OVERLAY)
    # -------------------------------------------------------
    def _build_semantic_sections(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, 
                                 tagged_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Создает семантическую структуру (Intro, Verse...) и НАКЛАДЫВАЕТ 
        ее на физические блоки текста, включая теги M/F/Mixed.
        """
        log.debug("Вызов функции: _build_semantic_sections")
        love, pain, truth = tlp.get("love",0), tlp.get("pain",0), tlp.get("truth",0)
        cf = tlp.get("conscious_frequency",0)
        avg_emo = mean(abs(v) for v in emo.values()) if emo else 0.0
        
        intro = {"section":"Intro","mood":"mystic" if cf>=0.5 else "calm","intensity":round(bpm*0.8,2),"focus":"tone_establish"}
        verse = {"section":"Verse","mood":"reflective" if truth > love else "narrative","intensity":round(bpm,2),"focus":"story_flow"}
        bridge= {"section":"Bridge","mood":"dramatic" if pain>0.3 else "dreamlike","intensity":round(bpm*(1.05+avg_emo/4),2),"focus":"contrast"}
        chorus= {"section":"Chorus","mood":"uplifting" if (love>=pain and love > 0.05) else "tense","intensity":round(bpm*1.15,2),"focus":"release"}
        outro = {"section":"Outro","mood":"peaceful" if cf>0.6 else "fading","intensity":round(bpm*0.7,2),"focus":"closure"}
        
        available_sections = [intro, verse, bridge, chorus]
        
        num_blocks = len(tagged_blocks)
        final_sections = []
        
        if num_blocks == 1:
            final_sections = [verse]
        elif num_blocks == 2:
            final_sections = [verse, chorus]
        elif num_blocks == 3:
            final_sections = [verse, bridge, chorus]
        elif num_blocks == 4:
            final_sections = [verse, chorus, verse, chorus]
        elif num_blocks == 5:
            final_sections = [intro, verse, bridge, chorus, outro]
        else:
            log.debug(f"Назначение {num_blocks} блоков на {len(available_sections)} секций...")
            for i in range(num_blocks):
                if i == num_blocks - 1:
                    final_sections.append(outro)
                elif i == 0:
                    final_sections.append(intro)
                else:
                    sec_index = (i - 1) % (len(available_sections) - 1) 
                    final_sections.append(available_sections[sec_index + 1]) 


        final_overlay_sections = []
        for i, block in enumerate(tagged_blocks):
            sec_data = final_sections[i].copy()
            sec_data["vocal"] = block.get("gender", "auto").upper()
            sec_data["hint"] = block.get("hint")
            final_overlay_sections.append(sec_data)

        bpm_adj = int(bpm + (avg_emo*8) + (cf*4))
        bpm_final = max(65, min(175, bpm_adj))
        log.debug(f"BPM скорректирован до {bpm_final}")

        return {
            "bpm_suggested": bpm_final,
            "overlay": {
                "depth": round((truth+pain)/2,2),
                "warmth": round(love,2),
                "clarity": round(cf,2),
                "sections": final_overlay_sections 
            }
        }

    # -------------------------------------------------------
    # v4.3 - АННОТАТОР (ТЕПЕРЬ ИСПОЛЬЗУЕТ OVERLAY)
    # -------------------------------------------------------
    def annotate_text(self, text: str, overlay: Dict[str, Any], style: Dict[str, Any],
                      vocals: List[str], bpm: int, emotions=None, tlp=None) -> str:
        
        log.debug("Вызов функции: annotate_text")
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
        if not blocks:
            blocks = [text.strip()]
            
        sections = overlay.get("sections", [])
        annotated_blocks = []

        if len(blocks) != len(sections):
            log.warning(f"Ошибка аннотации: кол-во блоков ({len(blocks)}) не совпадает с кол-вом секций ({len(sections)})!")
            annotated_blocks.append(f"[Full Text – BPM≈{bpm}, VocalForm={style.get('vocal_form', 'auto')}]")
            annotated_blocks.append(text)
        else:
            for i, block in enumerate(blocks):
                sec = sections[i]
                vocal_tag = sec.get('vocal', 'AUTO')
                header = (
                    f"[{sec.get('section','Block').upper()} - {vocal_tag} - "
                    f"{sec.get('mood','neutral')}, "
                    f"focus={sec.get('focus','flow')}, "
                    f"intensity≈{sec.get('intensity',bpm)}]"
                )
                annotated_blocks.append(header)
                annotated_blocks.append(block)
                annotated_blocks.append("") 

        vocal_form = style.get("vocal_form", "auto")
        tone_key = style.get("key", "auto")
        tech = ", ".join(sorted(list(set(v for v in vocals if v not in [
            "male","female","duet","trio","quartet","quintet","choir","solo"
        ])))) or "neutral tone"
        
        annotated_blocks.append(f"[End – BPM≈{bpm}, VocalForm={vocal_form}, Tone={tone_key}]")
        annotated_blocks.append(f"[Vocal Techniques: {tech}]")
        return "\n".join(annotated_blocks).strip()

    # -------------------------------------------------------
    # 🚀 ГЛАВНЫЙ ПАЙПЛАЙН АНАЛИЗА (v4.3)
    # -------------------------------------------------------
    def analyze(self, text: str, author_style=None, preferred_gender="auto", version=None,
                overlay: Dict[str, Any] | None = None) -> Dict[str, Any]:
        
        log.debug(f"--- ЗАПУСК АНАЛИЗА (v4.3.11) ---")
        log.debug(f"Preferred Gender: {preferred_gender}, Text: {text[:50]}...")
        
        version = version or self.cfg.get("suno_version", "v5")
        
        log.debug("Вызов: normalize_text_preserve_symbols")
        raw = normalize_text_preserve_symbols(text)
        
        log.debug("Вызов: self.emotion.analyze")
        emo = self.emotion.analyze(raw)
        log.debug(f"Результат EMO: {emo}")
        
        log.debug("Вызов: self.tlp.analyze")
        tlp = self.tlp.analyze(raw)
        log.debug(f"Результат TLP: {tlp}")

        log.debug("Вызов: self.rhythm.bpm_from_density")
        bpm = self.rhythm.bpm_from_density(raw, emo)
        log.debug(f"Базовый BPM: {bpm}")

        log.debug("Вызов: self._analyze_sections")
        tagged_blocks, vocal_profile_tags = self._analyze_sections(raw)

        log.debug("Вызов: self._build_semantic_sections")
        overlay_pack = self._build_semantic_sections(emo, tlp, bpm, tagged_blocks)
        bpm_adj = overlay_pack["bpm_suggested"] 
        semantic_overlay = overlay_pack["overlay"] 
        log.debug(f"Финальный BPM: {bpm_adj}")

        user_voice_hint = overlay.get("voice_profile_hint") if overlay else None
        
        if not user_voice_hint:
             block_hints = [b.get("hint") for b in tagged_blocks if b.get("hint")]
             if block_hints:
                 user_voice_hint = block_hints[0]
                 log.debug(f"Используем вокальный хинт из блока: {user_voice_hint}")

        mode = "USER-MODE" if user_voice_hint else "AUTO-DETECT"
        log.debug(f"Режим вокала: {mode}")

        log.debug("Вызов: self.style.build")
        style = self.style.build(emo, tlp, raw, bpm_adj, semantic_overlay, user_voice_hint)
        log.debug(f"Результат Style: Genre={style.get('genre')}, Style={style.get('style')}")

        log.debug("Вызов: self.vocals.get")
        vox, inst, vocal_form = self.vocals.get(
            style["genre"], 
            preferred_gender, 
            raw, 
            tagged_blocks, 
            vocal_profile_tags 
        )
        style["vocal_form"] = vocal_form 
        style["vocal_count"] = (
            vocal_profile_tags.get("male", 0) + 
            vocal_profile_tags.get("female", 0) +
            vocal_profile_tags.get("mixed", 0) * 2
        )
        if style["vocal_count"] == 0: style["vocal_count"] = 1 
        
        log.debug(f"Результат Vocals: Form={vocal_form}, Vox={vox}, Inst={inst}, Count={style['vocal_count']}")

        log.debug("Вызов: self.freq.resonance_profile")
        freq = self.freq.resonance_profile(tlp)
        freq["recommended_octaves"] = self.safety.clamp_octaves(freq["recommended_octaves"])

        log.debug("Вызов: self.integrity.analyze")
        integ = self.integrity.analyze(raw)
        
        log.debug("Вызов: self.tone.colors_for_primary")
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))

        philosophy = (f"Truth={tlp.get('truth', 0):.2f}, Love={tlp.get('love', 0):.2f}, "
                      f"Pain={tlp.get('pain', 0):.2f}, CF={tlp.get('conscious_frequency', 0):.2f}")

        log.debug("Вызов: self.annotate_text")
        annotated_text = self.annotate_text(raw, semantic_overlay, style, vox, bpm_adj, emo, tlp)

        log.debug("Вызов: build_suno_prompt (STYLE)")
        prompt_suno_style = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno_style")
        
        log.debug("Вызов: build_suno_prompt (LYRICS)")
        prompt_suno_lyrics = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno_lyrics")

        log.debug("--- АНАЛИЗ УСПЕШНО ЗАВЕРШЕН ---")
        
        return {
            "emotions": emo, "tlp": tlp, "bpm": bpm_adj, "frequency": freq,
            "style": style, "vocals": vox, "instruments": inst,
            "vocal_form": vocal_form, "integrity": integ, "tone_sync": tone,
            "semantic_overlay": semantic_overlay,
            "prompt_suno_style": prompt_suno_style,
            "prompt_suno_lyrics": prompt_suno_lyrics,
            "annotated_text": annotated_text,
            "preferred_gender": preferred_gender,
            "version": version, "mode": mode
        }

# ==========================================================
STUDIOCORE_VERSION = "v4.3.11"
log.info(f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section-Aware Duet Mode v2).")