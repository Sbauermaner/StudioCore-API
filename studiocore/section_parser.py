# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""Structured section parser used by the MAXI orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

from .logical_engines import TextStructureEngine
from .sections import SectionTagAnalyzer


@dataclass
class SectionParseResult:
    """Container with resolved sections, metadata and annotations."""

    sections: List[str]
    metadata: List[Dict[str, Any]]
    annotations: List[Dict[str, Any]]
    prefer_strict_boundary: bool = False


class SectionParser:
    """High-level helper that unifies structural parsing and annotations."""

    def __init__(self, text_engine: TextStructureEngine | None = None) -> None:
        self._text_engine = text_engine or TextStructureEngine()
        self._annotation_engine = SectionTagAnalyzer()

    def _estimate_lyrical_density(self, text: str) -> float:
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return 0.0
        words = sum(len(line.split()) for line in lines)
        avg_words = words / len(lines)
        return round(min(1.0, avg_words / 12.0), 3)

    def _estimate_rde_emotion(self, text: str) -> float:
        exclaim_weight = text.count("!") * 0.01
        caps_weight = sum(1 for line in text.splitlines() if line.strip().isupper()) * 0.05
        return round(min(1.0, exclaim_weight + caps_weight), 3)

    def parse(self, text: str, *, sections: Sequence[str] | None = None) -> SectionParseResult:
        resolved_sections = list(sections) if sections is not None else self._text_engine.auto_section_split(text)
        metadata = self._text_engine.section_metadata()
        annotations = self._annotation_engine.parse(text)
        lyrical_density = self._estimate_lyrical_density("\n".join(resolved_sections) or text)
        rde_emotion_hint = self._estimate_rde_emotion(text)
        prefer_strict_boundary = lyrical_density > 0.85 or rde_emotion_hint > 0.6
        metadata.append(
            {
                "lyrical_density": lyrical_density,
                "rde_emotion_hint": rde_emotion_hint,
                "prefer_strict_boundary": prefer_strict_boundary,
            }
        )
        return SectionParseResult(resolved_sections, metadata, annotations, prefer_strict_boundary)

    def apply_annotation_effects(
        self,
        *,
        emotions: Dict[str, float],
        bpm: float,
        annotations: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        payload = {"emotions": dict(emotions), "bpm": bpm}
        adjusted = self._annotation_engine.integrate_with_core(payload, list(annotations))
        return {
            "emotions": adjusted.get("emotions", {}),
            "bpm": adjusted.get("bpm", bpm),
            "annotations": list(annotations),
        }


__all__ = ["SectionParser", "SectionParseResult"]

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
