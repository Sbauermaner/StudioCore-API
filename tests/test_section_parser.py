# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

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


def test_section_parser_prefers_strict_boundary_only_for_extreme_rde():
    parser = SectionParser()

    calm_result = parser.parse("soft glow\nwhisper in the snow")
    assert calm_result.prefer_strict_boundary is False

    intense_lines = "\n".join(["TOTAL PANIC!!!"] * 18)
    intense_result = parser.parse(intense_lines)
    assert intense_result.prefer_strict_boundary is True

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
