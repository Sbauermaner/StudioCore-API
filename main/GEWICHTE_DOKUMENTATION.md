# Dokumentation der Gewichte - Alle Prozesse

Vollständige Übersicht aller Gewichte (Weights) die in verschiedenen Prozessen des StudioCore-Systems verwendet werden.

---

## 1. Algorithmus-Gewichte (ALGORITHM_WEIGHTS)

**Datei:** `studiocore/config.py`  
**Verwendung:** Zentrale Konfiguration für Algorithmus-Gewichtungen

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `tlp_truth_weight` | 0.4 | Gewicht für Truth-Komponente im TLP-Engine |
| `tlp_love_weight` | 0.3 | Gewicht für Love-Komponente im TLP-Engine |
| `tlp_pain_weight` | 0.5 | Gewicht für Pain-Komponente im TLP-Engine |
| `road_narrative_cf_weight` | 0.25 | Gewicht für Conscious Frequency in Road Narrative |
| `road_narrative_sorrow_weight` | 0.25 | Gewicht für Sorrow in Road Narrative |
| `road_narrative_determination_weight` | 0.20 | Gewicht für Determination in Road Narrative |
| `rde_resonance_smoothing` | 0.4 | Glättungsfaktor für RDE Resonance bei niedrigen Emotionen |
| `rde_fracture_smoothing` | 0.3 | Glättungsfaktor für RDE Fracture bei niedrigen Emotionen |
| `rde_entropy_smoothing` | 0.7 | Glättungsfaktor für RDE Entropy bei niedrigen Emotionen |
| `rage_anger_threshold` | 0.22 | Schwellenwert für Rage/Anger-Erkennung |
| `rage_tension_threshold` | 0.25 | Schwellenwert für Rage/Tension-Erkennung |
| `epic_threshold` | 0.35 | Schwellenwert für Epic-Erkennung |
| `default_section_intensity` | 0.5 | Standard-Intensität für Sektionen |
| `default_confidence` | 0.5 | Standard-Konfidenz-Wert |

---

## 2. Genre-Gewichte (GENRE_WEIGHTS)

**Datei:** `studiocore/config.py`  
**Verwendung:** Genre-spezifische Gewichtungen für verschiedene Features

### 2.1 Semantic Aggression

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `anger_multiplier` | 0.4 | Multiplikator für Anger-Erkennung |
| `conflict_base` | 1.0 | Basis-Konflikt-Wert |

### 2.2 Power Vector

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `bpm_divisor` | 180.0 | Divisor für BPM-Berechnung |
| `intensity_multiplier` | 0.3 | Multiplikator für Intensität |

### 2.3 Edge Factor

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `anger_multiplier` | 0.6 | Multiplikator für Anger |
| `tone_intense_boost` | 0.3 | Boost für intensive Töne |
| `tone_balanced_boost` | 0.15 | Boost für ausgewogene Töne |

### 2.4 Rhythm Density

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `bpm_divisor` | 200.0 | Divisor für BPM-Berechnung |

### 2.5 Narrative Pressure

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `fracture_multiplier` | 0.1 | Multiplikator für Fracture-Erkennung |

### 2.6 Poetic Density

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `imagery_multiplier` | 2.2 | Multiplikator für Bildsprache |
| `punctuation_multiplier` | 0.4 | Multiplikator für Interpunktion |
| `long_line_multiplier` | 0.3 | Multiplikator für lange Zeilen |
| `motif_multiplier` | 0.1 | Multiplikator für Motive |

### 2.7 Swing Ratio

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `command_boost` | 0.25 | Boost für Command-Erkennung |
| `poly_variance_divisor` | 40.0 | Divisor für Poly-Varianz |
| `keyword_weight` | 0.6 | Gewicht für Keywords |
| `variance_weight` | 0.4 | Gewicht für Varianz |

### 2.8 Jazz Complexity

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `palette_weight` | 0.35 | Gewicht für Palette |
| `modal_weight` | 0.35 | Gewicht für Modalität |
| `text_weight` | 0.3 | Gewicht für Text |

