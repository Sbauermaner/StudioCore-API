from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

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
    """Full analysis pipeline from lyrics → emotional → style logic."""

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

    def analyze(self, text: str, author_style: str | None = None, preferred_gender: str | None = None, version: str | None = None) -> Dict[str, Any]:
        version = version or self.cfg["suno_version"]
        txt = normalize_text_preserve_symbols(text)
        sections = extract_sections(txt)

        emo = self.emotion.analyze(txt)
        tlp = self.tlp.analyze(txt)
        bpm = self.rhythm.bpm_from_density(txt)
        style_data = self.style.build(emo, tlp, txt, bpm)

        vox, inst = self.vocals.get(style_data["genre"], preferred_gender or "auto", txt, sections)

        resonance = self.freq.resonance_profile(tlp)
        resonance["recommended_octaves"] = self.safety.clamp_octaves(resonance["recommended_octaves"])
        integrity = self.integrity.analyze(txt)
        tonesync = self.tone.colors_for_primary(emo)

        philosophy = f"Truth={tlp['truth']:.2f}, Love={tlp['love']:.2f}, Pain={tlp['pain']:.2f}"
        prompt_full = build_suno_prompt(style_data, vox, inst, bpm, philosophy, version, mode="full")
        prompt_suno = build_suno_prompt(style_data, vox, inst, bpm, philosophy, version, mode="suno")

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
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
