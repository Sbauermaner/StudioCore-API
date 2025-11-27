# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
def test_color_engine_adapter_basic():
    from studiocore.color_engine_adapter import ColorEngineAdapter

    adapter = ColorEngineAdapter()

    # Сильная боль → синий спектр
    res = adapter.resolve_color_wave(
        {
            "tlp": {"truth": 0, "love": 0, "pain": 0.9},
            "emotion": {"sadness": 0.85},
        }
    )
    assert "#0A1F44" in res.colors
    assert res.source in ("tlp_rules", "emotion_map", "fallback")

    # Гнев → черно-красная волна
    res2 = adapter.resolve_color_wave(
        {
            "tlp": {"truth": 0, "love": 0, "pain": 0.2},
            "emotion": {"anger": 0.9},
        }
    )
    assert "#8B0000" in res2.colors


# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
