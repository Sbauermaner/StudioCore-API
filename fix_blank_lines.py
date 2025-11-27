#!/usr/bin/env python3
"""
Скрипт для исправления форматирования пустых строк согласно PEP8:
- Перед функцией: 2 пустые строки
- Перед классом: 2 пустые строки
- Внутри класса: 1 пустая строка между методами
- Убрать лишние >2 пустые строки
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Set, Dict


def get_blank_line_errors() -> List[Tuple[str, int, str]]:
    """Получает список всех E302/E305/E306 ошибок: (filepath, lineno, error_code)."""
    try:
        result = subprocess.run(
            [
                "python3",
                "-m",
                "flake8",
                ".",
                "--select=E302,E305,E306",
                "--format=%(path)s:%(row)d:%(code)s",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        errors = []
        for line in result.stdout.split("\n"):
            if ("E302" in line or "E305" in line or "E306" in line) and ".py:" in line:
                # Формат: filepath:lineno:code
                parts = line.split(":")
                if len(parts) >= 3:
                    filepath = parts[0]
                    try:
                        lineno = int(parts[1])
                        error_code = parts[2].strip()
                        if "fix_" not in filepath:
                            errors.append((filepath, lineno, error_code))
                    except (ValueError, IndexError):
                        continue

        return errors
    except Exception as e:
        print(f"Ошибка получения ошибок: {e}")
        return []


def analyze_file_structure(filepath: Path) -> Tuple[Set[int], Set[int], Dict[int, int]]:
    """Анализирует структуру файла и возвращает позиции функций, классов и их вложенность."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except:
        return set(), set(), {}

    function_lines = set()
    class_lines = set()
    class_methods: Dict[int, List[int]] = {}  # class_line -> [method_lines]
    current_class = None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_lines.add(node.lineno)
            if current_class:
                if current_class not in class_methods:
                    class_methods[current_class] = []
                class_methods[current_class].append(node.lineno)
        elif isinstance(node, ast.ClassDef):
            class_lines.add(node.lineno)
            current_class = node.lineno

    return function_lines, class_lines, class_methods


