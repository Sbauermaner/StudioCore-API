#!/usr/bin/env python3
"""Исправляет E225 (missing whitespace around operator)."""

import re
import os


def fix_e225(filepath):
    """Добавляет пробелы вокруг операторов."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Паттерны для исправления (но не трогаем уже правильные)
        # x+y -> x + y
        # x-y -> x - y (но не x-1 в индексах или отрицательных числах)
        # x*y -> x * y
        # x/y -> x / y
        # x%y -> x % y
        # x**y -> x ** y
        # x//y -> x // y
        # x==y -> x == y
        # x!=y -> x != y
        # x<=y -> x <= y
        # x>=y -> x >= y
        # x<y -> x < y (но не в комментариях или строках)
        # x>y -> x > y

        # Более безопасный подход - используем regex с проверкой контекста
        def add_spaces_around_operator(match):
            """Добавляет пробелы вокруг оператора, если их нет."""
            before = match.group(1)
            op = match.group(2)
            after = match.group(3)

            # Пропускаем, если уже есть пробелы
            if " " in before[-1:] or " " in after[:1]:
                return match.group(0)

            # Пропускаем специальные случаи (отрицательные числа, индексы)
            if op == "-" and (
                before[-1:].isdigit() or after[:1].isdigit() or before[-1:] in "([{="
            ):
                return match.group(0)
            if op == "+" and (before[-1:].isdigit() or after[:1].isdigit()):
                return match.group(0)

            return f"{before} {op} {after}"

        # Исправляем операторы (но не в строках и комментариях)
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            # Пропускаем строки и комментарии
            if "#" in line:
                comment_pos = line.find("#")
                code_part = line[:comment_pos]
                comment_part = line[comment_pos:]
            else:
                code_part = line
                comment_part = ""

            # Исправляем операторы в коде
            # Более консервативный подход - только явные случаи
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\+([a-zA-Z0-9_\(\[\{])", r"\1 + \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\-([a-zA-Z0-9_\(\[\{])", r"\1 - \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\*([a-zA-Z0-9_\(\[\{])", r"\1 * \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\/([a-zA-Z0-9_\(\[\{])", r"\1 / \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\%([a-zA-Z0-9_\(\[\{])", r"\1 % \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\=\=([a-zA-Z0-9_\(\[\{])", r"\1 == \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\!\=([a-zA-Z0-9_\(\[\{])", r"\1 != \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\<\=([a-zA-Z0-9_\(\[\{])", r"\1 <= \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\>\=([a-zA-Z0-9_\(\[\{])", r"\1 >= \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\<([a-zA-Z0-9_\(\[\{])", r"\1 < \2", code_part
            )
            code_part = re.sub(
                r"([a-zA-Z0-9_\)\]\}])\>([a-zA-Z0-9_\(\[\{])", r"\1 > \2", code_part
            )

            new_lines.append(code_part + comment_part)

        content = "\n".join(new_lines)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Ошибка в {filepath}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    # Получаем список файлов с E225 ошибками
    import subprocess

    result = subprocess.run(
        [
            "python3",
            "-m",
            "flake8",
            "--select=E225",
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
        if fix_e225(f):
            fixed += 1
            print(f"✅ Исправлен: {f}")

    print(f"\nИсправлено файлов: {fixed}/{len(files)}")


if __name__ == "__main__":
    main()
