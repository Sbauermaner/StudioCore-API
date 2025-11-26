# СХЕМА ОТВЕТА ПОСЛЕ АНАЛИЗА

## Общая структура

```json
{
  "ok": true,
  "engine": "StudioCoreV6",
  "structure": {...},
  "tlp": {...},
  "emotion": {...},
  "style": {...},
  "vocal": {...},
  "bpm": 120,
  "tonality": {...},
  "color": {...},
  "fanf": {...},
  "suno": {...},
  "lyrics": {...},
  "diagnostics": {...}
}
```

## Детальная структура

### 1. Основные поля

```json
{
  "ok": true,                    // bool - статус успешности анализа
  "engine": "StudioCoreV6",      // str - название движка
  "error": null                  // str | null - ошибка (если ok=false)
}
```

### 2. structure (Структура текста)

```json
{
  "structure": {
    "sections": [                // list[str] - тексты секций
      "Белый вечер стыл в бокале...",
      "О, одно лишь прикосновение..."
    ],
    "headers": [                 // list[dict] - метаданные секций
      {
        "tag": "Verse 1",        // str - тег секции
        "label": "Verse 1",      // str - метка секции
        "name": "Verse 1",       // str - имя секции
        "line_count": 4         // int - количество строк
      },
      {
        "tag": "Chorus",
        "label": "Chorus",
        "name": "Chorus",
        "line_count": 2
      }
    ],
    "section_count": 7,          // int - количество секций
    "intro": false,              // bool - есть ли intro
    "chorus": true,              // bool - есть ли chorus
    "bridge": true,              // bool - есть ли bridge
    "outro": true,               // bool - есть ли outro
    "labels": ["Verse 1", "Chorus", ...]  // list[str] - метки секций
  }
}
```

### 3. tlp (Truth, Love, Pain)

```json
{
  "tlp": {
    "love": 0.85,                // float - уровень любви (0.0-1.0)
    "pain": 0.60,                // float - уровень боли (0.0-1.0)
    "truth": 0.78,               // float - уровень правды (0.0-1.0)
    "conscious_frequency": 0.75  // float - сознательная частота (0.0-1.0)
  }
}
```

### 4. emotion (Эмоции)

```json
{
  "emotion": {
    "vector": {                  // dict[str, float] - вектор эмоций
      "love": 0.85,
      "pain": 0.60,
      "joy": 0.20,
      "sadness": 0.40,
      "peace": 0.30,
      "sensual": 0.80,
      "nostalgia": 0.70,
      ...
    },
    "dominant": "sensual",       // str - доминирующая эмоция
    "intensity": 0.75,            // float - интенсивность эмоций
    "profile": {...}             // dict - профиль эмоций
  }
}
```

### 5. style (Стиль и жанр)

```json
{
  "style": {
    "genre": "lyrical_song",     // str - музыкальный жанр
    "prompt": "...",             // str - промпт для генерации
    "mood": "sensual",           // str - настроение
    "domain": "lyrical",         // str - домен жанра
    "subgenre": "ballad"         // str - поджанр
  }
}
```

### 6. vocal (Вокал)

```json
{
  "vocal": {
    "technique": "soft_tenor_baritone",  // str - вокальная техника
    "gender": "male",                     // str - пол вокалиста
    "profile": {                          // dict - профиль вокала
      "type": "tenor",
      "range": "C3-C5",
      "style": "soft"
    },
    "section_techniques": [               // list[dict] - техники по секциям
      {
        "section": "Verse 1",
        "technique": "soft_tenor"
      },
      ...
    ]
  }
}
```

### 7. bpm (Темп)

```json
{
  "bpm": 120  // int - темп (beats per minute)
}
```

### 8. tonality (Тональность)

```json
{
  "tonality": {
    "key": "C",                  // str - тональность (C, D, E, ...)
    "mode": "major",             // str - лад (major/minor)
    "frequency": 261.63,         // float - частота в Hz
    "resonance": {...}           // dict - резонанс
  }
}
```

### 9. color (Цвета)

```json
{
  "color": {
    "dominant": "#FF6B9D",       // str - доминирующий цвет (HEX)
    "palette": [                 // list[str] - палитра цветов
      "#FF6B9D",
      "#C44569",
      "#F8BBD0"
    ],
    "wave": {                    // dict - цветовая волна
      "primary": "#FF6B9D",
      "secondary": "#C44569",
      "accent": "#F8BBD0"
    }
  }
}
```

### 10. fanf (FANF аннотации)

```json
{
  "fanf": {
    "annotation": "...",          // str - FANF аннотация
    "narrative": "...",          // str - нарратив
    "cinematic": {...}           // dict - кинематографические данные
  }
}
```

### 11. suno (Suno аннотации)

```json
{
  "suno": {
    "prompt": "...",             // str - промпт для Suno
    "annotations": [             // list[str] - аннотации
      "[Verse 1]",
      "[Chorus]",
      ...
    ],
    "full_prompt": "..."         // str - полный промпт
  }
}
```

