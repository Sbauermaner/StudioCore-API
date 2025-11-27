# Funktionsdokumentation - main/ Verzeichnis

Diese Dokumentation beschreibt alle Funktionen in den Dateien des `main/`-Verzeichnisses im aktuellen Zustand.

---

## auto_log_cleaner.py

### `archive_reports(reports: list[str]) -> Path`
**Beschreibung:** Archiviert eine Liste von Diagnoseberichten in eine neue Archivdatei.

**Parameter:**
- `reports` (list[str]): Liste von Bericht-Strings, die archiviert werden sollen

**Rückgabe:**
- `Path`: Pfad zur erstellten Archivdatei

**Details:**
- Erstellt einen Zeitstempel im Format `YYYYMMDD_HHMMSS`
- Generiert einen Archivdateinamen im Format `lgp_archive_{timestamp}.txt`
- Schreibt alle Berichte mit Header-Präfix in die Archivdatei
- Verwendet UTF-8 Encoding

**Beispiel:**
```python
reports = ["Report 1", "Report 2"]
archive_path = archive_reports(reports)
```

---

### `main() -> None`
**Beschreibung:** Hauptfunktion des Auto Log Cleaners. Verwaltet die Archivierung alter Diagnoseberichte.

**Funktionalität:**
1. Erstellt das Archiv-Verzeichnis falls es nicht existiert
2. Prüft ob die `lgp.txt` Datei existiert
3. Liest den Inhalt der `lgp.txt` Datei
4. Teilt den Inhalt anhand des Headers in einzelne Berichte auf
5. Prüft ob mehr als 30 Berichte vorhanden sind
6. Archiviert alle Berichte außer den letzten 30
7. Behält nur die letzten 30 Berichte in `lgp.txt`
8. Gibt eine Zusammenfassung der Archivierung aus

**Ausgabe:**
- Konsolenmeldungen über den Archivierungsstatus
- Fehlermeldung wenn `lgp.txt` nicht gefunden wird
- Bestätigung wenn keine Archivierung nötig ist

---

## auto_trigger.py

### `main()`
**Beschreibung:** Startet automatisch die vollständige Diagnose über das Shell-Skript `run_full_diag.sh`.

**Funktionalität:**
1. Gibt eine Startmeldung aus
2. Ermittelt den Pfad zum `run_full_diag.sh` Skript (im übergeordneten Verzeichnis)
3. Führt das Shell-Skript mit `bash` aus
4. Prüft den Exit-Code (wirft Exception bei Fehler)
5. Gibt eine Abschlussmeldung aus

**Verwendung:**
- Wird von GitHub Actions und lokalen CI-Systemen verwendet
- Sollte sicher in automatisierten Umgebungen laufen

**Fehlerbehandlung:**
- Wirft `subprocess.CalledProcessError` wenn das Skript fehlschlägt

---

## comprehensive_analysis.py

### `ComprehensiveAnalyzer.__init__(self, base_path: Path)`
**Beschreibung:** Initialisiert den Comprehensive Analyzer.

**Parameter:**
- `base_path` (Path): Basis-Pfad des Projekts

**Initialisierte Attribute:**
- `base_path`: Basis-Pfad
- `studiocore_path`: Pfad zum `studiocore/` Verzeichnis
- `issues`: Liste von gefundenen Problemen
- `module_imports`: Dictionary mit Import-Informationen pro Datei
- `module_exports`: Dictionary mit Export-Informationen pro Datei
- `class_definitions`: Dictionary mit Klassen-Definitionen pro Datei
- `function_definitions`: Dictionary mit Funktions-Definitionen pro Datei
- `state_variables`: Dictionary mit State-Variablen pro Datei

---

### `ComprehensiveAnalyzer.analyze_all(self)`
**Beschreibung:** Führt alle Analyseschritte durch.

**Analyseschritte:**
1. Analysiert alle Python-Dateien
2. Analysiert Imports und Dependencies
3. Prüft spezifische Engines
4. Prüft Stateless-Verhalten
5. Sucht nach State-Leaks
6. Prüft Serialisierung
7. Prüft Verlust von mood und color_wave
8. Sucht Engine-Konflikte
9. Prüft Monolith-Fallback

