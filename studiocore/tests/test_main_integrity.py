# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — System Integrity Test (Converted to unittest)
Проверяет, что всё ядро работает согласованно:
- импорты модулей
- генерация BPM, Genre, Style
- корректный JSON API ответ

ИСПРАВЛЕНО (v4): 
- Таймаут API увеличен до 30с (для Inference API).
- Исправлен ImportError для PatchedLyricMeter.
"""

# === 🔧 Исправление пути импорта (ОБЯЗАТЕЛЬНО) ===
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import unittest
import importlib, json, traceback, requests

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
        # Загружаем ИИ-модули один раз для всех тестов
        # Это предотвращает многократную медленную загрузку
        try:
            from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
            cls.EmoAnalyzer = AutoEmotionalAnalyzer
            cls.TlpAnalyzer = TruthLovePainEngine
            print("[TestIntegrity] Emo/TLP Analyzers pre-loaded.")
        except Exception as e:
            print(f"[TestIntegrity] Ошибка предзагрузки ИИ: {e}")
            cls.EmoAnalyzer = None
            cls.TlpAnalyzer = None

    def test_imports(self):
        """
        Тест: [Integrity] Проверяет, что все основные модули ядра импортируются.
        """
        print("\n[TestIntegrity] 🔍 Checking imports...")
        all_ok = True
        for m in MODULES:
            with self.subTest(module=m):
                try:
                    importlib.import_module(m)
                    print(f"✅ {m} imported successfully.")
                except Exception as e:
                    self.fail(f"❌ Import failed: {m} — {e}")
                    all_ok = False
        self.assertTrue(all_ok, "Не все модули ядра удалось импортировать.")

    def test_prediction_pipeline(self):
        """
        Тест: [Integrity] Проверяет внутренний конвейер (BPM + Style).
        """
        print("\n[TestIntegrity] 🎧 Checking full pipeline...")
        self.assertIsNotNone(self.EmoAnalyzer, "ИИ-движок Emo не загружен")
        self.assertIsNotNone(self.TlpAnalyzer, "ИИ-движок TLP не загружен")

        try:
            # ИСПРАВЛЕНИЕ: PatchedLyricMeter теперь живет в monolith_v4_3_1
            from studiocore.monolith_v4_3_1 import PatchedLyricMeter
            from studiocore.style import StyleMatrix

            text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
            
            # Симулируем полный прогон, как в test_all.py
            emo_analyzer = self.EmoAnalyzer()
            tlp_analyzer = self.TlpAnalyzer()
            emo = emo_analyzer.analyze(text)
            tlp = tlp_analyzer.analyze(text)

            bpm = PatchedLyricMeter().bpm_from_density(text)
            style = StyleMatrix().build(emo, tlp, text, bpm)

            self.assertTrue(60 <= bpm <= 180, f"BPM out of range: {bpm}")
            self.assertIn("genre", style, "Missing 'genre' in style output")
            self.assertIn("style", style, "Missing 'style' in style output")
            self.assertIsInstance(style.get("techniques", []), list, "Techniques not list")

            print(f"✅ Pipeline OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")

        except Exception as e:
            self.fail(f"❌ Pipeline test failed: {traceback.format_exc()}")

    def test_api_response(self):
        """
        Тест: [Integrity] Проверяет эндпоинт (требует запущенного сервера).
        """
        print("\n[TestIntegrity] 🌐 Checking API endpoint...")
        api_url = "http://127.0.0.1:7860/api/predict"
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        
        try:
            # ИСПРАВЛЕНИЕ: Таймаут 30с (для Inference API)
            r = requests.post(api_url, json=payload, timeout=30) 
            
            self.assertEqual(
                r.status_code, 200,
                f"API test failed: HTTP {r.status_code}. "
                f"Убедитесь, что URL '{api_url}' корректный в app.py. "
                f"Response: {r.text[:200]}..."
            )
            
            data = r.json()
            self.assertIn("style", data, "Ответ API не содержит ключ 'style'")
            self.assertIn("bpm", data, "Ответ API не содержит ключ 'bpm'")
            
            print(f"✅ API OK | Style={data.get('style')} | BPM={data.get('bpm')}")

        except Exception as e:
            self.fail(f"❌ API test failed: {e}")


# Этот блок позволяет запускать файл напрямую
# ИЛИ через discover (из test_all.py)
if __name__ == "__main__":
    unittest.main()