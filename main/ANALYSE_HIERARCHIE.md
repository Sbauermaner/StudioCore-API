# Иерархия Анализа - Документация

Полная документация иерархии анализа текста в StudioCore: этапы, последовательность вызовов, зависимости и поток данных.

---

## 1. Общая Иерархия Анализа

```
┌─────────────────────────────────────────────────────────────┐
│                    УРОВЕНЬ 1: ВХОД                          │
│  api.py / app.py → core.analyze(text, preferred_gender)    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              УРОВЕНЬ 2: CORE FACADE                         │
│  StudioCoreV6.analyze() → monolith.analyze()                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│          УРОВЕНЬ 3: ПРЕДОБРАБОТКА ТЕКСТА                    │
│  1. normalize_text_preserve_symbols()                      │
│  2. extract_raw_blocks()                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│        УРОВЕНЬ 4: БАЗОВЫЙ АНАЛИЗ                            │
│  ├─> Emotion Analysis (emotion.analyze())                   │
│  ├─> Rhythm Analysis (rhythm.analyze())                     │
│  └─> Tone Detection (tone.detect_key())                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│      УРОВЕНЬ 5: УГЛУБЛЕННЫЙ АНАЛИЗ                          │
│  ├─> TLP Analysis (tlp.analyze())                          │
│  ├─> RDE Analysis (rde_engine)                             │
│  ├─> Genre Detection (hybrid_genre_engine.resolve())        │
│  └─> Section Analysis (_analyze_sections())                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│      УРОВЕНЬ 6: СТИЛЬ И ВОКАЛ                               │
│  ├─> Style Generation (style.build())                       │
│  ├─> Vocal Selection (vocals.select())                     │
│  └─> Semantic Layers (_build_semantic_layers())            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│      УРОВЕНЬ 7: ИНТЕГРАЦИЯ И ПРОВЕРКИ                       │
│  ├─> Integrity Scan (integrity.scan())                     │
│  ├─> Frequency Check (freq.check())                         │
│  └─> Safety Check (safety.check())                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│      УРОВЕНЬ 8: АННОТАЦИЯ И ФОРМАТИРОВАНИЕ                  │
│  ├─> Text Annotation (annotate_text())                      │
│  ├─> FANF Annotation (fanf_annotation)                     │
│  └─> Suno Prompts (suno_annotations)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│      УРОВЕНЬ 9: РЕЗУЛЬТАТ                                   │
│  Structured Dictionary mit allen Ergebnissen               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Детальная Последовательность Анализа

### 2.1 Этап 1: Инициализация и Вход

```python
# api.py / app.py
core = StudioCoreV6()  # Инициализация
result = core.analyze(
    text="...",
    preferred_gender="auto",
    version=None,
    semantic_hints=None
)
```

**Иерархия вызовов:**
```
api.py / app.py
  └─> StudioCoreV6.__init__()
      ├─> get_core() [из __init__.py]
      │   └─> Fallback-Kette: v6 → v5 → monolith → fallback
      └─> HybridGenreEngine() [optional]
```

---

### 2.2 Этап 2: Предобработка Текста

**Метод:** `monolith_v4_3_1.py → analyze()`

```python
# Шаг 1: Нормализация текста
raw = normalize_text_preserve_symbols(text)
  └─> text_utils.normalize_text_preserve_symbols()
      ├─> Удаление лишних пробелов
      ├─> Сохранение специальных символов
      └─> Нормализация кодировки

# Шаг 2: Извлечение блоков
text_blocks = extract_raw_blocks(raw)
  └─> text_utils.extract_raw_blocks()
      ├─> Разделение по пустым строкам
      ├─> Обработка секций [Verse], [Chorus], etc.
      └─> Возврат списка блоков
```

**Иерархия:**
```
analyze()
  ├─> normalize_text_preserve_symbols()
  │   └─> text_utils.normalize_text_preserve_symbols()
  └─> extract_raw_blocks()
      └─> text_utils.extract_raw_blocks()
```

---

### 2.3 Этап 3: Базовый Эмоциональный Анализ

**Метод:** `self.emotion.analyze(raw)`

```python
emotions = self.emotion.analyze(raw)
  └─> AutoEmotionalAnalyzer.analyze(text)
      ├─> Построение базового эмоционального вектора
      ├─> Проекция на кластеры эмоций
      ├─> Определение доминирующей эмоции
      └─> Возврат словаря эмоций
