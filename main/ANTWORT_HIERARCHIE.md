# Иерархия Ответа После Анализа - Документация

Полная документация структуры ответа, возвращаемого после анализа текста в StudioCore.

---

## 1. Общая Структура Ответа

### 1.1 API Response (FastAPI)

```json
{
  "ok": bool,              // Статус успешности
  "result": {              // Основной результат анализа
    // ... полная структура результата
  },
  "error": Optional[str]   // Сообщение об ошибке (если ok = false)
}
```

### 1.2 Основной Result Dictionary

```json
{
  "ok": bool,                    // Статус (обычно true, если нет ошибок)
  "emotions": {...},            // Эмоциональный анализ
  "bpm": int,                   // BPM (beats per minute)
  "key": str,                   // Музыкальная тональность
  "structure": {...},           // Структура текста
  "style": {...},               // Стиль и жанр
  "fanf": {...},                // FANF аннотации
  "tlp": {...},                 // Truth/Love/Pain анализ
  "rde": {...},                 // Resonance/Fracture/Entropy
  "tone": {...},                // Тональный профиль
  "genre": {...},               // Жанровый анализ
  "vocal": {...},               // Вокальный профиль
  "diagnostics": {...},         // Диагностическая информация
  "payload": {...},              // Дополнительные данные
  "annotated_text": str,         // Аннотированный текст (UI)
  "annotated_text_suno": str,    // Аннотированный текст (Suno)
  "lyrics": {...},              // Детальная информация о лирике
  "color": {...},               // Цветовой профиль
  "breathing": {...},           // Информация о дыхании
  "meaning": {...},             // Семантический анализ
  "tonality": {...},            // Тональность
  "instrumentation": {...},     // Инструментация
  "rem": {...},                 // REM данные
  "zero_pulse": {...},          // Zero Pulse статус
  "commands": {...}              // Команды
}
```

---

## 2. Детальная Иерархия Полей

### 2.1 Уровень 1: Корневые Поля

```
result/
├── ok: bool                          # Статус успешности
├── error: Optional[str]              # Сообщение об ошибке
├── emotions: Dict                    # Эмоциональный анализ
├── bpm: int                          # BPM значение
├── key: str                          # Музыкальная тональность
├── structure: Dict                   # Структура текста
├── style: Dict                       # Стиль и жанр
├── fanf: Dict                        # FANF аннотации
├── tlp: Dict                         # Truth/Love/Pain
├── rde: Dict                         # Resonance/Fracture/Entropy
├── tone: Dict                        # Тональный профиль
├── genre: Dict                       # Жанровый анализ
├── vocal: Dict                       # Вокальный профиль
├── diagnostics: Dict                # Диагностика
├── payload: Dict                     # Дополнительные данные
├── annotated_text: str               # Аннотированный текст (UI)
├── annotated_text_suno: str          # Аннотированный текст (Suno)
├── lyrics: Dict                      # Детальная лирика
├── color: Dict                       # Цветовой профиль
├── breathing: Dict                   # Дыхание
├── meaning: Dict                     # Семантика
├── tonality: Dict                    # Тональность
├── instrumentation: Dict             # Инструментация
├── rem: Dict                         # REM данные
├── zero_pulse: Dict                  # Zero Pulse
└── commands: Dict                    # Команды
```

---

## 3. Emotions (Эмоциональный Анализ)

### 3.1 Структура

```json
{
  "emotions": {
    "profile": {
      "joy": float,           // 0.0 - 1.0
      "sadness": float,
      "anger": float,
      "fear": float,
      "surprise": float,
      "disgust": float,
      "love": float,
      "hate": float,
      "peace": float,
      "epic": float,
      "hope": float,
      "pain": float,
      // ... другие эмоции
    },
    "dominant": str,          // Доминирующая эмоция
    "intensity": float,        // Общая интенсивность
    "clusters": {             // Эмоциональные кластеры
      "cluster_name": float
    },
    "base": {                 // Базовые эмоции
      "emotion_name": float
    },
    "vector": List[float]     // Эмоциональный вектор
  }
}
```

### 3.2 Иерархия

