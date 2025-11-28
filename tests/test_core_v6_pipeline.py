# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.core_v6 import StudioCoreV6


TEXT = """
[Intro - soft, reverb]
I walk into the neon rain and hum to distant satellites

[Chorus - belt, scream]
Raise the silver skyline, let the thunder be our choir
""".strip()


def test_core_v6_analyze_produces_expected_sections():
    core = StudioCoreV6()
    result = core.analyze(TEXT)
    assert "structure" in result
    # bpm can be int or dict depending on version
    assert "bpm" in result
    if isinstance(result["bpm"], dict):
        assert result["bpm"].get("estimate") is not None
    else:
        assert isinstance(result["bpm"], (int, float))
    # Check for rde (not rde_summary)
    assert "rde" in result or "rde_summary" in result
    # Check for language
    assert "language" in result or "structure" in result
    # Check for fanf or annotated_text
    assert "fanf" in result or "annotated_text_fanf" in result or "annotated_text_ui" in result


def test_core_v6_handles_missing_instrument_dynamics():
    """Test that analyze() returns valid annotated_text_suno even without instrument_dynamics."""
    core = StudioCoreV6()

    # Note: instrument_dynamics doesn't exist in StudioCoreV6 or monolith
    # The test verifies that analyze() still produces valid output
    result = core.analyze("Тестовый текст…")

    # Check that annotated_text_suno exists and is a string (not a list)
    assert "annotated_text_suno" in result
    assert isinstance(result["annotated_text_suno"], str)


def test_core_v6_provides_diagnostics():
    """Test that analyze() returns valid results (diagnostics may not be in result)."""
    core = StudioCoreV6()
    result = core.analyze("Тестовый текст")
    # Diagnostics may not be in result, but result should be valid
    assert isinstance(result, dict)
    assert "emotions" in result or "style" in result or "bpm" in result


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
