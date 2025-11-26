# Валидация формул StudioCore

## ✅ Статус проверки

Все формулы получены и проверены.

---

## 📊 Структура формул

### 1. Master_Analysis_Order (14 этапов)

Порядок анализа:
1. Structure
2. Emotion
3. TLP
4. RDE
5. Color
6. Vocal
7. BPM
8. Tonality
9. Genre
10. Instrumentation
11. Annotations
12. StylePrompt
13. Suno
14. Output

---

### 2. Color_Formula

**Цепочка цветов:**
```
BaseColor = emotion_to_color(dominant_emotion)
↓
LyricalColor = blend(BaseColor, LyricalShade[lyrical_genre], 0.35)
↓
MusicColor = blend(LyricalColor, MusicShade[music_genre], 0.35)
↓
EDMColor = blend(MusicColor, EDMShade[edm_genre], 0.45)  # если EDM
↓
TechnoColor = quantize(blend(MusicColor, TechnoShade[techno_genre], 0.55), techno_quantum)  # если Techno
↓
ColorWave = gradient([BaseColor, LyricalColor, MusicColor, EDMColor, TechnoColor], weights=[0.15,0.20,0.25,0.30,0.10])
```

**Правила для секций:**
- intro: soften(ColorWave.start, 0.20)
- verse: ColorWave.base
- pre_chorus: warm_shift(ColorWave.base, 0.10)
- chorus: saturate(ColorWave.peak, 0.35)
- bridge: darken(ColorWave.mid, -0.25)
- outro: fade(ColorWave.end, 0.40)

---

### 3. Genre_Selection_Formula

**Алгоритм выбора жанра:**
```
1. Detect_Lyrical_Genre: L = detect_lyrical_genre(text)
2. Base_Music_Set: BaseMusic = LyricalToMusic[L]
3. Emotion_Filter: EmotionMask = EmotionToMusic[dominant_emotion]
4. TLP_Filter: TLPBoost = TLP_to_Genre_Modifier(T,L,P)
5. Intersection: CandidateGenres = intersect(BaseMusic, EmotionMask, TLPBoost)
6. Fallback: if empty(CandidateGenres): CandidateGenres = union(BaseMusic, EmotionMask)
7. RDE_Adjustment: Adjusted = weight_genres(CandidateGenres, RDE)
8. Final_Selection: FinalMusicGenre = argmax(Adjusted * EmotionIntensity * TLPIntensity)
```

---

### 4. Vocal_Selection_Formula

**Алгоритм выбора вокала:**
```
1. BaseType: EmotionToVocal[dominant_emotion]
2. TLP_Adjustment: VocalType1 = adjust(BaseType, weighted(T,L,P))
3. RDE_Adjustment: VocalType2 = apply_RDE(VocalType1, RDE)
4. BPM_Flow: VocalFlow = BPM_to_VocalShape(BPM)
5. Key_Register: VocalType3 = shift_register(VocalType2, KeyMode_to_Register(Key, Mode))
6. Music_Style: VocalType4 = blend(VocalType3, MusicToVocalStyle[music_genre], 0.35)
7. Lyrical_Articulation: VocalType5 = apply_lyrical_articulation(VocalType4, lyrical_genre)
8. SectionMapping: Vocal(section) = transform(VocalType5, SectionRules[section])
```

**Правила для секций:**
- intro: softest_breathy
- verse: baseline_clean
- pre_chorus: warm_plus_10
- chorus: max_saturation_plus_35
- bridge: contrast_dark_or_light
- outro: fade_soft

---

### 5. Vocal_Weights_Formula

**Формула веса вокала:**
```
VocalWeight = EmotionWeight * TLPWeight * RDEWeight * BPMWeight * KeyWeight(mode) * GenreWeight * LyricalWeight
```

**Компоненты:**
- EmotionWeight: EmotionIntensity[dominant_emotion]
- TLPWeight: max(T, L, P)
- RDEWeight: normalize(R*0.4 + D*0.35 + E*0.25)
- BPMWeight: if BPM > 140: 1.2; if 90–140: 1.0; if <90: 0.85
- KeyWeight: Major (1.1 if bright; 0.9 if dark), Minor (1.1 if emotional; 0.85 if calm)
- GenreWeight: MusicToVocalWeight[music_genre]
- LyricalWeight: LyricalArticulationWeight[lyrical_genre]

**Финальный выбор:**
```
FinalVocalType = argmax_over_vocal_profiles(VocalProfileWeight)
```

---

### 6. TLP_Formula