```
emotions/
├── profile: Dict[str, float]         # Профиль эмоций
│   ├── joy: float
│   ├── sadness: float
│   ├── anger: float
│   ├── fear: float
│   ├── surprise: float
│   ├── disgust: float
│   ├── love: float
│   ├── hate: float
│   ├── peace: float
│   ├── epic: float
│   ├── hope: float
│   └── pain: float
├── dominant: str                     # Доминирующая эмоция
├── intensity: float                   # Интенсивность (0.0 - 1.0)
├── clusters: Dict[str, float]        # Кластеры эмоций
├── base: Dict[str, float]            # Базовые эмоции
└── vector: List[float]               # Векторное представление
```

---

## 4. TLP (Truth/Love/Pain)

### 4.1 Структура

```json
{
  "tlp": {
    "truth": float,              // 0.0 - 1.0
    "love": float,               // 0.0 - 1.0
    "pain": float,               // 0.0 - 1.0
    "conscious_frequency": float, // CF (гармоническое среднее)
    "dominant": str,             // "truth" | "love" | "pain"
    "balance": float,            // Баланс между осями
    "vector": {                  // Векторное представление
      "truth": float,
      "love": float,
      "pain": float
    }
  }
}
```

### 4.2 Иерархия

```
tlp/
├── truth: float                      # Значение Truth (0.0 - 1.0)
├── love: float                       # Значение Love (0.0 - 1.0)
├── pain: float                       # Значение Pain (0.0 - 1.0)
├── conscious_frequency: float        # CF (Conscious Frequency)
├── dominant: str                     # Доминирующая ось
├── balance: float                    # Баланс между осями
└── vector: Dict[str, float]          # Вектор TLP
```

---

## 5. RDE (Resonance/Fracture/Entropy)

### 5.1 Структура

```json
{
  "rde": {
    "resonance": float,          // Резонанс (повторения)
    "fracture": float,           // Фрактура (структурные разрывы)
    "entropy": float,            // Энтропия (разнообразие)
    "emotion": str,              // Доминирующая эмоция RDE
    "profile": {                 // Профиль RDE
      "resonance": float,
      "fracture": float,
      "entropy": float
    }
  }
}
```

### 5.2 Иерархия

```
rde/
├── resonance: float                  # Резонанс (0.0 - 1.0)
├── fracture: float                   # Фрактура (0.0 - 1.0)
├── entropy: float                    # Энтропия (0.0 - 1.0)
├── emotion: str                      # Доминирующая эмоция
└── profile: Dict[str, float]        # Профиль RDE
```

---

## 6. Structure (Структура Текста)

### 6.1 Структура

```json
{
  "structure": {
    "sections": [
      {
        "tag": str,              // "Verse", "Chorus", "Bridge", etc.
        "text": str,             // Текст секции
        "line_count": int,       // Количество строк
        "emotion": str,          // Эмоция секции
        "bpm": float             // BPM секции
      }
    ],
    "section_count": int,        // Количество секций
    "layout": str,               // "verse-chorus", "intro-verse-chorus", etc.
    "headers": [                 // Заголовки секций
      {
        "tag": str,
        "index": int,
        "line": int
      }
    ],
    "intro": str,                // Текст интро
    "chorus": str,               // Текст припева
    "outro": str                 // Текст аутро
  }
}
```

### 6.2 Иерархия

```
structure/
├── sections: List[Dict]              # Список секций
│   ├── tag: str                      # Тип секции
│   ├── text: str                     # Текст секции
│   ├── line_count: int               # Количество строк
│   ├── emotion: str                   # Эмоция секции
│   └── bpm: float                    # BPM секции
├── section_count: int                # Количество секций
├── layout: str                       # Схема композиции
├── headers: List[Dict]               # Заголовки секций
│   ├── tag: str
│   ├── index: int
│   └── line: int
├── intro: str                        # Текст интро
├── chorus: str                       # Текст припева
└── outro: str                        # Текст аутро
```

---

## 7. Style (Стиль и Жанр)

### 7.1 Структура

