# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List
from statistics import mean

# --- Core imports ---
from .config import load_config
from .text_utils import normalize_text_preserve_symbols, extract_sections
from .emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
from .rhythm import LyricMeter
from .frequency import UniversalFrequencyEngine, RNSSafety
from .integrity import IntegrityScanEngine
from .vocals import VocalProfileRegistry
from .style import StyleMatrix
from .tone import ToneSyncEngine
from .adapter import build_suno_prompt

STUDIOCORE_VERSION = "v4.3.1-adaptive"
__all__ = ["StudioCore", "STUDIOCORE_VERSION"]

# ========================================
# 🔀 Adaptive Sectioning Utility
# ========================================
def _likely_refrain(line: str) -> bool:
    """Эвристика для припева: короткая/повторяющаяся строка, восклицания, ключевые слова."""
    s = line.strip().lower()
    if not s:
        return False
    if len(s) <= 40:
        return True
    if s.count("!") >= 1:
        return True
    if any(k in s for k in ["припев", "chorus", "refrain", "hook"]):
        return True
    return False


def adaptive_sectioning(
    lines: List[str], tlp: Dict[str, float], emo: Dict[str, float], bpm: int
) -> List[Dict[str, Any]]:
    """
    Делит текст на секции на основе длины, ритмики, TLP и простых поведенческих маркеров.
    Возвращает список секций с прикреплёнными строками.
    """
    n = len(lines)
    if n == 0:
        return []

    # базовое число секций (5–6), корректируем по длине и энергии
    energy = (tlp.get("truth", 0) + tlp.get("love", 0) + tlp.get("pain", 0)) / 3 or 0.0
    target_sections = 6 if n > 16 or energy > 0.45 else 5

    # предварительный разрез
    step = max(2, n // target_sections)
    buckets = [lines[i : i + step] for i in range(0, n, step)]
    # сшиваем очень короткие хвосты
    if len(buckets) > 1 and len(buckets[-1]) == 1:
        buckets[-2].extend(buckets[-1])
        buckets = buckets[:-1]

    truth, love, pain = tlp.get("truth", 0), tlp.get("love", 0), tlp.get("pain", 0)
    cf = tlp.get("conscious_frequency", 0)
    anger, epic, joy, sadness, peace = (
        emo.get("anger", 0),
        emo.get("epic", 0),
        emo.get("joy", 0),
        emo.get("sadness", 0),
        emo.get("peace", 0),
    )

    sections: List[Dict[str, Any]] = []
    for bi, chunk in enumerate(buckets):
        rel = bi / max(1, len(buckets) - 1)

        # эвристика chorus: ищем "припевные" строки в чанке
        chunk_has_refrain = any(_likely_refrain(l) for l in chunk)

        if rel < 0.15:
            name = "Intro"
            mood = "mystic" if cf > 0.5 else "calm"
            focus = "tone_establish"
        elif rel < 0.35:
            name = "Verse 1"
            mood = "reflective" if truth >= love else "narrative"
            focus = "story_flow"
        elif rel < 0.55 and not chunk_has_refrain:
            name = "Bridge"
            mood = "dramatic" if (pain > 0.25 or anger > 0.25) else "dreamlike"
            focus = "contrast"
        elif chunk_has_refrain or (0.55 <= rel < 0.8):
            name = "Chorus"
            mood = "uplifting" if (love >= pain and joy >= sadness) else "tense"
            focus = "release"
        elif rel < 0.9:
            name = "Verse 2"
            mood = "narrative"
            focus = "development"
        else:
            name = "Outro"
            mood = "peaceful" if cf >= 0.6 or peace > sadness else "fading"
            focus = "closure"

        # интенсивность как функция bpm + эмоций
        intensity = round(bpm * (0.8 + 0.4 * rel + (love + pain + anger + epic) / 4), 2)
        tone = "warm" if (love + joy) >= (pain + anger) else "cold"

        sections.append(
            {
                "section": name,
                "mood": mood,
                "focus": focus,
                "intensity": intensity,
                "tone": tone,
                "lines": chunk,
            }
        )

    # слияние дубликатов-хуков (несколько chorus подряд)
    merged: List[Dict[str, Any]] = []
    for sec in sections:
        if merged and sec["section"] == "Chorus" and merged[-1]["section"] == "Chorus":
            merged[-1]["lines"].extend(sec["lines"])
            merged[-1]["intensity"] = max(merged[-1]["intensity"], sec["intensity"])
        else:
            merged.append(sec)
    return merged


class StudioCore:
    """Central AI pipeline: text → emotion → frequency → structure → tone → style → self-adaptive annotations."""

    def __init__(self, config_path: str | None = None):
        self.cfg = load_config(config_path or "studio_config.json")
        self.emotion = AutoEmotionalAnalyzer()
        self.tlp = TruthLovePainEngine()
        self.rhythm = LyricMeter()
        self.freq = UniversalFrequencyEngine()
        self.safety = RNSSafety(self.cfg)
        self.integrity = IntegrityScanEngine()
        self.vocals = VocalProfileRegistry()
        self.style = StyleMatrix()
        self.tone = ToneSyncEngine()

    # =============================
    # 🔬 Семантические секции
    # =============================
    def _build_semantic_sections(
        self, text: str, emo: Dict[str, float], tlp: Dict[str, float], bpm: int
    ) -> Dict[str, Any]:
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0)
        avg_emo = mean(abs(v) for v in emo.values()) if emo else 0.0

        bpm_adj = int(bpm + (avg_emo * 8) + (cf * 4))
        overlay = {
            "depth": round((truth + pain) / 2, 2),
            "warmth": round(love, 2),
            "clarity": round(cf, 2),
            "sections": adaptive_sectioning(
                [l for l in text.strip().split("\n") if l.strip()], tlp, emo, bpm_adj
            ),
        }
        return {"bpm": bpm_adj, "overlay": overlay}

    # =============================
    # 🎙 Тембральный дескриптор
    # =============================
    def _timbral_descriptor(
        self,
        sec: Dict[str, Any],
        emo: Dict[str, float],
        tlp: Dict[str, float],
        bpm: int,
        vocals: List[str],
    ) -> str:
        level = (sec.get("intensity", bpm) / max(1.0, bpm))
        anger, epic, joy, sadness, peace = (
            emo.get("anger", 0),
            emo.get("epic", 0),
            emo.get("joy", 0),
            emo.get("sadness", 0),
            emo.get("peace", 0),
        )
        love, pain = tlp.get("love", 0), tlp.get("pain", 0)
        parts = []

        if level < 0.9:
            parts.append("soft whisper, close-mic, airy")
        elif level < 1.05:
            parts.append("warm mid-voice, storytelling tone")
        elif level < 1.2:
            parts.append("emotional rise, mixed voice")
        else:
            parts.append("full belt, cinematic projection")

        if sadness > 0.25 or pain > 0.3:
            parts.append("gentle vibrato")
        if anger > 0.35:
            parts.append("rasp / grit accent")
        if joy > 0.3 and love > 0.35:
            parts.append("bright resonance, slight cry")
        if epic > 0.35 or any(x in vocals for x in ["choir", "trio", "quartet"]):
            parts.append("choral layering")

        if sec["section"].lower().startswith("intro"):
            parts.append("subtle breath, sparse reverb")
        if sec["section"].lower().startswith("outro"):
            parts.append("soft fade, intimate tail")

        return ", ".join(dict.fromkeys(parts))

    # =============================
    # 🧠 Авто-аннотация
    # =============================
    def annotate_text(
        self,
        text: str,
        overlay: Dict[str, Any],
        style: Dict[str, Any],
        vocals: list,
        bpm: int,
        emo: Dict[str, float],
        tlp: Dict[str, float],
    ) -> str:
        sections = overlay.get("sections", [])
        if not sections:
            return text

        annotated: List[str] = []
        for sec in sections:
            timbre = self._timbral_descriptor(sec, emo, tlp, bpm, vocals)
            annotated.append(
                f"[{sec['section']} – ({sec['mood']}, focus={sec['focus']}, "
                f"tone={sec.get('tone','neutral')}, intensity={sec['intensity']})]\n"
                f"(timbre: {timbre})"
            )
            annotated.extend(sec.get("lines", []))
            annotated.append("")

        annotated.append(
            f"[End – BPM≈{bpm}, Vocal={style.get('vocal_form','auto')}, "
            f"Tone={style.get('key','auto')}]"
        )
        return "\n".join(annotated).strip()

    # =============================
    # 🔍 Основной анализ
    # =============================
    def analyze(
        self,
        text: str,
        author_style: str | None = None,
        preferred_gender: str | None = None,
        version: str | None = None,
    ) -> Dict[str, Any]:
        version = version or self.cfg.get("suno_version", "v5")

        # --- Normalize / structure ---
        txt = normalize_text_preserve_symbols(text)
        sections_proto = extract_sections(txt)  # влияет на подбор вокала

        # --- Emotions & TLP ---
        emo = self.emotion.analyze(txt)
        tlp = self.tlp.analyze(txt)

        # --- Rhythm & Frequency ---
        bpm = self.rhythm.bpm_from_density(txt)
        resonance = self.freq.resonance_profile(tlp)
        resonance["recommended_octaves"] = self.safety.clamp_octaves(
            resonance.get("recommended_octaves", [2, 3, 4, 5])
        )

        # --- Semantic phases (adaptive) ---
        semantic = self._build_semantic_sections(txt, emo, tlp, bpm)
        bpm = semantic["bpm"]

        # --- Style & instrumentation ---
        style_data = self.style.build(emo, tlp, txt, bpm)
        vox, inst, vocal_form = self.vocals.get(
            style_data["genre"], preferred_gender or "auto", txt, sections_proto
        )
        style_data["vocal_form"] = vocal_form

        # --- Integrity & tonesync ---
        integrity = self.integrity.analyze(txt)
        tonesync = self.tone.colors_for_primary(
            emo, tlp, style_data.get("key", "auto")
        )

        # --- Philosophy ---
        philosophy = (
            f"Truth={tlp.get('truth', 0):.2f}, Love={tlp.get('love', 0):.2f}, "
            f"Pain={tlp.get('pain', 0):.2f}, "
            f"Conscious Frequency={tlp.get('conscious_frequency', 0):.2f}"
        )

        # --- Prompts ---
        prompt_full = build_suno_prompt(
            style_data, vox, inst, bpm, philosophy, version, mode="full"
        )
        prompt_suno = build_suno_prompt(
            style_data, vox, inst, bpm, philosophy, version, mode="suno"
        )
        prompt_suno += (
            f"\nToneSync: primary={tonesync['primary_color']}, "
            f"accent={tonesync['accent_color']}, "
            f"mood={tonesync['mood_temperature']}, "
            f"resonance={tonesync['resonance_hz']}Hz"
        )

        # --- Assemble result ---
        result: Dict[str, Any] = {
            "emotions": emo,
            "tlp": tlp,
            "bpm": bpm,
            "overlay": semantic["overlay"],
            "style": style_data,
            "vocals": vox,
            "instruments": inst,
            "resonance": resonance,
            "integrity": integrity,
            "tonesync": tonesync,
            "philosophy": philosophy,
            "prompt_full": prompt_full,
            "prompt_suno": prompt_suno,
            "safety": getattr(self.safety, "safety_meta", lambda: {})(),
            "version": version,
        }

        # ✅ повторная аннотация при её отсутствии
        if result.get("annotated_text"):
            annotated_text = result["annotated_text"]
        else:
            annotated_text = self.annotate_text(
                txt,
                result.get("overlay", {}),
                result.get("style", {}),
                result.get("vocals", []),
                result.get("bpm") or self.rhythm.bpm_from_density(txt) or 120,
                result.get("emotions", {}),
                result.get("tlp", {}),
            )

        result["annotated_text"] = annotated_text
        return result

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        """Exports full analysis report for external visualization."""
        Path(path).write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return path