**Ausgabe:**
- Fortschrittsmeldungen für jeden Analyseschritt
- Abschlussmeldung

---

### `ComprehensiveAnalyzer.analyze_all_files(self)`
**Beschreibung:** Analysiert alle Python-Dateien im `studiocore/` Verzeichnis.

**Funktionalität:**
- Durchsucht rekursiv alle `.py` Dateien
- Überspringt `__init__.py` Dateien
- Ruft `analyze_file()` für jede Datei auf

---

### `ComprehensiveAnalyzer.analyze_file(self, file_path: Path)`
**Beschreibung:** Analysiert eine einzelne Python-Datei.

**Parameter:**
- `file_path` (Path): Pfad zur zu analysierenden Datei

**Prüfungen:**
1. Syntax-Check mit `ast.parse()`
2. Sammelt Definitionen (Klassen, Funktionen, Imports)
3. Prüft Funktionskorrektheit
4. Findet State-Variablen

**Fehlerbehandlung:**
- Erfasst Syntax-Fehler als Issues
- Erfasst Datei-Lese-Fehler als Issues

---

### `ComprehensiveAnalyzer.collect_definitions(self, tree: ast.AST, file_path: str, lines: List[str])`
**Beschreibung:** Sammelt alle Definitionen aus einem AST-Baum.

**Parameter:**
- `tree` (ast.AST): Der geparste AST-Baum
- `file_path` (str): Pfad zur Datei
- `lines` (List[str]): Zeilen der Datei

**Gesammelte Informationen:**
- Imports (sowohl `import` als auch `from ... import`)
- Exports (Klassen, öffentliche Funktionen)
- Klassen-Definitionen
- Funktions-Definitionen

**Speicherung:**
- Aktualisiert `module_imports`, `module_exports`, `class_definitions`, `function_definitions`

---

### `ComprehensiveAnalyzer.check_function_correctness(self, tree: ast.AST, file_path: str, lines: List[str])`
**Beschreibung:** Prüft die Korrektheit von Funktionen.

**Parameter:**
- `tree` (ast.AST): Der geparste AST-Baum
- `file_path` (str): Pfad zur Datei
- `lines` (List[str]): Zeilen der Datei

**Prüfungen:**
1. Unreachable Code nach `return` Statements
2. Riskante `try-except` Blöcke (bare except mit pass)

**Erkannte Probleme:**
- Code nach einem `return` Statement
- Bare `except: pass` Konstrukte

---

### `ComprehensiveAnalyzer.find_state_variables(self, tree: ast.AST, file_path: str, lines: List[str])`
**Beschreibung:** Findet State-Variablen auf Module-Level.

**Parameter:**
- `tree` (ast.AST): Der geparste AST-Baum
- `file_path` (str): Pfad zur Datei
- `lines` (List[str]): Zeilen der Datei

**Funktionalität:**
- Durchsucht alle `ast.Assign` Nodes
- Prüft ob die Zuweisung auf Module-Level ist (nicht in Funktion/Klasse)
- Speichert gefundene Variablen in `state_variables`

---

### `ComprehensiveAnalyzer._is_inside_function_or_class(self, node: ast.AST) -> bool`
**Beschreibung:** Prüft ob ein AST-Node innerhalb einer Funktion oder Klasse ist.

**Parameter:**
- `node` (ast.AST): Der zu prüfende Node

**Rückgabe:**
- `bool`: `True` wenn Node in Funktion/Klasse, sonst `False`

**Hinweis:**
- Vereinfachte Implementierung, verwendet `parent` Attribut falls vorhanden

---

### `ComprehensiveAnalyzer.analyze_imports(self)`
**Beschreibung:** Analysiert Imports und Dependencies.

**Funktionalität:**
- Prüft alle gesammelten Imports
- Überprüft ob importierte `studiocore.*` Module existieren
- Erstellt Issues für fehlende Module

**Erkannte Probleme:**
- Fehlende Module die importiert werden
- Falsche Import-Pfade

---

### `ComprehensiveAnalyzer.check_specific_engines(self)`
**Beschreibung:** Prüft spezifische Engines auf Existenz und wichtige Methoden.

