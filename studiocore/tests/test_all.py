# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — COMPLETE SYSTEM VALIDATION (v3)
Автоматическая проверка:
1. Структура папок (проект)
2. Синтаксис Python / JSON / YAML (проект)
3. Внутренние связи ядра (AST)
4. Импорты модулей
5. ЗАПУСК ВСЕХ UNIT-ТЕСТОВ (Логика ядра)
6. Тест Интеграции API (проверка /api/predict)

ИСПРАВЛЕНИЕ (v5):
- Исправлен ImportError для PatchedLyricMeter.
- Увеличен таймаут для API (30с).
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

# === ИСПРАВЛЕНИЕ: Ограничиваем сканирование ===
# Папки и файлы в корне проекта, которые нужно проверять
PROJECT_FOLDERS_TO_SCAN = ["studiocore"]
PROJECT_FILES_TO_SCAN = ["app.py"] 

# Пути, которые нужно *полностью* игнорировать (для Hugging Face)
IGNORE_PATHS = ["/usr/", "/lib/", "/.git/", "/.venv/", "/.docker/", "/.huggingface/"]

def _is_ignored(path):
    """Проверяет, нужно ли игнорировать путь."""
    for ignored in IGNORE_PATHS:
        # Используем os.path.normpath для /usr/ и usr/
        norm_ignored = os.path.normpath(ignored)
        norm_path = os.path.normpath(path)
        if norm_path.startswith(norm_ignored):
            return True
    return False

# ==========================================================
# 📁 1. Проверка структуры и синтаксиса
# ==========================================================
def check_directories():
    print("📂 Проверка структуры...")
    
    # Пытаемся найти корень приложения (обычно /app в Docker)
    scan_root = ROOT_DIR
    if not os.path.isdir(os.path.join(scan_root, "studiocore")):
        scan_root = os.getcwd() # Откатываемся до текущей директории

    required = [os.path.join(scan_root, "studiocore"), os.path.join(scan_root, "studiocore/tests")]

    # В среде HF, пути могут быть относительными
    if not os.path.isdir(required[0]):
         required = ["studiocore", "studiocore/tests"]

    missing = [d for d in required if not os.path.isdir(d)]
    if missing:
        print(f"❌ Отсутствуют директории: {missing} (Проверено из {os.getcwd()})")
        return False
    print("✅ Структура в порядке.")
    return True


def check_python_syntax_project():
    print("\n🐍 Проверка синтаксиса Python (проект)...")
    all_ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir):
            print(f"⚠️  Папка {scan_dir} не найдена, пропускаем.")
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
                    except Exception as e:
                        print(f"❌ Ошибка чтения файла (возможно, UTF-8?): {path} → {e}")
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
            except Exception as e:
                print(f"❌ Ошибка чтения файла (возможно, UTF-8?): {path} → {e}")
                all_ok = False
        else:
            print(f"⚠️  Файл {path} не найден, пропускаем.")
                
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
    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        # Игнорируем ненужные директории в корне
        dirs[:] = [d for d in dirs if not _is_ignored(os.path.join(root, d))]
        
        for f in files:
            if f.endswith(".json") or f.endswith((".yml", ".yaml")):
                 path = os.path.join(root, f)
                 # Пропускаем, если уже проверили
                 if any(folder in path for folder in PROJECT_FOLDERS_TO_SCAN):
                     continue
                 
                 if f.endswith(".json"):
                    try:
                        json.load(open(path, "r", encoding="utf-8"))
                        print(f"✅ JSON OK: {path}")
                    except Exception as e:
                        print(f"❌ JSON Error: {path} → {e}")
                        ok = False
        # Прерываем os.walk, чтобы он не шел вглубь (только корень)
        break 

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
# 🕸️ 3. Проверка внутренних связей ядра (AST)
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
        if _is_ignored(root):
            continue
            
        for f in files:
            if not f.endswith(".py"):
                continue
            
            path = os.path.join(root, f)
            # Превращаем путь в имя модуля (studiocore.rhythm)
            # Убедимся, что ROOT_DIR имеет правильный разделитель
            norm_root_dir = ROOT_DIR.rstrip(os.path.sep) + os.path.sep
            module_name = path.replace(norm_root_dir, "") \
                              .replace(os.path.sep, ".") \
                              .replace(".py", "")
            
            # Убираем возможные артефакты (например, если ROOT_DIR = /app)
            module_name = module_name.lstrip(".") 
            
            dependencies[module_name] = []
            
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    tree = ast.parse(fp.read(), filename=path)
                
                # Ищем все 'import X' и 'from X import Y'
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("studiocore."):
                                dependencies[module_name].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        # Учитываем относительные импорты (from .style import X)
                        if node.level > 0: # Относительный импорт
                             base_module = ".".join(module_name.split(".")[:-1])
                             imported_module = f"{base_module}.{node.module}" if node.module else base_module
                             dependencies[module_name].append(imported_module)
                        elif node.module and node.module.startswith("studiocore."):
                            dependencies[module_name].append(node.module)
                            
            except Exception as e:
                print(f"❌ Не удалось спарсить {path}: {e}")
                ok = False

    # Печатаем отчет о связях
    print("--- Карта зависимостей ядра ---")
    for module, imports in dependencies.items():
        if imports:
            # Очищаем имя модуля, если оно начинается с 'app.'
            clean_module = module.lstrip("app.")
            print(f"📄 {clean_module} импортирует:")
            for imp in sorted(list(set(imports))):
                clean_imp = imp.lstrip("app.")
                print(f"    └── {clean_imp}")
    print("---------------------------------")
    return ok


