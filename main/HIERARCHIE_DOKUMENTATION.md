# Projekt-Hierarchie Dokumentation

Vollständige Dokumentation der Verzeichnisstruktur, Modul-Hierarchie und Abhängigkeiten des StudioCore-Projekts.

---

## 1. Verzeichnisstruktur

```
StudioCore-API/
├── 📁 studiocore/              # Haupt-Modul (Kern-Engine)
│   ├── __init__.py            # Modul-Loader & Entry Point
│   ├── core_v6.py             # V6 Facade (Haupt-Entry Point)
│   ├── monolith_v4_3_1.py     # Legacy Monolith (Fallback)
│   ├── fallback.py             # Fallback-Engine
│   │
│   ├── 📁 Emotion-Engines/
│   │   ├── emotion.py              # TruthLovePainEngine, AutoEmotionalAnalyzer
│   │   ├── emotion_engine.py       # EmotionEngineV64
│   │   ├── dynamic_emotion_engine.py
│   │   ├── emotion_curve.py
│   │   ├── emotion_dictionary_extended.py
│   │   ├── emotion_field.py
│   │   ├── emotion_genre_matrix.py
│   │   ├── emotion_map.py
│   │   ├── emotion_profile.py       # EmotionVector
│   │   ├── lyrical_emotion.py       # LyricalEmotionEngine
│   │   ├── multimodal_emotion_matrix.py
│   │   ├── spiritual_emotion_map.py
│   │   ├── tlp_engine.py            # Truth/Love/Pain Engine
│   │   └── rde_engine.py            # Resonance/Fracture/Entropy
│   │
│   ├── 📁 Genre-Engines/
│   │   ├── genre_colors.py
│   │   ├── genre_conflict_resolver.py
│   │   ├── genre_matrix_extended.py
│   │   ├── genre_meta_matrix.py
│   │   ├── genre_registry.py         # GlobalGenreRegistry
│   │   ├── genre_router.py
│   │   ├── genre_routing_engine.py
│   │   ├── genre_universe.py         # GenreUniverse
│   │   ├── genre_universe_adapter.py
│   │   ├── genre_universe_extended.py
│   │   ├── genre_universe_loader.py  # load_genre_universe()
│   │   ├── genre_weights.py          # GenreWeightsEngine
│   │   └── hybrid_genre_engine.py    # HybridGenreEngine
│   │
│   ├── 📁 Rhythm & BPM/
│   │   ├── rhythm.py                 # LyricMeter, RhythmEngine
│   │   ├── bpm_engine.py             # BPMEngine
│   │   └── frequency.py
│   │
│   ├── 📁 Tone & Style/
│   │   ├── tone.py                   # ToneSyncEngine
│   │   ├── tone_sync.py
│   │   ├── style.py                  # PatchedStyleMatrix
│   │   └── color_engine_v3.py
│   │
│   ├── 📁 Section & Structure/
│   │   ├── section_parser.py         # SectionParser
│   │   ├── section_intelligence.py
│   │   ├── section_merge_mode.py
│   │   ├── sections.py
│   │   └── structures.py
│   │
│   ├── 📁 Vocals & Instruments/
│   │   ├── vocals.py                 # VocalProfileRegistry
│   │   ├── vocal_techniques.py
│   │   ├── instrument.py
│   │   ├── instrument_dynamics.py
│   │   ├── hybrid_instrumentation.py
│   │   └── hybrid_instrumentation_layer.py
│   │
│   ├── 📁 Color & Visual/
│   │   ├── color_engine_adapter.py
│   │   └── color_engine_v3.py
│   │
│   ├── 📁 Fusion & Integration/
│   │   ├── fusion_engine_v64.py
│   │   ├── auto_integrator.py
│   │   └── adapter.py
│   │
│   ├── 📁 Configuration & Utils/
│   │   ├── config.py                 # ALGORITHM_WEIGHTS, GENRE_WEIGHTS
│   │   ├── text_utils.py             # normalize_text_preserve_symbols
│   │   ├── logger.py
│   │   ├── logger_runtime.py
│   │   └── ui_builder.py
│   │
│   ├── 📁 Diagnostics & Quality/
│   │   ├── diagnostics_v8.py
│   │   ├── consistency_v8.py
│   │   ├── integrity.py              # IntegrityScanEngine
│   │   ├── symbiosis_audit.py
│   │   └── rage_filter_v2.py
│   │
│   ├── 📁 Specialized Engines/
│   │   ├── epic_override.py
│   │   ├── neutral_mode.py
│   │   ├── neutral_mode_pre_finalizer.py
│   │   ├── universal_frequency_engine.py
│   │   └── logical_engines.py       # InstrumentationEngine, VocalEngine
│   │
│   ├── 📁 Annotations & Output/
│   │   ├── fanf_annotation.py        # FANF Annotations
│   │   ├── suno_annotations.py       # Suno Prompts
│   │   └── master_patch_v6_1.py
│   │
│   ├── 📁 User & Overrides/
│   │   └── user_override_manager.py
│   │
│   ├── 📁 Tests/
│   │   └── fake_users.json
│   │
│   └── 📁 Data/
│       └── emotion_model_v1.json
│
├── 📁 main/                    # Diagnostik & Wartung
│   ├── auto_log_cleaner.py
│   ├── auto_trigger.py
│   ├── comprehensive_analysis.py
│   ├── deep_scan_audit.py
│   ├── full_project_audit.py
│   ├── full_scan_audit.py
│   ├── full_system_diagnostics.py
│   ├── full_workflow_diagnostic_checker.py
│   ├── self_heal.py
│   ├── archive/
│   └── lgp.txt
│
├── 📁 tests/                   # Unit Tests
│   └── [33 Test-Dateien]
│
├── 📁 analysis_outputs/        # Analyse-Ergebnisse
│   └── last_analysis.json
│
├── 📁 flagged/                 # Flagged Files
│
├── 📄 api.py                   # FastAPI REST API
├── 📄 app.py                   # Gradio UI
├── 📄 core_v6.py               # (Legacy, siehe studiocore/core_v6.py)
│
├── 📄 requirements.txt          # Python Dependencies
├── 📄 requirements-dev.txt     # Dev Dependencies
├── 📄 Dockerfile               # Container-Konfiguration
├── 📄 studio_config.json       # Konfigurationsdatei
├── 📄 GENRE_DATABASE.json      # Genre-Datenbank
├── 📄 GENRE_DATABASE.md        # Genre-Dokumentation
├── 📄 openapi.json             # OpenAPI Spezifikation
├── 📄 openapi.yaml             # OpenAPI YAML
└── 📄 README.md                # Projekt-Dokumentation
```

