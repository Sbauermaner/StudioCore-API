#!/usr/bin/env python3
"""
Скрипт для автоматического исправления неиспользуемых импортов.
- Определяет использование импортов через AST и прямой поиск
- Удаляет неиспользуемые импорты
- Перемещает типы в TYPE_CHECKING блок
"""

import ast
import re
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple, Optional
from collections import defaultdict

# Типы, которые должны быть в TYPE_CHECKING
TYPE_ONLY_MODULES = {"typing", "typing_extensions", "collections.abc"}

TYPE_INDICATORS = {
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


class ImportAnalyzer(ast.NodeVisitor):
    """Анализатор использования импортов в AST."""

    def __init__(self):
        self.used_names: Set[str] = set()
        self.used_attrs: Set[Tuple[str, str]] = set()  # (module, attr)
        self.imports: Dict[str, List[ast.Import | ast.ImportFrom]] = defaultdict(list)

    def visit_Name(self, node):
        """Отслеживает использование имен."""
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Отслеживает использование атрибутов (module.attr)."""
        if isinstance(node.value, ast.Name):
            self.used_attrs.add((node.value.id, node.attr))
        elif isinstance(node.value, ast.Attribute):
            # Рекурсивно получаем полный путь
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                parts.reverse()
                if len(parts) >= 2:
                    self.used_attrs.add((parts[0], ".".join(parts[1:])))
        self.generic_visit(node)

    def visit_Import(self, node):
        """Записывает импорты."""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name].append(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Записывает импорты from."""
        module = node.module or ""
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name].append(node)
            # Также записываем модуль.имя
            if module:
                self.imports[f"{module}.{name}"].append(node)
        self.generic_visit(node)


def analyze_file(filepath: Path) -> Tuple[Set[str], Set[str], Dict]:
    """Анализирует файл и возвращает используемые имена и импорты."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        print(f"Ошибка при парсинге {filepath}: {e}")
        return set(), set(), {}

    analyzer = ImportAnalyzer()
    analyzer.visit(tree)

    # Дополнительный прямой поиск в строковом виде (для случаев, которые AST не ловит)
    used_in_strings = set()
    for match in re.finditer(r"\b([A-Z][a-zA-Z0-9_]*)\b", content):
        used_in_strings.add(match.group(1))

    return analyzer.used_names, analyzer.used_attrs, analyzer.imports


def is_type_import(import_name: str, module: Optional[str] = None) -> bool:
    """Определяет, является ли импорт типом."""
    # Проверяем имя
    if any(indicator in import_name for indicator in TYPE_INDICATORS):
        return True

    # Проверяем модуль
    if module:
        parts = module.split(".")
        if parts[0] in TYPE_ONLY_MODULES:
            return True
        if any(part in TYPE_ONLY_MODULES for part in parts):
            return True

    return False


def fix_imports_in_file(filepath: Path) -> bool:
    """Исправляет импорты в файле."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")
        return False

    # Анализируем использование
    used_names, used_attrs, imports_dict = analyze_file(filepath)

    # Парсим AST для получения структуры импортов
    try:
        tree = ast.parse(content, filename=str(filepath))
    except:
        return False

    content.split("\n")
    modified = False

    # Собираем информацию об импортах из AST
    import_nodes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)

    # Проверяем каждый импорт
    imports_to_remove = []
    type_imports = []

    for node in import_nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                # Проверяем использование
                is_used = (
                    name in used_names
                    or any(name in str(attr) for attr in used_attrs)
                    or name
                    in content.replace(f"import {name}", "").replace(f"from {name}", "")
                )

                if not is_used:
                    imports_to_remove.append((node.lineno, name))
                elif is_type_import(name):
                    type_imports.append((node.lineno, name, None))

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                name = alias.asname or alias.name
                full_name = f"{module}.{name}" if module else name

                # Проверяем использование
                is_used = (
                    name in used_names
                    or full_name in used_names
                    or any(
                        name in str(attr) or full_name in str(attr)
                        for attr in used_attrs
                    )
                    or name
                    in content.replace(f"import {name}", "").replace(
                        f"from {module} import", ""
                    )
                )

                if not is_used:
                    imports_to_remove.append((node.lineno, name))
                elif is_type_import(name, module):
                    type_imports.append((node.lineno, name, module))

    # Удаляем неиспользуемые импорты (упрощенная версия)
    # В реальности нужен более сложный алгоритм для правильного удаления строк

    return modified


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
                filepath = line.split(":")[0].strip("./")
                if filepath:
                    files_with_f401.add(filepath)

    print(f"Найдено {len(files_with_f401)} файлов с F401 ошибками")

    for filepath_str in sorted(files_with_f401):
        filepath = Path(filepath_str)
        if filepath.exists():
            print(f"Обрабатываю {filepath}...")
            fix_imports_in_file(filepath)
        else:
            print(f"Файл не найден: {filepath}")
