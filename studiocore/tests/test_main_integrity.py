# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — System Integrity Test
Проверяет, что всё ядро работает согласованно:
- импорты модулей
- генерация BPM, Genre, Style
- корректный JSON API ответ

ИСПРАВЛЕНО: Код преобразован в unittest-совместимый класс.
ИСПРАВЛЕНО: URL API обновлен на /api/predict
"""

# === 🔧 Исправление пути импорта (ОБЯЗАТЕЛЬНО) ===
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import importlib, json, traceback, unittest, requests

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

    def test_imports(self):
        """
        Тест: [Integrity] Проверяет, что все ключевые модули импортируются.
        """
        print("\n[TestIntegrity] 🔍 Checking imports...")
        for m in MODULES:
            with self.subTest(module=m):
                try:
                    importlib.import_module(m)
                    print(f"✅ {m} imported successfully.")
                except Exception as e:
                    self.fail(f"❌ Import failed: {m} — {e}")

    def test_prediction_pipeline(self):
        """
        Тест: [Integrity] Проверяет полный внутренний пайплайн.
        """
        print("\n[TestIntegrity] 🎧 Checking full pipeline...")
        try:
            from studiocore.style import PatchedStyleMatrix
            from studiocore.rhythm import LyricMeter
        except ImportError as e:
            self.fail(f"Не удалось импортировать модули ядра: {e}")
        except Exception as e:
            self.fail(f"Критическая ошибка при импорте модулей ядра (проверьте синтаксис): {e}")

        text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
        tlp = {"truth": 0.1, "love": 0.2, "pain": 0.04, "conscious_frequency": 0.85}
        emo = {"joy": 0.3, "peace": 0.4, "sadness": 0.1}

        try:
            bpm = LyricMeter().bpm_from_density(text, emo)
            style = PatchedStyleMatrix().build(emo, tlp, text, bpm)

            self.assertTrue(60 <= bpm <= 172, f"BPM out of range: {bpm}")
            self.assertIn("genre", style, "Missing 'genre' field in style output")
            self.assertIn("style", style, "Missing 'style' field in style output")
            self.assertIsInstance(style.get("techniques"), list, "Techniques not list")

            print(f"✅ Pipeline OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        
        except Exception as e:
            print(f"❌ Ошибка выполнения пайплайна: {traceback.format_exc()}")
            self.fail(e)


    def test_api_response(self):
        """
        Тест: [Integrity] Проверяет эндпоинт (требует запущенного сервера).
        """
        print("\n[TestIntegrity] 🌐 Checking API endpoint...")
        
        # ИСПРАВЛЕНИЕ: URL изменен на /api/predict
        api_url = "http://127.0.0.1:7860/api/predict"
        
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        
        try:
            r = requests.post(api_url, json=payload, timeout=10)
            
            if r.status_code == 503:
                self.fail(f"❌ API test failed: {r.status_code} (Service Unavailable). Ядро в режиме Fallback (проверьте синтаксис).")
            
            self.assertEqual(r.status_code, 200, 
                             f"API test failed: HTTP {r.status_code}. "
                             f"Убедитесь, что URL '{api_url}' корректный в app.py. "
                             f"Response: {r.text[:200]}")
            
            data = r.json()
            self.assertIn("bpm", data, "Ответ API не содержит 'bpm'")
            self.assertIn("style", data, "Ответ API не содержит 'style'")
            print(f"✅ API OK | Style={data.get('style')} | BPM={data.get('bpm')}")

        except requests.exceptions.ConnectionError:
            self.fail(f"❌ API test failed: Connection refused. Сервер {api_url} запущен?")
        except Exception as e:
            self.fail(f"❌ API test failed: {e}")

if __name__ == "__main__":
    unittest.main()