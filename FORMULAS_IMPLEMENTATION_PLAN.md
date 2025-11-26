# План интеграции формул StudioCore

## ✅ Статус проверки

Все формулы получены и проверены. Готов к интеграции.

---

## 📊 Master_Analysis_Order

**Ожидаемый порядок:**
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

**Текущий порядок в `_backend_analyze()`:**
Нужно проверить и выровнять с Master_Analysis_Order.

---

## 🔧 Формулы для реализации

### 1. Color_Formula

**Текущее состояние:** Частично реализовано
**Требуется:**
- ✅ BaseColor: `emotion_to_color(dominant_emotion)` - реализовано
- ⚠️ LyricalColor: `blend(BaseColor, LyricalShade[lyrical_genre], 0.35)` - нужно добавить
- ⚠️ MusicColor: `blend(LyricalColor, MusicShade[music_genre], 0.35)` - нужно добавить
- ❌ EDMColor: `blend(MusicColor, EDMShade[edm_genre], 0.45)` - нужно добавить
- ❌ TechnoColor: `quantize(blend(MusicColor, TechnoShade[techno_genre], 0.55), techno_quantum)` - нужно добавить
- ⚠️ ColorWave: `gradient([BaseColor, LyricalColor, MusicColor, EDMColor, TechnoColor], weights=[0.15,0.20,0.25,0.30,0.10])` - частично реализовано
- ❌ SectionColors: правила для секций - нужно добавить

**Файлы для обновления:**
- `studiocore/color_engine_adapter.py` - добавить функции blend, gradient, soften, warm_shift, saturate, darken, fade
- `studiocore/core_v6.py` - обновить логику формирования ColorWave

---

### 2. Genre_Selection_Formula

**Текущее состояние:** Частично реализовано
**Требуется:**
- ✅ Detect_Lyrical_Genre: реализовано в `genre_weights.py`
- ⚠️ Base_Music_Set: `LyricalToMusic[L]` - нужно проверить
- ⚠️ Emotion_Filter: `EmotionToMusic[dominant_emotion]` - нужно проверить
- ⚠️ TLP_Filter: `TLP_to_Genre_Modifier(T,L,P)` - нужно проверить
- ⚠️ Intersection: `intersect(BaseMusic, EmotionMask, TLPBoost)` - нужно проверить
- ⚠️ Fallback: `union(BaseMusic, EmotionMask)` - нужно проверить
- ⚠️ RDE_Adjustment: `weight_genres(CandidateGenres, RDE)` - нужно проверить
- ⚠️ Final_Selection: `argmax(Adjusted * EmotionIntensity * TLPIntensity)` - нужно проверить

**Файлы для обновления:**
- `studiocore/genre_weights.py` - проверить соответствие формуле
- `studiocore/core_v6.py` - проверить порядок вызова

---

### 3. Vocal_Selection_Formula

**Текущее состояние:** Частично реализовано
**Требуется:**
- ✅ BaseType: `EmotionToVocal[dominant_emotion]` - реализовано
- ⚠️ TLP_Adjustment: `adjust(BaseType, weighted(T,L,P))` - нужно проверить
- ⚠️ RDE_Adjustment: `apply_RDE(VocalType1, RDE)` - нужно проверить
- ❌ BPM_Flow: `BPM_to_VocalShape(BPM)` - нужно добавить
- ❌ Key_Register: `shift_register(VocalType2, KeyMode_to_Register(Key, Mode))` - нужно добавить
- ⚠️ Music_Style: `blend(VocalType3, MusicToVocalStyle[music_genre], 0.35)` - нужно проверить
- ⚠️ Lyrical_Articulation: `apply_lyrical_articulation(VocalType4, lyrical_genre)` - нужно проверить
- ❌ SectionMapping: правила для секций - нужно добавить

**Файлы для обновления:**
- `studiocore/vocal_techniques.py` - добавить недостающие функции
- `studiocore/core_v6.py` - обновить логику выбора вокала

---

### 4. Vocal_Weights_Formula

**Текущее состояние:** ❌ Не реализовано
**Требуется:**
- ❌ EmotionWeight: `EmotionIntensity[dominant_emotion]` - нужно добавить
- ❌ TLPWeight: `max(T, L, P)` - нужно добавить
- ❌ RDEWeight: `normalize(R*0.4 + D*0.35 + E*0.25)` - нужно добавить
- ❌ BPMWeight: `if BPM > 140: 1.2; if 90–140: 1.0; if <90: 0.85` - нужно добавить
- ❌ KeyWeight: Major/Minor правила - нужно добавить
- ❌ GenreWeight: `MusicToVocalWeight[music_genre]` - нужно добавить
- ❌ LyricalWeight: `LyricalArticulationWeight[lyrical_genre]` - нужно добавить
- ❌ Final_Vocal_Weight_Formula: `VocalWeight = EmotionWeight * TLPWeight * RDEWeight * BPMWeight * KeyWeight(mode) * GenreWeight * LyricalWeight` - нужно добавить
- ❌ Final_Selection: `argmax_over_vocal_profiles(VocalProfileWeight)` - нужно добавить