### 2.9 Electronic Pressure

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `palette_weight` | 0.5 | Gewicht für Palette |
| `text_weight` | 0.3 | Gewicht für Text |
| `bpm_weight` | 0.2 | Gewicht für BPM |

### 2.10 Comedy Factor

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `hits_weight` | 0.6 | Gewicht für Hits |
| `blob_weight` | 0.15 | Gewicht für Blob |
| `laughter_weight` | 0.1 | Gewicht für Laughter |

### 2.11 Gothic Factor

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `minor_lumen_multiplier` | 0.1 | Multiplikator für Minor Lumen |

### 2.12 Dramatic Weight

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `tension_weight` | 0.5 | Gewicht für Spannung |
| `gradient_weight` | 0.3 | Gewicht für Gradient |
| `pressure_weight` | 0.2 | Gewicht für Druck |

---

## 3. GenreWeightsEngine - Domain-Feature-Gewichte

**Datei:** `studiocore/genre_weights.py`  
**Verwendung:** Gewichtungen für Features pro Domain

### 3.1 Hard Domain

**Statistik:** Major: 11, Minor: 63, BPM: 128.8 (schnell, überwiegend minor)

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `sai` | 0.24 | Semantic Aggression Index |
| `power` | 0.24 | Power-Vektor |
| `rhythm_density` | 0.18 | Rhythm-Dichte |
| `edge` | 0.18 | Edge-Faktor |
| `hl_minor` | 0.16 | Harmonic Level Minor (erhöht: 63 vs 11) |
| `structure_tension` | 0.12 | Struktur-Spannung |

### 3.2 Electronic Domain

**Statistik:** Major: 21, Minor: 14, BPM: 134.9 (sehr schnell, gemischt)

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `electronic_pressure` | 0.26 | Electronic Pressure |
| `rhythm_density` | 0.22 | Rhythm-Dichte |
| `power` | 0.18 | Power-Vektor |
| `structure_tension` | 0.12 | Struktur-Spannung |
| `hl_minor` | 0.11 | Harmonic Level Minor |
| `hl_major` | 0.11 | Harmonic Level Major (ausgewogen: 21 major, 14 minor) |
| `cinematic_spread` | 0.10 | Cinematic Spread |
| `poetic_density` | -0.14 | Poetic Density (negativ: Elektronik sollte nicht lyrisch sein) |
| `lyric_form_weight` | -0.16 | Lyric Form Weight (negativ) |

### 3.3 Jazz Domain

**Statistik:** Major: 20, Minor: 0, BPM: 116.8 (mittel, nur major)

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `jazz_complexity` | 0.28 | Jazz-Komplexität |
| `swing_ratio` | 0.24 | Swing-Ratio |
| `rhythm_density` | 0.16 | Rhythm-Dichte |
| `hl_minor` | 0.08 | Harmonic Level Minor (reduziert: nur major) |
| `hl_major` | 0.20 | Harmonic Level Major (erhöht: nur major) |
| `emotional_gradient` | 0.12 | Emotional Gradient |

### 3.4 Lyrical Domain

**Statistik:** Major: 30, Minor: 6, BPM: 78.2 (langsam, überwiegend major)

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `narrative_pressure` | 0.24 | Narrative Pressure |
| `lyrical_emotion_score` | 0.30 | Lyrical Emotion Score (erhöht: Hauptmerkmal) |
| `emotional_gradient` | 0.18 | Emotional Gradient |
| `hl_major` | 0.16 | Harmonic Level Major (erhöht: 30 vs 6) |
| `hl_minor` | 0.08 | Harmonic Level Minor (reduziert) |
| `vocal_intention` | 0.14 | Vocal Intention |
| `poetic_density` | 0.20 | Poetic Density |
| `lyric_form_weight` | 0.24 | Lyric Form Weight (erhöht: wichtiges Merkmal) |
| `gothic_factor` | 0.04 | Gothic Factor (reduziert: nicht Hauptmerkmal) |
| `dramatic_weight` | 0.08 | Dramatic Weight |