### 12. lyrics (Текст с аннотациями)

```json
{
  "lyrics": {
    "sections": [                 // list[dict] - секции с аннотациями
      {
        "header": "Verse 1",
        "text": "Белый вечер стыл в бокале...",
        "vocal": "soft_tenor",
        "emotion": "sensual",
        "bpm": 120,
        "key": "C"
      },
      ...
    ],
    "full_text": "...",          // str - полный текст
    "annotated": "..."           // str - текст с аннотациями
  }
}
```

### 13. diagnostics (Диагностика)

```json
{
  "diagnostics": {
    "bpm": {...},                 // dict - диагностика BPM
    "tonality": {...},            // dict - диагностика тональности
    "vocal": {...},               // dict - диагностика вокала
    "emotion_matrix": {...}      // dict - диагностика эмоций
  }
}
```

## Полный пример ответа

```json
{
  "ok": true,
  "engine": "StudioCoreV6",
  "structure": {
    "sections": [
      "Белый вечер стыл в бокале,\nВ стекле играл лунный свет.",
      "О, одно лишь прикосновение, плотское наслажденье!"
    ],
    "headers": [
      {
        "tag": "Verse 1",
        "label": "Verse 1",
        "name": "Verse 1",
        "line_count": 2
      },
      {
        "tag": "Chorus",
        "label": "Chorus",
        "name": "Chorus",
        "line_count": 1
      }
    ],
    "section_count": 2,
    "intro": false,
    "chorus": true,
    "bridge": false,
    "outro": false
  },
  "tlp": {
    "love": 0.85,
    "pain": 0.60,
    "truth": 0.78,
    "conscious_frequency": 0.75
  },
  "emotion": {
    "vector": {
      "love": 0.85,
      "sensual": 0.80,
      "nostalgia": 0.70
    },
    "dominant": "sensual",
    "intensity": 0.75
  },
  "style": {
    "genre": "lyrical_song",
    "prompt": "A sensual, nostalgic ballad...",
    "mood": "sensual"
  },
  "vocal": {
    "technique": "soft_tenor_baritone",
    "gender": "male"
  },
  "bpm": 120,
  "tonality": {
    "key": "C",
    "mode": "major"
  },
  "color": {
    "dominant": "#FF6B9D",
    "palette": ["#FF6B9D", "#C44569", "#F8BBD0"]
  },
  "fanf": {
    "annotation": "A sensual memory...",
    "narrative": "The narrator recalls..."
  },
  "suno": {
    "prompt": "[120 BPM, C major] A sensual ballad...",
    "annotations": ["[Verse 1]", "[Chorus]"]
  },
  "lyrics": {
    "sections": [
      {
        "header": "Verse 1",
        "text": "Белый вечер стыл в бокале...",
        "vocal": "soft_tenor",
        "emotion": "sensual"
      }
    ]
  },
  "diagnostics": {}
}
```

## Визуальная схема

```
result
├─ ok: bool
├─ engine: str
├─ structure
│  ├─ sections: list[str]
│  ├─ headers: list[dict]
│  ├─ section_count: int
│  ├─ intro: bool
│  ├─ chorus: bool
│  ├─ bridge: bool
│  └─ outro: bool
├─ tlp
│  ├─ love: float
│  ├─ pain: float
│  ├─ truth: float
│  └─ conscious_frequency: float
├─ emotion
│  ├─ vector: dict[str, float]
│  ├─ dominant: str
│  └─ intensity: float
├─ style
│  ├─ genre: str
│  ├─ prompt: str
│  └─ mood: str
├─ vocal
│  ├─ technique: str
│  ├─ gender: str
│  └─ profile: dict
├─ bpm: int
├─ tonality
│  ├─ key: str
│  └─ mode: str
├─ color
│  ├─ dominant: str
│  ├─ palette: list[str]
│  └─ wave: dict
├─ fanf
│  ├─ annotation: str
│  └─ narrative: str
├─ suno
│  ├─ prompt: str
│  └─ annotations: list[str]
├─ lyrics
│  ├─ sections: list[dict]
│  └─ full_text: str
└─ diagnostics: dict
```

## Примечания

1. **Все числовые значения** (love, pain, truth, bpm) находятся в диапазоне [0.0, 1.0] для эмоций и [60, 200] для BPM
2. **Теги секций** могут быть: "Verse 1", "Verse 2", "Chorus", "Bridge", "Final Chorus", "Outro", "Intro", "Pre-Chorus"
3. **Жанры** определяются автоматически на основе анализа текста
4. **Цвета** представлены в формате HEX (#RRGGBB)
5. **Тональности** могут быть: C, C#, D, D#, E, F, F#, G, G#, A, A#, B
6. **Лады** могут быть: "major" или "minor"

