from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

# --- Import all internal modules ---
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

    def analyze(self, text: str,
                author_style: str | None = None,
                preferred_gender: str | None = None,
                version: str | None = None) -> Dict[str, Any]:
        """
        Full analysis pipeline — with safety guards and detailed debug output.
        Compresses (not trims) long prompts for Suno without loss of meaning.
        """
        try:
            version = version or self.cfg.get("suno_version", "v5")
            print("✅ StudioCore analyze started")

            txt = normalize_text_preserve_symbols(text)
            sections = extract_sections(txt)
            print("Text normalized OK")

            # === Analytical layers ===
            emo = self.emotion.analyze(txt)
            print("Emotion OK:", emo)

            tlp = self.tlp.analyze(txt)
            print("TLP OK:", tlp)

            bpm = self.rhythm.bpm_from_density(txt)
            print("BPM OK:", bpm)

            style_data = self.style.build(emo, tlp, txt, bpm)
            print("Style OK:", style_data)

            vox, inst = self.vocals.get(style_data.get("genre", "unknown"),
                                        preferred_gender or "auto", txt, sections)
            print("Vocals/Inst OK:", vox, inst)

            resonance = self.freq.resonance_profile(tlp)
            resonance["recommended_octaves"] = self.safety.clamp_octaves(
                resonance.get("recommended_octaves", [2, 3, 4, 5])
            )
            print("Resonance OK:", resonance)

            integrity = self.integrity.analyze(txt)
            print("Integrity OK:", integrity)

            tonesync = self.tone.colors_for_primary(emo)
            print("ToneSync OK:", tonesync)

            # === Philosophy (Truth × Love × Pain) ===
            philosophy = (
                f"Truth={tlp.get('truth', 0):.2f}, "
                f"Love={tlp.get('love', 0):.2f}, "
                f"Pain={tlp.get('pain', 0):.2f}, "
                f"Conscious Frequency={tlp.get('conscious_frequency', 0):.2f}"
            )
            print("Philosophy OK:", philosophy)

            # === Prompt building ===
            prompt_full = (
                f"Genre: {style_data.get('genre','unknown')} | "
                f"Style: {style_data.get('style','adaptive expressive')} | "
                f"Vocals: {', '.join(vox)} | "
                f"Instruments: {', '.join(inst)} | "
                f"Vocal techniques: {', '.join(style_data.get('techniques', []))} | "
                f"Tempo: {bpm} BPM | "
                f"{philosophy} | "
                f"Engine: StudioCore {version} adaptive emotional system"
            )

            prompt_suno = build_suno_prompt(
                style_data.get("genre", "unknown"),
                style_data.get("style", ""),
                vox,
                inst,
                bpm,
                philosophy,
                style_data.get("techniques", []),
                version
            )

            print("✅ Prompts built successfully")

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

        except Exception as e:
            print("❌ ERROR in StudioCore.analyze:", e)
            return {
                "error": str(e),
                "message": "⚠️ Анализ не завершён: ядро не вернуло результат.",
                "text_preview": text[:300]
            }

    def save_report(self, result: Dict[str, Any], path: str = "studio_report.json"):
        """Exports full analysis report for external visualization."""
        Path(path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
