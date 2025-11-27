# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf-8 -*-
"""
StudioCore V6 - Adapter wrapper around monolith with v6 features
"""

from __future__ import annotations
import sys
from typing import Any, Dict, Optional

try:
    from . import get_core
    from .monolith_v4_3_1 import StudioCore as MonolithStudioCore
except ImportError:
    # Handle direct execution
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from studiocore import get_core
    from studiocore.monolith_v4_3_1 import StudioCore as MonolithStudioCore


class StudioCoreV6:
    """
    StudioCore V6 - Wrapper around monolith with v6 compatibility layer.
    Uses monolith as the underlying engine.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize StudioCoreV6 using monolith as backend."""
        try:
            # Try to get core via loader (prefers v6, falls back to monolith)
            self._core = get_core(prefer_v6=False)
        except Exception:
            # Fallback to monolith directly
            self._core = MonolithStudioCore(config_path)

        # Initialize v6-specific components if available
        try:
            from .hybrid_genre_engine import HybridGenreEngine

            self._hge = HybridGenreEngine()
        except ImportError:
            self._hge = None

    def analyze(
        self,
        text: str,
        preferred_gender: str = "auto",
        version: Optional[str] = None,
        semantic_hints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze text and return comprehensive results.
        Compatible with StudioCore monolith analyze() signature.
        """
        result = self._core.analyze(
            text=text,
            preferred_gender=preferred_gender,
            version=version,
            semantic_hints=semantic_hints,
        )
        
        # Дополнительно: Используем HybridGenreEngine для уточнения жанра
        if self._hge is not None and result.get("style"):
            style = result.get("style", {})
            genre = style.get("genre")
            if genre:
                try:
                    # Используем HybridGenreEngine для уточнения жанра
                    context = {
                        "emotions": result.get("emotions", {}),
                        "tlp": result.get("tlp", {}),
                        "bpm": result.get("bpm"),
                        "key": result.get("key"),
                    }
                    resolved_genre = self._hge.resolve(genre=genre, context=context)
                    if resolved_genre and isinstance(resolved_genre, str):
                        # Обновляем жанр в style, если он был уточнен
                        style["genre"] = resolved_genre
                        style["genre_source"] = "hybrid_genre_engine"
                        result["style"] = style
                except Exception as e:
                    # Логируем ошибку, но не прерываем выполнение
                    import logging
                    log = logging.getLogger(__name__)
                    log.warning(f"HybridGenreEngine.resolve() failed: {e}")
        
        return result


def main():
    """Self-test entry point for core_v6.py"""
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        print("=" * 80)
        print("StudioCore V6 Self-Test")
        print("=" * 80)
        print()

        try:
            core = StudioCoreV6()
            print("✅ StudioCoreV6 initialized successfully")
            print()

            # Test analyze with sample text
            test_text = "[Verse 1]\nTest lyrics for self-test"
            print("Testing analyze() with sample text...")
            result = core.analyze(test_text)

            if isinstance(result, dict):
                print("✅ analyze() returned valid dict")
                print(f"   Keys: {list(result.keys())[:10]}...")
            else:
                print(f"⚠️  analyze() returned unexpected type: {type(result)}")

            print()
            print("=" * 80)
            print("✅ Self-test completed successfully")
            print("=" * 80)
            return 0

        except Exception as e:
            print(f"❌ Self-test failed: {e}")
            import traceback

            traceback.print_exc()
            return 1
    else:
        print("Usage: python3 studiocore/core_v6.py --selftest")
        return 1


if __name__ == "__main__":
    sys.exit(main())
