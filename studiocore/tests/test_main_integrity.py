# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — System Integrity Test
Проверяет, что всё ядро работает согласованно:
- импорты модулей
- генерация BPM, Genre, Style
- корректный JSON API ответ
"""

import importlib, json, traceback

MODULES = [
    "studiocore.text_utils",
    "studiocore.emotion",
    "studiocore.rhythm",
    "studiocore.vocals",
    "studiocore.style",
    "studiocore.tone",
    "studiocore.adapter"
]

def test_imports():
    print("🔍 Checking imports...")
    for m in MODULES:
        try:
            importlib.import_module(m)
            print(f"✅ {m} imported successfully.")
        except Exception as e:
            print(f"❌ Import failed: {m} — {e}")
            return False
    return True


def test_prediction_pipeline():
    from studiocore.style import PatchedStyleMatrix
    from studiocore.rhythm import LyricMeter

    print("\n🎧 Checking full pipeline...")
    text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
    tlp = {"truth": 0.1, "love": 0.2, "pain": 0.04, "conscious_frequency": 0.85}
    emo = {"joy": 0.3, "peace": 0.4, "sadness": 0.1}

    bpm = LyricMeter().bpm_from_density(text, emo)
    style = PatchedStyleMatrix().build(emo, tlp, text, bpm)

    assert 60 <= bpm <= 172, f"BPM out of range: {bpm}"
    assert "genre" in style and "style" in style, "Missing fields in style output"
    assert isinstance(style["techniques"], list), "Techniques not list"

    print(f"✅ BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
    return True


def test_api_response():
    import requests
    print("\n🌐 Checking /api/predict endpoint...")
    payload = {
        "text": "Я тону, когда солнце уходит вдаль...",
        "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
    }
    try:
        r = requests.post("http://127.0.0.1:7860/api/predict", json=payload, timeout=10)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        print(f"✅ API OK | Style={data.get('style')} | BPM={data.get('bpm')}")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n===== StudioCore v5.2.1 Integrity Test =====")
    try:
        ok1 = test_imports()
        ok2 = test_prediction_pipeline()
        ok3 = test_api_response()
        passed = sum([ok1, ok2, ok3])
        print(f"\n✅ PASSED {passed}/3 checks.\n")
    except Exception:
        traceback.print_exc()