```

**Внутренняя иерархия AutoEmotionalAnalyzer.analyze():**
```
AutoEmotionalAnalyzer.analyze()
  ├─> build_raw_emotion_vector()
  │   ├─> Анализ ключевых слов
  │   ├─> Анализ пунктуации (PUNCT_WEIGHTS)
  │   ├─> Анализ эмодзи (EMOJI_WEIGHTS)
  │   └─> Построение вектора базовых эмоций
  │
  ├─> project_to_clusters()
  │   ├─> Загрузка emotion_model_v1.json
  │   ├─> Проекция на кластеры
  │   └─> Нормализация значений
  │
  └─> Определение доминирующей эмоции
      └─> max(emotions.values())
```

**Зависимости:**
- `config.py` (ALGORITHM_WEIGHTS)
- `emotion_model_v1.json` (модель эмоций)
- `PUNCT_WEIGHTS`, `EMOJI_WEIGHTS` (веса)

---

### 2.4 Этап 4: Анализ Ритма и BPM

**Метод:** `self.rhythm.analyze(raw, emotions=emotions, tlp=None, cf=None)`

```python
rhythm_analysis = self.rhythm.analyze(
    raw,
    emotions=emotions,
    tlp=None,
    cf=None
)
  └─> LyricMeter.analyze(text, emotions, tlp, cf)
      ├─> Поиск BPM в заголовке [BPM: 120]
      ├─> Оценка BPM на основе текста
      ├─> Корректировка BPM на основе эмоций
      └─> Возврат rhythm_analysis
```

**Внутренняя иерархия LyricMeter.analyze():**
```
LyricMeter.analyze()
  ├─> Поиск header_bpm
  │   └─> HEADER_BPM_RE.search(text)
  │
  ├─> _density_bpm() [если header_bpm отсутствует]
  │   ├─> Анализ плотности текста
  │   ├─> Анализ пунктуации
  │   ├─> Учет эмоций (emotion_weight)
  │   └─> Расчет BPM
  │
  ├─> Корректировка на основе TLP
  │   ├─> Pain boost: pain * 50 * emotion_weight
  │   ├─> Love smoothing: love * 25 * emotion_weight
  │   └─> Truth drive: truth * 20 * emotion_weight
  │
  └─> Возврат {
        "global_bpm": bpm,
        "header_bpm": header_bpm,
        "estimated_bpm": estimated_bpm
      }
```

**Зависимости:**
- `emotions` (из этапа 3)
- `text_utils.extract_sections()` (для секционного анализа)
- `PUNCT_WEIGHTS` (веса пунктуации)

---

### 2.5 Этап 5: Определение Тональности

**Метод:** `self.tone.detect_key(raw)`

```python
tone_hint = self.tone.detect_key(raw)
  └─> ToneSyncEngine.detect_key(text)
      ├─> Поиск тональности в тексте
      ├─> Анализ эмоционального контекста
      └─> Возврат {"key": "C", ...}
```

**Внутренняя иерархия:**
```
ToneSyncEngine.detect_key()
  ├─> Поиск явных указаний тональности
  ├─> Анализ эмоций для определения тональности
  └─> Fallback на DEFAULT_CONFIG.FALLBACK_KEY
```

---

### 2.6 Этап 6: TLP Анализ (Truth/Love/Pain)

**Метод:** `self.tlp.analyze(raw)` [вызывается внутри других этапов]

```python
tlp = self.tlp.analyze(raw)
  └─> TruthLovePainEngine.analyze(text)
      ├─> Анализ ключевых слов Truth
      ├─> Анализ ключевых слов Love
      ├─> Анализ ключевых слов Pain
      ├─> Расчет Conscious Frequency (CF)
      └─> Возврат TLP профиля
