#!/usr/bin/env python3
"""
Скрипт для исправления всех F841 ошибок (неиспользуемые переменные).
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


class VariableUsageChecker(ast.NodeVisitor):
    """Проверяет использование переменных в AST."""

    def __init__(self, target_var: str):
        self.target_var = target_var
        self.is_used = False

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id == self.target_var:
            self.is_used = True
        self.generic_visit(node)


def check_variable_usage(filepath: Path, var_name: str, lineno: int) -> bool:
    """Проверяет, используется ли переменная после присваивания."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
        content.split("\n")

        # Находим узел с присваиванием
        class AssignFinder(ast.NodeVisitor):
            def __init__(self, target_line):
                self.target_line = target_line
                self.assign_node = None

            def visit_Assign(self, node):
                if node.lineno == self.target_line:
                    self.assign_node = node
                self.generic_visit(node)

        finder = AssignFinder(lineno)
        finder.visit(tree)

        if not finder.assign_node:
            return False

        # Проверяем использование после присваивания
        checker = VariableUsageChecker(var_name)
        checker.visit(tree)

        return checker.is_used
    except:
        return True  # Если ошибка, считаем что используется


def analyze_variable_context(filepath: Path, var_name: str, lineno: int) -> str:
    """Анализирует контекст переменной и определяет тип."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        if lineno > len(lines):
            return "unknown"

        line = lines[lineno - 1]

        # Проверяем контекст вокруг переменной
        context_lines = []
        start = max(0, lineno - 5)
        end = min(len(lines), lineno + 5)
        for i in range(start, end):
            context_lines.append(f"{i + 1}: {lines[i]}")

        context = "\n".join(context_lines)

        # Определяем тип по контексту
        # 1. Placeholder - переменная присваивается но не используется
        if "=" in line and var_name in line:
            # Проверяем комментарии
            if (
                "placeholder" in context.lower()
                or "reserved" in context.lower()
                or "future" in context.lower()
            ):
                return "placeholder"

            # Проверяем паттерны placeholder
            if re.search(
                rf'\b{re.escape(var_name)}\s*=\s*["\']?[^=]+["\']?\s*#.*(?:reserved|future|todo|placeholder)',
                line,
                re.IGNORECASE,
            ):
                return "placeholder"

            # Проверяем, используется ли в комментариях как "будет использовано"
            if re.search(
                rf"#.*(?:will|будет|future|reserved).*{re.escape(var_name)}",
                context,
                re.IGNORECASE,
            ):
                return "future_logic"

        # 2. Результат функции, который не используется
        if "(" in line and "=" in line:
            # Проверяем, это результат вызова функции?
            if re.search(rf"\b{re.escape(var_name)}\s*=\s*\w+\s*\(", line):
                # Проверяем комментарии
                if "noqa" in line.lower() or "unused" in line.lower():
                    return "future_logic"
                return "unused_result"

        # 3. Exception variable
        if "except" in context.lower() and "as" in line:
            return "exception_var"

        return "unused"
    except:
        return "unknown"


def fix_f841_in_file(filepath: Path, var_name: str, lineno: int) -> bool:
    """Исправляет F841 ошибку в файле."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
    except Exception as e:
        print(f"  Ошибка чтения {filepath}: {e}")
        return False

    if lineno > len(lines):
        return False

    line = lines[lineno - 1]
    var_type = analyze_variable_context(filepath, var_name, lineno)

    print(f"  Переменная '{var_name}' (строка {lineno}): {var_type}")

    modified = False

    if var_type == "placeholder":
        # Заменяем на _
        if "=" in line:
            # Заменяем имя переменной на _
            new_line = re.sub(rf"\b{re.escape(var_name)}\b", "_", line, count=1)
            if new_line != line:
                lines[lineno - 1] = new_line
                modified = True
                print("    → Заменено на _")

    elif var_type == "exception_var":
        # Для exception переменных заменяем на _
        if "except" in line and "as" in line:
            new_line = re.sub(rf"as\s+{re.escape(var_name)}\b", "as _", line)
            if new_line != line:
                lines[lineno - 1] = new_line
                modified = True
                print("    → Заменено на _")

    elif var_type == "future_logic":
        # Добавляем # noqa: F841
        if "# noqa" not in line and "#noqa" not in line:
            # Добавляем в конец строки
            stripped = line.rstrip()
            if stripped.endswith(":"):
                # Для многострочных конструкций добавляем на следующей строке
                if lineno < len(lines) and lines[lineno].strip():
                    lines[lineno] = (
                        "    # noqa: F841" + "\n" + lines[lineno]
                        if not lines[lineno].startswith("    #")
                        else lines[lineno]
                    )
                else:
                    lines[lineno - 1] = stripped + "  # noqa: F841"
            else:
                lines[lineno - 1] = stripped + "  # noqa: F841"
            modified = True
            print("    → Добавлен # noqa: F841")

    elif var_type in ["unused", "unused_result"]:
        # Проверяем, можно ли безопасно удалить
        if "=" in line:
            # Удаляем присваивание, оставляем только правую часть если она имеет побочные эффекты
            # Для простоты - удаляем всю строку если это просто присваивание
            stripped = line.strip()

            # Проверяем, есть ли побочные эффекты (вызовы функций)
            if re.search(r"\w+\s*\(", line):
                # Есть вызов функции - заменяем переменную на _
                new_line = re.sub(
                    rf"\b{re.escape(var_name)}\s*=\s*", "_ = ", line, count=1
                )
                if new_line != line:
                    lines[lineno - 1] = new_line
                    modified = True
                    print("    → Заменено на _ (есть побочные эффекты)")
            else:
                # Простое присваивание - удаляем строку
                if stripped.startswith(var_name + " =") or stripped.startswith(
                    var_name + "="
                ):
                    # Проверяем, не является ли это частью многострочного выражения
                    if lineno > 1 and lines[lineno - 2].rstrip().endswith("\\"):
                        # Продолжение строки - не удаляем
                        lines[lineno - 1] = line + "  # noqa: F841"
                        modified = True
                        print("    → Добавлен # noqa: F841 (многострочное выражение)")
                    else:
                        del lines[lineno - 1]
                        modified = True
                        print("    → Удалено")

    if modified:
        new_content = "\n".join(lines)
        # Убираем множественные пустые строки
        new_content = re.sub(r"\n\n\n+", "\n\n", new_content)
        filepath.write_text(new_content, encoding="utf-8")
        return True

    return False