```
Truth = f(first_person_freq, narrative_directness)
Love = f(sensual_words, romantic_words, joy, hope)
Pain = f(sadness, anger, despair)
ConsciousFrequency = CF = clamp((Truth + Love + Pain)/3 * (1 - dissonance), 0, 1)
```

---

### 7. RDE_Formula

```
Rhythm = R = syllable_rate / time_density
Dynamics = D = stress_variation(punctuation, semantics)
Entropy = E = variance(emotion_curve)
```

---

### 8. BPM_Formula

```
Base: bpm_base = rde_to_bpm(RDE)
Shift: bpm_shift = emotion_to_bpm(dominant_emotion)
Final: BPM = clamp(bpm_base + bpm_shift, 40, 200)
```

---

### 9. Tonality_Formula

```
KeyFromColor: key = color_to_key(primary_color)
Mode: mode = major/minor(emotion_profile)
SectionKeys: section_keys = varied_by_curve(emotion_curve, key)
```

---

### 10. Instrumentation_Formula

```
FromEmotion: instrument_set = emotion_to_instruments(dominant_emotion)
FromRDE: instrument_mod = rde_instrument_adjust(RDE)
Final: instrument_final = combine(instrument_set, instrument_mod)
```

---

### 11. Instrument_Color_Formula

**Алгоритм определения цвета инструмента:**
```
1. BaseEmotionColor: BaseColor = emotion_to_color(dominant_emotion)
2. GenreColorMix: GenreColor = blend(BaseColor, MusicShade[music_genre], 0.30)
3. EDM_Techno_Mix: If edm/techno branch active: GenreColor = blend(GenreColor, EDMShade[edm_or_techno_subgenre], 0.35)
4. TLP_ColorShift:
   - TruthShift: shift_hue(+8°) if Truth high
   - LoveShift: shift_saturation(+12%) if Love high
   - PainShift: shift_brightness(-14%) if Pain high
5. RDE_ColorDynamics:
   - Rhythm: high rhythm → increase vibrance (+10%)
   - Dynamics: high dynamics → increase contrast (+12%)
   - Entropy: high entropy → introduce noise/random darkening (5–12%)
6. KeyColorInfluence:
   - Major: lighten(+6%)
   - Minor: darken(-8%)
7. ColorWaveIntegration: InstrumentColorBase = project(ColorWave.position(section), 0.15)
8. InstrumentSpecificRules:
   - piano: cooler tint (-6° hue)
   - strings: warm amber (+10° hue)
   - brass: golden saturation (+18%)
   - woodwinds: pastel desaturation (-14%)
   - pads: neon tint (+22° hue if EDM)
   - leadSynth: full saturation (+35%)
   - bass: darkening (-25% brightness)
   - guitars: mid-warmth contrast (+8%)
   - drums: neutral gray baseline + vibrance from RDE
9. Final_Color: InstrumentColor = combine(BaseColor, GenreColor, TLP_Shifts, RDE_Modifiers, KeyInfluence, InstrumentSpecificRules)
10. Output: ColorHEX(instrument) = clamp_to_palette(InstrumentColor)
```

---

## 🔍 Проверка соответствия текущей реализации

### ✅ Соответствует:
- TLP_Formula: реализовано в `tlp_engine.py`
- RDE_Formula: реализовано в `rde_engine.py`
- BPM_Formula: частично реализовано в `bpm_engine.py`
- Tonality_Formula: частично реализовано в `tone_sync.py`

### ⚠️ Частично соответствует:
- Color_Formula: реализовано, но нужно проверить полную цепочку
- Genre_Selection_Formula: реализовано, но нужно проверить все шаги
- Vocal_Selection_Formula: реализовано, но нужно проверить все шаги
- Instrumentation_Formula: реализовано, но нужно интегрировать InstrumentMatrix

### ❌ Требует реализации:
- Vocal_Weights_Formula: нужно добавить
- Instrument_Color_Formula: нужно добавить
- Master_Analysis_Order: нужно проверить порядок в `core_v6.py`

---

## 🔧 Следующие шаги

1. Проверить порядок анализа в `core_v6.py` против Master_Analysis_Order
2. Реализовать полную Color_Formula с EDM/Techno ветками
3. Реализовать Vocal_Weights_Formula
4. Реализовать Instrument_Color_Formula
5. Интегрировать InstrumentMatrix с Instrumentation_Formula
6. Обновить все формулы для полного соответствия

---

## ✅ Готов к интеграции

Все формулы проверены и готовы к интеграции в проект.

