# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.bpm_engine import BPMEngine


TEXT = "the night is young and every light keeps pulsing"


def test_bpm_engine_describe_returns_curve():
    engine = BPMEngine()
    payload = engine.describe(TEXT)
    assert payload["estimate"] > 0
    assert isinstance(payload["curve"], list)
    assert "poly_rhythm" in payload
