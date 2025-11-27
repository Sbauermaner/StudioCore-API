#!/usr/bin/env python3
"""Исправляет E501 (line too long) - разбивает длинные строки."""

import os
import subprocess


def fix_e501_line(line, max_length=79):
    """Разбивает длинную строку на несколько, если возможно."""
    if len(line.rstrip("\n")) <= max_length:
        return line

    # Если это комментарий, просто обрезаем или переносим
    stripped = line.lstrip()
    if stripped.startswith("#"):
        # Для комментариев просто обрезаем или переносим
        if len(line) > max_length + 1:
            # Пробуем разбить комментарий
            indent = len(line) - len(stripped)
            comment = stripped[1:].strip()
            if len(comment) > max_length - indent - 2:
                # Разбиваем комментарий
                words = comment.split()
                new_lines = []
                current_line = " " * indent + "# "
                for word in words:
                    if len(current_line + word) > max_length:
                        new_lines.append(current_line.rstrip() + "\n")
                        current_line = " " * indent + "# " + word + " "
                    else:
                        current_line += word + " "
                new_lines.append(current_line.rstrip() + "\n")
                return "".join(new_lines)
        return line

    # Если это строка с кавычками, не трогаем
    if ('"' in line or "'" in line) and not line.strip().startswith("#"):
        # Проверяем, не является ли это f-string или обычной строкой
        if line.strip().startswith(('f"', "f'", 'f"""', "f'''")):
            # Для f-strings можно попробовать разбить, но это сложно
            # Пока оставляем как есть
            return line

    # Для обычного кода пробуем разбить по операторам
    # Это сложная задача, поэтому используем autopep8 подход
    # Просто возвращаем исходную строку - autopep8 лучше справится
    return line


def fix_e501_file(filepath):
    """Исправляет E501 в файле."""
    try:
        # Используем autopep8 для автоматического исправления
        import subprocess

        result = subprocess.run(
            [
                "python3",
                "-m",
                "autopep8",
                "--in-place",
                "--select=E501",
                "--max-line-length=79",
                filepath,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True
        return False
    except Exception as e:
        print(f"Ошибка в {filepath}: {e}")
        return False


def main():
    # Получаем список файлов с E501 ошибками
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
    print("Исправление длинных строк через autopep8...")

    fixed = 0
    for f in sorted(files):
        if fix_e501_file(f):
            fixed += 1
            if fixed % 50 == 0:
                print(f"Обработано: {fixed}/{len(files)}")

    print(f"\n✅ Обработано файлов: {fixed}/{len(files)}")
    print("Примечание: autopep8 может не исправить все случаи автоматически.")


if __name__ == "__main__":
    main()
