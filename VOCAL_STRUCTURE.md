# СТРУКТУРА ОПРЕДЕЛЕНИЯ ВОКАЛА

## Общая структура

```json
{
  "vocal": {
    "gender": "auto" | "male" | "female",
    "type": "spoken" | "sung" | "mixed",
    "tone": "balanced" | "intense" | "soft",
    "style": "spoken-word" | "ballad" | "rock" | ...,
    "dynamics": {
      "section_1": 0.5,
      "section_2": 0.55,
      ...
    },
    "intensity_curve": [0.5, 0.55, 0.45, ...],
    "average_intensity": 0.486,
    "section_techniques": [
      "soft_tenor",
      "expanded_tenor",
      "soft_tenor",
      ...
    ]
  }
}
```

## Процесс формирования вокала

### Шаг 1: Определение базовых параметров

**Источники:**
- `preferred_gender` (параметр пользователя)
- `VocalEngine.detect_voice_gender(text)` (автоматическое определение)
- Анализ текста на наличие грамматических маркеров пола

**Результат:**
```python
voice_gender = "auto" | "male" | "female"
voice_type = "spoken" | "sung"
voice_tone = "balanced" | "intense" | "soft"
voice_style = "spoken-word" | "ballad" | ...
```

### Шаг 2: Анализ эмоций секций

**Источники:**
- `section_intelligence.section_emotions(sections)`
- Эмоциональный профиль каждой секции
- Интенсивность эмоций

**Результат:**
```python
section_emotions_data = [
    {
        "section": "Verse 1",
        "dominant": "sensual",
        "intensity": 0.8,
        "tlp_mean": {"love": 0.75, "pain": 0.25, "truth": 0.0}
    },
    ...
]
```

### Шаг 3: Определение техник для каждой секции

**Функция:** `get_vocal_for_section()`

**Параметры:**
- `section_emotion`: str - доминирующая эмоция секции
- `section_intensity`: float - интенсивность эмоции (0.0-1.0)
- `global_emotion`: str - глобальная эмоция текста
- `genre`: str - музыкальный жанр
- `section_name`: str - название секции (Verse, Chorus, Bridge, etc.)

**Процесс:**

1. **Получение базовых техник из эмоции:**
   ```python
   techniques = get_vocal_for_emotion(section_emotion, section_intensity)
   # Возвращает список техник с весами, отсортированный по релевантности
   ```

2. **Вариативность по типу секции:**
   - **Verse**: более интимный, мягкий вокал
     - Добавляет: `["soft_tenor", "intimate_baritone", "breathy"]`
   - **Chorus**: более расширенный, эмоциональный вокал
     - Добавляет: `["expanded_tenor", "belting", "emotional"]`
   - **Final Chorus**: эмоциональный пик
     - Добавляет: `["powerful_tenor", "belting", "emotional_peak"]`
   - **Bridge**: дыхательный, напряженный вокал
     - Добавляет: `["breathy", "tension", "emotional"]`
   - **Outro**: шёпот, низкая энергия
     - Добавляет: `["whisper", "soft", "low_energy"]`

3. **Жанровые модификации:**
   - **Metal/Rock**: добавляет `["belting", "rasp", "grit"]`
   - **Jazz**: добавляет `["scat_singing", "crooning"]`
   - **Classical/Orchestral**: приоритет академическим техникам

4. **Выбор основной техники:**
   ```python
   primary = techniques[0]  # Первая техника из списка
   if len(techniques) > 1:
       return f"{primary} with {', '.join(techniques[1:3])}"
   return primary
   ```

### Шаг 4: Построение динамики по секциям

**Источники:**
- `VocalEngine.vocal_dynamics(sections, emotion_profile)`
- Интенсивность эмоций в каждой секции
- BPM кривая

**Результат:**
```python
vocal_dynamics = {
    "section_1": 0.5,
    "section_2": 0.55,
    "section_3": 0.45,
    ...
}
```

### Шаг 5: Кривая интенсивности

**Источники:**
- `VocalEngine.vocal_intensity_curve(sections, emotion_profile)`
- Динамика эмоций по секциям

**Результат:**
```python
vocal_curve = [0.5, 0.55, 0.45, 0.55, 0.45, 0.55, 0.35]
average_intensity = sum(vocal_curve) / len(vocal_curve)
```

### Шаг 6: Финальная сборка

