#!/usr/bin/env python3
"""
Финальный скрипт для исправления неиспользуемых импортов.
Использует AST для точного определения использования.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Set, List, Tuple, Optional, Dict


class ImportUsageAnalyzer(ast.NodeVisitor):
    """Анализатор использования имен в AST."""

    def __init__(self):
        self.used_names: Set[str] = set()
        self.used_attrs: List[Tuple[str, str]] = []  # (module, attr)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Отслеживаем использование атрибутов
        if isinstance(node.value, ast.Name):
            self.used_attrs.append((node.value.id, node.attr))
        self.generic_visit(node)


def analyze_import_usage(filepath: Path) -> Tuple[Set[str], List[Tuple[str, str]]]:
    """Анализирует использование импортов в файле."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        print(f"  Ошибка парсинга: {e}")
        return set(), []

    analyzer = ImportUsageAnalyzer()
    analyzer.visit(tree)

    return analyzer.used_names, analyzer.used_attrs


def get_import_statements(filepath: Path) -> List[Dict]:
    """Получает все импорты из файла."""
    imports = []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "lineno": node.lineno,
                            "name": alias.asname or alias.name,
                            "module": None,
                            "full_name": alias.name,
                            "line": lines[node.lineno - 1]
                            if node.lineno <= len(lines)
                            else "",
                        }
                    )

            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    imports.append(
                        {
                            "type": "from",
                            "lineno": node.lineno,
                            "name": alias.asname or alias.name,
                            "module": module,
                            "full_name": f"{module}.{alias.name}"
                            if module
                            else alias.name,
                            "line": lines[node.lineno - 1]
                            if node.lineno <= len(lines)
                            else "",
                        }
                    )
    except Exception as e:
        print(f"  Ошибка получения импортов: {e}")

    return imports


def is_type_only(name: str, module: Optional[str]) -> bool:
    """Проверяет, является ли импорт только типом."""
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
    }

    if name in type_names:
        return True

    if module:
        type_modules = {"typing", "typing_extensions", "collections.abc"}
        if any(m in module for m in type_modules):
            return True

    return False


def fix_file(filepath: Path) -> bool:
    """Исправляет импорты в файле."""
    print(f"\n{'=' * 60}")
    print(f"Обрабатываю: {filepath}")

    # Анализируем использование
    used_names, used_attrs = analyze_import_usage(filepath)

    # Получаем импорты
    imports = get_import_statements(filepath)

    if not imports:
        print("  Нет импортов")
        return False

    # Читаем файл
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
    except Exception as e:
        print(f"  Ошибка чтения: {e}")
        return False

    # Проверяем каждый импорт
    unused_imports = []
    type_imports = []

    for imp in imports:
        name = imp["name"]
        module = imp["module"]
        lineno = imp["lineno"]

        # Пропускаем __future__ импорты
        if module == "__future__":
            continue

        # Проверяем использование
        is_used = False

        # Прямое использование имени
        if name in used_names:
            is_used = True

        # Использование как атрибут модуля
        if not is_used and module:
            for mod_name, attr_name in used_attrs:
                if mod_name == name or (module and name in module.split(".")):
                    is_used = True
                    break

        # Дополнительная проверка через строковый поиск (для случаев вне AST)
        if not is_used:
            # Ищем использование в коде (исключая строку импорта)
            search_content = "\n".join(
                [l for i, l in enumerate(lines) if i != lineno - 1]
            )
            if name in search_content and f"import {name}" not in search_content:
                # Проверяем, что это не просто часть другого слова
                pattern = r"\b" + re.escape(name) + r"\b"
                if re.search(pattern, search_content):
                    is_used = True

        if not is_used:
            print(f"  ✗ Неиспользуемый: {name} (строка {lineno})")
            if is_type_only(name, module):
                print("    → Тип, переместить в TYPE_CHECKING")
                type_imports.append(imp)
            else:
                unused_imports.append(imp)
        else:
            print(f"  ✓ Используется: {name}")

    # Удаляем неиспользуемые импорты
    if unused_imports or type_imports:
        # Сортируем по номерам строк (в обратном порядке для удаления)
        all_to_remove = sorted(unused_imports, key=lambda x: x["lineno"], reverse=True)

        # Удаляем строки
        for imp in all_to_remove:
            lineno = imp["lineno"] - 1  # 0-based
            if 0 <= lineno < len(lines):
                line = lines[lineno]
                # Проверяем, что это действительно импорт
                if "import" in line:
                    # Если это единственный импорт в строке, удаляем всю строку
                    if imp["type"] == "import":
                        # Простой импорт: import name
                        if re.match(
                            r"^\s*import\s+" + re.escape(imp["name"]) + r"\s*$", line
                        ):
                            del lines[lineno]
                        else:
                            # Множественный импорт - нужно аккуратно удалить
                            # Упрощенная версия: удаляем всю строку если это единственный импорт
                            if (
                                line.strip().startswith("import ")
                                and imp["name"] in line
                            ):
                                # Проверяем, сколько импортов в строке
                                imports_in_line = [
                                    a.strip()
                                    for a in line.split("import")[1].split(",")
                                ]
                                if len(imports_in_line) == 1:
                                    del lines[lineno]
                                else:
                                    # Удаляем только этот импорт из строки
                                    new_line = line.replace(
                                        f", {imp['name']}", ""
                                    ).replace(f"{imp['name']}, ", "")
                                    if new_line != line:
                                        lines[lineno] = new_line
                    elif imp["type"] == "from":
                        # from module import name
                        if f"from {imp['module']} import" in line:
                            # Проверяем, сколько импортов в строке
                            after_import = (
                                line.split("import")[1] if "import" in line else ""
                            )
                            imports_list = [
                                a.strip().split(" as ")[0]
                                for a in after_import.split(",")
                            ]
                            if len(imports_list) == 1 and imp["name"] in imports_list:
                                del lines[lineno]
                            else:
                                # Удаляем только этот импорт
                                pattern = (
                                    r",\s*"
                                    + re.escape(imp["name"])
                                    + r"(?:\s+as\s+\w+)?\b"
                                )
                                new_line = re.sub(pattern, "", line)
                                pattern2 = (
                                    r"\b"
                                    + re.escape(imp["name"])
                                    + r"(?:\s+as\s+\w+)?\s*,"
                                )
                                new_line = re.sub(pattern2, "", new_line)
                                if new_line != line:
                                    lines[lineno] = new_line

        # Сохраняем
        new_content = "\n".join(lines)
        # Убираем множественные пустые строки
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
        print("Запустите сначала: python3 run_code_audit.py")
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

    fixed_count = 0
    for filepath_str in sorted(files_with_f401):
        filepath = Path(filepath_str)
        if filepath.exists():
            if fix_file(filepath):
                fixed_count += 1
        else:
            print(f"Файл не найден: {filepath}")

    print(f"\n{'=' * 60}")
    print(f"Итого: обработано {len(files_with_f401)}, исправлено {fixed_count}")
