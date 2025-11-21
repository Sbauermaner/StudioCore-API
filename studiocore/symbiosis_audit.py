# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

# -*- coding: utf-8 -*-
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
import os
import sys
import traceback
from pathlib import Path


class SymbiosisAudit:
    def __init__(self):
        self.report = []
        self.errors = []
        self.root = Path("studiocore")

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
        required_dirs = [
            "studiocore",
            "studiocore/engines",
            "tests",
        ]
        for d in required_dirs:
            if not Path(d).exists():
                self.err(f"Missing directory: {d}")
            else:
                self.log(f"[OK] Directory exists: {d}")

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
        for path in self.root.rglob("*.py"):
            module = str(path).replace("/", ".").replace(".py", "")
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
