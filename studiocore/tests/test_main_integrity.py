# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — System Integrity Test (v7 - Включено логирование)
"""

# === 1. Активация логгера (ДО ВСЕХ ОСТАЛЬНЫХ ИМПОРТОВ) ===
try:
    from studiocore.logger import setup_logging
    setup_logging()
except ImportError:
    print("WARNING: studiocore.logger не найден.")

import unittest
import importlib
import json
import traceback
import requests
import os, sys
import logging

# Получаем настроенный логгер
log = logging.getLogger(__name__)

# === 🔧 Исправление пути импорта ===
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# === Импорты ядра (после исправления пути) ===
try:
    # v6 - Исправлен ImportError
    from studiocore.monolith_v4_3_1 import PatchedLyricMeter
    from studiocore.style import StyleMatrix # Используем алиас
    from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
    CORE_LOADED = True
except ImportError as e:
    log.critical(f"Критическая ошибка импорта в 'test_main_integrity': {e}")
    CORE_LOADED = False
    # Создаем заглушки, чтобы тест мог запуститься и показать ошибку
    class PatchedLyricMeter: pass
    class StyleMatrix: pass
    class AutoEmotionalAnalyzer: pass
    class TruthLovePainEngine: pass

MODULES = [
    "studiocore.text_utils",
    "studiocore.emotion",
    "studiocore.rhythm",
    "studiocore.vocals",
    "studiocore.style",
    "studiocore.tone",
    "studiocore.adapter"
]

# ===============================================
# 🚀 Класс Теста Целостности
# ===============================================

class TestMainIntegrity(unittest.TestCase):
    """
    Проверяет три столпа:
    1. Импорты (могут ли модули загрузиться)
    2. Пайплайн (могут ли модули отработать вместе)
    3. API (отвечает ли сервер)
    """
    
    emo_engine = None
    tlp_engine = None

    @classmethod
    def setUpClass(cls):
        """Загружает движки один раз для всех тестов."""
        log.info("[TestIntegrity] Emo/TLP Analyzers pre-loaded.")
        if CORE_LOADED:
            try:
                cls.emo_engine = AutoEmotionalAnalyzer()
                cls.tlp_engine = TruthLovePainEngine()
            except Exception as e:
                log.critical(f"Критическая ошибка загрузки движков: {e}")
                CORE_LOADED = False # Блокируем тесты, если движки не загрузились
        else:
            log.error("[TestIntegrity] Ядро не было загружено (ImportError).")

    def test_imports(self):
        """Тест: [Integrity] Проверяет, что все основные модули импортируются."""
        log.info("[TestIntegrity] 🔍 Checking imports...")
        failures = []
        for m in MODULES:
            try:
                importlib.import_module(m)
                log.info(f"✅ {m} imported successfully.")
            except Exception as e:
                log.error(f"❌ Import failed: {m} — {e}")
                failures.append(f"❌ Import failed: {m} — {e}")
        
        self.assertEqual(failures, [], "\n".join(failures))

    def test_prediction_pipeline(self):
        """Тест: [Integrity] Проверяет внутренний конвейер (BPM + Style)."""
        log.info("[TestIntegrity] 🎧 Checking full pipeline...")
        
        # Проверяем, что движки из setUpClass загрузились
        self.assertIsNotNone(self.emo_engine, "Emo Engine не был загружен")
        self.assertIsNotNone(self.tlp_engine, "TLP Engine не был загружен")

        try:
            text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
            
            log.debug("Вызов: emo_engine.analyze (pipeline test)")
            emo = self.emo_engine.analyze(text)
            log.debug("Вызов: tlp_engine.analyze (pipeline test)")
            tlp = self.tlp_engine.analyze(text)
            log.debug("Вызов: PatchedLyricMeter.bpm_from_density (pipeline test)")
            bpm = PatchedLyricMeter().bpm_from_density(text, emo)
            log.debug("Вызов: StyleMatrix.build (pipeline test)")
            style = StyleMatrix().build(emo, tlp, text, bpm, {}) # v4.3: нужен overlay

            self.assertGreaterEqual(bpm, 60)
            self.assertLessEqual(bpm, 180)
            self.assertIn("genre", style)
            self.assertIn("style", style)
            self.assertIsInstance(style.get("techniques", []), list)

            log.info(f"✅ Pipeline OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        
        except Exception as e:
            log.error(f"❌ Ошибка теста Пайплайна: {traceback.format_exc()}")
            self.fail(f"❌ Pipeline test failed: {traceback.format_exc()}")

    def test_api_response(self):
        """Тест: [Integrity] Проверяет эндпоинт (требует запущенного сервера)."""
        log.info("[TestIntegrity] 🌐 Checking API endpoint...")
        api_url = "http://127.0.0.1:7860/api/predict"
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        
        try:
            # v6 - Таймаут 20с
            r = requests.post(api_url, json=payload, timeout=20)
            
            data = r.json()
            
            self.assertEqual(r.status_code, 200, 
                             f"API test failed: HTTP {r.status_code}. "
                             f"Убедитесь, что URL '{api_url}' корректный в app.py. "
                             f"Response: {r.text[:200]}")
            
            log.info(f"✅ API OK | Style={data.get('style')} | BPM={data.get('bpm')}")

        except requests.exceptions.ReadTimeout as e:
            log.error(f"❌ Ошибка API: Таймаут (ReadTimeout) (>{20}с). Сервер (CPU) перегружен.")
            self.fail(f"❌ API test failed: {e}")
        except requests.exceptions.ConnectionError as e:
            log.error(f"❌ Ошибка API: Не удалось подключиться (ConnectionError). Сервер не запущен?")
            self.fail(f"❌ API test failed: {e}")
        except Exception as e:
            log.error(f"❌ Ошибка API (Общая): {e}")
            self.fail(f"❌ API test failed: {e}")

if __name__ == "__main__":
    log.info("Запуск test_main_integrity.py как отдельного скрипта...")
    unittest.main()