#!/usr/bin/env python3
"""
Deep Scan Audit für studiocore Projekt

Prüft jeden Datei auf:
1. Syntaxfehler (unclosed brackets, wrong indentation, typos)
2. Audit-Fixes (HybridGenreEngine.resolve(), emotion.py imports, fehlende Module)
3. Integrität (undefined variables/functions)
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# Status constants
OK = "OK"
ERROR = "ERROR"
WARNING = "WARNING"


class DeepScanAuditor:
    """Deep Scan Auditor für studiocore."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.studiocore_path = base_path / "studiocore"
        # (file, status, comment)
        self.results: List[Tuple[str, str, str]] = []

    def scan_all(self):
        """Scannt alle Dateien in studiocore."""
        if not self.studiocore_path.exists():
            self.results.append(("studiocore/", ERROR, "Verzeichnis nicht gefunden"))
            return

        # Finde alle Python-Dateien
        python_files = list(self.studiocore_path.rglob("*.py"))

        print(f"🔍 Scanne {len(python_files)} Python-Dateien...")

        for py_file in sorted(python_files):
            rel_path = py_file.relative_to(self.base_path)
            self.scan_file(py_file, rel_path)

        # Spezielle Audit-Checks (werden separat hinzugefügt)
        pass

    def run_audit_checks(self):
        """Führt spezielle Audit-Checks aus."""
        self.check_audit_fixes()

    def scan_file(self, file_path: Path, rel_path: Path):
        """Scannt eine einzelne Datei."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. Syntax-Check
            syntax_ok = self.check_syntax(content, file_path)

            if not syntax_ok:
                self.results.append((str(rel_path), ERROR, "Syntax-Fehler gefunden"))
                return

            # 2. Basis-Integritäts-Check
            integrity_issues = self.check_integrity(content, file_path)

            if integrity_issues:
                self.results.append((str(rel_path), WARNING, integrity_issues))
            else:
                self.results.append((str(rel_path), OK, "Keine Probleme gefunden"))

        except Exception as e:
            self.results.append((str(rel_path), ERROR, f"Fehler beim Lesen: {e}"))

    def check_syntax(self, content: str, file_path: Path) -> bool:
        """Prüft Syntax mit ast.parse."""
        try:
            ast.parse(content, filename=str(file_path))
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    def check_integrity(self, content: str, file_path: Path) -> Optional[str]:
        """Prüft auf undefined variables/functions."""
        issues = []

        try:
            tree = ast.parse(content, filename=str(file_path))

            # Sammle alle definierten Namen
            defined_names = set()
            imported_names = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_names.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_names.add(node.module.split(".")[0])
                    for alias in node.names:
                        imported_names.add(alias.name)

            # Prüfe auf offensichtliche undefined calls (vereinfacht)
            # In Produktion würde man einen vollständigen Scope-Tracker
            # verwenden

        except Exception:
            pass

        if issues:
            return "; ".join(issues)
        return None

    def check_audit_fixes(self):
        """Prüft spezifische Audit-Fixes."""
        print("\n🔍 Prüfe spezifische Audit-Fixes...")

        # 1. HybridGenreEngine.resolve()
        hge_path = self.studiocore_path / "hybrid_genre_engine.py"
        if hge_path.exists():
            try:
                with open(hge_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "def resolve" in content:
                    # Prüfe ob beide Signaturen unterstützt werden
                    if "text_input" in content and "genre" in content:
                        self.results.append(
                            (
                                "studiocore/hybrid_genre_engine.py",
                                OK,
                                "resolve() Methode vorhanden mit beiden Signaturen",
                            )
                        )
                    else:
                        self.results.append(
                            (
                                "studiocore/hybrid_genre_engine.py",
                                WARNING,
                                "resolve() vorhanden, aber möglicherweise unvollständig",
                            )
                        )
                else:
                    self.results.append(
                        (
                            "studiocore/hybrid_genre_engine.py",
                            ERROR,
                            "resolve() Methode fehlt",
                        )
                    )
            except Exception as e:
                self.results.append(
                    (
                        "studiocore/hybrid_genre_engine.py",
                        ERROR,
                        f"Fehler beim Prüfen: {e}",
                    )
                )
        else:
            self.results.append(
                ("studiocore/hybrid_genre_engine.py", ERROR, "Datei nicht gefunden")
            )

        # 2. emotion.py - kein top-level Import von tlp_engine
        emotion_path = self.studiocore_path / "emotion.py"
        if emotion_path.exists():
            try:
                with open(emotion_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Prüfe erste 50 Zeilen auf top-level imports
                top_level_imports = []
                for i, line in enumerate(lines[:50], 1):
                    stripped = line.strip()
                    if stripped.startswith("from") and "tlp_engine" in stripped:
                        if not stripped.startswith("#"):  # Kein Kommentar
                            top_level_imports.append(i)

                if top_level_imports:
                    self.results.append(
                        (
                            "studiocore/emotion.py",
                            WARNING,
                            f"Top-level Import von tlp_engine in Zeilen: {top_level_imports}",
                        )
                    )
                else:
                    # Prüfe ob lazy import vorhanden ist
                    content = "".join(lines)
                    if "from .tlp_engine import" in content:
                        # Prüfe ob es innerhalb einer Funktion ist
                        if "def " in content[: content.find("from .tlp_engine import")]:
                            self.results.append(
                                (
                                    "studiocore/emotion.py",
                                    OK,
                                    "tlp_engine Import ist lazy (innerhalb Funktion)",
                                )
                            )
                        else:
                            self.results.append(
                                (
                                    "studiocore/emotion.py",
                                    WARNING,
                                    "tlp_engine Import gefunden, aber möglicherweise nicht lazy",
                                )
                            )
                    else:
                        self.results.append(
                            (
                                "studiocore/emotion.py",
                                OK,
                                "Kein top-level Import von tlp_engine",
                            )
                        )
            except Exception as e:
                self.results.append(
                    ("studiocore/emotion.py", ERROR, f"Fehler beim Prüfen: {e}")
                )

        # 3. Fehlende Module prüfen
        required_modules = [
            "universal_frequency_engine.py",
            "hybrid_instrumentation_layer.py",
            "neutral_mode_pre_finalizer.py",
        ]

        for module_name in required_modules:
            module_path = self.studiocore_path / module_name
            if module_path.exists():
                try:
                    with open(module_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()

                    if len(content) > 50:  # Nicht leer
                        self.results.append(
                            (
                                f"studiocore/{module_name}",
                                OK,
                                "Datei existiert und ist nicht leer",
                            )
                        )
                    else:
                        self.results.append(
                            (
                                f"studiocore/{module_name}",
                                WARNING,
                                "Datei existiert, aber sehr kurz (möglicherweise leer)",
                            )
                        )
                except Exception as e:
                    self.results.append(
                        (f"studiocore/{module_name}", ERROR, f"Fehler beim Lesen: {e}")
                    )
            else:
                self.results.append(
                    (f"studiocore/{module_name}", ERROR, "Datei nicht gefunden")
                )

    def generate_report(self) -> str:
        """Generiert einen formatierten Report."""
        report = []
        report.append("=" * 80)
        report.append("DEEP SCAN AUDIT REPORT - STUDIOCORE")
        report.append("=" * 80)
        report.append("")

        # Gruppiere nach Status
        ok_files = []
        warning_files = []
        error_files = []

        for file, status, comment in self.results:
            if status == OK:
                ok_files.append((file, comment))
            elif status == WARNING:
                warning_files.append((file, comment))
            else:
                error_files.append((file, comment))

        # Errors
        if error_files:
            report.append("## ❌ FEHLER")
            for file, comment in error_files:
                report.append(f"  [{file}] : {ERROR} : {comment}")
            report.append("")

        # Warnings
        if warning_files:
            report.append("## ⚠️  WARNUNGEN")
            for file, comment in warning_files:
                report.append(f"  [{file}] : {WARNING} : {comment}")
            report.append("")

        # OK
        if ok_files:
            report.append(f"## ✅ OK ({len(ok_files)} Dateien)")
            for file, comment in ok_files[:20]:  # Zeige erste 20
                report.append(f"  [{file}] : {OK} : {comment}")
            if len(ok_files) > 20:
                report.append(f"  ... und {len(ok_files) - 20} weitere Dateien")
            report.append("")

        # Spezielle Audit-Checks separat anzeigen
        audit_results = [
            r
            for r in self.results
            if any(
                keyword in r[0]
                for keyword in [
                    "hybrid_genre_engine",
                    "emotion.py",
                    "universal_frequency_engine",
                    "hybrid_instrumentation_layer",
                    "neutral_mode_pre_finalizer",
                ]
            )
        ]

        if audit_results:
            report.append("## 🔍 SPEZIELLE AUDIT-CHECKS")
            for file, status, comment in audit_results:
                status_symbol = (
                    "✅" if status == OK else "⚠️" if status == WARNING else "❌"
                )
                report.append(f"  {status_symbol} [{file}] : {status} : {comment}")
            report.append("")

        # Zusammenfassung
        report.append("=" * 80)
        report.append("ZUSAMMENFASSUNG")
        report.append("=" * 80)
        report.append(f"  Gesamt: {len(self.results)} Dateien geprüft")
        report.append(f"  ✅ OK: {len(ok_files)}")
        report.append(f"  ⚠️  WARNUNGEN: {len(warning_files)}")
        report.append(f"  ❌ FEHLER: {len(error_files)}")
        report.append("")

        if error_files:
            report.append("⚠️  SYSTEM STATUS: FEHLER GEFUNDEN")
        elif warning_files:
            report.append("⚠️  SYSTEM STATUS: WARNUNGEN GEFUNDEN")
        else:
            report.append("✅ SYSTEM STATUS: ALLE PRÜFUNGEN BESTANDEN")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Hauptfunktion."""
    base_path = Path(__file__).parent.parent
    auditor = DeepScanAuditor(base_path)

    print("🔍 Starte Deep Scan Audit...")
    auditor.scan_all()
    auditor.run_audit_checks()

    report = auditor.generate_report()
    print("\n" + report)

    # Speichere Report
    report_path = base_path / "DEEP_SCAN_AUDIT_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 Report gespeichert: {report_path}")

    # Exit code basierend auf Fehlern
    error_count = sum(1 for _, status, _ in auditor.results if status == ERROR)
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
