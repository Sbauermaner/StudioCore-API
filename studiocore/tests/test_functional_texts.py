# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Extended Functional Logic Test
Тестирует реакцию ядра на тексты с разными эмоциональными профилями:
Love / Pain / Fear / Joy / Light / Dark

ИСПРАВЛЕНО: Код преобразован в unittest-совместимый класс.
"""

# === 🔧 Исправление пути импорта (ОБЯЗАТЕЛЬНО) ===
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest
from studiocore import get_core

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

class TestFunctionalEmotionalLogic(unittest.TestCase):
    
    core = None

    @classmethod
    def setUpClass(cls):
        """Загружаем ядро один раз для всех тестов в этом классе."""
        print("\n[TestFunctionalTexts] Загрузка StudioCore...")
        try:
            cls.core = get_core()
            print("[TestFunctionalTexts] Ядро успешно загружено.")
        except Exception as e:
            print(f"[TestFunctionalTexts] КРИТИЧЕСКАЯ ОШИБКА загрузки ядра: {e}")
            cls.core = None

    def test_emotional_logic_responses(self):
        """
        Главный тест: Прогоняет все тексты и сравнивает с эталонами.
        """
        self.assertIsNotNone(self.core, "Ядро StudioCore не было загружено (см. setUpClass). Тест прерван.")

        for name, text in texts.items():
            # self.subTest позволяет тесту продолжаться, даже если один из
            # кейсов упадет, и сообщает, какой именно упал.
            with self.subTest(name=name.upper()):
                result = self.core.analyze(text)

                style = result.get("style", {})
                actual_genre = style.get("genre", "—")
                actual_mood = style.get("style", "—")
                actual_atmosphere = style.get("atmosphere", "—")
                actual_bpm = result.get("bpm", 0)

                expected_data = expected[name]
                
                # --- Проверки (Assertions) ---
                
                self.assertEqual(
                    actual_genre, 
                    expected_data["genre"],
                    f"[{name.upper()}] Ошибка ЖАНРА: ожидался '{expected_data['genre']}', получен '{actual_genre}'"
                )
                
                self.assertEqual(
                    actual_mood, 
                    expected_data["style"],
                    f"[{name.upper()}] Ошибка СТИЛЯ: ожидался '{expected_data['style']}', получен '{actual_mood}'"
                )
                
                self.assertEqual(
                    actual_atmosphere, 
                    expected_data["atmosphere"],
                    f"[{name.upper()}] Ошибка АТМОСФЕРЫ: ожидалась '{expected_data['atmosphere']}', получена '{actual_atmosphere}'"
                )
                
                self.assertTrue(
                    60 <= actual_bpm <= 172,
                    f"[{name.upper()}] Ошибка BPM: {actual_bpm} вне диапазона [60, 172]"
                )

# Этот блок позволяет запускать файл напрямую (python studiocore/tests/test_functional_texts.py)
# ИЛИ через discover (python studiocore/tests/test_all.py)
if __name__ == "__main__":
    unittest.main()