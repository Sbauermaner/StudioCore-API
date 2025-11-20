def test_genre_universe_adapter_smoke():
    from studiocore.genre_universe_adapter import GenreUniverseAdapter

    adapter = GenreUniverseAdapter()
    dummy_result = {}

    res = adapter.resolve("rock_metal", dummy_result)
    assert res.macro_genre == "rock_metal"
    assert isinstance(res.subgenre, str)
    assert isinstance(res.tags, list)
    assert res.source in ("universe_v2", "fallback_table", "fallback_minimal")