**Geprüfte Engines:**
- `SectionParser` in `section_parser.py`
- `EmotionEngine` in `emotion.py`
- `TruthLovePainEngine` in `tlp_engine.py`
- `RhythmDynamicsEmotionEngine` in `rde_engine.py`
- `ToneSyncEngine` in `tone.py`
- `BPMEngine` in `bpm_engine.py`
- `GenreMatrix` in `genre_matrix_extended.py`
- `ColorEngineAdapter` in `color_engine_adapter.py`
- `InstrumentationEngine` in `logical_engines.py`
- `VocalEngine` in `logical_engines.py`

**Prüfungen:**
- Existenz der Engine-Klasse
- Vorhandensein wichtiger Methoden (z.B. `parse()` für SectionParser)

---

### `ComprehensiveAnalyzer.check_stateless_behavior(self)`
**Beschreibung:** Prüft Stateless-Verhalten des Systems.

**Prüfungen:**
1. Module-Level State-Variablen (warnet bei >5 Variablen)
2. `core_v6.py` auf `_build_engine_bundle` Methode
3. Persistente Instanz-Variablen in `core_v6.py`

**Erkannte Probleme:**
- Zu viele Module-Level Variablen
- Fehlende `_build_engine_bundle` Methode
- Potentielle State-Leaks durch persistente Instanz-Variablen

---

### `ComprehensiveAnalyzer.find_state_leaks(self)`
**Beschreibung:** Findet State-Leaks (Tags, Gewichte, Emotionen, Genres).

**Suchbegriffe:**
- `tag`, `weight`, `emotion`, `genre`, `mood`, `color`

**Prüfungen:**
- Sucht nach `self.` Variablen die zwischen Requests gespeichert werden könnten
- Ignoriert Variablen in `__init__` (OK)
- Ignoriert Variablen mit `cache` oder `temp` im Namen

**Erkannte Probleme:**
- Potentielle State-Leaks durch persistente Instanz-Variablen

---

### `ComprehensiveAnalyzer.check_serialization(self)`
**Beschreibung:** Prüft Serialisierung von `result`, `style`, `payload`.

**Prüfungen:**
- Existenz von `result` in `core_v6.py`
- Behandlung von `result["style"]`
- Behandlung von `result["payload"]`

**Hinweis:**
- Aktuell werden nur grundlegende Prüfungen durchgeführt

---

### `ComprehensiveAnalyzer.check_mood_color_loss(self)`
**Beschreibung:** Prüft Verlust von `mood` und `color_wave`.

**Prüfungen:**
- Sucht nach Stellen wo `mood` gesetzt wird
- Prüft ob `mood` versehentlich gelöscht wird (`del`, `pop()`)
- Gleiche Prüfung für `color_wave`

**Erkannte Probleme:**
- Versehentliches Löschen von `mood` oder `color_wave`

---

### `ComprehensiveAnalyzer.find_engine_conflicts(self)`
**Beschreibung:** Findet Konflikte zwischen Engines.

**Prüfungen:**
- Mehrere `analyze()` Methoden in verschiedenen Emotion-Engines
- Mehrere `process()` Methoden in verschiedenen Emotion-Engines

**Erkannte Probleme:**
- Mehr als 2 `analyze()` Methoden in verschiedenen Dateien

---

### `ComprehensiveAnalyzer.check_monolith_fallback(self)`
**Beschreibung:** Prüft Monolith-Fallback auf Fehler.

**Geprüfte Dateien:**
- `fallback.py`
- `monolith_v4_3_1.py`

**Prüfungen:**
- Silent Failures (`except: pass`)
- Import-Fehler Behandlung

**Erkannte Probleme:**
- Silent Failures ohne Logging
- Unbehandelte Import-Fehler

---

### `ComprehensiveAnalyzer.add_issue(self, file_path: str, line: int, issue_type: str, error: str, solution: str)`
**Beschreibung:** Fügt ein Issue zur Issues-Liste hinzu.

