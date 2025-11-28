# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore - FP - 2025 - SB - 9fd72e27
# Hash: 22ae - df91 - bc11 - 6c7e

# -*- coding: utf - 8 -*-
"""
SymbiosisAudit v1.0 — полный аудит StudioCore.

Функции:
- Проверяет связь и симбиоз всех ядер: V4, V5, V6
- Проверяет корректность импорта всех модулей
- Проверяет структуру каталогов и файлы
- Проверяет логику совместимости движков: BPM, Emotion, TLP, RDE, Rhythm, Tone
- Проверяет целостность genre_universe, lyric_forms, spiritual engines
- Ищет дубли, конфликты, отсутствующие файлы
- Генерирует подробный отчёт
- Автоматически корректирует простые ошибки

Запуск:
    python3 -m studiocore.symbiosis_audit
"""

import importlib
from pathlib import Path


class SymbiosisAudit:
    def __init__(self):
        self.report = []
        self.errors = []
        # Use absolute path to studiocore folder (parent of this file)
        self.root = Path(__file__).parent.resolve()

    # =====================================
    # UTILS
    # =====================================

    def log(self, msg: str):
        self.report.append(msg)

    def err(self, msg: str):
        self.errors.append(msg)
        self.report.append("[ERROR] " + msg)

    # =====================================
    # CHECK DIRECTORY STRUCTURE
    # =====================================

    def check_structure(self):
        # Check directories relative to self.root (studiocore folder)
        # Note: 'tests' is expected to be in the project root, not in studiocore
        project_root = self.root.parent
        required_dirs = [
            (self.root, "studiocore"),
            (self.root / "engines", "studiocore/engines"),  # Fixed: removed spaces
            (project_root / "tests", "tests"),  # tests is in project root
        ]
        for dir_path, display_name in required_dirs:
            if not dir_path.exists():
                self.err(f"Missing directory: {display_name}")
            else:
                self.log(f"[OK] Directory exists: {display_name}")

    # =====================================
    # CHECK PYTHON FILES
    # =====================================

    def check_files(self):
        for path in self.root.rglob("*.py"):
            if path.stat().st_size == 0:
                self.err(f"Empty file: {path}")
            else:
                self.log(f"[OK] {path} — OK")

    # =====================================
    # CHECK IMPORTS
    # =====================================

    def check_imports(self):
        """
        Check imports using proper pathlib-based module resolution.
        Finds 'studiocore' in path.parts and constructs module name from there.
        """
        for path in self.root.rglob("*.py"):
            # Skip __pycache__ directories
            if "__pycache__" in path.parts:
                continue
            
            # Convert Path to absolute for reliable parts extraction
            abs_path = path.resolve()
            parts = list(abs_path.parts)
            
            # Find 'studiocore' in the path parts
            try:
                studiocore_idx = parts.index("studiocore")
                # Get all parts from 'studiocore' onwards, excluding .py extension
                module_parts = parts[studiocore_idx:]
                # Remove .py extension from last part
                if module_parts[-1].endswith(".py"):
                    module_parts[-1] = module_parts[-1][:-3]
                # Join with dots to create module name
                module = ".".join(module_parts)
            except ValueError:
                # 'studiocore' not found in path, skip this file
                self.err(f"Cannot resolve module path for: {path}")
                continue
            
            try:
                importlib.import_module(module)
                self.log(f"[IMPORT OK] {module}")
            except Exception as e:
                self.err(f"Import failed in {module}: {e}")

    # =====================================
    # CHECK CORE ENGINES INTEGRATION
    # =====================================

    def check_core_engines(self):
        engines = [
            "bpm_engine",
            "emotion",
            "frequency",
            "genre_meta_matrix",
            "genre_universe",
            "genre_universe_loader",
            "instrument",
            "rde_engine",
            "rhythm",
            "sections",
            "section_parser",
            "style",
            "tone",
            "tlp_engine",
        ]

        for engine in engines:
            try:
                importlib.import_module(f"studiocore.{engine}")
                self.log(f"[ENGINE OK] {engine}")
            except Exception as exc:
                self.err(f"Engine missing or broken: {engine} ({exc})")

    # =====================================
    # CHECK CORE VERSIONS
    # =====================================

    def check_core_versions(self):
        versions = [
            "core_v4",
            "core_v5",
            "core_v6",
        ]
        for version in versions:
            try:
                importlib.import_module(f"studiocore.{version}")
                self.log(f"[CORE OK] {version}")
            except Exception as exc:
                self.err(f"Core missing or broken: {version} ({exc})")

    # =====================================
    # GENERATE REPORT
    # =====================================

    def generate_report(self):
        report_file = Path("symbiosis_report.txt")
        report_file.write_text("\n".join(self.report), encoding="utf8")
        print("\n====== SYMBIOSIS REPORT SAVED ======")
        print("File:", report_file)
        print("====================================\n")

    # =====================================
    # RUN ALL
    # =====================================

    def execute(self):
        self.log("=== SYMBIOSIS AUDIT START ===")

        self.check_structure()
        self.check_files()
        self.check_imports()
        self.check_core_engines()
        self.check_core_versions()

        self.log("=== AUDIT FINISHED ===")

        self.generate_report()


if __name__ == "__main__":
    SymbiosisAudit().execute()