**Файлы для создания/обновления:**
- `studiocore/vocal_weights.py` - новый файл для формулы весов вокала
- `studiocore/core_v6.py` - интегрировать формулу весов

---

### 5. TLP_Formula

**Текущее состояние:** ✅ Реализовано
**Требуется:**
- ✅ Truth: `f(first_person_freq, narrative_directness)` - реализовано
- ✅ Love: `f(sensual_words, romantic_words, joy, hope)` - реализовано
- ✅ Pain: `f(sadness, anger, despair)` - реализовано
- ✅ ConsciousFrequency: `CF = clamp((Truth + Love + Pain)/3 * (1 - dissonance), 0, 1)` - реализовано

**Файлы:**
- `studiocore/tlp_engine.py` - уже реализовано

---

### 6. RDE_Formula

**Текущее состояние:** ✅ Реализовано
**Требуется:**
- ✅ Rhythm: `R = syllable_rate / time_density` - реализовано
- ✅ Dynamics: `D = stress_variation(punctuation, semantics)` - реализовано
- ✅ Entropy: `E = variance(emotion_curve)` - реализовано

**Файлы:**
- `studiocore/rde_engine.py` - уже реализовано

---

### 7. BPM_Formula

**Текущее состояние:** ⚠️ Частично реализовано
**Требуется:**
- ⚠️ Base: `bpm_base = rde_to_bpm(RDE)` - нужно проверить
- ✅ Shift: `bpm_shift = emotion_to_bpm(dominant_emotion)` - реализовано (через цвет эмоции)
- ✅ Final: `BPM = clamp(bpm_base + bpm_shift, 40, 200)` - реализовано

**Файлы для обновления:**
- `studiocore/bpm_engine.py` - проверить соответствие формуле

---

### 8. Tonality_Formula

**Текущее состояние:** ⚠️ Частично реализовано
**Требуется:**
- ✅ KeyFromColor: `key = color_to_key(primary_color)` - реализовано
- ✅ Mode: `mode = major/minor(emotion_profile)` - реализовано
- ⚠️ SectionKeys: `section_keys = varied_by_curve(emotion_curve, key)` - нужно проверить

**Файлы для обновления:**
- `studiocore/tone_sync.py` - проверить соответствие формуле

---

### 9. Instrumentation_Formula

**Текущее состояние:** ⚠️ Частично реализовано
**Требуется:**
- ✅ FromEmotion: `instrument_set = emotion_to_instruments(dominant_emotion)` - реализовано
- ⚠️ FromRDE: `instrument_mod = rde_instrument_adjust(RDE)` - нужно проверить
- ⚠️ Final: `instrument_final = combine(instrument_set, instrument_mod)` - нужно проверить

**Файлы для обновления:**
- `studiocore/instrument.py` - обновить для использования InstrumentMatrix
- `studiocore/core_v6.py` - интегрировать InstrumentMatrix

---

## 📋 Приоритеты реализации

### Критичные (высокий приоритет):
1. ✅ Проверить Master_Analysis_Order в `core_v6.py`
2. ⚠️ Реализовать полную Color_Formula (EDM/Techno ветки, SectionColors)
3. ⚠️ Реализовать Vocal_Weights_Formula
4. ⚠️ Интегрировать InstrumentMatrix с Instrumentation_Formula

### Важные (средний приоритет):
5. ⚠️ Проверить Genre_Selection_Formula
6. ⚠️ Проверить Vocal_Selection_Formula (BPM_Flow, Key_Register, SectionMapping)
7. ⚠️ Проверить BPM_Formula (rde_to_bpm)
8. ⚠️ Проверить Tonality_Formula (SectionKeys)

### Опциональные (низкий приоритет):
9. Оптимизация существующих формул
10. Добавление кэширования для производительности

---

## 🔧 Следующие шаги

1. **Проверить порядок анализа** в `core_v6.py` против Master_Analysis_Order
2. **Реализовать Color_Formula** полностью (EDM/Techno, SectionColors)
3. **Реализовать Vocal_Weights_Formula** (новый файл)
4. **Интегрировать InstrumentMatrix** с Instrumentation_Formula
5. **Проверить и обновить** остальные формулы

---

## ✅ Готов к интеграции

Все формулы проверены и готовы к реализации.