### 3.5 Cinematic Domain

**Statistik:** Major: 1, Minor: 10, BPM: 80.0 (langsam, überwiegend minor)

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `cinematic_spread` | 0.30 | Cinematic Spread |
| `power` | 0.18 | Power-Vektor |
| `emotional_gradient` | 0.20 | Emotional Gradient |
| `structure_tension` | 0.16 | Struktur-Spannung |
| `hl_minor` | 0.18 | Harmonic Level Minor (erhöht: 10 vs 1) |
| `hl_major` | 0.06 | Harmonic Level Major (reduziert) |
| `dramatic_weight` | 0.20 | Dramatic Weight |
| `darkness_level` | 0.14 | Darkness Level |

### 3.6 Comedy Domain

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `comedy_factor` | 0.42 | Comedy Factor |
| `lyrical_emotion_score` | 0.22 | Lyrical Emotion Score |
| `narrative_pressure` | 0.22 | Narrative Pressure |
| `hl_major` | 0.12 | Harmonic Level Major |
| `vocal_intention` | 0.12 | Vocal Intention |

### 3.7 Soft Domain

**Statistik:** Major: 12, Minor: 1, BPM: 91.9 (mittel, überwiegend major)

| Feature | Gewicht | Beschreibung |
|---------|---------|--------------|
| `narrative_pressure` | 0.26 | Narrative Pressure |
| `emotional_gradient` | 0.24 | Emotional Gradient |
| `hl_major` | 0.22 | Harmonic Level Major (erhöht: 12 vs 1) |
| `hl_minor` | 0.04 | Harmonic Level Minor (reduziert) |
| `power` | 0.08 | Power-Vektor |
| `rhythm_density` | 0.08 | Rhythm-Dichte |
| `structure_tension` | 0.16 | Struktur-Spannung |
| `poetic_density` | 0.14 | Poetic Density |

### 3.8 Domain-Schwellenwerte (Thresholds)

| Domain | Schwellenwert | Beschreibung |
|--------|--------------|--------------|
| `hard` | 0.48 | Erhöht: strengere Auswahl für Hard-Genres |
| `electronic` | 0.46 | Leicht erhöht |
| `jazz` | 0.44 | Leicht reduziert: Jazz ist spezifischer |
| `lyrical` | 0.52 | Erhöht: Lyrik benötigt höheren Schwellenwert |
| `cinematic` | 0.50 | Unverändert |
| `comedy` | 0.38 | Reduziert: Comedy ist flexibler |
| `soft` | 0.50 | Unverändert |

---

## 4. GenreWeightsEngine - Genre-Profile-Gewichte

**Datei:** `studiocore/genre_weights.py`  
**Verwendung:** Gewichtungen für spezifische Genre-Profile

### 4.1 Баллада (Ballade)

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.35 | Gewicht für Struktur |
| `emotion_weight` | 0.40 | Gewicht für Emotion |
| `lexicon_weight` | 0.15 | Gewicht für Lexikon |
| `narrative_weight` | 0.10 | Gewicht für Narrative |

### 4.2 Ода (Ode)

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.30 | Gewicht für Struktur |
| `emotion_weight` | 0.35 | Gewicht für Emotion |
| `lexicon_weight` | 0.25 | Gewicht für Lexikon |
| `narrative_weight` | 0.10 | Gewicht für Narrative |

### 4.3 Сонет (Sonett)

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.45 | Gewicht für Struktur |
| `emotion_weight` | 0.30 | Gewicht für Emotion |
| `lexicon_weight` | 0.15 | Gewicht für Lexikon |
| `narrative_weight` | 0.10 | Gewicht für Narrative |

### 4.4 Притча (Parabel)

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.25 | Gewicht für Struktur |
| `emotion_weight` | 0.25 | Gewicht für Emotion |
| `lexicon_weight` | 0.20 | Gewicht für Lexikon |
| `narrative_weight` | 0.30 | Gewicht für Narrative |