**Parameter:**
- `file_path` (str): Pfad zur betroffenen Datei
- `line` (int): Zeilennummer
- `issue_type` (str): Typ des Issues
- `error` (str): Fehlerbeschreibung
- `solution` (str): Lösungsvorschlag

**Funktionalität:**
- Erstellt ein Dictionary mit allen Informationen
- Fügt es zur `self.issues` Liste hinzu

---

### `ComprehensiveAnalyzer.generate_report(self) -> str`
**Beschreibung:** Generiert einen vollständigen Report.

**Rückgabe:**
- `str`: Formatierter Report-String

**Report-Struktur:**
1. Header
2. Issues gruppiert nach Typ
3. Zusammenfassung mit Statistiken
4. System-Status

**Limitierung:**
- Zeigt maximal 20 Issues pro Typ

---

### `main() -> int`
**Beschreibung:** Hauptfunktion des Comprehensive Analyzers.

**Funktionalität:**
1. Erstellt Analyzer-Instanz
2. Führt alle Analysen durch
3. Generiert Report
4. Druckt Report auf Konsole
5. Speichert Report als Markdown-Datei
6. Speichert Issues als JSON-Datei

**Ausgabedateien:**
- `COMPREHENSIVE_ANALYSIS_REPORT.md`
- `COMPREHENSIVE_ANALYSIS_DATA.json`

**Exit-Code:**
- `0` wenn keine Issues gefunden
- `1` wenn Issues gefunden wurden

---

## deep_scan_audit.py

### `DeepScanAuditor.__init__(self, base_path: Path)`
**Beschreibung:** Initialisiert den Deep Scan Auditor.

**Parameter:**
- `base_path` (Path): Basis-Pfad des Projekts

**Initialisierte Attribute:**
- `base_path`: Basis-Pfad
- `studiocore_path`: Pfad zum `studiocore/` Verzeichnis
- `results`: Liste von Tupeln `(file, status, comment)`

---

### `DeepScanAuditor.scan_all(self)`
**Beschreibung:** Scannt alle Dateien in `studiocore/`.

**Funktionalität:**
1. Prüft ob `studiocore/` Verzeichnis existiert
2. Findet alle Python-Dateien rekursiv
3. Ruft `scan_file()` für jede Datei auf
4. Gibt Anzahl gescannter Dateien aus

---

### `DeepScanAuditor.run_audit_checks(self)`
**Beschreibung:** Führt spezielle Audit-Checks aus.

**Funktionalität:**
- Ruft `check_audit_fixes()` auf

---

### `DeepScanAuditor.scan_file(self, file_path: Path, rel_path: Path)`
**Beschreibung:** Scannt eine einzelne Datei.

**Parameter:**
- `file_path` (Path): Absoluter Pfad zur Datei
- `rel_path` (Path): Relativer Pfad zur Datei

**Prüfungen:**
1. Syntax-Check
2. Basis-Integritäts-Check

**Ergebnisse:**
- `ERROR` bei Syntax-Fehlern
- `WARNING` bei Integritäts-Problemen
- `OK` wenn keine Probleme gefunden

---

### `DeepScanAuditor.check_syntax(self, content: str, file_path: Path) -> bool`
**Beschreibung:** Prüft Syntax mit `ast.parse()`.

**Parameter:**
- `content` (str): Dateiinhalt
- `file_path` (Path): Pfad zur Datei

**Rückgabe:**
- `bool`: `True` wenn Syntax korrekt, sonst `False`

**Funktionalität:**
- Verwendet `ast.parse()` zur Syntax-Validierung
- Fängt alle Exceptions ab

---

### `DeepScanAuditor.check_integrity(self, content: str, file_path: Path) -> Optional[str]`
**Beschreibung:** Prüft auf undefined variables/functions.

**Parameter:**
- `content` (str): Dateiinhalt
- `file_path` (Path): Pfad zur Datei

**Rückgabe:**
- `Optional[str]`: Fehlermeldung oder `None`

**Funktionalität:**
- Sammelt definierte Namen (Funktionen, Klassen)
- Sammelt importierte Namen
- Prüft auf offensichtliche undefined calls (vereinfacht)

**Hinweis:**
- Aktuell nur Grundgerüst, vollständiger Scope-Tracker würde in Produktion verwendet

