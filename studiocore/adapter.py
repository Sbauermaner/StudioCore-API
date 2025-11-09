# -*- coding: utf-8 -*-
"""
Adapters and helpers for external AI music systems (Suno, etc.).
"""

def soft_trim(text: str, max_len: int) -> str:
    """Trim text softly to max_len without breaking words."""
    if len(text) <= max_len:
        return text
    trimmed = text[:max_len]
    if " " in trimmed:
        trimmed = trimmed.rsplit(" ", 1)[0]
    return trimmed.strip()
