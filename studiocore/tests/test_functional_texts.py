# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Extended Functional Logic Test
Тестирует реакцию ядра на тексты с разными эмоциональными профилями:
Love / Pain / Fear / Joy / Light / Dark
"""

from studiocore import get_core
core = get_core()

# --- Тестовые тексты по архетипам ---
texts = {
    "love": """Я встаю, когда солнце касается крыш,
Когда воздух поёт о свободе.
Каждый день — это шанс, что услышишь,
Как любовь возвращается к Богу.""",

    "pain": """Я тону, когда солнце уходит вдаль,
Когда воздух застыл, как камень.
Каждый день — это груз и печаль,
Где любовь утонула в обмане.""",

    "fear": """Я стою на краю между светом и тьмой,
Слышу шаги — и замираю.
Каждый шорох становится болью,
Каждый вдох — испытанием веры.""",

    "joy": """Я бегу по траве босиком,
Смеюсь, обгоняя ветер.
Всё вокруг сияет теплом,
И я чувствую жизнь на свете."""
}

# --- Эталонные ожидания ---
expected = {
    "love": {
        "genre": "lyrical adaptive",
        "style": "majestic major",
        "atmosphere": "serene and hopeful",
    },
    "pain": {
        "genre": "cinematic adaptive",
        "style": "melancholic minor",
        "atmosphere": "introspective and melancholic",
    },
    "fear": {
        "genre": "cinematic adaptive",
        "style": "dramatic harmonic minor",
        "atmosphere": "mystic and suspenseful",
    },
    "joy": {
        "genre": "lyrical adaptive",
        "style": "majestic major",
        "atmosphere": "serene and hopeful",
    },
}

# --- Проверка ---
print("\n🧠 StudioCore v5.2.1 — Functional Emotional Logic Test")
print("===============================================")

for name, text in texts.items():
    print(f"\n=== 🔹 TEST CASE: {name.upper()} ===")
    result = core.analyze(text)

    style = result.get("style", {})
    genre = style.get("genre", "—")
    mood = style.get("style", "—")
    atmosphere = style.get("atmosphere", "—")
    narrative = style.get("narrative", "—")
    bpm = result.get("bpm", "—")

    print(f"🎭 Genre: {genre}")
    print(f"🎵 Style: {mood}")
    print(f"🌤 Atmosphere: {atmosphere}")
    print(f"📖 Narrative: {narrative}")
    print(f"⏱ BPM: {bpm}")

    ok = (
        genre == expected[name]["genre"]
        and mood == expected[name]["style"]
        and atmosphere == expected[name]["atmosphere"]
        and 60 <= (bpm or 0) <= 172
    )

    print("✅ OK — ядро реагирует корректно." if ok else "⚠️ MISMATCH — логика нарушена!")

print("\n📊 Тест завершён.")
print("Если есть ⚠️ — сравни вывод с эталоном выше.")
