================================================================================
COMPREHENSIVE ANALYSIS REPORT - STUDIOCORE
================================================================================

## POTENTIAL_STATE_LEAK (171 Issues)

  [studiocore/adapter.py:21]
    Fehler: Viele Module-Level Variablen: log, noise_pattern, text, text, text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/app.py:37]
    Fehler: Viele Module-Level Variablen: input_data, core, result, out_path, text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/auto_integrator.py:89]
    Fehler: Viele Module-Level Variablen: required_dirs, cmd_parts, result, text, text...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/bpm_engine.py:80]
    Fehler: Viele Module-Level Variablen: __all__, text_lines, total_syllables, total_words, avg_syllables_per_word...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/color_engine_adapter.py:138]
    Fehler: Viele Module-Level Variablen: key, hex_color, factor, rgb1, rgb2...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/config.py:21]
    Fehler: Viele Module-Level Variablen: STUDIOCORE_VERSION, VERSION_LIMITS, DEFAULT_CONFIG, NEUTRAL_MOOD, NEUTRAL_COLOR_WAVE...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/consistency_v8.py:27]
    Fehler: Viele Module-Level Variablen: bpm, tlp, pain, truth, genre...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/core_v6.py:82]
    Fehler: Viele Module-Level Variablen: logger, _GENRE_UNIVERSE, _genre_universe_lock, _BRACKET_LINE_RE, STUDIOCORE_LICENSE_ENV...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/dynamic_emotion_engine.py:64]
    Fehler: Viele Module-Level Variablen: __all__, AXES, text, emotion_scores, tlp_scores...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion.py:35]
    Fehler: Viele Module-Level Variablen: log, PUNCT_WEIGHTS, EMOJI_WEIGHTS, __all__, TRUTH_WORDS...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_curve.py:13]
    Fehler: Viele Module-Level Variablen: SECTION_ORDER, __all__, order_index, ordered, total...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_dictionary_extended.py:69]
    Fehler: Viele Module-Level Variablen: lowered, buckets, high_hits, medium_hits, low_hits...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_engine.py:124]
    Fehler: Viele Module-Level Variablen: vector, lower_text, total, weights, vector...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_genre_matrix.py:12]
    Fehler: Viele Module-Level Variablen: _GENRES, __all__, bias, vector, anger...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_map.py:32]
    Fehler: Viele Module-Level Variablen: r, g, b, brightness, r...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/emotion_profile.py:34]
    Fehler: Viele Module-Level Variablen: total_weight, t, l, p, v_mean...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/fanf_annotation.py:53]
    Fehler: Viele Module-Level Variablen: CHOIR_KEYWORDS, INTIMATE_KEYWORDS, analysis, emotion, bpm...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/frequency.py:62]
    Fehler: Viele Module-Level Variablen: BASE_HZ, MAX_MULT, s, base, phase...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/fusion_engine_v64.py:47]
    Fehler: Viele Module-Level Variablen: profile, legacy_bpm, locks, manual, manual_bpm...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  [studiocore/genre_colors.py:217]
    Fehler: Viele Module-Level Variablen: genre_lower, genre_lower, hex_color, best_genre, best_distance...
    Lösung: Verschiebe Variablen in Klassen oder verwende lokale Variablen

  ... und 151 weitere Issues

================================================================================
ZUSAMMENFASSUNG
================================================================================
  Gesamt Issues: 171
  Nach Typ:
    - potential_state_leak: 171

⚠️  SYSTEM STATUS: ISSUES GEFUNDEN
================================================================================