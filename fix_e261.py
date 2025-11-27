#!/usr/bin/env python3
"""Исправляет E261 (at least two spaces before inline comment)."""

import os
import subprocess


def fix_e261(filepath):
    """Добавляет два пробела перед комментариями, если их нет."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        changed = False

        for line in lines:
            # Пропускаем строки без комментариев
            if "#" not in line:
                new_lines.append(line)
                continue

            # Разделяем на код и комментарий
            comment_pos = line.find("#")
            code_part = line[:comment_pos].rstrip()
            comment_part = line[comment_pos:]

            # Если код пустой, оставляем как есть
            if not code_part:
                new_lines.append(line)
                continue

            # Проверяем, есть ли минимум 2 пробела перед комментарием
            if code_part.endswith("  "):
                # Уже есть 2 пробела
                new_lines.append(line)
            elif code_part.endswith(" "):
                # Только 1 пробел - добавляем еще один
                new_line = code_part + " " + comment_part
                new_lines.append(new_line)
                changed = True
            else:
                # Нет пробелов - добавляем 2
                new_line = code_part + "  " + comment_part
                new_lines.append(new_line)
                changed = True

        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        return False
    except Exception as e:
        print(f"Ошибка в {filepath}: {e}")
        return False


def main():
    result = subprocess.run(
        [
            "python3",
            "-m",
            "flake8",
            "--select=E261",
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

    fixed = 0
    for f in sorted(files):
        if fix_e261(f):
            fixed += 1
            print(f"✅ Исправлен: {f}")

    print(f"\nИсправлено файлов: {fixed}/{len(files)}")


if __name__ == "__main__":
    main()
