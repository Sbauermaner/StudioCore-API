from studiocore.genre_universe_loader import load_genre_universe


def test_universe_counts():
    universe = load_genre_universe()

    assert len(universe.music_genres) >= 40
    assert len(universe.edm_genres) >= 20
    assert len(universe.lyric_forms) >= 15
    assert len(universe.literature_styles) >= 15
    assert len(universe.dramatic_genres) >= 8
    assert len(universe.comedy_genres) >= 8
    assert len(universe.gothic_styles) >= 8
    assert len(universe.ethnic_schools) >= 8
    assert len(universe.hybrids) >= 6


def test_resolve_and_detect_domain():
    universe = load_genre_universe()

    assert universe.resolve("drum and bass") == "drum_and_bass"
    assert universe.detect_domain("DnB")["type"] == "edm"

    assert universe.resolve("элегия") == "elegy"
    assert universe.detect_domain("элегия")["domain"] == "literature"

    gothic_info = universe.detect_domain("gothic_rock")
    assert gothic_info["domain"] == "music"

    hybrid_info = universe.detect_domain("tribal_techno")
    assert hybrid_info["type"] in {"hybrid", "music", "edm"}
