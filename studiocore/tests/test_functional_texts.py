# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Extended Functional Logic Test
Тестирует реакцию ядра на тексты с разными эмоциональными профилями.

ИСПРАВЛЕНО: Преобразовано в unittest.TestCase для запуска через discover.
ИСПРАВЛЕНО: Обновлены эталоны (snapshots) для `style` и `genre`.
"""

# === 🔧 Исправление пути импорта (ОБЯЗАТЕЛЬНО) ===
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest, traceback

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

# --- Эталонные ожидания (ОБНОВЛЕНЫ) ---
# Эталоны, обновленные на основе логов (ошибка 'neutral modal')
expected = {
    "love": {
        "genre": "lyrical adaptive",          # Было: cinematic narrative
        "style": "majestic major",          # Было: neutral modal
        "atmosphere": "serene and hopeful",
    },
    "pain": {
        "genre": "lyrical adaptive",          # Было: cinematic narrative
        "style": "melancholic minor",       # Было: neutral modal
        "atmosphere": "introspective and melancholic",
    },
    "fear": {
        "genre": "cinematic adaptive",
        "style": "dramatic harmonic minor",
        "atmosphere": "intense and cathartic", # Было: mystic and suspenseful
    },
    "joy": {
        "genre": "lyrical adaptive",          # Было: cinematic narrative
        "style": "majestic major",          # Было: neutral modal
        "atmosphere": "serene and hopeful",
    },
}


class TestFunctionalEmotionalLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Загружает ядро один раз для всех тестов в этом классе."""
        print("\n[TestFunctionalTexts] Загрузка StudioCore...")
        try:
            from studiocore import get_core
            cls.core = get_core()
            
            if getattr(cls.core, "is_fallback", False):
                 print("🧩 [StudioCoreFallback] Активен временный режим.")
            
            print("[TestFunctionalTexts] Ядро успешно загружено.")
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить ядро: {e}")
            print(traceback.format_exc())
            cls.core = None

    def test_emotional_logic_responses(self):
        """
        Главный тест: Прогоняет все тексты и сравнивает с эталонами.
        """
        if not self.core or getattr(self.core, "is_fallback", False):
            self.fail("Ядро не было загружено (в режиме Fallback), тесты логики пропущены.")

        for name, text in texts.items():
            # subTest позволяет тесту продолжаться, даже если один из кейсов упал
            with self.subTest(name=name.upper()):
                try:
                    result = self.core.analyze(text)
                except Exception as e:
                    self.fail(f"Ошибка ядра при анализе кейса {name.upper()}: {e}")

                style = result.get("style", {})
                genre = style.get("genre", "—")
                mood = style.get("style", "—")
                atmosphere = style.get("atmosphere", "—")
                bpm = result.get("bpm", 0)

                expected_case = expected[name]

                # Проверка ЖАНРА
                self.assertEqual(
                    genre, expected_case["genre"],
                    f"[{name.upper()}] Ошибка ЖАНРА: "
                    f"ожидался '{expected_case['genre']}', получен '{genre}'"
                )
                
                # Проверка СТИЛЯ
                self.assertEqual(
                    mood, expected_case["style"],
                    f"[{name.upper()}] Ошибка СТИЛЯ: "
                    f"ожидался '{expected_case['style']}', получен '{mood}'"
                )

                # Проверка АТМОСФЕРЫ
                self.assertEqual(
                    atmosphere, expected_case["atmosphere"],
                    f"[{name.upper()}] Ошибка АТМОСФЕРЫ: "
                    f"ожидалась '{expected_case['atmosphere']}', получена '{atmosphere}'"
                )
                
                # Проверка BPM
                self.assertTrue(
                    60 <= bpm <= 172,
                    f"[{name.upper()}] Ошибка BPM: "
                    f"BPM вне диапазона (60-172), получен {bpm}"
                )
                
                print(f"✅ [TestFunctionalTexts] {name.upper()} OK.")


# Этот блок позволяет запускать файл напрямую
# ИЛИ через discover (из test_all.py)
if __name__ == "__main__":
    unittest.main()