```json
{
  "style": {
    "genre": str,                // "rock", "pop", "cinematic", etc.
    "style": str,                // Стиль
    "bpm": int,                  // BPM
    "key": str,                  // Тональность ("C", "Am", etc.)
    "mood": str,                 // Настроение
    "visual": str,               // Визуальное описание
    "narrative": str,            // Нарративное описание
    "structure": str,            // Структурное описание
    "emotion": str,              // Эмоциональное описание
    "color_wave": str,           // Цветовая волна
    "prompt": str                // Стилевой промпт
  }
}
```

### 7.2 Иерархия

```
style/
├── genre: str                        # Жанр
├── style: str                        # Стиль
├── bpm: int                          # BPM
├── key: str                          # Тональность
├── mood: str                         # Настроение
├── visual: str                       # Визуальное описание
├── narrative: str                    # Нарративное описание
├── structure: str                   # Структурное описание
├── emotion: str                      # Эмоциональное описание
├── color_wave: str                   # Цветовая волна
└── prompt: str                       # Стилевой промпт
```

---

## 8. FANF (Аннотации)

### 8.1 Структура

```json
{
  "fanf": {
    "style_prompt": str,          // Промпт для стиля
    "lyrics_prompt": str,         // Промпт для лирики (Suno)
    "ui_text": str,               // Аннотированный текст для UI
    "annotated_text_fanf": str,   // FANF аннотированный текст
    "full": str,                  // Полный FANF текст
    "summary": str                // Краткое резюме
  }
}
```

### 8.2 Иерархия

```
fanf/
├── style_prompt: str                 # Промпт стиля
├── lyrics_prompt: str                # Промпт лирики (для Suno)
├── ui_text: str                      # Аннотированный текст (UI)
├── annotated_text_fanf: str          # FANF аннотированный текст
├── full: str                         # Полный FANF
└── summary: str                      # Краткое резюме
```

---

## 9. Tone (Тональный Профиль)

### 9.1 Структура

```json
{
  "tone": {
    "key": str,                   // "C", "Am", "Dm", etc.
    "mode": str,                  // "major" | "minor"
    "profile": {                  // Тональный профиль
      "key": str,
      "mode": str,
      "confidence": float
    },
    "colors": [                   // Цвета тональности
      "#FF0000",
      "#00FF00"
    ]
  }
}
```

### 9.2 Иерархия

```
tone/
├── key: str                           # Тональность
├── mode: str                          # Режим (major/minor)
├── profile: Dict                      # Тональный профиль
│   ├── key: str
│   ├── mode: str
│   └── confidence: float
└── colors: List[str]                  # Цвета тональности
```

---

## 10. Genre (Жанровый Анализ)

### 10.1 Структура

```json
{
  "genre": {
    "genre": str,                 // Основной жанр
    "confidence": float,          // Уверенность (0.0 - 1.0)
    "signals": {                  // Сигналы жанров
      "rock": float,
      "pop": float,
      "electronic": float
    },
    "domain": str,                // Домен ("hard", "electronic", etc.)
    "tags": List[str],            // Жанровые теги
    "universe_tags": List[str]    // Теги из GenreUniverse
  }
}
```

### 10.2 Иерархия

```
genre/
├── genre: str                         # Основной жанр
├── confidence: float                  # Уверенность (0.0 - 1.0)
├── signals: Dict[str, float]          # Сигналы жанров
├── domain: str                        # Домен
├── tags: List[str]                    # Жанровые теги
└── universe_tags: List[str]           # Теги из GenreUniverse
```

---

## 11. Vocal (Вокальный Профиль)

### 11.1 Структура

```json
{
  "vocal": {
    "gender": str,                // "male" | "female" | "mixed" | "auto"
    "type": str,                  // Тип вокала
    "tone": str,                  // Тон вокала
    "style": str,                 // Стиль вокала
    "form": str,                  // Форма вокала
    "vocal_count": int,           // Количество вокалистов
    "final_gender_preference": str, // Финальное предпочтение пола
    "section_profiles": [         // Профили секций
      {
        "gender": str,
        "hint": Optional[str]
      }
    ]
  }
}
```

### 11.2 Иерархия

```
vocal/
├── gender: str                        # Пол ("male" | "female" | "mixed" | "auto")
├── type: str                          # Тип вокала
├── tone: str                          # Тон вокала
├── style: str                         # Стиль вокала
├── form: str                          # Форма вокала
├── vocal_count: int                   # Количество вокалистов
├── final_gender_preference: str       # Финальное предпочтение
└── section_profiles: List[Dict]       # Профили секций
    ├── gender: str
    └── hint: Optional[str]
```