```

**Внутренняя иерархия TruthLovePainEngine.analyze():**
```
TruthLovePainEngine.analyze()
  ├─> Поиск Truth слов
  │   └─> TRUTH_WORDS matching
  │
  ├─> Поиск Love слов
  │   └─> LOVE_WORDS matching
  │
  ├─> Поиск Pain слов
  │   └─> PAIN_WORDS matching
  │
  ├─> Расчет весов
  │   ├─> truth_weight = 0.4 (из ALGORITHM_WEIGHTS)
  │   ├─> love_weight = 0.3
  │   └─> pain_weight = 0.5
  │
  ├─> Расчет Conscious Frequency (CF)
  │   └─> Гармоническое среднее truth, love, pain
  │
  └─> Возврат {
        "truth": float,
        "love": float,
        "pain": float,
        "conscious_frequency": float,
        "dominant": "truth" | "love" | "pain"
      }
```

**Зависимости:**
- `config.py` (ALGORITHM_WEIGHTS: tlp_truth_weight, tlp_love_weight, tlp_pain_weight)
- Словари ключевых слов (TRUTH_WORDS, LOVE_WORDS, PAIN_WORDS)

---

### 2.7 Этап 7: Анализ Секций

**Метод:** `_analyze_sections(text_blocks, preferred_gender)`

```python
section_analysis = self._analyze_sections(text_blocks, preferred_gender)
  ├─> detect_gender_from_grammar(block_text)
  │   └─> Анализ грамматики ("я шел" → male, "я ждала" → female)
  │
  ├─> detect_voice_profile(block_text)
  │   └─> Поиск хинтов ("(шепотом)", "(мужской вокал)")
  │
  └─> Определение финального пола
      ├─> Приоритет 1: UI gender
      ├─> Приоритет 2: Грамматический дуэт (mixed)
      ├─> Приоритет 3: Только male
      └─> Приоритет 4: Только female
```

**Иерархия:**
```
_analyze_sections()
  ├─> Для каждого text_block:
  │   ├─> detect_gender_from_grammar()
  │   └─> detect_voice_profile()
  │
  └─> Определение final_gender_preference
      └─> Логика приоритетов
```

---

### 2.8 Этап 8: Генерация Семантических Слоев

**Метод:** `_build_semantic_layers(emo, tlp, bpm, style_key)`

```python
semantic_layers = self._build_semantic_layers(
    emotions,
    tlp,
    bpm,
    key
)
  ├─> Извлечение TLP значений
  │   ├─> love = tlp.get("love", 0)
  │   ├─> pain = tlp.get("pain", 0)
  │   ├─> truth = tlp.get("truth", 0)
  │   └─> cf = tlp.get("conscious_frequency", 0)
  │
  ├─> Генерация секций
  │   ├─> Intro (mood: mystic/calm, energy: low)
  │   ├─> Verse (mood: narrative/reflective, energy: mid)
  │   ├─> Bridge (mood: dramatic/dreamlike, energy: mid-high)
  │   ├─> Chorus (mood: uplifting/tense, energy: high)
  │   └─> Outro (mood: peaceful/fading, energy: low)
  │
  ├─> Корректировка BPM
  │   └─> bpm_adj = bpm + (love * 10) - (pain * 15) + (truth * 5)
  │
  └─> Возврат {
        "bpm_suggested": bpm_adj,
        "layers": {
          "depth": (truth + pain) / 2,
          "warmth": love,
          "clarity": cf,
          "sections": [intro, verse, bridge, chorus, outro]
        }
      }
```

**Иерархия:**
```
_build_semantic_layers()
  ├─> Извлечение TLP
  ├─> Генерация секций (5 типов)
  ├─> Добавление focus для каждой секции
  ├─> Корректировка BPM на основе TLP
  └─> Сборка результата
```

---

### 2.9 Этап 9: Определение Жанра

**Метод:** `HybridGenreEngine.resolve(text_input, genre=None)` [если доступен]

```python
genre_result = self._hge.resolve(text_input, genre=None)
  └─> HybridGenreEngine.resolve()
      ├─> Анализ семантической агрессии
      ├─> Анализ swing ratio
      ├─> Анализ электронного давления
      ├─> Определение домена (hard/electronic/jazz/lyrical/cinematic/comedy/soft)
      └─> Выбор конкретного жанра
```

**Внутренняя иерархия HybridGenreEngine.resolve():**
```
HybridGenreEngine.resolve()
  ├─> _build_signals()
  │   ├─> semantic_aggression анализ
  │   ├─> swing_ratio анализ
  │   ├─> electronic_pressure анализ
  │   └─> Сборка signals dictionary
  │
  ├─> _resolve_top_genres()
  │   ├─> Сортировка по весу
  │   ├─> Проверка dramatic_weight
  │   └─> Выбор топ-3 жанров
  │
  └─> Возврат {
        "genre": "selected_genre",
        "confidence": float,
        "signals": {...}
      }
