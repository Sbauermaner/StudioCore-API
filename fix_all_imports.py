#!/usr/bin/env python3
"""
Итеративный скрипт для исправления всех F401 ошибок.
Обрабатывает файлы до тех пор, пока F401 не станет 0.
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Set, Optional


def get_used_names_ast(filepath: Path) -> Set[str]:
    """Получает все используемые имена через AST."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
    except:
        return set()

    used = set()

    class Collector(ast.NodeVisitor):
        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Load, ast.Store)):
                used.add(node.id)
            self.generic_visit(node)

    Collector().visit(tree)
    return used


def is_type_import(name: str, module: Optional[str]) -> bool:
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
    }
    if name in type_names:
        return True
    if module and any(
        m in module for m in ["typing", "typing_extensions", "collections.abc"]
    ):
        return True
    return False


def fix_imports_in_file(filepath: Path) -> bool:
    """Исправляет импорты в одном файле."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Ошибка чтения {filepath}: {e}")
        return False

    used_names = get_used_names_ast(filepath)
    lines = content.split("\n")
    modified = False

    try:
        tree = ast.parse(content, filename=str(filepath))
    except:
        return False

    # Находим все импорты
    imports_to_check = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imports_to_check.append((node.lineno, name, None, "import", node))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                name = alias.asname or alias.name
                imports_to_check.append((node.lineno, name, node.module, "from", node))

    # Проверяем каждый импорт
    unused = []
    type_imports = []

    for lineno, name, module, imp_type, node in imports_to_check:
        # Проверяем использование
        is_used = name in used_names

        # Дополнительная проверка через строковый поиск
        if not is_used:
            search_content = "\n".join(
                [l for i, l in enumerate(lines) if i != lineno - 1]
            )
            pattern = r"\b" + re.escape(name) + r"\b"
            if re.search(pattern, search_content):
                is_used = True

        if not is_used:
            if is_type_import(name, module):
                type_imports.append((lineno, name, module, imp_type))
            else:
                unused.append((lineno, name, module, imp_type))

    # Удаляем неиспользуемые импорты
    if unused:
        # Сортируем по номерам строк (обратный порядок)
        for lineno, name, module, imp_type in sorted(unused, reverse=True):
            idx = lineno - 1
            if 0 <= idx < len(lines):
                line = lines[idx]
                if "import" in line:
                    # Простое удаление строки (для начала)
                    if imp_type == "import" and f"import {name}" in line:
                        if line.strip() == f"import {name}":
                            del lines[idx]
                            modified = True
                    elif (
                        imp_type == "from"
                        and module
                        and f"from {module} import" in line
                    ):
                        # Удаляем из списка импортов
                        after_import = (
                            line.split("import", 1)[1] if "import" in line else ""
                        )
                        imports_list = [
                            a.strip().split(" as ")[0] for a in after_import.split(",")
                        ]
                        if len(imports_list) == 1 and name in imports_list:
                            del lines[idx]
                            modified = True
                        elif name in imports_list:
                            # Удаляем из множественного импорта
                            new_line = re.sub(
                                r",\s*" + re.escape(name) + r"(?:\s+as\s+\w+)?",
                                "",
                                line,
                            )
                            new_line = re.sub(
                                r"\b" + re.escape(name) + r"(?:\s+as\s+\w+)?\s*,",
                                "",
                                new_line,
                            )
                            if new_line != line:
                                lines[idx] = new_line
                                modified = True

    if modified:
        new_content = "\n".join(lines)
        new_content = re.sub(r"\n\n\n+", "\n\n", new_content)
        filepath.write_text(new_content, encoding="utf-8")
        return True

    return False


def get_f401_count() -> int:
    """Получает количество F401 ошибок."""
    try:
        result = subprocess.run(
            ["python3", "run_code_audit.py"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        # Парсим вывод
        if "Found potential issues:" in result.stdout:
            # Запускаем flake8 напрямую для подсчета F401
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "flake8",
                    ".",
                    "--select=F401",
                    "--exclude=.git,__pycache__,venv,env,node_modules,build,dist,*.pyc",
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            return len(
                [l for l in result.stdout.split("\n") if "F401" in l and l.strip()]
            )
    except:
        pass
    return -1


def main():
    print("=" * 60)
    print("Итеративное исправление F401 ошибок")
    print("=" * 60)

    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        iteration += 1
        print(f"\nИтерация {iteration}")
        print("-" * 60)

        # Получаем список файлов с F401
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "flake8",
                    ".",
                    "--select=F401",
                    "--exclude=.git,__pycache__,venv,env,node_modules,build,dist,*.pyc",
                    "--format=%(path)s",
                ],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            files_with_f401 = set()
            for line in result.stdout.split("\n"):
                if line.strip() and line.endswith(".py"):
                    files_with_f401.add(line.strip())
        except Exception as e:
            print(f"Ошибка получения списка файлов: {e}")
            break

        if not files_with_f401:
            print("✓ Все F401 ошибки исправлены!")
            break

        print(f"Найдено {len(files_with_f401)} файлов с F401")

        fixed = 0
        for filepath_str in sorted(files_with_f401):
            filepath = Path(filepath_str)
            if filepath.exists() and not filepath.name.startswith("fix_"):
                print(f"  Обрабатываю {filepath}...")
                if fix_imports_in_file(filepath):
                    fixed += 1
                    print("    ✓ Исправлено")

        if fixed == 0:
            print("Нет изменений в этой итерации. Остановка.")
            break

        print(f"\nИсправлено файлов: {fixed}")

    # Финальная проверка
    print("\n" + "=" * 60)
    print("Финальная проверка F401...")
    f401_count = get_f401_count()
    if f401_count >= 0:
        print(f"Осталось F401 ошибок: {f401_count}")
    else:
        print("Запустите: python3 run_code_audit.py для проверки")


if __name__ == "__main__":
    main()
