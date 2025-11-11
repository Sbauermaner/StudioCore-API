# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Functional Logic Test
Проверка соответствия анализа текста эталонным результатам.
"""

from studiocore import get_core
core = get_core()

texts = {
    "light": """Я встаю, когда солнце касается крыш,
Когда воздух поёт о свободе.
Каждый день — это шанс, что услышишь,
Как любовь возвращается к Богу.""",

    "dark": """Я тону, когда солнце уходит вдаль,
Когда воздух застыл, как камень.
Каждый день — это груз и печаль,
Где любовь утонула в обмане."""
}

expected = {
    "light": {
        "genre": "lyrical adaptive",
        "style": "majestic major",
        "atmosphere": "serene and hopeful",
    },
    "dark": {
        "genre": "cinematic adaptive",
        "style": "melancholic minor",
        "atmosphere": "introspective and melancholic",
    },
}

print("\n🧠 Functional Logic Test — StudioCore v5.2.1")

for name, text in texts.items():
    print(f"\n=== 🔹 TEST CASE: {name.upper()} ===")
    result = core.analyze(text)

    style = result.get("style", {})
    genre = style.get("genre", "—")
    mood = style.get("style", "—")
    atmosphere = style.get("atmosphere", "—")
    bpm = result.get("bpm", "—")

    print(f"🎭 Genre: {genre}")
    print(f"🎵 Style: {mood}")
    print(f"🌤 Atmosphere: {atmosphere}")
    print(f"⏱ BPM: {bpm}")

    ok = (
        genre == expected[name]["genre"]
        and mood == expected[name]["style"]
        and atmosphere == expected[name]["atmosphere"]
    )
    print("✅ OK" if ok else "⚠️ MISMATCH")
