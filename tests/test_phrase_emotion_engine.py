# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

from studiocore.emotion import EmotionEngine
from studiocore.structures import PhraseEmotionPacket


def test_phrase_emotion_packet_basic_shape():
    engine = EmotionEngine()
    phrase = "Как лошадь, загнанная в мыле"
    packet = engine.analyze_phrase(phrase)
    assert isinstance(packet, PhraseEmotionPacket)
    data = packet.to_dict()
    assert "phrase" in data and data["phrase"]
    assert "emotions" in data and isinstance(data["emotions"], dict)
    assert "tlp" in data["emotions"]
    assert "pain" in data["emotions"]["tlp"]
    assert isinstance(data["weight"], float)
    assert 0.0 <= data["weight"] <= 1.0


def test_phrase_pain_dominates_for_burnout_metaphor():
    engine = EmotionEngine()
    phrase = "Как лошадь, загнанная в мыле"
    packet = engine.analyze_phrase(phrase)
    tlp = packet.emotions["tlp"]
    assert tlp["pain"] >= tlp["love"]
    assert packet.impact_zone in ("pain", "mixed")


def test_phrase_love_cluster_for_love_poem_line():
    engine = EmotionEngine()
    phrase = "Любовь! какой чаруйный звук!"
    packet = engine.analyze_phrase(phrase)
    tlp = packet.emotions["tlp"]
    assert tlp["love"] > 0.0


def test_phrase_engine_neutral_on_empty():
    engine = EmotionEngine()
    packet = engine.analyze_phrase("   ")
    tlp = packet.emotions["tlp"]
    assert 0.0 <= tlp["pain"] <= 1.0
    assert 0.0 <= tlp["love"] <= 1.0
    assert packet.weight <= 0.2

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
