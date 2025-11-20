from studiocore.emotion_curve import build_global_emotion_curve
from studiocore.core_v6 import StudioCoreV6


def test_emotion_curve_builds_from_sections():
    sections = [
        {
            "section": "intro",
            "tlp_mean": {"truth": 0.2, "love": 0.1, "pain": 0.7},
            "cluster_peak": "rage",
            "intensity": 0.9,
            "emotional_shape": "spike",
            "hot_phrases": ["Убей их всех"],
        },
        {
            "section": "chorus",
            "tlp_mean": {"truth": 0.3, "love": 0.2, "pain": 0.8},
            "cluster_peak": "rage",
            "intensity": 0.95,
            "emotional_shape": "rising",
            "hot_phrases": ["НАЧНИ С СЕБЯ"],
        },
    ]
    curve = build_global_emotion_curve(sections)
    data = curve.to_dict()
    assert "global_tlp" in data
    assert "dominant_cluster" in data
    assert data["dominant_cluster"] == "rage"
    assert "peaks" in data and data["peaks"]


def test_dynamic_bias_applies_for_love():
    sections = [
        {
            "section": "verse",
            "tlp_mean": {"truth": 0.1, "love": 0.8, "pain": 0.1},
            "cluster_peak": "tender",
            "intensity": 0.6,
            "emotional_shape": "flat",
            "hot_phrases": ["Любовь! какой чаруйный звук!"],
        }
    ]
    curve = build_global_emotion_curve(sections)
    bias = curve.to_dict()["dynamic_bias"]
    assert bias["bpm_delta"] < 0
    assert bias["key_hint"] == "major"


def test_core_exposes_emotion_curve():
    core = StudioCoreV6()
    text = "[Verse]\nКак лошадь, загнанная в мыле\nЛюбовь и боль сплетают мост"
    result = core.analyze(text)
    assert "emotion_curve" in result
    assert "auto_context" in result
    assert "dynamic_bias" in result["auto_context"]
