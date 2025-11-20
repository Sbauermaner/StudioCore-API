# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Public BPM helper built on top of the logical engines module."""

from __future__ import annotations

from typing import Any, Dict, Sequence

from .logical_engines import BPMEngine as _CoreBPMEngine


class BPMEngine(_CoreBPMEngine):
    """Expose a concise helper API for rhythm-aware tooling."""

    def describe(self, text: str, *, sections: Sequence[str] | None = None) -> Dict[str, Any]:
        resolved_sections = list(sections) if sections else [text]
        joined_text = "\n\n".join(resolved_sections)
        estimate = float(self.text_bpm_estimation(joined_text))
        curve = self.meaning_bpm_curve(resolved_sections, base_bpm=estimate)
        mapping = self.emotion_bpm_mapping({}, base_bpm=int(estimate))
        poly = self.poly_rhythm_detection(curve)
        return {
            "estimate": estimate,
            "curve": curve,
            "poly_rhythm": poly,
            "target_energy": mapping.get("target_energy"),
        }


__all__ = ["BPMEngine"]
