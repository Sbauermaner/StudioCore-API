#!/usr/bin/env python3
"""
Продвинутый скрипт для исправления неиспользуемых импортов.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Set, List, Tuple, Optional


def get_used_names_from_ast(filepath: Path) -> Set[str]:
    """Получает все используемые имена из AST."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        print(f"  Ошибка парсинга AST: {e}")
        return set()

    used = set()

    class NameCollector(ast.NodeVisitor):
        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Load, ast.Store)):
                used.add(node.id)
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name):
                used.add(node.value.id)
            self.generic_visit(node)

    collector = NameCollector()
    collector.visit(tree)
    return used


def get_imports_from_file(filepath: Path) -> List[Tuple[int, str, Optional[str], str]]:
    """Получает список импортов: (lineno, name, module, full_line)."""
    imports = []
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")

        tree = ast.parse(content, filename=str(filepath))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    lineno = node.lineno
                    name = alias.asname or alias.name
                    module = None
                    full_line = lines[lineno - 1] if lineno <= len(lines) else ""
                    imports.append((lineno, name, module, full_line))

            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    lineno = node.lineno
                    name = alias.asname or alias.name
                    full_line = lines[lineno - 1] if lineno <= len(lines) else ""
                    imports.append((lineno, name, module, full_line))
    except Exception as e:
        print(f"  Ошибка при получении импортов: {e}")

    return imports


def is_type_hint(name: str, module: Optional[str]) -> bool:
    """Проверяет, является ли импорт типом."""
    type_names = {
        "Any",
        "Dict",
        "List",
        "Tuple",
        "Set",
        "Optional",
        "Union",
        "Callable",
        "Iterator",
        "Iterable",
        "Mapping",
        "Sequence",
        "Type",
        "TypeVar",
        "Generic",
        "Protocol",
        "Literal",
        "TYPE_CHECKING",
    }

    if name in type_names:
        return True

    if module:
        type_modules = {"typing", "typing_extensions", "collections.abc"}
        if any(m in module for m in type_modules):
            return True

    return False


def fix_file_imports(filepath: Path) -> bool:
    """Исправляет импорты в одном файле."""
    print(f"\nОбрабатываю: {filepath}")

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Ошибка чтения: {e}")
        return False

    # Получаем используемые имена
    used_names = get_used_names_from_ast(filepath)

    # Дополнительная проверка через прямой поиск (для случаев вне AST)
    # Ищем использование в строках, комментариях и т.д.
    content.lower()

    # Получаем импорты
    imports = get_imports_from_file(filepath)

    if not imports:
        print("  Нет импортов для проверки")
        return False

    lines = content.split("\n")
    modified = False
    lines_to_remove = set()
    type_imports_to_move = []

    # Анализируем каждый импорт
    for lineno, name, module, full_line in imports:
        # Проверяем использование
        is_used = (
            name in used_names
            or name
            in content.replace(f"import {name}", "").replace(
                f"from {module} import", ""
            )
            if module
            else content
        )

        # Дополнительная проверка для атрибутов модулей
        if module and not is_used:
            # Проверяем использование как module.name
            if f"{module}.{name}" in content or f"{name}." in content:
                is_used = True

        if not is_used:
            print(f"  Неиспользуемый импорт: {name} (строка {lineno})")
            # Проверяем, является ли это типом
            if is_type_hint(name, module):
                print("    → Это тип, нужно переместить в TYPE_CHECKING")
                type_imports_to_move.append((lineno, name, module, full_line))
            else:
                print("    → Удаляем")
                lines_to_remove.add(lineno - 1)  # 0-based index
                modified = True

    # Удаляем строки (в обратном порядке, чтобы не сбить индексы)
    if lines_to_remove:
        for lineno in sorted(lines_to_remove, reverse=True):
            if lines[lineno].strip() and not lines[lineno].strip().startswith("#"):
                # Проверяем, что это действительно импорт
                if "import" in lines[lineno]:
                    del lines[lineno]
                    modified = True

    # Сохраняем изменения
    if modified:
        new_content = "\n".join(lines)
        # Убираем лишние пустые строки
        new_content = re.sub(r"\n\n\n+", "\n\n", new_content)
        filepath.write_text(new_content, encoding="utf-8")
        print("  ✓ Файл обновлен")
        return True

    print("  - Изменений не требуется")
    return False


if __name__ == "__main__":
    # Получаем список файлов с F401
    report_file = Path("errors_report.txt")
    if not report_file.exists():
        print("Файл errors_report.txt не найден. Запустите сначала run_code_audit.py")
        sys.exit(1)

    files_with_f401 = set()
    with open(report_file, "r") as f:
        for line in f:
            if "F401" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    filepath = parts[0].strip("./")
                    if filepath and filepath.endswith(".py"):
                        files_with_f401.add(filepath)

    print(f"Найдено {len(files_with_f401)} файлов с F401 ошибками")
    print("=" * 60)

    fixed_count = 0
    for filepath_str in sorted(files_with_f401):
        filepath = Path(filepath_str)
        if filepath.exists():
            if fix_file_imports(filepath):
                fixed_count += 1
        else:
            print(f"Файл не найден: {filepath}")

    print("\n" + "=" * 60)
    print(f"Обработано файлов: {len(files_with_f401)}")
    print(f"Исправлено файлов: {fixed_count}")
