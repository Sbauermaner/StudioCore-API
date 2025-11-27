# Funktionen-Tabellen - main/ Verzeichnis

Übersicht aller Funktionen in tabellarischer Form.

---

## auto_log_cleaner.py

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `archive_reports` | `reports: list[str]` | `Path` | Archiviert eine Liste von Diagnoseberichten in eine neue Archivdatei mit Zeitstempel |
| `main` | - | `None` | Hauptfunktion: Verwaltet Archivierung alter Diagnoseberichte (behält letzten 30) |

---

## auto_trigger.py

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `main` | - | - | Startet automatisch vollständige Diagnose über `run_full_diag.sh` Skript |

---

## comprehensive_analysis.py

| Funktion/Methode | Parameter | Rückgabe | Beschreibung |
|------------------|-----------|----------|--------------|
| `__init__` | `base_path: Path` | - | Initialisiert Comprehensive Analyzer mit Basis-Pfad |
| `analyze_all` | - | - | Führt alle 9 Analyseschritte durch |
| `analyze_all_files` | - | - | Analysiert alle Python-Dateien im studiocore/ Verzeichnis |
| `analyze_file` | `file_path: Path` | - | Analysiert eine einzelne Python-Datei (Syntax, Definitionen, State) |
| `collect_definitions` | `tree: ast.AST, file_path: str, lines: List[str]` | - | Sammelt Definitionen (Klassen, Funktionen, Imports) aus AST |
| `check_function_correctness` | `tree: ast.AST, file_path: str, lines: List[str]` | - | Prüft Korrektheit von Funktionen (unreachable code, risky except) |
| `find_state_variables` | `tree: ast.AST, file_path: str, lines: List[str]` | - | Findet State-Variablen auf Module-Level |
| `_is_inside_function_or_class` | `node: ast.AST` | `bool` | Prüft ob AST-Node innerhalb Funktion/Klasse ist |
| `analyze_imports` | - | - | Analysiert Imports und Dependencies, prüft fehlende Module |
| `check_specific_engines` | - | - | Prüft spezifische Engines auf Existenz und wichtige Methoden |
| `check_stateless_behavior` | - | - | Prüft Stateless-Verhalten (Module-Level State, core_v6.py) |
| `find_state_leaks` | - | - | Findet State-Leaks (Tags, Gewichte, Emotionen, Genres) |
| `check_serialization` | - | - | Prüft Serialisierung von result, style, payload |
| `check_mood_color_loss` | - | - | Prüft Verlust von mood und color_wave |
| `find_engine_conflicts` | - | - | Findet Konflikte zwischen Engines (mehrere analyze/process Methoden) |
| `check_monolith_fallback` | - | - | Prüft Monolith-Fallback auf Fehler (silent failures, Import-Fehler) |
| `add_issue` | `file_path: str, line: int, issue_type: str, error: str, solution: str` | - | Fügt ein Issue zur Issues-Liste hinzu |
| `generate_report` | - | `str` | Generiert vollständigen Report (gruppiert nach Typ, max 20 pro Typ) |
| `main` | - | `int` | Hauptfunktion: Führt Analysen durch, speichert Report und JSON |

---

## deep_scan_audit.py

| Funktion/Methode | Parameter | Rückgabe | Beschreibung |
|------------------|-----------|----------|--------------|
| `__init__` | `base_path: Path` | - | Initialisiert Deep Scan Auditor mit Basis-Pfad |
| `scan_all` | - | - | Scannt alle Dateien in studiocore/ Verzeichnis |
| `run_audit_checks` | - | - | Führt spezielle Audit-Checks aus (ruft check_audit_fixes auf) |
| `scan_file` | `file_path: Path, rel_path: Path` | - | Scannt eine einzelne Datei (Syntax, Integrität) |
| `check_syntax` | `content: str, file_path: Path` | `bool` | Prüft Syntax mit ast.parse() |
| `check_integrity` | `content: str, file_path: Path` | `Optional[str]` | Prüft auf undefined variables/functions (vereinfacht) |
| `check_audit_fixes` | - | - | Prüft spezifische Audit-Fixes (HybridGenreEngine, emotion.py, fehlende Module) |
| `generate_report` | - | `str` | Generiert formatierten Report (Fehler, Warnungen, OK, Audit-Checks) |
| `main` | - | `int` | Hauptfunktion: Führt Scan und Audit-Checks durch, speichert Report |

---

## full_project_audit.py

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `_run_compile_check` | - | `tuple[bool, str]` | Kompiliert alle Python-Dateien, gibt Erfolgs-Flag und Output zurück |
| `_validate_structured_files` | - | `list[str]` | Validiert OpenAPI-Dateien (JSON/YAML), gibt Fehlerliste zurück |
| `_check_required_assets` | - | `list[str]` | Prüft kritische Skripte und Config-Dateien (Existenz, Ausführbarkeit) |
| `_check_requirements_duplicates` | - | `list[str]` | Erkennt doppelte Einträge in requirements.txt |
| `full_project_audit` | - | `int` | Hauptfunktion: Führt vollständige Projekt-Audit durch (4 Checks) |