### 4.5 Реп текст (Rap-Text)

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.20 | Gewicht für Struktur |
| `emotion_weight` | 0.40 | Gewicht für Emotion |
| `lexicon_weight` | 0.30 | Gewicht für Lexikon |
| `narrative_weight` | 0.10 | Gewicht für Narrative |

### 4.6 Spoken Word

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.20 | Gewicht für Struktur |
| `emotion_weight` | 0.45 | Gewicht für Emotion |
| `lexicon_weight` | 0.25 | Gewicht für Lexikon |
| `narrative_weight` | 0.10 | Gewicht für Narrative |

### 4.7 Верлибр (Freier Vers)

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `structure_weight` | 0.15 | Gewicht für Struktur |
| `emotion_weight` | 0.45 | Gewicht für Emotion |
| `lexicon_weight` | 0.25 | Gewicht für Lexikon |
| `narrative_weight` | 0.15 | Gewicht für Narrative |

---

## 5. LyricalEmotionEngine - Gewichte

**Datei:** `studiocore/lyrical_emotion.py`  
**Verwendung:** Gewichtungen für lyrische Emotion-Berechnung

| Gewicht | Wert | Beschreibung |
|---------|------|--------------|
| `rde` | 0.35 | Gewicht für RDE (Raw Dramatic Emotion) |
| `tlp` | 0.35 | Gewicht für TLP (Truth/Love/Pain) |
| `poetic_density` | 0.20 | Gewicht für Poetic Density |
| `emotional_gradient` | 0.10 | Gewicht für Emotional Gradient |

### 5.1 TLP-Skalar-Gewichte (innerhalb LyricalEmotionEngine)

| Komponente | Gewicht | Beschreibung |
|------------|---------|--------------|
| `truth` | 0.4 | Truth-Komponente im TLP-Skalar |
| `love` | 0.3 | Love-Komponente im TLP-Skalar |
| `pain` | 0.3 | Pain-Komponente im TLP-Skalar |

---

## 6. Interpunktions-Gewichte (PUNCT_WEIGHTS)

**Dateien:** `studiocore/emotion.py`, `studiocore/rhythm.py`  
**Verwendung:** Gewichtungen für Interpunktionszeichen

| Zeichen | Gewicht | Beschreibung |
|---------|---------|--------------|
| `!` | 0.6 | Ausrufezeichen (höchstes Gewicht) |
| `…` | 0.5 | Ellipse |
| `?` | 0.4 | Fragezeichen |
| `—` | 0.2 | Gedankenstrich |
| `:` | 0.15 | Doppelpunkt |
| `;` | 0.1 | Semikolon |
| `.` | 0.1 | Punkt |
| `, ` | 0.05 | Komma (niedrigstes Gewicht) |

---

## 7. Emoji-Gewichte (EMOJI_WEIGHTS)

**Datei:** `studiocore/emotion.py`  
**Verwendung:** Gewichtungen für Emojis

| Emoji | Gewicht | Beschreibung |
|-------|---------|--------------|
| `❤💔💖🔥😭😢✨🌌🌅🌙🌈☀⚡💫` | 0.5 | Alle Emojis haben einheitliches Gewicht von 0.5 |

---

## 8. Rhythm-Engine - Emotion-Gewichte

**Datei:** `studiocore/rhythm.py`  
**Verwendung:** Gewichtungen für Emotionen in BPM-Berechnung

### 8.1 Standard Emotion Weight

| Parameter | Standardwert | Beschreibung |
|-----------|--------------|--------------|
| `emotion_weight` | 0.3 | Standard-Gewicht für Emotionen in BPM-Berechnung |

### 8.2 TLP-Boost-Gewichte (in BPM-Berechnung)

| Emotion | Multiplikator | Basis | Beschreibung |
|---------|---------------|-------|--------------|
| `Pain` | 50 | `emotion_weight` | Pain-Boost für BPM |
| `Love` | 25 | `emotion_weight` | Love-Smoothing für BPM |
| `Truth` | 20 | `emotion_weight` | Truth-Drive für BPM |
| `Conscious Frequency` | 100 | `emotion_weight` | CF-Boost für BPM (bei CF > 0.8) |