---

## 12. Diagnostics (Диагностика)

### 12.1 Структура (v8.0 Schema)

```json
{
  "diagnostics": {
    "diagnostic_schema": "v8.0",
    "engines": {
      "bpm": {...},
      "rde": {...},
      "tlp": {...},
      "genre": {...},
      "tone": {...},
      "frequency": {...},
      "emotion": {...}
    },
    "summary_blocks": {
      "tlp_summary": str,
      "rde_summary": str,
      "genre_summary": str,
      "color_wave_summary": str,
      "zero_pulse_summary": str,
      "integrity_summary": str
    },
    "consistency": {
      "score": float,
      "issues": List[str]
    },
    "meta": {
      "version": str,
      "runtime_ms": float,
      "timestamp": str
    },
    // Legacy keys (сохраняются для обратной совместимости)
    "bpm": {...},
    "rde": {...},
    "tlp": {...},
    "genre": {...}
  }
}
```

### 12.2 Иерархия

```
diagnostics/
├── diagnostic_schema: str             # Версия схемы ("v8.0")
├── engines: Dict                      # Результаты движков
│   ├── bpm: Dict
│   ├── rde: Dict
│   ├── tlp: Dict
│   ├── genre: Dict
│   ├── tone: Dict
│   ├── frequency: Dict
│   └── emotion: Dict
├── summary_blocks: Dict               # Текстовые блоки
│   ├── tlp_summary: str
│   ├── rde_summary: str
│   ├── genre_summary: str
│   ├── color_wave_summary: str
│   ├── zero_pulse_summary: str
│   └── integrity_summary: str
├── consistency: Dict                  # Согласованность
│   ├── score: float
│   └── issues: List[str]
├── meta: Dict                         # Метаданные
│   ├── version: str
│   ├── runtime_ms: float
│   └── timestamp: str
└── [Legacy keys]                      # Старые ключи (для совместимости)
```

---

## 13. Lyrics (Детальная Лирика)

### 13.1 Структура

```json
{
  "lyrics": {
    "sections": [
      {
        "tag": str,
        "text": str,
        "emotion": str,
        "bpm": float,
        "line_count": int
      }
    ],
    "annotations": {
      "rhythm": [...],
      "emotion": [...],
      "breathing": [...]
    }
  }
}
```

### 13.2 Иерархия

```
lyrics/
├── sections: List[Dict]               # Секции лирики
│   ├── tag: str
│   ├── text: str
│   ├── emotion: str
│   ├── bpm: float
│   └── line_count: int
└── annotations: Dict                  # Аннотации
    ├── rhythm: List
    ├── emotion: List
    └── breathing: List
```

---

## 14. Color (Цветовой Профиль)

### 14.1 Структура

```json
{
  "color": {
    "primary_color": str,          // "#FF0000"
    "secondary_color": str,        // "#00FF00"
    "color_wave": str,             // Описание цветовой волны
    "profile": {                   // Цветовой профиль
      "primary": str,
      "secondary": str,
      "gradient": List[str]
    }
  }
}
```

### 14.2 Иерархия

```
color/
├── primary_color: str                 # Основной цвет
├── secondary_color: str               # Вторичный цвет
├── color_wave: str                    # Цветовая волна
└── profile: Dict                      # Цветовой профиль
    ├── primary: str
    ├── secondary: str
    └── gradient: List[str]
```

---

## 15. Breathing (Дыхание)

### 15.1 Структура

```json
{
  "breathing": {
    "sync_points": [              // Точки синхронизации дыхания
      {
        "line": int,
        "position": int,
        "type": str
      }
    ],
    "pattern": str,               // Паттерн дыхания
    "intensity": float            // Интенсивность
  }
}
```

### 15.2 Иерархия

```
breathing/
├── sync_points: List[Dict]            # Точки синхронизации
│   ├── line: int
│   ├── position: int
│   └── type: str
├── pattern: str                       # Паттерн дыхания
└── intensity: float                   # Интенсивность
```

---