---

## 2. Architektur-Schichten

### 2.1 Entry Point Layer (Einstiegsebene)

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Points                         │
├─────────────────────────────────────────────────────────┤
│  api.py (FastAPI)                                       │
│    └─> studiocore.core_v6.StudioCoreV6                  │
│                                                          │
│  app.py (Gradio UI)                                     │
│    └─> studiocore.core_v6.StudioCoreV6                  │
│                                                          │
│  studiocore/__init__.py (Loader)                        │
│    └─> get_core() → StudioCoreV6 / Monolith / Fallback │
└─────────────────────────────────────────────────────────┘
```

**Verantwortlichkeiten:**
- REST API Endpoints (FastAPI)
- Web UI (Gradio)
- Modul-Loader mit Fallback-Mechanismus

---

### 2.2 Core Facade Layer (Kern-Fassade)

```
┌─────────────────────────────────────────────────────────┐
│                    Core Facade                          │
├─────────────────────────────────────────────────────────┤
│  studiocore/core_v6.py                                  │
│    └─> StudioCoreV6                                      │
│         ├─> Wrapper um monolith_v4_3_1                  │
│         └─> HybridGenreEngine (optional)                │
│                                                          │
│  studiocore/monolith_v4_3_1.py                          │
│    └─> StudioCore (Legacy Monolith)                     │
│                                                          │
│  studiocore/fallback.py                                  │
│    └─> StudioCoreFallback (Minimal Fallback)            │
└─────────────────────────────────────────────────────────┘
```

**Verantwortlichkeiten:**
- Orchestrierung der Analyse-Pipeline
- Request-Scoped State Management
- Fallback-Mechanismus

---

### 2.3 Engine Layer (Engine-Ebene)

```
┌─────────────────────────────────────────────────────────┐
│                    Engines                              │
├─────────────────────────────────────────────────────────┤
│  Emotion Engines                                         │
│    ├─> TruthLovePainEngine (emotion.py)                 │
│    ├─> AutoEmotionalAnalyzer (emotion.py)               │
│    ├─> EmotionEngineV64 (emotion_engine.py)             │
│    ├─> LyricalEmotionEngine (lyrical_emotion.py)        │
│    ├─> RDE Engine (rde_engine.py)                       │
│    └─> TLP Engine (tlp_engine.py)                        │
│                                                          │
│  Genre Engines                                           │
│    ├─> HybridGenreEngine (hybrid_genre_engine.py)       │
│    ├─> GenreWeightsEngine (genre_weights.py)            │
│    ├─> GlobalGenreRegistry (genre_registry.py)          │
│    └─> GenreUniverse (genre_universe.py)                │
│                                                          │
│  Rhythm & BPM Engines                                    │
│    ├─> LyricMeter (rhythm.py)                            │
│    └─> BPMEngine (bpm_engine.py)                         │
│                                                          │
│  Tone & Style Engines                                    │
│    ├─> ToneSyncEngine (tone.py)                          │
│    └─> PatchedStyleMatrix (style.py)                    │
│                                                          │
│  Section Engines                                         │
│    └─> SectionParser (section_parser.py)                 │
│                                                          │
│  Vocals & Instruments                                    │
│    ├─> VocalProfileRegistry (vocals.py)                 │
│    └─> Logical Engines (logical_engines.py)              │
└─────────────────────────────────────────────────────────┘
```

**Verantwortlichkeiten:**
- Spezialisierte Analyse-Engines
- Stateless Verarbeitung
- Feature-Extraktion

---

### 2.4 Utility & Support Layer (Utility-Ebene)

```
┌─────────────────────────────────────────────────────────┐
│                    Utilities                            │
├─────────────────────────────────────────────────────────┤
│  Configuration                                           │
│    └─> config.py (ALGORITHM_WEIGHTS, GENRE_WEIGHTS)     │
│                                                          │
│  Text Processing                                        │
│    └─> text_utils.py (normalize, extract)               │
│                                                          │
│  Logging                                                 │
│    ├─> logger.py                                         │
│    └─> logger_runtime.py                                 │
│                                                          │
│  Diagnostics                                             │
│    ├─> diagnostics_v8.py                                │
│    ├─> integrity.py                                     │
│    └─> consistency_v8.py                                │
│                                                          │
│  Annotations                                             │
│    ├─> fanf_annotation.py                               │
│    └─> suno_annotations.py                               │
└─────────────────────────────────────────────────────────┘
```

**Verantwortlichkeiten:**
- Konfigurations-Management
- Text-Verarbeitung
- Logging & Diagnostik
- Output-Formatierung

---

## 3. Modul-Abhängigkeiten

### 3.1 Core-Abhängigkeiten

```
core_v6.py
  ├─> studiocore.__init__.py (get_core)
  ├─> studiocore.monolith_v4_3_1 (StudioCore)
  └─> studiocore.hybrid_genre_engine (HybridGenreEngine)

