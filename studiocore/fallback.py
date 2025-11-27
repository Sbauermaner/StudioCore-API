# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""Fallback implementation for StudioCore when the main engine is unavailable."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class StudioCoreFallback:
    """Simple safe - mode placeholder that prevents crashes when core loading fails."""

    def __init__(self, *args, **kwargs) -> None:
        logger.warning("🧩 [StudioCoreFallback] Активен временный режим.")
        self.is_fallback = True
        self.status = "safe - mode"
        self.subsystems = []

    def analyze(
        self,
        text: str,
        preferred_gender: str = "auto",
        version: Optional[str] = None,
        semantic_hints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Task 4.1: Implement a basic analyze method that returns a valid (but static/minimal)
        result dictionary using DEFAULT_CONFIG values, ensuring the API doesn't crash if Monolith fails.
        """
        logger.warning(
            f"⚠️ [StudioCoreFallback] Используется минимальный fallback анализ для текста: {text[:40]}..."
        )
        
        # Return a minimal but valid result structure using DEFAULT_CONFIG values
        return {
            "emotions": {
                "neutral": 1.0,
                "dominant": "neutral"
            },
            "tlp": {
                "truth": 0.33,
                "love": 0.33,
                "pain": 0.33,
                "conscious_frequency": 0.5
            },
            "bpm": DEFAULT_CONFIG.FALLBACK_BPM,
            "key": DEFAULT_CONFIG.FALLBACK_KEY,
            "structure": {
                "sections": [text] if text else [],
                "section_count": 1 if text else 0,
                "layout": DEFAULT_CONFIG.FALLBACK_STRUCTURE
            },
            "style": {
                "genre": DEFAULT_CONFIG.FALLBACK_STYLE,
                "style": DEFAULT_CONFIG.FALLBACK_STYLE,
                "bpm": DEFAULT_CONFIG.FALLBACK_BPM,
                "key": DEFAULT_CONFIG.FALLBACK_KEY,
                "visual": DEFAULT_CONFIG.FALLBACK_VISUAL,
                "narrative": DEFAULT_CONFIG.FALLBACK_NARRATIVE,
                "structure": DEFAULT_CONFIG.FALLBACK_STRUCTURE,
                "emotion": DEFAULT_CONFIG.FALLBACK_EMOTION
            },
            "vocal": {
                "vocal_form": "solo",
                "gender": preferred_gender,
                "vocal_count": 1
            },
            "semantic_layers": {
                "layers": {
                    "sections": []
                }
            },
            "integrity": {
                "word_count": len(text.split()) if text else 0,
                "sentence_count": len([s for s in text.split('.') if s.strip()]) if text else 0,
                "status": "fallback_mode"
            },
            "annotated_text_ui": text if text else "",
            "annotated_text_suno": text if text else "",
            "color_wave": ["#808080"],  # Neutral gray
            "rde": {
                "resonance": 0.5,
                "fracture": 0.5,
                "entropy": 0.5
            },
            "_fallback_mode": True,
            "_status": "safe - mode"
        }


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
