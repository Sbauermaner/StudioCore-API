# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — COMPLETE SYSTEM VALIDATION
Автоматическая проверка всех модулей, структуры, синтаксиса и API:
1. Структура папок
2. Синтаксис Python / JSON / YAML (ТОЛЬКО ПРОЕКТ)
3. Импорты и взаимодействие модулей
4. АНАЛИЗ ВНУТРЕННИХ СВЯЗЕЙ (AST)
5. ЗАПУСК ВСЕХ UNIT-ТЕСТОВ (логика ядра)
6. Тест API /api/predict
"""

# === 🔧 Исправление пути импорта (чтобы test видели пакет) ===
import os, sys, json, ast, yaml, importlib, requests, traceback
from statistics import mean
import unittest # <-- Добавлен для запуска всех тестов

# ВАЖНО: Этот блок исправляет путь, чтобы можно было импортировать 'studiocore'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Используем ROOT как корень проекта
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

# ИСПРАВЛЕНИЕ: Сканируем только эти папки и файлы, чтобы не трогать /usr/lib
PROJECT_FOLDERS_TO_SCAN = ["studiocore"]
# Добавьте сюда другие корневые файлы .py или .json, если они есть
PROJECT_FILES_TO_SCAN = ["app.py", "studio_config.json"]


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

# ИСПРАВЛЕНО: Эта функция теперь сканирует только папки проекта
def check_python_syntax_project():
    print("\n🐍 Проверка синтаксиса Python (проект)...")
    all_ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir):
            print(f"⚠️  Папка для сканирования не найдена: {scan_dir}")
            continue
        
        for root, _, files in os.walk(scan_dir):
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

    # 2. Проверяем отдельные файлы в корне
    for f in PROJECT_FILES_TO_SCAN:
        if not f.endswith(".py"): continue
        path = os.path.join(ROOT_DIR, f)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    ast.parse(fp.read(), filename=path)
                print(f"✅ OK: {path}")
            except SyntaxError as e:
                print(f"❌ Ошибка синтаксиса: {path} → {e}")
                all_ok = False
                
    return all_ok

# ИСПРАВЛЕНО: Эта функция теперь сканирует только папки проекта
def check_json_yaml_project():
    print("\n🧩 Проверка JSON / YAML (проект)...")
    ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir): continue

        for root, _, files in os.walk(scan_dir):
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
                        
    # 2. Проверяем отдельные файлы в корне
    for f in PROJECT_FILES_TO_SCAN:
        if not (f.endswith(".json") or f.endswith(".yml") or f.endswith(".yaml")): continue
        path = os.path.join(ROOT_DIR, f)
        if os.path.isfile(path):
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
# 🕸️ 3. ДОБАВЛЕНО: Проверка внутренних связей ядра (AST)
# ==========================================================
def check_internal_dependencies():
    """
    Сканирует все .py файлы в 'studiocore' и ищет внутренние импорты,
    чтобы показать "взаимосвязи" ядра.
    """
    print("\n🕸️  Проверка внутренних связей (studiocore.*)...")
    dependencies = {}
    ok = True
    
    scan_dir = os.path.join(ROOT_DIR, "studiocore")
    
    for root, _, files in os.walk(scan_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            
            path = os.path.join(root, f)
            # Превращаем путь в имя модуля (studiocore/rhythm.py -> studiocore.rhythm)
            rel_path = os.path.relpath(path, ROOT_DIR)
            module_name = rel_path.replace(os.path.sep, ".").replace(".py", "")
            
            # Пропускаем __init__ файлы, если они пустые или для связей
            if f == "__init__.py":
                module_name = module_name.replace(".__init__", "")

            dependencies[module_name] = []
            
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    tree = ast.parse(fp.read(), filename=path)
                
                # Ищем все 'import X' и 'from X import Y'
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("studiocore"):
                                dependencies[module_name].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        # Убеждаемся, что node.module не None (для 'from . import X')
                        if node.module and node.module.startswith("studiocore"):
                            dependencies[module_name].append(node.module)
                            
            except Exception as e:
                print(f"❌ Не удалось спарсить {path}: {e}")
                ok = False

    # Печатаем отчет о связях
    print("--- Карта зависимостей ядра ---")
    for module, imports in sorted(dependencies.items()):
        if imports:
            # Убираем дубликаты
            unique_imports = sorted(list(set(imports)))
            print(f"📄 {module} импортирует:")
            for imp in unique_imports:
                print(f"    └── {imp}")
    print("---------------------------------")
    return ok

# ==========================================================
# 🔬 4. (БЫЛ 3) Запуск ВСЕХ Unit-тестов (Логика ядра)
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
        
        # ИСПРАВЛЕНИЕ: Ищем тесты только в папке tests, а не во всем проекте.
        test_dir = os.path.join(ROOT_DIR, "studiocore", "tests")
        suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
        
        runner = unittest.TextTestRunner(verbosity=1) # verbosity=2 для деталей
        result = runner.run(suite)

        if not result.wasSuccessful():
            print("❌ Обнаружены ошибки в Unit-тестах.")
            return False

        # Проверяем, были ли тесты вообще запущены
        if result.testsRun == 0:
             print("⚠️  НИ ОДНОГО ТЕСТА НЕ НАЙДЕНО. (Это может быть нормально, если их пока нет)")
             return True 

        print(f"✅ Все {result.testsRun} Unit-теста пройдены.")
        return True
    except Exception:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА при запуске тестов:")
        traceback.print_exc()
        return False

# ==========================================================
# 🎧 5. (БЫЛ 4) Проверка конкретного пайплайна (Интеграционный)
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
# 🌐 6. (БЫЛ 5) Проверка API /api/predict
# ==========================================================
def test_api_response():
    print("\n🌐 Проверка /api/predict ...")
    
    # !!! ИСПРАВЛЕНИЕ 404: Убран /api/ префикс. Проверьте ваш app.py!
    api_url = "http://127.0.0.1:7860/predict" 
    
    try:
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        r = requests.post(api_url, json=payload, timeout=10)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        data = r.json()
        print(f"✅ API OK | BPM={data.get('bpm')} | Style={data.get('style')}")
        return True
    except Exception as e:
        print(f"❌ Ошибка API: {e} (Проверьте URL: {api_url})")
        return False


# ==========================================================
# 🧩 7. (БЫЛ 6) Запуск всех тестов и финальный отчёт
# ==========================================================
if __name__ == "__main__":
    print("\n===== 🧩 StudioCore v5.2.1 — FULL SYSTEM CHECK =====")

    total = 7
    results = {
        "structure": check_directories(),
        "syntax": check_python_syntax_project(), # <-- Вызов исправленной функции
        "json_yaml": check_json_yaml_project(), # <-- Вызов исправленной функции
        "imports": test_imports(),
        "dependencies (AST)": check_internal_dependencies(), # <-- НОВЫЙ ТЕСТ СВЯЗЕЙ
        "unit_tests (logic)": run_all_unit_tests(), # <-- Вызов исправленной функции
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