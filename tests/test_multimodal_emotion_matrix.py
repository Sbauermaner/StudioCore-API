from studiocore.core_v6 import StudioCoreV6


def test_matrix_rage():
    text = "[Chorus]\nУбей их всех!\nНАЧНИ С СЕБЯ"
    core = StudioCoreV6()
    result = core.analyze(text)
    m = result.get("emotion_matrix")
    assert m
    assert m["genre"]["primary"] != "edm"
    assert m["bpm"]["recommended"] > 130


def test_matrix_love():
    text = "[Verse]\nЛюбовь как тихий свет\nСердце растает"
    core = StudioCoreV6()
    result = core.analyze(text)
    m = result.get("emotion_matrix")
    assert m
    assert m["genre"]["primary"] != "extreme_adaptive_rage"
    assert m["tlp"]["love"] > m["tlp"]["pain"]


def test_core_matrix_integrated():
    text = "[Verse]\nКак лошадь, загнанная в мыле"
    core = StudioCoreV6()
    result = core.analyze(text)
    assert "emotion_matrix" in result
    assert isinstance(result["emotion_matrix"], dict)


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
