# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

import math

from studiocore.emotion_genre_matrix import compute_genre_bias


def test_compute_genre_bias_neutral_vector():
    bias = compute_genre_bias({})

    assert all(math.isclose(val, 1.0) for val in bias.values())


def test_compute_genre_bias_variant_a_rules():
    vector = {"anger": 0.6, "sadness": 0.3, "awe": 0.1}
    bias = compute_genre_bias(vector)

    assert bias["rock_metal"] >= bias["jazz"]
    assert bias["gothic"] > bias["edm"]
    assert bias["orchestral"] >= bias["hip_hop"]
    assert all(0.0 <= val <= 1.0 for val in bias.values())

