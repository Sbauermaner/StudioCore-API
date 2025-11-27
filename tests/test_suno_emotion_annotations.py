# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
from studiocore.suno_annotations import SunoAnnotationEngine, build_suno_annotations


def test_suno_emotion_adapter_basic():
    curve = {
        "dominant_cluster": "tender",
        "global_tlp": {"truth": 0.1, "love": 0.8, "pain": 0.1},
    }
    sections = [
        {
            "section": "verse",
            "intensity": 0.4,
            "hot_phrases": ["Любовь как тихий свет"],
        },
        {"section": "chorus", "intensity": 0.9, "hot_phrases": ["Сгорит душа"]},
    ]
    ann = build_suno_annotations("..", sections, curve)
    assert "vocal_profile" in ann
    assert "instrumentation" in ann
    assert "section_annotations" in ann
    assert "chorus" in ann["section_annotations"]


def test_prepare_diagnostics_fills_from_emotion_matrix():
    engine = SunoAnnotationEngine()
    diagnostics = {
        "emotion_matrix": {
            "bpm": {"recommended": 132, "source": "emotion_matrix_v1"},
            "key": {
                "recommended": "F#",
                "mode": "minor",
                "source": "emotion_matrix_v1",
            },
            "vocals": {
                "gender": "female",
                "notes": ["airy", "soft"],
                "intensity_curve": [0.1, 0.2],
            },
        }
    }

    prepared = engine._prepare_diagnostics(diagnostics)

    assert prepared["bpm"]["estimate"] == 132
    assert prepared["tonality"]["key"] == "minor"
    assert prepared["vocal"]["style"] == "airy, soft"


def test_esenin_diagnostics_not_none():
    from studiocore.core_v6 import StudioCoreV6

    text = (
        "Вы помните,\n"
        "Вы всё, конечно, помните,\n"
        "Как я стоял,\n"
        "Приблизившись к стене,\n"
        "Взволнованно ходили вы по комнате\n"
        "И что-то резкое\n"
        "В лицо бросали мне."
    )
    core = StudioCoreV6()
    result = core.analyze(text, preferred_gender="auto")
    diagnostics = result.get("diagnostics", {})

    assert isinstance(diagnostics, dict)
    assert diagnostics.get("bpm") is not None
    assert diagnostics.get("tonality") is not None
    assert diagnostics.get("vocal") is not None
    assert diagnostics.get("emotion_matrix") is not None


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
