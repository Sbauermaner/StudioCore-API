# MASTER_PATCH_V5_SKELETON: GenreConflictResolver (NO - OP)
# Task 17.3: Implement Color-Key conflict resolution

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .genre_colors import get_key_from_emotion_color


class GenreConflictResolver:
    """
    Resolves conflicts between genre, color, and key.
    
    Task 17.3: Prioritize Color-implied keys if the detected Key contradicts
    the dominant emotional color (reference EMOTION_COLOR_TO_KEY table).
    """

    def resolve(self, genre: str, payload: Dict[str, Any]) -> str:  # noqa: ARG002
        """
        Resolve genre conflicts.
        
        Future: prioritize overrides > fusion > legacy > matrix > fallback
        
        Args:
            genre: Current genre string
            payload: Additional payload data (reserved for future use)
        """
        return genre

    def resolve_color_key_conflict(
        self,
        detected_key: str,
        color_wave: Optional[List[str]],
        style_payload: Optional[Dict[str, Any]] = None,  # noqa: ARG002
    ) -> Tuple[Optional[str], bool]:
        """
        Task 17.3: Suggest a Key change if it conflicts with the established Color emotion.
        
        Rules from KONFLIKTE_UND_PROZESSE.md:
        - If Key not in list of preferred keys for color → select first from list
        - Priority: Color → Key (color determines preferred keys)
        
        Args:
            detected_key: The currently detected key (e.g., "C major", "A minor")
            color_wave: List of color hex codes (first is dominant)
            style_payload: Optional style payload for additional context
        
        Returns:
            Tuple of (suggested_key, was_resolved)
        """
        if not color_wave or len(color_wave) == 0:
            return None, False

        # Extract dominant color (first color in wave)
        dominant_color = color_wave[0]

        # Get preferred keys for this color from EMOTION_COLOR_TO_KEY
        preferred_keys = get_key_from_emotion_color(dominant_color)

        if not preferred_keys:
            return None, False

        # Normalize detected key for comparison
        detected_key_normalized = self._normalize_key(detected_key)

        # Check if detected key is in preferred keys list
        preferred_keys_normalized = [self._normalize_key(k) for k in preferred_keys]

        if detected_key_normalized in preferred_keys_normalized:
            # No conflict - key is already in preferred list
            return None, False

        # Conflict detected - suggest first preferred key
        suggested_key = preferred_keys[0]
        return suggested_key, True

    def _normalize_key(self, key: str) -> str:
        """
        Normalize key string for comparison.
        
        Examples:
            "C major" -> "c major"
            "A minor" -> "a minor"
            "C (C minor)" -> "c minor"
        """
        if not key:
            return ""

        # Convert to lowercase
        normalized = key.lower().strip()

        # Handle formats like "C (C minor)" -> extract "C minor"
        if "(" in normalized and ")" in normalized:
            # Extract content in parentheses
            start = normalized.find("(") + 1
            end = normalized.find(")")
            if start > 0 and end > start:
                normalized = normalized[start:end].strip()

        return normalized