---

### `DeepScanAuditor.check_audit_fixes(self)`
**Beschreibung:** Prüft spezifische Audit-Fixes.

**Geprüfte Fixes:**
1. **HybridGenreEngine.resolve()**
   - Prüft ob `resolve()` Methode vorhanden ist
   - Prüft ob beide Signaturen unterstützt werden (`text_input`, `genre`)

2. **emotion.py - kein top-level Import von tlp_engine**
   - Prüft erste 50 Zeilen auf top-level Imports
   - Prüft ob lazy Import vorhanden ist

3. **Fehlende Module**
   - Prüft Existenz von:
     - `universal_frequency_engine.py`
     - `hybrid_instrumentation_layer.py`
     - `neutral_mode_pre_finalizer.py`
   - Prüft ob Dateien nicht leer sind (>50 Zeichen)

**Ergebnisse:**
- Fügt Ergebnisse zur `results` Liste hinzu

---

### `DeepScanAuditor.generate_report(self) -> str`
**Beschreibung:** Generiert einen formatierten Report.

**Rückgabe:**
- `str`: Formatierter Report-String

**Report-Struktur:**
1. Header
2. Fehler-Sektion
3. Warnungen-Sektion
4. OK-Sektion (erste 20 Dateien)
5. Spezielle Audit-Checks
6. Zusammenfassung mit Statistiken
7. System-Status

**Status-Symbole:**
- ✅ für OK
- ⚠️ für WARNING
- ❌ für ERROR

---

### `main() -> int`
**Beschreibung:** Hauptfunktion des Deep Scan Auditors.

**Funktionalität:**
1. Erstellt Auditor-Instanz
2. Führt Scan durch
3. Führt Audit-Checks durch
4. Generiert Report
5. Druckt Report auf Konsole
6. Speichert Report als Markdown-Datei

**Ausgabedatei:**
- `DEEP_SCAN_AUDIT_REPORT.md`

**Exit-Code:**
- `0` wenn keine Fehler gefunden
- `1` wenn Fehler gefunden wurden

---

## full_project_audit.py

### `_run_compile_check() -> tuple[bool, str]`
**Beschreibung:** Kompiliert alle Python-Dateien und gibt Erfolgs-Flag mit Output zurück.

**Rückgabe:**
- `tuple[bool, str]`: `(success, output)`

**Funktionalität:**
- Führt `python -m compileall . -q` aus
- Sammelt stdout und stderr
- Gibt Erfolgs-Status und Output zurück

**Verwendung:**
- Validierung der Python-Syntax im gesamten Projekt

---

### `_validate_structured_files() -> list[str]`
**Beschreibung:** Validiert OpenAPI-Dateien können als JSON/YAML geparst werden.

**Rückgabe:**
- `list[str]`: Liste von Fehlermeldungen (leer wenn keine Fehler)

**Geprüfte Dateien:**
- `openapi.json` (JSON-Validierung)
- `openapi.yaml` (YAML-Validierung)

**Erkannte Probleme:**
- Ungültiges JSON/YAML
- Fehlende Dateien

---

### `_check_required_assets() -> list[str]`
**Beschreibung:** Bestätigt dass kritische Skripte und Config-Dateien existieren und verwendbar sind.

**Rückgabe:**
- `list[str]`: Liste von Fehlermeldungen

**Geprüfte Dateien:**
- `run_full_diag.sh` (muss existieren und ausführbar sein)
- `main/full_system_diagnostics.py`
- `main/auto_log_cleaner.py`
- `app.py`
- `requirements.txt`

**Erkannte Probleme:**
- Fehlende Dateien
- Nicht ausführbare Shell-Skripte

---

### `_check_requirements_duplicates() -> list[str]`
**Beschreibung:** Erkennt doppelte Einträge in `requirements.txt`.

**Rückgabe:**
- `list[str]`: Liste von Fehlermeldungen

**Funktionalität:**
- Liest `requirements.txt`
- Ignoriert leere Zeilen und Kommentare
- Erkennt doppelte Einträge (case-insensitive)

**Erkannte Probleme:**
- Doppelte Requirements-Einträge