def fix_blank_lines(filepath: Path) -> bool:
    """Исправляет форматирование пустых строк в файле."""
    print(f"\nОбрабатываю: {filepath}")

    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
    except Exception as e:
        print(f"  Ошибка чтения: {e}")
        return False

    # Анализируем структуру файла
    function_lines, class_lines, class_methods = analyze_file_structure(filepath)

    # Получаем ошибки для этого файла
    all_errors = get_blank_line_errors()
    file_errors = [
        (lineno, code) for f, lineno, code in all_errors if f == str(filepath)
    ]

    if not file_errors:
        print("  Нет ошибок форматирования пустых строк")
        return False

    print(f"  Найдено {len(file_errors)} ошибок")

    modified = False

    # Исправляем ошибки (обрабатываем в обратном порядке)
    for lineno, error_code in sorted(file_errors, key=lambda x: x[0], reverse=True):
        if lineno > len(lines) or lineno < 1:
            continue

        line_idx = lineno - 1
        current_line = lines[line_idx] if line_idx < len(lines) else ""

        if error_code == "E302":
            # expected 2 blank lines, found X
            # Нужно добавить пустые строки перед функцией/классом
            if line_idx == 0:
                continue

            # Определяем, что это - функция или класс
            is_function = lineno in function_lines
            is_class = lineno in class_lines

            if not (is_function or is_class):
                continue

            # Считаем пустые строки перед
            blank_count = 0
            for i in range(line_idx - 1, -1, -1):
                if i < 0:
                    break
                if lines[i].strip() == "":
                    blank_count += 1
                else:
                    break

            # Нужно 2 пустые строки
            if blank_count < 2:
                # Добавляем недостающие пустые строки
                insert_pos = line_idx - blank_count
                needed = 2 - blank_count
                for _ in range(needed):
                    lines.insert(insert_pos, "")
                    modified = True
                print(
                    f"    Строка {lineno}: добавлено {needed} пустых строк перед {'классом' if is_class else 'функцией'}"
                )

        elif error_code == "E305":
            # expected 2 blank lines after class or function definition
            # Нужно добавить пустые строки после класса/функции
            if line_idx >= len(lines) - 1:
                continue

            # Определяем, что это - функция или класс
            is_function = lineno in function_lines
            is_class = lineno in class_lines

            if not (is_function or is_class):
                continue

            # Находим конец функции/класса
            end_line = line_idx
            indent_level = len(current_line) - len(current_line.lstrip())

            # Ищем следующую непустую строку с меньшим или равным отступом
            for i in range(line_idx + 1, len(lines)):
                if lines[i].strip() == "":
                    continue
                line_indent = len(lines[i]) - len(lines[i].lstrip())
                if line_indent <= indent_level:
                    end_line = i - 1
                    break
            else:
                end_line = len(lines) - 1

            # Считаем пустые строки после
            blank_count = 0
            for i in range(end_line + 1, min(end_line + 4, len(lines))):
                if i < len(lines) and lines[i].strip() == "":
                    blank_count += 1
                else:
                    break

            # Нужно 2 пустые строки
            if blank_count < 2:
                # Добавляем недостающие пустые строки
                needed = 2 - blank_count
                for _ in range(needed):
                    lines.insert(end_line + 1, "")
                    modified = True
                print(
                    f"    Строка {lineno}: добавлено {needed} пустых строк после {'класса' if is_class else 'функции'}"
                )

        elif error_code == "E306":
            # expected 1 blank line before a nested definition
            # Нужно добавить 1 пустую строку перед вложенным определением
            if line_idx == 0:
                continue

            # Это должен быть метод внутри класса
            is_method = False
            for class_line, method_lines in class_methods.items():
                if lineno in method_lines:
                    is_method = True
                    break

            if not is_method:
                continue

            # Считаем пустые строки перед
            blank_count = 0
            for i in range(line_idx - 1, -1, -1):
                if i < 0:
                    break
                if lines[i].strip() == "":
                    blank_count += 1
                else:
                    break

            # Нужна 1 пустая строка
            if blank_count < 1:
                lines.insert(line_idx, "")
                modified = True
                print(f"    Строка {lineno}: добавлена 1 пустая строка перед методом")
            elif blank_count > 1:
                # Удаляем лишние
                for i in range(line_idx - 1, line_idx - blank_count, -1):
                    if i >= 0 and lines[i].strip() == "":
                        del lines[i]
                        modified = True
                print(
                    f"    Строка {lineno}: удалены лишние пустые строки перед методом"
                )

    # Убираем множественные пустые строки (>2 подряд)
    i = 0
    while i < len(lines):
        if lines[i].strip() == "":
            # Считаем подряд идущие пустые строки
            blank_start = i
            blank_count = 0
            while i < len(lines) and lines[i].strip() == "":
                blank_count += 1
                i += 1

            # Если больше 2, оставляем только 2
            if blank_count > 2:
                # Оставляем 2 пустые строки
                lines[blank_start : blank_start + blank_count] = ["", ""]
                modified = True
                print(
                    f"    Строки {blank_start + 1}-{blank_start + blank_count}: удалены лишние пустые строки ({blank_count} -> 2)"
                )
                i = blank_start + 2
        else:
            i += 1

    if modified:
        new_content = "\n".join(lines)
        # Убираем множественные пустые строки в конце файла
        new_content = re.sub(r"\n\n+$", "\n", new_content)
        filepath.write_text(new_content, encoding="utf-8")
        print("  ✓ Файл обновлен")
        return True

    return False


def main():
    print("=" * 60)
    print("Исправление форматирования пустых строк (E302/E305/E306)")
    print("=" * 60)

    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 60}")
        print(f"Итерация {iteration}")
        print(f"{'=' * 60}")

        errors = get_blank_line_errors()

        if not errors:
            print("\n✓ Все ошибки форматирования пустых строк исправлены!")
            break

        # Группируем по файлам
        files_errors: Dict[str, int] = {}
        for filepath, lineno, code in errors:
            if filepath not in files_errors:
                files_errors[filepath] = 0
            files_errors[filepath] += 1

        print(f"\nНайдено {len(errors)} ошибок в {len(files_errors)} файлах")

        fixed_count = 0
        for filepath_str in sorted(files_errors.keys()):
            filepath = Path(filepath_str)
            if filepath.exists():
                if fix_blank_lines(filepath):
                    fixed_count += 1

        if fixed_count == 0:
            print("\nНет изменений в этой итерации.")
            break

        print(f"\nИсправлено файлов: {fixed_count}")

    # Финальная проверка
    print(f"\n{'=' * 60}")
    print("Финальная проверка...")
    final_errors = get_blank_line_errors()
    if final_errors:
        print(f"Осталось {len(final_errors)} ошибок:")
        files_count = {}
        for filepath, lineno, code in final_errors[:20]:
            if filepath not in files_count:
                files_count[filepath] = 0
            files_count[filepath] += 1
            print(f"  - {filepath}:{lineno} ({code})")
        if len(final_errors) > 20:
            print(f"  ... и еще {len(final_errors) - 20}")
    else:
        print("✓ Все ошибки форматирования пустых строк исправлены!")


if __name__ == "__main__":
    main()
