"""
Integration tests for StudioCore V7 - Production Ready Candidate

Tests critical functionality:
- State persistence
- Engine initialization
- Configuration loading
- Multiple analyze() calls
"""

import unittest
import sys
from pathlib import Path

# Add studiocore to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from studiocore.core_v6 import StudioCoreV6
from studiocore.config import (
    GENRE_WEIGHTS,
    GENRE_THRESHOLDS,
    ROAD_NARRATIVE_KEYWORDS,
    FOLK_BALLAD_KEYWORDS,
    load_config_weights,
)


class TestIntegrationV7(unittest.TestCase):
    """Integration tests for V7 production readiness."""
    
    def setUp(self):
        """Create a fresh StudioCoreV6 instance for each test."""
        self.core = StudioCoreV6()
    
    def test_state_persistence(self):
        """Test that state is preserved across multiple analyze() calls."""
        # First call
        result1 = self.core.analyze("Test text for state persistence.")
        self.assertIsInstance(result1, dict)
        
        # Verify system components are preserved
        self.assertIsNotNone(self.core._hge, "_hge should be preserved")
        self.assertIsNotNone(self.core._text_engine, "_text_engine should be preserved")
        self.assertIsNotNone(self.core._emotion_engine, "_emotion_engine should be preserved")
        
        # Second call (critical test)
        result2 = self.core.analyze("Another test text.")
        self.assertIsInstance(result2, dict)
        
        # Verify components are still intact
        self.assertIsNotNone(self.core._hge, "_hge should still be preserved")
        self.assertIsNotNone(self.core._text_engine, "_text_engine should still be preserved")
    
    def test_engine_initialization(self):
        """Test that engines are initialized once in __init__."""
        # Verify engines are initialized
        self.assertIsNotNone(self.core._text_engine)
        self.assertIsNotNone(self.core._emotion_engine)
        self.assertIsNotNone(self.core._bpm_engine)
        self.assertIsNotNone(self.core._section_parser)
        
        # Verify engines are reused (same object references)
        engines1 = self.core._text_engine
        result = self.core.analyze("Test")
        engines2 = self.core._text_engine
        
        self.assertIs(engines1, engines2, "Engines should be reused, not re-instantiated")
    
    def test_configuration_loading(self):
        """Test that configuration is loaded correctly."""
        # Test hardcoded values
        self.assertIn("semantic_aggression", GENRE_WEIGHTS)
        self.assertIn("poetic_density", GENRE_WEIGHTS)
        self.assertIn("road_narrative_score_min", GENRE_THRESHOLDS)
        
        # Test external config loading
        external_config = load_config_weights("config_weights.json")
        if external_config:
            self.assertIn("genre_weights", external_config)
            self.assertIn("keywords", external_config)
            self.assertIn("thresholds", external_config)
    
    def test_keyword_structures(self):
        """Test that keyword structures are correct."""
        # Road narrative should be a dict
        self.assertIsInstance(ROAD_NARRATIVE_KEYWORDS, dict)
        self.assertIn("road", ROAD_NARRATIVE_KEYWORDS)
        self.assertIn("death", ROAD_NARRATIVE_KEYWORDS)
        
        # Folk ballad should be a dict with ru/en
        self.assertIsInstance(FOLK_BALLAD_KEYWORDS, dict)
        self.assertIn("ru", FOLK_BALLAD_KEYWORDS)
        self.assertIn("en", FOLK_BALLAD_KEYWORDS)
    
    def test_multiple_analyze_calls(self):
        """Test multiple analyze() calls with different texts."""
        texts = [
            "Simple test text.",
            "Text with emotions: joy, sadness, anger.",
            "Epic narrative with multiple sections.",
        ]
        
        for text in texts:
            result = self.core.analyze(text)
            self.assertIsInstance(result, dict)
            self.assertIn("style", result)
            
            # Verify state is preserved
            self.assertIsNotNone(self.core._hge)
            self.assertIsNotNone(self.core._text_engine)
    
    def test_genre_weights_structure(self):
        """Test that genre weights have correct structure."""
        required_weights = [
            "semantic_aggression",
            "power_vector",
            "edge_factor",
            "poetic_density",
            "swing_ratio",
            "jazz_complexity",
            "electronic_pressure",
        ]
        
        for weight_name in required_weights:
            self.assertIn(weight_name, GENRE_WEIGHTS, f"{weight_name} should be in GENRE_WEIGHTS")
            self.assertIsInstance(GENRE_WEIGHTS[weight_name], dict)
    
    def test_thresholds_structure(self):
        """Test that thresholds have correct values."""
        self.assertGreaterEqual(GENRE_THRESHOLDS["road_narrative_score_min"], 0.0)
        self.assertLessEqual(GENRE_THRESHOLDS["road_narrative_score_min"], 1.0)
        self.assertGreaterEqual(GENRE_THRESHOLDS["rage_mode_anger_min"], 0.0)
        self.assertLessEqual(GENRE_THRESHOLDS["rage_mode_anger_min"], 1.0)


if __name__ == "__main__":
    unittest.main()