---

### `full_project_audit() -> int`
**Beschreibung:** Führt vollständige Projekt-Audit durch.

**Rückgabe:**
- `int`: Exit-Code (0 = Erfolg, 1 = Fehler)

**Audit-Schritte:**
1. Kompilierungs-Check
2. Validierung strukturierter Dateien
3. Prüfung erforderlicher Assets
4. Prüfung auf doppelte Requirements

**Ausgabe:**
- Erfolgsmeldungen für bestandene Checks
- Fehlermeldungen für gefundene Probleme

**Exit-Code:**
- `0` wenn keine Fehler
- `1` wenn Fehler gefunden

---

## full_scan_audit.py

### `check_syntax(file_path) -> tuple[bool, Optional[str]]`
**Beschreibung:** Prüft Datei auf syntaktische Fehler.

**Parameter:**
- `file_path`: Pfad zur zu prüfenden Datei

**Rückgabe:**
- `tuple[bool, Optional[str]]`: `(valid, error_message)`

**Funktionalität:**
- Liest Dateiinhalt
- Verwendet `ast.parse()` zur Syntax-Validierung
- Fängt `SyntaxError` und andere Exceptions ab

**Rückgabe:**
- `(True, None)` wenn Syntax korrekt
- `(False, error_message)` bei Fehlern

---

### `check_class_methods(file_path) -> tuple[bool, str]`
**Beschreibung:** Prüft ob obligatorische Methoden vorhanden sind (Audit-Fix).

**Parameter:**
- `file_path`: Pfad zur zu prüfenden Datei

**Rückgabe:**
- `tuple[bool, str]`: `(valid, message)`

**Geprüfte Klassen:**
- `HybridGenreEngine` muss `resolve()` Methode haben

**Funktionalität:**
- Parst Datei mit AST
- Findet alle Klassen
- Prüft ob erforderliche Methoden vorhanden sind

**Rückgabe:**
- `(True, "OK")` wenn alle Methoden vorhanden
- `(False, error_message)` wenn Methoden fehlen

---

### `scan_project()`
**Beschreibung:** Führt vollständiges Scannen des Projekts durch.

**Funktionalität:**
1. Prüft Existenz kritischer Dateien:
   - `universal_frequency_engine.py`
   - `hybrid_instrumentation_layer.py`
   - `neutral_mode_pre_finalizer.py`
2. Scannt alle Python-Dateien in `studiocore/`:
   - Syntax-Check
   - Spezifische Klassen-Prüfungen (HybridGenreEngine)

**Ausgabe:**
- Fortschrittsmeldungen
- Fehlermeldungen für gefundene Probleme
- Zusammenfassung am Ende

**Ergebnis:**
- Erfolgsmeldung wenn keine Fehler
- Fehlerliste wenn Probleme gefunden

---

## full_system_diagnostics.py

### `_collect_workflow_diagnostics() -> tuple[list[str], list[str]]`
**Beschreibung:** Sammelt Workflow-Validierungsinformationen und Fehlermeldungen.

**Rückgabe:**
- `tuple[list[str], list[str]]`: `(errors, info)`

**Prüfungen:**
1. **YAML-Syntax für alle Workflows**
   - Validiert alle `.yml` Dateien in `.github/workflows/`
   - Verwendet `yaml.safe_load()`
   - Fügt Erfolgsmeldungen zu `info` hinzu

2. **Referenzierte Dateien in run-Schritten**
   - Durchsucht alle Workflow-Dateien nach `run:` Zeilen
   - Prüft ob referenzierte Dateien existieren:
     - `run_full_diag.sh` (muss im ROOT existieren)
     - `auto_log_cleaner.py` (muss in `main/` existieren)
     - `full_system_diagnostics.py` (muss in `main/` existieren)

3. **Ausführbarkeit von `run_full_diag.sh`**
   - Prüft ob Datei existiert
   - Prüft ob Datei ausführbar ist (chmod +x)
   - Prüft Datei-Berechtigungen mit `stat().st_mode & 0o100`

