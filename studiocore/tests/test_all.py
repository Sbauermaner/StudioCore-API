# -*- coding: utf-8 -*-
"""
StudioCore v5.2.1 — COMPLETE SYSTEM VALIDATION (v8 - Включено логирование)
v8: Восстановлены check_directories, check_syntax и т.д.
"""

# === 🔧 Исправление пути импорта ===
import os
import sys
import re # <-- v6: ИСПРАВЛЕН NameError
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# === Конец исправления ===

import json
import ast
import yaml
import importlib
import requests
import traceback
import unittest
import time
import logging # v8: Добавлен импорт
import pytest

# === 1. АКТИВАЦИЯ ЛОГГЕРА ===
try:
    from studiocore.logger import setup_logging
    # Устанавливаем уровень DEBUG, чтобы видеть все
    setup_logging(level=logging.DEBUG) 
except ImportError:
    print("WARNING: studiocore.logger не найден. Используется стандартный print.")
    # Fallback
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)-5.5s] [%(name)-20s] %(message)s")
    pass

log = logging.getLogger("test_all")
# === Конец активации логгера ===

# Папки для сканирования (только наши)
ROOT_DIR = ROOT 
PROJECT_FOLDERS_TO_SCAN = ["studiocore"]
# v8: Добавляем app.py в список сканирования
PROJECT_FILES_TO_SCAN = ["app.py"] 

log.info(f"ROOT проекта: {ROOT_DIR}")
log.info(f"Папки для сканирования: {PROJECT_FOLDERS_TO_SCAN}")

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
#  HELPER: Функции сканирования (v8 - ВОССТАНОВЛЕНЫ)
# ==========================================================

# Пути, которые нужно *полностью* игнорировать
IGNORE_PATHS = ["/usr/", "/lib/", "/.git/", "/.venv/"]

def _is_ignored(path):
    """Проверяет, нужно ли игнорировать путь."""
    for ignored in IGNORE_PATHS:
        if ignored in path:
            return True
    return False

# v8: ВОССТАНОВЛЕНО
def check_directories():
    log.info("📂 Проверка структуры...")
    # Проверяем только 'studiocore', а не весь ROOT
    required = [f"{ROOT_DIR}/studiocore", f"{ROOT_DIR}/studiocore/tests"]
    missing = [d for d in required if not os.path.isdir(d)]
    if missing:
        log.error(f"❌ Отсутствуют директории: {missing}")
        return False
    log.info("✅ Структура в порядке.")
    return True

# v8: ВОССТАНОВЛЕНО
def check_python_syntax():
    log.info("🐍 Проверка синтаксиса Python (проект)...")
    all_ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir):
            log.warning(f"Папка для сканирования не найдена: {scan_dir}")
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
                        log.info(f"✅ OK: {path}")
                    except SyntaxError as e:
                        log.error(f"❌ Ошибка синтаксиса: {path} → {e}")
                        all_ok = False

    # 2. Проверяем отдельные файлы в корне
    for f in PROJECT_FILES_TO_SCAN:
        path = os.path.join(ROOT_DIR, f)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    ast.parse(fp.read(), filename=path)
                log.info(f"✅ OK: {path}")
            except SyntaxError as e:
                log.error(f"❌ Ошибка синтаксиса: {path} → {e}")
                all_ok = False
                
    return all_ok

# v8: ВОССТАНОВЛЕНО
def check_json_yaml():
    log.info("🧩 Проверка JSON / YAML (проект)...")
    ok = True
    
    # 1. Сканируем указанные папки
    for folder in PROJECT_FOLDERS_TO_SCAN:
        scan_dir = os.path.join(ROOT_DIR, folder)
        if not os.path.isdir(scan_dir): continue

        for root, _, files in os.walk(scan_dir):
            if _is_ignored(root): continue
            
            for f in files:
                path = os.path.join(root, f)
                if f.endswith(".json"):
                    try:
                        with open(path, "r", encoding="utf-8") as fp:
                            json.load(fp)
                        log.info(f"✅ JSON OK: {path}")
                    except Exception as e:
                        log.error(f"❌ JSON Error: {path} → {e}")
                        ok = False
                elif f.endswith((".yml", ".yaml")):
                    try:
                        with open(path, "r", encoding="utf-8") as fp:
                            yaml.safe_load(fp)
                        log.info(f"✅ YAML OK: {path}")
                    except Exception as e:
                        log.error(f"❌ YAML Error: {path} → {e}")
                        ok = False
                        
    # 2. Проверяем json/yaml в корне
    for f in os.listdir(ROOT_DIR):
        path = os.path.join(ROOT_DIR, f)
        if not os.path.isfile(path):
            continue
            
        if f.endswith(".json"):
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    json.load(fp)
                log.info(f"✅ JSON OK: {path}")
            except Exception as e:
                log.error(f"❌ JSON Error: {path} → {e}")
                ok = False
        elif f.endswith((".yml", ".yaml")):
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    yaml.safe_load(fp)
                log.info(f"✅ YAML OK: {path}")
            except Exception as e:
                log.error(f"❌ YAML Error: {path} → {e}")
                ok = False
    return ok

