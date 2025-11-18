from studiocore.section_parser import SectionParser


EXAMPLE_TEXT = """
[Intro - soft, reverb]
we fall into the silver snow
[Chorus - belt, scream]
raise the light above the noise
""".strip()


def test_section_parser_detects_annotations():
    parser = SectionParser()
    result = parser.parse(EXAMPLE_TEXT)
    assert result.sections
    assert result.annotations
    adjustments = parser.apply_annotation_effects(
        emotions={"joy": 0.4, "sadness": 0.2},
        bpm=120,
        annotations=result.annotations,
    )
    assert adjustments["bpm"] >= 120
    assert adjustments["annotations"] == result.annotations
