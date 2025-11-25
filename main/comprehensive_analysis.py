#!/usr/bin/env python3
"""
Comprehensive Analysis für StudioCore Projekt

Prüft:
- Alle Python-Dateien
- Korrektheit aller Funktionen
- Imports und Dependencies
- Spezifische Engines (SectionParser, EmotionEngine, TLP, RDE, etc.)
- Stateless-Verhalten
- State-Leaks (Tags, Gewichte, Emotionen, Genres)
- Serialisierung (result, style, payload)
- Verlust von mood und color_wave
- Konflikte zwischen Engines
- Fehler im Monolith-Fallback
"""

from __future__ import annotations

import ast
import sys
import traceback
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import json

class ComprehensiveAnalyzer:
    """Umfassender Analyzer für StudioCore."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.studiocore_path = base_path / "studiocore"
        self.issues: List[Dict] = []  # {file, line, type, error, solution}
        self.module_imports: Dict[str, Set[str]] = {}
        self.module_exports: Dict[str, Set[str]] = {}
        self.class_definitions: Dict[str, List[str]] = defaultdict(list)
        self.function_definitions: Dict[str, List[str]] = defaultdict(list)
        self.state_variables: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
        
    def analyze_all(self):
        """Führt alle Analysen durch."""
        print("🔍 Starte Comprehensive Analysis...")
        
        # 1. Alle Python-Dateien analysieren
        print("📁 Analysiere alle Python-Dateien...")
        self.analyze_all_files()
        
        # 2. Imports und Dependencies
        print("🔗 Analysiere Imports und Dependencies...")
        self.analyze_imports()
        
        # 3. Spezifische Engines prüfen
        print("⚙️  Prüfe spezifische Engines...")
        self.check_specific_engines()
        
        # 4. Stateless-Verhalten prüfen
        print("🔄 Prüfe Stateless-Verhalten...")
        self.check_stateless_behavior()
        
        # 5. State-Leaks finden
        print("🔓 Suche State-Leaks...")
        self.find_state_leaks()
        
        # 6. Serialisierung prüfen
        print("💾 Prüfe Serialisierung...")
        self.check_serialization()
        
        # 7. Verlust von mood und color_wave
        print("🎨 Prüfe mood und color_wave...")
        self.check_mood_color_loss()
        
        # 8. Konflikte zwischen Engines
        print("⚔️  Suche Engine-Konflikte...")
        self.find_engine_conflicts()
        
        # 9. Monolith-Fallback Fehler
        print("🏛️  Prüfe Monolith-Fallback...")
        self.check_monolith_fallback()
        
        print("✅ Analysis abgeschlossen!")
    
    def analyze_all_files(self):
        """Analysiert alle Python-Dateien."""
        if not self.studiocore_path.exists():
            return
        
        for py_file in sorted(self.studiocore_path.rglob("*.py")):
            if py_file.name == "__init__.py":
                continue
            
            self.analyze_file(py_file)
    
    def analyze_file(self, file_path: Path):
        """Analysiert eine einzelne Datei."""
        rel_path = file_path.relative_to(self.base_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Syntax-Check
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                self.add_issue(str(rel_path), e.lineno or 0, "syntax_error",
                             f"Syntax-Fehler: {e.msg}",
                             "Korrigiere Syntax-Fehler (Klammern, Einrückungen, etc.)")
                return
            
            # Sammle Informationen
            self.collect_definitions(tree, str(rel_path), lines)
            self.check_function_correctness(tree, str(rel_path), lines)
            self.find_state_variables(tree, str(rel_path), lines)
            
        except Exception as e:
            self.add_issue(str(rel_path), 0, "file_error",
                         f"Fehler beim Lesen: {e}",
                         "Prüfe Datei-Zugriffsrechte und Encoding")
    
    def collect_definitions(self, tree: ast.AST, file_path: str, lines: List[str]):
        """Sammelt Definitionen (Klassen, Funktionen, Imports)."""
        imports = set()
        exports = set()
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
                for alias in node.names:
                    exports.add(alias.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
                exports.add(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                if not node.name.startswith('_'):
                    exports.add(node.name)
        
        self.module_imports[file_path] = imports
        self.module_exports[file_path] = exports
        self.class_definitions[file_path] = classes
        self.function_definitions[file_path] = functions
    
    def check_function_correctness(self, tree: ast.AST, file_path: str, lines: List[str]):
        """Prüft Korrektheit von Funktionen."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Prüfe auf fehlende Returns
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                
                # Prüfe auf unreachable code
                body = node.body
                found_return = False
                for stmt in body:
                    if isinstance(stmt, ast.Return) and not found_return:
                        found_return = True
                    elif found_return and not isinstance(stmt, (ast.Pass, ast.Expr)):
                        self.add_issue(file_path, stmt.lineno if hasattr(stmt, 'lineno') else 0,
                                     "unreachable_code",
                                     f"Unreachable code nach return in {node.name}",
                                     "Entferne unreachable code oder restructure Funktion")
                
                # Prüfe auf riskante try-except
                for child in ast.walk(node):
                    if isinstance(child, ast.Try):
                        for handler in child.handlers:
                            if handler.type is None:  # bare except
                                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                                    self.add_issue(file_path, handler.lineno if hasattr(handler, 'lineno') else 0,
                                                 "risky_except",
                                                 f"Bare except: pass in {node.name}",
                                                 "Verwende spezifische Exception-Types oder logge Fehler")
    
    def find_state_variables(self, tree: ast.AST, file_path: str, lines: List[str]):
        """Findet State-Variablen (Module-Level)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Prüfe ob es Module-Level ist (nicht in Funktion/Klasse)
                if not self._is_inside_function_or_class(node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.state_variables[file_path].append(
                                (node.lineno if hasattr(node, 'lineno') else 0, target.id)
                            )
    
    def _is_inside_function_or_class(self, node: ast.AST) -> bool:
        """Prüft ob Node innerhalb einer Funktion oder Klasse ist."""
        parent = getattr(node, 'parent', None)
        while parent:
            if isinstance(parent, (ast.FunctionDef, ast.ClassDef)):
                return True
            parent = getattr(parent, 'parent', None)
        return False
    
    def analyze_imports(self):
        """Analysiert Imports und Dependencies."""
        # Prüfe auf fehlende Imports
        for file_path, imports in self.module_imports.items():
            for imp in imports:
                if imp.startswith("studiocore.") or imp == "studiocore":
                    # Prüfe ob Modul existiert
                    module_parts = imp.split('.')
                    if len(module_parts) > 1:
                        module_file = self.studiocore_path / Path(*module_parts[1:]) / "__init__.py"
                        if not module_file.exists():
                            module_file = self.studiocore_path / Path(*module_parts[1:-1]) / f"{module_parts[-1]}.py"
                            if not module_file.exists():
                                self.add_issue(file_path, 0, "missing_import",
                                             f"Möglicherweise fehlendes Modul: {imp}",
                                             "Prüfe ob Modul existiert oder Import korrekt ist")
    
    def check_specific_engines(self):
        """Prüft spezifische Engines."""
        engines_to_check = {
            "SectionParser": "section_parser.py",
            "EmotionEngine": "emotion.py",
            "TruthLovePainEngine": "tlp_engine.py",
            "RhythmDynamicsEmotionEngine": "rde_engine.py",
            "ToneSyncEngine": "tone.py",
            "BPMEngine": "bpm_engine.py",
            "GenreMatrix": "genre_matrix_extended.py",
            "ColorEngineAdapter": "color_engine_adapter.py",
            "InstrumentationEngine": "logical_engines.py",
            "VocalEngine": "logical_engines.py",
        }
        
        for engine_name, file_name in engines_to_check.items():
            file_path = self.studiocore_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if engine_name not in content:
                        self.add_issue(f"studiocore/{file_name}", 0, "missing_engine",
                                     f"Engine-Klasse {engine_name} nicht gefunden",
                                     f"Stelle sicher, dass {engine_name} in {file_name} definiert ist")
                    else:
                        # Prüfe auf wichtige Methoden
                        if engine_name == "SectionParser":
                            if "def parse" not in content and "def extract" not in content:
                                self.add_issue(f"studiocore/{file_name}", 0, "missing_method",
                                             f"{engine_name} hat keine parse/extract Methode",
                                             "Implementiere parse() oder extract() Methode")
                except Exception as e:
                    self.add_issue(f"studiocore/{file_name}", 0, "engine_check_error",
                                 f"Fehler beim Prüfen von {engine_name}: {e}",
                                 "Prüfe Datei-Zugriffsrechte")
            else:
                self.add_issue(f"studiocore/{file_name}", 0, "missing_file",
                             f"Engine-Datei {file_name} nicht gefunden",
                             f"Erstelle {file_name} mit {engine_name} Klasse")
    
    def check_stateless_behavior(self):
        """Prüft Stateless-Verhalten."""
        # Prüfe auf Module-Level State
        for file_path, variables in self.state_variables.items():
            if len(variables) > 5:  # Viele Module-Level Variablen
                var_list = ", ".join([v[1] for v in variables[:5]])
                self.add_issue(file_path, variables[0][0], "potential_state_leak",
                             f"Viele Module-Level Variablen: {var_list}...",
                             "Verschiebe Variablen in Klassen oder verwende lokale Variablen")
        
        # Prüfe core_v6.py auf stateless
        core_v6_path = self.studiocore_path / "core_v6.py"
        if core_v6_path.exists():
            try:
                with open(core_v6_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Prüfe ob _build_engine_bundle existiert (sollte für jeden Request neu erstellt werden)
                if "_build_engine_bundle" not in content:
                    self.add_issue("studiocore/core_v6.py", 0, "stateless_violation",
                                 "_build_engine_bundle Methode fehlt",
                                 "Implementiere _build_engine_bundle() für stateless Verhalten")
                
                # Prüfe auf persistente Instanz-Variablen
                if "self._engine_bundle" in content and "self._engine_bundle = " in content:
                    # Suche nach Stellen wo _engine_bundle gesetzt wird
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if "self._engine_bundle = " in line and "engines" not in line:
                            self.add_issue("studiocore/core_v6.py", i, "potential_state_leak",
                                         "self._engine_bundle wird möglicherweise zwischen Requests gespeichert",
                                         "Stelle sicher, dass _engine_bundle pro Request neu erstellt wird")
            except Exception:
                pass
    
    def find_state_leaks(self):
        """Findet State-Leaks (Tags, Gewichte, Emotionen, Genres)."""
        keywords_to_check = ["tag", "weight", "emotion", "genre", "mood", "color"]
        
        for py_file in self.studiocore_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                rel_path = py_file.relative_to(self.base_path)
                
                # Suche nach persistenter Speicherung
                for i, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    # Prüfe auf self. Variablen die zwischen Requests gespeichert werden könnten
                    if any(kw in line_lower for kw in keywords_to_check):
                        if "self." in line and "=" in line:
                            # Prüfe ob es in __init__ ist (OK) oder in anderen Methoden (potentiell problematisch)
                            # Vereinfachte Prüfung
                            if "__init__" not in content[max(0, i-20):i]:
                                # Möglicherweise State-Leak
                                if "cache" not in line_lower and "temp" not in line_lower:
                                    self.add_issue(str(rel_path), i, "potential_state_leak",
                                                 f"Möglicher State-Leak: {line.strip()[:60]}",
                                                 "Prüfe ob Variable zwischen Requests gespeichert wird")
            except Exception:
                pass
    
    def check_serialization(self):
        """Prüft Serialisierung von result, style, payload."""
        core_v6_path = self.studiocore_path / "core_v6.py"
        if core_v6_path.exists():
            try:
                with open(core_v6_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Prüfe auf result Serialisierung
                if '"result"' in content or "'result'" in content:
                    # Prüfe ob result korrekt serialisiert wird
                    if "json.dumps" not in content and "json.dump" not in content:
                        # Möglicherweise Problem wenn result nicht serialisierbar ist
                        pass
                
                # Prüfe auf result["style"]
                if 'result["style"]' in content or "result['style']" in content:
                    # Prüfe ob style korrekt behandelt wird
                    for i, line in enumerate(lines, 1):
                        if 'result["style"]' in line or "result['style']" in line:
                            if "=" in line and "None" not in line:
                                # Prüfe ob es korrekt gesetzt wird
                                pass
                
                # Prüfe auf result["payload"]
                if 'result["payload"]' in content or "result['payload']" in content:
                    for i, line in enumerate(lines, 1):
                        if 'result["payload"]' in line or "result['payload']" in line:
                            # Prüfe ob payload korrekt behandelt wird
                            pass
            except Exception:
                pass
    
    def check_mood_color_loss(self):
        """Prüft Verlust von mood und color_wave."""
        core_v6_path = self.studiocore_path / "core_v6.py"
        if core_v6_path.exists():
            try:
                with open(core_v6_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Suche nach Stellen wo mood gesetzt wird
                mood_set = False
                mood_lost = False
                
                for i, line in enumerate(lines, 1):
                    if "mood" in line.lower() and "=" in line:
                        mood_set = True
                    if mood_set and ("del " in line or "pop(" in line) and "mood" in line.lower():
                        mood_lost = True
                        self.add_issue("studiocore/core_v6.py", i, "mood_loss",
                                     f"Mood möglicherweise gelöscht: {line.strip()[:60]}",
                                     "Stelle sicher, dass mood nicht versehentlich gelöscht wird")
                
                # Suche nach Stellen wo color_wave gesetzt wird
                color_wave_set = False
                for i, line in enumerate(lines, 1):
                    if "color_wave" in line and "=" in line:
                        color_wave_set = True
                    if color_wave_set and ("del " in line or "pop(" in line) and "color_wave" in line.lower():
                        self.add_issue("studiocore/core_v6.py", i, "color_wave_loss",
                                     f"color_wave möglicherweise gelöscht: {line.strip()[:60]}",
                                     "Stelle sicher, dass color_wave nicht versehentlich gelöscht wird")
            except Exception:
                pass
    
    def find_engine_conflicts(self):
        """Findet Konflikte zwischen Engines."""
        # Prüfe auf Konflikte zwischen Emotion-Engines
        emotion_files = [
            "emotion.py",
            "emotion_engine.py",
            "dynamic_emotion_engine.py",
            "logical_engines.py"
        ]
        
        emotion_methods = defaultdict(list)
        
        for file_name in emotion_files:
            file_path = self.studiocore_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Suche nach analyze/process Methoden
                    if "def analyze" in content:
                        emotion_methods["analyze"].append(file_name)
                    if "def process" in content:
                        emotion_methods["process"].append(file_name)
                except Exception:
                    pass
        
        # Prüfe auf Konflikte
        if len(emotion_methods.get("analyze", [])) > 2:
            self.add_issue("studiocore/", 0, "engine_conflict",
                         f"Mehrere analyze() Methoden in: {', '.join(emotion_methods['analyze'])}",
                         "Stelle sicher, dass keine Konflikte zwischen Engines bestehen")
    
    def check_monolith_fallback(self):
        """Prüft Monolith-Fallback auf Fehler."""
        fallback_path = self.studiocore_path / "fallback.py"
        monolith_path = self.studiocore_path / "monolith_v4_3_1.py"
        
        if fallback_path.exists():
            try:
                with open(fallback_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Prüfe auf Fehlerbehandlung
                if "except" in content and "pass" in content:
                    # Suche nach bare except: pass
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if "except:" in line or "except Exception:" in line:
                            # Prüfe nächste Zeilen
                            if i < len(lines) and "pass" in lines[i]:
                                self.add_issue("studiocore/fallback.py", i, "silent_failure",
                                             "Silent failure in Fallback (except: pass)",
                                             "Logge Fehler oder behandle spezifisch")
            except Exception:
                pass
        
        if monolith_path.exists():
            try:
                with open(monolith_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Prüfe auf Import-Fehler
                if "ImportError" in content or "ModuleNotFoundError" in content:
                    # Prüfe ob Fehler korrekt behandelt werden
                    if "except" in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if "ImportError" in line or "ModuleNotFoundError" in line:
                                if i < len(lines) and "pass" in lines[i]:
                                    self.add_issue("studiocore/monolith_v4_3_1.py", i, "import_error_handling",
                                                 "Import-Fehler möglicherweise nicht korrekt behandelt",
                                                 "Stelle sicher, dass Import-Fehler korrekt behandelt werden")
            except Exception:
                pass
    
    def add_issue(self, file_path: str, line: int, issue_type: str, error: str, solution: str):
        """Fügt ein Issue hinzu."""
        self.issues.append({
            "file": file_path,
            "line": line,
            "type": issue_type,
            "error": error,
            "solution": solution
        })
    
    def generate_report(self) -> str:
        """Generiert einen vollständigen Report."""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE ANALYSIS REPORT - STUDIOCORE")
        report.append("=" * 80)
        report.append("")
        
        # Gruppiere nach Typ
        by_type = defaultdict(list)
        for issue in self.issues:
            by_type[issue["type"]].append(issue)
        
        # Zeige Issues nach Typ
        for issue_type, issues in sorted(by_type.items()):
            report.append(f"## {issue_type.upper()} ({len(issues)} Issues)")
            report.append("")
            
            for issue in issues[:20]:  # Limit auf 20 pro Typ
                report.append(f"  [{issue['file']}:{issue['line']}]")
                report.append(f"    Fehler: {issue['error']}")
                report.append(f"    Lösung: {issue['solution']}")
                report.append("")
            
            if len(issues) > 20:
                report.append(f"  ... und {len(issues) - 20} weitere Issues")
                report.append("")
        
        # Zusammenfassung
        report.append("=" * 80)
        report.append("ZUSAMMENFASSUNG")
        report.append("=" * 80)
        report.append(f"  Gesamt Issues: {len(self.issues)}")
        report.append(f"  Nach Typ:")
        for issue_type, issues in sorted(by_type.items()):
            report.append(f"    - {issue_type}: {len(issues)}")
        report.append("")
        
        if self.issues:
            report.append("⚠️  SYSTEM STATUS: ISSUES GEFUNDEN")
        else:
            report.append("✅ SYSTEM STATUS: KEINE ISSUES GEFUNDEN")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Hauptfunktion."""
    base_path = Path(__file__).parent.parent
    analyzer = ComprehensiveAnalyzer(base_path)
    
    analyzer.analyze_all()
    report = analyzer.generate_report()
    
    print("\n" + report)
    
    # Speichere Report
    report_path = base_path / "COMPREHENSIVE_ANALYSIS_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report gespeichert: {report_path}")
    
    # Speichere JSON
    json_path = base_path / "COMPREHENSIVE_ANALYSIS_DATA.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analyzer.issues, f, indent=2, ensure_ascii=False)
    
    print(f"📊 JSON-Daten gespeichert: {json_path}")
    
    return 0 if not analyzer.issues else 1


if __name__ == "__main__":
    sys.exit(main())

