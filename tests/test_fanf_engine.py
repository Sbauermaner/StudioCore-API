from studiocore.fanf_annotation import FANFAnnotationEngine


def test_fanf_choir_activation_on_elevated_text():
    engine = FANFAnnotationEngine()
    analysis = {
        "emotion": {"curve": [0.2, 0.8], "profile": {"epic": 0.9}},
        "bpm": {"estimate": 128},
        "tonality": {"section_keys": ["Am"], "modal_shifts": ["aeolian"]},
        "style": {"genre": "cinematic", "mood": "dramatic"},
    }
    annotation = engine.build_annotations("sacred cathedral chorus", ["intro"], analysis)
    assert annotation.choir_active is True
    assert "ChoirLayers" in annotation.annotated_text_fanf


def test_fanf_choir_disabled_for_intimate_text():
    engine = FANFAnnotationEngine()
    analysis = {
        "emotion": {"curve": [0.1, 0.2], "profile": {"epic": 0.1}},
        "bpm": {"estimate": 90},
        "tonality": {"section_keys": ["C"], "modal_shifts": ["stable"]},
        "style": {"genre": "lofi", "mood": "intimate"},
    }
    annotation = engine.build_annotations("soft whisper under blankets", ["intro"], analysis)
    assert annotation.choir_active is False
    assert "No choir" in annotation.annotated_text_suno
