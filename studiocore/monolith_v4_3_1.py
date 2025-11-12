# -*- coding: utf-8 -*-
"""
StudioCore v4.3.11 — Monolith (Duet & Section-Aware)
ИСПРАВЛЕНИЕ v4: Исправлена ошибка 'NameError: _AUTO_VOCAL_DETECT'
"""

from __future__ import annotations
import re, json
from statistics import mean
from typing import Dict, Any, List, Tuple

# --- Core imports ---
from .config import load_config
from .text_utils import normalize_text_preserve_symbols, extract_sections
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from .tone import ToneSyncEngine
from .adapter import build_suno_prompt
from .vocals import VocalProfileRegistry
from .style import StyleMatrix  # безопасный импорт (патч или стандарт)

# ==========================================================
# 🗣️ Движок определения вокала (Перемещено из style.py)
# ==========================================================

def detect_voice_profile(text: str) -> str | None:
    """
    Автоматически определяет вокальные подсказки (например, "(growl)")
    """
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
            print(f"🎙️ [AutoDetect] Найдена вокальная подсказка: {hint}")
            return hint
    return None

def detect_gender_from_grammar(text: str) -> str | None:
    """
    Анализирует текст на грамматические признаки (я шел / я шла)
    """
    matches = re.findall(r"\b(я)\s+([а-яё]+)\b", text.lower())
    if not matches:
        return None

    male_verbs = 0
    female_verbs = 0
    for _, verb in matches:
        if verb.endswith("л") and not verb.endswith("ла"):
            male_verbs += 1
        elif verb.endswith("ла"):
            female_verbs += 1

    if male_verbs > female_verbs:
        return "male"
    if female_verbs > male_verbs:
        return "female"
    return None

# --- !! ВОТ ИСПРАВЛЕНИЕ !! ---
# Определяем _AUTO_VOCAL_DETECT, так как он используется в analyze()
_AUTO_VOCAL_DETECT = True
print("🎙️ [Monolith] Auto voice detection активен (detect_voice_profile встроен).")
# --- !! КОНЕЦ ИСПРАВЛЕНИЯ !! ---


# ==========================================================
# 🔹 Adaptive Vocal Allocation (Fallback)
# ==========================================================
class AdaptiveVocalAllocator:
    """ 
    Определяет *предполагаемую* форму вокала, если грамматика 
    или подсказки не найдены.
    """
    def analyze(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, text: str) -> Dict[str, Any]:
        love, pain, cf, truth = tlp.get("love", 0.0), tlp.get("pain", 0.0), tlp.get("conscious_frequency", 0.0), tlp.get("truth", 0.0)
        word_count = len(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text))
        avg_line_len = word_count / max(1, len(text.split("\n")))

        if cf > 0.7 and love > pain and word_count > 80:
            form, gender, count = "choir", "mixed", 4
        elif pain >= 0.6 and cf < 0.6:
            form, gender, count = "duet_f", "female", 2 # Изменено на duet_f
        elif truth > 0.5 and bpm > 130:
            form, gender, count = "trio_m", "male", 3 # Изменено на trio_m
        elif avg_line_len < 6 and love < 0.3 and bpm < 100:
            form, gender, count = "solo_m", "male", 1
        elif bpm > 150 and love > 0.4:
            form, gender, count = "duet_mixed", "mixed", 2
        else:
            form, gender, count = "solo_auto", "auto", 1
        return {"vocal_form": form, "gender": gender, "vocal_count": count}


# ==========================================================
# 🔸 Локальные подсистемы (без изменений)
# ==========================================================
class PatchedLyricMeter:
    vowels = set("aeiouyауоыиэяюёеAEIOUYАУОЫИЭЯЮЁЕ")
    def _syllables(self, line: str) -> int:
        return max(1, sum(1 for ch in line if ch in self.vowels))
    def bpm_from_density(self, text: str) -> int:
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines: return 100
        avg_syll = sum(self._syllables(l) for l in lines) / max(1, len(lines))
        bpm = 140 - min(60, (avg_syll - 8) * 6)
        punct_boost = sum(ch in ",.!?…" for ch in text) * 0.5
        bpm = bpm + min(20, punct_boost)
        return int(max(60, min(180, bpm)))

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
        self.cfg = cfg.get("safety", {})
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
            "vibrational_coherence": vib_coh,
            "flags": []
        }

