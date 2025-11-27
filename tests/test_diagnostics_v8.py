# -*- coding: utf-8 -*-
"""Basic sanity checks for Diagnostics v8.0 schema."""

from __future__ import annotations

from typing import Any, Dict

from studiocore.core_v6 import StudioCoreV6


def _run_simple_analysis(
    text: str = "Тестовая строка для диагностики.",
) -> Dict[str, Any]:
    engine = StudioCoreV6()
    result = engine.analyze(text)
    assert isinstance(result, dict)
    assert result.get("engine") == "StudioCoreV6"
    return result


def test_diagnostics_v8_schema_present() -> None:
    result = _run_simple_analysis()
    diagnostics = result.get("diagnostics")
    assert isinstance(diagnostics, dict)

    # New schema marker
    assert diagnostics.get("diagnostic_schema") == "v8.0"

    # Structured blocks must exist
    assert "engines" in diagnostics
    assert "summary_blocks" in diagnostics
    assert "meta" in diagnostics


def test_diagnostics_v8_engines_block_shape() -> None:
    result = _run_simple_analysis()
    diagnostics = result["diagnostics"]
    engines = diagnostics.get("engines")
    assert isinstance(engines, dict)

    # engines block may be partially filled, but must be a dict
    # and safe to access typical keys
    for key in ("bpm", "tlp", "genre", "tone", "frequency"):
        _ = engines.get(key, None)  # access should not raise


def test_diagnostics_v8_consistency_block_optional() -> None:
    result = _run_simple_analysis()
    diagnostics = result["diagnostics"]

    # Consistency block may or may not be present,
    # but if it exists, it must be a dict with basic keys.
    consistency = diagnostics.get("consistency")
    if consistency is not None:
        assert isinstance(consistency, dict)
        for key in (
            "bpm_matches_tlp",
            "genre_matches_emotion",
            "tone_bpm_coherence",
            "structure_coherence",
        ):
            assert key in consistency