```

**Зависимости:**
- `config.py` (GENRE_WEIGHTS, GENRE_THRESHOLDS)
- `genre_weights.py` (GenreWeightsEngine)
- `genre_registry.py` (GlobalGenreRegistry)

---

### 2.10 Этап 10: Генерация Стиля

**Метод:** `self.style.build(emo, tlp, text, bpm, semantic_hints, voice_hint)` [если доступен]

```python
style_result = self.style.build(
    emotions,
    tlp,
    text,
    bpm,
    semantic_hints,
    voice_hint
)
  └─> PatchedStyleMatrix.build()
      ├─> Анализ эмоций для стиля
      ├─> Анализ TLP для стиля
      ├─> Генерация визуального стиля
      ├─> Генерация нарративного стиля
      └─> Возврат style dictionary
```

---

### 2.11 Этап 11: Выбор Вокала

**Метод:** `VocalProfileRegistry.select()` [вызывается через vocal_allocator]

```python
vocal_profile = self.vocal_allocator.allocate(
    section_profiles,
    final_gender
)
  └─> AdaptiveVocalAllocator.allocate()
      ├─> Анализ section_profiles
      ├─> Определение vocal_form
      ├─> Определение gender
      └─> Возврат vocal profile
```

---

### 2.12 Этап 12: Проверка Целостности

**Метод:** `self.integrity.scan(text)` [опционально]

```python
integrity_result = self.integrity.scan(text)
  └─> IntegrityScanEngine.scan()
      ├─> Проверка структуры текста
      ├─> Проверка согласованности
      └─> Возврат integrity report
```

---

### 2.13 Этап 13: Аннотация Текста

**Метод:** `annotate_text(text_blocks, section_profiles, semantic_sections)`

```python
annotated_ui, annotated_suno = self.annotate_text(
    text_blocks,
    section_profiles,
    semantic_sections
)
  ├─> Построение semantic_map
  │   └─> Маппинг блоков на секции (Intro, Verse, Chorus, etc.)
  │
  ├─> Для каждого блока:
  │   ├─> Определение tag_name (из semantic_map)
  │   ├─> Получение семантики секции
  │   ├─> Получение вокального профиля
  │   ├─> Сборка Suno тега
  │   └─> Сборка UI тега
  │
  └─> Возврат (annotated_text_ui, annotated_text_suno)
```

**Иерархия:**
```
annotate_text()
  ├─> Построение semantic_map (на основе количества блоков)
  ├─> Построение sec_defs (определения секций)
  ├─> Для каждого text_block:
  │   ├─> Получение tag_name
  │   ├─> Получение семантики
  │   ├─> Получение gender_tag
  │   ├─> Сборка suno_tag
  │   └─> Сборка ui_tag
  └─> Добавление финального тега
```

---

## 3. Полная Иерархия Вызовов (Call Tree)

```
analyze(text, preferred_gender, ...)
│
├─> normalize_text_preserve_symbols(text)
│   └─> text_utils.normalize_text_preserve_symbols()
│
├─> extract_raw_blocks(raw)
│   └─> text_utils.extract_raw_blocks()
│
├─> self.emotion.analyze(raw)
│   └─> AutoEmotionalAnalyzer.analyze()
│       ├─> build_raw_emotion_vector()
│       ├─> project_to_clusters()
│       └─> Определение доминирующей эмоции
│
├─> self.rhythm.analyze(raw, emotions, tlp, cf)
│   └─> LyricMeter.analyze()
│       ├─> Поиск header_bpm
│       ├─> _density_bpm()
│       └─> Корректировка на основе TLP
│
├─> self.tone.detect_key(raw)
│   └─> ToneSyncEngine.detect_key()
│
├─> self.tlp.analyze(raw) [может вызываться внутри других этапов]
│   └─> TruthLovePainEngine.analyze()
│       ├─> Поиск Truth слов
│       ├─> Поиск Love слов
│       ├─> Поиск Pain слов
│       └─> Расчет CF
│
├─> _analyze_sections(text_blocks, preferred_gender)
│   ├─> detect_gender_from_grammar()
│   └─> detect_voice_profile()
│
├─> _build_semantic_layers(emotions, tlp, bpm, key)
│   ├─> Генерация Intro
│   ├─> Генерация Verse
│   ├─> Генерация Bridge
│   ├─> Генерация Chorus
│   ├─> Генерация Outro
│   └─> Корректировка BPM
│
├─> self.style.build(...) [если доступен]
│   └─> PatchedStyleMatrix.build()
│
├─> self._hge.resolve(...) [если доступен]
│   └─> HybridGenreEngine.resolve()
│       ├─> _build_signals()
│       └─> _resolve_top_genres()
│
├─> self.vocal_allocator.allocate(...)
│   └─> AdaptiveVocalAllocator.allocate()
│
├─> self.integrity.scan(text) [опционально]
│   └─> IntegrityScanEngine.scan()
│
└─> annotate_text(text_blocks, section_profiles, semantic_sections)
    ├─> Построение semantic_map
    ├─> Построение sec_defs
    └─> Генерация аннотаций для каждого блока
