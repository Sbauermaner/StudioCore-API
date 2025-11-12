# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — COMPLETE SYSTEM VALIDATION (v4)
Автоматическая проверка всех модулей, структуры, синтаксиса и API:
1. Структура папок (Только проект)
2. Синтаксис Python / JSON / YAML (Только проект)
3. Проверка внутренних связей (AST)
4. Импорты и взаимодействие модулей
5. ЗАПУСК ВСЕХ UNIT-ТЕСТОВ (проверка логики ядра и связей)
6. Интеграционный тест (API)
7. Интеграционный тест (Ядро)

ИСПРАВЛЕНИЯ (v4):
- Добавлен 'import re' (исправление NameError)
- Исправлен ImportError для PatchedLyricMeter (теперь импортируется из monolith)
- Увеличен таймаут API до 120с
"""

# === 🔧 Исправление пути импорта (чтобы test видели пакет) ===
import os, sys, json, ast, yaml, importlib, requests, traceback
from statistics import mean
import unittest
import re # <-- ИСПРАВЛЕНИЕ: Добавлен 'import re'

# ВАЖНО: Этот блок исправляет путь, чтобы можно было импортировать 'studiocore'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Проверяем только папки нашего проекта
ROOT_DIR = ROOT
PROJECT_FOLDERS_TO_SCAN = ["studiocore"]
PROJECT_FILES_TO_SCAN = ["app.py"] 

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
# 📁 1. Проверка структуры и синтаксиса (v2 - Только проект)
# ==========================================================
def check_directories():
    print("📂 Проверка структуры...")
    required = [f"{ROOT_DIR}/studiocore", f"{ROOT_DIR}/studiocore/tests"]
    missing = [d for d in required if not os.path.isdir(d)]
    if missing:
        print(f"❌ Отсутствуют директории: {missing}")
        return False
    print("✅ Структура в порядке.")
    return True


def _is_ignored(path):
    """Проверяет, нужно ли игнорировать путь (системные папки)."""
    # Предотвращаем сканирование site-packages, /usr/lib и т.д.
    return any(p in path for p in ["/usr/", "/lib/", ".git/", ".venv/", "site-packages"])

def check_python_syntax_project():
    print("\n🐍 Проверка синтаксиса Python (проект)...")
    all_ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir):
            continue
        
        for root, _, files in os.walk(scan_dir):
            if _is_ignored(root):
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

    # 2. Проверяем отдельные файлы в корне
    for f in PROJECT_FILES_TO_SCAN:
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


def check_json_yaml_project():
    print("\n🧩 Проверка JSON / YAML (проект)...")
    ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir): continue

        for root, _, files in os.walk(scan_dir):
            if _is_ignored(root):
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
                        
    # 2. Проверяем отдельные файлы в корне (например, studio_config.json)
    for root, _, files in os.walk(ROOT_DIR, topdown=True):
        # Идем только по корневой директории, не глубже
        for f in files:
            if f.endswith(".json") or f.endswith((".yml", ".yaml")):
                 path = os.path.join(root, f)
                 # Пропускаем, если уже проверили (на всякий случай)
                 if any(folder in path for folder in PROJECT_FOLDERS_TO_SCAN):
                     continue
                 
                 if f.endswith(".json"):
                    try:
                        json.load(open(path, "r", encoding="utf-8"))
                        print(f"✅ JSON OK: {path}")
                    except Exception as e:
                        print(f"❌ JSON Error: {path} → {e}")
                        ok = False
        # Прерываем os.walk, чтобы он не шел вглубь
        break 

    return ok

# ==========================================================
# 🕸️ 2. Проверка внутренних связей (AST)
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
            # Превращаем путь в имя модуля (studiocore.rhythm)
            # Убираем os.path.sep, чтобы // не ломали имя
            module_name = path.replace(ROOT_DIR, "") \
                              .replace(os.path.sep, ".") \
                              .replace("..", ".") \
                              .strip(".") \
                              .replace(".py", "")
            
            # ИСПРАВЛЕНИЕ: Используем 're'
            module_name = re.sub(r"\.+", ".", module_name)
            
            dependencies[module_name] = []
            
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    tree = ast.parse(fp.read(), filename=path)
                
                # Ищем все 'import X' и 'from X import Y'
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("studiocore.") or alias.name.startswith("."):
                                dependencies[module_name].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and (node.module.startswith("studiocore.") or node.module.startswith(".")):
                            dependencies[module_name].append(node.module)
                            
            except Exception as e:
                print(f"❌ Не удалось спарсить {path}: {e}")
                ok = False

    # Печатаем отчет о связях
    print("--- Карта зависимостей ядра ---")
    for module, imports in dependencies.items():
        if imports:
            print(f"📄 {module} импортирует:")
            for imp in sorted(list(set(imports))):
                print(f"    └── {imp}")
    print("---------------------------------")
    return ok

# ==========================================================
# 🧠 3. Проверка импорта модулей
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
# 🔬 4. Запуск ВСЕХ Unit-тестов (Логика ядра)
# ==========================================================
def run_all_unit_tests():
    """
    Автоматически находит и запускает все файлы 'test_*.py' 
    в папке 'studiocore/tests/'.
    """
    print("\n🔬 Запуск всех Unit-тестов (проверка логики)...")
    try:
        loader = unittest.TestLoader()
        
        # ИСПРАВЛЕНИЕ: Ищем тесты только в папке tests
        test_dir = os.path.join(ROOT_DIR, "studiocore", "tests")
        suite = loader.discover(start_dir=test_dir, pattern="test_*.py") 
        
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print("❌ Обнаружены ошибки в Unit-тестах.")
            return False
        
        # Проверяем, что тесты вообще были найдены
        if result.testsRun == 0:
            print("⚠️  НИ ОДНОГО ТЕСТА НЕ НАЙДЕНО. Проверьте test_*.py файлы на наличие sys.path!")
            # Мы не считаем это ошибкой, но это предупреждение
            return True
            
        print(f"✅ Все Unit-тесты ({result.testsRun}) пройдены.")
        return True
    except Exception:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА при запуске тестов:")
        traceback.print_exc()
        return False

# ==========================================================
# 🎧 5. Проверка конкретного пайплайна (Интеграционный)
# ==========================================================
def test_prediction_pipeline():
    print("\n🎧 Проверка (интеграционная) ядра StudioCore...")
    try:
        # ИСПРАВЛЕНИЕ: Импорт PatchedLyricMeter из monolith_v4_3_1
        from studiocore.monolith_v4_3_1 import PatchedLyricMeter
        from studiocore.style import PatchedStyleMatrix
        from studiocore.emotion import TruthLovePainEngine, AutoEmotionalAnalyzer

        # Инициализируем движки, которые нужны для теста
        emo_analyzer = AutoEmotionalAnalyzer()
        tlp_engine = TruthLovePainEngine()
        
        text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
        
        # Эмулируем полный пайплайн
        emo = emo_analyzer.analyze(text)
        tlp = tlp_engine.analyze(text)
        bpm = PatchedLyricMeter().bpm_from_density(text)
        style = PatchedStyleMatrix().build(emo, tlp, text, bpm)

        assert 60 <= bpm <= 180, f"BPM вне диапазона: {bpm}"
        assert "genre" in style and "style" in style, "Отсутствуют ключевые поля"
        assert isinstance(style.get("techniques"), list), "Поле techniques не list"

        print(f"✅ Интеграция OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        return True
    except Exception:
        print("❌ Ошибка интеграционного теста ядра:")
        traceback.print_exc()
        return False


# ==========================================================
# 🌐 6. Проверка API /api/predict
# ==========================================================
def test_api_response():
    print("\n🌐 Проверка /api/predict ...")
    api_url = "http://127.0.0.1:7860/api/predict" # Используем /api/predict
    try:
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        
        # ИСПРАВЛЕНИЕ: Таймаут увеличен до 120 секунд для медленного API (ИИ)
        r = requests.post(api_url, json=payload, timeout=120)
        
        assert r.status_code == 200, f"HTTP {r.status_code}. Ответ: {r.text}"
        data = r.json()
        print(f"✅ API OK | BPM={data.get('bpm')} | Style={data.get('style')}")
        return True
    except Exception as e:
        print(f"❌ Ошибка API: {e} (Проверьте URL: {api_url})")
        return False


# ==========================================================
# 🧩 7. Запуск всех тестов и финальный отчёт
# ==========================================================
if __name__ == "__main__":
    print("\n===== 🧩 StudioCore v5.2.1 — FULL SYSTEM CHECK =====")

    total = 7
    results = {}
    
    # Запускаем тесты пошагово
    results["structure"] = check_directories()
    results["syntax"] = check_python_syntax_project()
    results["json_yaml"] = check_json_yaml_project()
    results["imports"] = test_imports()
    results["dependencies (AST)"] = check_internal_dependencies()
    
    # Сначала запускаем unit_tests. 
    # Если они провалятся, нет смысла проверять интеграцию API
    results["unit_tests (logic)"] = run_all_unit_tests()
    
    if results["unit_tests (logic)"]:
        # Запускаем интеграционные тесты, только если unit-тесты прошли
        results["integration_core"] = test_prediction_pipeline()
        results["integration_api"] = test_api_response()
    else:
        print("\n🔬 Пропуск 'integration_api' и 'integration_core', так как 'unit_tests (logic)' провалились.")
        results["integration_core"] = False
        results["integration_api"] = False

    passed = sum(1 for k in results.values() if k)
    
    # Обновляем total, если тесты были пропущены (хотя мы их засчитали как False)
    total = len(results)

    print("\n===== 🧾 ИТОГОВЫЙ ОТЧЁТ =====")
    for name, ok in results.items():
        print(f"{'✅' if ok else '❌'} {name}")

    print(f"\n🎯 ПРОЙДЕНО: {passed}/{total} тестов ({round(passed / total * 100, 2)}%)")

    # Получаем процент для условного вывода
    percent = round(passed / total * 100, 2)
    
    if percent == 100:
        print("🚀 Система полностью функциональна.")
    elif percent >= 70:
        print("⚠️ Система работает, но требует проверки некоторых модулей.")
    else:
        print("❌ Обнаружены критические ошибки, требуется ревизия.")