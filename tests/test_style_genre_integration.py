# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.genre_weights import GenreWeightsEngine
from studiocore.genre_universe_loader import load_genre_universe


def test_gothic_detection_prefers_gothic_domain():
    universe = load_genre_universe()
    info = universe.detect_domain("gothic_poetry")

    assert info["domain"] in {"gothic", "literature"}
    assert info["canonical"] == "gothic_poetry"


def test_edm_features_pick_electronic_domain():
    engine = GenreWeightsEngine()
    genre = engine.infer_genre({
        "electronic_pressure": 0.9,
        "rhythm_density": 0.7,
        "power": 0.6,
    })

    assert genre in engine._genres_for_domain("electronic")


def test_lyrical_features_pick_lyric_forms():
    engine = GenreWeightsEngine()
    genre = engine.infer_genre({
        "lyrical_emotion_score": 0.9,
        "narrative_pressure": 0.8,
        "emotional_gradient": 0.7,
        "hl_major": 0.3,
    })

    assert genre in engine._genres_for_domain("lyrical")

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