---

## 9. EmotionProfile - Vector-Gewichte

**Datei:** `studiocore/emotion_profile.py`  
**Verwendung:** Gewichtungen für Emotion-Vektoren

| Attribut | Standardwert | Beschreibung |
|----------|--------------|--------------|
| `weight` | 1.0 | Standard-Gewicht eines Emotion-Vektors in Aggregation |

**Verwendung:**
- Gewichtete Aggregation von Emotion-Vektoren
- Berechnung: `sum(value * weight) / sum(weights)`
- Minimum: 0.0 (wird auf 0.0 begrenzt wenn negativ)

---

## 10. Color-to-Domain-Boost-Gewichte

**Datei:** `studiocore/genre_weights.py`  
**Verwendung:** Farb-basierte Domain-Boosts

### 10.1 Love-Farben → Lyrical

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#FF7AA2` | lyrical | 0.15 | love |
| `#FFC0CB` | lyrical | 0.12 | love_soft |
| `#FFB6C1` | lyrical | 0.12 | love_soft |
| `#FFE4E1` | lyrical | 0.12 | love_soft |
| `#C2185B` | lyrical | 0.18 | love_deep |
| `#880E4F` | lyrical | 0.18 | love_deep |

### 10.2 Pain/Gothic-Farben → Hard

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#DC143C` | hard | 0.12 | pain / crimson |
| `#2F1B25` | hard | 0.15 | pain |
| `#0A1F44` | hard | 0.15 | pain |
| `#2C1A2E` | hard | 0.18 | gothic_dark |
| `#1B1B2F` | hard | 0.18 | gothic_dark |
| `#000000` | hard | 0.20 | gothic_dark |
| `#111111` | hard | 0.16 | dark |
| `#8B0000` | hard | 0.18 | rage_extreme |

### 10.3 Truth-Farben → Lyrical/Cinematic

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#4B0082_lyrical` | lyrical | 0.15 | truth |
| `#6C1BB1` | lyrical | 0.15 | truth |
| `#5B3FA8` | lyrical | 0.15 | truth |
| `#AEE3FF` | cinematic | 0.12 | clear_truth |
| `#6DA8C8` | cinematic | 0.12 | cold_truth |

### 10.4 Joy-Farben → Electronic

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#FFD93D` | electronic | 0.15 | joy |
| `#FFD700` | electronic | 0.18 | joy_bright |
| `#FFFF00` | electronic | 0.18 | joy_bright |
| `#FFF59D` | electronic | 0.15 | joy_bright |

### 10.5 Peace-Farben → Soft

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#40E0D0` | soft | 0.15 | peace |
| `#E0F7FA` | soft | 0.12 | peace |
| `#9FD3FF` | soft | 0.12 | calm_flow |
| `#8FC1E3` | soft | 0.10 | calm |

### 10.6 Epic-Farben → Cinematic

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#8A2BE2` | cinematic | 0.20 | epic |
| `#4B0082_cinematic` | cinematic | 0.18 | epic (auch truth) |
| `#FF00FF` | cinematic | 0.18 | epic |

### 10.7 Nostalgia-Farben → Lyrical

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#D8BFD8` | lyrical | 0.12 | nostalgia |
| `#E6E6FA` | lyrical | 0.12 | nostalgia |
| `#C3B1E1` | lyrical | 0.12 | nostalgia |

### 10.8 Sorrow-Farben → Lyrical

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#3E5C82` | lyrical | 0.15 | sorrow |
| `#4A6FA5` | lyrical | 0.12 | sadness |
| `#596E94` | lyrical | 0.12 | melancholy |

### 10.9 Warm-Farben → Soft/Jazz

| Farbe | Domain | Boost | Beschreibung |
|-------|--------|-------|--------------|
| `#F5B56B` | soft | 0.12 | warm_pulse |
| `#F7B267` | soft | 0.10 | warmth |