monolith_v4_3_1.py
  ├─> config.py (DEFAULT_CONFIG, load_config)
  ├─> text_utils.py (normalize_text_preserve_symbols)
  ├─> emotion.py (AutoEmotionalAnalyzer, TruthLovePainEngine)
  ├─> tone.py (ToneSyncEngine)
  ├─> vocals.py (VocalProfileRegistry)
  ├─> integrity.py (IntegrityScanEngine)
  ├─> rhythm.py (LyricMeter)
  └─> style.py (PatchedStyleMatrix)
```

### 3.2 Emotion-Engine-Abhängigkeiten

```
emotion.py
  ├─> config.py (ALGORITHM_WEIGHTS)
  └─> (selbstständig)

lyrical_emotion.py
  └─> (selbstständig, verwendet emotion.py Output)

rde_engine.py
  └─> (selbstständig)

tlp_engine.py
  └─> emotion_profile.py (EmotionVector)
```

### 3.3 Genre-Engine-Abhängigkeiten

```
hybrid_genre_engine.py
  ├─> config.py (GENRE_WEIGHTS, GENRE_THRESHOLDS)
  └─> (selbstständig)

genre_weights.py
  ├─> genre_registry.py (GlobalGenreRegistry)
  └─> genre_universe_loader.py (load_genre_universe)