---

## full_scan_audit.py

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `check_syntax` | `file_path` | `tuple[bool, Optional[str]]` | Prüft Datei auf syntaktische Fehler mit ast.parse() |
| `check_class_methods` | `file_path` | `tuple[bool, str]` | Prüft ob obligatorische Methoden vorhanden sind (z.B. HybridGenreEngine.resolve()) |
| `scan_project` | - | - | Führt vollständiges Scannen durch (kritische Dateien, Syntax, Methoden) |

---

## full_system_diagnostics.py

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `_collect_workflow_diagnostics` | - | `tuple[list[str], list[str]]` | Sammelt Workflow-Validierungsinformationen (YAML-Syntax, Dateien, Berechtigungen) |
| `main` | - | `int` | Hauptfunktion: Führt Diagnostik durch, schreibt in lgp.txt, gibt Exit-Code zurück |

---

## full_workflow_diagnostic_checker.py

| Element | Typ | Beschreibung |
|---------|-----|--------------|
| **Dateityp** | Skript | Keine Funktionen - Code wird direkt ausgeführt |
| **Globale Variablen** | `ROOT`, `WF_DIR`, `errors` | Basis-Pfad, Workflow-Verzeichnis, Fehlerliste |
| **Hauptlogik** | Schleifen | Prüft alle `.yml` Dateien auf: YAML-Syntax, Jobs-Block, Steps, referenzierte Dateien |
| **Ausgabe** | Konsolen-Output | Fortschrittsmeldungen und Fehlerliste mit Details |

---

## self_heal.py

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `heal` | `fix_workflows: bool \| None = None` | `list[str]` | Analysiert lgp.txt und behebt verbreitete Fehlertypen (Tags, leere Sektionen, Workflows, Diagnostics) |

---

## Zusammenfassung nach Dateien

| Datei | Anzahl Funktionen | Hauptzweck |
|-------|-------------------|------------|
| `auto_log_cleaner.py` | 2 | Archivierung alter Diagnoseberichte |
| `auto_trigger.py` | 1 | Automatischer Start der Diagnose |
| `comprehensive_analysis.py` | 18 | Umfassende Code-Analyse mit vielen Prüfungen |
| `deep_scan_audit.py` | 9 | Tiefe Code-Überprüfung mit spezifischen Audit-Checks |
| `full_project_audit.py` | 5 | Projektweite Validierung (Kompilierung, Dateien, Requirements) |
| `full_scan_audit.py` | 3 | Vollständiges Scannen mit Syntax- und Methoden-Prüfungen |
| `full_system_diagnostics.py` | 2 | GitHub Workflow-Validierung mit lgp.txt-Integration |
| `full_workflow_diagnostic_checker.py` | 0 (Skript) | Einfacheres Workflow-Validierungsskript |
| `self_heal.py` | 1 | Automatische Fehlerbehebung |
| **GESAMT** | **41 Funktionen** | - |

---

## Funktionen nach Kategorie

### Analyse & Audit
- `ComprehensiveAnalyzer` (18 Methoden)
- `DeepScanAuditor` (9 Methoden)
- `check_syntax` (2x)
- `check_class_methods`
- `scan_project`
- `full_project_audit` (5 Funktionen)

### Workflow & Diagnostik
- `_collect_workflow_diagnostics`
- `main` (full_system_diagnostics.py)
- `full_workflow_diagnostic_checker.py` (Skript)

### Wartung & Automatisierung
- `archive_reports`
- `main` (auto_log_cleaner.py)
- `main` (auto_trigger.py)
- `heal`

---

## Funktionen mit Rückgabewerten

| Funktion | Rückgabetyp | Zweck |
|----------|-------------|-------|
| `archive_reports` | `Path` | Pfad zur Archivdatei |
| `_is_inside_function_or_class` | `bool` | Prüfung ob Node in Funktion/Klasse |
| `check_syntax` (deep_scan_audit) | `bool` | Syntax-Validierung |
| `check_integrity` | `Optional[str]` | Integritäts-Prüfung |
| `check_syntax` (full_scan_audit) | `tuple[bool, Optional[str]]` | Syntax-Prüfung mit Fehlermeldung |
| `check_class_methods` | `tuple[bool, str]` | Methoden-Prüfung mit Status |
| `generate_report` (2x) | `str` | Formatierter Report-String |
| `_run_compile_check` | `tuple[bool, str]` | Kompilierungs-Status und Output |
| `_validate_structured_files` | `list[str]` | Liste von Fehlermeldungen |
| `_check_required_assets` | `list[str]` | Liste von Fehlermeldungen |
| `_check_requirements_duplicates` | `list[str]` | Liste von Fehlermeldungen |
| `_collect_workflow_diagnostics` | `tuple[list[str], list[str]]` | Fehler- und Info-Listen |
| `heal` | `list[str]` | Liste der angewendeten Fixes |
| `main` (comprehensive_analysis) | `int` | Exit-Code (0/1) |
| `main` (deep_scan_audit) | `int` | Exit-Code (0/1) |
| `full_project_audit` | `int` | Exit-Code (0/1) |
| `main` (full_system_diagnostics) | `int` | Exit-Code (0/1) |

