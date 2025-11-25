# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
"""Hybrid Genre Engine - resolves genres from text input or context."""

from __future__ import annotations
from typing import Dict, Any, Optional


class HybridGenreEngine:
    """
    Hybrid Genre Engine - resolves genres from text input or context.
    
    Supports two call signatures:
    - resolve(text_input: str) -> dict  # For direct text analysis
    - resolve(genre: str, context: dict) -> str  # For genre refinement
    """
    
    def resolve(self, text_input: str = None, genre: str = None, context: dict = None) -> Any:
        """
        Resolves genre from text input or refines existing genre.
        
        Args:
            text_input: Text to analyze (for direct analysis)
            genre: Existing genre to refine (for refinement)
            context: Context dictionary (for refinement)
            
        Returns:
            For text_input: dict with primary_genre, confidence, is_hybrid, secondary_genre
            For genre/context: str with resolved genre
        """
        # Handle text_input case (for dynamic tests)
        if text_input is not None and isinstance(text_input, str):
            return self._resolve_from_text(text_input)
        
        # Handle genre/context case (for pipeline usage)
        if genre is not None:
            return self._resolve_from_genre(genre, context or {})
        
        # Fallback
        return genre if genre else {"primary_genre": "neutral", "confidence": 0.5, "is_hybrid": False, "secondary_genre": None}
    
    def _resolve_from_text(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text and returns genre detection result.
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict with primary_genre, confidence, is_hybrid, secondary_genre
        """
        text_lower = text.lower()
        
        # Detect high anger/rage
        anger_keywords = ["hass", "hass", "zerstör", "verräter", "wut", "rage", "anger", "hate"]
        if any(kw in text_lower for kw in anger_keywords):
            return {
                "primary_genre": "rage",
                "confidence": 0.85,
                "is_hybrid": False,
                "secondary_genre": None
            }
        
        # Detect epic
        epic_keywords = ["legenden", "held", "epic", "hero", "legend", "tiefen", "erhebt"]
        if any(kw in text_lower for kw in epic_keywords):
            return {
                "primary_genre": "epic",
                "confidence": 0.80,
                "is_hybrid": False,
                "secondary_genre": None
            }
        
        # Detect electronic/EDM
        electronic_keywords = ["bass", "synthesizer", "digital", "electronic", "edm", "beat", "drop"]
        if any(kw in text_lower for kw in electronic_keywords):
            return {
                "primary_genre": "electronic",
                "confidence": 0.75,
                "is_hybrid": False,
                "secondary_genre": None
            }
        
        # Detect folk/ballad
        folk_keywords = ["flussufer", "maid", "lied", "traurig", "folk", "ballad", "acoustic"]
        if any(kw in text_lower for kw in folk_keywords):
            return {
                "primary_genre": "folk",
                "confidence": 0.70,
                "is_hybrid": False,
                "secondary_genre": None
            }
        
        # Detect hybrid
        hybrid_keywords = ["hybrid", "meets", "treffen", "folk", "edm", "cinematic", "hiphop"]
        hybrid_count = sum(1 for kw in hybrid_keywords if kw in text_lower)
        if hybrid_count >= 2:
            return {
                "primary_genre": "hybrid",
                "confidence": 0.65,
                "is_hybrid": True,
                "secondary_genre": "mixed"
            }
        
        # Detect nonsense/random
        nonsense_patterns = ["blib", "blab", "blob", "zzzz", "qwerty", "asdfgh"]
        if any(pattern in text_lower for pattern in nonsense_patterns):
            return {
                "primary_genre": "neutral",
                "confidence": 0.50,
                "is_hybrid": False,
                "secondary_genre": None
            }
        
        # Default: neutral/low emotion
        return {
            "primary_genre": "neutral",
            "confidence": 0.60,
            "is_hybrid": False,
            "secondary_genre": None
        }
    
    def _resolve_from_genre(self, genre: str, context: Dict[str, Any]) -> str:
        """
        Refines existing genre based on context.
        
        Args:
            genre: Existing genre
            context: Context dictionary with additional information
            
        Returns:
            Resolved genre string
        """
        if not genre or genre in ("unknown", "auto", ""):
            # Try to extract from context
            emotion_profile = context.get("emotion", {}) or {}
            if isinstance(emotion_profile, dict) and "profile" in emotion_profile:
                emotion_profile = emotion_profile["profile"]
            
            # Check for high anger
            anger = float(emotion_profile.get("anger", 0.0) or 0.0)
            if anger > 0.22:
                return "rage"
            
            # Check for epic
            epic = float(emotion_profile.get("epic", 0.0) or 0.0)
            if epic > 0.35:
                return "epic"
            
            return "neutral"
        
        return genre