4. **Erforderliche main/*.py Dateien**
   - Prüft Existenz von:
     - `full_system_diagnostics.py`
     - `auto_trigger.py`
     - `auto_log_cleaner.py`

**Hilfsfunktion:**
- `add(msg: str)`: Fügt Fehlermeldung zur `errors` Liste hinzu

**Rückgabe:**
- `errors`: Liste von Fehlermeldungen
- `info`: Liste von Informationsmeldungen (Erfolgsmeldungen)

---

### `main() -> int`
**Beschreibung:** Hauptfunktion für vollständige System-Diagnostik.

**Funktionalität:**
1. Sammelt Workflow-Diagnostik
2. Druckt Header und Informationsmeldungen
3. Druckt Fehlermeldungen falls vorhanden
4. Schreibt Ergebnisse in `main/lgp.txt`:
   - Header mit Timestamp
   - Informationsmeldungen
   - Fehlermeldungen (falls vorhanden)
   - Status (PASSED/FAILED)
   - Trennlinie

**Report-Format:**
```
=== StudioCore — FULL SYSTEM DIAGNOSTIC REPORT ===
Timestamp: YYYY-MM-DD HH:MM:SS UTC
[OK] YAML syntax valid → workflow_name.yml
...
Status: PASSED/FAILED
==================================================
```

**Ausgabe:**
- Konsolen-Ausgabe mit Header und Ergebnissen
- Datei-Ausgabe in `main/lgp.txt` (append mode)

**Exit-Code:**
- `0` wenn keine Fehler gefunden
- `1` wenn Fehler gefunden wurden

**Hinweis:**
- Diese Datei ist identisch mit `full_workflow_diagnostic_checker.py`
- Beide Dateien führen die gleichen Prüfungen durch

---

## full_workflow_diagnostic_checker.py

**Hinweis:** Diese Datei ist ein Skript ohne Funktionen - der Code wird direkt ausgeführt.

**Beschreibung:** Prüft alle `.github/workflows/*.yml` Dateien auf Fehler und meldet welcher Workflow den Pipeline bricht und in welcher Zeile der Fehler ist.

**Globale Variablen:**
- `ROOT`: Basis-Pfad des Projekts (übergeordnetes Verzeichnis)
- `WF_DIR`: Pfad zu `.github/workflows/`
- `errors`: Liste von Fehlertupeln `(workflow_name, location, error_message)`

**Ausgeführte Prüfungen:**

1. **YAML-Syntax-Validierung**
   - Für jede `.yml` Datei in `.github/workflows/`:
     - Liest Dateiinhalt
     - Versucht `yaml.safe_load()` auszuführen
     - Bei Fehler: Fügt Tupel `(workflow_name, "YAML SYNTAX ERROR", error_message)` hinzu
     - Setzt mit `continue` fort bei Syntax-Fehler

2. **Jobs-Block-Prüfung**
   - Prüft ob `"jobs"` Key im geparsten YAML vorhanden ist
   - Bei Fehlen: Fügt Tupel `(workflow_name, "NO JOBS BLOCK", "Missing 'jobs:' root key")` hinzu

3. **Job-Steps-Korrektheit**
   - Für jeden Job in `data["jobs"]`:
     - Prüft ob `"steps"` Key vorhanden ist
     - Bei Fehlen: Fügt Tupel `(workflow_name, job_name, "Missing 'steps:'")` hinzu
     - Für jeden Step:
       - Prüft ob `"run"` Key vorhanden ist
       - Sucht nach `"run_full_diag.sh"` im Befehl:
         - Prüft ob Datei existiert
         - Bei Fehlen: Fügt Tupel `(workflow_name, job_name, "Script not found: {path}")` hinzu
       - Sucht nach `"auto_log_cleaner.py"` im Befehl:
         - Prüft ob Datei in `main/` existiert
         - Bei Fehlen: Fügt Tupel `(workflow_name, job_name, "auto_log_cleaner.py missing")` hinzu

**Ausgabe:**
- Fortschrittsmeldungen: `">>> Scanning workflows..."`
- Für jeden Workflow: `"Checking: {workflow_name}"`
- Erfolgsmeldung: `"OK: {workflow_name}"`
- Zusammenfassung:
  - Wenn keine Fehler: `"All workflows are valid — no structural errors."`
  - Wenn Fehler gefunden:
    - `"FOUND ERRORS:"`
    - Für jeden Fehler:
      - `"Workflow: {workflow_name}"`
      - `"Location: {location}"`
      - `"Error: {error_message}"`
      - Trennlinie `"-" * 40`

**Fehlerformat:**
- Fehler werden als Tupel gespeichert: `(workflow_name, location, error_message)`
- `location` kann sein: Job-Name, "YAML SYNTAX ERROR", "NO JOBS BLOCK"

**Hinweis:**
- Diese Datei ist ein einfacheres Skript im Vergleich zu `full_system_diagnostics.py`
- Führt keine Datei-Schreiboperationen durch (nur Konsolen-Ausgabe)
- Prüft die YAML-Struktur detaillierter (jobs, steps)

---

## self_heal.py

### `heal(fix_workflows: bool | None = None) -> list[str]`
**Beschreibung:** Analysiert `lgp.txt` und behebt verbreitete Fehlertypen.

**Parameter:**
- `fix_workflows` (bool | None): Ob Workflow-Fixes aktiviert werden sollen. Wenn `None`, wird Umgebungsvariable `STUDIOCORE_HEAL_WORKFLOWS` geprüft.

**Rückgabe:**
- `list[str]`: Liste der angewendeten Fixes

**Durchgeführte Fixes:**

1. **Entfernung alter Tags**
   - Entfernt veraltete Tags wie:
     - `"cinematic narrative"`
     - `"majestic major"`
     - `"EMOTION: neutral"`
     - `"female soprano"`
     - `"[91 BPM]"`
     - `"choir_mixed"`

2. **Korrektur leerer Sektionen**
   - Ersetzt `"Segmentation: []"` durch `"Segmentation: [not detected]"`

3. **Automatische Workflow-Korrekturen** (nur wenn aktiviert)
   - Korrigiert Pfade in `.github/workflows/*.yml`:
     - `"bash ./run_full_diag.sh"` → `"bash ${{ github.workspace }}/run_full_diag.sh"`
   - Normalisiert Python-Aufrufe:
     - `"python main/"` → `"python3 main/"`

4. **Normalisierung leerer Diagnostics**
   - Ersetzt `"Diagnostics: None"` durch `"Diagnostics: []"`

**Funktionalität:**
- Liest `main/lgp.txt`
- Wendet alle relevanten Fixes an
- Schreibt geänderte Datei zurück
- Fügt Self-Heal-Log am Ende der Datei hinzu

**Rückgabe:**
- Liste von Strings beschreibend welche Fixes angewendet wurden
- `"lgp.txt not found"` wenn Datei nicht existiert

---

## Zusammenfassung

### Dateien und ihre Hauptzwecke:

1. **auto_log_cleaner.py** - Archiviert alte Diagnoseberichte
2. **auto_trigger.py** - Startet automatisch vollständige Diagnose
3. **comprehensive_analysis.py** - Umfassende Code-Analyse mit vielen Prüfungen
4. **deep_scan_audit.py** - Tiefe Code-Überprüfung mit spezifischen Audit-Checks
5. **full_project_audit.py** - Projektweite Validierung (Kompilierung, Dateien, Requirements)
6. **full_scan_audit.py** - Vollständiges Scannen mit Syntax- und Methoden-Prüfungen
7. **full_system_diagnostics.py** - GitHub Workflow-Validierung mit lgp.txt-Integration
8. **full_workflow_diagnostic_checker.py** - Einfacheres Workflow-Validierungsskript (nur Konsolen-Ausgabe)
9. **self_heal.py** - Automatische Fehlerbehebung in lgp.txt und Workflows

### Gemeinsame Muster:

- Alle Skripte verwenden `Path` für Dateipfade
- Die meisten Skripte schreiben Reports in Markdown-Format
- Exit-Codes: `0` = Erfolg, `1` = Fehler
- Viele Skripte schreiben in `main/lgp.txt`
- AST-basierte Code-Analyse wird häufig verwendet

---

**Erstellt:** $(date)
**Stand:** Aktueller Zustand des main/ Verzeichnisses

