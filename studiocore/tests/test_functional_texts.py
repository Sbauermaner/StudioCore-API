# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — Extended Functional Logic Test (v12 - Обновлены эталоны)
(Использует "План С" - быстрые словари v13)
"""

# === 🔧 Исправление пути импорта ===
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest
import logging
import traceback # v12: Добавлен traceback

# === 1. АКТИВАЦИЯ ЛОГГЕРА ===
try:
    from studiocore.logger import setup_logging
    setup_logging()
except ImportError:
    pass # test_all.py уже должен был его настроить

log = logging.getLogger(__name__)
# === Конец активации логгера ===


# --- Глобальная загрузка ядра ---
CORE = None
CORE_LOADED = False
try:
    from studiocore import get_core
    CORE = get_core()
    CORE_LOADED = True
except Exception as e:
    log.critical(f"НЕ УДАЛОСЬ ЗАГРУЗИТЬ ЯДРО для тестов: {e}")


# --- Тестовые тексты по архетипам ---
texts = {
    "LOVE": """Я встаю, когда солнце касается крыш,
Когда воздух поёт о свободе.
Каждый день — это шанс, что услышишь,
Как любовь возвращается к Богу.""",

    "PAIN": """Я тону, когда солнце уходит вдаль,
Когда воздух застыл, как камень.
Каждый день — это груз и печаль,
Где любовь утонула в обмане.""",

    "FEAR": """Я стою на краю между светом и тьмой,
Слышу шаги — и замираю.
Каждый шорох становится болью,
Каждый вдох — испытанием веры.""",

    "JOY": """Я бегу по траве босиком,
Смеюсь, обгоняя ветер.
Всё вокруг сияет теплом,
И я чувствую жизнь на свете."""
}

# --- Эталонные ожидания (v12 - для словарей v13 + style v12) ---
expected = {
    "LOVE": {
        "genre": "lyrical adaptive", # (Mood=joy/peace ИЛИ Love > Pain)
        "style": "majestic major",
    },
    "PAIN": {
        "genre": "lyrical adaptive", # (Mood=sadness ИЛИ Pain > Love)
        "style": "melancholic minor",
    },
    # v12: 'fear' (из emo.py) теперь ПЕРВЫМ триггерит 'dramatic' стиль
    "FEAR": {
        "genre": "cinematic adaptive", 
        "style": "dramatic harmonic minor",
    },
    "JOY": {
        "genre": "lyrical adaptive", # (Mood=joy/peace)
        "style": "majestic major",
    },
}


class TestFunctionalEmotionalLogic(unittest.TestCase):
    
    core = None

    @classmethod
    def setUpClass(cls):
        """Загружаем ядро ОДИН РАЗ для всех тестов."""
        log.info("[TestFunctionalTexts] Загрузка StudioCore...")
        if not CORE_LOADED or not CORE:
            # v12: Проверяем CORE, а не CORE_LOADED
            cls.core = None 
        else:
            cls.core = CORE
        log.info("[TestFunctionalTexts] Ядро успешно загружено.")

    def test_emotional_logic_responses(self):
        """Главный тест: Прогоняет все тексты и сравнивает с эталонами."""
        
        # v12: Улучшенная проверка загрузки ядра
        if not self.core:
            self.fail("Ядро не было загружено (в режиме Fallback), тесты логики пропущены.")

        # Используем subTest, чтобы не падать на первой же ошибке
        for name, text in texts.items():
            # v12: Приводим name к UPPERCASE для единообразия
            name_upper = name.upper() 
            with self.subTest(name=name_upper):
                log.debug(f"--- [SubTest] Запуск анализа для: {name_upper} ---")
                
                try:
                    result = self.core.analyze(text)
                except Exception as e:
                    # Проваливаем тест, если analyze() упал
                    self.fail(f"Ошибка ядра при анализе кейса {name_upper}: {e}\n{traceback.format_exc()}")

                style = result.get("style", {})
                
                # 1. Проверка ЖАНРА
                expected_genre = expected[name_upper]["genre"]
                actual_genre = style.get("genre")
                self.assertEqual(
                    actual_genre, 
                    expected_genre,
                    f"[{name_upper}] Ошибка ЖАНРА: ожидался '{expected_genre}', получен '{actual_genre}'"
                )
                
                # 2. Проверка СТИЛЯ
                expected_style = expected[name_upper]["style"]
                actual_style = style.get("style")
                self.assertEqual(
                    actual_style,
                    expected_style,
                    f"[{name_upper}] Ошибка СТИЛЯ: ожидался '{expected_style}', получен '{actual_style}'"
                )

                log.info(f"✅ [TestFunctionalTexts] {name_upper} OK.")

if __name__ == "__main__":
    log.info("Запуск test_functional_texts.py как отдельного скрипта...")
    # v12: Добавляем активацию логгера при прямом запуске
    try:
        from studiocore.logger import setup_logging
        setup_logging(level=logging.DEBUG)
    except ImportError:
        logging.basicConfig(level=logging.DEBUG)
        
    unittest.main()