**Код:**
```python
vocal_payload = {
    "gender": voice_gender,
    "type": voice_type,
    "tone": voice_tone,
    "style": voice_style,
    "dynamics": vocal_dynamics,
    "intensity_curve": vocal_curve,
    "average_intensity": round(sum(vocal_curve) / max(len(vocal_curve), 1), 3),
    "section_techniques": section_vocals,  # Техники для каждой секции
}
```

## Маппинг эмоций → вокальные техники

### Основные эмоции

#### Love (Любовь)
```python
"love": [
    ("lyric_soprano", 0.3),
    ("soft_female_alto", 0.4),
    ("gentle_male_tenor", 0.3),
    ("breathy", 0.2),
]
```

#### Pain (Боль)
```python
"deep_pain": [
    ("dramatic_baritone", 0.4),
    ("rasp", 0.3),
    ("grit", 0.3),
]
```

#### Sensual (Чувственность)
```python
# Маппится на "love_soft"
"love_soft": [
    ("contralto", 0.4),
    ("soft_tone", 0.4),
    ("close_mic", 0.2),
]
```

#### Nostalgia (Ностальгия)
```python
# Маппится на "sadness"
"sadness": [
    ("baritone", 0.4),
    ("soft", 0.3),
    ("vibrato", 0.3),
]
```

#### Truth (Правда)
```python
"clear_truth": [
    ("tenor", 0.4),
    ("clear", 0.4),
    ("spoken", 0.2),
]
```

## Вариативность по секциям

### Verse (Куплет)
- **Характеристики:** интимный, мягкий, лиричный
- **Техники:** `soft_tenor`, `intimate_baritone`, `breathy`
- **Пример:** "soft_tenor with intimate_baritone, breathy"

### Chorus (Припев)
- **Характеристики:** расширенный, эмоциональный, мощный
- **Техники:** `expanded_tenor`, `belting`, `emotional`
- **Пример:** "expanded_tenor with belting, emotional"

### Final Chorus (Финальный припев)
- **Характеристики:** эмоциональный пик, максимальная интенсивность
- **Техники:** `powerful_tenor`, `belting`, `emotional_peak`
- **Пример:** "powerful_tenor with belting, emotional_peak"

### Bridge (Мост)
- **Характеристики:** дыхательный, напряженный, переходный
- **Техники:** `breathy`, `tension`, `emotional`
- **Пример:** "breathy with tension, emotional"

### Outro (Аутро)
- **Характеристики:** шёпот, низкая энергия, затухание
- **Техники:** `whisper`, `soft`, `low_energy`
- **Пример:** "whisper with soft, low_energy"

## Жанровые модификации

### Metal/Rock
```python
if "metal" in genre or "rock" in genre:
    techniques = ["belting", "rasp", "grit"] + techniques
```

### Jazz
```python
if "jazz" in genre:
    techniques = ["scat_singing", "crooning"] + techniques
```

### Classical/Orchestral
```python
if "classical" in genre or "orchestral" in genre:
    # Приоритет академическим техникам
    academic_techs = [t for t in techniques if any(cat in t for cat in 
                   ["soprano", "tenor", "baritone", "bass", "alto"])]
    if academic_techs:
        techniques = academic_techs + techniques
```

## Полный процесс в коде

```python
# 1. Определение базовых параметров
auto_gender = vocal_engine.detect_voice_gender(text)
voice_gender = preferred_gender if preferred_gender != "auto" else auto_gender

# 2. Анализ эмоций секций
section_emotions_data = section_intelligence.section_emotions(sections)

# 3. Определение техник для каждой секции
section_vocals = []
for idx, sec_emo in enumerate(section_emotions_data):
    sec_emotion = sec_emo.get("dominant", "neutral")
    sec_intensity = sec_emo.get("intensity", 0.5)
    section_name = headers[idx].get("tag") if idx < len(headers) else None
    
    section_vocal = get_vocal_for_section(
        section_emotion=sec_emotion,
        section_intensity=sec_intensity,
        global_emotion=global_emotion,
        genre=style_payload.get("genre"),
        section_name=section_name,
    )
    section_vocals.append(section_vocal)

# 4. Построение динамики
vocal_dynamics = vocal_engine.vocal_dynamics(sections, emotion_profile)

# 5. Кривая интенсивности
vocal_curve = vocal_engine.vocal_intensity_curve(sections, emotion_profile)

# 6. Финальная сборка
vocal_payload = {
    "gender": voice_gender,
    "type": voice_type,
    "tone": voice_tone,
    "style": voice_style,
    "dynamics": vocal_dynamics,
    "intensity_curve": vocal_curve,
    "average_intensity": round(sum(vocal_curve) / len(vocal_curve), 3),
    "section_techniques": section_vocals,
}
```

