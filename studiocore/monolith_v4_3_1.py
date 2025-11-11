# -*- coding: utf-8 -*-
"""
StudioCore v4.3.2 — Monolith (Patched for v5.2)
Совместимость с app.py (gender adaptive)
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
        if cf > 0.7:
            rec = [4, 5, 6, 7]
        elif cf > 0.3:
            rec = [2, 3, 4, 5]
        else:
            rec = [1, 2, 3, 4]
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
        vib_coh = round(
            (1 - abs(avg_sent_len - 14) / 14 + 1 - abs(lexical_div - 0.5) / 0.5) / 2, 3
        )
        return {
            "form": {
                "word_count": len(words),
                "avg_sentence_len": round(avg_sent_len, 2),
                "lexical_diversity": round(lexical_div, 2)
            },
            "reflection": {"self_awareness_density": round(reflection, 2)},
            "vibrational_coherence": vib_coh,
            "flags": []
        }


# ================================
# Patched StyleMatrix
# ================================

class PatchedStyleMatrix:
    def _tone_profile(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        dominant = max(emo, key=emo.get)
        cf = tlp.get("conscious_frequency", 0.0)
        if dominant in ("joy", "peace") and cf > 0.3:
            return "majestic major"
        elif dominant in ("sadness", "pain") or tlp.get("pain", 0) > 0.3:
            return "melancholic minor"
        elif dominant in ("anger", "epic") and cf > 0.5:
            return "dramatic harmonic minor"
        else:
            return "neutral modal"

    def _derive_genre(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        word_count = len(re.findall(r"\b\w+\b", text))
        sentences = [s for s in re.split(r"[.!?]", text) if s.strip()]
        avg_sent_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        density = min(word_count / 100.0, 10)
        emotional_range = (tlp.get("love", 0) + tlp.get("pain", 0) + tlp.get("truth", 0)) / 3

        if emotional_range > 0.7 and density < 2:
            base = "orchestral poetic"
        elif density > 6 and tlp.get("pain", 0) > 0.4:
            base = "dark rhythmic"
        elif density > 5 and tlp.get("love", 0) > 0.4:
            base = "dynamic emotional"
        elif avg_sent_len > 12:
            base = "cinematic narrative"
        else:
            base = "lyrical adaptive"

        dominant = max(emo, key=emo.get)
        if dominant == "anger":
            mood = "dramatic"
        elif dominant == "fear":
            mood = "mystic"
        elif dominant == "joy":
            mood = "uplifting"
        elif dominant == "sadness":
            mood = "melancholic"
        elif dominant == "epic":
            mood = "heroic"
        else:
            mood = "reflective"

        return f"{base} {mood}".strip()

    def _derive_key(self, tlp: Dict[str, float], bpm: int) -> str:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        if p > 0.45:
            mode = "minor"
        elif l > 0.55:
            mode = "major"
        else:
            mode = "modal"
        if t > 0.6 and l > 0.5:
            key = "E"
        elif l > 0.7:
            key = "G"
        elif p > 0.6:
            key = "A"
        elif t < 0.3 and l > 0.4:
            key = "D"
        elif p > 0.5 and l < 0.3:
            key = "F"
        elif bpm > 140 and l > 0.5:
            key = "C"
        else:
            key = "C#"
        return f"{key} {mode}"

    def build(self, emo: Dict[str, float], tlp: Dict[str, float], text: str, bpm: int) -> Dict[str, Any]:
        descr = self._derive_genre(text, emo, tlp)
        valid_genres = {"rock", "pop", "folk", "electronic", "ambient", "cinematic", "orchestral", "hip hop", "rap"}
        genre = next((g for g in valid_genres if g in descr), "rock")
        return {
            "genre": genre,
            "style": self._tone_profile(emo, tlp),
            "key": self._derive_key(tlp, bpm),
            "structure": "intro-verse-chorus-outro",
            "style_descr_full": descr,
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
        style = self.style.build(emo, tlp, raw, bpm_adj)

        vox, inst, vocal_form = self.vocals.get(style["genre"], preferred_gender or "auto", raw, sections)
        style["vocal_form"] = vocal_form

        # --- лог для Hugging Face / Gradio ---
        print(f"🎧 [StudioCore] Analyze: Gender={preferred_gender or 'auto'} | Genre={style['genre']} | BPM={bpm_adj}")

        integ = self.integrity.analyze(raw)
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))

        philosophy = (
            f"Truth={tlp.get('truth', 0):.2f}, Love={tlp.get('love', 0):.2f}, Pain={tlp.get('pain', 0):.2f}, CF={tlp.get('conscious_frequency', 0):.2f}"
        )

        prompt_full = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno")
        annotated_text = self.annotate_text(raw, overlay_pack["overlay"], style, vox, bpm_adj, emo, tlp)

        return {
            "emotions": emo,
            "tlp": tlp,
            "bpm": bpm_adj,
            "frequency": freq,
            "style": style,
            "vocals": vox,
            "instruments": inst,
            "prompt_full": prompt_full,
            "prompt_suno": prompt_suno,
            "annotated_text": annotated_text,
            "preferred_gender": preferred_gender or "auto",
            "version": version
        }

# ==========================================================
# ✅ Auto-Register Patch
# ==========================================================
STUDIOCORE_VERSION = "v4.3.2"
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
