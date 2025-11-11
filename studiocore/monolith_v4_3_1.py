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
        self.style = __import__("studiocore.monolith_v4_3_1").PatchedStyleMatrix()
        self.tone = ToneSyncEngine()

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
        overlay = {
            "depth": round((truth + pain) / 2, 2),
            "warmth": round(love, 2),
            "clarity": round(cf, 2),
            "sections": [intro, verse, bridge, chorus, outro],
        }
        return {"bpm": bpm_adj, "overlay": overlay}

    def annotate_text(self, text: str, overlay: Dict[str, Any], style: Dict[str, Any], vocals: List[str], bpm: int, emotions=None, tlp=None) -> str:
        lines = [l for l in text.strip().split("\n") if l.strip()]
        sections = overlay.get("sections", [])
        if not sections:
            return text
        block_size = max(1, len(lines) // len(sections))
        annotated = []
        idx = 0
        for sec in sections:
            tag = f"[{sec['section']} – {sec['mood']}, focus={sec['focus']}] (intensity={sec['intensity']})"
            annotated.append(tag)
            block_lines = lines[idx: idx + block_size]
            annotated.extend(block_lines)
            idx += block_size
        if idx < len(lines):
            annotated.extend(lines[idx:])
        annotated.append(f"[End – BPM≈{bpm}, Vocal={style.get('vocal_form','auto')}, Tone={style.get('key','auto')}]")
        tech = ", ".join([v for v in vocals if v not in ["male", "female"]]) or "neutral tone"
        annotated.append(f"[Vocal Techniques: {tech}]")
        return "\n".join(annotated)

    def analyze(self, text: str, author_style=None, preferred_gender=None, version=None) -> Dict[str, Any]:
        version = version or self.cfg.get("suno_version", "v5")
        raw = normalize_text_preserve_symbols(text)
        sections = extract_sections(raw)
        emo = self.emotion.analyze(raw)
        tlp = self.tlp.analyze(raw)
        bpm = self.rhythm.bpm_from_density(raw)
        freq = self.freq.resonance_profile(tlp)
        rec_oct = self.safety.clamp_octaves(freq.get("recommended_octaves", [2, 3, 4, 5]))
        overlay_pack = self._build_semantic_sections(emo, tlp, bpm)
        bpm_adj = overlay_pack["bpm"]
        style = self.style.build(emo, tlp, raw, bpm_adj)

        # --- адаптированный вокал ---
        vox, inst, vocal_form = self.vocals.get(
            style["genre"],
            preferred_gender or "auto",
            raw,
            sections
        )
        style["vocal_form"] = vocal_form

        integ = self.integrity.analyze(raw)
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))

        philosophy = (
            f"Truth={tlp.get('truth', 0):.2f}, "
            f"Love={tlp.get('love', 0):.2f}, "
            f"Pain={tlp.get('pain', 0):.2f}, "
            f"Conscious Frequency={tlp.get('conscious_frequency', 0):.2f}"
        )

        prompt_full = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno")
        prompt_suno += (
            f"\nToneSync: primary={tone['primary_color']}, "
            f"accent={tone['accent_color']}, "
            f"mood={tone['mood_temperature']}, "
            f"resonance={tone['resonance_hz']}Hz"
        )

        annotated_text = self.annotate_text(raw, overlay_pack["overlay"], style, vox, bpm_adj, emo, tlp)

        return {
            "emotions": emo,
            "tlp": tlp,
            "bpm": bpm_adj,
            "frequency": freq,
            "octaves_safe": rec_oct,
            "safety": self.safety.safety_meta(),
            "tone": tone,
            "integrity": integ,
            "style": style,
            "vocals": vox,
            "instruments": inst,
            "sections": sections,
            "overlay": overlay_pack["overlay"],
            "prompt_full": prompt_full,
            "prompt_suno": prompt_suno,
            "annotated_text": annotated_text,
            "preferred_gender": preferred_gender or "auto",
            "version": version
        }

    def save_report(self, result: Dict[str, Any], path="studio_report.json"):
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
