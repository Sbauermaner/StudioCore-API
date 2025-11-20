# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from studiocore.section_intelligence import SectionIntelligence
from studiocore.emotion import EmotionEngine


def test_section_emotion_wave_basic():
    text = """[Verse]
    Как лошадь, загнанная в мыле
    Любовь светает в тишине
    """
    engine = EmotionEngine()
    si = SectionIntelligence(engine=engine)
    result = si.parse(text)
    waves = result.get("section_emotions")
    assert waves and isinstance(waves, list)
    wave = waves[0]
    assert "tlp_mean" in wave
    assert "cluster_peak" in wave
    assert "intensity" in wave


def test_section_wave_detects_spike():
    text = """[Chorus]
    Убей! Убей их всех!
    Тихий шепот любви...
    """
    engine = EmotionEngine()
    si = SectionIntelligence(engine=engine)
    waves = si.parse(text)["section_emotions"]
    assert waves[0]["emotional_shape"] in ("spike", "rising")

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
