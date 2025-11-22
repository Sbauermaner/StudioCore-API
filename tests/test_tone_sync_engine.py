from studiocore.tone_sync import ToneSyncEngine


def test_tone_sync_warm_minor():
    engine = ToneSyncEngine()
    tone = engine.pick_profile(
        bpm=80,
        key="D minor",
        tlp={"truth": 0.6, "love": 0.7, "pain": 0.5},
        emotion_matrix={"sadness": 0.7},
    )
    assert tone["name"] in ("warm_minor", "cold_minor")
    assert tone["bpm"] == 80


def test_tone_sync_chaotic_dark():
    engine = ToneSyncEngine()
    tone = engine.pick_profile(
        bpm=140,
        key="G minor",
        tlp={"truth": 0.4, "love": 0.2, "pain": 0.9},
        emotion_matrix={"anger": 0.8},
    )
    assert tone["name"] == "chaotic_dark"