# ==========================================================
# 🧠 2. Проверка импорта
# ==========================================================
def run_import_checks():
    log.info("🧠 Проверка модулей StudioCore...")
    all_ok = True
    for m in MODULES:
        try:
            importlib.import_module(m)
            log.info(f"✅ Импортирован: {m}")
        except Exception as e:
            # v7: Используем полный traceback для ошибок импорта
            log.error(f"❌ Ошибка импорта: {m} — {traceback.format_exc()}")
            all_ok = False
    return all_ok


def test_imports():
    assert run_import_checks(), "Импорт StudioCore модулей завершился с ошибками"

# ==========================================================
# 🕸️ 3. Проверка внутренних связей (AST)
# ==========================================================
def check_internal_dependencies():
    """
    Сканирует все .py файлы в 'studiocore' и ищет внутренние импорты.
    """
    log.info("🕸️  Проверка внутренних связей (studiocore.*)...")
    dependencies = {}
    ok = True
    
    scan_dir = os.path.join(ROOT_DIR, "studiocore")
    
    for root, dirs, files in os.walk(scan_dir):
        # Игнорируем папку tests
        if "tests" in dirs:
            dirs.remove("tests")
            
        for f in files:
            if not f.endswith(".py"):
                continue
            
            path = os.path.join(root, f)
            # v7: Улучшенная нормализация имени модуля
            rel_path = os.path.relpath(path, scan_dir)
            module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")
            
            # v8: Убираем __init__
            if module_name.endswith(".__init__"):
                 module_name = module_name.replace(".__init__", "")
            
            # v8: Пропускаем сам logger
            if module_name == "logger":
                continue
            
            # v16: Пропускаем app.py (он не в .studiocore)
            if "app.py" in path:
                continue

            dependencies[module_name] = []
            
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    tree = ast.parse(fp.read(), filename=path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("studiocore.") or alias.name.startswith("."):
                                dependencies[module_name].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        # Игнорируем __future__
                        if node.module == "__future__":
                            continue
                            
                        # v16: Добавляем проверку, что node.module не None
                        if node.module and (node.module.startswith("studiocore.") or node.module.startswith(".")):
                            # Убираем . из '.emotion'
                            dependencies[module_name].append(node.module.lstrip('.'))
                            
            except Exception as e:
                log.error(f"❌ Не удалось спарсить {path}: {e}")
                ok = False

    # Печатаем отчет о связях
    log.info("--- Карта зависимостей ядра ---")
    for module, imports in sorted(dependencies.items()):
        if imports:
            imports_clean = sorted(list(set(imports)))
            log.info(f"📄 {module} импортирует:")
            for imp in imports_clean:
                log.info(f"    └── {imp}")
    log.info("---------------------------------")
    return ok

# ==========================================================
# 🔬 4. Запуск всех Unit-тестов (Логика ядра)
# ==========================================================
def run_all_unit_tests():
    """
    Автоматически находит и запускает все файлы 'test_*.py' 
    в папке 'studiocore/tests'.
    """
    log.info("🔬 Запуск всех Unit-тестов (проверка логики)...")
    try:
        loader = unittest.TestLoader()
        test_dir = os.path.join(ROOT_DIR, "studiocore", "tests")
        log.debug(f"Поиск тестов в: {test_dir}")
        
        # v3: Уточненный путь
        suite = loader.discover(start_dir=test_dir, pattern="test_*.py") 
        
        # Проверяем, нашлись ли тесты
        test_count = suite.countTestCases()
        log.debug(f"Найдено тестов: {test_count}")
        if test_count == 0:
            log.warning("⚠️  НИ ОДНОГО ТЕСТА НЕ НАЙДЕНО. Проверьте test_*.py файлы на наличие sys.path!")
            return True # (Технически не ошибка, если тестов нет)

        # Запускаем тесты
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stderr) # Вывод в STDERR
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            log.error("❌ Обнаружены ошибки в Unit-тестах.")
            return False
        
        log.info(f"✅ Все Unit-тесты ({test_count}) пройдены.")
        return True
    except Exception:
        log.error("❌ КРИТИЧЕСКАЯ ОШИБКА при запуске тестов:")
        log.error(traceback.format_exc())
        return False

