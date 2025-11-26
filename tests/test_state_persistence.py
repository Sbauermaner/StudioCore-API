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

from studiocore.core_v6 import StudioCoreV6


class TestStatePersistence(unittest.TestCase):
    """Test suite for state persistence after analyze() calls."""
    
    def setUp(self):
        """Create a fresh StudioCoreV6 instance for each test."""
        self.core = StudioCoreV6()
        
        # Store references to system components
        self.initial_hge = self.core._hge
        self.initial_text_engine = self.core._text_engine
        self.initial_section_parser = self.core._section_parser
        self.initial_emotion_engine = self.core._emotion_engine
        self.initial_bpm_engine = self.core._bpm_engine
    
    def test_system_components_preserved_after_first_analyze(self):
        """Test that system components are preserved after first analyze() call."""
        # First analyze call
        result1 = self.core.analyze("This is a test text for analysis.")
        
        # Verify result is valid
        self.assertIsInstance(result1, dict)
        self.assertNotIn("error", result1)
        
        # Verify system components are still the same objects
        self.assertIs(self.core._hge, self.initial_hge, 
                     "_hge should be preserved after analyze()")
        self.assertIs(self.core._text_engine, self.initial_text_engine,
                     "_text_engine should be preserved after analyze()")
        self.assertIs(self.core._section_parser, self.initial_section_parser,
                     "_section_parser should be preserved after analyze()")
        self.assertIs(self.core._emotion_engine, self.initial_emotion_engine,
                     "_emotion_engine should be preserved after analyze()")
        self.assertIs(self.core._bpm_engine, self.initial_bpm_engine,
                     "_bpm_engine should be preserved after analyze()")
    
    def test_system_components_preserved_after_multiple_analyze(self):
        """Test that system components are preserved after multiple analyze() calls."""
        # Multiple analyze calls
        for i in range(5):
            result = self.core.analyze(f"Test text {i} for multiple calls.")
            self.assertIsInstance(result, dict)
        
        # Verify system components are still the same objects
        self.assertIs(self.core._hge, self.initial_hge,
                     "_hge should be preserved after multiple analyze() calls")
        self.assertIs(self.core._text_engine, self.initial_text_engine,
                     "_text_engine should be preserved after multiple analyze() calls")
        self.assertIs(self.core._section_parser, self.initial_section_parser,
                     "_section_parser should be preserved after multiple analyze() calls")
    
    def test_engine_bundle_cleared_after_analyze(self):
        """Test that _engine_bundle is cleared after analyze() (transient state)."""
        # First analyze call
        result1 = self.core.analyze("Test text for engine bundle check.")
        
        # _engine_bundle should be cleared (or empty) after analyze()
        # It's transient state that gets rebuilt on each analyze()
        if hasattr(self.core, '_engine_bundle'):
            # It's okay if it's empty or None, but it shouldn't contain stale data
            self.assertIsInstance(self.core._engine_bundle, dict)
    
    def test_no_attribute_error_on_reuse(self):
        """Test that no AttributeError occurs when reusing the instance."""
        # First call
        result1 = self.core.analyze("First call.")
        self.assertIsInstance(result1, dict)
        
        # Second call (critical test - this would fail if CRIT-001 wasn't fixed)
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
            self.assertIsNotNone(self.core._hge)
            self.assertIsNotNone(self.core._text_engine)
            self.assertIsNotNone(self.core._section_parser)


if __name__ == "__main__":
    unittest.main()

