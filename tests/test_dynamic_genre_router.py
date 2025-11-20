from studiocore.genre_router import DynamicGenreRouter


def test_dynamic_genre_router_basic_sanity():
    router = DynamicGenreRouter()

    base = {
        "bpm": {"estimate": 172},
        "style": {"key": "D#m"},
        "integrity": {"rhyme_density": 0.8, "narrative_pressure": 0.4},
        "tlp": {"pain": 0.9, "valence": -0.7, "arousal": 0.9},
        "emotion": {"label": "rage"},
    }

    macro, reason = router.route(base)
    assert macro in ("rock_metal", "gothic", "edm")
    assert reason == "dynamic_router"

    base["style"]["genre"] = "jazz"
    macro2, reason2 = router.route(base)
    assert macro2 == "jazz"
    assert reason2 == "user_override"
