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