```

---

## 4. Поток Данных (Data Flow)

### 4.1 Входные Данные

```python
Input = {
    "text": str,                    # Исходный текст
    "preferred_gender": str,        # "auto" | "male" | "female" | "mixed"
    "version": Optional[str],       # Версия API
    "semantic_hints": Optional[Dict] # Семантические подсказки
}
```

### 4.2 Промежуточные Данные

```python
# После предобработки
raw: str                           # Нормализованный текст
text_blocks: List[str]             # Список блоков текста

# После эмоционального анализа
emotions: Dict[str, float]         # {"joy": 0.5, "sadness": 0.3, ...}

# После ритмического анализа
rhythm_analysis: Dict              # {"global_bpm": 120, "header_bpm": None, ...}
bpm: int                           # Финальный BPM

# После TLP анализа
tlp: Dict[str, float]              # {"truth": 0.4, "love": 0.3, "pain": 0.5, "conscious_frequency": 0.4}

# После анализа секций
section_profiles: List[Dict]       # [{"gender": "male", "hint": None}, ...]
final_gender: str                  # "auto" | "male" | "female" | "mixed"

# После генерации семантических слоев
semantic_layers: Dict              # {"bpm_suggested": 125, "layers": {...}}

# После определения жанра
genre_result: Dict                 # {"genre": "rock", "confidence": 0.8, ...}

# После генерации стиля
style_result: Dict                # {"genre": "...", "style": "...", ...}
```

### 4.3 Выходные Данные

```python
Output = {
    "emotions": Dict[str, float],
    "bpm": int,
    "key": str,
    "structure": {
        "sections": List[str],
        "section_count": int,
        "layout": str
    },
    "style": {
        "genre": str,
        "style": str,
        "bpm": int,
        "key": str,
        "visual": str,
        "narrative": str,
        "structure": str,
        "emotion": str
    },
    "annotated_text_ui": str,      # Аннотированный текст для UI
    "annotated_text_suno": str,    # Аннотированный текст для Suno
    "diagnostics": Dict,           # Диагностическая информация
    "fanf": Dict,                  # FANF аннотации
    "ok": bool                     # Статус успешности
}
```

---

## 5. Зависимости Между Этапами

### 5.1 Граф Зависимостей

```
Предобработка
  └─> Базовый анализ
      ├─> Emotion Analysis (независим)
      ├─> Rhythm Analysis (зависит от Emotion)
      └─> Tone Detection (независим)
          │
          ├─> TLP Analysis (может использоваться в Rhythm)
          │
          ├─> Section Analysis (зависит от text_blocks)
          │
          ├─> Semantic Layers (зависит от Emotion, TLP, BPM, Key)
          │
          ├─> Genre Detection (зависит от текста, может использовать Emotion)
          │
          ├─> Style Generation (зависит от Emotion, TLP, BPM)
          │
          ├─> Vocal Selection (зависит от Section Analysis)
          │
          └─> Text Annotation (зависит от Section Analysis, Semantic Layers)
