#!/usr/bin/env python3
"""
Скрипт для исправления E128/E117 ошибок (проблемы с отступами в многострочных выражениях).
Приводит код к единому стилю согласно PEP8.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict


def get_e128_e117_errors() -> List[Tuple[str, int, int]]:
    """Получает список всех E128/E117 ошибок: (filepath, lineno, col)."""
    try:
        result = subprocess.run(
            ["python3", "-m", "flake8", ".", "--select=E128,E117"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        errors = []
        for line in result.stdout.split("\n"):
            if ("E128" in line or "E117" in line) and ".py:" in line:
                # Формат: filepath:lineno:col: E128/E117 ...
                parts = line.split(":")
                if len(parts) >= 3:
                    filepath = parts[0]
                    try:
                        lineno = int(parts[1])
                        col = int(parts[2])
                        errors.append((filepath, lineno, col))
                    except ValueError:
                        continue

        return errors
    except Exception as e:
        print(f"Ошибка получения E128/E117 ошибок: {e}")
        return []


def fix_indentation_pep8(
    line: str, base_indent: int, continuation_indent: int = 4
) -> str:
    """Исправляет отступ строки согласно PEP8."""
    stripped = line.lstrip()
    if not stripped:
        return line

    current_indent = len(line) - len(stripped)

    # PEP8: continuation lines должны быть выровнены либо:
    # 1. С открывающей скобкой/кавычкой
    # 2. С отступом base_indent + continuation_indent (обычно 4 пробела)

    # Если строка начинается с закрывающей скобки, она должна быть на уровне base_indent
    if stripped.startswith((")", "]", "}")):
        return " " * base_indent + stripped

    # Для продолжения строки используем base_indent + continuation_indent
    target_indent = base_indent + continuation_indent

    # Если текущий отступ правильный, не меняем
    if current_indent == target_indent:
        return line

    # Исправляем отступ
    return " " * target_indent + stripped


def fix_multiline_expression(
    lines: List[str], start_line: int, end_line: int
) -> List[str]:
    """Исправляет многострочное выражение согласно требованиям."""
    if start_line < 0 or end_line >= len(lines):
        return lines

    # Получаем базовый отступ первой строки
    first_line = lines[start_line]
    base_indent = len(first_line) - len(first_line.lstrip())

    # Находим открывающую скобку
    opening_char = None
    for char in ["(", "[", "{"]:
        if char in first_line:
            opening_char = char
            break

    if not opening_char:
        return lines

    closing_char = {"(": ")", "[": "]", "{": "}"}[opening_char]

    # Исправляем отступы для продолжения
    fixed_lines = lines[: start_line + 1]

    for i in range(start_line + 1, end_line + 1):
        line = lines[i]
        stripped = line.lstrip()

        if not stripped:
            fixed_lines.append(line)
            continue

        # Если это закрывающая скобка, она должна быть на новой строке с базовым отступом
        if stripped.startswith(closing_char):
            # Убираем висящую запятую перед закрывающей скобкой
            if i > start_line + 1:
                prev_line = fixed_lines[-1].rstrip()
                if prev_line.endswith(","):
                    fixed_lines[-1] = prev_line[:-1].rstrip()

            fixed_lines.append(" " * base_indent + stripped)
        else:
            # Продолжение строки - выравниваем по PEP8
            fixed_line = fix_indentation_pep8(line, base_indent)
            fixed_lines.append(fixed_line)

    fixed_lines.extend(lines[end_line + 1 :])
    return fixed_lines


def fix_file_indentation(filepath: Path) -> bool:
    """Исправляет отступы в файле согласно PEP8."""
    print(f"\nОбрабатываю: {filepath}")

    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
    except Exception as e:
        print(f"  Ошибка чтения: {e}")
        return False

    # Получаем ошибки для этого файла
    all_errors = get_e128_e117_errors()
    file_errors = [(lineno, col) for f, lineno, col in all_errors if f == str(filepath)]

    if not file_errors:
        print("  Нет E128/E117 ошибок")
        return False

    print(f"  Найдено {len(file_errors)} ошибок")

    # Группируем ошибки по строкам
    error_lines = sorted(set(lineno for lineno, _ in file_errors))

    modified = False

    # Обрабатываем каждую проблемную строку
    for lineno in error_lines:
        if lineno > len(lines):
            continue

        line = lines[lineno - 1]
        stripped = line.lstrip()

        if not stripped:
            continue

        # Определяем базовый отступ предыдущей строки
        if lineno > 1:
            prev_line = lines[lineno - 2]
            base_indent = len(prev_line) - len(prev_line.lstrip())
        else:
            base_indent = 0

        # Проверяем, является ли это продолжением многострочного выражения
        is_continuation = False
        if lineno > 1:
            prev_stripped = lines[lineno - 2].lstrip()
            # Проверяем, есть ли незакрытая скобка в предыдущей строке
            for char in ["(", "[", "{"]:
                if char in prev_stripped:
                    # Считаем открывающие и закрывающие скобки
                    open_count = prev_stripped.count(char)
                    close_count = prev_stripped.count(
                        {")": ")", "]": "]", "}": "}"}[char]
                    )
                    if open_count > close_count:
                        is_continuation = True
                        break

        if is_continuation:
            # Это продолжение - исправляем отступ
            current_indent = len(line) - len(stripped)
            target_indent = base_indent + 4  # PEP8: 4 пробела для продолжения

            if current_indent != target_indent:
                lines[lineno - 1] = " " * target_indent + stripped
                modified = True
                print(
                    f"    Строка {lineno}: исправлен отступ ({current_indent} -> {target_indent})"
                )
        else:
            # Проверяем, нужно ли исправить отступ
            current_indent = len(line) - len(stripped)

            # Если строка начинается с закрывающей скобки, она должна быть на уровне базового отступа
            if stripped.startswith((")", "]", "}")):
                if current_indent != base_indent:
                    lines[lineno - 1] = " " * base_indent + stripped
                    modified = True
                    print(f"    Строка {lineno}: закрывающая скобка выровнена")
            else:
                # Обычная строка - проверяем, не является ли она частью многострочного выражения
                # Если предыдущая строка заканчивается запятой или открывающей скобкой
                if lineno > 1:
                    prev_line = lines[lineno - 2].rstrip()
                    if prev_line.endswith((",", "(", "[", "{")):
                        target_indent = base_indent + 4
                        if current_indent != target_indent:
                            lines[lineno - 1] = " " * target_indent + stripped
                            modified = True
                            print(f"    Строка {lineno}: исправлен отступ продолжения")

    # Убираем висящие запятые перед закрывающими скобками
    for i in range(len(lines) - 1):
        line = lines[i].rstrip()
        next_line = lines[i + 1].lstrip() if i + 1 < len(lines) else ""

        # Если строка заканчивается запятой, а следующая начинается с закрывающей скобки
        if line.endswith(",") and next_line.startswith((")", "]", "}")):
            lines[i] = line[:-1].rstrip()
            modified = True
            print(f"    Строка {i + 1}: удалена висящая запятая")

    # Убеждаемся, что закрывающие скобки на новой строке
    for i in range(len(lines) - 1):
        line = lines[i].rstrip()
        # Если строка заканчивается запятой или открывающей скобкой, а следующая не пустая
        if line.endswith((",", "(", "[", "{")):
            next_line = lines[i + 1].lstrip() if i + 1 < len(lines) else ""
            # Если следующая строка начинается с закрывающей скобки, это нормально
            if next_line.startswith((")", "]", "}")):
                continue
            # Если следующая строка - продолжение, проверяем отступ
            if next_line and not next_line.startswith("#"):
                # Продолжение должно быть с правильным отступом
                base_indent = len(lines[i]) - len(lines[i].lstrip())
                target_indent = base_indent + 4
                current_indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                if current_indent != target_indent:
                    lines[i + 1] = " " * target_indent + lines[i + 1].lstrip()
                    modified = True

    if modified:
        new_content = "\n".join(lines)
        # Убираем множественные пустые строки
        new_content = re.sub(r"\n\n\n+", "\n\n", new_content)
        filepath.write_text(new_content, encoding="utf-8")
        print("  ✓ Файл обновлен")
        return True

    return False


def main():
    print("=" * 60)
    print("Исправление E128/E117 ошибок (отступы в многострочных выражениях)")
    print("=" * 60)

    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 60}")
        print(f"Итерация {iteration}")
        print(f"{'=' * 60}")

        errors = get_e128_e117_errors()

        if not errors:
            print("\n✓ Все E128/E117 ошибки исправлены!")
            break

        # Группируем по файлам
        files_errors: Dict[str, List[Tuple[int, int]]] = {}
        for filepath, lineno, col in errors:
            if "fix_" in filepath:
                continue
            if filepath not in files_errors:
                files_errors[filepath] = []
            files_errors[filepath].append((lineno, col))

        print(f"\nНайдено {len(errors)} ошибок в {len(files_errors)} файлах")

        fixed_count = 0
        for filepath_str in sorted(files_errors.keys()):
            filepath = Path(filepath_str)
            if filepath.exists():
                if fix_file_indentation(filepath):
                    fixed_count += 1

        if fixed_count == 0:
            print("\nНет изменений в этой итерации.")
            break

        print(f"\nИсправлено файлов: {fixed_count}")

    # Финальная проверка
    print(f"\n{'=' * 60}")
    print("Финальная проверка...")
    final_errors = get_e128_e117_errors()
    final_errors = [e for e in final_errors if "fix_" not in e[0]]
    if final_errors:
        print(f"Осталось {len(final_errors)} E128/E117 ошибок:")
        for filepath, lineno, col in final_errors[:10]:
            print(f"  - {filepath}:{lineno}:{col}")
        if len(final_errors) > 10:
            print(f"  ... и еще {len(final_errors) - 10}")
    else:
        print("✓ Все E128/E117 ошибки исправлены!")


if __name__ == "__main__":
    main()