## Визуальная схема процесса

```
Текст
  │
  ├─→ VocalEngine.detect_voice_gender()
  │   └─→ voice_gender: "auto" | "male" | "female"
  │
  ├─→ section_intelligence.section_emotions()
  │   └─→ section_emotions_data: [
  │         {"section": "Verse 1", "dominant": "sensual", "intensity": 0.8},
  │         {"section": "Chorus", "dominant": "love", "intensity": 0.9},
  │         ...
  │       ]
  │
  ├─→ Для каждой секции:
  │   │
  │   ├─→ get_vocal_for_emotion(section_emotion, section_intensity)
  │   │   └─→ Базовые техники из EMOTION_TO_VOCAL_MAP
  │   │
  │   ├─→ Вариативность по section_name:
  │   │   ├─→ Verse → ["soft_tenor", "intimate_baritone", "breathy"]
  │   │   ├─→ Chorus → ["expanded_tenor", "belting", "emotional"]
  │   │   ├─→ Bridge → ["breathy", "tension", "emotional"]
  │   │   └─→ Outro → ["whisper", "soft", "low_energy"]
  │   │
  │   ├─→ Жанровые модификации:
  │   │   ├─→ Metal/Rock → ["belting", "rasp", "grit"]
  │   │   ├─→ Jazz → ["scat_singing", "crooning"]
  │   │   └─→ Classical → академические техники
  │   │
  │   └─→ section_vocals.append(primary_technique)
  │
  ├─→ vocal_engine.vocal_dynamics()
  │   └─→ vocal_dynamics: {"section_1": 0.5, "section_2": 0.55, ...}
  │
  ├─→ vocal_engine.vocal_intensity_curve()
  │   └─→ vocal_curve: [0.5, 0.55, 0.45, ...]
  │
  └─→ Сборка vocal_payload
      └─→ {
            "gender": ...,
            "type": ...,
            "tone": ...,
            "style": ...,
            "dynamics": ...,
            "intensity_curve": ...,
            "average_intensity": ...,
            "section_techniques": [...]
          }
```

## Пример реального результата

```json
{
  "vocal": {
    "gender": "auto",
    "type": "spoken",
    "tone": "balanced",
    "style": "spoken-word",
    "dynamics": {
      "section_1": 0.5,
      "section_2": 0.55,
      "section_3": 0.45,
      "section_4": 0.55,
      "section_5": 0.45,
      "section_6": 0.55,
      "section_7": 0.35
    },
    "intensity_curve": [0.5, 0.55, 0.45, 0.55, 0.45, 0.55, 0.35],
    "average_intensity": 0.486,
    "section_techniques": [
      "soft_tenor with intimate_baritone, breathy",
      "expanded_tenor with belting, emotional",
      "soft_tenor with intimate_baritone, breathy",
      "expanded_tenor with belting, emotional",
      "breathy with tension, emotional",
      "powerful_tenor with belting, emotional_peak",
      "whisper with soft, low_energy"
    ]
  }
}
```

## Категории вокальных техник

### 1. Академический (Классический)
- soprano, mezzo_soprano, alto, tenor, baritone, bass
- Различные подтипы: lyric, dramatic, coloratura, etc.

### 2. Популярная музыка
- head_voice, chest_voice, mixed_voice, belting, falsetto

### 3. Джазовый
- scat_singing, vocalese, crooning, growl, blue_notes

### 4. Этнический
- throat_singing, yodel, cante_flamenco, sean_nos

### 5. Экстремальный
- false_cord_scream, fry_scream, death_growl, harsh_vocals

### 6. Экспериментальный
- overtone_singing, beatboxing, multiphonics, extended_vocal_techniques

## Примечания

1. **Вариативность:** Каждая секция получает свою технику на основе эмоций и типа секции
2. **Интенсивность:** Учитывается интенсивность эмоций для выбора техники
3. **Жанр:** Жанр влияет на модификацию техник (metal → belting, jazz → scat)
4. **Секции:** Разные типы секций (Verse, Chorus, Bridge, Outro) имеют свои характеристики
5. **Глобальная эмоция:** Учитывается общая эмоциональная направленность текста

