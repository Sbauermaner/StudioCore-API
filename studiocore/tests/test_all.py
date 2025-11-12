# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — COMPLETE SYSTEM VALIDATION
v8: Внедрен централизованный логгер
"""

# === 1. Активация логгера (ДО ВСЕХ ОСТАЛЬНЫХ ИМПОРТОВ) ===
try:
    from studiocore.logger import setup_logging
    setup_logging()
except ImportError:
    print("WARNING: studiocore.logger не найден. Используется стандартный print.")
    # Определяем 'log' как заглушку, если логгер не найден
    class PrintLogger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    log = PrintLogger()

import logging
import os, sys, json, ast, yaml, importlib, requests, traceback, re # 're' добавлен
from statistics import mean
import unittest

# Получаем настроенный логгер
log = logging.getLogger(__name__)


# === 🔧 Исправление пути импорта (чтобы test видели пакет) ===
# (Этот блок остается без изменений)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ИЗМЕНЕНИЕ: Проверяем только папки нашего проекта
ROOT_DIR = ROOT 
PROJECT_FOLDERS_TO_SCAN = ["studiocore", "app.py"] 
IGNORE_PATHS = ["/usr/", "/lib/", "/.git/", "/.venv/"]

log.info(f"ROOT проекта: {ROOT_DIR}")
log.info(f"Папки для сканирования: {PROJECT_FOLDERS_TO_SCAN}")


# ==========================================================
# 📁 1. Проверка структуры и синтаксиса (v3)
# ==========================================================
def _is_ignored(path):
    """Проверяет, нужно ли игнорировать путь."""
    for ignored in IGNORE_PATHS:
        if ignored in path:
            return True
    return False

def check_directories():
    log.info("📂 Проверка структуры...")
    required = [os.path.join(ROOT_DIR, "studiocore"), os.path.join(ROOT_DIR, "studiocore/tests")]
    missing = [d for d in required if not os.path.isdir(d)]
    if missing:
        log.error(f"❌ Отсутствуют директории: {missing}")
        return False
    log.info("✅ Структура в порядке.")
    return True

def check_python_syntax_project():
    log.info("\n🐍 Проверка синтаксиса Python (проект)...")
    all_ok = True
    files_to_scan = []
    
    for item in PROJECT_FOLDERS_TO_SCAN:
        item_path = os.path.join(ROOT_DIR, item)
        if os.path.isfile(item_path) and item.endswith(".py"):
            files_to_scan.append(item_path)
        elif os.path.isdir(item_path):
            for root, _, files in os.walk(item_path):
                if _is_ignored(root):
                    continue
                for f in files:
                    if f.endswith(".py"):
                        files_to_scan.append(os.path.join(root, f))
                        
    log.debug(f"Найдено {len(files_to_scan)} .py файлов для проверки.")
    
    for path in files_to_scan:
        try:
            with open(path, "r", encoding="utf-8") as fp:
                ast.parse(fp.read(), filename=path)
            log.info(f"✅ OK: {path}")
        except SyntaxError as e:
            log.error(f"❌ Ошибка синтаксиса: {path} → {e}")
            all_ok = False
        except Exception as e:
            log.error(f"❌ Не удалось прочитать файл: {path} → {e}")
            all_ok = False
    return all_ok

def check_json_yaml_project():
    log.info("\n🧩 Проверка JSON / YAML (проект)...")
    ok = True
    files_to_scan = []
    
    # 1. Проверяем корень на config-файлы
    for item in os.listdir(ROOT_DIR):
        if item.endswith(".json") or item.endswith(".yaml") or item.endswith(".yml"):
             files_to_scan.append(os.path.join(ROOT_DIR, item))

    # 2. Проверяем папки проекта
    for folder in PROJECT_FOLDERS_TO_SCAN:
        item_path = os.path.join(ROOT_DIR, folder)
        if os.path.isdir(item_path):
            for root, _, files in os.walk(item_path):
                if _is_ignored(root):
                    continue
                for f in files:
                    if f.endswith(".json") or f.endswith((".yml", ".yaml")):
                        files_to_scan.append(os.path.join(root, f))
                        
    log.debug(f"Найдено {len(files_to_scan)} .json/.yaml файлов для проверки.")

    for path in files_to_scan:
        if path.endswith(".json"):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    json.load(f)
                log.info(f"✅ JSON OK: {path}")
            except Exception as e:
                log.error(f"❌ JSON Error: {path} → {e}")
                ok = False
        elif path.endswith((".yml", ".yaml")):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                log.info(f"✅ YAML OK: {path}")
            except Exception as e:
                log.error(f"❌ YAML Error: {path} → {e}")
                ok = False
    return ok

# ==========================================================
# 🧠 2. Проверка импорта (без изменений)
# ==========================================================
# (Загрузка модулей происходит в __main__, здесь только проверка)
MODULES = [
    "studiocore.text_utils",
    "studiocore.emotion",
    "studiocore.rhythm",
    "studiocore.vocals",
    "studiocore.style",
    "studiocore.tone",
    "studiocore.adapter"
]

def test_imports():
    log.info("\n🧠 Проверка импорта модулей StudioCore...")
    all_ok = True
    for m in MODULES:
        try:
            importlib.import_module(m)
            log.info(f"✅ Импортирован: {m}")
        except Exception as e:
            log.error(f"❌ Ошибка импорта: {m} — {e}")
            log.error(traceback.format_exc())
            all_ok = False
    return all_ok

# ==========================================================
# 🕸️ 3. Проверка внутренних связей (v2 - Исправлен re)
# ==========================================================
def check_internal_dependencies():
    """
    Сканирует все .py файлы в 'studiocore' и ищет внутренние импорты.
    """
    log.info("\n🕸️  Проверка внутренних связей (studiocore.*)...")
    dependencies = {}
    ok = True
    
    scan_dir = os.path.join(ROOT_DIR, "studiocore")
    
    for root, _, files in os.walk(scan_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            
            path = os.path.join(root, f)
            # //studiocore/tests/test_all.py -> tests.test_all
            module_name = path.replace(scan_dir + os.path.sep, "") \
                              .replace(os.path.sep, ".") \
                              .replace(".py", "")
            
            # Убираем __init__
            module_name = module_name.replace(".__init__", "")
            if module_name == "__init__": continue

            dependencies[module_name] = []
            
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    tree = ast.parse(fp.read(), filename=path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("studiocore.") or alias.name in MODULES:
                                dependencies[module_name].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        # from . import emotion -> studiocore.emotion
                        if node.level > 0 and node.module:
                            full_module = "." * node.level + node.module
                            # Пытаемся разрешить относительный импорт
                            try:
                                # Разрешаем .emotion -> studiocore.emotion
                                abs_module = importlib.util.resolve_name(full_module, f"studiocore.{module_name}")
                                if abs_module.startswith("studiocore."):
                                    dependencies[module_name].append(abs_module.split('.')[1])
                            except ImportError:
                                # Если не получилось, просто используем имя модуля
                                if node.module.startswith("studiocore."):
                                     dependencies[module_name].append(node.module)
                                elif f"studiocore.{node.module}" in MODULES:
                                     dependencies[module_name].append(node.module)

                        elif node.module and node.module.startswith("studiocore."):
                             dependencies[module_name].append(node.module)

            except Exception as e:
                log.error(f"❌ Не удалось спарсить {path}: {e}")
                ok = False

    # Печатаем отчет о связях
    log.info("--- Карта зависимостей ядра ---")
    for module, imports in dependencies.items():
        if imports:
            # Очищаем и форматируем (убираем 'studiocore.')
            clean_imports = sorted(list(set(
                imp.replace("studiocore.", "") for imp in imports
            )))
            log.info(f"📄 {module} импортирует:")
            for imp in clean_imports:
                if imp != module: # Не показываем импорт самого себя
                    log.info(f"    └── {imp}")
    log.info("---------------------------------")
    return ok


# ==========================================================
# 🔬 4. Запуск ВСЕХ Unit-тестов (v3)
# ==========================================================
def run_all_unit_tests():
    """
    Автоматически находит и запускает все 'test_*.py' в папке /tests.
    """
    log.info("\n🔬 Запуск всех Unit-тестов (проверка логики)...")
    try:
        loader = unittest.TestLoader()
        test_dir = os.path.join(ROOT_DIR, "studiocore/tests")
        log.debug(f"Поиск тестов в: {test_dir}")
        
        # Ищем тесты ТОЛЬКО в папке tests, исключая test_all.py
        suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
        
        # Фильтруем test_all.py, чтобы он не запустил сам себя
        filtered_suite = unittest.TestSuite()
        for test_suite in suite:
            for test_case in test_suite:
                if "test_all" not in str(test_case):
                     filtered_suite.addTest(test_case)
        
        log.debug(f"Найдено тестов: {filtered_suite.countTestCases()}")
        if filtered_suite.countTestCases() == 0:
            log.warning("⚠️  НИ ОДНОГО ТЕСТА НЕ НАЙДЕНО. Проверьте test_*.py файлы!")
            return True # Не проваливаем сборку, если тестов нет

        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(filtered_suite)
        
        if not result.wasSuccessful():
            log.error("❌ Обнаружены ошибки в Unit-тестах.")
            return False
        
        log.info(f"✅ Все Unit-тесты ({filtered_suite.countTestCases()}) пройдены.")
        return True
    except Exception:
        log.critical("❌ КРИТИЧЕСКАЯ ОШИБКА при запуске тестов:")
        log.critical(traceback.format_exc())
        return False

# ==========================================================
# 🎧 5. Проверка конкретного пайплайна (Интеграционный) (v2)
# ==========================================================
def test_prediction_pipeline():
    log.info("\n🎧 Проверка (интеграционная) ядра StudioCore...")
    try:
        # v3 - Исправлен ImportError
        from studiocore.monolith_v4_3_1 import PatchedLyricMeter
        from studiocore.style import StyleMatrix # Используем алиас
        from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine
        
        emo_engine = AutoEmotionalAnalyzer()
        tlp_engine = TruthLovePainEngine()
        
        text = "Я встаю, когда солнце касается крыш, когда воздух поёт о свободе..."
        
        log.debug("Вызов: emo_engine.analyze (integration test)")
        emo = emo_engine.analyze(text)
        log.debug("Вызов: tlp_engine.analyze (integration test)")
        tlp = tlp_engine.analyze(text)
        log.debug("Вызов: PatchedLyricMeter.bpm_from_density (integration test)")
        bpm = PatchedLyricMeter().bpm_from_density(text, emo)
        log.debug("Вызов: StyleMatrix.build (integration test)")
        style = StyleMatrix().build(emo, tlp, text, bpm, {})

        assert 60 <= bpm <= 180, f"BPM вне диапазона: {bpm}"
        assert "genre" in style and "style" in style, "Отсутствуют ключевые поля"
        assert isinstance(style.get("techniques", []), list), "Поле techniques не list"

        log.info(f"✅ Интеграция OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        return True
    except Exception:
        log.error("❌ Ошибка интеграционного теста ядра:")
        log.error(traceback.format_exc())
        return False


# ==========================================================
# 🌐 6. Проверка API /api/predict (v3)
# ==========================================================
def test_api_response():
    log.info("\n🌐 Проверка /api/predict ...")
    api_url = "http://127.0.0.1:7860/api/predict"
    try:
        payload = {
            "text": "Я тону, когда солнце уходит вдаль...",
            "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
        }
        # v7 - Увеличен таймаут до 20с (для "Плана C")
        r = requests.post(api_url, json=payload, timeout=20)
        
        assert r.status_code == 200, f"HTTP {r.status_code}. Ответ: {r.text[:200]}"
        
        data = r.json()
        log.info(f"✅ API OK | BPM={data.get('bpm')} | Style={data.get('style')}")
        return True
    except requests.exceptions.ReadTimeout as e:
        log.error(f"❌ Ошибка API: Таймаут (ReadTimeout) (>{20}с). Сервер (CPU) перегружен.")
        log.error(f"URL: {api_url} | {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        log.error(f"❌ Ошибка API: Не удалось подключиться (ConnectionError). Сервер не запущен?")
        log.error(f"URL: {api_url} | {e}")
        return False
    except Exception as e:
        log.error(f"❌ Ошибка API (Общая): {e} (Проверьте URL: {api_url})")
        log.error(traceback.format_exc())
        return False


# ==========================================================
# 🧩 7. Запуск всех тестов и финальный отчёт (v3)
# ==========================================================
if __name__ == "__main__":
    log.info("\n" + "="*40)
    log.info("🧩 StudioCore v5.2.1 — FULL SYSTEM CHECK")
    log.info("="*40)

    # v3 - Разделены 'integration_core' и 'integration_api'
    total = 8
    results = {
        "structure": check_directories(),
        "syntax": check_python_syntax_project(),
        "json_yaml": check_json_yaml_project(),
        "imports": test_imports(),
        "dependencies (AST)": check_internal_dependencies(),
        "unit_tests (logic)": run_all_unit_tests(),
        "integration_core": test_prediction_pipeline(),
        "integration_api": False # Запускаем только если unit-тесты и core прошли
    }

    # API-тест (самый хрупкий) запускаем только если все остальное в порядке
    if results["unit_tests (logic)"] and results["integration_core"]:
        results["integration_api"] = test_api_response()
    else:
        log.warning("\n🔬 Пропуск 'integration_api', так как 'unit_tests (logic)' или 'integration_core' провалились.")


    passed = sum(1 for k in results.values() if k)
    percent = round(passed / total * 100, 2)

    log.info("\n" + "="*20 + " 🧾 ИТОГОВЫЙ ОТЧЁТ " + "="*20)
    for name, ok in results.items():
        log.info(f"{'✅' if ok else '❌'} {name}")

    log.info(f"\n🎯 ПРОЙДЕНО: {passed}/{total} тестов ({percent}%)")

    if percent == 100:
        log.info("🚀 Система полностью функциональна.")
    elif percent >= 75: # 6/8
        log.warning("⚠️ Система работает, но требует проверки некоторых модулей.")
    else:
        log.error("❌ Обнаружены критические ошибки, требуется ревизия.")

    # Возвращаем код ошибки, если тесты провалены
    if passed != total:
        sys.exit(1)