## 16. Zero Pulse

### 16.1 Структура

```json
{
  "zero_pulse": {
    "status": str,                 // "active" | "inactive"
    "detected": bool,              // Обнаружен ли Zero Pulse
    "confidence": float,           // Уверенность
    "summary": str                 // Краткое описание
  }
}
```

### 16.2 Иерархия

```
zero_pulse/
├── status: str                        # Статус ("active" | "inactive")
├── detected: bool                     # Обнаружен ли
├── confidence: float                  # Уверенность
└── summary: str                       # Описание
```

---

## 17. Instrumentation (Инструментация)

### 17.1 Структура

```json
{
  "instrumentation": {
    "instruments": [              // Список инструментов
      {
        "name": str,
        "role": str,
        "intensity": float
      }
    ],
    "arrangement": str,           // Аранжировка
    "density": float              // Плотность
  }
}
```

### 17.2 Иерархия

```
instrumentation/
├── instruments: List[Dict]           # Инструменты
│   ├── name: str
│   ├── role: str
│   └── intensity: float
├── arrangement: str                  # Аранжировка
└── density: float                    # Плотность
```

---

## 18. Payload (Дополнительные Данные)

### 18.1 Структура

```json
{
  "payload": {
    "engine": str,                // "StudioCoreV6"
    "legacy": {...},              // Legacy данные
    "semantic_layers": {...},     // Семантические слои
    "section_intelligence": {...} // Интеллект секций
  }
}
```

### 18.2 Иерархия

```
payload/
├── engine: str                       # Версия движка
├── legacy: Dict                      # Legacy данные
├── semantic_layers: Dict              # Семантические слои
└── section_intelligence: Dict        # Интеллект секций
```

---

## 19. Полная Иерархия Ответа (Tree View)

```
Response
│
├── ok: bool
├── error: Optional[str]
└── result: Dict
    │
    ├── ok: bool
    ├── emotions: Dict
    │   ├── profile: Dict[str, float]
    │   ├── dominant: str
    │   ├── intensity: float
    │   ├── clusters: Dict[str, float]
    │   ├── base: Dict[str, float]
    │   └── vector: List[float]
    │
    ├── bpm: int
    ├── key: str
    │
    ├── structure: Dict
    │   ├── sections: List[Dict]
    │   ├── section_count: int
    │   ├── layout: str
    │   ├── headers: List[Dict]
    │   ├── intro: str
    │   ├── chorus: str
    │   └── outro: str
    │
    ├── style: Dict
    │   ├── genre: str
    │   ├── style: str
    │   ├── bpm: int
    │   ├── key: str
    │   ├── mood: str
    │   ├── visual: str
    │   ├── narrative: str
    │   ├── structure: str
    │   ├── emotion: str
    │   ├── color_wave: str
    │   └── prompt: str
    │
    ├── fanf: Dict
    │   ├── style_prompt: str
    │   ├── lyrics_prompt: str
    │   ├── ui_text: str
    │   ├── annotated_text_fanf: str
    │   ├── full: str
    │   └── summary: str
    │
    ├── tlp: Dict
    │   ├── truth: float
    │   ├── love: float
    │   ├── pain: float
    │   ├── conscious_frequency: float
    │   ├── dominant: str
    │   ├── balance: float
    │   └── vector: Dict[str, float]
    │
    ├── rde: Dict
    │   ├── resonance: float
    │   ├── fracture: float
    │   ├── entropy: float
    │   ├── emotion: str
    │   └── profile: Dict[str, float]
    │
    ├── tone: Dict
    │   ├── key: str
    │   ├── mode: str
    │   ├── profile: Dict
    │   └── colors: List[str]
    │
    ├── genre: Dict
    │   ├── genre: str
    │   ├── confidence: float
    │   ├── signals: Dict[str, float]
    │   ├── domain: str
    │   ├── tags: List[str]
    │   └── universe_tags: List[str]
    │
    ├── vocal: Dict
    │   ├── gender: str
    │   ├── type: str
    │   ├── tone: str
    │   ├── style: str
    │   ├── form: str
    │   ├── vocal_count: int
    │   ├── final_gender_preference: str
    │   └── section_profiles: List[Dict]
    │
    ├── diagnostics: Dict
    │   ├── diagnostic_schema: str
    │   ├── engines: Dict
    │   ├── summary_blocks: Dict
    │   ├── consistency: Dict
    │   ├── meta: Dict
    │   └── [Legacy keys]
    │
    ├── lyrics: Dict
    │   ├── sections: List[Dict]
    │   └── annotations: Dict
    │
    ├── color: Dict
    │   ├── primary_color: str
    │   ├── secondary_color: str
    │   ├── color_wave: str
    │   └── profile: Dict
    │
    ├── breathing: Dict
    │   ├── sync_points: List[Dict]
    │   ├── pattern: str
    │   └── intensity: float
    │
    ├── zero_pulse: Dict
    │   ├── status: str
    │   ├── detected: bool
    │   ├── confidence: float
    │   └── summary: str
    │
    ├── instrumentation: Dict
    │   ├── instruments: List[Dict]
    │   ├── arrangement: str
    │   └── density: float
    │
    ├── payload: Dict
    │   ├── engine: str
    │   ├── legacy: Dict
    │   ├── semantic_layers: Dict
    │   └── section_intelligence: Dict
    │
    ├── annotated_text: str
    ├── annotated_text_suno: str
    │
    ├── meaning: Dict
    ├── tonality: Dict
    ├── rem: Dict
    └── commands: Dict
```