# ==========================================================
# StudioCore (Переработанный)
# ==========================================================
class StudioCore:
    def __init__(self, config_path: str | None = None):
        self.cfg = load_config(config_path or "studio_config.json")
        self.emotion = AutoEmotionalAnalyzer()
        self.tlp = TruthLovePainEngine()
        self.rhythm = PatchedLyricMeter()
        self.freq = PatchedUniversalFrequencyEngine()
        self.safety = PatchedRNSSafety(self.cfg)
        self.integrity = PatchedIntegrityScanEngine()
        self.vocals = VocalProfileRegistry()
        self.style = StyleMatrix() # Использует StyleMatrix (или Patched, если импортирован)
        self.tone = ToneSyncEngine()
        self.vocal_allocator = AdaptiveVocalAllocator() # Fallback

    # -------------------------------------------------------
    def _build_semantic_sections(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int) -> Dict[str, Any]:
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0.0)
        avg_emo = mean(abs(v) for v in emo.values()) if emo else 0.0
        intro = {"section": "Intro", "mood": "mystic" if cf >= 0.5 else "calm", "intensity": round(bpm * 0.8, 2), "focus": "tone_establish"}
        verse = {"section": "Verse", "mood": "reflective" if truth > love else "narrative", "intensity": round(bpm, 2), "focus": "story_flow"}
        bridge = {"section": "Bridge", "mood": "dramatic" if pain > 0.3 else "dreamlike", "intensity": round(bpm * (1.05 + avg_emo / 4), 2), "focus": "contrast"}
        chorus = {"section": "Chorus", "mood": "uplifting" if love >= pain else "tense", "intensity": round(bpm * 1.15, 2), "focus": "release"}
        outro = {"section": "Outro", "mood": "peaceful" if cf > 0.6 else "fading", "intensity": round(bpm * 0.7, 2), "focus": "closure"}
        bpm_adj = int(bpm + (avg_emo * 8) + (cf * 4))
        overlay = {"depth": round((truth + pain) / 2, 2), "warmth": round(love, 2), "clarity": round(cf, 2),
                   "sections": [intro, verse, bridge, chorus, outro]}
        return {"bpm": bpm_adj, "overlay": overlay}

    # -------------------------------------------------------
    # ИЗМЕНЕНО: Принимает 'block_genders'
    def annotate_text(self, text: str, overlay: Dict[str, Any], style: Dict[str, Any],
                      vocals: List[str], bpm: int, 
                      block_genders: List[str], # <-- НОВЫЙ ПАРАМЕТР
                      emotions=None, tlp=None) -> str:
        
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
        sections = overlay.get("sections", [])
        annotated_blocks = []

        # ИЗМЕНЕНО: Умная аннотация с полом
        for i, block in enumerate(blocks):
            # 1. Структура (Intro, Verse...)
            sec = sections[i % len(sections)] if sections else {}
            sec_name = sec.get('section', 'Block')
            sec_mood = sec.get('mood', 'neutral')
            sec_intensity = sec.get('intensity', bpm)

            # 2. Пол (MALE, FEMALE, MIXED)
            block_gender = block_genders[i] if i < len(block_genders) else "auto"
            if block_gender == "male":
                gender_tag = "MALE"
            elif block_gender == "female":
                gender_tag = "FEMALE"
            elif block_gender == "mixed":
                gender_tag = "MIXED"
            else:
                gender_tag = "AUTO" # (Использует основной вокал)

            header = f"[{sec_name} – {gender_tag} – {sec_mood}, intensity≈{sec_intensity}]"
            annotated_blocks.append(header)
            annotated_blocks.append(block)
            annotated_blocks.append("")

        vocal_form = style.get("vocal_form", "auto")
        tone_key = style.get("key", "auto")
        tech = ", ".join([v for v in vocals if v not in ["male","female"]]) or "neutral tone"
        annotated_blocks.append(f"[End – BPM≈{bpm}, Vocal={vocal_form}, Tone={tone_key}]")
        annotated_blocks.append(f"[Vocal Techniques: {tech}]")
        return "\n".join(annotated_blocks).strip()

    # -------------------------------------------------------
    # ИЗМЕНЕНО: Логика 'analyze' полностью переработана
    def analyze(self, text: str, author_style=None, preferred_gender=None, version=None,
                overlay: Dict[str, Any] | None = None) -> Dict[str, Any]:
        
        version = version or self.cfg.get("suno_version", "v5")
        raw = normalize_text_preserve_symbols(text)
        sections = extract_sections(raw) # (Это [Verse], [Chorus]... не используется)
        
        # 1. Сначала полный анализ TLP/BPM/Style для всей песни
        emo = self.emotion.analyze(raw)
        tlp = self.tlp.analyze(raw)
        bpm = self.rhythm.bpm_from_density(raw)
        freq = self.freq.resonance_profile(tlp)
        overlay_pack = self._build_semantic_sections(emo, tlp, bpm)
        bpm_adj = overlay_pack["bpm"]

        # 2. НОВИНКА: По-блочный анализ вокала
        blocks = [b.strip() for b in re.split(r"\n\s*\n", raw.strip()) if b.strip()]
        block_genders = [] # Список полов: ['male', 'female', 'mixed', ...]
        has_male = False
        has_female = False
        
        # 'user_voice_hint' из overlay (Gradio)
        user_voice_hint = overlay.get("voice_profile_hint") if overlay else None

        for block_text in blocks:
            gender = "auto"
            
            # Приоритет 1: Прямая подсказка из Gradio (если есть)
            if user_voice_hint:
                if any(k in user_voice_hint for k in ["female", "женск"]): gender = "female"
                elif any(k in user_voice_hint for k in ["male", "мужск"]): gender = "male"

            # Приоритет 2: Грамматика ("я шел" / "я шла")
            if gender == "auto":
                grammatical_gender = detect_gender_from_grammar(block_text)
                if grammatical_gender:
                    gender = grammatical_gender
            
            # Приоритет 3: Подсказки в тексте ("(female vocal)")
            if gender == "auto":
                text_hint = detect_voice_profile(block_text)
                if text_hint:
                    if any(k in text_hint for k in ["female", "женск"]): gender = "female"
                    elif any(k in text_hint for k in ["male", "мужск"]): gender = "male"
            
            block_genders.append(gender)
            if gender == "male": has_male = True
            if gender == "female": has_female = True

        # 3. Определение финальной формы вокала
        final_vocal_form = "solo_auto"
        dominant_gender = "auto"

        if has_male and has_female:
            final_vocal_form = "duet_mf" # MALE/FEMALE DUET
            dominant_gender = "mixed"
        elif has_male:
            final_vocal_form = "solo_m"
            dominant_gender = "male"
        elif has_female:
            final_vocal_form = "solo_f"
            dominant_gender = "female"
        else:
            # Если не найдено ни 'male', ни 'female', используем TLP-fallback
            vocal_meta_fallback = self.vocal_allocator.analyze(emo, tlp, bpm_adj, raw)
            final_vocal_form = vocal_meta_fallback.get("vocal_form", "solo_auto")
            dominant_gender = vocal_meta_fallback.get("gender", "auto")
            
        # 4. Уважение к выбору пользователя в UI
        # Если пользователь выбрал "female" в Gradio, он отменяет всё.
        if preferred_gender and preferred_gender != "auto":
            gender_final = preferred_gender
            # И также отменяем по-блочный анализ
            block_genders = [preferred_gender] * len(blocks)
            if preferred_gender == "male": final_vocal_form = "solo_m"
            elif preferred_gender == "female": final_vocal_form = "solo_f"
        else:
            gender_final = dominant_gender

        # 5. Получаем Стиль и Вокал
        
        # Передаем подсказку в Style. (Style не должен решать пол, но может учесть growl)
        vocal_hint_for_style = user_voice_hint or (detect_voice_profile(raw) if _AUTO_VOCAL_DETECT else None)
        if vocal_hint_for_style:
             overlay_pack["overlay"]["voice_profile_hint"] = vocal_hint_for_style

        style = self.style.build(emo, tlp, raw, bpm_adj, overlay_pack["overlay"])

        vox, inst, vocal_form_from_registry = self.vocals.get(
            style["genre"], gender_final, raw, sections
        )
        
        # 6. Финализация
        # Принудительно устанавливаем нашу обнаруженную форму дуэта
        style["vocal_form"] = final_vocal_form 
        style["vocal_count"] = 2 if "duet" in final_vocal_form else 1 # Упрощение

        mode = "AUTO-DETECT (Duet)" if "duet_mf" in final_vocal_form else "AUTO-DETECT"

        print(f"🎧 [StudioCore] Analyze [{mode}]: Gender={gender_final} | Form={final_vocal_form} | Genre={style['genre']} | BPM={bpm_adj}")

        integ = self.integrity.analyze(raw)
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))
        philosophy = (f"Truth={tlp.get('truth', 0):.2f}, Love={tlp.get('love', 0):.2f}, "
                      f"Pain={tlp.get('pain', 0):.2f}, CF={tlp.get('conscious_frequency', 0):.2f}")

        prompt_full = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno")
        
        # Вызываем обновленный аннотатор
        annotated_text = self.annotate_text(raw, overlay_pack["overlay"], style, vox, bpm_adj, 
                                            block_genders, # <-- Передаем профиль полов
                                            emo, tlp)

        return {
            "emotions": emo, "tlp": tlp, "bpm": bpm_adj, "frequency": freq,
            "style": style, "vocals": vox, "instruments": inst,
            "prompt_full": prompt_full, "prompt_suno": prompt_suno,
            "annotated_text": annotated_text, "preferred_gender": gender_final,
            "version": version, "mode": mode,
            "vocal_profile_blocks": block_genders # Для дебага
        }


# ==========================================================
STUDIOCORE_VERSION = "v4.3.11"
print(f"🔹 [StudioCore {STUDIOCORE_VERSION}] Monolith loaded (Section-Aware Duet Mode v2).")