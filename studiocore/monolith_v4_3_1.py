# -*- coding: utf-8 -*-
"""
StudioCore v4.3.1 — Monolith
Включает патчи:
- Улучшенный расчёт BPM по слогам и пунктуации
- Расширенный частотный профиль (base/harmonic_range/modulation_depth)
- RNS Safety с метаданными лимитов
- Integrity: когнитивные метрики (лекс. разнообразие, саморефлексия, coherence)
- StyleMatrix: «whitelist» жанров для Suno + style_descr_full
- Возврат safety в результате анализа
- Авто-аннотация текста (overlay + вокальный слой)
"""

from __future__ import annotations
import re
import json
from pathlib import Path
from statistics import mean
from typing import Dict, Any, List, Tuple

# --- Core imports (используем существующие модули где нужно) ---
from .config import load_config
from .text_utils import normalize_text_preserve_symbols, extract_sections
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from .tone import ToneSyncEngine
from .adapter import build_suno_prompt
from .vocals import VocalProfileRegistry


# ================================
# Patched subsystems (локально)
# ================================

class PatchedLyricMeter:
    """BPM по слоговой плотности + учёт пунктуации."""
    vowels = set("aeiouyауоыиэяюёеAEIOUYАУОЫИЭЯЮЁЕ")

    def _syllables(self, line: str) -> int:
        return max(1, sum(1 for ch in line if ch in self.vowels))

    def bpm_from_density(self, text: str) -> int:
        lines = [l for l in text.split("\n") if l.strip()]
        if not lines:
            return 100
        avg_syll = sum(self._syllables(l) for l in lines) / max(1, len(lines))
        # длиннее фраза → медленнее темп
        bpm = 140 - min(60, (avg_syll - 8) * 6)
        punct_boost = sum(ch in ",.!?…" for ch in text) * 0.5
        bpm = bpm + min(20, punct_boost)
        return int(max(60, min(180, bpm)))


class PatchedUniversalFrequencyEngine:
    """Расширенный частотный профиль."""
    base = 24.5  # базовая условная частота для построения дальнейших слоёв

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
    """RNS-безопасность с белым списком октав и метаданными лимитов."""
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
    """Когнитивные метрики текста."""
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


# ----- StyleMatrix: используем твою логику и whitelist жанров -----