---

## 11. Emotion-to-Domain-Boost-Gewichte

**Datei:** `studiocore/genre_weights.py`  
**Verwendung:** Emotion-basierte Domain-Boosts

| Emotion | Domain | Boost | Beschreibung |
|---------|--------|-------|--------------|
| `love` | lyrical | 0.20 | Love-Emotion |
| `love_soft` | lyrical | 0.18 | Soft Love |
| `love_deep` | lyrical | 0.22 | Deep Love |
| `pain` | hard | 0.18 | Pain-Emotion |
| `gothic_dark` | hard | 0.20 | Gothic Dark |
| `dark` | hard | 0.16 | Dark |
| `truth` | lyrical | 0.15 | Truth-Emotion |
| `joy` | electronic | 0.18 | Joy-Emotion |
| `joy_bright` | electronic | 0.20 | Bright Joy |
| `peace` | soft | 0.15 | Peace-Emotion |
| `calm_flow` | soft | 0.12 | Calm Flow |
| `epic` | cinematic | 0.20 | Epic-Emotion |
| `nostalgia` | lyrical | 0.12 | Nostalgia |
| `sorrow` | lyrical | 0.15 | Sorrow |
| `sadness` | lyrical | 0.12 | Sadness |
| `melancholy` | lyrical | 0.12 | Melancholy |
| `rage` | hard | 0.18 | Rage |
| `rage_extreme` | hard | 0.20 | Extreme Rage |
| `anger` | hard | 0.16 | Anger |

---

## 12. Domain-Korrektur-Gewichte

**Datei:** `studiocore/genre_weights.py`  
**Verwendung:** Zusätzliche Korrekturen basierend auf Features

### 12.1 Lyrical Domain

| Feature | Multiplikator | Beschreibung |
|---------|---------------|--------------|
| `poetic` | 0.22 | Poetic Density Multiplikator |
| `lyric` | 0.28 | Lyric Form Weight Multiplikator |

### 12.2 Cinematic Domain

| Feature | Multiplikator | Beschreibung |
|---------|---------------|--------------|
| `dramatic` | 0.18 | Dramatic Weight Multiplikator |
| `gothic` | 0.12 | Gothic Factor Multiplikator |

### 12.3 Electronic Domain (Subtraktion)

| Feature | Multiplikator | Beschreibung |
|---------|---------------|--------------|
| `poetic` | -0.28 | Poetic Density Subtraktion (Elektronik sollte nicht lyrisch sein) |
| `gothic` | -0.22 | Gothic Factor Subtraktion |
| `dramatic` | -0.12 | Dramatic Weight Subtraktion |

---

## 13. Section Intelligence - Packet-Gewichte

**Datei:** `studiocore/section_intelligence.py`  
**Verwendung:** Gewichtungen für Section-Packets

| Attribut | Beschreibung |
|----------|--------------|
| `packet.weight` | Gewicht eines Section-Packets (verwendet für Sortierung und Filterung) |
| **Schwellenwert** | `weight > 0.8` für hohe Priorität |
| **Verwendung** | Top 3 Packets nach Gewicht sortiert |

---

## 14. Vocal Techniques - Technik-Gewichte

**Datei:** `studiocore/vocal_techniques.py`  
**Verwendung:** Gewichtungen für Vokal-Techniken

| Parameter | Beschreibung |
|-----------|--------------|
| `weight * intensity` | Kombiniertes Gewicht für Technik-Auswahl |
| **Schwellenwert** | `weight * intensity >= 0.15` (Minimum für Technik-Auswahl) |

---

## 15. Hybrid Genre Engine - Signal-Gewichte

**Datei:** `studiocore/hybrid_genre_engine.py`  
**Verwendung:** Gewichtungen für Genre-Signale

### 15.1 Swing Ratio (aus GENRE_WEIGHTS)

| Gewicht | Wert | Verwendung |
|---------|------|------------|
| `command_boost` | 0.25 | Boost für Command-Erkennung |
| `keyword_weight` | 0.6 | Gewicht für Keywords in Folk Ballad |
| `keyword_weight * 0.5` | 0.3 | Folk Ballad Confidence-Boost |