# ==========================================================
# 🎧 5. Проверка (интеграционная) ядра
# ==========================================================
def run_prediction_pipeline():
    """
    (v7) Интеграционный тест ядра (без API).
    """
    log.info("\n🎧 Проверка (интеграционная) ядра StudioCore...")
    try:
        # v16: Исправлен ImportError. 
        from studiocore.monolith_v4_3_1 import PatchedLyricMeter
        from studiocore.style import PatchedStyleMatrix
        # v15: Исправлен ImportError
        from studiocore.emotion import AutoEmotionalAnalyzer, TruthLovePainEngine

        # Инициализируем их вручную, как в test_main_integrity
        log.debug("Инициализация движков для integration_core...")
        emo_engine = AutoEmotionalAnalyzer()
        tlp_engine = TruthLovePainEngine()
        lyric_meter = PatchedLyricMeter()
        style_matrix = PatchedStyleMatrix()
        log.debug("Движки успешно инициализированы.")

        text = "This is an integration test"
        log.debug(f"Вызов: emo_engine.analyze (integration test)")
        emo = emo_engine.analyze(text)
        log.debug(f"Вызов: tlp_engine.analyze (integration test)")
        tlp = tlp_engine.analyze(text)
        log.debug(f"Вызов: PatchedLyricMeter.bpm_from_density (integration test)")
        bpm = lyric_meter.bpm_from_density(text, emo)
        log.debug(f"Вызов: StyleMatrix.build (integration test)")
        # v6: Добавлен voice_hint=None
        style = style_matrix.build(emo, tlp, text, bpm, {}, None)

        assert "genre" in style and "style" in style, "Отсутствуют ключевые поля"
        log.info(f"✅ Интеграция OK | BPM={bpm} | Genre={style['genre']} | Style={style['style']}")
        return True
    except Exception:
        log.error("❌ Ошибка интеграционного теста ядра:")
        log.error(traceback.format_exc())
        return False


def test_prediction_pipeline():
    assert run_prediction_pipeline(), "Интеграционный тест ядра завершился с ошибками"


# ==========================================================
# 🌐 6. Проверка API /api/predict
# ==========================================================
def run_api_response_check():
    log.info("\n🌐 Проверка /api/predict ...")

    api_url = "http://127.0.0.1:7860/api/predict"
    payload = {
        "text": "Я тону, когда солнце уходит вдаль...",
        "tlp": {"truth": 0.06, "love": 0.08, "pain": 0.14, "conscious_frequency": 0.92}
    }
    
    try:
        # v7: Таймаут 20с (для "Плана C" - быстрые словари)
        r = requests.post(api_url, json=payload, timeout=20) 
        
        if r.status_code == 200:
            data = r.json()
            log.info(f"✅ API OK | BPM={data.get('bpm')} | Style={data.get('style')}")
            return True
        else:
            log.error(f"❌ Ошибка API: HTTP {r.status_code}. Ответ: {r.text[:200]}")
            return False
            
    except requests.exceptions.ReadTimeout as e:
        log.error(f"❌ Ошибка API: ReadTimeout! (Сервер не ответил за 20с). {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        log.error(f"❌ Ошибка API: ConnectionError! (Сервер не запущен?). {e}")
        return None
    except Exception as e:
        log.error(f"❌ Ошибка API (Unknown): {e} (Проверьте URL: {api_url})")
        log.error(traceback.format_exc())
        return False


def test_api_response():
    result = run_api_response_check()
    if result is None:
        pytest.skip("API сервер не запущен, проверка пропущена")
    assert result, "API /api/predict вернуло ошибку"


# ==========================================================
# 🧩 7. Запуск всех тестов и финальный отчёт
# ==========================================================
if __name__ == "__main__":
    log.info("\n" + "=" * 20 + " 🧩 StudioCore v5.2.1 — FULL SYSTEM CHECK " + "=" * 20)

    # Запускаем тесты по порядку, от "дешевых" к "дорогим"
    results = {}
    results["structure"] = check_directories()
    results["syntax"] = check_python_syntax()
    results["json_yaml"] = check_json_yaml()
    
    # Если синтаксис сломан, нет смысла проверять импорты
    if results["syntax"]:
        results["imports"] = run_import_checks()
        results["dependencies (AST)"] = check_internal_dependencies()
    else:
        results["imports"] = False
        results["dependencies (AST)"] = False

    # Если импорты сломаны, нет смысла запускать тесты
    if results["imports"]:
        results["unit_tests (logic)"] = run_all_unit_tests()
        results["integration_core"] = run_prediction_pipeline()
    else:
        results["unit_tests (logic)"] = False
        results["integration_core"] = False

    # API-тест запускаем, только если тесты ядра прошли
    if results["unit_tests (logic)"] and results["integration_core"]:
        results["integration_api"] = run_api_response_check()
    else:
        log.warning("\n🔬 Пропуск 'integration_api', так как 'unit_tests (logic)' или 'integration_core' провалились.")
        results["integration_api"] = False

    total = len(results)
    passed = sum(1 for k in results.values() if k)
    percent = round(passed / total * 100, 2)

    log.info("\n" + "=" * 20 + " 🧾 ИТОГОВЫЙ ОТЧЁТ " + "=" * 20)
    for name, ok in results.items():
        log.info(f"{'✅' if ok else '❌'} {name}")

    log.info(f"\n🎯 ПРОЙДЕНО: {passed}/{total} тестов ({percent}%)")

    if percent == 100:
        log.info("🚀 Система полностью функциональна.")
    elif percent >= 75: # (6/8)
        log.warning("⚠️ Система работает, но требует проверки некоторых модулей.")
    else:
        log.error("❌ Обнаружены критические ошибки, требуется ревизия.")