---

## 20. Пример Полного Ответа

```json
{
  "ok": true,
  "result": {
    "ok": true,
    "emotions": {
      "profile": {
        "sadness": 0.6,
        "love": 0.3,
        "pain": 0.5,
        "hope": 0.2
      },
      "dominant": "sadness",
      "intensity": 0.65
    },
    "bpm": 85,
    "key": "Am",
    "structure": {
      "sections": [
        {
          "tag": "Verse",
          "text": "Я шел по дороге одинокой",
          "line_count": 4,
          "emotion": "sadness",
          "bpm": 85
        },
        {
          "tag": "Chorus",
          "text": "Любовь ушла, но память осталась",
          "line_count": 4,
          "emotion": "love",
          "bpm": 90
        }
      ],
      "section_count": 2,
      "layout": "verse-chorus"
    },
    "style": {
      "genre": "ballad",
      "style": "acoustic",
      "bpm": 85,
      "key": "Am",
      "mood": "melancholic",
      "color_wave": "deep blue to purple"
    },
    "fanf": {
      "style_prompt": "acoustic ballad, melancholic, 85 BPM, Am",
      "lyrics_prompt": "[VERSE - vocal: MALE - mood: narrative - energy: mid]\nЯ шел по дороге одинокой\n[CHORUS - vocal: MALE - mood: uplifting - energy: high]\nЛюбовь ушла, но память осталась",
      "ui_text": "[VERSE - MALE - narrative, mid, standard, BPM≈85]\nЯ шел по дороге одинокой\n\n[CHORUS - MALE - uplifting, high, full arrangement, BPM≈90]\nЛюбовь ушла, но память осталась"
    },
    "tlp": {
      "truth": 0.4,
      "love": 0.3,
      "pain": 0.5,
      "conscious_frequency": 0.4,
      "dominant": "pain"
    },
    "rde": {
      "resonance": 0.3,
      "fracture": 0.2,
      "entropy": 0.5,
      "emotion": "sadness"
    },
    "tone": {
      "key": "Am",
      "mode": "minor",
      "colors": ["#3E5C82", "#4A6FA5"]
    },
    "genre": {
      "genre": "ballad",
      "confidence": 0.8,
      "domain": "lyrical"
    },
    "vocal": {
      "gender": "male",
      "final_gender_preference": "male"
    },
    "diagnostics": {
      "diagnostic_schema": "v8.0",
      "engines": {
        "bpm": {"status": "ok"},
        "rde": {"status": "ok"},
        "tlp": {"status": "ok"}
      },
      "meta": {
        "version": "v6.4 - maxi",
        "runtime_ms": 125.5
      }
    },
    "annotated_text": "[VERSE - MALE - narrative, mid, standard, BPM≈85]\nЯ шел по дороге одинокой",
    "annotated_text_suno": "[VERSE - vocal: MALE - mood: narrative - energy: mid]\nЯ шел по дороге одинокой"
  }
}
```

