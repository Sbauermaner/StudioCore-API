# -*- coding: utf-8 -*-
"""Tests for the style prompt builder and color exposure logic."""

import unittest

from studiocore.core_v6 import StudioCoreV6
from studiocore.logical_engines import StyleEngine
from studiocore.user_override_manager import UserOverrideManager, UserOverrides


class TestStylePromptFormatting(unittest.TestCase):
    def setUp(self):
        self.engine = StyleEngine()

    def test_prompt_is_wrapped_and_hides_visual_by_default(self):
        prompt = self.engine.final_style_prompt_build(
            genre="indie pop",
            mood="reflective",
            instrumentation="minimal instrumentation",
            vocal="airy tenor",
            visual=None,
            tone="minor arc",
        )
        self.assertTrue(prompt.startswith("[("))
        self.assertTrue(prompt.endswith("[END]"))
        self.assertNotIn("VISUALS", prompt)

    def test_prompt_can_include_visuals(self):
        prompt = self.engine.final_style_prompt_build(
            genre="cinematic",
            mood="dramatic",
            instrumentation="strings",
            vocal="power belt",
            visual="aurora gradients",
            tone="modal shift",
        )
        self.assertIn("(VISUALS: aurora gradients)", prompt)


class TestColorExposureLogic(unittest.TestCase):
    def setUp(self):
        self.core = StudioCoreV6()

    def test_exposes_color_when_user_override_specified(self):
        overrides = UserOverrides(color_state="gold")
        manager = UserOverrideManager(overrides)
        self.assertTrue(self.core._should_expose_color_visuals({}, manager))

    def test_exposes_color_when_hint_requests_it(self):
        manager = UserOverrideManager()
        hints = {"color": {"expose_in_prompt": True}}
        self.assertTrue(self.core._should_expose_color_visuals(hints, manager))

    def test_hides_color_by_default(self):
        manager = UserOverrideManager()
        self.assertFalse(self.core._should_expose_color_visuals({}, manager))


if __name__ == "__main__":
    unittest.main()
