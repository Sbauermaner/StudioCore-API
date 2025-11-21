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
    assert "bpm" in result and result["bpm"]["estimate"]
    assert result["rde_summary"]
    assert result["language"]["language"]
    assert result["bpm"].get("section_annotations")
    assert result["bpm"].get("emotion_map", {}).get("target_bpm")
    assert result.get("fanf", {}).get("annotated_text_fanf")
    assert "choir_active" in result.get("fanf", {})


def test_core_v6_handles_missing_instrument_dynamics():
    core = StudioCoreV6()

    core.instrument_dynamics.map_instruments_to_structure = (
        lambda *args, **kwargs: None
    )

    result = core.analyze("Тестовый текст…")

    assert isinstance(result["suno_annotations"], list)


def test_core_v6_provides_diagnostics():
    core = StudioCoreV6()
    result = core.analyze("Тестовый текст")
    assert "diagnostics" in result
    assert isinstance(result["diagnostics"], dict)

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
