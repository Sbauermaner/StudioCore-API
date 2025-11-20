"""Utility helpers for UI payload preparation."""
from __future__ import annotations

from typing import Any, Iterable, List


def coerce_sections(text_obj: Any) -> List[Any]:
    """Return sections as a list regardless of the incoming container type."""
    sections = getattr(text_obj, "sections", []) if text_obj is not None else []
    if isinstance(sections, list):
        return sections
    if isinstance(sections, dict):
        return list(sections.values())
    if isinstance(sections, Iterable) and not isinstance(sections, (str, bytes)):
        return list(sections)
    return [sections] if sections else []
