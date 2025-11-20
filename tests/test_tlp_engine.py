# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.tlp_engine import TruthLovePainEngine


TEXT = "When the city whispers I still carry the fire inside"


def test_tlp_engine_describe_returns_dominant_axis():
    engine = TruthLovePainEngine()
    profile = engine.describe(TEXT)
    assert {"truth", "love", "pain"}.issubset(profile.keys())
    assert profile["dominant_axis"] in profile
    assert "balance" in profile

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
