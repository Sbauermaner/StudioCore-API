from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
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


class StudioCore:
    """
    Central AI pipeline:
    text → emotion → frequency → structure → tone → style → self-adaptive annotations.
    """

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

    # ========================================
    # 🧩 Построение семантических аннотаций
    # ========================================
    def _build_semantic_sections(self, emo: Dict[str, float], tlp: Dict[str, float], bpm: int) -> Dict[str, Any]:
        """
        Создаёт динамические аннотации (Intro, Verse, Bridge, Chorus, Outro)
        на основе эмоционального фона и параметров ядра.
        """
        love, pain, truth = tlp.get("love", 0), tlp.get("pain", 0), tlp.get("truth", 0)
        cf = tlp.get("conscious_frequency", 0)
        avg_emo = mean(abs(v) for v in emo.values()) if emo else 0.0

        intro = {
            "section": "Intro",
            "mood": "calm" if cf < 0.5 else "mystic",
            "intensity": round(bpm * 0.8, 2),
            "focus": "tone_establish",
        }
        verse = {
            "section": "Verse",
            "mood": "reflective" if truth > love else "narrative",
            "intensity": round(bpm, 2),
            "focus": "story_flow",
        }
        bridge = {
            "section": "Bridge",
            "mood": "dramatic" if pain > 0.3 else "dreamlike",
            "intensity": round(bpm * (1.05 + avg_emo / 4), 2),
            "focus": "contrast",
        }
        chorus = {
            "section": "Chorus",
            "mood": "uplifting" if love > pain else "tense",
            "intensity": round(bpm * 1.15, 2),
            "focus": "release",
        }
        outro = {
            "section": "Outro",
            "mood": "peaceful" if cf > 0.6 else "fading",
            "intensity": round(bpm * 0.7, 2),
            "focus": "closure",
        }

        bpm_adj = int(bpm + (avg_emo * 8) + (cf * 4))
        overlay = {
            "depth": round((truth + pain) / 2, 2),
            "warmth": round(love, 2),
            "clarity": round(cf, 2),
            "sections": [intro, verse, bridge, chorus, outro],
        }
        return {"bpm": bpm_adj, "overlay": overlay}

    # ========================================
    # 🧠 Автоматическая аннотация текста
    # ========================================
    def annotate_text(self, text: str, overlay: Dict[str, Any], style: Dict[str, Any], vocals: list, bpm: int) -> str:
        """
        Возвращает текст с автоматической аннотацией секций и параметров ядра.
        """
        lines = [l for l in text.strip().split("\n") if l.strip()]
        sections = overlay.get("sections", [])
        if not sections:
            return text

        # Делим текст на логические блоки по длине
        block_size = max(1, len(lines) // len(sections))
        annotated = []
        idx = 0

        for sec in sections:
            tag = f"[{sec['section']} – {sec['mood'].capitalize()}, focus={sec['focus']}]"
            annotated.append(tag)
            block_lines = lines[idx: idx + block_size]
            annotated.extend(block_lines)
            idx += block_size

        annotated.append(f"[End – BPM≈{bpm}, Vocal={style.get('vocal_form','auto')}, Tone={style.get('key','auto')}]")

        # Добавляем информацию о вокалах
        tech = ", ".join([v for v in vocals if v not in ["male", "female"]])
        annotated.append(f"[Vocal Techniques: {tech or 'neutral tone'}]")
        return "\n".join(annotated)

    # ========================================
    # 🔬 Основной анализ
    # ========================================
    def analyze(
        self,
        text: str,
        author_style: str | None = None,
        preferred_gender: str | None = None,
        version: str | None = None
    ) -> Dict[str, Any]:
        """
        Full adaptive emotional-semantic analysis + self-generated annotation overlay.
        """
        version = version or self.cfg.get("suno_version", "v5")
        txt = normalize_text_preserve_symbols(text)
        sections = extract_sections(txt)

        # --- Эмоции и TLP ---
        emo = self.emotion.analyze(txt)
        tlp = self.tlp.analyze(txt)

        # --- Ритм и частоты ---
        bpm = self.rhythm.bpm_from_density(txt)
        resonance = self.freq.resonance_profile(tlp)
        resonance["recommended_octaves"] = self.safety.clamp_octaves(resonance.get("recommended_octaves", [2, 3, 4, 5]))

        # --- Семантические фазы ---
        semantic = self._build_semantic_sections(emo, tlp, bpm)
        bpm = semantic["bpm"]

        # --- Стиль и инструменты ---
        style_data = self.style.build(emo, tlp, txt, bpm)
        vox, inst, vocal_form = self.vocals.get(style_data["genre"], preferred_gender or "auto", txt, sections)
        style_data["vocal_form"] = vocal_form

        # --- Цвет и структура ---
        integrity = self.integrity.analyze(txt)
        tonesync = self.tone.colors_for_primary(emo, tlp, style_data.get("key", "auto"))

        # --- Философия ---
        philosophy = (
            f"Truth={tlp.get('truth', 0):.2f}, "
            f"Love={tlp.get('love', 0):.2f}, "
            f"Pain={tlp.get('pain', 0):.2f}, "
            f"Conscious Frequency={tlp.get('conscious_frequency', 0):.2f}"
        )

        # --- Промты ---
        prompt_full = build_suno_prompt(style_data, vox, inst, bpm, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style_data, vox, inst, bpm, philosophy, version, mode="suno")
        prompt_suno += (
            f"\nToneSync: primary={tonesync['primary_color']}, "
            f"accent={tonesync['accent_color']}, "
            f"mood={tonesync['mood_temperature']}, "
            f"resonance={tonesync['resonance_hz']}Hz"
        )

        # --- Авто-аннотированный текст ---
        annotated_text = self.annotate_text(txt, semantic["overlay"], style_data, vox, bpm)

        # --- Результат ---
        return {
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
            "annotated_text": annotated_text,   # ⬅️ добавлен возврат аннотированного текста
            "version": version
        }

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        """Exports full analysis report for external visualization."""
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
