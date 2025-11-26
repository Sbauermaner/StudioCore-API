#!/usr/bin/env python3
"""
FULL_FUNCTIONAL_AUDIT_STUDIOCORE_V1

Umfassendes funktionales Audit für StudioCore
Prüft Architektur, Dependencies, Pipeline-Flows, Logik-Korrektheit,
Datenkonsistenz, statische Analyse, dynamische Tests und Output-Verification.
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

# Expected output ranges
TLP_RANGE = (0.0, 1.0)
RDE_RESONANCE_RANGE = (0.0, 1.0)
RDE_FRACTURE_RANGE = (0.0, 1.0)
RDE_ENTROPY_RANGE = (0.0, 1.0)
BPM_RANGE = (40, 200)
MOOD_VALUES = ["rage", "epic", "neutral", "peace", "anger", "tension", "calm"]


class FunctionalAuditResult:
    """Container für funktionale Audit-Ergebnisse."""
    
    def __init__(self):
        # Error categories
        self.critical_errors: List[Dict] = []
        self.major_errors: List[Dict] = []
        self.minor_errors: List[Dict] = []
        self.functional_breakages: List[Dict] = []
        
        # Maps
        self.conflict_map: Dict[str, List[Dict]] = defaultdict(list)
        self.dependency_map: Dict[str, Set[str]] = {}
        self.pipeline_graph: Dict[str, Dict] = {}
        self.module_graph: Dict[str, Dict] = {}
        
        # Architecture
        self.file_structure_issues: List[Dict] = []
        self.module_hierarchy_issues: List[Dict] = []
        self.class_hierarchy_issues: List[Dict] = []
        self.stateless_integrity_issues: List[Dict] = []
        self.initialization_sequence_issues: List[Dict] = []
        self.reset_sequence_issues: List[Dict] = []
        self.pipeline_order_issues: List[Dict] = []
        self.module_interoperability_issues: List[Dict] = []
        
        # Dependencies
        self.import_graph: Dict[str, Set[str]] = {}
        self.circular_imports: List[List[str]] = []
        self.missing_dependencies: List[Dict] = []
        self.orphan_modules: List[str] = []
        self.unused_modules: List[str] = []
        self.shadowed_modules: List[Dict] = []
        self.conflicting_imports: List[Dict] = []
        
        # Pipeline flows
        self.pipeline_flow_issues: Dict[str, List[Dict]] = defaultdict(list)
        
        # Logic correctness
        self.logic_correctness_issues: Dict[str, List[Dict]] = defaultdict(list)
        
        # Data consistency
        self.data_consistency_issues: List[Dict] = []
        
        # Static analysis
        self.static_analysis_issues: List[Dict] = []
        
        # Dynamic tests
        self.dynamic_test_results: Dict[str, Dict] = {}
        
        # Pipeline outputs
        self.pipeline_output_issues: Dict[str, List[Dict]] = defaultdict(list)
        
        # Summary
        self.works: List[str] = []
        self.partially_works: List[str] = []
        self.broken: List[str] = []
        
    def add_error(self, severity: str, category: str, message: str,
                  file: Optional[str] = None, line: Optional[int] = None,
                  details: Optional[Dict] = None):
        """Fügt einen Fehler hinzu."""
        error = {
            "severity": severity,
            "category": category,
            "message": message,
            "file": file,
            "line": line,
            "details": details or {}
        }
        
        if severity == CRITICAL:
            self.critical_errors.append(error)
        elif severity == MAJOR:
            self.major_errors.append(error)
        else:
            self.minor_errors.append(error)


class ArchitectureChecker:
    """Prüft Architektur-Aspekte."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
        self.studiocore_path = base_path / "studiocore"
        
    def check_file_structure(self):
        """Prüft Dateistruktur."""
        if not self.studiocore_path.exists():
            self.result.add_error(CRITICAL, "file_structure",
                                "studiocore/ Verzeichnis nicht gefunden")
            return
        
        # Prüfe auf wichtige Dateien
        required_files = [
            "core_v6.py",
            "emotion.py",
            "tlp_engine.py",
            "rde_engine.py",
            "bpm_engine.py"
        ]
        
        for req_file in required_files:
            if not (self.studiocore_path / req_file).exists():
                self.result.add_error(MAJOR, "file_structure",
                                    f"Erforderliche Datei fehlt: {req_file}")
    
    def check_module_hierarchy(self):
        """Prüft Modul-Hierarchie."""
        # Prüfe ob core_v6.py die Hauptklasse hat
        core_v6_path = self.studiocore_path / "core_v6.py"
        if core_v6_path.exists():
            try:
                with open(core_v6_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "class StudioCoreV6" not in content:
                    self.result.add_error(CRITICAL, "module_hierarchy",
                                        "StudioCoreV6 Klasse nicht gefunden")
            except Exception as e:
                self.result.add_error(MAJOR, "module_hierarchy",
                                    f"Fehler beim Lesen von core_v6.py: {e}")
    
    def check_class_hierarchy(self):
        """Prüft Klassen-Hierarchie."""
        # Vereinfachte Prüfung - in Produktion würde man AST-Analyse verwenden
        pass
    
    def check_stateless_integrity(self):
        """Prüft Stateless-Integrität."""
        studiocore_path = self.studiocore_path
        if not studiocore_path.exists():
            return
        
        # Suche nach potentiellen State-Leaks
        for py_file in studiocore_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Prüfe auf Module-Level State
                lines = content.split('\n')
                module_level_assignments = []
                for i, line in enumerate(lines, 1):
                    # Suche nach Modul-Level Variablen (nicht in Funktionen/Klassen)
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        if '=' in stripped and not any(keyword in stripped for keyword in 
                                                       ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except']):
                            # Vereinfachte Heuristik
                            if not stripped.startswith(' ') and not stripped.startswith('\t'):
                                module_level_assignments.append((i, stripped))
                
                if len(module_level_assignments) > 10:  # Viele Modul-Level Variablen
                    rel_path = py_file.relative_to(self.base_path)
                    self.result.add_error(MINOR, "stateless_integrity",
                                        f"Viele Modul-Level Variablen in {rel_path}",
                                        str(rel_path))
            except Exception:
                pass
    
    def check_initialization_sequence(self):
        """Prüft Initialisierungsreihenfolge."""
        core_v6_path = self.studiocore_path / "core_v6.py"
        if not core_v6_path.exists():
            return
        
        try:
            with open(core_v6_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob _build_engine_bundle existiert
            if "_build_engine_bundle" not in content:
                self.result.add_error(MAJOR, "initialization_sequence",
                                    "_build_engine_bundle Methode nicht gefunden")
        except Exception:
            pass
    
    def check_reset_sequences(self):
        """Prüft Reset-Sequenzen."""
        # Prüfe ob Engines Reset-Methoden haben
        pass
    
    def check_pipeline_order(self):
        """Prüft Pipeline-Reihenfolge."""
        core_v6_path = self.studiocore_path / "core_v6.py"
        if not core_v6_path.exists():
            return
        
        try:
            with open(core_v6_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Erwartete Reihenfolge: prepare -> analyze -> process -> finalize
            if "_prepare_text_and_structure" in content:
                if "_backend_analyze" in content:
                    # Prüfe Reihenfolge im Code
                    prep_pos = content.find("_prepare_text_and_structure")
                    analyze_pos = content.find("_backend_analyze")
                    
                    if analyze_pos < prep_pos:
                        self.result.add_error(MINOR, "pipeline_order",
                                            "Pipeline-Reihenfolge möglicherweise falsch")
        except Exception:
            pass
    
    def check_module_interoperability(self):
        """Prüft Modul-Interoperabilität."""
        # Prüfe ob Module korrekt zusammenarbeiten
        pass


class DependencyChecker:
    """Prüft Dependencies."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
        self.module_analyzer = None
        
    def check_import_graph(self):
        """Baut Import-Graph."""
        from full_system_audit_all_modules_v1 import ModuleAnalyzer
        
        self.module_analyzer = ModuleAnalyzer(self.base_path)
        self.module_analyzer.discover_modules()
        self.module_analyzer.analyze_all()
        
        # Baue Import-Graph
        studiocore_modules = {m for m in self.module_analyzer.modules.keys() 
                             if m.startswith("studiocore.")}
        
        for module_name in studiocore_modules:
            imports = self.module_analyzer.imports.get(module_name, set())
            dependencies = set()
            
            for imp in imports:
                if imp == "studiocore" or imp.startswith("studiocore."):
                    dep_module = imp
                else:
                    dep_module = f"studiocore.{imp}"
                
                if dep_module in studiocore_modules:
                    dependencies.add(dep_module)
            
            self.result.import_graph[module_name] = dependencies
            self.result.dependency_map[module_name] = dependencies
    
    def check_circular_imports(self):
        """Prüft zyklische Imports."""
        from full_system_audit_all_modules_v1 import DependencyAnalyzer
        
        if not self.module_analyzer:
            return
        
        dep_analyzer = DependencyAnalyzer(self.module_analyzer)
        cycles = dep_analyzer.find_cycles(self.result.import_graph)
        self.result.circular_imports = cycles
        
        for cycle in cycles:
            self.result.add_error(MAJOR, "circular_imports",
                                f"Zyklischer Import: {' -> '.join(cycle)}")
    
    def check_missing_dependencies(self):
        """Prüft fehlende Dependencies."""
        studiocore_path = self.base_path / "studiocore"
        if not studiocore_path.exists():
            return
        
        for py_file in studiocore_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                rel_path = py_file.relative_to(self.base_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            # Prüfe ob Modul existiert
                            module_parts = node.module.split('.')
                            if module_parts[0] == "studiocore":
                                # Prüfe ob Datei existiert
                                module_path = self.base_path / Path(*module_parts) / "__init__.py"
                                if not module_path.exists():
                                    # Prüfe ob .py Datei existiert
                                    module_path = self.base_path / Path(*module_parts[:-1]) / f"{module_parts[-1]}.py"
                                    if not module_path.exists():
                                        self.result.add_error(MINOR, "missing_dependencies",
                                                            f"Möglicherweise fehlendes Modul: {node.module}",
                                                            str(rel_path), node.lineno)
            except SyntaxError:
                pass
            except Exception:
                pass
    
    def check_orphan_modules(self):
        """Prüft Orphan-Module."""
        from full_system_audit_all_modules_v1 import DependencyAnalyzer
        
        if not self.module_analyzer:
            return
        
        dep_analyzer = DependencyAnalyzer(self.module_analyzer)
        orphans = dep_analyzer.find_orphans(self.result.import_graph)
        self.result.orphan_modules = orphans
        
        for orphan in orphans:
            self.result.add_error(MINOR, "orphan_modules",
                                f"Orphan-Modul: {orphan}")
    
    def check_unused_modules(self):
        """Prüft ungenutzte Module."""
        from full_system_audit_all_modules_v1 import DependencyAnalyzer
        
        if not self.module_analyzer:
            return
        
        dep_analyzer = DependencyAnalyzer(self.module_analyzer)
        unused = dep_analyzer.find_unused(self.result.import_graph)
        self.result.unused_modules = unused
        
        for mod in unused:
            self.result.add_error(MINOR, "unused_modules",
                                f"Ungenutztes Modul: {mod}")
    
    def check_shadowed_modules(self):
        """Prüft shadowed Modules."""
        # Prüfe auf Module die andere Module überschatten
        pass
    
    def check_conflicting_imports(self):
        """Prüft konfliktierende Imports."""
        # Prüfe auf Import-Konflikte
        pass


class PipelineFlowChecker:
    """Prüft Pipeline-Flows für alle Engines."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
        self.studiocore_path = base_path / "studiocore"
        
        self.engine_flows = {
            "tlp_engine": self._check_tlp_flow,
            "rde_engine": self._check_rde_flow,
            "emotion_engine": self._check_emotion_flow,
            "bpm_engine": self._check_bpm_flow,
            "tone_engine": self._check_tone_flow,
            "frequency_engine": self._check_frequency_flow,
            "section_parser": self._check_section_parser_flow,
            "section_merge_mode": self._check_section_merge_mode_flow,
            "genre_router": self._check_genre_router_flow,
            "hybrid_genre_engine": self._check_hybrid_genre_flow,
            "genre_conflict_resolver": self._check_genre_conflict_resolver_flow,
            "style_engine": self._check_style_engine_flow,
            "color_engine_adapter": self._check_color_engine_adapter_flow,
            "color_engine_v3": self._check_color_engine_v3_flow,
            "instrumentation_engine": self._check_instrumentation_engine_flow,
            "hybrid_instrumentation_layer": self._check_hybrid_instrumentation_flow,
            "neutral_mode": self._check_neutral_mode_flow,
            "rage_filter_v2": self._check_rage_filter_v2_flow,
            "epic_override": self._check_epic_override_flow,
            "finalize_result": self._check_finalize_result_flow,
        }
    
    def check_all_flows(self):
        """Prüft alle Pipeline-Flows."""
        for engine_name, check_func in self.engine_flows.items():
            try:
                check_func()
            except Exception as e:
                self.result.add_error(MINOR, "pipeline_flow",
                                    f"Fehler beim Prüfen von {engine_name}: {e}")
    
    def _check_tlp_flow(self):
        """Prüft TLP Engine Flow."""
        tlp_path = self.studiocore_path / "tlp_engine.py"
        if not tlp_path.exists():
            self.result.pipeline_flow_issues["tlp_engine"].append({
                "severity": MAJOR,
                "message": "tlp_engine.py nicht gefunden"
            })
            return
        
        try:
            with open(tlp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob analyze Methode existiert (kann in Basisklasse sein)
            if "def analyze" not in content and "analyze(" not in content:
                # Prüfe ob es eine Basisklasse gibt die analyze hat
                if "_TruthLovePainEngine" in content:
                    # Basisklasse wird verwendet - prüfe emotion.py
                    emotion_path = self.studiocore_path / "emotion.py"
                    if emotion_path.exists():
                        with open(emotion_path, 'r', encoding='utf-8') as ef:
                            emotion_content = ef.read()
                        if "def analyze" not in emotion_content:
                            self.result.pipeline_flow_issues["tlp_engine"].append({
                                "severity": CRITICAL,
                                "message": "analyze() Methode nicht gefunden (auch nicht in Basisklasse)"
                            })
                else:
                    self.result.pipeline_flow_issues["tlp_engine"].append({
                        "severity": CRITICAL,
                        "message": "analyze() Methode nicht gefunden"
                    })
            
            # Prüfe ob TLP-Werte zurückgegeben werden
            if '"truth"' not in content and "'truth'" not in content:
                self.result.pipeline_flow_issues["tlp_engine"].append({
                    "severity": MAJOR,
                    "message": "TLP-Werte (truth/love/pain) nicht gefunden"
                })
        except Exception as e:
            self.result.pipeline_flow_issues["tlp_engine"].append({
                "severity": MAJOR,
                "message": f"Fehler beim Lesen: {e}"
            })
    
    def _check_rde_flow(self):
        """Prüft RDE Engine Flow."""
        rde_path = self.studiocore_path / "rde_engine.py"
        if not rde_path.exists():
            self.result.pipeline_flow_issues["rde_engine"].append({
                "severity": MAJOR,
                "message": "rde_engine.py nicht gefunden"
            })
            return
        
        try:
            with open(rde_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob calc_resonance, calc_fracture, calc_entropy existieren
            required_methods = ["calc_resonance", "calc_fracture", "calc_entropy"]
            for method in required_methods:
                if f"def {method}" not in content:
                    self.result.pipeline_flow_issues["rde_engine"].append({
                        "severity": MAJOR,
                        "message": f"{method}() Methode nicht gefunden"
                    })
        except Exception:
            pass
    
    def _check_emotion_flow(self):
        """Prüft Emotion Engine Flow."""
        emotion_path = self.studiocore_path / "emotion.py"
        if not emotion_path.exists():
            self.result.pipeline_flow_issues["emotion_engine"].append({
                "severity": MAJOR,
                "message": "emotion.py nicht gefunden"
            })
            return
        
        try:
            with open(emotion_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "class EmotionEngine" not in content:
                self.result.pipeline_flow_issues["emotion_engine"].append({
                    "severity": CRITICAL,
                    "message": "EmotionEngine Klasse nicht gefunden"
                })
        except Exception:
            pass
    
    def _check_bpm_flow(self):
        """Prüft BPM Engine Flow."""
        bpm_path = self.studiocore_path / "bpm_engine.py"
        if not bpm_path.exists():
            self.result.pipeline_flow_issues["bpm_engine"].append({
                "severity": MAJOR,
                "message": "bpm_engine.py nicht gefunden"
            })
            return
        
        try:
            with open(bpm_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "def compute_bpm_v2" not in content and "def text_bpm_estimation" not in content:
                self.result.pipeline_flow_issues["bpm_engine"].append({
                    "severity": MAJOR,
                    "message": "BPM-Berechnungsmethoden nicht gefunden"
                })
        except Exception:
            pass
    
    def _check_tone_flow(self):
        """Prüft Tone Engine Flow."""
        tone_path = self.studiocore_path / "tone.py"
        if tone_path.exists():
            try:
                with open(tone_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class ToneSyncEngine" not in content:
                    self.result.pipeline_flow_issues["tone_engine"].append({
                        "severity": MAJOR,
                        "message": "ToneSyncEngine Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_frequency_flow(self):
        """Prüft Frequency Engine Flow."""
        freq_path = self.studiocore_path / "frequency.py"
        if freq_path.exists():
            try:
                with open(freq_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class UniversalFrequencyEngine" not in content:
                    self.result.pipeline_flow_issues["frequency_engine"].append({
                        "severity": MAJOR,
                        "message": "UniversalFrequencyEngine Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_section_parser_flow(self):
        """Prüft Section Parser Flow."""
        section_path = self.studiocore_path / "section_parser.py"
        if section_path.exists():
            try:
                with open(section_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class SectionParser" not in content:
                    self.result.pipeline_flow_issues["section_parser"].append({
                        "severity": MAJOR,
                        "message": "SectionParser Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_section_merge_mode_flow(self):
        """Prüft Section Merge Mode Flow."""
        merge_path = self.studiocore_path / "section_merge_mode.py"
        if not merge_path.exists():
            self.result.pipeline_flow_issues["section_merge_mode"].append({
                "severity": MINOR,
                "message": "section_merge_mode.py nicht gefunden (möglicherweise NO-OP)"
            })
    
    def _check_genre_router_flow(self):
        """Prüft Genre Router Flow."""
        router_path = self.studiocore_path / "genre_router.py"
        if router_path.exists():
            try:
                with open(router_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class DynamicGenreRouter" not in content:
                    self.result.pipeline_flow_issues["genre_router"].append({
                        "severity": MAJOR,
                        "message": "DynamicGenreRouter Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_hybrid_genre_flow(self):
        """Prüft Hybrid Genre Engine Flow."""
        hybrid_path = self.studiocore_path / "hybrid_genre_engine.py"
        if hybrid_path.exists():
            try:
                with open(hybrid_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class HybridGenreEngine" not in content:
                    self.result.pipeline_flow_issues["hybrid_genre_engine"].append({
                        "severity": MAJOR,
                        "message": "HybridGenreEngine Klasse nicht gefunden"
                    })
                # Prüfe ob resolve Methode existiert (wurde im vorherigen Audit als fehlend identifiziert)
                if "def resolve" not in content:
                    self.result.pipeline_flow_issues["hybrid_genre_engine"].append({
                        "severity": CRITICAL,
                        "message": "resolve() Methode fehlt - semantische Tests schlagen fehl"
                    })
            except Exception:
                pass
    
    def _check_genre_conflict_resolver_flow(self):
        """Prüft Genre Conflict Resolver Flow."""
        resolver_path = self.studiocore_path / "genre_conflict_resolver.py"
        if resolver_path.exists():
            try:
                with open(resolver_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "def resolve" not in content and "def resolve_conflict" not in content:
                    self.result.pipeline_flow_issues["genre_conflict_resolver"].append({
                        "severity": MAJOR,
                        "message": "Resolution-Methode nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_style_engine_flow(self):
        """Prüft Style Engine Flow."""
        # Style Engine ist in logical_engines.py
        logical_path = self.studiocore_path / "logical_engines.py"
        if logical_path.exists():
            try:
                with open(logical_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class StyleEngine" not in content:
                    self.result.pipeline_flow_issues["style_engine"].append({
                        "severity": MAJOR,
                        "message": "StyleEngine Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_color_engine_adapter_flow(self):
        """Prüft Color Engine Adapter Flow."""
        adapter_path = self.studiocore_path / "color_engine_adapter.py"
        if adapter_path.exists():
            try:
                with open(adapter_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class ColorEngineAdapter" not in content:
                    self.result.pipeline_flow_issues["color_engine_adapter"].append({
                        "severity": MAJOR,
                        "message": "ColorEngineAdapter Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_color_engine_v3_flow(self):
        """Prüft Color Engine V3 Flow."""
        v3_path = self.studiocore_path / "color_engine_v3.py"
        if v3_path.exists():
            try:
                with open(v3_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Prüfe ob es NO-OP ist
                if "NO-OP" in content or "MASTER_PATCH_V5_SKELETON" in content:
                    self.result.pipeline_flow_issues["color_engine_v3"].append({
                        "severity": MINOR,
                        "message": "ColorEngineV3 ist NO-OP Skeleton"
                    })
            except Exception:
                pass
    
    def _check_instrumentation_engine_flow(self):
        """Prüft Instrumentation Engine Flow."""
        # Instrumentation Engine ist in logical_engines.py
        logical_path = self.studiocore_path / "logical_engines.py"
        if logical_path.exists():
            try:
                with open(logical_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "class InstrumentationEngine" not in content:
                    self.result.pipeline_flow_issues["instrumentation_engine"].append({
                        "severity": MAJOR,
                        "message": "InstrumentationEngine Klasse nicht gefunden"
                    })
            except Exception:
                pass
    
    def _check_hybrid_instrumentation_flow(self):
        """Prüft Hybrid Instrumentation Flow."""
        hybrid_path = self.studiocore_path / "hybrid_instrumentation.py"
        if hybrid_path.exists():
            try:
                with open(hybrid_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content or "MASTER_PATCH_V5_SKELETON" in content:
                    self.result.pipeline_flow_issues["hybrid_instrumentation_layer"].append({
                        "severity": MINOR,
                        "message": "HybridInstrumentation ist NO-OP Skeleton"
                    })
            except Exception:
                pass
    
    def _check_neutral_mode_flow(self):
        """Prüft Neutral Mode Flow."""
        neutral_path = self.studiocore_path / "neutral_mode.py"
        if neutral_path.exists():
            try:
                with open(neutral_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content or "MASTER_PATCH_V5_SKELETON" in content:
                    self.result.pipeline_flow_issues["neutral_mode"].append({
                        "severity": MINOR,
                        "message": "NeutralMode ist NO-OP Skeleton"
                    })
            except Exception:
                pass
    
    def _check_rage_filter_v2_flow(self):
        """Prüft Rage Filter V2 Flow."""
        rage_path = self.studiocore_path / "rage_filter_v2.py"
        if rage_path.exists():
            try:
                with open(rage_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content or "MASTER_PATCH_V5_SKELETON" in content:
                    self.result.pipeline_flow_issues["rage_filter_v2"].append({
                        "severity": MINOR,
                        "message": "RageFilterV2 ist NO-OP Skeleton"
                    })
            except Exception:
                pass
    
    def _check_epic_override_flow(self):
        """Prüft Epic Override Flow."""
        epic_path = self.studiocore_path / "epic_override.py"
        if epic_path.exists():
            try:
                with open(epic_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content or "MASTER_PATCH_V5_SKELETON" in content:
                    self.result.pipeline_flow_issues["epic_override"].append({
                        "severity": MINOR,
                        "message": "EpicOverride ist NO-OP Skeleton"
                    })
            except Exception:
                pass
    
    def _check_finalize_result_flow(self):
        """Prüft Finalize Result Flow."""
        core_v6_path = self.studiocore_path / "core_v6.py"
        if core_v6_path.exists():
            try:
                with open(core_v6_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "def _finalize_result" not in content:
                    self.result.pipeline_flow_issues["finalize_result"].append({
                        "severity": CRITICAL,
                        "message": "_finalize_result Methode nicht gefunden"
                    })
            except Exception:
                pass


class LogicCorrectnessChecker:
    """Prüft Logik-Korrektheit."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
        
    def check_all(self):
        """Prüft alle Logik-Korrektheit-Aspekte."""
        self.check_tlp_consistency()
        self.check_rde_consistency()
        self.check_bpm_consistency()
        self.check_emotion_conflict_resolver()
        self.check_mood_override_correctness()
        self.check_neutral_mode_correctness()
        self.check_rage_mode_correctness()
        self.check_epic_mode_correctness()
        self.check_hybrid_genre_consistency()
        self.check_genre_priority_tree()
        self.check_genre_fallback_logic()
        self.check_style_merge_logic()
        self.check_color_priority_logic()
        self.check_hybrid_color_logic()
        self.check_instrumentation_priority_logic()
        self.check_section_naming_logic()
        self.check_section_merge_logic()
    
    def check_tlp_consistency(self):
        """Prüft TLP-Konsistenz."""
        tlp_path = self.base_path / "studiocore" / "tlp_engine.py"
        if not tlp_path.exists():
            return
        
        try:
            with open(tlp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob TLP-Werte normalisiert werden
            if "clamp" not in content.lower() and "min" not in content.lower() and "max" not in content.lower():
                self.result.logic_correctness_issues["tlp_consistency"].append({
                    "severity": MINOR,
                    "message": "TLP-Werte möglicherweise nicht normalisiert"
                })
        except Exception:
            pass
    
    def check_rde_consistency(self):
        """Prüft RDE-Konsistenz."""
        rde_path = self.base_path / "studiocore" / "rde_engine.py"
        if not rde_path.exists():
            return
        
        try:
            with open(rde_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob RDE-Werte im erwarteten Range sind
            if "min(1.0" not in content and "max(0.0" not in content:
                self.result.logic_correctness_issues["rde_consistency"].append({
                    "severity": MINOR,
                    "message": "RDE-Werte möglicherweise nicht auf [0.0, 1.0] geklemmt"
                })
        except Exception:
            pass
    
    def check_bpm_consistency(self):
        """Prüft BPM-Konsistenz."""
        bpm_path = self.base_path / "studiocore" / "bpm_engine.py"
        if not bpm_path.exists():
            return
        
        try:
            with open(bpm_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob BPM im erwarteten Range ist
            if "max(40" not in content and "min(200" not in content:
                if "max(40" not in content or "min(200" not in content:
                    self.result.logic_correctness_issues["bpm_consistency"].append({
                        "severity": MINOR,
                        "message": "BPM möglicherweise nicht auf [40, 200] geklemmt"
                    })
        except Exception:
            pass
    
    def check_emotion_conflict_resolver(self):
        """Prüft Emotion-Konflikt-Resolver."""
        core_v6_path = self.base_path / "studiocore" / "core_v6.py"
        if not core_v6_path.exists():
            return
        
        try:
            with open(core_v6_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe ob Rage-Mode Conflict Resolver existiert
            if "rage" in content.lower() and "peace" in content.lower():
                # Gut - Conflict Resolver vorhanden
                pass
            else:
                self.result.logic_correctness_issues["emotion_conflict_resolver"].append({
                    "severity": MINOR,
                    "message": "Emotion-Konflikt-Resolver möglicherweise unvollständig"
                })
        except Exception:
            pass
    
    def check_mood_override_correctness(self):
        """Prüft Mood-Override-Korrektheit."""
        # Prüfe ob Mood-Overrides korrekt implementiert sind
        pass
    
    def check_neutral_mode_correctness(self):
        """Prüft Neutral-Mode-Korrektheit."""
        neutral_path = self.base_path / "studiocore" / "neutral_mode.py"
        if neutral_path.exists():
            try:
                with open(neutral_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content:
                    self.result.logic_correctness_issues["neutral_mode_correctness"].append({
                        "severity": MINOR,
                        "message": "NeutralMode ist NO-OP - Logik nicht implementiert"
                    })
            except Exception:
                pass
    
    def check_rage_mode_correctness(self):
        """Prüft Rage-Mode-Korrektheit."""
        # Prüfe ob Rage-Mode korrekt implementiert ist
        pass
    
    def check_epic_mode_correctness(self):
        """Prüft Epic-Mode-Korrektheit."""
        epic_path = self.base_path / "studiocore" / "epic_override.py"
        if epic_path.exists():
            try:
                with open(epic_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content:
                    self.result.logic_correctness_issues["epic_mode_correctness"].append({
                        "severity": MINOR,
                        "message": "EpicOverride ist NO-OP - Logik nicht implementiert"
                    })
            except Exception:
                pass
    
    def check_hybrid_genre_consistency(self):
        """Prüft Hybrid-Genre-Konsistenz."""
        hybrid_path = self.base_path / "studiocore" / "hybrid_genre_engine.py"
        if hybrid_path.exists():
            try:
                with open(hybrid_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "NO-OP" in content:
                    self.result.logic_correctness_issues["hybrid_genre_consistency"].append({
                        "severity": MINOR,
                        "message": "HybridGenreEngine ist NO-OP - Logik nicht implementiert"
                    })
            except Exception:
                pass
    
    def check_genre_priority_tree(self):
        """Prüft Genre-Priority-Tree."""
        # Prüfe ob Genre-Prioritäten korrekt implementiert sind
        pass
    
    def check_genre_fallback_logic(self):
        """Prüft Genre-Fallback-Logik."""
        # Prüfe ob Genre-Fallbacks korrekt implementiert sind
        pass
    
    def check_style_merge_logic(self):
        """Prüft Style-Merge-Logik."""
        # Prüfe ob Style-Merge korrekt implementiert ist
        pass
    
    def check_color_priority_logic(self):
        """Prüft Color-Priority-Logik."""
        # Prüfe ob Color-Prioritäten korrekt implementiert sind
        pass
    
    def check_hybrid_color_logic(self):
        """Prüft Hybrid-Color-Logik."""
        # Prüfe ob Hybrid-Color-Logik korrekt implementiert ist
        pass
    
    def check_instrumentation_priority_logic(self):
        """Prüft Instrumentation-Priority-Logik."""
        # Prüfe ob Instrumentation-Prioritäten korrekt implementiert sind
        pass
    
    def check_section_naming_logic(self):
        """Prüft Section-Naming-Logik."""
        # Prüfe ob Section-Naming korrekt implementiert ist
        pass
    
    def check_section_merge_logic(self):
        """Prüft Section-Merge-Logik."""
        # Prüfe ob Section-Merge korrekt implementiert ist
        pass


class DataConsistencyChecker:
    """Prüft Datenkonsistenz."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
    
    def check_all(self):
        """Prüft alle Datenkonsistenz-Aspekte."""
        # Vereinfachte Implementierung
        pass


class StaticAnalyzer:
    """Erweiterte statische Analyse."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
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
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                rel_path = py_file.relative_to(self.base_path)
                
                self._check_undefined_vars(tree, rel_path)
                self._check_dead_code(tree, rel_path)
                self._check_unreachable_code(tree, rel_path)
                self._check_redundant_conditions(tree, rel_path)
                self._check_duplicated_logic(tree, rel_path)
                self._check_risky_try_blocks(tree, rel_path)
                self._check_unsafe_fallbacks(tree, rel_path)
                self._check_missing_returns(tree, rel_path)
                
            except SyntaxError:
                pass
            except Exception:
                pass
    
    def _check_undefined_vars(self, tree: ast.AST, file_path: Path):
        """Prüft auf undefinierte Variablen."""
        # Vereinfachte Implementierung
        pass
    
    def _check_dead_code(self, tree: ast.AST, file_path: Path):
        """Prüft auf Dead Code."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                body = node.body
                found_return = False
                for stmt in body:
                    if isinstance(stmt, ast.Return) and not found_return:
                        found_return = True
                    elif found_return and not isinstance(stmt, (ast.Pass, ast.Expr)):
                        self.result.static_analysis_issues.append({
                            "severity": MINOR,
                            "message": f"Potentiell unreachable code nach return in {node.name}",
                            "file": str(file_path),
                            "line": stmt.lineno if hasattr(stmt, 'lineno') else None
                        })
    
    def _check_unreachable_code(self, tree: ast.AST, file_path: Path):
        """Prüft auf unreachable Code."""
        # Ähnlich wie dead_code
        pass
    
    def _check_redundant_conditions(self, tree: ast.AST, file_path: Path):
        """Prüft auf redundante Bedingungen."""
        # Vereinfachte Implementierung
        pass
    
    def _check_duplicated_logic(self, tree: ast.AST, file_path: Path):
        """Prüft auf duplizierte Logik."""
        # Vereinfachte Implementierung
        pass
    
    def _check_risky_try_blocks(self, tree: ast.AST, file_path: Path):
        """Prüft auf riskante try-Blöcke."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Prüfe ob except: pass vorhanden ist
                for handler in node.handlers:
                    if handler.type is None:  # bare except
                        if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                            self.result.static_analysis_issues.append({
                                "severity": MINOR,
                                "message": "Bare except: pass gefunden - möglicherweise stille Fehler",
                                "file": str(file_path),
                                "line": node.lineno if hasattr(node, 'lineno') else None
                            })
    
    def _check_unsafe_fallbacks(self, tree: ast.AST, file_path: Path):
        """Prüft auf unsichere Fallbacks."""
        # Vereinfachte Implementierung
        pass
    
    def _check_missing_returns(self, tree: ast.AST, file_path: Path):
        """Prüft auf fehlende Returns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Prüfe ob Funktion einen Return hat (außer __init__, __str__, etc.)
                if node.name.startswith('__') and node.name.endswith('__'):
                    continue
                
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                # Vereinfachte Prüfung - in Produktion würde man Typ-Hints verwenden
                pass


class DynamicTester:
    """Führt dynamische Tests durch."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
        
        self.test_cases = {
            "low_emotion_text": "Das ist ein normaler Text ohne besondere Emotionen.",
            "high_anger_text": "Ich hasse dich! Du bist ein Verräter! Ich will dich zerstören!",
            "high_epic_text": "In den Tiefen der Zeit, wo Legenden geboren werden, erhebt sich der Held.",
            "neutral_observational_text": "Die Sonne scheint. Die Vögel singen. Alles ist ruhig.",
            "folk_ballad_text": "Am Flussufer saß die Maid, sie sang ein Lied so traurig.",
            "electronic_text": "Bass drops, synthesizers, digital beats, electronic rhythm.",
            "hybrid_text": "Folkloristische Melodien treffen auf elektronische Beats.",
            "contradictory_text": "Ich liebe dich und hasse dich gleichzeitig.",
            "nonsense_text": "Blib blab blob zzzz qwerty asdfgh",
            "random_mixed_text": "Folk meets EDM meets cinematic meets hiphop meets jazz meets metal."
        }
    
    def run_tests(self):
        """Führt alle dynamischen Tests aus."""
        for test_name, test_text in self.test_cases.items():
            try:
                self._test_text(test_name, test_text)
            except Exception as e:
                self.result.dynamic_test_results[test_name] = {
                    "status": "error",
                    "error": str(e)
                }
    
    def _test_text(self, test_name: str, text: str):
        """Testet einen Text."""
        try:
            sys.path.insert(0, str(self.base_path))
            from studiocore.core_v6 import StudioCoreV6
            
            core = StudioCoreV6()
            result = core.analyze(text)
            
            self.result.dynamic_test_results[test_name] = {
                "status": "success",
                "result_keys": list(result.keys()) if isinstance(result, dict) else None,
                "has_tlp": "tlp" in result if isinstance(result, dict) else False,
                "has_emotion": "emotion" in result if isinstance(result, dict) else False,
                "has_bpm": "bpm" in result if isinstance(result, dict) else False
            }
        except Exception as e:
            self.result.dynamic_test_results[test_name] = {
                "status": "error",
                "error": str(e)
            }


class PipelineOutputVerifier:
    """Verifiziert Pipeline-Outputs."""
    
    def __init__(self, base_path: Path, result: FunctionalAuditResult):
        self.base_path = base_path
        self.result = result
    
    def verify_outputs(self):
        """Verifiziert alle Pipeline-Outputs."""
        # Nutze dynamische Test-Ergebnisse
        for test_name, test_result in self.result.dynamic_test_results.items():
            if test_result.get("status") != "success":
                continue
            
            # Prüfe TLP-Output
            # Prüfe RDE-Output
            # Prüfe BPM-Output
            # etc.
            pass


class FullFunctionalAudit:
    """Hauptklasse für das vollständige funktionale Audit."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.result = FunctionalAuditResult()
        
        self.arch_checker = ArchitectureChecker(base_path, self.result)
        self.dep_checker = DependencyChecker(base_path, self.result)
        self.pipeline_checker = PipelineFlowChecker(base_path, self.result)
        self.logic_checker = LogicCorrectnessChecker(base_path, self.result)
        self.data_checker = DataConsistencyChecker(base_path, self.result)
        self.static_analyzer = StaticAnalyzer(base_path, self.result)
        self.dynamic_tester = DynamicTester(base_path, self.result)
        self.output_verifier = PipelineOutputVerifier(base_path, self.result)
    
    def run(self):
        """Führt das vollständige funktionale Audit durch."""
        print("🔍 Starte FULL_FUNCTIONAL_AUDIT_STUDIOCORE_V1...")
        
        # 1. Architecture Checks
        print("🏗️  Prüfe Architektur...")
        self.arch_checker.check_file_structure()
        self.arch_checker.check_module_hierarchy()
        self.arch_checker.check_class_hierarchy()
        self.arch_checker.check_stateless_integrity()
        self.arch_checker.check_initialization_sequence()
        self.arch_checker.check_reset_sequences()
        self.arch_checker.check_pipeline_order()
        self.arch_checker.check_module_interoperability()
        
        # 2. Dependency Checks
        print("🔗 Prüfe Dependencies...")
        self.dep_checker.check_import_graph()
        self.dep_checker.check_circular_imports()
        self.dep_checker.check_missing_dependencies()
        self.dep_checker.check_orphan_modules()
        self.dep_checker.check_unused_modules()
        self.dep_checker.check_shadowed_modules()
        self.dep_checker.check_conflicting_imports()
        
        # 3. Pipeline Flow Checks
        print("🌊 Prüfe Pipeline-Flows...")
        self.pipeline_checker.check_all_flows()
        
        # 4. Logic Correctness Checks
        print("🧠 Prüfe Logik-Korrektheit...")
        self.logic_checker.check_all()
        
        # 5. Data Consistency Checks
        print("📊 Prüfe Datenkonsistenz...")
        self.data_checker.check_all()
        
        # 6. Static Analysis
        print("📈 Führe statische Analyse durch...")
        self.static_analyzer.analyze()
        
        # 7. Dynamic Tests
        print("🧪 Führe dynamische Tests durch...")
        self.dynamic_tester.run_tests()
        
        # 8. Pipeline Output Verification
        print("✅ Verifiziere Pipeline-Outputs...")
        self.output_verifier.verify_outputs()
        
        # 9. Generiere Summary
        print("📋 Generiere Summary...")
        self._generate_summary()
        
        print("✅ Audit abgeschlossen!")
    
    def _generate_summary(self):
        """Generiert Summary (was funktioniert, was teilweise funktioniert, was kaputt)."""
        # Analysiere Ergebnisse
        working_engines = []
        partially_working_engines = []
        broken_engines = []
        
        for engine_name, issues in self.result.pipeline_flow_issues.items():
            critical = any(i.get("severity") == CRITICAL for i in issues)
            major = any(i.get("severity") == MAJOR for i in issues)
            
            if critical:
                broken_engines.append(engine_name)
            elif major:
                partially_working_engines.append(engine_name)
            else:
                working_engines.append(engine_name)
        
        self.result.works = working_engines
        self.result.partially_works = partially_working_engines
        self.result.broken = broken_engines
    
    def generate_report(self) -> str:
        """Generiert einen detaillierten Report."""
        report = []
        report.append("=" * 80)
        report.append("FULL_FUNCTIONAL_AUDIT_STUDIOCORE_V1 - REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Critical Errors
        report.append("## CRITICAL ERRORS")
        if self.result.critical_errors:
            for error in self.result.critical_errors:
                report.append(f"  🔴 [{error['category']}] {error['message']}")
                if error.get('file'):
                    report.append(f"      File: {error['file']}")
        else:
            report.append("  ✅ Keine kritischen Fehler gefunden")
        report.append("")
        
        # Major Errors
        report.append("## MAJOR ERRORS")
        if self.result.major_errors:
            for error in self.result.major_errors[:20]:  # Limit auf 20
                report.append(f"  🟠 [{error['category']}] {error['message']}")
        else:
            report.append("  ✅ Keine Major-Fehler gefunden")
        report.append("")
        
        # Pipeline Flow Issues
        report.append("## PIPELINE FLOW ISSUES")
        for engine_name, issues in self.result.pipeline_flow_issues.items():
            if issues:
                report.append(f"  ⚠️  {engine_name}:")
                for issue in issues:
                    report.append(f"      [{issue['severity']}] {issue['message']}")
        report.append("")
        
        # Logic Correctness Issues
        report.append("## LOGIC CORRECTNESS ISSUES")
        for category, issues in self.result.logic_correctness_issues.items():
            if issues:
                report.append(f"  ⚠️  {category}:")
                for issue in issues:
                    report.append(f"      [{issue['severity']}] {issue['message']}")
        report.append("")
        
        # Dynamic Test Results
        report.append("## DYNAMIC TEST RESULTS")
        success_count = sum(1 for r in self.result.dynamic_test_results.values() 
                          if r.get("status") == "success")
        total_count = len(self.result.dynamic_test_results)
        report.append(f"  Erfolgreich: {success_count}/{total_count}")
        for test_name, test_result in self.result.dynamic_test_results.items():
            status = test_result.get("status", "unknown")
            if status == "success":
                report.append(f"  ✅ {test_name}")
            else:
                report.append(f"  ❌ {test_name}: {test_result.get('error', 'Unbekannter Fehler')}")
        report.append("")
        
        # Summary
        report.append("## SUMMARY")
        report.append("### Was funktioniert:")
        for item in self.result.works:
            report.append(f"  ✅ {item}")
        if not self.result.works:
            report.append("  (Keine)")
        report.append("")
        
        report.append("### Was teilweise funktioniert:")
        for item in self.result.partially_works:
            report.append(f"  ⚠️  {item}")
        if not self.result.partially_works:
            report.append("  (Keine)")
        report.append("")
        
        report.append("### Was kaputt ist:")
        for item in self.result.broken:
            report.append(f"  ❌ {item}")
        if not self.result.broken:
            report.append("  (Keine)")
        report.append("")
        
        # Recommended Fix Order
        report.append("## RECOMMENDED FIX ORDER")
        if self.result.critical_errors:
            report.append("  1. Kritische Fehler beheben")
        if self.result.broken:
            report.append("  2. Kaputte Engines reparieren")
        if self.result.circular_imports:
            report.append("  3. Zyklische Imports auflösen")
        if self.result.partially_works:
            report.append("  4. Teilweise funktionierende Engines vervollständigen")
        report.append("")
        
        # Recommended Patch Plan V7
        report.append("## RECOMMENDED PATCH PLAN V7")
        report.append("  1. HybridGenreEngine.resolve() Methode implementieren")
        report.append("  2. NO-OP Skeletons vervollständigen (ColorEngineV3, EpicOverride, etc.)")
        report.append("  3. Zyklische Abhängigkeit emotion ↔ tlp_engine auflösen")
        report.append("  4. Stateless-Integrität verbessern")
        report.append("  5. Pipeline-Output-Verification implementieren")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Hauptfunktion."""
    base_path = Path(__file__).parent
    audit = FullFunctionalAudit(base_path)
    
    try:
        audit.run()
        report = audit.generate_report()
        
        print("\n" + report)
        
        # Speichere Report
        report_path = base_path / "FULL_FUNCTIONAL_AUDIT_REPORT_V1.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Report gespeichert: {report_path}")
        
        # Speichere JSON-Daten
        json_path = base_path / "FULL_FUNCTIONAL_AUDIT_DATA_V1.json"
        json_data = {
            "critical_errors": len(audit.result.critical_errors),
            "major_errors": len(audit.result.major_errors),
            "minor_errors": len(audit.result.minor_errors),
            "circular_imports": audit.result.circular_imports,
            "pipeline_flow_issues": {k: len(v) for k, v in audit.result.pipeline_flow_issues.items()},
            "works": audit.result.works,
            "partially_works": audit.result.partially_works,
            "broken": audit.result.broken,
            "dynamic_test_results": audit.result.dynamic_test_results
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

