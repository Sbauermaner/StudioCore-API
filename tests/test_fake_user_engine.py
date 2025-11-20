# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

import json
import pytest

from studiocore.core_v6 import StudioCoreV6


def load_fake_users():
    """
    Загружаем всех фейковых юзеров из fake_users.json.
    Каждый юзер имеет:
      - sample_text
      - expected_emotion
      - expected_genre
    """
    with open("studiocore/tests/fake_users.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("users", [])


@pytest.mark.parametrize("user", load_fake_users())
def test_fake_user_emotion_and_genre(user):
    """
    Главный тест:
    - Текст анализируется ядром
    - Эмоция сверяется
    - Жанр сверяется
    """
    core = StudioCoreV6()
    result = core.analyze(user["sample_text"], preferred_gender="auto")

    assert isinstance(result, dict), "Core returned non-dict payload"

    # === 1. Проверка эмоции ===
    tlp = result.get("tlp", {}) or {}
    emotion_name = tlp.get("dominant_name") or tlp.get("emotion") or ""

    expected_emotion = user["expected_emotion"].lower()
    assert expected_emotion in emotion_name.lower(), (
        f"❌ Emotion mismatch for user={user['id']}: "
        f"expected '{expected_emotion}', got '{emotion_name}'"
    )

    # === 2. Проверка жанра ===
    style = result.get("style", {}) or {}
    genre = style.get("genre", "").lower()
    expected_genre = user["expected_genre"].lower()

    assert expected_genre in genre, (
        f"❌ Genre mismatch for user={user['id']}: "
        f"expected '{expected_genre}', got '{genre}'"
    )

    # === 3. BPM должен быть числом
    bpm = result.get("bpm", {}).get("estimate")
    assert bpm is not None, f"❌ BPM missing for user={user['id']}"
    assert isinstance(bpm, (int, float)), f"❌ BPM wrong type for user={user['id']}"

    # === 4. Проверка структуры секций (UI / Suno)
    structure = result.get("auto_context", {}).get("section_headers", [])
    assert isinstance(structure, list), "❌ Structure must be list"
    assert len(structure) >= 1, (
        f"❌ No section parsing for user={user['id']}. "
        "Expected Intro/Verse/Chorus/etc."
    )

    # === 5. Не должно быть утечек override-маркеров
    assert "_overrides_applied" not in result, "❌ leaked override marker!"

    # === 6. Проверка что JSON полностью валиден
    assert result.get("summary") is not None, (
        f"❌ summary missing for user={user['id']}"
    )

    print(f"✅ OK: {user['id']} | emotion={emotion_name} | genre={genre}")