---

## Funktionen ohne Rückgabewert (None/Void)

| Funktion | Zweck |
|----------|-------|
| `main` (auto_log_cleaner) | Archivierung (Seiteneffekt: Datei-Operationen) |
| `main` (auto_trigger) | Skript-Ausführung (Seiteneffekt: Subprocess) |
| `__init__` (2x) | Initialisierung (Seiteneffekt: Objekt-Setup) |
| `analyze_all` | Analyse-Durchführung (Seiteneffekt: Issues sammeln) |
| `analyze_all_files` | Datei-Analyse (Seiteneffekt: Issues sammeln) |
| `analyze_file` | Einzeldatei-Analyse (Seiteneffekt: Issues sammeln) |
| `collect_definitions` | Definitionen sammeln (Seiteneffekt: Attribute aktualisieren) |
| `check_function_correctness` | Funktions-Prüfung (Seiteneffekt: Issues sammeln) |
| `find_state_variables` | State-Variablen finden (Seiteneffekt: Attribute aktualisieren) |
| `analyze_imports` | Import-Analyse (Seiteneffekt: Issues sammeln) |
| `check_specific_engines` | Engine-Prüfung (Seiteneffekt: Issues sammeln) |
| `check_stateless_behavior` | Stateless-Prüfung (Seiteneffekt: Issues sammeln) |
| `find_state_leaks` | State-Leak-Suche (Seiteneffekt: Issues sammeln) |
| `check_serialization` | Serialisierungs-Prüfung (Seiteneffekt: Issues sammeln) |
| `check_mood_color_loss` | Mood/Color-Prüfung (Seiteneffekt: Issues sammeln) |
| `find_engine_conflicts` | Konflikt-Suche (Seiteneffekt: Issues sammeln) |
| `check_monolith_fallback` | Fallback-Prüfung (Seiteneffekt: Issues sammeln) |
| `add_issue` | Issue hinzufügen (Seiteneffekt: Liste erweitern) |
| `scan_all` | Vollständiger Scan (Seiteneffekt: Results sammeln) |
| `run_audit_checks` | Audit-Checks ausführen (Seiteneffekt: Results sammeln) |
| `scan_file` | Datei scannen (Seiteneffekt: Results sammeln) |
| `check_audit_fixes` | Audit-Fixes prüfen (Seiteneffekt: Results sammeln) |
| `scan_project` | Projekt scannen (Seiteneffekt: Konsolen-Ausgabe) |

---

## Funktionen mit Datei-Operationen

| Funktion | Operation | Datei(en) |
|----------|-----------|-----------|
| `archive_reports` | Schreiben | `archive/lgp_archive_{timestamp}.txt` |
| `main` (auto_log_cleaner) | Lesen/Schreiben | `main/lgp.txt` |
| `generate_report` (comprehensive) | - | (wird von main geschrieben) |
| `main` (comprehensive_analysis) | Schreiben | `COMPREHENSIVE_ANALYSIS_REPORT.md`, `COMPREHENSIVE_ANALYSIS_DATA.json` |
| `generate_report` (deep_scan) | - | (wird von main geschrieben) |
| `main` (deep_scan_audit) | Schreiben | `DEEP_SCAN_AUDIT_REPORT.md` |
| `check_syntax` (2x) | Lesen | Verschiedene Python-Dateien |
| `check_class_methods` | Lesen | Python-Dateien |
| `scan_project` | Lesen | Python-Dateien in studiocore/ |
| `main` (full_system_diagnostics) | Lesen/Schreiben | `.github/workflows/*.yml`, `main/lgp.txt` |
| `heal` | Lesen/Schreiben | `main/lgp.txt`, `.github/workflows/*.yml` |

---

## Funktionen mit AST-Operationen

| Funktion | AST-Operation | Zweck |
|----------|--------------|-------|
| `analyze_file` | `ast.parse()` | Syntax-Validierung |
| `collect_definitions` | `ast.walk()` | Definitionen sammeln |
| `check_function_correctness` | `ast.walk()` | Funktions-Prüfung |
| `find_state_variables` | `ast.walk()` | State-Variablen finden |
| `_is_inside_function_or_class` | AST-Traversierung | Node-Position prüfen |
| `check_syntax` (deep_scan) | `ast.parse()` | Syntax-Validierung |
| `check_integrity` | `ast.parse()`, `ast.walk()` | Integritäts-Prüfung |
| `check_syntax` (full_scan) | `ast.parse()` | Syntax-Validierung |
| `check_class_methods` | `ast.parse()`, `ast.walk()` | Methoden-Prüfung |

---

## Funktionen mit Subprocess/System-Aufrufen

| Funktion | Aufruf | Zweck |
|----------|--------|-------|
| `main` (auto_trigger) | `subprocess.run(["bash", script])` | Shell-Skript ausführen |
| `_run_compile_check` | `subprocess.run([sys.executable, "-m", "compileall"])` | Python-Kompilierung |

---

**Erstellt:** Aktueller Stand
**Stand:** Alle Funktionen aus main/ Verzeichnis

