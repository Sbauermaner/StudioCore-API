from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

# --- Import internal logic modules ---
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
    Central pipeline for text → emotional → musical transformation.
    Converts human-written lyrics into Suno-ready style prompts.
    """

    def __init__(self, config_path: str | None = None):
        # --- Load global configuration ---
        self.cfg = load_config(config_path or "studio_config.json")

        # --- Initialize analytical modules ---
        self.emotion = AutoEmotionalAnalyzer()
        self.tlp = TruthLovePainEngine()
        self.rhythm = LyricMeter()
        self.freq = UniversalFrequencyEngine()
        self.safety = RNSSafety(self.cfg)
        self.integrity = IntegrityScanEngine()
        self.vocals = VocalProfileRegistry()
        self.style = StyleMatrix()
        self.tone = ToneSyncEngine()

    # ===========================================================
    # ---------------------- MAIN ANALYSIS ----------------------
    # ===========================================================

    def analyze(self, text: str,
                author_style: str | None = None,
                preferred_gender: str | None = None,
                version: str | None = None) -> Dict[str, Any]:
        """
        Full StudioCore pipeline — from raw lyrics to ready-to-use Suno prompt.
        """
        version = version or self.cfg.get("suno_version", "v5")

        # --- Normalize and parse ---
        txt = normalize_text_preserve_symbols(text)
        sections = extract_sections(txt)

        # --- Emotional & structural layers ---
        emo = self.emotion.analyze(txt)           # joy, sadness, anger, etc.
        tlp = self.tlp.analyze(txt)               # truth, love, pain

        bpm = self.rhythm.bpm_from_density(txt)
        tonality = self.style.tonality(emo)
        genre = self.style.genre(emo, tlp, txt, bpm)
        techniques = self.style.techniques(emo, txt)
        style_words = self.style.recommend(emo, tlp, author_style, sections)

        # --- Vocals & instruments recommendation ---
        vox, inst = self.vocals.get(genre, preferred_gender or "auto", txt, sections)

        # --- Frequency resonance & safety control ---
        resonance = self.freq.resonance_profile(tlp)
        resonance["recommended_octaves"] = self.safety.clamp_octaves(
            resonance["recommended_octaves"]
        )

        # --- Integrity & tonal sync analysis ---
        integrity = self.integrity.analyze(txt)
        tonesync = self.tone.colors_for_primary(emo)

        # --- Build philosophical summary ---
        truth = tlp.get("truth", 0.0)
        love = tlp.get("love", 0.0)
        pain = tlp.get("pain", 0.0)
        freq = tlp.get("conscious_frequency", round(truth * love * max(pain, 0.05), 2))

        philosophy = (
            f"Truth={truth:.2f}, Love={love:.2f}, Pain={pain:.2f}, "
            f"Conscious Frequency={freq:.2f}"
        )

        # --- Final Suno prompt ---
        prompt = build_suno_prompt(
            genre=genre,
            style_words=style_words,
            voices=vox,
            instruments=inst,
            bpm=bpm,
            philosophy=philosophy,
            techniques=techniques,
            version=version,
        )

        # --- Return full structured report ---
        return {
            "genre": genre,
            "bpm": bpm,
            "tonality": tonality,
            "vocals": vox,
            "instruments": inst,
            "techniques": techniques,
            "emotions": emo,
            "tlp": tlp,
            "resonance": resonance,
            "integrity": integrity,
            "tonesync": tonesync,
            "prompt": prompt,
            "version": version,
        }

    # ===========================================================
    # ---------------------- SAVE REPORT ------------------------
    # ===========================================================

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        """
        Exports full analysis report for external visualization or testing.
        """
        Path(path).write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return path


__all__ = ["StudioCore"]
