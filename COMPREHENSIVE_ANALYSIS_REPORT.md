================================================================================
COMPREHENSIVE ANALYSIS REPORT - STUDIOCORE
================================================================================

## POTENTIAL_STATE_LEAK (157 Issues)

  [studiocore/adapter.py:21]
    Fehler: Viele Module-Level Variablen: log, noise_pattern, text, text, text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/app.py:37]
    Fehler: Viele Module-Level Variablen: input_data, core, result, out_path, text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/auto_integrator.py:92]
    Fehler: Viele Module-Level Variablen: required_dirs, cmd_parts, result, text, text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/bpm_engine.py:82]
    Fehler: Viele Module-Level Variablen: __all__, text_lines, total_syllables, total_words, avg_syllables_per_word...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/color_engine_adapter.py:154]
    Fehler: Viele Module-Level Variablen: key, hex_color, factor, rgb1, rgb2...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/config.py:21]
    Fehler: Viele Module-Level Variablen: logger, STUDIOCORE_VERSION, VERSION_LIMITS, DEFAULT_CONFIG, NEUTRAL_MOOD...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/consistency_v8.py:27]
    Fehler: Viele Module-Level Variablen: bpm, tlp, pain, truth, genre...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/core_v6.py:60]
    Fehler: Viele Module-Level Variablen: result, style, genre, core, test_text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/diagnostics_v8.py:21]
    Fehler: Viele Module-Level Variablen: SCHEMA_VERSION, base, base, runtime_ms, engine_name...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/dynamic_emotion_engine.py:67]
    Fehler: Viele Module-Level Variablen: __all__, AXES, text, emotion_scores, tlp_scores...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion.py:34]
    Fehler: Viele Module-Level Variablen: log, PUNCT_WEIGHTS, EMOJI_WEIGHTS, _EMOTION_MODEL_LOCK, __all__...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_curve.py:13]
    Fehler: Viele Module-Level Variablen: SECTION_ORDER, __all__, order_index, ordered, total...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_dictionary_extended.py:69]
    Fehler: Viele Module-Level Variablen: lowered, buckets, high_hits, medium_hits, low_hits...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_engine.py:302]
    Fehler: Viele Module-Level Variablen: vector, lower_text, total, weights, vector...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_genre_matrix.py:12]
    Fehler: Viele Module-Level Variablen: _GENRES, __all__, bias, vector, anger...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_map.py:35]
    Fehler: Viele Module-Level Variablen: r, g, b, brightness, r...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_profile.py:34]
    Fehler: Viele Module-Level Variablen: total_weight, t, l, p, v_mean...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/fanf_annotation.py:54]
    Fehler: Viele Module-Level Variablen: CHOIR_KEYWORDS, INTIMATE_KEYWORDS, analysis, emotion, bpm...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/frequency.py:67]
    Fehler: Viele Module-Level Variablen: BASE_HZ, MAX_MULT, s, base, phase...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/fusion_engine_v64.py:45]
    Fehler: Viele Module-Level Variablen: profile, legacy_bpm, locks, manual, manual_bpm...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  ... und 137 weitere Issues

## STATELESS_VIOLATION (1 Issues)

  [studiocore/core_v6.py:0]
    Fehler: _build_engine_bundle Methode fehlt
    Lösung: Implementiere _build_engine_bundle() für stateless Verhalten

================================================================================
ZUSAMMENFASSUNG
================================================================================
  Gesamt Issues: 158
  Nach Typ:
    - potential_state_leak: 157
    - stateless_violation: 1

⚠️  SYSTEM STATUS: ISSUES GEFUNDEN
================================================================================