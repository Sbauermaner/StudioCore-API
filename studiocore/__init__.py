from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

# --- Internal modules ---
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
    StudioCore v5 — Self-adaptive lyrical interpretation engine.
    No fixed styles: every output is generated uniquely from lyrical semantics,
    emotional ratios (Truth × Love × Pain), and rhythmic density.
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
        """Adaptive analysis — no pre-defined genres, pure emergent logic."""
        try:
            version = version or self.cfg.get("suno_version", "v5")
            print("✅ StudioCore v5: analyze() started")

            # --- Stage 1. Text normalization ---
            txt = normalize_text_preserve_symbols(text)
            sections = extract_sections(txt)

            # --- Stage 2. Emotional & Semantic scan ---
            emo = self.emotion.analyze(txt)
            tlp = self.tlp.analyze(txt)
            bpm = self.rhythm.bpm_from_density(txt)

            # --- Stage 3. Self-adaptive style generation ---
            # StyleMatrix.build() не берёт жанры из списка, а выводит их из лирики
            style_data = self.style.build(emo, tlp, txt, bpm)
            # Например: {'genre': 'adaptive emotional', 'style': 'text-driven cinematic', ...}

            # --- Stage 4. Vocals & Instruments prediction ---
            vox, inst = self.vocals.get(style_data.get("genre", "auto"), preferred_gender or "auto", txt, sections)

            # --- Stage 5. Frequency & safety ---
            resonance = self.freq.resonance_profile(tlp)
            resonance["recommended_octaves"] = self.safety.clamp_octaves(resonance.get("recommended_octaves", [2,3,4,5]))

            # --- Stage 6. Integrity + ToneColor ---
            integrity = self.integrity.analyze(txt)
            tonesync = self.tone.colors_for_primary(emo)

            # --- Stage 7. Philosophical layer ---
            philosophy = (
                f"Truth={tlp.get('truth',0):.2f}, "
                f"Love={tlp.get('love',0):.2f}, "
                f"Pain={tlp.get('pain',0):.2f}, "
                f"Conscious Frequency={tlp.get('conscious_frequency',0):.2f}"
            )

            # --- Stage 8. Prompt assembly ---
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
                "prompt": prompt_full,
                "prompt_suno": prompt_suno,
                "version": version,
            }

        except Exception as e:
            print("❌ ERROR in StudioCore.analyze:", e)
            return {
                "error": str(e),
                "message": "⚠️ Анализ не завершён: ядро не вернуло результат.",
                "text_preview": text[:300]
            }

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        """Exports full adaptive analysis report."""
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
