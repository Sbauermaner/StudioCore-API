import os
import ast

# Конфигурация
TARGET_DIR = "studiocore"
REQUIRED_METHODS = {"HybridGenreEngine": ["resolve"]}
CRITICAL_FILES = [
    "universal_frequency_engine.py",
    "hybrid_instrumentation_layer.py",
    "neutral_mode_pre_finalizer.py",
]


def check_syntax(file_path):
    """Проверяет файл на синтаксические ошибки."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Read Error: {e}"


def check_class_methods(file_path):
    """Проверяет наличие обязательных методов (исправление аудита)."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name in REQUIRED_METHODS:
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                missing = [m for m in REQUIRED_METHODS[node.name] if m not in methods]
                if missing:
                    return (
                        False,
                        f"CRITICAL: Class '{node.name}' missing methods: {missing}",
                    )
    return True, "OK"


def scan_project():
    print(f"=== ЗАПУСК ПОЛНОГО СКАНИРОВАНИЯ: {TARGET_DIR} ===\n")
    error_count = 0
    checked_files = 0

    # 1. Проверка существования файлов из аудита
    print("--- Проверка структуры файлов ---")
    for fname in CRITICAL_FILES:
        path = os.path.join(TARGET_DIR, fname)
        if not os.path.exists(path):
            print(f"[FAIL] Отсутствует обязательный модуль: {fname}")
            error_count += 1
        else:
            print(f"[OK] Модуль найден: {fname}")

    print("\n--- Сканирование кода (Синтаксис и Логика) ---")
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                checked_files += 1
                full_path = os.path.join(root, file)

                # А. Синтаксис
                valid, msg = check_syntax(full_path)
                if not valid:
                    print(f"[ERROR] {file}: {msg}")
                    error_count += 1
                    continue

                # Б. Проверка специфичных классов (HybridGenreEngine)
                if "hybrid_genre_engine.py" in file:
                    valid_logic, msg_logic = check_class_methods(full_path)
                    if not valid_logic:
                        print(f"[FAIL] {file}: {msg_logic}")
                        error_count += 1
                        continue

    print("\n" + "=" * 30)
    if error_count == 0:
        print(f"ИТОГ: УСПЕХ. Проверено файлов: {checked_files}. Ошибок: 0.")
        print("Система готова к запуску.")
    else:
        print(f"ИТОГ: ОБНАРУЖЕНО ОШИБОК: {error_count}. См. лог выше.")


if __name__ == "__main__":
    scan_project()
