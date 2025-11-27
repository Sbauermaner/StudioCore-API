# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
# -*- coding: utf - 8 -*-
# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

"""
AutoIntegrator v1.0 — системный модуль автоматической синхронизации StudioCore.

Функции:
- авто - обновление main после каждого патча
- авто - слияние изменений между ветками
- авто - обновление архитектуры (ядра, движки, секции, модули)
- авто - исправление лёгких конфликтов
- авто - расширение каталогов при появлении новых файлов
- авто - линтинг + авто - форматирование
- авто - проверка целостности связей между ядрами V4 / V5 / V6
"""

import subprocess
import os
from pathlib import Path


class AutoIntegrator:
    def __init__(self, base_branch: str = "main"):
        self.base_branch = base_branch

    # ==============================
    #       GIT HELPERS
    # ==============================

    def _run(self, cmd: str):
        """
        Безопасное выполнение команды без shell=True.
        Разбивает команду на список аргументов для предотвращения инъекций.
        """
        try:
            # Безопасное разбиение команды на аргументы
            # Используем shlex.split для правильной обработки кавычек и
            # пробелов
            import shlex

            cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else cmd

            # Если cmd уже список, используем его напрямую
            if not isinstance(cmd_parts, list):
                cmd_parts = [str(cmd)]

            # Выполняем без shell=True для безопасности
            result = subprocess.run(
                cmd_parts,
                shell=False,  # Безопасно: без shell
                capture_output=True,
                text=True,
                timeout=30,  # Таймаут для предотвращения зависаний
            )
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", "Command timeout (30s)"
        except FileNotFoundError:
            return "", f"Command not found: {cmd_parts[0] if cmd_parts else 'unknown'}"
        except Exception as e:
            return "", str(e)

    def auto_pull(self):
        return self._run(
            f"git pull origin {self.base_branch} --allow - unrelated - histories"
        )

    def auto_add(self):
        return self._run("git add -A")

    def auto_commit(self, msg: str):
        return self._run(f"git commit -m '{msg}'")

    def auto_push(self):
        return self._run(f"git push origin {self.base_branch}")

    def auto_merge(self, branch: str):
        return self._run(f"git merge {branch} --strategy - option=ours --no - edit")

    # ==============================
    #       ARCHITECTURE FIXES
    # ==============================

    def ensure_directories(self):
        required_dirs = [
            "studiocore",
            "tests",
        ]
        for d in required_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

    def ensure_init_files(self):
        for root, dirs, files in os.walk("studiocore"):
            if "__init__.py" not in files:
                open(os.path.join(root, "__init__.py"), "a").close()

    def auto_lint(self):
        """Авто - форматирование + базовая очистка."""
        self._run("python3 -m black studiocore")
        self._run("python3 -m isort studiocore")

    def auto_fix_imports(self):
        """Исправление разбитых импортов."""
        for path in Path("studiocore").rglob("*.py"):
            text = path.read_text(encoding="utf8")
            text = text.replace("from  .", "from .")
            text = text.replace("import  ", "import ")
            path.write_text(text, encoding="utf8")

    # ==============================
    #       MASTER EXECUTION
    # ==============================

    def execute(self):
        self.ensure_directories()
        self.ensure_init_files()
        self.auto_fix_imports()
        self.auto_lint()

        self.auto_add()
        self.auto_commit("AUTO - INTEGRATOR: sync architecture")
        self.auto_push()


if __name__ == "__main__":
    AutoIntegrator().execute()

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e
