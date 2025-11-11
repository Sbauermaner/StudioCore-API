# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — COMPLETE SYSTEM VALIDATION
Автоматическая проверка всех модулей, структуры, синтаксиса и API:
1. Структура папок (ВЕСЬ ПРОЕКТ)
2. Синтаксис Python / JSON / YAML (ВЕСЬ ПРОЕКТ)
3. Импорты и взаимодействие модулей
4. ЗАПУСК ВСЕХ UNIT-ТЕСТОВ (проверка логики ядра и связей)
5. Тест API /api/predict
"""

# === 🔧 Исправление пути импорта (чтобы test видели пакет) ===
import os, sys, json, ast, yaml, importlib, requests, traceback
from statistics import mean
import unittest # <-- Добавлен для запуска всех тестов

# ВАЖНО: Этот блок исправляет путь, чтобы можно было импортировать 'studiocore'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ИЗМЕНЕНИЕ 1: Проверяем весь проект, а не только 'studiocore'
ROOT_DIR = ROOT 

MODULES = [
    "studiocore.text_utils",
    "studiocore.emotion",
    "studiocore.rhythm",
    "studiocore.vocals",
    "studiocore.style",
    "studiocore.tone",
    "studiocore.adapter"
]

# ==========================================================
# 📁 1. Проверка структуры и синтаксиса
# ==========================================================
def check_directories():
    print("📂 Проверка структуры...")
    # Проверяем только 'studiocore', а не весь ROOT
    required = [f"{ROOT_DIR}/studiocore", f"{ROOT_DIR}/studiocore/tests"]
    missing = [d for d in required if not os.path.isdir(d)]
    if missing:
        print(f"❌ Отсутствуют директории: {missing}")
        return False
    print("✅ Структура в порядке.")
    return True


def check_python_syntax():
    print("\n🐍 Проверка синтаксиса Python (весь проект)...")
    all_ok = True
    # Теперь os.walk идет по всему ROOT_DIR (всему проекту)
    for root, _, files in os.walk(ROOT_DIR):
        if ".venv" in root or ".git" in root: # Игнорируем ненужные
            continue
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8") as fp:
                        ast.parse(fp.read(), filename=path)
                    print(f"✅ OK: {path}")
                except SyntaxError as e:
                    print(f"❌ Ошибка синтаксиса: {path} → {e}")
                    all_ok = False
    return all_ok


def check_json_yaml():
    print("\n🧩 Проверка JSON / YAML (весь проект)...")
    ok = True
    # Теперь os.walk идет по всему ROOT_DIR (всему проекту)
    for root, _, files in os.walk(ROOT_DIR):
        if ".venv" in root or ".git" in root: # Игнорируем ненужные
            continue
        for f in files:
            path = os.path.join(root, f)
            if f.endswith(".json"):
                try:
                    json.load(open(path, "r", encoding="utf-8"))
                    print(f"✅ JSON OK: {path}")
                except Exception as e:
                    print(f"❌ JSON Error: {path} → {e}")
                    ok = False
            elif f.endswith((".yml", ".yaml")):
                try:
                    yaml.safe_load(open(path, "r", encoding="utf-8"))
                    print(f"✅ YAML OK: {path}")
                except Exception as e:
                    print(f"❌ YAML Error: {path} → {e}")
                    ok = False
    return ok


# ==========================================================
# 🧠 2. Проверка импорта и взаимодействия модулей
# ==========================================================
def test_imports():
    print("\n🧠 Проверка модулей StudioCore...")
    all_ok = True
    for m in MODULES:
        try:
            importlib.import_module(m)
            print(f"✅ Импортирован: {m}")
        except Exception as e:
            print(f"❌ Ошибка импорта: {m} — {e}")
            all_ok = False
    return all_ok

# ==========================================================
# 🔬 3. ИЗМЕНЕНИЕ 2: Запуск ВСЕХ Unit-тестов (Логика ядра)
# ==========================================================
def run_all_unit_tests():
    """
    Автоматически находит и запускает все файлы 'test_*.py' 
    во всех папках проекта (в ROOT_DIR).
    Это и есть проверка "логики ядра" и "связей".
    """
    print("\n🔬 Запуск всех Unit-тестов (проверка логики)...")
    try:
        loader = unittest.TestLoader()
        # Ищем все тесты во всех папках
        suite = loader.discover(start_dir=ROOT_DIR, pattern="test_*.py") 
        runner = unittest.TextTestRunner(verbosity=1) # verbosity=2 для деталей
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print("❌ Обнаружены ошибки в Unit-тестах.")
            return False
        
        print("✅ Все Unit-тесты пройдены.")
        return True
    except Exception:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА при запуске тестов:")
        traceback.print_exc()
        return False

# ==========================================================
# 🎧 4. (БЫЛ 3) Проверка конкретного пайплайна (Интеграционный)
# ==========================================================
def test_prediction_pipeline():
    print("\n🎧 Проверка (интеграционная) ядра StudioCore...")
    try:
        from studiocore.style import PatchedStyleMatrix
        from studiocore.rhythm import LyricMeter

        text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
        tlp = {"truth": 0.1, "love": 0.2, "pain": 0.04, "conscious_frequency": 0.85}
        emo = {"joy": 0.3, "peace": 0.4, "sadness": 0.1}

        bpm = LyricMeter().bpm_from_density(text, emo)
        style = PatchedStyleMatrix().build(emo, tlp, text, bpm)

        assert 60 <= bpm <= 172, f"BPM вне диапазона: {bpm}"
        assert "genre" in style and "style" in style, "Отсутствуют ключевые поля"
        assert isinstance(style["techniques"], list), "Поле techniques не list"

        print(f"✅ Интеграция OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        return True
    except Exception:
        traceback.print_exc()
        return False


# ==========================================================
# 🌐 5. (БЫЛ 4) Проверка API /api/predict
# ==========================================================
def test_api_response():
    print("\n🌐 Проверка /api/predict ...")
    try:
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        r = requests.post("http://127.0.0.1:7860/api/predict", json=payload, timeout=10)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        print(f"✅ API OK | BPM={data.get('bpm')} | Style={data.get('style')}")
        return True
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return False


# ==========================================================
# 🧩 6. (БЫЛ 5) Запуск всех тестов и финальный отчёт
# ==========================================================
if __name__ == "__main__":
    print("\n===== 🧩 StudioCore v5.2.1 — FULL SYSTEM CHECK =====")

    # ИЗМЕНЕНИЕ 3: Обновлен список тестов
    total = 6
    results = {
        "structure": check_directories(),
        "syntax": check_python_syntax(),
        "json_yaml": check_json_yaml(),
        "imports": test_imports(),
        "unit_tests (logic)": run_all_unit_tests(), # <-- НОВЫЙ ТЕСТ
        "integration_api": test_prediction_pipeline() and test_api_response()
    }

    passed = sum(1 for k in results.values() if k)
    percent = round(passed / total * 100, 2)

    print("\n===== 🧾 ИТОГОВЫЙ ОТЧЁТ =====")
    for name, ok in results.items():
        print(f"{'✅' if ok else '❌'} {name}")

    print(f"\n🎯 ПРОЙДЕНО: {passed}/{total} тестов ({percent}%)")

    if percent == 100:
        print("🚀 Система полностью функциональна.")
    elif percent >= 80:
        print("⚠️ Система работает, но требует проверки некоторых модулей.")
    else:
        print("❌ Обнаружены критические ошибки, требуется ревизия.")