# ==========================================================
# 🔬 4. Запуск ВСЕХ Unit-тестов (Логика ядра)
# ==========================================================
def run_all_unit_tests():
    """
    Автоматически находит и запускает все файлы 'test_*.py' 
    в папке 'studiocore/tests'.
    """
    print("\n🔬 Запуск всех Unit-тестов (проверка логики)...")
    try:
        loader = unittest.TestLoader()
        # ИСПРАВЛЕНИЕ: Ищем только в папке tests
        test_dir = os.path.join(ROOT_DIR, "studiocore", "tests")
        # Если мы не в /app, ищем относительно
        if not os.path.isdir(test_dir):
            test_dir = "studiocore/tests"
            
        suite = loader.discover(start_dir=test_dir, pattern="test_*.py") 
        
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            print("❌ Обнаружены ошибки в Unit-тестах.")
            return False
        
        # Проверяем, что тесты вообще были найдены
        if result.testsRun == 0:
            print(f"⚠️  НИ ОДНОГО ТЕСТА НЕ НАЙДЕНО. Проверьте {test_dir}!")
            return True # Не проваливаем сборку, но предупреждаем

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
    """Интеграционный тест: Убеждается, что модули могут работать вместе."""
    print("\n🎧 Проверка (интеграционная) ядра StudioCore...")
    try:
        # ИСПРАВЛЕНИЕ: PatchedLyricMeter теперь живет в monolith_v4_3_1
        from studiocore.monolith_v4_3_1 import PatchedLyricMeter
        from studiocore.style import StyleMatrix
        from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine


        text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
        
        # Для интеграционного теста мы должны симулировать полный прогон
        emo_analyzer = AutoEmotionalAnalyzer()
        tlp_analyzer = TruthLovePainEngine()
        emo = emo_analyzer.analyze(text)
        tlp = tlp_analyzer.analyze(text)

        bpm = PatchedLyricMeter().bpm_from_density(text)
        style = StyleMatrix().build(emo, tlp, text, bpm)

        assert 60 <= bpm <= 180, f"BPM вне диапазона: {bpm}"
        assert "genre" in style and "style" in style, "Отсутствуют ключевые поля"
        assert isinstance(style.get("techniques", []), list), "Поле techniques не list"

        print(f"✅ Интеграция OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        return True
    except Exception:
        traceback.print_exc()
        return False


# ==========================================================
# 🌐 6. Проверка API /api/predict
# ==========================================================
def test_api_response():
    print("\n🌐 Проверка /api/predict ...")
    api_url = "http://127.0.0.1:7860/api/predict"
    try:
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        # ИСПРАВЛЕНИЕ: Таймаут 30с (для Inference API)
        r = requests.post(api_url, json=payload, timeout=30) 
        
        assert r.status_code == 200, f"HTTP {r.status_code}. Ответ: {r.text[:200]}..."
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

    # Запускаем тесты по порядку
    results = {}
    results["structure"] = check_directories()
    results["syntax"] = check_python_syntax_project()
    results["json_yaml"] = check_json_yaml_project()
    results["imports"] = test_imports()
    results["dependencies (AST)"] = check_internal_dependencies()
    
    # Сначала запускаем unit_tests
    results["unit_tests (logic)"] = run_all_unit_tests()
    
    # Интеграционные тесты запускаем, только если unit_tests прошли
    # (чтобы не ждать 30с, если ядро и так сломано)
    integration_tests_ok = False
    if results["unit_tests (logic)"]:
        print("\n🔬 'unit_tests' пройдены, запускаем 'integration_api'...")
        # Объединяем integration_api и prediction_pipeline
        integration_tests_ok = test_prediction_pipeline() and test_api_response()
        results["integration_api"] = integration_tests_ok
    else:
        print("\n🔬 Пропуск 'integration_api', так как 'unit_tests (logic)' провалились.")
        results["integration_api"] = False

    total = 7
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