```

### 5.2 Критические Зависимости

| Этап | Зависит от | Критичность |
|------|------------|-------------|
| Rhythm Analysis | Emotion Analysis | Средняя (может работать без) |
| Semantic Layers | Emotion, TLP, BPM, Key | Высокая |
| Style Generation | Emotion, TLP, BPM | Высокая |
| Text Annotation | Section Analysis, Semantic Layers | Высокая |
| Genre Detection | Текст | Средняя |
| Vocal Selection | Section Analysis | Высокая |

---

## 6. Параллелизация Возможностей

### 6.1 Независимые Этапы (можно выполнять параллельно)

```
┌─────────────────┐
│ Emotion Analysis│ (независим)
└─────────────────┘

┌─────────────────┐
│ Tone Detection  │ (независим)
└─────────────────┘

┌─────────────────┐
│ TLP Analysis    │ (независим, но может использоваться в Rhythm)
└─────────────────┘
```

### 6.2 Последовательные Этапы (требуют предыдущих результатов)

```
Emotion Analysis
  └─> Rhythm Analysis (может использовать emotions)

Section Analysis
  └─> Vocal Selection

Emotion + TLP + BPM + Key
  └─> Semantic Layers

Section Analysis + Semantic Layers
  └─> Text Annotation
```

---

## 7. Обработка Ошибок и Fallback

### 7.1 Иерархия Fallback

```
Попытка 1: StudioCoreV6
  └─> Ошибка? ↓
Попытка 2: StudioCoreV5
  └─> Ошибка? ↓
Попытка 3: Monolith (StudioCore)
  └─> Ошибка? ↓
Попытка 4: StudioCoreFallback
```

### 7.2 Fallback Значения

| Параметр | Fallback Источник | Значение |
|----------|-------------------|----------|
| BPM | DEFAULT_CONFIG.FALLBACK_BPM | 120 |
| Key | DEFAULT_CONFIG.FALLBACK_KEY | "C" |
| Genre | DEFAULT_CONFIG.FALLBACK_STYLE | "cinematic" |
| Emotion | DEFAULT_CONFIG.FALLBACK_EMOTION | "neutral" |
| Structure | DEFAULT_CONFIG.FALLBACK_STRUCTURE | "verse-chorus" |

---

## 8. Временная Сложность Этапов

| Этап | Сложность | Примечание |
|------|-----------|------------|
| Предобработка | O(n) | n = длина текста |
| Emotion Analysis | O(n * m) | m = количество ключевых слов |
| Rhythm Analysis | O(n) | Линейный проход |
| TLP Analysis | O(n * k) | k = количество TLP слов |
| Section Analysis | O(b) | b = количество блоков |
| Semantic Layers | O(1) | Константное время |
| Genre Detection | O(n * g) | g = количество жанровых признаков |
| Text Annotation | O(b) | b = количество блоков |

**Общая сложность:** O(n * m) где n = длина текста, m = максимальное количество признаков

---

## 9. Порядок Выполнения (Execution Order)

```
1. Инициализация Core
2. Нормализация текста
3. Извлечение блоков
4. Emotion Analysis (параллельно с Tone Detection)
5. Tone Detection (параллельно с Emotion Analysis)
6. Rhythm Analysis (после Emotion Analysis)
7. TLP Analysis (может быть параллельно)
8. Section Analysis
9. Semantic Layers (после Emotion, TLP, BPM, Key)
10. Genre Detection (может быть параллельно)
11. Style Generation (после Emotion, TLP, BPM)
12. Vocal Selection (после Section Analysis)
13. Integrity Scan (опционально, параллельно)
14. Text Annotation (после Section Analysis, Semantic Layers)
15. Сборка результата
```

---

## 10. Ключевые Методы и Их Иерархия

### 10.1 Основные Методы Анализа

| Метод | Класс | Уровень | Зависимости |
|-------|-------|---------|-------------|
| `analyze()` | StudioCore | Top | Все нижележащие |
| `analyze()` | AutoEmotionalAnalyzer | Level 2 | build_raw_emotion_vector, project_to_clusters |
| `analyze()` | LyricMeter | Level 2 | _density_bpm |
| `analyze()` | TruthLovePainEngine | Level 2 | Словари ключевых слов |
| `detect_key()` | ToneSyncEngine | Level 2 | - |
| `resolve()` | HybridGenreEngine | Level 2 | _build_signals, _resolve_top_genres |
| `build()` | PatchedStyleMatrix | Level 2 | - |
| `_analyze_sections()` | StudioCore | Level 2 | detect_gender_from_grammar, detect_voice_profile |
| `_build_semantic_layers()` | StudioCore | Level 2 | TLP, Emotions, BPM, Key |
| `annotate_text()` | StudioCore | Level 2 | Section Analysis, Semantic Layers |

---

## 11. Расширенная Иерархия (с опциональными компонентами)

```
analyze()
│
├─> [Обязательные этапы]
│   ├─> Предобработка
│   ├─> Emotion Analysis
│   ├─> Rhythm Analysis
│   ├─> Tone Detection
│   └─> Section Analysis
│
├─> [Опциональные этапы - если доступны]
│   ├─> TLP Analysis
│   ├─> RDE Analysis
│   ├─> Genre Detection (HybridGenreEngine)
│   ├─> Style Generation
│   ├─> Vocal Selection
│   ├─> Integrity Scan
│   └─> Frequency Check
│
└─> [Финальные этапы]
    ├─> Semantic Layers
    ├─> Text Annotation
    └─> Сборка результата
