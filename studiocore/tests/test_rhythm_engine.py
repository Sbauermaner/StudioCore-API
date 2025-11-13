import math

from ..rhythm import LyricMeter


def test_rhythm_analysis_respects_header_and_flags_conflict():
    text = """[BPM: 140]\n[Verse 1]\nмедленно тянутся влажные тяжёлые облака над головой и я пою без дыхания словно туман\nкаждый вздох растягивается на вечность и шаги звучат как эхо в пустых коридорах\n\n[Chorus]\nдай мне свет\nдай мне свет\nдай мне свет быстрее\n"""

    analysis = LyricMeter().analyze(text)

    assert math.isclose(analysis["global_bpm"], 140.0, rel_tol=0, abs_tol=0.5)
    assert analysis["conflict"]["has_conflict"] is True
    assert "VERSE_1" in analysis["sections"]
    assert analysis["sections"]["VERSE_1"]["mean_bpm"] < analysis["global_bpm"]
    assert len(analysis["sections"]["CHORUS_1"]["micro_curve"]) == analysis["sections"]["CHORUS_1"]["line_count"]


def test_rhythm_analysis_provides_section_dynamics():
    text = """[Verse]\nI walk along the river in a quiet solemn motion taking time with every breath\nMy thoughts are heavy stones that tumble softly under water far away from any rush\n\n[Chorus]\nRun now!\nRun now!\nRun with me into the neon night!\n"""

    analysis = LyricMeter().analyze(text)

    assert analysis["header_bpm"] is None
    assert set(analysis["sections"].keys()) == {"VERSE_1", "CHORUS_1"}

    verse_bpm = analysis["sections"]["VERSE_1"]["mean_bpm"]
    chorus_bpm = analysis["sections"]["CHORUS_1"]["mean_bpm"]
    assert chorus_bpm - verse_bpm > 15

    for section in analysis["sections"].values():
        assert len(section["micro_curve"]) == section["line_count"]
        assert section["tension"] >= 0.0
        assert section["phrase_pattern"]

    assert min(verse_bpm, chorus_bpm) <= analysis["global_bpm"] <= max(verse_bpm, chorus_bpm)
