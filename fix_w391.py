#!/usr/bin/env python3
"""Удаляет пустые строки в конце файлов (W391)."""

import os


def fix_w391(filepath):
    """Удаляет пустые строки в конце файла."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Удаляем все пустые строки в конце
        while content.endswith("\n\n") or content.endswith("\r\n\r\n"):
            content = content.rstrip("\n\r")
            if content:
                content += "\n"

        # Если файл не пустой и не заканчивается на \n, добавляем один
        if content and not content.endswith("\n"):
            content += "\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Ошибка в {filepath}: {e}")
        return False


def main():
    files = [
        "api.py",
        "main/comprehensive_analysis.py",
        "main/deep_scan_audit.py",
        "studiocore/adapter.py",
        "studiocore/core_v6.py",
        "studiocore/emotion.py",
        "studiocore/rhythm.py",
        "studiocore/style.py",
        "studiocore/text_utils.py",
        "test_analysis.py",
        "test_text_analysis.py",
        "tests/auto_calibration.py",
        "tests/test_diagnostics_v8.py",
        "tests/test_integration_v7.py",
        "tests/test_state_persistence.py",
    ]

    fixed = 0
    for f in files:
        if os.path.exists(f):
            if fix_w391(f):
                fixed += 1
                print(f"✅ Исправлен: {f}")

    print(f"\nИсправлено файлов: {fixed}/{len(files)}")


if __name__ == "__main__":
    main()