```

---

## 12. Пример Полного Прохода

### 12.1 Входные Данные

```python
text = """
[Verse 1]
Я шел по дороге одинокой
Боль в сердце, правда в словах

[Chorus]
Любовь ушла, но память осталась
Истина в том, что я один
"""
preferred_gender = "auto"
```

### 12.2 Последовательность Обработки

```
1. normalize_text_preserve_symbols()
   → raw = "Я шел по дороге одинокой\nБоль в сердце..."

2. extract_raw_blocks()
   → text_blocks = ["Я шел по дороге одинокой\nБоль в сердце...", "Любовь ушла..."]

3. emotion.analyze(raw)
   → emotions = {"sadness": 0.6, "pain": 0.5, "love": 0.3, "dominant": "sadness"}

4. rhythm.analyze(raw, emotions, ...)
   → rhythm_analysis = {"global_bpm": 85, "header_bpm": None, "estimated_bpm": 85}
   → bpm = 85

5. tone.detect_key(raw)
   → tone_hint = {"key": "Am"}
   → key = "Am"

6. tlp.analyze(raw)
   → tlp = {"truth": 0.4, "love": 0.3, "pain": 0.5, "conscious_frequency": 0.4}

7. _analyze_sections(text_blocks, "auto")
   → section_profiles = [{"gender": "male", "hint": None}, {"gender": "auto", "hint": None}]
   → final_gender = "male"

8. _build_semantic_layers(emotions, tlp, 85, "Am")
   → semantic_layers = {
       "bpm_suggested": 80,
       "layers": {
         "depth": 0.45,
         "warmth": 0.3,
         "clarity": 0.4,
         "sections": [intro, verse, bridge, chorus, outro]
       }
     }

9. annotate_text(text_blocks, section_profiles, semantic_sections)
   → annotated_ui = "[VERSE - MALE - narrative, mid, standard, BPM≈85]\nЯ шел..."
   → annotated_suno = "[VERSE - vocal: MALE - mood: narrative - energy: mid - arrangement: standard]\nЯ шел..."

10. Сборка результата
    → result = {
        "emotions": emotions,
        "bpm": 85,
        "key": "Am",
        "structure": {...},
        "style": {...},
        "annotated_text_ui": annotated_ui,
        "annotated_text_suno": annotated_suno,
        "ok": True
      }
```

---

## Резюме

**Основные уровни иерархии:**
1. **Вход** - API/UI Entry Points
2. **Core Facade** - Orchestrierung
3. **Предобработка** - Text Normalization
4. **Базовый анализ** - Emotion, Rhythm, Tone
5. **Углубленный анализ** - TLP, RDE, Genre, Sections
6. **Стиль и вокал** - Style, Vocal Selection
7. **Интеграция** - Integrity, Safety Checks
8. **Аннотация** - Text Annotation, FANF, Suno
9. **Результат** - Structured Output

**Ключевые зависимости:**
- Rhythm зависит от Emotion
- Semantic Layers зависит от Emotion, TLP, BPM, Key
- Text Annotation зависит от Section Analysis и Semantic Layers
- Style Generation зависит от Emotion, TLP, BPM

**Временная сложность:** O(n * m) где n = длина текста, m = количество признаков

---

**Создано:** Текущее состояние  
**Статус:** Полная иерархия анализа

