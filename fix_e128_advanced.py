#!/usr/bin/env python3
"""
Улучшенный скрипт для исправления E128/E117 ошибок.
Использует прямое чтение ошибок flake8 и исправляет отступы.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict


def get_e128_e117_errors() -> List[Tuple[str, int, int, str]]:
    """Получает список всех E128/E117 ошибок: (filepath, lineno, col, error_type)."""
    try:
        result = subprocess.run(
            [
                "python3",
                "-m",
                "flake8",
                ".",
                "--select=E128,E117",
                "--format=%(path)s:%(row)d:%(col)d:%(code)s",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        errors = []
        for line in result.stdout.split("\n"):
            if ("E128" in line or "E117" in line) and ".py:" in line:
                # Формат: filepath:lineno:col:code
                parts = line.split(":")
                if len(parts) >= 4:
                    filepath = parts[0]
                    try:
                        lineno = int(parts[1])
                        col = int(parts[2])
                        error_code = parts[3].strip()
                        if "fix_" not in filepath:
                            errors.append((filepath, lineno, col, error_code))
                    except (ValueError, IndexError):
                        continue

        return errors
    except Exception as e:
        print(f"Ошибка получения E128/E117 ошибок: {e}")
        return []


def calculate_correct_indent(base_line: str, continuation_indent: int = 4) -> int:
    """Вычисляет правильный отступ для продолжения строки согласно PEP8."""
    base_indent = len(base_line) - len(base_line.lstrip())

    # PEP8: continuation lines должны иметь отступ base_indent + continuation_indent
    # Но если есть открывающая скобка, можно выровнять по ней

    # Ищем открывающую скобку в базовой строке
    stripped = base_line.lstrip()
    for char in ["(", "[", "{"]:
        if char in stripped:
            # Находим позицию открывающей скобки
            bracket_pos = stripped.find(char)
            # Отступ = базовый отступ + позиция скобки + 1 (чтобы быть после скобки)
            return base_indent + bracket_pos + 1

    # Если нет скобки, используем стандартный отступ продолжения
    return base_indent + continuation_indent


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
    file_errors = [
        (lineno, col, code) for f, lineno, col, code in all_errors if f == str(filepath)
    ]

    if not file_errors:
        print("  Нет E128/E117 ошибок")
        return False

    print(f"  Найдено {len(file_errors)} ошибок")

    modified = False

    # Сортируем ошибки по номерам строк (обратный порядок для безопасного исправления)
    for lineno, col, error_code in sorted(
        file_errors, key=lambda x: x[0], reverse=True
    ):
        if lineno > len(lines) or lineno < 1:
            continue

        line_idx = lineno - 1
        line = lines[line_idx]
        stripped = line.lstrip()

        if not stripped or stripped.startswith("#"):
            continue

        current_indent = len(line) - len(stripped)

        # Определяем правильный отступ
        if lineno > 1:
            prev_line = lines[line_idx - 1]
            correct_indent = calculate_correct_indent(prev_line)
        else:
            correct_indent = 0

        # Исправляем отступ
        if current_indent != correct_indent:
            lines[line_idx] = " " * correct_indent + stripped
            modified = True
            print(
                f"    Строка {lineno}: исправлен отступ ({current_indent} -> {correct_indent} пробелов)"
            )

    # Убираем висящие запятые перед закрывающими скобками
    for i in range(len(lines) - 1):
        line = lines[i].rstrip()
        next_line = lines[i + 1].lstrip() if i + 1 < len(lines) else ""

        # Если строка заканчивается запятой, а следующая начинается с закрывающей скобки
        if line.endswith(",") and next_line.startswith((")", "]", "}")):
            lines[i] = line[:-1].rstrip()
            modified = True
            print(f"    Строка {i + 1}: удалена висящая запятая")

    # Убеждаемся, что закрывающие скобки на новой строке с правильным отступом
    for i in range(len(lines) - 1):
        line = lines[i].rstrip()
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        next_stripped = next_line.lstrip()

        # Если следующая строка начинается с закрывающей скобки
        if next_stripped.startswith((")", "]", "}")):
            # Определяем базовый отступ (ищем соответствующую открывающую скобку)
            base_indent = 0
            for j in range(i, max(-1, i - 20), -1):  # Ищем назад до 20 строк
                prev_line = lines[j] if j >= 0 else ""
                # Ищем строку с открывающей скобкой
                for char in ["(", "[", "{"]:
                    if char in prev_line:
                        base_indent = len(prev_line) - len(prev_line.lstrip())
                        break
                if base_indent > 0:
                    break

            # Закрывающая скобка должна быть на уровне базового отступа
            current_indent = len(next_line) - len(next_stripped)
            if current_indent != base_indent:
                lines[i + 1] = " " * base_indent + next_stripped
                modified = True
                print(f"    Строка {i + 2}: закрывающая скобка выровнена")

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
    max_iterations = 15

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
        files_errors: Dict[str, int] = {}
        for filepath, lineno, col, code in errors:
            if filepath not in files_errors:
                files_errors[filepath] = 0
            files_errors[filepath] += 1

        print(f"\nНайдено {len(errors)} ошибок в {len(files_errors)} файлах")

        fixed_count = 0
        for filepath_str in sorted(files_errors.keys()):
            filepath = Path(filepath_str)
            if filepath.exists():
                if fix_file_indentation(filepath):
                    fixed_count += 1

        if fixed_count == 0:
            print("\nНет изменений в этой итерации.")
            # Попробуем еще раз с более агрессивным подходом
            if iteration < max_iterations:
                continue
            else:
                break

        print(f"\nИсправлено файлов: {fixed_count}")

    # Финальная проверка
    print(f"\n{'=' * 60}")
    print("Финальная проверка...")
    final_errors = get_e128_e117_errors()
    if final_errors:
        print(f"Осталось {len(final_errors)} E128/E117 ошибок:")
        files_count = {}
        for filepath, lineno, col, code in final_errors[:20]:
            if filepath not in files_count:
                files_count[filepath] = 0
            files_count[filepath] += 1
            print(f"  - {filepath}:{lineno}:{col} ({code})")
        if len(final_errors) > 20:
            print(f"  ... и еще {len(final_errors) - 20}")
        print("\nПо файлам:")
        for filepath, count in sorted(files_count.items()):
            print(f"  {filepath}: {count} ошибок")
    else:
        print("✓ Все E128/E117 ошибки исправлены!")


if __name__ == "__main__":
    main()
