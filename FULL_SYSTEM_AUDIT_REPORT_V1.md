================================================================================
FULL_SYSTEM_AUDIT_ALL_MODULES_V1 - REPORT
================================================================================

## DEPENDENCY GRAPH
Module: 69

## CYCLICAL DEPENDENCIES
  ⚠️  studiocore.emotion -> studiocore.tlp_engine -> studiocore.emotion

## ORPHAN MODULES
  ⚠️  studiocore.symbiosis_audit
  ⚠️  studiocore.logger
  ⚠️  studiocore.genre_routing_engine
  ⚠️  studiocore.emotion_map
  ⚠️  studiocore.hybrid_genre_engine
  ⚠️  studiocore.app
  ⚠️  studiocore.genre_universe_extended
  ⚠️  studiocore.ui_builder
  ⚠️  studiocore.genre_meta_matrix
  ⚠️  studiocore.fallback
  ⚠️  studiocore.auto_integrator
  ⚠️  studiocore.emotion_engine
  ⚠️  studiocore.emotion_dictionary_extended
  ⚠️  studiocore.spiritual_emotion_map
  ⚠️  studiocore.monolith_v4_3_1
  ⚠️  studiocore.logger_runtime
  ⚠️  studiocore.emotion_curve

## UNUSED MODULES
  ⚠️  studiocore.symbiosis_audit
  ⚠️  studiocore.logger
  ⚠️  studiocore.genre_routing_engine
  ⚠️  studiocore.emotion_map
  ⚠️  studiocore.hybrid_genre_engine
  ⚠️  studiocore.app
  ⚠️  studiocore.genre_universe_extended
  ⚠️  studiocore.ui_builder
  ⚠️  studiocore.genre_meta_matrix
  ⚠️  studiocore.style
  ⚠️  studiocore.fallback
  ⚠️  studiocore.auto_integrator
  ⚠️  studiocore.emotion_engine
  ⚠️  studiocore.emotion_dictionary_extended
  ⚠️  studiocore.spiritual_emotion_map
  ⚠️  studiocore.monolith_v4_3_1
  ⚠️  studiocore.logger_runtime
  ⚠️  studiocore.emotion_curve
  ⚠️  studiocore.vocals

## PIPELINE ISSUES
  ⚠️  universal_frequency_engine:
      - Engine-Modul universal_frequency_engine nicht gefunden
  ⚠️  hybrid_instrumentation_layer:
      - Engine-Modul hybrid_instrumentation_layer nicht gefunden
  ⚠️  neutral_mode_pre_finalizer:
      - Engine-Modul neutral_mode_pre_finalizer nicht gefunden

## LOGIC CONFLICTS
  ✅ Keine Logik-Konflikte gefunden

## EMOTION CONFLICTS
  ⚠️  [minor] Potentieller Konflikt zwischen epic und anderen Emotionen

## COLOR CONFLICTS
  ⚠️  [minor] Potentieller Konflikt zwischen genre_color und mood_color in color_engine_v3.py

## HYBRID GENRE CONFLICTS
  ✅ Keine Hybrid-Genre-Konflikte gefunden

## INSTRUMENTATION CONFLICTS
  ⚠️  [minor] Potentieller Konflikt zwischen Genres in hybrid_instrumentation: ['folk', 'edm', 'cinematic']
  ⚠️  [minor] Keine explizite Prioritätslogik in hybrid_instrumentation gefunden
  ⚠️  [minor] Keine explizite Prioritätslogik in instrument_dynamics gefunden

## CROSS-VERIFICATION ISSUES
  ✅ Keine Cross-Verification-Issues gefunden

## STATIC ANALYSIS ISSUES
  ✅ Keine statischen Analyse-Issues gefunden

## SEMANTIC TEST RESULTS
  ❌ low_emotion_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ high_anger_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ epic_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ hybrid_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ folk_ballad_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ electronic_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ nonsense_text: 'HybridGenreEngine' object has no attribute 'resolve'
  ❌ ultra_mixed_hybrid_text: 'HybridGenreEngine' object has no attribute 'resolve'

## SEVERITY RANKING
  🔴 CRITICAL: 0
  🟠 MAJOR: 1
  🟡 MINOR: 36

## RECOMMENDED PATCH PLAN
  1. Zyklische Abhängigkeiten auflösen
  2. Orphan-Module integrieren oder entfernen
  3. Ungenutzte Module entfernen oder dokumentieren
  4. Pipeline-Issues beheben

================================================================================