class PatchedStyleMatrix:
    EMO_GROUPS = {
        "soft": ["love", "peace", "joy"],
        "dark": ["sadness", "pain", "fear"],
        "epic": ["anger", "epic"],
    }

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

    def _derive_visual(self, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        t, l, p = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
        if p > l and p > t:
            return "rain, fog, silhouettes, slow motion"
        elif l > p and l > t:
            return "warm light, faces, sunrise, hands touching"
        elif t > 0.4:
            return "clear sky, horizon, open space"
        else:
            return "shifting colors, abstract movement"

    def _derive_narrative(self, text: str, emo: Dict[str, float], tlp: Dict[str, float]) -> str:
        if tlp.get("pain", 0) > 0.6:
            return "suffering → awakening → transcendence"
        elif tlp.get("love", 0) > 0.6:
            return "loneliness → connection → unity"
        elif tlp.get("truth", 0) > 0.6:
            return "ignorance → revelation → wisdom"
        else:
            return "search → struggle → transformation"

    def _derive_techniques(self, emo: Dict[str, float], tlp: Dict[str, float]) -> List[str]:
        tech = []
        if emo.get("anger", 0) > 0.4:
            tech += ["belt", "rasp", "grit"]
        if emo.get("sadness", 0) > 0.3 or tlp.get("pain", 0) > 0.4:
            tech += ["vibrato", "soft cry"]
        if emo.get("joy", 0) > 0.3:
            tech += ["falsetto", "bright tone"]
        if emo.get("epic", 0) > 0.4:
            tech += ["choral layering"]
        return tech or ["neutral tone"]

    def _derive_atmosphere(self, emo: Dict[str, float]) -> str:
        dominant = max(emo, key=emo.get)
        if dominant in ("joy", "peace"):
            return "serene and hopeful"
        elif dominant in ("sadness", "pain"):
            return "introspective and melancholic"
        elif dominant == "anger":
            return "intense and cathartic"
        elif dominant == "epic":
            return "monumental and triumphant"
        else:
            return "mysterious and reflective"

    def build(self, emo: Dict[str, float], tlp: Dict[str, float], text: str, bpm: int) -> Dict[str, Any]:
        descr = self._derive_genre(text, emo, tlp)
        # Suno whitelist: если в полном описании встречается валидный жанр — берём его
        valid_genres = {"rock", "pop", "folk", "electronic", "ambient", "cinematic", "orchestral", "hip hop", "rap"}
        genre = next((g for g in valid_genres if g in descr), "rock")
        return {
            "genre": genre,
            "style": self._tone_profile(emo, tlp),
            "key": self._derive_key(tlp, bpm),
            "structure": "intro-verse-chorus-outro",
            "visual": self._derive_visual(emo, tlp),
            "narrative": self._derive_narrative(text, emo, tlp),
            "atmosphere": self._derive_atmosphere(emo),
            "techniques": self._derive_techniques(emo, tlp),
            "style_descr_full": descr,
        }


# ================================
# StudioCore (монолит)
# ================================

class StudioCore:
    """
    Central AI pipeline:
    text → emotion → frequency → structure → tone → style → annotations.
    """

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

    # -------- Семантические фазы (overlay) --------
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

    # -------- Авто-аннотация текста линиями --------
    def annotate_text(
        self,
        text: str,
        overlay: Dict[str, Any],
        style: Dict[str, Any],
        vocals: List[str],
        bpm: int,
        emotions: Dict[str, float] | None = None,
        tlp: Dict[str, float] | None = None,
    ) -> str:
        lines = [l for l in text.strip().split("\n") if l.strip()]
        sections = overlay.get("sections", [])
        if not sections:
            return text

        block_size = max(1, len(lines) // len(sections))
        annotated: List[str] = []
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

    # -------- Основной анализ --------
    def analyze(
        self,
        text: str,
        author_style: str | None = None,
        preferred_gender: str | None = None,
        version: str | None = None
    ) -> Dict[str, Any]:

        version = version or self.cfg.get("suno_version", "v5")
        raw = normalize_text_preserve_symbols(text)
        sections = extract_sections(raw)

        # Эмоции / TLP
        emo = self.emotion.analyze(raw)
        tlp = self.tlp.analyze(raw)

        # Ритм / Частоты / Безопасность
        bpm = self.rhythm.bpm_from_density(raw)
        freq = self.freq.resonance_profile(tlp)
        rec_oct = self.safety.clamp_octaves(freq.get("recommended_octaves", [2, 3, 4, 5]))

        # Семантические фазы и корректировка BPM
        overlay_pack = self._build_semantic_sections(emo, tlp, bpm)
        bpm_adj = overlay_pack["bpm"]

        # Стиль и ансамбль
        style = self.style.build(emo, tlp, raw, bpm_adj)
        vox, inst, vocal_form = self.vocals.get(style["genre"], preferred_gender or "auto", raw, sections)
        style["vocal_form"] = vocal_form

        # Интегрит и цвет
        integ = self.integrity.analyze(raw)
        tone = self.tone.colors_for_primary(emo, tlp, style.get("key", "auto"))

        # Философия
        philosophy = (
            f"Truth={tlp.get('truth', 0):.2f}, "
            f"Love={tlp.get('love', 0):.2f}, "
            f"Pain={tlp.get('pain', 0):.2f}, "
            f"Conscious Frequency={tlp.get('conscious_frequency', 0):.2f}"
        )

        # Промты
        prompt_full = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style, vox, inst, bpm_adj, philosophy, version, mode="suno")
        prompt_suno += (
            f"\nToneSync: primary={tone['primary_color']}, "
            f"accent={tone['accent_color']}, "
            f"mood={tone['mood_temperature']}, "
            f"resonance={tone['resonance_hz']}Hz"
        )

        # Аннотированный текст
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
            "version": version
        }

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
