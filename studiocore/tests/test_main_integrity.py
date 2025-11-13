# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — System Integrity Test (v6 - Таймаут 20с)
Проверяет, что всё ядро работает согласованно.
"""

# === 🔧 Исправление пути импорта ===
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest
import importlib
import json
import requests
import traceback

# === 1. АКТИВАЦИЯ ЛОГГЕРА ===
try:
    from studiocore.logger import setup_logging
    setup_logging()
except ImportError:
    pass # test_all.py уже должен был его настроить

import logging
log = logging.getLogger(__name__)
# === Конец активации логгера ===


# === 2. Глобальные переменные для хранения движков ===
# (Чтобы не загружать их для каждого теста)
CORE_LOADED = False
EMO_ENGINE = None
TLP_ENGINE = None

try:
    # v15: Исправляем ImportError
    from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
    EMO_ENGINE = AutoEmotionalAnalyzer()
    TLP_ENGINE = TruthLovePainEngine()
    CORE_LOADED = True
except Exception as e:
    log.critical(f"Критическая ошибка загрузки движков: {e}")
    CORE_LOADED = False # v7: Устанавливаем в False при ошибке


MODULES = [
    "studiocore.text_utils",
    "studiocore.emotion",
    "studiocore.rhythm",
    "studiocore.vocals",
    "studiocore.style",
    "studiocore.tone",
    "studiocore.adapter"
]

class TestMainIntegrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Запускается один раз перед всеми тестами в этом классе."""
        log.info("[TestIntegrity] Emo/TLP Analyzers pre-loaded.")
        # v7: Исправлена ошибка UnboundLocalError
        if not CORE_LOADED:
            # Этот assert должен провалить тест, если ядро не загрузилось
            cls.fail("КРИТИЧЕСКАЯ ОШИБКА: Движки Emo/TLP не смогли загрузиться.")
        
        cls.emo_engine = EMO_ENGINE
        cls.tlp_engine = TLP_ENGINE


    def test_imports(self):
        """Тест: [Integrity] Проверяет, что все основные модули импортируются."""
        log.debug("Запуск: test_imports")
        failures = []
        for m in MODULES:
            try:
                importlib.import_module(m)
                log.info(f"✅ {m} imported successfully.")
            except Exception as e:
                failure_msg = f"❌ Import failed: {m} — {e}"
                log.error(failure_msg)
                failures.append(failure_msg)
        
        # Проверяем, что список сбоев пуст
        self.assertEqual(failures, [], "\n".join(failures))

    def test_prediction_pipeline(self):
        """Тест: [Integrity] Проверяет внутренний конвейер (BPM + Style)."""
        log.debug("Запуск: test_prediction_pipeline")
        
        # v7: Проверяем, что движки из setUpClass загрузились
        self.assertIsNotNone(self.emo_engine, "EMO Engine не был загружен")
        self.assertIsNotNone(self.tlp_engine, "TLP Engine не был загружен")

        try:
            # v6: Исправлен ImportError
            from studiocore.monolith_v4_3_1 import PatchedLyricMeter
            from studiocore.style import PatchedStyleMatrix

            lyric_meter = PatchedLyricMeter()
            style_matrix = PatchedStyleMatrix()

            text = "Я встаю, когда солнце касается крыш..."
            emo = self.emo_engine.analyze(text)
            tlp = self.tlp_engine.analyze(text)

            bpm = lyric_meter.bpm_from_density(text, emo)
            style = style_matrix.build(emo, tlp, text, bpm, {}, None)

            self.assertIn("genre", style)
            self.assertIn("style", style)
            self.assertIsInstance(style.get("techniques"), list)

            log.info(f"✅ Pipeline OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        
        except Exception:
            # Если что-то пошло не так, тест должен провалиться с подробным логом
            self.fail(f"❌ Pipeline test failed: {traceback.format_exc()}")


    def test_api_response(self):
        """Тест: [Integrity] Проверяет эндпоинт (требует запущенного сервера)."""
        log.debug("Запуск: test_api_response")
        
        api_url = "http://127.0.0.1:7860/api/predict"
        payload = {"text": "Тест API"}
        
        try:
            # v6: Увеличен таймаут
            r = requests.post(api_url, json=payload, timeout=20) 
            
            # Проверяем, что статус 200 OK
            self.assertEqual(r.status_code, 200, 
                             f"API test failed: HTTP {r.status_code}. "
                             f"Убедитесь, что URL '{api_url}' корректный в app.py. "
                             f"Response: {r.text[:200]}")
            
            data = r.json()
            self.assertIn("bpm", data)
            self.assertIn("style", data)
            
            log.info(f"✅ API OK | Style={data.get('style')} | BPM={data.get('bpm')}")

        except Exception as e:
            self.fail(f"❌ API test failed: {e}")

if __name__ == "__main__":
    log.info("Запуск test_main_integrity.py как отдельного скрипта...")
    unittest.main()