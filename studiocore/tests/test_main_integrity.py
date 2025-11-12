# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — System Integrity Test (v3 - Unittest)
Проверяет, что всё ядро работает согласованно в формате Unittest:
- импорты модулей
- генерация BPM, Genre, Style
- корректный JSON API ответ
"""

# === 🔧 Исправление пути импорта ===
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest
import importlib
import json
import traceback
import requests # Убедитесь, что requests установлен

# --- Модули для проверки ---
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
        """Загружаем анализаторы один раз для всех тестов класса."""
        print("\n[TestIntegrity] Emo/TLP Analyzers pre-loaded.")
        try:
            # Импортируем движки, чтобы убедиться, что они загружаются
            from studiocore.emotion import TruthLovePainEngine, AutoEmotionalAnalyzer
            cls.tlp_engine = TruthLovePainEngine()
            cls.emo_analyzer = AutoEmotionalAnalyzer()
        except Exception as e:
            print(f"Критическая ошибка загрузки движков: {e}")
            cls.tlp_engine = None
            cls.emo_analyzer = None

    def test_imports(self):
        """Тест: [Integrity] Проверяет, что все основные модули импортируются."""
        print("\n[TestIntegrity] 🔍 Checking imports...")
        failures = []
        for m in MODULES:
            with self.subTest(module=m):
                try:
                    importlib.import_module(m)
                    print(f"✅ {m} imported successfully.")
                except Exception as e:
                    failures.append(f"❌ Import failed: {m} — {e}")
        
        self.assertEqual(failures, [], "\n".join(failures))

    def test_prediction_pipeline(self):
        """Тест: [Integrity] Проверяет внутренний конвейер (BPM + Style)."""
        print("\n[TestIntegrity] 🎧 Checking full pipeline...")
        
        # Проверяем, что движки загрузились в setUpClass
        self.assertIsNotNone(self.tlp_engine, "TLP Engine не был загружен")
        self.assertIsNotNone(self.emo_analyzer, "Emotion Analyzer не был загружен")

        try:
            # ИСПРАВЛЕНИЕ: PatchedLyricMeter теперь в monolith_v4_3_1
            from studiocore.monolith_v4_3_1 import PatchedLyricMeter
            from studiocore.style import PatchedStyleMatrix

            text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
            
            # Эмулируем пайплайн
            emo = self.emo_analyzer.analyze(text)
            tlp = self.tlp_engine.analyze(text)
            bpm = PatchedLyricMeter().bpm_from_density(text)
            style = PatchedStyleMatrix().build(emo, tlp, text, bpm)

            self.assertGreaterEqual(bpm, 60, f"BPM out of range: {bpm}")
            self.assertLessEqual(bpm, 180, f"BPM out of range: {bpm}")
            self.assertIn("genre", style, "Missing 'genre' in style output")
            self.assertIn("style", style, "Missing 'style' in style output")
            self.assertIsInstance(style.get("techniques"), list, "Techniques not list")

            print(f"✅ Pipeline OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")

        except ImportError as e:
            self.fail(f"❌ Ошибка импорта в тесте пайплайна: {e}")
        except Exception:
            self.fail(f"❌ Pipeline test failed: {traceback.format_exc()}")

    def test_api_response(self):
        """Тест: [Integrity] Проверяет эндпоинт (требует запущенного сервера)."""
        print("\n[TestIntegrity] 🌐 Checking API endpoint...")
        api_url = "http://127.0.0.1:7860/api/predict" # Используем /api/predict
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        
        try:
            # ИСПРАВЛЕНИЕ: Таймаут увеличен до 120 секунд
            r = requests.post(api_url, json=payload, timeout=120)
            
            self.assertEqual(r.status_code, 200, 
                             f"API test failed: HTTP {r.status_code}. Убедитесь, что URL '{api_url}' корректный в app.py. Response: {r.text}")
            
            data = r.json()
            self.assertIn("bpm", data)
            self.assertIn("style", data)
            print(f"✅ API OK | Style={data.get('style')} | BPM={data.get('bpm')}")

        except Exception as e:
            self.fail(f"❌ API test failed: {e}")

if __name__ == "__main__":
    unittest.main()