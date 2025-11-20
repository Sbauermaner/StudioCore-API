from studiocore.suno_annotations import build_suno_annotations


def test_suno_emotion_adapter_basic():
    curve = {
        "dominant_cluster": "tender",
        "global_tlp": {"truth": 0.1, "love": 0.8, "pain": 0.1},
    }
    sections = [
        {"section": "verse", "intensity": 0.4, "hot_phrases": ["Любовь как тихий свет"]},
        {"section": "chorus", "intensity": 0.9, "hot_phrases": ["Сгорит душа"]},
    ]
    ann = build_suno_annotations("..", sections, curve)
    assert "vocal_profile" in ann
    assert "instrumentation" in ann
    assert "section_annotations" in ann
    assert "chorus" in ann["section_annotations"]

