#!/usr/bin/env python3
"""
Полный скрипт для исправления всех F401 ошибок.
Использует AST для точного определения использования импортов.
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Set, List, Dict, Tuple, Optional


class ImportUsageChecker(ast.NodeVisitor):
    """Проверяет использование имен в AST."""

    def __init__(self):
        self.used_names: Set[str] = set()
        self.used_attrs: List[Tuple[str, str]] = []

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store)):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            self.used_attrs.append((node.value.id, node.attr))
        self.generic_visit(node)


def get_used_names(filepath: Path) -> Set[str]:
    """Получает все используемые имена через AST."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(filepath))
        checker = ImportUsageChecker()
        checker.visit(tree)
        return checker.used_names
    except Exception as e:
        print(f"  Ошибка AST для {filepath}: {e}")
        return set()


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
    if module and any(
        m in module for m in ["typing", "typing_extensions", "collections.abc"]
    ):
        return True
    return False


def fix_file_imports(filepath: Path) -> bool:
    """Исправляет импорты в файле."""
    print(f"\n{'=' * 60}")
    print(f"Обрабатываю: {filepath}")

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Ошибка чтения: {e}")
        return False

    used_names = get_used_names(filepath)
    lines = content.split("\n")

    try:
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        print(f"  Ошибка парсинга: {e}")
        return False

    # Находим все импорты
    imports_info = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports_info.append(
                    {
                        "lineno": node.lineno,
                        "name": alias.asname or alias.name,
                        "module": None,
                        "type": "import",
                        "full_name": alias.name,
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                imports_info.append(
                    {
                        "lineno": node.lineno,
                        "name": alias.asname or alias.name,
                        "module": node.module,
                        "type": "from",
                        "full_name": f"{node.module}.{alias.name}"
                        if node.module
                        else alias.name,
                    }
                )

    # Проверяем каждый импорт
    unused_imports = []
    type_imports = []

    for imp in imports_info:
        name = imp["name"]
        lineno = imp["lineno"]
        module = imp["module"]

        # Проверяем использование
        is_used = name in used_names

        # Дополнительная проверка через строковый поиск
        if not is_used:
            # Ищем использование в коде (исключая строку импорта)
            search_lines = [l for i, l in enumerate(lines) if i != lineno - 1]
            search_content = "\n".join(search_lines)

            # Ищем точное совпадение имени
            pattern = r"\b" + re.escape(name) + r"\b"
            if re.search(pattern, search_content):
                # Проверяем, что это не просто часть другого слова или комментария
                for line in search_lines:
                    if re.search(pattern, line) and not line.strip().startswith("#"):
                        is_used = True
                        break

        if not is_used:
            if is_type_hint(name, module):
                type_imports.append(imp)
                print(
                    f"  ✗ Тип не используется: {name} (строка {lineno}) → переместить в TYPE_CHECKING"
                )
            else:
                unused_imports.append(imp)
                print(f"  ✗ Не используется: {name} (строка {lineno}) → удалить")
        else:
            print(f"  ✓ Используется: {name}")

    if not unused_imports and not type_imports:
        print("  - Все импорты используются")
        return False

    # Удаляем неиспользуемые импорты
    modified = False

    # Сортируем по номерам строк (обратный порядок для безопасного удаления)
    for imp in sorted(unused_imports, key=lambda x: x["lineno"], reverse=True):
        lineno = imp["lineno"] - 1  # 0-based index
        if 0 <= lineno < len(lines):
            line = lines[lineno]
            name = imp["name"]

            if imp["type"] == "import":
                # Простой импорт: import name
                if line.strip() == f"import {name}":
                    del lines[lineno]
                    modified = True
                elif f"import {name}" in line:
                    # Множественный импорт
                    imports_list = [
                        a.strip().split(" as ")[0]
                        for a in line.split("import")[1].split(",")
                    ]
                    if len(imports_list) == 1:
                        del lines[lineno]
                        modified = True
                    else:
                        # Удаляем из списка
                        new_line = re.sub(
                            r",\s*" + re.escape(name) + r"(?:\s+as\s+\w+)?", "", line
                        )
                        new_line = re.sub(
                            r"\b" + re.escape(name) + r"(?:\s+as\s+\w+)?\s*,",
                            "",
                            new_line,
                        )
                        if new_line != line:
                            lines[lineno] = new_line
                            modified = True

            elif imp["type"] == "from":
                # from module import name
                module = imp["module"]
                if module and f"from {module} import" in line:
                    after_import = (
                        line.split("import", 1)[1] if "import" in line else ""
                    )
                    imports_list = [
                        a.strip().split(" as ")[0] for a in after_import.split(",")
                    ]

                    if len(imports_list) == 1 and name in imports_list:
                        del lines[lineno]
                        modified = True
                    elif name in imports_list:
                        # Удаляем из множественного импорта
                        # Удаляем запятую и имя
                        pattern1 = r",\s*" + re.escape(name) + r"(?:\s+as\s+\w+)?\b"
                        pattern2 = r"\b" + re.escape(name) + r"(?:\s+as\s+\w+)?\s*,"
                        new_line = re.sub(pattern1, "", line)
                        new_line = re.sub(pattern2, "", new_line)
                        if new_line != line:
                            lines[lineno] = new_line
                            modified = True

    # Обрабатываем типы - перемещаем в TYPE_CHECKING
    if type_imports:
        # Проверяем, есть ли уже TYPE_CHECKING блок
        has_type_checking = False
        type_checking_start = -1

        for i, line in enumerate(lines):
            if "TYPE_CHECKING" in line and "import" in line:
                has_type_checking = True
                type_checking_start = i
                break

        # Группируем типы по модулям
        type_imports_by_module: Dict[Optional[str], List[str]] = {}
        for imp in type_imports:
            module = imp["module"]
            name = imp["name"]
            if module not in type_imports_by_module:
                type_imports_by_module[module] = []
            type_imports_by_module[module].append(name)

        # Удаляем старые импорты типов
        for imp in sorted(type_imports, key=lambda x: x["lineno"], reverse=True):
            lineno = imp["lineno"] - 1
            if 0 <= lineno < len(lines):
                line = lines[lineno]
                name = imp["name"]

                if imp["type"] == "from" and imp["module"]:
                    module = imp["module"]
                    if f"from {module} import" in line:
                        after_import = (
                            line.split("import", 1)[1] if "import" in line else ""
                        )
                        imports_list = [
                            a.strip().split(" as ")[0] for a in after_import.split(",")
                        ]

                        if len(imports_list) == 1 and name in imports_list:
                            del lines[lineno]
                            modified = True
                        elif name in imports_list:
                            pattern1 = r",\s*" + re.escape(name) + r"(?:\s+as\s+\w+)?\b"
                            pattern2 = r"\b" + re.escape(name) + r"(?:\s+as\s+\w+)?\s*,"
                            new_line = re.sub(pattern1, "", line)
                            new_line = re.sub(pattern2, "", new_line)
                            if new_line != line:
                                lines[lineno] = new_line
                                modified = True

        # Добавляем TYPE_CHECKING блок если его нет
        if not has_type_checking:
            # Находим место для вставки (после __future__ импортов, перед остальными)
            insert_pos = 0
            for i, line in enumerate(lines):
                if (
                    "from __future__" in line
                    or line.strip().startswith('"""')
                    or line.strip().startswith("'''")
                ):
                    insert_pos = i + 1
                elif line.strip() and not line.strip().startswith("#"):
                    break

            # Вставляем TYPE_CHECKING блок
            type_checking_block = [
                "from typing import TYPE_CHECKING",
                "",
                "if TYPE_CHECKING:",
            ]

            for module, names in type_imports_by_module.items():
                if module:
                    type_checking_block.append(
                        f"    from {module} import {', '.join(names)}  # noqa: F401"
                    )
                else:
                    type_checking_block.append(
                        f"    from typing import {', '.join(names)}  # noqa: F401"
                    )

            lines[insert_pos:insert_pos] = type_checking_block
            modified = True
        else:
            # Добавляем в существующий блок
            if type_checking_start >= 0:
                # Находим конец блока TYPE_CHECKING
                end_pos = type_checking_start + 1
                indent_level = 0
                for i in range(type_checking_start, len(lines)):
                    if "if TYPE_CHECKING:" in lines[i]:
                        indent_level = len(lines[i]) - len(lines[i].lstrip())
                    elif (
                        lines[i].strip()
                        and len(lines[i]) - len(lines[i].lstrip()) <= indent_level
                    ):
                        if i > type_checking_start:
                            end_pos = i
                            break

                # Добавляем импорты в блок
                for module, names in type_imports_by_module.items():
                    if module:
                        lines.insert(
                            end_pos,
                            f"    from {module} import {', '.join(names)}  # noqa: F401",
                        )
                    else:
                        lines.insert(
                            end_pos,
                            f"    from typing import {', '.join(names)}  # noqa: F401",
                        )
                    end_pos += 1
                modified = True

    if modified:
        new_content = "\n".join(lines)
        # Убираем множественные пустые строки
        new_content = re.sub(r"\n\n\n+", "\n\n", new_content)
        filepath.write_text(new_content, encoding="utf-8")
        print("  ✓ Файл обновлен")
        return True

    return False


def get_f401_files() -> List[str]:
    """Получает список файлов с F401 ошибками."""
    try:
        result = subprocess.run(
            [
                "python3",
                "-m",
                "flake8",
                ".",
                "--select=F401",
                "--exclude=.git,__pycache__,venv,env,node_modules,build,dist,*.pyc,fix_*.py",
            ],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        files = set()
        for line in result.stdout.split("\n"):
            if "F401" in line and ".py:" in line:
                filepath = line.split(":")[0]
                if filepath and filepath.endswith(".py"):
                    files.add(filepath)

        return sorted(files)
    except Exception as e:
        print(f"Ошибка получения списка файлов: {e}")
        return []


def main():
    print("=" * 60)
    print("Полное исправление всех F401 ошибок")
    print("=" * 60)

    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 60}")
        print(f"Итерация {iteration}")
        print(f"{'=' * 60}")

        files_with_f401 = get_f401_files()

        if not files_with_f401:
            print("\n✓ Все F401 ошибки исправлены!")
            break

        print(f"\nНайдено {len(files_with_f401)} файлов с F401 ошибками")

        fixed_count = 0
        for filepath_str in files_with_f401:
            filepath = Path(filepath_str)
            if filepath.exists():
                if fix_file_imports(filepath):
                    fixed_count += 1

        if fixed_count == 0:
            print("\nНет изменений в этой итерации.")
            print("Возможно, остались только типы в TYPE_CHECKING (это нормально)")
            break

        print(f"\nИсправлено файлов: {fixed_count}")

    # Финальная проверка
    print(f"\n{'=' * 60}")
    print("Финальная проверка...")
    final_files = get_f401_files()
    if final_files:
        print(f"Осталось {len(final_files)} файлов с F401:")
        for f in final_files[:10]:
            print(f"  - {f}")
        if len(final_files) > 10:
            print(f"  ... и еще {len(final_files) - 10}")
    else:
        print("✓ Все F401 ошибки исправлены!")


if __name__ == "__main__":
    main()
