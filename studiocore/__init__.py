from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

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
    text → emotion → frequency → structure → tone → style.
    No predefined genres — all parameters form adaptively.
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

    def analyze(
        self,
        text: str,
        author_style: str | None = None,
        preferred_gender: str | None = None,
        version: str | None = None
    ) -> Dict[str, Any]:
        """
        Full adaptive emotional-semantic analysis.
        Detects structure, tone, BPM, resonance, colors, and builds a synesthetic style.
        """
        version = version or self.cfg.get("suno_version", "v5")

        # --- Normalize and parse text ---
        txt = normalize_text_preserve_symbols(text)
        sections = extract_sections(txt)

        # --- Emotional layers ---
        emo = self.emotion.analyze(txt)
        tlp = self.tlp.analyze(txt)

        # --- Rhythmic and frequency analysis ---
        bpm = self.rhythm.bpm_from_density(txt)
        resonance = self.freq.resonance_profile(tlp)
        resonance["recommended_octaves"] = self.safety.clamp_octaves(
            resonance.get("recommended_octaves", [2, 3, 4, 5])
        )

        # --- Style and instrumentation ---
        style_data = self.style.build(emo, tlp, txt, bpm)

        # ⬇️ Обновлённый вызов — с поддержкой формы ансамбля
        vox, inst, vocal_form = self.vocals.get(
            style_data["genre"],
            preferred_gender or "auto",
            txt,
            sections
        )
        style_data["vocal_form"] = vocal_form

        # --- Integrity & tone sync ---
        integrity = self.integrity.analyze(txt)
        tonesync = self.tone.colors_for_primary(emo, tlp, style_data.get("key", "auto"))

        # --- Conscious formula ---
        philosophy = (
            f"Truth={tlp.get('truth', 0):.2f}, "
            f"Love={tlp.get('love', 0):.2f}, "
            f"Pain={tlp.get('pain', 0):.2f}, "
            f"Conscious Frequency={tlp.get('conscious_frequency', 0):.2f}"
        )

        # --- Build prompts ---
        prompt_full = build_suno_prompt(
            style_data, vox, inst, bpm, philosophy, version, mode="full"
        )
        prompt_suno = build_suno_prompt(
            style_data, vox, inst, bpm, philosophy, version, mode="suno"
        )

        # Добавляем цветовой слой ToneSync в финальный prompt
        prompt_suno += (
            f"\nToneSync: primary={tonesync['primary_color']}, "
            f"accent={tonesync['accent_color']}, "
            f"mood={tonesync['mood_temperature']}, "
            f"resonance={tonesync['resonance_hz']}Hz"
        )

        return {
            "emotions": emo,
            "tlp": tlp,
            "bpm": bpm,
            "style": style_data,
            "vocals": vox,
            "instruments": inst,
            "resonance": resonance,
            "integrity": integrity,
            "tonesync": tonesync,
            "philosophy": philosophy,
            "prompt_full": prompt_full,
            "prompt_suno": prompt_suno,
            "version": version
        }

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        """Exports full analysis report for external visualization."""
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
