# АНАЛИЗ ПАЙПЛАЙНА STUDIOCORE V6

## Структура пайплайна (на основе диаграммы)

### INPUT LAYER
1. **INPUT TEXT** - Входной текст для анализа
2. **USER COMMANDS** - Парсинг пользовательских команд из текста
3. **ENGINES & SYSTEMS** - Инициализация всех движков и систем

### MICRO LAYER (Микро-анализ)
Базовый анализ текста на уровне токенов и фраз:

1. **STRUCTURE** - Парсинг структуры текста (секции, маркеры)
2. **TOKENIZATION** - Разбиение текста на токены и предложения
3. **SENTIMENT** - Начальный анализ эмоций (базовый sentiment)
4. **COLOR PALETTE** - Определение цветовой палитры по эмоциям
5. **TLP & RDE** - Анализ Truth/Love/Pain и Resonance/Dynamics/Entropy
6. **MUSICAL CUES** - Извлечение музыкальных подсказок (BPM, тональность)

**Реализация:**
- `TextStructureEngine.auto_section_split()` - STRUCTURE
- `text_utils._words()`, `text_utils._split_sentences()` - TOKENIZATION
- `AutoEmotionalAnalyzer.analyze()` - SENTIMENT
- `ColorEmotionEngine.assign_color_by_emotion()` - COLOR PALETTE
- `TruthLovePainEngine.analyze()`, `ResonanceDynamicsEngine` - TLP & RDE
- `BPMEngine.text_bpm_estimation()`, `ToneSyncEngine.detect_key()` - MUSICAL CUES

### MESO LAYER (Мезо-анализ)
Анализ по секциям текста:

1. **SENTIMENT** - Анализ эмоций по секциям
2. **COLOR SECTION** - Цветовые профили для каждой секции
3. **GENRES SECTION** - Определение жанров для каждой секции

**Реализация:**
- `SectionIntelligenceEngine.analyze()` - SENTIMENT по секциям
- `ColorEmotionEngine.generate_color_wave()` - COLOR SECTION
- `GenreWeightsEngine.infer_genre()` - GENRES SECTION

### MACRO LAYER (Макро-анализ)
Глобальный анализ всего текста:

1. **TLP SONG** - TLP профиль для всего текста
2. **RDE SONG** - RDE метрики для всего текста
3. **COLOR SONG** - Глобальная цветовая волна
4. **EMOTION CURVE** - Кривая эмоций по всему тексту
5. **FINAL GENRES** - Финальное определение жанров
6. **SEMANTIC SPEED** - Семантическая скорость и фрактуры

**Реализация:**
- `TruthLovePainEngine.analyze()` - TLP SONG
- `ResonanceDynamicsEngine.calc_resonance()`, `ResonanceDynamicsEngine.calc_fracture()` - RDE SONG
- `ColorEngineAdapter.resolve_color_wave()` - COLOR SONG
- `EmotionEngine.emotion_intensity_curve()` - EMOTION CURVE
- `GenreWeightsEngine.infer_genre()` - FINAL GENRES
- `MeaningVelocityEngine.meaning_curve_generation()` - SEMANTIC SPEED

### MUSIC LAYER (Музыкальный слой)
Музыкальные параметры и стиль:

1. **REM** - Синхронизация ритмических и эмоциональных слоев
2. **ZERO PULSE** - Анализ тишины и пауз
3. **BPM ENGINE** - Расчет BPM и ритмических кривых
4. **TONALITY** - Определение тональности и ключей
5. **VOCALS** - Вокальные характеристики и техники
6. **INSTRUMENTATION** - Выбор инструментов
7. **MUSIC STYLE** - Финальный музыкальный стиль

**Реализация:**
- `REM_Synchronizer.align_layers_for_final_output()` - REM
- `ZeroPulseEngine.detect_zero_pulse()` - ZERO PULSE
- `BPMEngine.text_bpm_estimation()` - BPM ENGINE
- `ToneSyncEngine.detect_key()` - TONALITY
- `VocalEngine`, `get_vocal_for_section()` - VOCALS
- `InstrumentationEngine.instrument_selection()` - INSTRUMENTATION
- `StyleEngine.final_style_prompt_build()` - MUSIC STYLE

### OUTPUT LAYER (Выходной слой)
Финальная сборка результатов:

1. **ANNOTATIONS** - Аннотации для лирики (вокальные, дыхательные, тональные)
2. **PAYLOAD** - Полный payload с результатами анализа

**Реализация:**
- `LyricsAnnotationEngine.add_vocal_annotations()` (в `suno_annotations.py`) - ANNOTATIONS
- `FANFAnnotationEngine.build_annotations()` (в `fanf_annotation.py`) - ANNOTATIONS
- `_backend_analyze()` возвращает полный payload

## Связь с текущей реализацией

Все компоненты диаграммы реализованы в коде. Пайплайн соответствует структуре, показанной на диаграмме.

## Примечания

- Диаграмма содержит опечатки: "COLOR GECTION" → "COLOR SECTION", "GENERS SECTION" → "GENRES SECTION", "SMANNTIC SPEED" → "SEMANTIC SPEED"
- Все компоненты успешно интегрированы в `core_v6.py` через метод `_backend_analyze()`