def get_f841_errors() -> List[Tuple[str, str, int]]:
    """Получает список всех F841 ошибок: (filepath, var_name, lineno)."""
    try:
        result = subprocess.run(
            ["python3", "-m", "flake8", ".", "--select=F841"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        errors = []
        for line in result.stdout.split("\n"):
            if "F841" in line and ".py:" in line:
                # Формат: filepath:lineno:col: F841 local variable 'var' is assigned but never used
                parts = line.split(":")
                if len(parts) >= 4:
                    filepath = parts[0]
                    lineno = int(parts[1])

                    # Извлекаем имя переменной из сообщения
                    match = re.search(r"local variable '(\w+)'", line)
                    if match:
                        var_name = match.group(1)
                        errors.append((filepath, var_name, lineno))

        return errors
    except Exception as e:
        print(f"Ошибка получения F841 ошибок: {e}")
        return []


def main():
    print("=" * 60)
    print("Исправление всех F841 ошибок (неиспользуемые переменные)")
    print("=" * 60)

    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 60}")
        print(f"Итерация {iteration}")
        print(f"{'=' * 60}")

        errors = get_f841_errors()

        if not errors:
            print("\n✓ Все F841 ошибки исправлены!")
            break

        print(f"\nНайдено {len(errors)} F841 ошибок")

        # Группируем по файлам
        files_errors: Dict[str, List[Tuple[str, int]]] = {}
        for filepath, var_name, lineno in errors:
            if filepath not in files_errors:
                files_errors[filepath] = []
            files_errors[filepath].append((var_name, lineno))

        fixed_count = 0
        for filepath_str, vars_info in sorted(files_errors.items()):
            filepath = Path(filepath_str)
            if not filepath.exists() or "fix_" in filepath.name:
                continue

            print(f"\n{filepath}:")
            # Сортируем по номерам строк (обратный порядок)
            for var_name, lineno in sorted(vars_info, key=lambda x: x[1], reverse=True):
                if fix_f841_in_file(filepath, var_name, lineno):
                    fixed_count += 1

        if fixed_count == 0:
            print("\nНет изменений в этой итерации.")
            break

        print(f"\nИсправлено переменных: {fixed_count}")

    # Финальная проверка
    print(f"\n{'=' * 60}")
    print("Финальная проверка...")
    final_errors = get_f841_errors()
    if final_errors:
        print(f"Осталось {len(final_errors)} F841 ошибок:")
        for filepath, var_name, lineno in final_errors[:10]:
            print(f"  - {filepath}:{lineno} - {var_name}")
        if len(final_errors) > 10:
            print(f"  ... и еще {len(final_errors) - 10}")
    else:
        print("✓ Все F841 ошибки исправлены!")


if __name__ == "__main__":
    main()
