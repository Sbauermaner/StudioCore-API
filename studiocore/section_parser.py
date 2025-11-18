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


class SectionParser:
    """High-level helper that unifies structural parsing and annotations."""

    def __init__(self, text_engine: TextStructureEngine | None = None) -> None:
        self._text_engine = text_engine or TextStructureEngine()
        self._annotation_engine = SectionTagAnalyzer()

    def parse(self, text: str, *, sections: Sequence[str] | None = None) -> SectionParseResult:
        resolved_sections = list(sections) if sections is not None else self._text_engine.auto_section_split(text)
        metadata = self._text_engine.section_metadata()
        annotations = self._annotation_engine.parse(text)
        return SectionParseResult(resolved_sections, metadata, annotations)

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