---

## 21. Обязательные vs Опциональные Поля

### 21.1 Обязательные Поля

| Поле | Уровень | Описание |
|------|---------|----------|
| `ok` | Root | Статус успешности |
| `result` | Root | Основной результат (в API response) |

### 21.2 Опциональные Поля (зависят от конфигурации)

| Поле | Условие присутствия |
|------|---------------------|
| `emotions` | Всегда (базовый анализ) |
| `bpm` | Всегда |
| `key` | Всегда |
| `structure` | Всегда |
| `style` | Всегда |
| `fanf` | Если включены FANF аннотации |
| `tlp` | Если включен TLP анализ |
| `rde` | Если включен RDE анализ |
| `tone` | Если включен Tone анализ |
| `genre` | Если включен Genre анализ |
| `vocal` | Если включен Vocal анализ |
| `diagnostics` | Если включена диагностика |
| `lyrics` | Если включен детальный анализ лирики |
| `color` | Если включен Color анализ |
| `breathing` | Если включен Breathing анализ |
| `zero_pulse` | Если включен Zero Pulse |
| `instrumentation` | Если включена Instrumentation |
| `payload` | Дополнительные данные |

---

## 22. Типы Данных

### 22.1 Базовые Типы

| Тип | Описание | Примеры |
|-----|----------|---------|
| `bool` | Булево значение | `true`, `false` |
| `int` | Целое число | `85`, `120` |
| `float` | Число с плавающей точкой | `0.65`, `0.4` |
| `str` | Строка | `"ballad"`, `"Am"` |
| `List[T]` | Список элементов типа T | `["rock", "pop"]` |
| `Dict[str, T]` | Словарь строковых ключей | `{"joy": 0.5}` |
| `Optional[T]` | Опциональное значение типа T | `null` или значение |

### 22.2 Специальные Типы

| Тип | Описание |
|-----|----------|
| `Color` | HEX цвет (`"#FF0000"`) |
| `BPM` | Beats Per Minute (40-200) |
| `Key` | Музыкальная тональность (`"C"`, `"Am"`, etc.) |
| `Gender` | `"male"` | `"female"` | `"mixed"` | `"auto"` |
| `Emotion` | Название эмоции (`"joy"`, `"sadness"`, etc.) |
| `Genre` | Название жанра (`"rock"`, `"pop"`, etc.) |
| `SectionTag` | `"Verse"` | `"Chorus"` | `"Bridge"` | `"Intro"` | `"Outro"` |

---

## 23. Валидация Ответа

### 23.1 Проверки

```python
# Проверка успешности
assert result.get("ok", True) == True

# Проверка обязательных полей
assert "bpm" in result
assert "key" in result
assert "structure" in result
assert "style" in result

# Проверка типов
assert isinstance(result["bpm"], int)
assert isinstance(result["key"], str)
assert isinstance(result["emotions"], dict)

# Проверка диапазонов
assert 40 <= result["bpm"] <= 200
assert 0.0 <= result["tlp"]["truth"] <= 1.0
```

---

## Резюме

**Основные блоки ответа:**
1. **Статус** - `ok`, `error`
2. **Базовый анализ** - `emotions`, `bpm`, `key`, `structure`
3. **Стиль** - `style`, `genre`, `tone`
4. **Аннотации** - `fanf`, `annotated_text`, `annotated_text_suno`
5. **Углубленный анализ** - `tlp`, `rde`, `lyrics`
6. **Вокал** - `vocal`
7. **Диагностика** - `diagnostics`
8. **Дополнительно** - `color`, `breathing`, `zero_pulse`, `instrumentation`

**Иерархия уровней:**
- **Уровень 0:** API Response (`ok`, `result`, `error`)
- **Уровень 1:** Основные блоки результата
- **Уровень 2:** Вложенные структуры внутри блоков
- **Уровень 3:** Детальные данные внутри структур

**Схема версионирования:**
- `diagnostic_schema: "v8.0"` для диагностики
- Legacy ключи сохраняются для обратной совместимости

---

**Создано:** Текущее состояние  
**Статус:** Полная иерархия ответа