genre_universe_loader.py
  └─> genre_universe.py (GenreUniverse)
```

### 3.4 Rhythm-Engine-Abhängigkeiten

```
rhythm.py
  ├─> text_utils.py (extract_sections)
  └─> (selbstständig)

bpm_engine.py
  └─> (selbstständig)
```

### 3.5 Section-Engine-Abhängigkeiten

```
section_parser.py
  └─> (selbstständig)

section_intelligence.py
  └─> structures.py
```

---

## 4. Loader-Hierarchie

### 4.1 Loader-Ordnung

```
get_core() Fallback-Kette:
  1. v6 (StudioCoreV6)          [Priority: 100]
     └─> Falls fehlgeschlagen ↓
  2. v5 (StudioCoreV5)          [Priority: 80]
     └─> Falls fehlgeschlagen ↓
  3. monolith (StudioCore)      [Priority: 60]
     └─> Falls fehlgeschlagen ↓
  4. fallback (StudioCoreFallback) [Priority: 0]
```

### 4.2 Loader-Status

```python
LOADER_GRAPH = {
    "v6": {
        "name": "StudioCoreV6",
        "loader": StudioCoreV6,
        "available": StudioCoreV6 is not None,
        "version": "v6.4 - maxi",
        "priority": 100,
    },
    "v5": {
        "name": "StudioCoreV5",
        "loader": _MONOLITH_V5,
        "available": _MONOLITH_V5 is not None,
        "version": MONOLITH_VERSION,
        "priority": 80,
    },
    "monolith": {
        "name": "StudioCore",
        "loader": _MONOLITH_CLS,
        "available": _MONOLITH_CLS is not None,
        "version": MONOLITH_VERSION,
        "priority": 60,
    },
    "fallback": {
        "name": "StudioCoreFallback",
        "loader": StudioCoreFallback,
        "available": True,
        "version": "fallback",
        "priority": 0,
    },
}
```

---

## 5. Analyse-Pipeline (Request-Flow)

### 5.1 Request-Flow-Diagramm

```
┌─────────────┐
│   Client    │
│  (API/UI)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  api.py / app.py│
│  (Entry Point)   │
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│  StudioCoreV6        │
│  (core_v6.py)        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  monolith_v4_3_1     │
│  (StudioCore)        │
└──────┬───────────────┘
       │
       ├─> SectionParser.parse()
       │
       ├─> TruthLovePainEngine.analyze()
       │
       ├─> AutoEmotionalAnalyzer.analyze()
       │
       ├─> LyricMeter.analyze()
       │
       ├─> BPMEngine.calculate()
       │
       ├─> ToneSyncEngine.sync()
       │
       ├─> HybridGenreEngine.resolve()
       │
       ├─> PatchedStyleMatrix.generate()
       │
       ├─> VocalProfileRegistry.select()
       │
       └─> IntegrityScanEngine.scan()
       │
       ▼
