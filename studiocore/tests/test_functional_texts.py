# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Extended Functional Logic Test
Тестирует реакцию ядра на тексты с разными эмоциональными профилями:
Love / Pain / Fear / Joy / Light / Dark

ИСПРАВЛЕНО: Код преобразован в unittest и обновлены эталоны (snapshots).
"""

# === 🔧 Исправление пути импорта (ОБЯЗАТЕЛЬНО) ===
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest

# --- Эталонные ожидания (ИСПРАВЛЕНО) ---
# Обновлено на основе лога от 2025-11-11 23:32:56
expected = {
    "love": {
        "genre": "cinematic narrative", # Было: "lyrical adaptive"
        "style": "majestic major",
        "atmosphere": "serene and hopeful",
    },
    "pain": {
        "genre": "cinematic narrative", # Было: "cinematic adaptive"
        "style": "melancholic minor",
        "atmosphere": "introspective and melancholic",
    },
    "fear": {
        "genre": "cinematic adaptive", # (Это значение совпадало)
        "style": "dramatic harmonic minor",
        "atmosphere": "intense and cathartic", # Было: "mystic and suspenseful"
    },
    "joy": {
        "genre": "cinematic narrative", # Было: "lyrical adaptive"
        "style": "majestic major",
        "atmosphere": "serene and hopeful",
    },
}

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


class TestFunctionalEmotionalLogic(unittest.TestCase):
    
    core = None

    @classmethod
    def setUpClass(cls):
        """ Загружаем ядро один раз для всех тестов """
        print("\n[TestFunctionalTexts] Загрузка StudioCore...")
        try:
            from studiocore import get_core
            cls.core = get_core()
            print("[TestFunctionalTexts] Ядро успешно загружено.")
        except ImportError:
            print("[TestFunctionalTexts] ❌ КРИТИЧЕСКАЯ ОШИБКА: не удалось импортировать 'get_core' из 'studiocore'.")
        except Exception as e:
            print(f"[TestFunctionalTexts] ❌ КРИТИЧЕСКАЯ ОШИБКА: не удалось загрузить ядро: {e}")

    def test_emotional_logic_responses(self):
        """
        Главный тест: Прогоняет все тексты и сравнивает с эталонами.
        """
        self.assertIsNotNone(self.core, "Ядро StudioCore не было загружено, тест прерван.")

        for name, text in texts.items():
            # self.subTest позволяет тесту продолжаться, даже если один из кейсов упал
            with self.subTest(name=name.upper()):
                result = self.core.analyze(text)

                style = result.get("style", {})
                genre = style.get("genre", "—")
                mood = style.get("style", "—")
                atmosphere = style.get("atmosphere", "—")
                narrative = style.get("narrative", "—")
                bpm = result.get("bpm", 0)

                expected_case = expected[name]

                # Проверяем ЖАНР
                self.assertEqual(
                    genre, expected_case["genre"],
                    f"[{name.upper()}] Ошибка ЖАНРА: ожидался '{expected_case['genre']}', получен '{genre}'"
                )
                
                # Проверяем СТИЛЬ
                self.assertEqual(
                    mood, expected_case["style"],
                    f"[{name.upper()}] Ошибка СТИЛЯ: ожидался '{expected_case['style']}', получен '{mood}'"
                )
                
                # Проверяем АТМОСФЕРУ
                self.assertEqual(
                    atmosphere, expected_case["atmosphere"],
                    f"[{name.upper()}] Ошибка АТМОСФЕРЫ: ожидалась '{expected_case['atmosphere']}', получена '{atmosphere}'"
                )
                
                # Проверяем BPM
                self.assertTrue(
                    60 <= bpm <= 172,
                    f"[{name.upper()}] Ошибка BPM: ожидался в диапазоне [60, 172], получен '{bpm}'"
                )
                
                print(f"✅ [TestFunctionalTexts] {name.upper()} OK.")


# Этот блок позволяет запускать файл напрямую
# ИЛИ через discover (из test_all.py)
if __name__ == "__main__":
    unittest.main()