# -*- coding: utf-8 -*-
"""
StudioCore v4.3.5 — Monolith (Adaptive Vocal Allocation Patch)
Динамическая куплетная аннотация, адаптивный жанр, безопасные частоты,
автоматическое распределение вокалистов.
"""

from __future__ import annotations
import re
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Any, List, Tuple

# --- Core imports ---
from .config import load_config
from .text_utils import normalize_text_preserve_symbols, extract_sections
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from .tone import ToneSyncEngine
from .adapter import build_suno_prompt
from .vocals import VocalProfileRegistry


# ================================
# 🔹 Adaptive Vocal Allocation
# ================================

class AdaptiveVocalAllocator:
    """
    Анализирует текст, эмоции и BPM, чтобы определить оптимальную форму вокала:
    solo / duet / trio / choir, а также гендер и количество певцов.
    """
    def analyze(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int, text: str) -> Dict[str, Any]:
        love = tlp.get("love", 0.0)
        pain = tlp.get("pain", 0.0)
        cf = tlp.get("conscious_frequency", 0.0)
        truth = tlp.get("truth", 0.0)
        word_count = len(re.findall(r"[a-zA-Zа-яА-ЯёЁ]+", text))
        avg_line_len = word_count / max(1, len(text.split("\n")))

        # --- логика распределения ---
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

        return {
            "vocal_form": form,
            "gender": gender,
            "vocal_count": count
        }


# ================================
# Patched subsystems
# ================================

class PatchedLyricMeter:
    vowels = set("aeiouyауоыиэяюёеAEIOUYАУОЫИЭЯЮЁЕ")

    def _syllables(self, line: str) -> int:
        return max(1, sum(1 for ch in line if ch in self.vowels))

    def bpm_from_density(self, text: str) -> int:
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines:
            return 100
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
        self.cfg = cfg.get("safety", {
            "safe_octaves": [2, 3, 4, 5],
            "avoid_freq_bands_hz": [18.0, 30.0],
            "max_peak_db": -1.0,
            "max_rms_db": -14.0,
            "fade_in_ms": 1000,
            "fade_out_ms": 1500,
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
        reflection = len([w for w in words if w in ("я", "i", "me", "my", "меня", "сам")]) / max(1, len(words))
        vib_coh = round((1 - abs(avg_sent_len - 14) / 14 + 1 - abs(lexical_div - 0.5) / 0.5) / 2, 3)
        return {
            "form": {"word_count": len(words), "avg_sentence_len": round(avg_sent_len, 2),
                     "lexical_diversity": round(lexical_div, 2)},
            "reflection": {"self_awareness_density": round(reflection, 2)},
            "vibrational_coherence": vib_coh,
            "flags": []
        }


# ================================
# StudioCore
# ================================

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
        self.style = PatchedStyleMatrix()
        self.tone = ToneSyncEngine()
        self.vocal_allocator = AdaptiveVocalAllocator()  # новый модуль

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

    def annotate_text(self, text: str, overlay: Dict[str, Any], style: Dict[str, Any],
                      vocals: List[str], bpm: int, emotions=None, tlp=None) -> str:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
        sections = overlay.get("sections", [])
        annotated_blocks = []
        for i, block in enumerate(blocks):
            sec = sections[i % len(sections)] if sections else {}
            header = f"[{sec.get('section','Block')} – {sec.get('mood','neutral')}, focus={sec.get('focus','flow')}, intensity≈{sec.get('intensity',bpm)}]"
            annotated_blocks.append(header)
            annotated_blocks.append(block)
            annotated_blocks.append("")
        vocal_form = style.get("vocal_form", "auto")
        tone_key = style.get("key", "auto")
        tech = ", ".join([v for v in vocals if v not in ["male", "female"]]) or "neutral tone"
        annotated_blocks.append(f"[End – BPM≈{bpm}, Vocal={vocal_form}, Tone={tone_key}]")
        annotated_blocks.append(f"[Vocal Techniques: {tech}]")
        return "\n".join(annotated_blocks).strip()

    def analyze(self, text: str, author_style=None, preferred_gender=None, version=None) -> Dict[str, Any]:
        version = version or self.cfg.get("suno_version", "v5")
        raw = normalize_text_preserve_symbols(text)
        sections = extract_sections(raw)
        emo = self.emotion.analyze(raw)
        tlp = self.tlp.analyze(raw)
        bpm = self.rhythm.bpm_from_density(raw)
        freq = self.freq.resonance_profile(tlp)
        overlay_pack = self._build_semantic_sections(emo, tlp, bpm)
        bpm_adj = overlay_pack["bpm"]

        # 🔹 Новый шаг — анализ вокала
        vocal_meta = self.vocal_allocator.analyze(emo, tlp, bpm_adj, raw)
        preferred_gender = vocal_meta["gender"]

        style = self.style.build(emo, tlp, raw, bpm_adj)
        vox, inst, vocal_form = self.vocals.get(style["genre"], preferred_gender, raw, sections)
        style["vocal_form"] = vocal_meta["vocal_form"]
        style["vocal_count"] = vocal_meta["vocal_count"]

        print(f"🎧 [StudioCore] Analyze: Gender={preferred_gender} | Form={vocal_meta['vocal_form']} | Genre={style['genre']} | BPM={bpm_adj}")

        integ = self.integrity.analyze(raw)
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))
        philosophy = (f"Truth={tlp.get('truth', 0):.2f}, Love={tlp.get('love', 0):.2f}, "
                      f"Pain={tlp.get('pain', 0):.2f}, CF={tlp.get('conscious_frequency', 0):.2f}")
        prompt_full = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno")
        annotated_text = self.annotate_text(raw, overlay_pack["overlay"], style, vox, bpm_adj, emo, tlp)

        return {
            "emotions": emo, "tlp": tlp, "bpm": bpm_adj, "frequency": freq, "style": style,
            "vocals": vox, "instruments": inst, "prompt_full": prompt_full, "prompt_suno": prompt_suno,
            "annotated_text": annotated_text, "preferred_gender": preferred_gender, "version": version
        }


# ==========================================================
# ✅ Auto-Register Patch
# ==========================================================
STUDIOCORE_VERSION = "v4.3.5"
try:
    from inspect import isclass
    if "StudioCore" not in globals():
        for name, obj in globals().items():
            if isclass(obj) and name == "StudioCore":
                globals()["StudioCore"] = obj
                print(f"🔹 [StudioCore {STUDIOCORE_VERSION}] Auto-registered successfully.")
                break
        else:
            print("⚠️ [StudioCore] Class not found during auto-registration.")
    else:
        print("🔹 [StudioCore] Already registered in globals().")
except Exception as e:
    print(f"⚠️ [StudioCore Auto-Register Error] {e}")
