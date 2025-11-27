from studiocore.monolith_v4_3_1 import StudioCore


def _build_section(tag: str, bpm: int = 120, key: str = "C"):
    return {
        "tag": tag,
        "mood": "calm",
        "energy": "medium",
        "arrangement": "full",
        "bpm": bpm,
        "key": key,
    }


def _extract_tags(suno_text: str, block_count: int):
    lines = suno_text.splitlines()
    return [lines[i * 3].lstrip("[").split(" - ", 1)[0] for i in range(block_count)]


def _default_sections():
    return [
        _build_section("Intro"),
        _build_section("Verse"),
        _build_section("Chorus"),
        _build_section("Bridge"),
        _build_section("Outro"),
    ]


def test_single_block_prioritizes_outro():
    core = StudioCore.__new__(StudioCore)

    annotated_ui, annotated_suno = core.annotate_text(
        ["one block"],
        [{}],
        _default_sections(),
    )

    assert annotated_ui  # sanity check output is produced
    assert _extract_tags(annotated_suno, 1) == ["INTRO"]


def test_long_sequence_repeats_verse_chorus_and_ends_with_outro():
    core = StudioCore.__new__(StudioCore)
    text_blocks = [f"line {i}" for i in range(9)]

    annotated_ui, annotated_suno = core.annotate_text(
        text_blocks,
        [{} for _ in text_blocks],
        _default_sections(),
    )

    assert annotated_ui  # sanity check output is produced
    assert _extract_tags(annotated_suno, len(text_blocks)) == [
        "INTRO",
        "VERSE",
        "PRE-CHORUS",
        "CHORUS",
        "VERSE",
        "BRIDGE",
        "CHORUS",
        "OUTRO",
        "VERSE",
    ]