### 15.2 Electronic Pressure (aus GENRE_WEIGHTS)

| Gewicht | Wert | Verwendung |
|---------|------|------------|
| `text_weight` | 0.3 | Gewicht für Text in Electronic/EDM |
| `text_weight * 0.83` | 0.249 | Hiphop/Rap Factor |
| `text_weight * 0.83` | 0.249 | EDM Factor |
| `text_weight * 0.83` | 0.249 | Cinematic/Epic Factor |

### 15.3 Dramatic Weight (aus GENRE_WEIGHTS)

| Gewicht | Wert | Verwendung |
|---------|------|------------|
| `tension_weight` | 0.5 | Schwellenwert für Top-Genre-Auswahl |

---

## 16. Adapter - Phrase-Gewichte

**Datei:** `studiocore/adapter.py`  
**Verwendung:** Gewichtungen für Phrasen

| Parameter | Beschreibung |
|-----------|--------------|
| `weight = len(letters) / len(phrase)` | Buchstaben-Dichte als Gewicht |
| **Schwellenwert** | `weight < 0.2` für Phrase-Filterung |

---

## 17. Logical Engines - Emotion-BPM-Gewichte

**Datei:** `studiocore/logical_engines.py`  
**Verwendung:** Gewichtungen für Emotion-zu-BPM-Mapping

| Parameter | Beschreibung |
|-----------|--------------|
| `emotions` | Dictionary mit Emotion-Gewichten |
| `shift = (weight - 0.3) * 40` | BPM-Shift basierend auf Gewicht |
| `weighted_sum = sum(mapping[emotion] * weight)` | Gewichtete Summe für BPM |
| `target_bpm = weighted_sum / total_weight` | Finaler BPM-Wert |

---

## Zusammenfassung der Gewichts-Kategorien

| Kategorie | Anzahl Gewichte | Hauptdatei |
|-----------|-----------------|------------|
| Algorithmus-Gewichte | 13 | `config.py` |
| Genre-Gewichte | 12 Gruppen | `config.py` |
| Domain-Feature-Gewichte | 7 Domains × ~6-10 Features | `genre_weights.py` |
| Genre-Profile-Gewichte | 7 Genres × 4 Features | `genre_weights.py` |
| Lyrical Emotion Gewichte | 4 | `lyrical_emotion.py` |
| TLP-Gewichte | 3 | `lyrical_emotion.py`, `config.py` |
| Interpunktions-Gewichte | 8 | `emotion.py`, `rhythm.py` |
| Emoji-Gewichte | 1 (einheitlich) | `emotion.py` |
| Rhythm Emotion Gewichte | 4 | `rhythm.py` |
| Color-to-Domain Boosts | ~30 Farben | `genre_weights.py` |
| Emotion-to-Domain Boosts | 19 Emotionen | `genre_weights.py` |
| Domain-Korrekturen | 3 Domains | `genre_weights.py` |

**Gesamt:** Über 200 verschiedene Gewichte und Multiplikatoren

---

## Gewichts-Bereiche

| Typ | Minimum | Maximum | Beschreibung |
|-----|---------|---------|--------------|
| **Normale Gewichte** | 0.0 | 1.0 | Positive Gewichte (meist 0.0-1.0) |
| **Negative Gewichte** | -0.5 | 0.5 | Für Subtraktion (z.B. poetic_density in electronic) |
| **Multiplikatoren** | 0.1 | 2.2 | Verschiedene Bereiche (z.B. imagery_multiplier: 2.2) |
| **Divisoren** | 40.0 | 200.0 | Für Division (z.B. bpm_divisor) |
| **Schwellenwerte** | 0.15 | 0.52 | Für Thresholds |
| **Boosts** | 0.10 | 0.28 | Für Domain-Boosts |

---

**Erstellt:** Aktueller Stand  
**Stand:** Alle Gewichte aus dem StudioCore-System

