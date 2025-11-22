from studiocore.genre_universe_loader import load_genre_universe


def test_genre_universe_loader_basic_sets():
    U = load_genre_universe()

    # базовые sanity-check-и
    assert "rock" in U.music
    assert "drum_and_bass" in U.music
    assert "лирика" in U.lyric_forms
    assert "роман" in U.literary
    assert "трагедия" in U.drama
    assert "gothic_rock" in U.gothic
    assert "ukrainian_folk" in U.ethnic
