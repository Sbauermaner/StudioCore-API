# АНАЛИЗ СИСТЕМЫ ВЕСОВ STUDIOCORE

## Структура весов (на основе диаграммы WEIGHT REGISTRY)

### 1. GENRES WEIGHTS

#### LYRICAL GENRES
- ballad, romantic, pastoral, haiku, epic, verse_table
- rock_poetry, spoken_word, triolet, quatrain, lyric
- blues_verse, hymn, pastoral_elegy, sonnet, rustic
- epistolary, poetry, elegy, gothic_poetry, free_verse
- sestina, protest_poetry, blank_verse, ode, tanka, rondeau

**Реализация:**
- `studiocore/genre_registry.py` - `GlobalGenreRegistry.lyrical_genres`
- `studiocore/genre_weights.py` - `GenreWeightsEngine.genre_profiles`

#### DRAMATIC GENRES
- dramatic, tragic, epic, cinematic

**Реализация:**
- `studiocore/genre_registry.py` - `GlobalGenreRegistry.musical_genres` (cinematic domain)
- `studiocore/genre_weights.py` - `domain_feature_weights["cinematic"]`

### 2. EMOTIONS WEIGHTS

#### Основные эмоции
- FEAR, SADNESS, ANGER, HOPE, JOY, PEACE

**Реализация:**
- `studiocore/emotion.py` - `AutoEmotionalAnalyzer.EMO_FIELDS`
- `studiocore/emotion_genre_matrix.py` - `compute_genre_bias()` для каждой эмоции

### 3. COLOR WEIGHTS

#### INFLUENCES
Цвета влияют на:
- Определение доменов (lyrical, hard, electronic, soft, cinematic)
- Выбор жанров
- TLP профили

**Реализация:**
- `studiocore/color_engine_adapter.py` - `EMOTION_COLOR_MAP`
- `studiocore/genre_weights.py` - цветовая коррекция в `score_domains()`
- `studiocore/core_v6.py` - передача `color_profile` в `feature_map`

### 4. TLP/RDE WEIGHTS

#### TLP (Truth, Love, Pain)
- TRUTH - исповедальность, откровенность
- LOVE - телесность, нежность, память тела
- PAIN - боль, горе, страдание

**Реализация:**
- `studiocore/tlp_engine.py` - `TruthLovePainEngine`
- `studiocore/config.py` - `TLP_CLAMP_MIN`, `TLP_CLAMP_MAX`

#### RDE (Rhythm, Dynamics, Entropy)
- RHYTHM - ритмические паттерны
- DYNAMICS - динамические изменения
- ENTROPY - энтропия/хаос

**Реализация:**
- `studiocore/rde_engine.py` - `ResonanceDynamicsEngine`
- `studiocore/core_v6.py` - использование RDE в `feature_map`

## Связи между весами (из диаграммы)

### Поток влияния:

```
TLP WEIGHTS
    ↓
COLOR WEIGHTS
    ↓
LYRICAL GENRES WEIGHTS
```

```
RDE WEIGHTS
    ↓
SENTIMENT WEIGHTS
    ↓
MUSICAL GENRES WEIGHTS
```

### Реализация связей:

1. **TLP → COLOR:**
   - `studiocore/core_v6.py` - `color_profile = color_engine.assign_color_by_emotion(emotion_profile)`
   - `studiocore/color_engine_adapter.py` - `ColorEngineAdapter.resolve_color_wave()` использует TLP

2. **COLOR → GENRES:**
   - `studiocore/genre_weights.py` - `score_domains()` использует `color_profile` для коррекции доменов
   - `studiocore/emotion_genre_matrix.py` - `compute_genre_bias()` учитывает цвета эмоций

3. **RDE → SENTIMENT:**
   - `studiocore/core_v6.py` - RDE метрики влияют на `emotion_profile`
   - `studiocore/rde_engine.py` - `ResonanceDynamicsEngine` вычисляет RDE для секций

4. **SENTIMENT → GENRES:**
   - `studiocore/emotion_genre_matrix.py` - `compute_genre_bias()` использует эмоции для определения жанров
   - `studiocore/genre_weights.py` - `infer_genre()` учитывает эмоциональные профили

## Интеграция весов в пайплайн

### Порядок применения весов:

1. **MICRO LAYER:**
   - TLP анализ → TLP WEIGHTS
   - RDE анализ → RDE WEIGHTS
   - Emotion анализ → EMOTIONS WEIGHTS

2. **MESO LAYER:**
   - Color по секциям → COLOR WEIGHTS
   - Genres по секциям → GENRES WEIGHTS

3. **MACRO LAYER:**
   - Финальные TLP/RDE → применение всех весов
   - Финальные Genres → комбинация всех весов

4. **MUSIC LAYER:**
   - Применение весов к BPM, Key, Vocals, Instruments

## Рекомендации

1. **Создать централизованный WeightRegistry:**
   - Объединить все веса в один класс
   - Обеспечить единообразный доступ к весам
   - Упростить обновление и синхронизацию весов

2. **Документировать зависимости:**
   - Явно описать, как TLP влияет на COLOR
   - Описать, как COLOR влияет на GENRES
   - Описать, как RDE влияет на SENTIMENT

3. **Валидация весов:**
   - Проверка диапазонов весов
   - Проверка согласованности между весами
   - Логирование применения весов

