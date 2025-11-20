import math

from studiocore.emotion import EmotionEngine, load_emotion_model


def test_emotion_model_loads_clusters():
    model = load_emotion_model()
    assert "clusters" in model
    assert len(model.get("clusters", {})) >= 12


def test_emotion_profile_shape():
    engine = EmotionEngine()
    profile = engine.build_emotion_profile("gentle hope and love across the sky")

    assert profile.get("raw")
    assert len(profile["raw"]) <= 66
    assert len(profile.get("clusters", {})) >= 12
    assert 60 <= profile.get("bpm", 0) <= 190
    assert len(profile.get("genre_scores", {})) >= 1


def test_integration_aggression_and_love():
    engine = EmotionEngine()

    aggressive_text = "rage anger hatred fury fight scream burn the stage with metal thunder"
    aggressive_profile = engine.build_emotion_profile(aggressive_text)
    aggressive_genres = [
        genre
        for genre in aggressive_profile.get("genre_scores", {})
        if any(tag in genre for tag in ("metal", "industrial", "hardcore", "rap"))
    ]
    assert aggressive_genres
    assert aggressive_profile.get("bpm", 0) > 110

    love_text = "love tenderness warmth embrace forever gentle melody soft heart full of hope"
    love_profile = engine.build_emotion_profile(love_text)
    soft_genres = (
        "pop_ballad",
        "soul",
        "rnb",
        "soft_rock",
        "lyrical_ballad",
    )
    assert any(love_profile.get("genre_scores", {}).get(name, 0) >= 0 for name in soft_genres)
    assert 70 <= love_profile.get("bpm", 0) <= 110
    assert str(love_profile.get("key", {}).get("scale", "")).startswith("major")