┌──────────────────────┐
│  Result Dictionary   │
│  (Structured Output)  │
└──────────────────────┘
```

### 5.2 Pipeline-Schritte

1. **Text Input** → `api.py` / `app.py`
2. **Core Initialization** → `StudioCoreV6.__init__()`
3. **Text Normalization** → `text_utils.normalize_text_preserve_symbols()`
4. **Section Parsing** → `SectionParser.parse()`
5. **Emotion Analysis** → `TruthLovePainEngine.analyze()`
6. **RDE Analysis** → `RDE Engine`
7. **BPM Calculation** → `BPMEngine.calculate()`
8. **Tone Sync** → `ToneSyncEngine.sync()`
9. **Genre Detection** → `HybridGenreEngine.resolve()`
10. **Style Generation** → `PatchedStyleMatrix.generate()`
11. **Vocal Selection** → `VocalProfileRegistry.select()`
12. **Integrity Check** → `IntegrityScanEngine.scan()`
13. **Annotation** → `FANF / Suno Annotations`
14. **Result Assembly** → Structured Dictionary

---

## 6. Modul-Gruppierungen

### 6.1 Emotion-Module

| Modul | Zweck | Abhängigkeiten |
|-------|-------|----------------|
| `emotion.py` | Truth/Love/Pain Engine | `config.py` |
| `emotion_engine.py` | EmotionEngineV64 | - |
| `lyrical_emotion.py` | Lyrical Emotion Kombination | - |
| `rde_engine.py` | Resonance/Fracture/Entropy | - |
| `tlp_engine.py` | TLP Engine | `emotion_profile.py` |
| `emotion_profile.py` | EmotionVector Datenstruktur | - |
| `emotion_curve.py` | Emotion-Kurven | - |
| `emotion_map.py` | Emotion-Mapping | - |
| `emotion_genre_matrix.py` | Emotion-Genre-Matrix | - |

### 6.2 Genre-Module

| Modul | Zweck | Abhängigkeiten |
|-------|-------|----------------|
| `hybrid_genre_engine.py` | Hybrid Genre Detection | `config.py` |
| `genre_weights.py` | GenreWeightsEngine | `genre_registry.py`, `genre_universe_loader.py` |
| `genre_registry.py` | GlobalGenreRegistry | - |
| `genre_universe.py` | GenreUniverse Datenstruktur | - |
| `genre_universe_loader.py` | GenreUniverse Loader | `genre_universe.py` |
| `genre_matrix_extended.py` | Genre Matrix | - |
| `genre_router.py` | Genre Routing | - |
| `genre_routing_engine.py` | Genre Routing Engine | - |

### 6.3 Rhythm & BPM Module

| Modul | Zweck | Abhängigkeiten |
|-------|-------|----------------|
| `rhythm.py` | LyricMeter, Rhythm Analysis | `text_utils.py` |
| `bpm_engine.py` | BPM Calculation | - |
| `frequency.py` | Frequency Analysis | - |

### 6.4 Tone & Style Module

| Modul | Zweck | Abhängigkeiten |
|-------|-------|----------------|
| `tone.py` | ToneSyncEngine | - |
| `tone_sync.py` | Tone Synchronization | - |
| `style.py` | PatchedStyleMatrix | - |
| `color_engine_v3.py` | Color Engine | - |
| `color_engine_adapter.py` | Color Engine Adapter | - |

### 6.5 Section & Structure Module

| Modul | Zweck | Abhängigkeiten |
|-------|-------|----------------|
| `section_parser.py` | Section Parsing | - |
| `section_intelligence.py` | Section Intelligence | `structures.py` |
| `section_merge_mode.py` | Section Merge | - |
| `sections.py` | Section Utilities | - |
| `structures.py` | Structure Data | - |

---

## 7. Konfigurations-Hierarchie

### 7.1 Konfigurationsquellen

```
1. studio_config.json (User Config)
   └─> load_config() in config.py
       │
2. config.py (Hardcoded Defaults)
   ├─> DEFAULT_CONFIG
   ├─> ALGORITHM_WEIGHTS
   └─> GENRE_WEIGHTS
       │
3. Environment Variables
   ├─> STUDIOCORE_FORCE_V5
   ├─> STUDIOCORE_MONOLITH
   └─> API_KEYS
```

### 7.2 Konfigurations-Priorität

1. **User Config** (`studio_config.json`) - Höchste Priorität
2. **Hardcoded Defaults** (`config.py`) - Fallback
3. **Environment Variables** - Runtime Override

---

## 8. Datenfluss-Hierarchie

### 8.1 Input → Processing → Output

```
Input (Text)
  │
  ├─> Text Normalization
  │   └─> text_utils.normalize_text_preserve_symbols()
  │
  ├─> Section Parsing
  │   └─> SectionParser.parse()
  │
  ├─> Feature Extraction
  │   ├─> Emotion Features (TLP, RDE)
  │   ├─> Rhythm Features (BPM, Meter)
  │   ├─> Genre Features (Domain, Genre)
  │   └─> Style Features (Tone, Color)
  │
  ├─> Engine Processing
  │   ├─> Emotion Engines
  │   ├─> Genre Engines
  │   ├─> Rhythm Engines
  │   └─> Style Engines
  │
  ├─> Fusion & Integration
  │   └─> fusion_engine_v64.py
  │
  ├─> Annotation
  │   ├─> FANF Annotations
  │   └─> Suno Prompts
  │
  └─> Output (Structured Dictionary)
      ├─> result
      ├─> style
      ├─> payload
      ├─> diagnostics
      └─> fanf
