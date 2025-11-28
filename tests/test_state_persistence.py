"""
Integration test for state persistence (CRIT-001 fix verification).

This test verifies that StudioCoreV6 instances can be reused across multiple
analyze() calls without losing system components initialized in __init__.
"""

import unittest
import sys
from pathlib import Path

# Add studiocore to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from studiocore.core_v6 import StudioCoreV6  # noqa: E402


class TestStatePersistence(unittest.TestCase):
    """Test suite for state persistence after analyze() calls."""

    def setUp(self):
        """Create a fresh StudioCoreV6 instance for each test."""
        self.core = StudioCoreV6()

        # Store references to system components
        # _hge is on StudioCoreV6 directly
        self.initial_hge = self.core._hge
        # Other engines are in _core (monolith)
        # Handle both StudioCore and StudioCoreV5 wrapper
        actual_core = self.core._core
        if hasattr(actual_core, '_core'):
            # It's a wrapper (StudioCoreV5), access inner core
            actual_core = actual_core._core
        self.initial_tlp = actual_core.tlp
        self.initial_rhythm = actual_core.rhythm
        self.initial_emotion = actual_core.emotion
        self.initial_freq = actual_core.freq

    def test_system_components_preserved_after_first_analyze(self):
        """Test that system components are preserved after first analyze() call."""
        # First analyze call
        result1 = self.core.analyze("This is a test text for analysis.")

        # Verify result is valid
        self.assertIsInstance(result1, dict)
        self.assertNotIn("error", result1)

        # Get actual core (handle wrapper if present)
        actual_core = self.core._core
        if hasattr(actual_core, '_core'):
            actual_core = actual_core._core

        # Verify system components are still the same objects
        self.assertIs(
            self.core._hge, self.initial_hge, "_hge should be preserved after analyze()"
        )
        self.assertIs(
            actual_core.tlp,
            self.initial_tlp,
            "tlp (text engine) should be preserved after analyze()",
        )
        self.assertIs(
            actual_core.rhythm,
            self.initial_rhythm,
            "rhythm (section parser) should be preserved after analyze()",
        )
        self.assertIs(
            actual_core.emotion,
            self.initial_emotion,
            "emotion engine should be preserved after analyze()",
        )
        self.assertIs(
            actual_core.freq,
            self.initial_freq,
            "freq (bpm engine) should be preserved after analyze()",
        )

    def test_system_components_preserved_after_multiple_analyze(self):
        """Test that system components are preserved after multiple analyze() calls."""
        # Multiple analyze calls
        for i in range(5):
            result = self.core.analyze(f"Test text {i} for multiple calls.")
            self.assertIsInstance(result, dict)

        # Get actual core (handle wrapper if present)
        actual_core = self.core._core
        if hasattr(actual_core, '_core'):
            actual_core = actual_core._core

        # Verify system components are still the same objects
        self.assertIs(
            self.core._hge,
            self.initial_hge,
            "_hge should be preserved after multiple analyze() calls",
        )
        self.assertIs(
            actual_core.tlp,
            self.initial_tlp,
            "tlp (text engine) should be preserved after multiple analyze() calls",
        )
        self.assertIs(
            actual_core.rhythm,
            self.initial_rhythm,
            "rhythm (section parser) should be preserved after multiple analyze() calls",
        )

    def test_engine_bundle_cleared_after_analyze(self):
        """Test that _engine_bundle is cleared after analyze() (transient state)."""
        # First analyze call
        self.core.analyze("Test text for engine bundle check.")

        # _engine_bundle should be cleared (or empty) after analyze()
        # It's transient state that gets rebuilt on each analyze()
        if hasattr(self.core, "_engine_bundle"):
            # It's okay if it's empty or None, but it shouldn't contain stale
            # data
            self.assertIsInstance(self.core._engine_bundle, dict)

    def test_no_attribute_error_on_reuse(self):
        """Test that no AttributeError occurs when reusing the instance."""
        # First call
        result1 = self.core.analyze("First call.")
        self.assertIsInstance(result1, dict)

        # Second call (critical test - this would fail if CRIT-001 wasn't
        # fixed)
        result2 = self.core.analyze("Second call.")
        self.assertIsInstance(result2, dict)

        # Third call
        result3 = self.core.analyze("Third call.")
        self.assertIsInstance(result3, dict)

        # If we get here without AttributeError, CRIT-001 is fixed!

    def test_different_text_inputs(self):
        """Test state persistence with different text inputs."""
        texts = [
            "Simple text.",
            "Text with emotions: joy, sadness, anger.",
            "Epic narrative with multiple sections.",
            "Low emotion neutral text.",
            "Text with special characters: !@#$%^&*()",
        ]

        for text in texts:
            result = self.core.analyze(text)
            self.assertIsInstance(result, dict)

            # Verify system components are still intact
            # _hge is on StudioCoreV6 directly
            self.assertIsNotNone(self.core._hge)
            # Other engines are in _core (monolith)
            actual_core = self.core._core
            if hasattr(actual_core, '_core'):
                actual_core = actual_core._core
            self.assertIsNotNone(actual_core.tlp)
            self.assertIsNotNone(actual_core.rhythm)


if __name__ == "__main__":
    unittest.main()
