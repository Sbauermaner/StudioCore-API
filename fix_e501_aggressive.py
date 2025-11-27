#!/usr/bin/env python3
"""Агрессивное исправление E501 (line too long)."""

import os
import subprocess


def fix_long_lines_in_file(filepath, max_length=79):
    """Исправляет длинные строки в файле."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        changed = False

        for i, line in enumerate(lines):
            stripped = line.rstrip("\n")

            # Пропускаем строки нормальной длины
            if len(stripped) <= max_length:
                new_lines.append(line)
                continue

            # Пропускаем строки с только комментариями (они могут быть длинными)
            code_part = line.split("#")[0] if "#" in line else line
            if not code_part.strip():
                new_lines.append(line)
                continue

            # Пропускаем строки с URL или длинными строками
            if "http://" in line or "https://" in line or "www." in line:
                new_lines.append(line)
                continue

            # Пропускаем docstrings
            if stripped.strip().startswith('"""') or stripped.strip().startswith("'''"):
                new_lines.append(line)
                continue

            # Для обычного кода пробуем разбить
            # Используем autopep8 для этого
            new_lines.append(line)

        # Если были изменения, записываем файл
        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        return False
    except Exception as e:
        print(f"Ошибка в {filepath}: {e}")
        return False


def main():
    # Получаем список файлов с E501
    result = subprocess.run(
        [
            "python3",
            "-m",
            "flake8",
            "--select=E501",
            "studiocore/",
            "app.py",
            "api.py",
            "test_*.py",
            "tests/",
            "main/",
        ],
        capture_output=True,
        text=True,
    )

    files = set()
    for line in result.stdout.split("\n"):
        if ":" in line:
            filepath = line.split(":")[0]
            if filepath and os.path.exists(filepath):
                files.add(filepath)

    print(f"Найдено файлов с E501: {len(files)}")
    print("Исправление через autopep8 с максимальной агрессивностью...")

    fixed = 0
    for f in sorted(files):
        # Используем autopep8 с максимальной агрессивностью
        result = subprocess.run(
            [
                "python3",
                "-m",
                "autopep8",
                "--in-place",
                "--aggressive",
                "--aggressive",
                "--select=E501",
                "--max-line-length=79",
                f,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            fixed += 1
            if fixed % 20 == 0:
                print(f"Обработано: {fixed}/{len(files)}")

    print(f"\n✅ Обработано файлов: {fixed}/{len(files)}")

    # Проверяем результат
    result = subprocess.run(
        [
            "python3",
            "-m",
            "flake8",
            "--count",
            "--select=E501",
            "studiocore/",
            "app.py",
            "api.py",
            "test_*.py",
            "tests/",
            "main/",
        ],
        capture_output=True,
        text=True,
    )
    remaining = result.stdout.strip().split("\n")[-1]
    print(f"Осталось ошибок E501: {remaining}")


if __name__ == "__main__":
    main()