```

---

## 9. Test-Hierarchie

### 9.1 Test-Struktur

```
tests/
  ├─> test_*.py (33 Test-Dateien)
  │   ├─> test_emotion_*.py
  │   ├─> test_genre_*.py
  │   ├─> test_rhythm_*.py
  │   ├─> test_section_*.py
  │   └─> test_integration_*.py
  │
  └─> conftest.py (Pytest Configuration)

studiocore/tests/
  └─> fake_users.json (Test Data)
```

---

## 10. Wartungs-Hierarchie

### 10.1 Diagnostik-Tools

```
main/
  ├─> comprehensive_analysis.py    # Umfassende Code-Analyse
  ├─> deep_scan_audit.py          # Tiefe Code-Überprüfung
  ├─> full_project_audit.py       # Projektweite Validierung
  ├─> full_scan_audit.py          # Vollständiges Scannen
  ├─> full_system_diagnostics.py  # System-Diagnostik
  ├─> full_workflow_diagnostic_checker.py  # Workflow-Validierung
  ├─> auto_log_cleaner.py         # Log-Archivierung
  ├─> auto_trigger.py             # Automatischer Trigger
  └─> self_heal.py                # Selbstheilung
```

---

## 11. Abhängigkeits-Graph (Vereinfacht)

```
api.py / app.py
  └─> core_v6.py
      └─> __init__.py (get_core)
          └─> monolith_v4_3_1.py
              ├─> config.py
              ├─> text_utils.py
              ├─> emotion.py
              │   └─> config.py
              ├─> tone.py
              ├─> vocals.py
              ├─> integrity.py
              ├─> rhythm.py
              │   └─> text_utils.py
              └─> style.py

hybrid_genre_engine.py
  └─> config.py

genre_weights.py
  ├─> genre_registry.py
  └─> genre_universe_loader.py
      └─> genre_universe.py
```

---

## 12. Version-Hierarchie

### 12.1 Version-Informationen

| Komponente | Version | Status |
|------------|---------|--------|
| StudioCore | v6.4 - maxi | Aktuell |
| Monolith | v4.3.11 | Legacy (Fallback) |
| API | 1.0.0 | Aktuell |
| Fingerprint | StudioCore - FP - 2025 - SB - 9fd72e27 | Identifikation |

### 12.2 Version-Loader

```
DEFAULT_LOADER_ORDER = ("v6", "v5", "monolith", "fallback")
```

---

## 13. Stateless-Architektur

### 13.1 Request-Scoped State

```
Jeder Request:
  1. Neue Engine-Instanzen werden erstellt
  2. Keine persistente State-Variablen
  3. State wird nach Request gelöscht
  4. _build_engine_bundle() pro Request
```

### 13.2 State-Management

- **Module-Level State**: Vermieden (nur Konstanten)
- **Instance State**: Request-scoped
- **Global State**: Nur Loader-Status

---

## Zusammenfassung

**Haupt-Ebenen:**
1. **Entry Point Layer** - API/UI Entry Points
2. **Core Facade Layer** - Core Orchestrierung
3. **Engine Layer** - Spezialisierte Engines
4. **Utility Layer** - Support-Funktionen

**Kern-Module:**
- `core_v6.py` - Haupt-Facade
- `monolith_v4_3_1.py` - Legacy Engine
- `__init__.py` - Loader mit Fallback

**Wichtige Engines:**
- Emotion: `emotion.py`, `lyrical_emotion.py`, `rde_engine.py`
- Genre: `hybrid_genre_engine.py`, `genre_weights.py`
- Rhythm: `rhythm.py`, `bpm_engine.py`
- Style: `tone.py`, `style.py`

**Konfiguration:**
- `config.py` - Zentrale Konfiguration
- `studio_config.json` - User Config

---

**Erstellt:** Aktueller Stand  
**Stand:** Vollständige Projekt-Hierarchie

