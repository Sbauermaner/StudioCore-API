# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.rde_engine import RDESnapshot, RhythmDynamicsEmotionEngine


BPM_PAYLOAD = {
    "estimate": 118.0,
    "emotion_map": {"map": {"truth": 110.0, "love": 118.0, "pain": 132.0}},
}
BREATH = {"sync_score": 0.72}
EMOTIONS = {"truth": 0.6, "love": 0.3, "pain": 0.1}
INSTRUMENTS = {"palette": ["pads", "synth bass"]}


def test_rde_engine_compose_returns_snapshot():
    engine = RhythmDynamicsEmotionEngine()
    snapshot = engine.compose(
        bpm_payload=BPM_PAYLOAD,
        breathing_profile=BREATH,
        emotion_profile=EMOTIONS,
        instrumentation_payload=INSTRUMENTS,
    )
    assert isinstance(snapshot, RDESnapshot)
    assert snapshot.dominant_emotion == "truth"
    assert snapshot.target_bpm == BPM_PAYLOAD["estimate"]
    assert "pads" in (snapshot.palette or [])
    assert snapshot.breath_sync == BREATH["sync_score"]


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
