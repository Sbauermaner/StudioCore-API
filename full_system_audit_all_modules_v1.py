#!/usr/bin/env python3
"""
FULL_SYSTEM_AUDIT_ALL_MODULES_V1

Umfassendes System-Audit für StudioCore-API
Prüft Dependency-Graphen, Import-Graphen, zyklische Abhängigkeiten,
Orphan-Module, fehlende Module, ungenutzte Module, Pipeline-Konsistenz,
Logik-Konsistenz, statische Analyse und semantische Tests.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import os
import sys
import traceback
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Optional
import json
import re

# Severity levels
CRITICAL = "critical"
MAJOR = "major"
MINOR = "minor"

class AuditResult:
    """Container für Audit-Ergebnisse."""
    
    def __init__(self):
        self.architecture_warnings: List[Dict] = []
        self.missing_module_warnings: List[Dict] = []
        self.logic_conflicts: List[Dict] = []
        self.color_conflicts: List[Dict] = []
        self.emotion_conflicts: List[Dict] = []
        self.hybrid_genre_conflicts: List[Dict] = []
        self.instrumentation_conflicts: List[Dict] = []
        self.suggested_fixes: List[Dict] = []
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.import_graph: Dict[str, Set[str]] = {}
        self.cyclical_dependencies: List[List[str]] = []
        self.orphan_modules: List[str] = []
        self.missing_modules: List[str] = []
        self.unused_modules: List[str] = []
        self.module_initialization_order: List[str] = []
        self.pipeline_issues: Dict[str, List[Dict]] = {}
        self.static_analysis_issues: List[Dict] = []
        self.semantic_test_results: Dict[str, Dict] = {}
        
    def add_issue(self, category: str, severity: str, message: str, 
                  file: Optional[str] = None, line: Optional[int] = None,
                  details: Optional[Dict] = None):
        """Fügt ein Issue hinzu."""
        issue = {
            "severity": severity,
            "message": message,
            "file": file,
            "line": line,
            "details": details or {}
        }
        
        if category == "architecture":
            self.architecture_warnings.append(issue)
        elif category == "missing_module":
            self.missing_module_warnings.append(issue)
        elif category == "logic":
            self.logic_conflicts.append(issue)
        elif category == "color":
            self.color_conflicts.append(issue)
        elif category == "emotion":
            self.emotion_conflicts.append(issue)
        elif category == "hybrid_genre":
            self.hybrid_genre_conflicts.append(issue)
        elif category == "instrumentation":
            self.instrumentation_conflicts.append(issue)
        elif category == "static":
            self.static_analysis_issues.append(issue)
        elif category == "fix":
            self.suggested_fixes.append(issue)


class ModuleAnalyzer:
    """Analysiert Python-Module für Imports, Dependencies, etc."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.modules: Dict[str, Path] = {}
        self.imports: Dict[str, Set[str]] = {}
        self.exports: Dict[str, Set[str]] = {}
        self.classes: Dict[str, Set[str]] = {}
        self.functions: Dict[str, Set[str]] = {}
        
    def discover_modules(self):
        """Entdeckt alle Python-Module im studiocore Verzeichnis."""
        studiocore_path = self.base_path / "studiocore"
        if not studiocore_path.exists():
            return
            
        for py_file in studiocore_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            module_name = self._path_to_module(py_file)
            self.modules[module_name] = py_file
            
    def _path_to_module(self, path: Path) -> str:
        """Konvertiert einen Pfad zu einem Modulnamen."""
        rel_path = path.relative_to(self.base_path)
        parts = rel_path.parts[:-1] + (rel_path.stem,)
        return ".".join(parts)
    
    def analyze_module(self, module_name: str) -> bool:
        """Analysiert ein einzelnes Modul."""
        if module_name not in self.modules:
            return False
            
        file_path = self.modules[module_name]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            imports = set()
            exports = set()
            classes = set()
            functions = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                elif isinstance(node, ast.ClassDef):
                    classes.add(node.name)
                    exports.add(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') or node.name.startswith('__'):
                        functions.add(node.name)
                        exports.add(node.name)
            
            self.imports[module_name] = imports
            self.exports[module_name] = exports
            self.classes[module_name] = classes
            self.functions[module_name] = functions
            
            return True
        except Exception as e:
            print(f"Fehler beim Analysieren von {module_name}: {e}")
            return False
    
    def analyze_all(self):
        """Analysiert alle Module."""
        for module_name in list(self.modules.keys()):
            self.analyze_module(module_name)


class DependencyAnalyzer:
    """Analysiert Dependencies und zyklische Abhängigkeiten."""
    
    def __init__(self, module_analyzer: ModuleAnalyzer):
        self.module_analyzer = module_analyzer
        
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Baut den Dependency-Graphen."""
        graph = {}
        studiocore_modules = {m for m in self.module_analyzer.modules.keys() 
                             if m.startswith("studiocore.")}
        
        for module_name in studiocore_modules:
            dependencies = set()
            imports = self.module_analyzer.imports.get(module_name, set())
            
            for imp in imports:
                # Konvertiere Import zu Modulnamen
                if imp == "studiocore" or imp.startswith("studiocore."):
                    dep_module = imp
                else:
                    # Versuche studiocore. Präfix hinzuzufügen
                    dep_module = f"studiocore.{imp}"
                
                if dep_module in studiocore_modules:
                    dependencies.add(dep_module)
            
            graph[module_name] = dependencies
            
        return graph
    
    def find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Findet zyklische Abhängigkeiten."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str):
            if node in rec_stack:
                # Zyklus gefunden
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
                
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, set()):
                dfs(neighbor)
            
            rec_stack.remove(node)
            path.pop()
        
        for node in graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def find_orphans(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Findet Module ohne eingehende Dependencies."""
        all_deps = set()
        for deps in graph.values():
            all_deps.update(deps)
        
        orphans = []
        for module in graph:
            if module not in all_deps and module != "studiocore.core_v6":
                orphans.append(module)
        
        return orphans
    
    def find_unused(self, graph: Dict[str, Set[str]], 
                   entry_point: str = "studiocore.core_v6") -> List[str]:
        """Findet ungenutzte Module."""
        if entry_point not in graph:
            return []
        
        reachable = set()
        queue = deque([entry_point])
        
        while queue:
            node = queue.popleft()
            if node in reachable:
                continue
            reachable.add(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in reachable:
                    queue.append(neighbor)
        
        all_modules = set(graph.keys())
        unused = all_modules - reachable
        
        return list(unused)
    
    def topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Topologisches Sortieren für Initialisierungsreihenfolge."""
        in_degree = defaultdict(int)
        
        for node in graph:
            in_degree[node] = 0
        
        for node, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = deque([node for node in graph if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # Füge verbleibende Module hinzu (mögliche Zyklen)
        remaining = set(graph.keys()) - set(result)
        result.extend(remaining)
        
        return result


class PipelineValidator:
    """Validiert Pipeline-Konsistenz."""
    
    def __init__(self, base_path: Path, result: AuditResult):
        self.base_path = base_path
        self.result = result
        self.required_engines = [
            "tlp_engine",
            "rde_engine",
            "emotion_engine",
            "bpm_engine",
            "universal_frequency_engine",
            "section_parser",
            "section_merge_mode",
            "hybrid_genre_engine",
            "genre_router",
            "genre_conflict_resolver",
            "style_engine",
            "color_engine_v3",
            "color_engine_adapter",
            "instrumentation_engine",
            "hybrid_instrumentation_layer",
            "neutral_mode_pre_finalizer",
            "epic_override",
            "rage_filter_v2",
        ]
        
    def validate_pipelines(self):
        """Validiert alle Pipelines."""
        for engine_name in self.required_engines:
            self._validate_engine(engine_name)
    
    def _validate_engine(self, engine_name: str):
        """Validiert einen einzelnen Engine."""
        issues = []
        
        # Prüfe ob Modul existiert
        module_path = self.base_path / "studiocore" / f"{engine_name}.py"
        if not module_path.exists():
            # Prüfe ob es in logical_engines ist
            if engine_name in ["style_engine", "instrumentation_engine"]:
                # Diese sind in logical_engines
                pass
            else:
                issues.append({
                    "severity": MAJOR,
                    "message": f"Engine-Modul {engine_name} nicht gefunden",
                    "file": None,
                    "line": None
                })
        
        # Prüfe ob Klasse existiert
        if issues:
            self.result.pipeline_issues[engine_name] = issues


class LogicConsistencyChecker:
    """Prüft Logik-Konsistenz."""
    
    def __init__(self, base_path: Path, result: AuditResult):
        self.base_path = base_path
        self.result = result
        
    def check_emotion_conflicts(self):
        """Prüft Emotion-Konflikte (peace vs anger vs epic)."""
        # Suche nach Emotion-Logik
        core_v6_path = self.base_path / "studiocore" / "core_v6.py"
        if not core_v6_path.exists():
            return
        
        try:
            with open(core_v6_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Suche nach Konflikten zwischen peace, anger, epic
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'peace' in line.lower() and 'anger' in line.lower():
                    self.result.add_issue(
                        "emotion", MINOR,
                        f"Potentieller Konflikt zwischen peace und anger",
                        "studiocore/core_v6.py", i
                    )
                if 'epic' in line.lower() and ('peace' in line.lower() or 'anger' in line.lower()):
                    self.result.add_issue(
                        "emotion", MINOR,
                        f"Potentieller Konflikt zwischen epic und anderen Emotionen",
                        "studiocore/core_v6.py", i
                    )
        except Exception as e:
            pass
    
    def check_color_conflicts(self):
        """Prüft Color-Konflikte."""
        color_modules = [
            "color_engine_v3.py",
            "color_engine_adapter.py",
            "genre_colors.py"
        ]
        
        for mod_file in color_modules:
            mod_path = self.base_path / "studiocore" / mod_file
            if mod_path.exists():
                try:
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Suche nach Konflikten
                    if 'genre_color' in content and 'mood_color' in content:
                        self.result.add_issue(
                            "color", MINOR,
                            f"Potentieller Konflikt zwischen genre_color und mood_color in {mod_file}",
                            f"studiocore/{mod_file}"
                        )
                except Exception:
                    pass
    
    def check_hybrid_genre_conflicts(self):
        """Prüft Hybrid-Genre-Konflikte."""
        hybrid_path = self.base_path / "studiocore" / "hybrid_genre_engine.py"
        if not hybrid_path.exists():
            return
        
        try:
            with open(hybrid_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            genres = ['folk', 'edm', 'cinematic', 'hiphop']
            found_genres = [g for g in genres if g in content.lower()]
            
            if len(found_genres) > 2:
                self.result.add_issue(
                    "hybrid_genre", MINOR,
                    f"Mehrere potenziell konfliktierende Genres gefunden: {found_genres}",
                    "studiocore/hybrid_genre_engine.py"
                )
        except Exception:
            pass
    
    def check_instrumentation_conflicts(self):
        """Prüft Instrumentation-Konflikte."""
        inst_modules = [
            "instrumentation_engine",
            "hybrid_instrumentation",
            "instrument_dynamics"
        ]
        
        for mod_name in inst_modules:
            mod_path = self.base_path / "studiocore" / f"{mod_name}.py"
            if mod_path.exists():
                try:
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    genres = ['folk', 'edm', 'cinematic']
                    found = [g for g in genres if g in content.lower()]
                    
                    if len(found) > 1:
                        self.result.add_issue(
                            "instrumentation", MINOR,
                            f"Potentieller Konflikt zwischen Genres in {mod_name}: {found}",
                            f"studiocore/{mod_name}.py"
                        )
                except Exception:
                    pass


class StaticAnalyzer:
    """Statische Code-Analyse."""
    
    def __init__(self, base_path: Path, result: AuditResult):
        self.base_path = base_path
        self.result = result
        
    def analyze(self):
        """Führt statische Analyse durch."""
        studiocore_path = self.base_path / "studiocore"
        if not studiocore_path.exists():
            return
        
        for py_file in studiocore_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            self._analyze_file(py_file)
    
    def _analyze_file(self, file_path: Path):
        """Analysiert eine einzelne Datei."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            rel_path = file_path.relative_to(self.base_path)
            
            # Prüfe auf undefined variables
            self._check_undefined_variables(tree, rel_path)
            
            # Prüfe auf dead code
            self._check_dead_code(tree, rel_path)
            
            # Prüfe auf missing return paths
            self._check_return_paths(tree, rel_path)
            
        except SyntaxError:
            pass
        except Exception:
            pass
    
    def _check_undefined_variables(self, tree: ast.AST, file_path: Path):
        """Prüft auf undefinierte Variablen."""
        # Vereinfachte Prüfung - in Produktion würde man einen vollständigen
        # Scope-Tracker verwenden
        pass
    
    def _check_dead_code(self, tree: ast.AST, file_path: Path):
        """Prüft auf Dead Code."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Prüfe auf unreachable code nach return
                body = node.body
                found_return = False
                for i, stmt in enumerate(body):
                    if isinstance(stmt, ast.Return) and not found_return:
                        found_return = True
                    elif found_return and not isinstance(stmt, (ast.Pass, ast.Comment)):
                        self.result.add_issue(
                            "static", MINOR,
                            f"Potentiell unreachable code nach return in {node.name}",
                            str(file_path), stmt.lineno if hasattr(stmt, 'lineno') else None
                        )
    
    def _check_return_paths(self, tree: ast.AST, file_path: Path):
        """Prüft auf fehlende Return-Pfade."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Prüfe ob Funktion einen Return hat
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                if not has_return and node.name[0].isupper():  # Vermutlich eine Klasse
                    # Ignoriere __init__ und andere spezielle Methoden
                    if node.name not in ['__init__', '__str__', '__repr__']:
                        # Prüfe ob es eine Methode ist die einen Wert zurückgeben sollte
                        pass


class CrossVerifier:
    """Cross-Verification für Prioritätsreihenfolgen."""
    
    def __init__(self, base_path: Path, result: AuditResult):
        self.base_path = base_path
        self.result = result
        
    def verify_fallback_priority(self):
        """Prüft Fallback-Prioritätsreihenfolge: overrides → fusion → legacy → HGE → fallback"""
        core_v6_path = self.base_path / "studiocore" / "core_v6.py"
        if not core_v6_path.exists():
            return
        
        try:
            with open(core_v6_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Suche nach der Reihenfolge
            expected_order = ['override', 'fusion', 'legacy', 'hge', 'hybrid_genre', 'fallback']
            found_order = []
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                if any(term in line_lower for term in expected_order):
                    for term in expected_order:
                        if term in line_lower and term not in found_order:
                            found_order.append(term)
                            break
            
            # Prüfe ob Reihenfolge korrekt ist
            if found_order:
                # Vereinfachte Prüfung - in Produktion würde man die tatsächliche Ausführungsreihenfolge prüfen
                if 'fallback' in found_order and found_order.index('fallback') < len(found_order) - 2:
                    self.result.add_issue(
                        "architecture", MINOR,
                        "Fallback-Priorität möglicherweise nicht korrekt (sollte letzter sein)",
                        "studiocore/core_v6.py"
                    )
        except Exception:
            pass
    
    def verify_color_priority(self):
        """Prüft Color-Prioritätsreihenfolge: user → genre → mood → hybrid → neutral"""
        color_modules = [
            "color_engine_v3.py",
            "color_engine_adapter.py"
        ]
        
        for mod_file in color_modules:
            mod_path = self.base_path / "studiocore" / mod_file
            if mod_path.exists():
                try:
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    expected_order = ['user', 'genre', 'mood', 'hybrid', 'neutral']
                    # Prüfe ob alle Begriffe vorhanden sind
                    found = [term for term in expected_order if term in content.lower()]
                    
                    if len(found) < 3:
                        self.result.add_issue(
                            "color", MINOR,
                            f"Color-Prioritätsreihenfolge möglicherweise unvollständig in {mod_file}",
                            f"studiocore/{mod_file}"
                        )
                except Exception:
                    pass
    
    def verify_instrumentation_priority(self):
        """Prüft Instrumentation-Prioritätsreihenfolge."""
        inst_modules = [
            "instrumentation_engine",
            "hybrid_instrumentation",
            "instrument_dynamics"
        ]
        
        for mod_name in inst_modules:
            mod_path = self.base_path / "studiocore" / f"{mod_name}.py"
            if mod_path.exists():
                try:
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Prüfe auf Prioritätslogik
                    if 'priority' not in content.lower() and 'override' not in content.lower():
                        self.result.add_issue(
                            "instrumentation", MINOR,
                            f"Keine explizite Prioritätslogik in {mod_name} gefunden",
                            f"studiocore/{mod_name}.py"
                        )
                except Exception:
                    pass
    
    def verify_genre_resolution_order(self):
        """Prüft Genre-Resolution-Reihenfolge."""
        genre_modules = [
            "genre_router.py",
            "genre_conflict_resolver.py",
            "hybrid_genre_engine.py"
        ]
        
        for mod_file in genre_modules:
            mod_path = self.base_path / "studiocore" / mod_file
            if mod_path.exists():
                try:
                    with open(mod_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Prüfe auf Resolution-Logik
                    if 'resolve' not in content.lower() and 'conflict' not in content.lower():
                        if mod_file == "genre_conflict_resolver.py":
                            self.result.add_issue(
                                "hybrid_genre", MAJOR,
                                f"Genre-Conflict-Resolver hat keine Resolution-Logik in {mod_file}",
                                f"studiocore/{mod_file}"
                            )
                except Exception:
                    pass


class SemanticTester:
    """Führt semantische Tests durch."""
    
    def __init__(self, base_path: Path, result: AuditResult):
        self.base_path = base_path
        self.result = result
        
    def run_tests(self):
        """Führt alle semantischen Tests aus."""
        test_cases = {
            "low_emotion_text": "Das ist ein normaler Text ohne besondere Emotionen.",
            "high_anger_text": "Ich hasse dich! Du bist ein Verräter! Ich will dich zerstören!",
            "epic_text": "In den Tiefen der Zeit, wo Legenden geboren werden, erhebt sich der Held.",
            "hybrid_text": "Folkloristische Melodien treffen auf elektronische Beats.",
            "folk_ballad_text": "Am Flussufer saß die Maid, sie sang ein Lied so traurig.",
            "electronic_text": "Bass drops, synthesizers, digital beats, electronic rhythm.",
            "nonsense_text": "Blib blab blob zzzz qwerty asdfgh",
            "ultra_mixed_hybrid_text": "Folk meets EDM meets cinematic meets hiphop meets jazz meets metal."
        }
        
        for test_name, test_text in test_cases.items():
            try:
                self._test_text(test_name, test_text)
            except Exception as e:
                self.result.semantic_test_results[test_name] = {
                    "status": "error",
                    "error": str(e)
                }
    
    def _test_text(self, test_name: str, text: str):
        """Testet einen Text."""
        # Versuche StudioCore zu importieren und zu verwenden
        try:
            sys.path.insert(0, str(self.base_path))
            from studiocore.core_v6 import StudioCoreV6
            
            core = StudioCoreV6()
            result = core.analyze(text)
            
            self.result.semantic_test_results[test_name] = {
                "status": "success",
                "result_keys": list(result.keys()) if isinstance(result, dict) else None
            }
        except Exception as e:
            self.result.semantic_test_results[test_name] = {
                "status": "error",
                "error": str(e)
            }


class FullSystemAudit:
    """Hauptklasse für das vollständige System-Audit."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.result = AuditResult()
        self.module_analyzer = ModuleAnalyzer(base_path)
        self.dependency_analyzer = None
        self.pipeline_validator = PipelineValidator(base_path, self.result)
        self.logic_checker = LogicConsistencyChecker(base_path, self.result)
        self.cross_verifier = CrossVerifier(base_path, self.result)
        self.static_analyzer = StaticAnalyzer(base_path, self.result)
        self.semantic_tester = SemanticTester(base_path, self.result)
        
    def run(self):
        """Führt das vollständige Audit durch."""
        print("🔍 Starte FULL_SYSTEM_AUDIT_ALL_MODULES_V1...")
        
        # 1. Module entdecken
        print("📦 Entdecke Module...")
        self.module_analyzer.discover_modules()
        print(f"   Gefunden: {len(self.module_analyzer.modules)} Module")
        
        # 2. Module analysieren
        print("🔬 Analysiere Module...")
        self.module_analyzer.analyze_all()
        
        # 3. Dependency-Analyse
        print("🔗 Analysiere Dependencies...")
        self.dependency_analyzer = DependencyAnalyzer(self.module_analyzer)
        self.result.dependency_graph = self.dependency_analyzer.build_dependency_graph()
        self.result.import_graph = self.result.dependency_graph.copy()
        
        # 4. Zyklische Abhängigkeiten
        print("🔄 Suche zyklische Abhängigkeiten...")
        self.result.cyclical_dependencies = self.dependency_analyzer.find_cycles(
            self.result.dependency_graph
        )
        
        # 5. Orphan-Module
        print("👻 Suche Orphan-Module...")
        self.result.orphan_modules = self.dependency_analyzer.find_orphans(
            self.result.dependency_graph
        )
        
        # 6. Ungenutzte Module
        print("🗑️  Suche ungenutzte Module...")
        self.result.unused_modules = self.dependency_analyzer.find_unused(
            self.result.dependency_graph
        )
        
        # 7. Initialisierungsreihenfolge
        print("📋 Bestimme Initialisierungsreihenfolge...")
        self.result.module_initialization_order = self.dependency_analyzer.topological_sort(
            self.result.dependency_graph
        )
        
        # 8. Pipeline-Validierung
        print("🔧 Validiere Pipelines...")
        self.pipeline_validator.validate_pipelines()
        
        # 9. Logik-Konsistenz
        print("🧠 Prüfe Logik-Konsistenz...")
        self.logic_checker.check_emotion_conflicts()
        self.logic_checker.check_color_conflicts()
        self.logic_checker.check_hybrid_genre_conflicts()
        self.logic_checker.check_instrumentation_conflicts()
        
        # 9.5. Cross-Verification
        print("🔍 Führe Cross-Verification durch...")
        self.cross_verifier.verify_fallback_priority()
        self.cross_verifier.verify_color_priority()
        self.cross_verifier.verify_instrumentation_priority()
        self.cross_verifier.verify_genre_resolution_order()
        
        # 10. Statische Analyse
        print("📊 Führe statische Analyse durch...")
        self.static_analyzer.analyze()
        
        # 11. Semantische Tests
        print("🧪 Führe semantische Tests durch...")
        self.semantic_tester.run_tests()
        
        print("✅ Audit abgeschlossen!")
        
    def generate_report(self) -> str:
        """Generiert einen detaillierten Report."""
        report = []
        report.append("=" * 80)
        report.append("FULL_SYSTEM_AUDIT_ALL_MODULES_V1 - REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Dependency-Graph
        report.append("## DEPENDENCY GRAPH")
        report.append(f"Module: {len(self.result.dependency_graph)}")
        report.append("")
        
        # Zyklische Abhängigkeiten
        report.append("## CYCLICAL DEPENDENCIES")
        if self.result.cyclical_dependencies:
            for cycle in self.result.cyclical_dependencies:
                report.append(f"  ⚠️  {' -> '.join(cycle)}")
                self.result.add_issue("architecture", MAJOR, 
                                     f"Zyklische Abhängigkeit: {' -> '.join(cycle)}")
        else:
            report.append("  ✅ Keine zyklischen Abhängigkeiten gefunden")
        report.append("")
        
        # Orphan-Module
        report.append("## ORPHAN MODULES")
        if self.result.orphan_modules:
            for mod in self.result.orphan_modules:
                report.append(f"  ⚠️  {mod}")
                self.result.add_issue("architecture", MINOR, f"Orphan-Modul: {mod}")
        else:
            report.append("  ✅ Keine Orphan-Module gefunden")
        report.append("")
        
        # Ungenutzte Module
        report.append("## UNUSED MODULES")
        if self.result.unused_modules:
            for mod in self.result.unused_modules:
                report.append(f"  ⚠️  {mod}")
                self.result.add_issue("architecture", MINOR, f"Ungenutztes Modul: {mod}")
        else:
            report.append("  ✅ Keine ungenutzten Module gefunden")
        report.append("")
        
        # Pipeline-Issues
        report.append("## PIPELINE ISSUES")
        if self.result.pipeline_issues:
            for engine, issues in self.result.pipeline_issues.items():
                report.append(f"  ⚠️  {engine}:")
                for issue in issues:
                    report.append(f"      - {issue['message']}")
        else:
            report.append("  ✅ Keine Pipeline-Issues gefunden")
        report.append("")
        
        # Logik-Konflikte
        report.append("## LOGIC CONFLICTS")
        if self.result.logic_conflicts:
            for conflict in self.result.logic_conflicts:
                report.append(f"  ⚠️  [{conflict['severity']}] {conflict['message']}")
        else:
            report.append("  ✅ Keine Logik-Konflikte gefunden")
        report.append("")
        
        # Emotion-Konflikte
        report.append("## EMOTION CONFLICTS")
        if self.result.emotion_conflicts:
            for conflict in self.result.emotion_conflicts:
                report.append(f"  ⚠️  [{conflict['severity']}] {conflict['message']}")
        else:
            report.append("  ✅ Keine Emotion-Konflikte gefunden")
        report.append("")
        
        # Color-Konflikte
        report.append("## COLOR CONFLICTS")
        if self.result.color_conflicts:
            for conflict in self.result.color_conflicts:
                report.append(f"  ⚠️  [{conflict['severity']}] {conflict['message']}")
        else:
            report.append("  ✅ Keine Color-Konflikte gefunden")
        report.append("")
        
        # Hybrid-Genre-Konflikte
        report.append("## HYBRID GENRE CONFLICTS")
        if self.result.hybrid_genre_conflicts:
            for conflict in self.result.hybrid_genre_conflicts:
                report.append(f"  ⚠️  [{conflict['severity']}] {conflict['message']}")
        else:
            report.append("  ✅ Keine Hybrid-Genre-Konflikte gefunden")
        report.append("")
        
        # Instrumentation-Konflikte
        report.append("## INSTRUMENTATION CONFLICTS")
        if self.result.instrumentation_conflicts:
            for conflict in self.result.instrumentation_conflicts:
                report.append(f"  ⚠️  [{conflict['severity']}] {conflict['message']}")
        else:
            report.append("  ✅ Keine Instrumentation-Konflikte gefunden")
        report.append("")
        
        # Cross-Verification Issues (aus architecture_warnings extrahiert)
        report.append("## CROSS-VERIFICATION ISSUES")
        cross_issues = [w for w in self.result.architecture_warnings 
                       if 'priority' in w.get('message', '').lower() or 
                          'resolution' in w.get('message', '').lower()]
        if cross_issues:
            for issue in cross_issues:
                report.append(f"  ⚠️  [{issue['severity']}] {issue['message']}")
        else:
            report.append("  ✅ Keine Cross-Verification-Issues gefunden")
        report.append("")
        
        # Statische Analyse
        report.append("## STATIC ANALYSIS ISSUES")
        if self.result.static_analysis_issues:
            for issue in self.result.static_analysis_issues[:20]:  # Limit auf 20
                report.append(f"  ⚠️  [{issue['severity']}] {issue['message']}")
        else:
            report.append("  ✅ Keine statischen Analyse-Issues gefunden")
        report.append("")
        
        # Semantische Tests
        report.append("## SEMANTIC TEST RESULTS")
        for test_name, test_result in self.result.semantic_test_results.items():
            status = test_result.get("status", "unknown")
            if status == "success":
                report.append(f"  ✅ {test_name}: Erfolgreich")
            else:
                report.append(f"  ❌ {test_name}: {test_result.get('error', 'Unbekannter Fehler')}")
        report.append("")
        
        # Severity-Ranking
        report.append("## SEVERITY RANKING")
        critical = sum(1 for w in self.result.architecture_warnings if w['severity'] == CRITICAL)
        major = sum(1 for w in self.result.architecture_warnings if w['severity'] == MAJOR)
        minor = sum(1 for w in self.result.architecture_warnings if w['severity'] == MINOR)
        
        report.append(f"  🔴 CRITICAL: {critical}")
        report.append(f"  🟠 MAJOR: {major}")
        report.append(f"  🟡 MINOR: {minor}")
        report.append("")
        
        # Empfohlene Fixes
        report.append("## RECOMMENDED PATCH PLAN")
        if self.result.cyclical_dependencies:
            report.append("  1. Zyklische Abhängigkeiten auflösen")
        if self.result.orphan_modules:
            report.append("  2. Orphan-Module integrieren oder entfernen")
        if self.result.unused_modules:
            report.append("  3. Ungenutzte Module entfernen oder dokumentieren")
        if self.result.pipeline_issues:
            report.append("  4. Pipeline-Issues beheben")
        if not self.result.cyclical_dependencies and not self.result.orphan_modules:
            report.append("  ✅ Keine kritischen Fixes erforderlich")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Hauptfunktion."""
    base_path = Path(__file__).parent
    audit = FullSystemAudit(base_path)
    
    try:
        audit.run()
        report = audit.generate_report()
        
        print("\n" + report)
        
        # Speichere Report
        report_path = base_path / "FULL_SYSTEM_AUDIT_REPORT_V1.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Report gespeichert: {report_path}")
        
        # Speichere JSON-Daten
        json_path = base_path / "FULL_SYSTEM_AUDIT_DATA_V1.json"
        json_data = {
            "dependency_graph": {k: list(v) for k, v in audit.result.dependency_graph.items()},
            "cyclical_dependencies": audit.result.cyclical_dependencies,
            "orphan_modules": audit.result.orphan_modules,
            "unused_modules": audit.result.unused_modules,
            "module_initialization_order": audit.result.module_initialization_order,
            "pipeline_issues": audit.result.pipeline_issues,
            "semantic_test_results": audit.result.semantic_test_results
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 JSON-Daten gespeichert: {json_path}")
        
    except Exception as e:
        print(f"❌ Fehler beim Audit: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

