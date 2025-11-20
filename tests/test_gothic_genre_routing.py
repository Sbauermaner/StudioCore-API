# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.core_v6 import StudioCoreV6


GOTHIC_TEXT = """
[Intro]
В неоне готика — это готика, мрак и шёпот света.

[Verse]
Я падаю в соборы тени, рифмы режут, строфы дышат.

[Chorus]
Это готика! Это готика!
Это готика! Это готика!
""".strip()


def test_gothic_material_not_classified_as_edm():
    core = StudioCoreV6()
    result = core.analyze(
        GOTHIC_TEXT,
        semantic_hints={"target_bpm": 95, "tonality": {"key": "B (B minor)"}},
    )

    style = result.get("style", {})
    assert style.get("genre") != "edm"
    assert style.get("domain_genre", style.get("genre")) != "edm"

    bpm_estimate = result.get("bpm", {}).get("estimate")
    assert bpm_estimate and abs(float(bpm_estimate) - 95) < 5

    tonality = result.get("tonality", {})
    assert tonality.get("mode") == "minor"

    sections = result.get("structure", {}).get("sections", [])
    assert sections and not (len(sections) == 1 and "BODY" in sections)

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
