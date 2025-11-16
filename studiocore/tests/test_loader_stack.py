# -*- coding: utf-8 -*-
"""Focused tests for the StudioCore loader stack."""

import unittest

from studiocore import (
    StudioCore,
    StudioCoreFallback,
    StudioCoreV6,
    get_core,
    loader_diagnostics,
)


class TestLoaderStack(unittest.TestCase):
    def test_default_loader_returns_v6(self):
        core = get_core()
        self.assertIsInstance(core, StudioCoreV6)
        self.assertIsInstance(StudioCore(), StudioCoreV6)

    def test_loader_diagnostics_structure(self):
        diag = loader_diagnostics()
        self.assertIn("available", diag)
        self.assertTrue(any(item["key"] == "v6" for item in diag["available"]))
        self.assertIn("monolith", diag)
        self.assertIn("module", diag["monolith"])

    def test_forced_fallback(self):
        core = get_core(preferred_stack=("missing", "fallback"))
        self.assertIsInstance(core, StudioCoreFallback)
        self.assertTrue(getattr(core, "is_fallback", False))


if __name__ == "__main__":
    unittest.main()
