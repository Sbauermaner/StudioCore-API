# Иерархия Элементов - Эмоции, Цвета, BPM, Key, RDE, Вокалы, Лирика, Жанры

Полная документация иерархий и взаимосвязей между эмоциями, цветами, BPM, тональностями, RDE, вокалами, лирикой и жанрами музыки.

---

## 1. Общая Схема Взаимосвязей

```
┌─────────────────────────────────────────────────────────────┐
│                    ЭМОЦИИ (Emotions)                        │
│  Базовый уровень - определяет все остальное                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   ЦВЕТА      │  │     BPM      │  │     KEY     │
│  (Colors)    │  │  (Beats/Min) │  │ (Tonalities)│
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │
       └─────────┬───────┴──────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   RDE           │
        │ (Resonance/     │
        │  Fracture/      │
        │  Entropy)       │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   ВОКАЛЫ     │  │    ЖАНРЫ    │
│  (Vocals)    │  │  (Genres)   │
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                ┌──────────────┐
                │    ЛИРИКА    │
                │   (Lyrics)   │
                └──────────────┘
```

---

## 2. Иерархия Эмоций

### 2.1 Базовые Эмоции (Core Emotions)

```
Эмоции
│
├── Положительные
│   ├── joy (радость)
│   ├── happiness (счастье)
│   ├── delight (восторг)
│   ├── love (любовь)
│   │   ├── love_soft (мягкая любовь)
│   │   ├── love_deep (глубокая любовь)
│   │   ├── infinite_love (бесконечная любовь)
│   │   ├── healing_love (исцеляющая любовь)
│   │   ├── maternal_love (материнская любовь)
│   │   ├── radiant_love (сияющая любовь)
│   │   ├── longing_love (тоска по любви)
│   │   ├── gentle_love (нежная любовь)
│   │   └── unconditional_love (безусловная любовь)
│   ├── peace (покой)
│   ├── calm (спокойствие)
│   ├── serenity (безмятежность)
│   ├── hope (надежда)
│   ├── trust (доверие)
│   ├── affection (привязанность)
│   ├── compassion (сострадание)
│   ├── warmth (тепло)
│   ├── admiration (восхищение)
│   └── relief (облегчение)
│
├── Отрицательные
│   ├── sadness (печаль)
│   ├── sorrow (скорбь)
│   ├── melancholy (меланхолия)
│   ├── loneliness (одиночество)
│   ├── grief (горе)
│   ├── regret (сожаление)
│   ├── guilt (вина)
│   ├── shame (стыд)
│   ├── pain (боль)
│   │   ├── deep_pain (глубокая боль)
│   │   ├── phantom_pain (фантомная боль)
│   │   ├── burning_pain (жгучая боль)
│   │   ├── soul_pain (душевная боль)
│   │   ├── silent_pain (тихая боль)
│   │   ├── explosive_pain (взрывная боль)
│   │   └── collapsing_pain (коллапсирующая боль)
│   ├── anger (гнев)
│   ├── rage (ярость)
│   │   └── rage_extreme (экстремальная ярость)
│   ├── aggression (агрессия)
│   ├── bitterness (горечь)
│   ├── jealousy (ревность)
│   ├── envy (зависть)
│   ├── betrayal (предательство)
│   ├── resentment (обида)
│   ├── anxiety (тревога)
│   ├── panic (паника)
│   ├── fear (страх)
│   ├── disgust (отвращение)
│   ├── aversion (неприязнь)
│   ├── confusion (замешательство)
│   ├── frustration (фрустрация)
│   └── disappointment (разочарование)
│
├── Специальные
│   ├── truth (истина)
│   │   ├── clear_truth (ясная истина)
│   │   ├── cold_truth (холодная истина)
│   │   ├── sharp_truth (острая истина)
│   │   ├── brutal_honesty (жестокая честность)
│   │   ├── revelation (откровение)
│   │   └── righteous_truth (праведная истина)
│   ├── epic (эпическое)
│   ├── awe (благоговение)
│   ├── wonder (удивление)
│   ├── nostalgia (ностальгия)
│   ├── irony (ирония)
│   ├── conflict (конфликт)
│   ├── resolve (решимость)
│   ├── determination (определенность)
│   ├── gothic_dark (готическая тьма)
│   ├── dark_poetic (темная поэзия)
│   ├── dark_romantic (темный романтизм)
│   ├── hiphop_conflict (хип-хоп конфликт)
│   ├── street_power (уличная сила)
│   └── neutral (нейтральное)
│
└── Ритмические / Структурные
    ├── calm_flow (спокойный поток)
    ├── warm_pulse (теплый пульс)
    ├── cold_pulse (холодный пульс)
    ├── frantic (безумный)
    ├── trembling (дрожащий)
    ├── escalating (эскалирующий)
    ├── descending (нисходящий)
    ├── pressure (давление)
    ├── static_tension (статическое напряжение)
    └── breathless (бездыханный)
```

### 2.2 Эмоциональные Кластеры

```
Кластеры Эмоций (из emotion_model_v1.json)
│
├── rage (ярость)
│   └── anger, aggression, rage_extreme
│
├── despair (отчаяние)
│   └── sadness, grief, sorrow, melancholy
│
├── tender (нежность)
│   └── love, love_soft, affection, compassion
│
├── hope (надежда)
│   └── hope, peace, calm, serenity
│
└── narrative (нарративное)
    └── truth, epic, awe, wonder
```

---

## 3. Иерархия Цветов

### 3.1 Эмоция → Цвет Маппинг

```
EMOTION_COLOR_MAP
│
├── Core Emotions
│   ├── truth → ["#4B0082", "#6C1BB1", "#5B3FA8"] (индиго/фиолетовый)
│   ├── love → ["#FF7AA2"] (розовый)
│   ├── pain → ["#DC143C", "#2F1B25", "#0A1F44"] (красный/темный)
│   ├── joy → ["#FFD93D"] (желтый)
│   ├── sadness → ["#5A6A86"] (серо-синий)
│   ├── anger → ["#D62828"] (красный)
│   └── fear → ["#4B3F72"] (темно-фиолетовый)
│
├── Love Spectrum
│   ├── love_soft → ["#FFC0CB", "#FFB6C1", "#FFE4E1"] (светло-розовый)
│   ├── love_deep → ["#C2185B", "#880E4F", "#DC143C"] (темно-розовый)
│   ├── infinite_love → ["#FF6FA8"]
│   ├── healing_love → ["#FF9CCB"]
│   ├── maternal_love → ["#FFB7DA"]
│   ├── radiant_love → ["#FFD1E8"]
│   ├── longing_love → ["#E88AB7"]
│   ├── gentle_love → ["#FFCEDA"]
│   └── unconditional_love → ["#FFA3C4"]
│
├── Pain Spectrum
│   ├── deep_pain → ["#2A0000"]
│   ├── phantom_pain → ["#3A1A1A"]
│   ├── burning_pain → ["#660000"]
│   ├── soul_pain → ["#400021"]
│   ├── silent_pain → ["#2E1A27"]
│   ├── explosive_pain → ["#7F0000"]
│   └── collapsing_pain → ["#1A0000"]
│
├── Truth Spectrum
│   ├── clear_truth → ["#AEE3FF"]
│   ├── cold_truth → ["#6DA8C8"]
│   ├── sharp_truth → ["#3A5E73"]
│   ├── brutal_honesty → ["#1A3F56"]
│   ├── revelation → ["#8FE1FF"]
│   └── righteous_truth → ["#0099CC"]
│
├── Joy Spectrum
│   ├── joy_bright → ["#FFD700", "#FFFF00", "#FFF59D"] (золотой/желтый)
│   ├── happiness → ["#FFE97F"]
│   └── delight → ["#FFF2A6"]
│
├── Peace Spectrum
│   ├── peace → ["#8FD3FE"]
│   ├── calm → ["#8FC1E3"]
│   ├── serenity → ["#A8D8FF"]
│   └── calm_flow → ["#9FD3FF"]
│
├── Sorrow Spectrum
│   ├── sorrow → ["#3E5C82"]
│   ├── sadness → ["#4A6FA5"]
│   └── melancholy → ["#596E94"]
│
├── Gothic/Dark Spectrum
│   ├── gothic_dark → ["#2C1A2E", "#1B1B2F", "#000000"] (черный)
│   ├── dark_poetic → ["#2C1A2E", "#3F2A44", "#1B1B2F"]
│   └── dark → ["#111111", "#2F2F2F", "#0B0B0B"]
│
└── Special
    ├── epic → ["#8A2BE2", "#4B0082", "#FF00FF"] (фиолетовый/магента)
    ├── nostalgia → ["#FFD1A1", "#D8BFD8", "#E6E6FA"]
    └── neutral → ["#FFFFFF", "#B0BEC5", "#ECEFF1"] (белый/серый)
```

### 3.2 Цвет → BPM Маппинг

```
EMOTION_COLOR_TO_BPM
│
├── LOVE цвета → BPM 60-100 (лирические)
│   ├── #FF7AA2 → (70, 100, 85)      # love
│   ├── #FFC0CB → (60, 100, 80)      # love_soft
│   ├── #FFB6C1 → (60, 100, 80)      # love_soft
│   ├── #FFE4E1 → (60, 100, 80)      # love_soft
│   ├── #C2185B → (70, 95, 82)       # love_deep
│   ├── #880E4F → (70, 95, 82)       # love_deep
│   └── #DC143C → (70, 95, 82)       # love_deep
│
├── PAIN/GOTHIC цвета → BPM 50-80 (низкие)
│   ├── #2C1A2E → (50, 80, 65)       # gothic_poetry
│   ├── #1B1B2F → (50, 80, 65)       # gothic_poetry
│   ├── #000000 → (50, 80, 65)       # gothic_poetry
│   ├── #2F1B25 → (50, 80, 65)       # pain
│   ├── #0A1F44 → (50, 80, 65)       # pain
│   ├── #8B0000 → (50, 80, 65)       # rage_extreme
│   └── #111111 → (50, 80, 65)       # dark
│
├── TRUTH цвета → BPM 60-90 (средние)
│   ├── #4B0082 → (60, 90, 75)       # truth
│   ├── #6C1BB1 → (60, 90, 75)       # truth
│   ├── #5B3FA8 → (60, 90, 75)       # truth
│   ├── #AEE3FF → (60, 90, 75)       # clear_truth
│   └── #6DA8C8 → (60, 90, 75)       # cold_truth
│
├── JOY цвета → BPM 100-140 (высокие)
│   ├── #FFD93D → (100, 140, 120)    # joy
│   ├── #FFD700 → (100, 140, 120)    # joy_bright
│   ├── #FFFF00 → (100, 140, 120)    # joy_bright
│   └── #FFF59D → (100, 140, 120)    # joy_bright
│
├── PEACE цвета → BPM 50-100 (средние)
│   ├── #40E0D0 → (50, 100, 80)      # peace
│   ├── #E0F7FA → (50, 100, 80)      # peace
│   ├── #FFFFFF → (50, 100, 80)      # neutral
│   ├── #9FD3FF → (50, 100, 80)      # calm_flow
│   └── #8FC1E3 → (50, 100, 80)      # calm
│
├── SORROW цвета → BPM 50-80 (низкие)
│   ├── #3E5C82 → (50, 80, 65)       # sorrow
│   ├── #4A6FA5 → (50, 80, 65)       # sadness
│   └── #596E94 → (50, 80, 65)       # melancholy
│
├── NOSTALGIA цвета → BPM 60-85 (средние)
│   ├── #D8BFD8 → (60, 85, 72)       # nostalgia
│   ├── #E6E6FA → (60, 85, 72)       # nostalgia
│   └── #C3B1E1 → (60, 85, 72)       # nostalgia
│
└── EPIC цвета → BPM 70-100 (средние)
    ├── #8A2BE2 → (70, 100, 85)      # epic
    └── #FF00FF → (70, 100, 85)       # epic
```

### 3.3 Цвет → Key Маппинг

```
EMOTION_COLOR_TO_KEY
│
├── LOVE цвета → Major ключи
│   ├── #FF7AA2 → ["C major", "G major", "A major", "E major", "D major"]
│   ├── #FFC0CB → ["C major", "G major", "A minor", "D minor", "F major"]
│   ├── #FFB6C1 → ["C major", "G major", "A minor", "F major"]
│   ├── #FFE4E1 → ["C major", "G major", "A minor", "F major"]
│   ├── #C2185B → ["C major", "G major", "D major", "A major", "E major"]
│   ├── #880E4F → ["C major", "G major", "D major", "A major", "E major"]
│   └── #DC143C → ["C major", "G major", "D major", "A major", "E major"]
│
├── PAIN/GOTHIC цвета → Minor ключи
│   ├── #2C1A2E → ["D minor", "A minor", "E minor", "B minor", "G minor"]
│   ├── #1B1B2F → ["D minor", "A minor", "E minor", "B minor", "G minor"]
│   ├── #000000 → ["D minor", "A minor", "E minor", "B minor", "G minor"]
│   ├── #2F1B25 → ["D minor", "A minor", "E minor", "B minor"]
│   ├── #0A1F44 → ["D minor", "A minor", "E minor", "B minor"]
│   ├── #8B0000 → ["D minor", "A minor", "E minor", "B minor"]
│   └── #111111 → ["D minor", "A minor", "E minor", "B minor"]
│
├── TRUTH цвета → Minor ключи (исповедальность)
│   ├── #4B0082 → ["C minor", "G minor", "A minor", "F minor", "D minor"]
│   ├── #6C1BB1 → ["C minor", "G minor", "A minor", "F minor", "D minor"]
│   ├── #5B3FA8 → ["C minor", "G minor", "A minor", "F minor", "D minor"]
│   ├── #AEE3FF → ["C minor", "G minor", "A minor", "F minor", "D minor"]
│   └── #6DA8C8 → ["C minor", "G minor", "A minor", "F minor", "D minor"]
│
├── JOY цвета → Major ключи
│   ├── #FFD93D → ["C major", "G major", "A minor", "F major", "D major"]
│   ├── #FFD700 → ["C major", "G major", "A minor", "F major"]
│   ├── #FFFF00 → ["C major", "G major", "A minor", "F major"]
│   └── #FFF59D → ["C major", "G major", "A minor", "F major"]
│
├── PEACE цвета → Major/Minor ключи
│   ├── #40E0D0 → ["C major", "F major", "A minor", "D minor"]
│   ├── #E0F7FA → ["C major", "F major", "A minor", "D minor"]
│   ├── #FFFFFF → ["C major", "A minor"]
│   ├── #9FD3FF → ["C major", "F major", "A minor", "D minor"]
│   └── #8FC1E3 → ["C major", "F major", "A minor", "D minor"]
│
├── SORROW цвета → Minor ключи
│   ├── #3E5C82 → ["D minor", "A minor", "E minor", "G minor"]
│   ├── #4A6FA5 → ["D minor", "A minor", "E minor", "B minor"]
│   └── #596E94 → ["A minor", "D minor", "E minor", "G minor", "C minor"]
│
├── NOSTALGIA цвета → Minor ключи
│   ├── #D8BFD8 → ["A minor", "D minor", "E minor", "G minor", "C minor"]
│   ├── #E6E6FA → ["A minor", "D minor", "E minor", "G minor", "C minor"]
│   └── #C3B1E1 → ["A minor", "D minor", "E minor", "G minor", "C minor"]
│
└── EPIC цвета → Major ключи
    ├── #8A2BE2 → ["C major", "G major", "D major", "A major"]
    └── #FF00FF → ["C major", "G major", "D major", "A major"]
```

---

## 4. Иерархия BPM

### 4.1 BPM Диапазоны по Эмоциям

```
BPM Иерархия
│
├── Очень Низкие (40-60)
│   └── Используется для: deep_pain, collapsing_pain, gothic_dark
│
├── Низкие (50-80)
│   ├── PAIN эмоции → 50-80 BPM
│   ├── GOTHIC эмоции → 50-80 BPM
│   ├── SORROW эмоции → 50-80 BPM
│   └── Используется для: sadness, melancholy, sorrow, pain, gothic
│
├── Средние-Низкие (60-90)
│   ├── TRUTH эмоции → 60-90 BPM
│   ├── NOSTALGIA эмоции → 60-85 BPM
│   └── Используется для: truth, nostalgia, confessional
│
├── Средние (70-100)
│   ├── LOVE эмоции → 60-100 BPM (default: 85)
│   ├── PEACE эмоции → 50-100 BPM (default: 80)
│   ├── EPIC эмоции → 70-100 BPM (default: 85)
│   └── Используется для: love, peace, epic, lyrical
│
├── Средние-Высокие (100-120)
│   └── Используется для: joy, pop, dance
│
├── Высокие (100-140)
│   ├── JOY эмоции → 100-140 BPM (default: 120)
│   └── Используется для: joy_bright, pop, electronic
│
└── Очень Высокие (140-200)
    └── Используется для: rage, aggression, extreme metal
```

### 4.2 BPM Расчет на основе Эмоций

```
compute_bpm_base(clusters)
│
├── Базовый BPM: 92.0
│
├── Модификаторы:
│   ├── aggression (rage) → +40.0 * value
│   ├── sadness → -20.0 * value
│   ├── hope → +15.0 * value
│   └── awe → +10.0 * value
│
├── Кластерные модификаторы:
│   └── Для каждого кластера: +value * cluster.bpm_delta * 0.25
│
└── Ограничение: clamp(60.0, 190.0)
```

### 4.3 BPM Расчет на основе TLP

```
_density_bpm() с TLP коррекцией
│
├── Базовый BPM (из текста)
│
├── TLP модификаторы:
│   ├── Pain boost → +pain * 50 * emotion_weight
│   ├── Love smoothing → -love * 25 * emotion_weight
│   └── Truth drive → +truth * 20 * emotion_weight
│
└── CF (Conscious Frequency) коррекция:
    └── + (cf - 0.8) * 100 * emotion_weight
```

---

## 5. Иерархия Key (Тональностей)

### 5.1 Key Определение на основе Эмоций

```
compute_key_and_mode(clusters)
│
├── Базовое правило:
│   └── sadness > 0.55 → minor
│   └── Иначе → major
│
├── Love/Hope коррекция:
│   └── love + hope + tenderness > 0.55 → major
│
├── Awe коррекция:
│   └── awe > 0.7 → modal_phrygian_lydian (phrygian mode)
│
└── Rage коррекция:
    └── rage > 0.7 → minor_dark (dark_minor mode)
```

### 5.2 Key Модификация на основе Цвета

```
apply_emotion_modulation() с цветом
│
├── Red/Crimson/Scarlet → minor, shift -2 (темнее)
├── Blue/Navy/Cyan → minor, shift -1
├── Yellow/Gold/Amber → major, shift +2 (ярче)
├── Green/Emerald → neutral (без изменений)
├── Purple/Violet → phrygian (драматично)
└── Black/Gray → minor, shift -3 (самый темный)
```

### 5.3 Key Модификация на основе Arousal

```
Arousal-based semitone shift:
│
├── arousal > 0.6 → shift +1 (выше)
└── arousal < 0.3 → shift -1 (ниже)
```

### 5.4 Key Модификация на основе Valence

```
Valence-based mode:
│
├── valence > 0.3 → major
└── valence < -0.3 → minor
```

---

## 6. Иерархия RDE (Resonance/Fracture/Entropy)

### 6.1 RDE Компоненты

```
RDE (Rhythm Dynamics Emotion)
│
├── Resonance (Резонанс)
│   ├── Описание: Повторения, рефрены, цикличность
│   ├── Диапазон: 0.0 - 1.0
│   └── Высокий резонанс → предсказуемость, структурированность
│
├── Fracture (Фрактура)
│   ├── Описание: Структурные разрывы, неожиданные переходы
│   ├── Диапазон: 0.0 - 1.0
│   └── Высокая фрактура → динамичность, неожиданность
│
└── Entropy (Энтропия)
    ├── Описание: Разнообразие, непредсказуемость токенов
    ├── Диапазон: 0.0 - 1.0
    └── Высокая энтропия → разнообразие, сложность
```

### 6.2 RDE → Эмоции Маппинг

```
RDE → Emotion
│
├── Высокий Resonance + Низкая Fracture → peace, calm
├── Высокая Fracture + Низкий Resonance → tension, conflict
├── Высокая Entropy → complexity, wonder
└── Низкая Entropy → simplicity, clarity
```

### 6.3 RDE Smoothing Factors

```
RDE Smoothing (для низких эмоций)
│
├── rde_resonance_smoothing: 0.4
├── rde_fracture_smoothing: 0.3
└── rde_entropy_smoothing: 0.7
```

---

## 7. Иерархия Вокалов

### 7.1 Эмоция → Вокал Маппинг

```
EMOTION_TO_VOCAL_MAP
│
├── Joy / Happiness
│   ├── joy → ["lyric_soprano", "falsetto", "head_voice", "bright_tone"]
│   ├── joy_bright → ["coloratura_soprano", "whistle_register", "falsetto"]
│   ├── happiness → ["lyric_tenor", "mixed_voice", "belting"]
│   └── delight → ["soprano", "head_voice", "bright_tone"]
│
├── Calm / Serenity
│   ├── calm → ["lyric_baritone", "soft_tone", "breathy"]
│   ├── serenity → ["contralto", "head_voice", "ethereal"]
│   └── trust → ["warm_baritone", "mixed_voice", "resonant"]
│
├── Love
│   ├── love → ["lyric_soprano", "soft_female_alto", "gentle_male_tenor", "breathy"]
│   ├── love_soft → ["contralto", "soft_tone", "close_mic"]
│   ├── love_deep → ["baritone", "chest_voice", "warm"]
│   ├── infinite_love → ["soprano", "tenor", "layered_harmonies"]
│   ├── healing_love → ["lyric_soprano", "ethereal", "angelic"]
│   ├── maternal_love → ["contralto", "warm", "soft"]
│   ├── radiant_love → ["coloratura_soprano", "bright_tone", "head_voice"]
│   ├── longing_love → ["lyric_tenor", "vibrato", "emotional"]
│   ├── gentle_love → ["mezzo_soprano", "soft", "breathy"]
│   └── unconditional_love → ["soprano", "baritone", "choir"]
│
├── Sadness
│   ├── sadness → ["baritone", "soft", "vibrato"]
│   ├── disappointment → ["lyric_tenor", "soft_cry", "emotional"]
│   ├── melancholy → ["baritone", "soft", "warm"]
│   ├── sorrow → ["dramatic_baritone", "vibrato", "emotional"]
│   ├── loneliness → ["tenor", "soft", "distant"]
│   ├── grief → ["bass", "dramatic", "powerful"]
│   ├── regret → ["baritone", "soft", "vibrato"]
│   ├── guilt → ["tenor", "whisper", "soft"]
│   └── shame → ["mezzo_soprano", "soft", "breathy"]
│
├── Pain
│   ├── deep_pain → ["dramatic_baritone", "rasp", "grit"]
│   ├── phantom_pain → ["contralto", "ethereal", "distant"]
│   ├── burning_pain → ["dramatic_tenor", "belting", "rasp"]
│   ├── soul_pain → ["bass", "dramatic", "powerful"]
│   ├── silent_pain → ["mezzo_soprano", "whisper", "soft"]
│   ├── explosive_pain → ["dramatic_soprano", "belting", "scream"]
│   └── collapsing_pain → ["bass", "guttural", "low"]
│
├── Rage / Anger
│   ├── rage → ["dramatic_tenor", "harsh", "scream"]
│   ├── rage_extreme → ["death_growl", "false_cord_scream", "harsh_vocals"]
│   ├── aggression → ["baritone", "grit", "rasp"]
│   └── anger → ["dramatic_baritone", "belting", "rasp"]
│
├── Truth
│   ├── truth → ["tenor", "clear", "resonant"]
│   ├── clear_truth → ["lyric_tenor", "clear", "bright"]
│   └── cold_truth → ["baritone", "clear", "neutral"]
│
└── Epic / Special
    ├── epic → ["layered_choir", "dramatic", "powerful"]
    └── awe → ["soprano", "ethereal", "angelic"]
```

### 7.2 Вокал → Жанр Влияние

```
Vocal Selection влияет на Genre:
│
├── Female vocals (joy_peace > anger_epic) → lyrical, pop, soft
└── Male vocals (anger_epic > joy_peace) → rock, metal, hard
```

---

## 8. Иерархия Лирики

### 8.1 Лирические Формы

```
Лирические Формы
│
├── Баллада (ballad)
│   ├── structure_weight: 0.35
│   ├── emotion_weight: 0.40
│   ├── lexicon_weight: 0.15
│   └── narrative_weight: 0.10
│
├── Ода (ode)
│   ├── structure_weight: 0.30
│   ├── emotion_weight: 0.35
│   ├── lexicon_weight: 0.25
│   └── narrative_weight: 0.10
│
├── Сонет (sonnet)
│   ├── structure_weight: 0.45
│   ├── emotion_weight: 0.30
│   ├── lexicon_weight: 0.15
│   └── narrative_weight: 0.10
│
├── Притча (parable)
│   ├── structure_weight: 0.25
│   ├── emotion_weight: 0.25
│   ├── lexicon_weight: 0.20
│   └── narrative_weight: 0.30
│
├── Реп текст (rap_text)
│   ├── structure_weight: 0.20
│   ├── emotion_weight: 0.40
│   ├── lexicon_weight: 0.30
│   └── narrative_weight: 0.10
│
├── Spoken Word
│   ├── structure_weight: 0.20
│   ├── emotion_weight: 0.45
│   ├── lexicon_weight: 0.25
│   └── narrative_weight: 0.10
│
└── Верлибр (free verse)
    ├── structure_weight: 0.15
    ├── emotion_weight: 0.45
    ├── lexicon_weight: 0.25
    └── narrative_weight: 0.15
```

### 8.2 Лирика → Эмоции Влияние

```
Lyrical Emotion влияет на:
│
├── Domain Selection
│   └── lyrical_emotion_score → lyrical domain boost
│
└── Genre Selection
    └── Высокий lyrical_emotion_score → lyrical genres
```

---

## 9. Иерархия Жанров Музыки

### 9.1 Домены Жанров

```
Genre Domains
│
├── hard (rock/metal/rap/агрессия)
│   ├── Статистика: Major: 11, Minor: 63, BPM: 128.8
│   ├── Характеристики: быстрый, преимущественно minor
│   └── Жанры: rock, metal, punk, rap, hip_hop, drill, trap
│
├── electronic (edm/techno/trance/dnb)
│   ├── Статистика: Major: 21, Minor: 14, BPM: 134.9
│   ├── Характеристики: очень быстрый, смешанный
│   └── Жанры: edm, techno, trance, dnb, dubstep, house, bass
│
├── jazz (jazz/swing/bebop/nu_jazz)
│   ├── Статистика: Major: 20, Minor: 0, BPM: 116.8
│   ├── Характеристики: средний, только major
│   └── Жанры: jazz, swing, bebop, nu_jazz
│
├── lyrical (поэтическая/песенная лирика)
│   ├── Статистика: Major: 30, Minor: 6, BPM: 78.2
│   ├── Характеристики: медленный, преимущественно major
│   └── Жанры: ballad, ode, sonnet, lyrical_song, chanson
│
├── cinematic (score/epic/trailer)
│   ├── Статистика: Major: 1, Minor: 10, BPM: 80.0
│   ├── Характеристики: медленный, преимущественно minor
│   └── Жанры: cinematic, orchestral, epic, score
│
├── comedy (комедийная музыка/пародии)
│   └── Жанры: comedy_rock, parody, humorous
│
└── soft (спокойные жанры)
    ├── Статистика: Major: 12, Minor: 1, BPM: 91.9
    ├── Характеристики: средний, преимущественно major
    └── Жанры: folk, ambient, lofi, chill, dream, soft, ballad
```

### 9.2 Эмоция → Жанр Маппинг

```
EMOTION_GROUPS (GenreRoutingEngine)
│
├── rage → ["metal", "thrash_metal", "deathcore", "industrial_metal", "drill", "dark_hiphop"]
├── rage_extreme → ["black_metal", "death_metal", "martial_industrial", "ideological_drama"]
├── love → ["romantic_ballad", "lyrical", "soul", "R&B", "soft_pop"]
├── love_soft → ["acoustic_poem", "folk", "indie_soft"]
├── love_deep → ["neoclassical_romantic", "string_ballad", "ambient_love"]
├── joy → ["pop", "dance_pop", "electropop", "funk", "disco"]
├── sadness → ["darkwave", "post_punk", "coldwave", "neo_folk"]
├── melancholy → ["chamber_dark", "neoclassical_dark", "minimal_piano"]
├── disappointment → ["lowfi", "dark_indie", "tragic_poem"]
├── gothic_dark → ["gothic_rock", "dark_cabaret", "neoclassical_darkwave", "ethereal_dark"]
├── dark_poetic → ["poetic_darkwave", "baroque_dark", "dramatic_ballad"]
├── hiphop_conflict → ["hardcore_rap", "east_coast", "drill", "rage_rap"]
├── street_power → ["old_school_hiphop", "boom_bap", "trap", "g-funk"]
├── fear → ["industrial_dark", "horror_synth", "martial_dark"]
├── hope → ["orchestral_cinematic", "epic_light", "uplifting"]
├── peace → ["ambient_light", "meditation", "soft_world"]
└── neutral → ["cinematic_neutral", "soft_ambient"]
```

### 9.3 Эмоция → Жанр Bias (Genre Bias)

```
compute_genre_bias(emotion_vector)
│
├── anger ↑
│   ├── rock_metal: +0.65 * anger
│   ├── hip_hop: +0.55 * anger
│   ├── jazz: -0.45 * anger
│   ├── folk: -0.35 * anger
│   └── pop: -0.35 * anger
│
├── sadness ↑
│   ├── gothic: +0.60 * sadness
│   ├── folk: +0.28 * sadness
│   ├── edm: -0.38 * sadness
│   └── pop: -0.28 * sadness
│
├── awe ↑
│   ├── orchestral: +0.70 * awe
│   └── hip_hop: -0.28 * awe
│
├── joy ↑
│   ├── pop: +0.50 * joy
│   ├── edm: +0.40 * joy
│   └── gothic: -0.30 * joy
│
├── pain ↑
│   ├── gothic: +0.55 * pain
│   └── pop: -0.25 * pain
│
└── love ↑
    ├── lyrical: +0.60 * love
    ├── pop: +0.30 * love
    └── metal: -0.40 * love
```

### 9.4 Цвет → Домен Boost

```
color_to_domain_boost
│
├── LOVE цвета → lyrical (+0.12 to +0.18)
├── PAIN/GOTHIC цвета → hard (+0.12 to +0.20)
├── TRUTH цвета → lyrical/cinematic (+0.12 to +0.15)
├── JOY цвета → electronic (+0.15 to +0.20)
├── PEACE цвета → soft (+0.10 to +0.15)
├── EPIC цвета → cinematic (+0.18 to +0.20)
├── NOSTALGIA цвета → lyrical (+0.12)
└── SORROW цвета → lyrical (+0.12 to +0.15)
```

### 9.5 Эмоция → Домен Boost

```
emotion_to_domain_boost
│
├── love → lyrical (+0.20)
├── love_soft → lyrical (+0.18)
├── love_deep → lyrical (+0.22)
├── pain → hard (+0.18)
├── gothic_dark → hard (+0.20)
├── dark → hard (+0.16)
├── truth → lyrical (+0.15)
├── joy → electronic (+0.18)
├── joy_bright → electronic (+0.20)
├── peace → soft (+0.15)
├── calm_flow → soft (+0.12)
├── epic → cinematic (+0.20)
├── nostalgia → lyrical (+0.12)
├── sorrow → lyrical (+0.15)
├── sadness → lyrical (+0.12)
├── melancholy → lyrical (+0.12)
├── rage → hard (+0.18)
├── rage_extreme → hard (+0.20)
└── anger → hard (+0.16)
```

---

## 10. Полная Матрица Взаимосвязей

### 10.1 Эмоция → Все Элементы

```
Эмоция (например: "love")
│
├── → Цвет: #FF7AA2 (розовый)
│   └── → BPM: (70, 100, 85)
│   └── → Key: ["C major", "G major", "A major", "E major", "D major"]
│
├── → BPM: 60-100 (лирический диапазон)
│   └── Базовый: 92.0
│   └── Модификаторы: +love * 25 * emotion_weight (smoothing)
│
├── → Key: Major (love + hope > 0.55)
│   └── Предпочтительные: C, G, A, E, D major
│
├── → RDE:
│   ├── Resonance: средний (лирические повторения)
│   ├── Fracture: низкий (плавные переходы)
│   └── Entropy: средний
│
├── → Вокал: ["lyric_soprano", "soft_female_alto", "gentle_male_tenor", "breathy"]
│   └── Интенсивность влияет на выбор техник
│
├── → Лирика: lyrical формы (ballad, ode, sonnet)
│   └── emotion_weight: 0.40 (высокий)
│
└── → Жанр:
    ├── Domain: lyrical (+0.20 boost)
    ├── Жанры: ["romantic_ballad", "lyrical", "soul", "R&B", "soft_pop"]
    └── Bias: lyrical +0.60, pop +0.30, metal -0.40
```

### 10.2 Цвет → Все Элементы

```
Цвет (например: #FF7AA2 - love)
│
├── → BPM: (70, 100, 85) - min, max, default
│
├── → Key: ["C major", "G major", "A major", "E major", "D major"]
│
├── → Домен: lyrical (+0.15 boost)
│
└── → Жанр: lyrical genres (romantic_ballad, lyrical_song)
```

### 10.3 BPM → Все Элементы

```
BPM (например: 85)
│
├── → Эмоция: Средний BPM → love, peace, lyrical emotions
│
├── → Key: Влияет на выбор тональности
│   └── Формула: index_shift = (bpm / 15) + (pain * 5) + (truth * 2) % 12
│
├── → Жанр:
│   ├── 50-80 → gothic, darkwave, ballad
│   ├── 60-100 → lyrical, folk, acoustic
│   ├── 100-140 → pop, electronic, dance
│   └── 140+ → metal, hardcore, extreme
│
└── → Вокал: Влияет на интенсивность техник
```

### 10.4 Key → Все Элементы

```
Key (например: "Am" - A minor)
│
├── → Эмоция: Minor → sadness, pain, gothic emotions
│
├── → Цвет: Minor keys → темные цвета (#2C1A2E, #1B1B2F, etc.)
│
├── → Жанр:
│   ├── Major → pop, jazz, lyrical, soft
│   └── Minor → gothic, darkwave, metal, cinematic
│
└── → Вокал: Minor → более драматичные техники
```

---

## 11. Иерархия Влияний (Priority Order)

### 11.1 Порядок Приоритетов

```
1. ЭМОЦИИ (базовый уровень)
   └── Определяет все остальное
   
2. TLP (Truth/Love/Pain)
   └── Уточняет эмоции, влияет на BPM, Key, Genre
   
3. ЦВЕТА (из эмоций)
   └── Визуальное представление, влияет на BPM, Key, Domain
   
4. BPM (из эмоций + TLP + цвета)
   └── Влияет на Key, Genre, Вокал
   
5. KEY (из эмоций + цвета + BPM)
   └── Влияет на Genre, Вокал
   
6. RDE (из структуры текста)
   └── Уточняет эмоции, влияет на Genre
   
7. ВОКАЛ (из эмоций + жанра)
   └── Зависит от эмоций, жанра, BPM
   
8. ЖАНР (из эмоций + цвета + BPM + Key)
   └── Финальный выбор на основе всех факторов
   
9. ЛИРИКА (из жанра + эмоций)
   └── Форма определяется жанром и эмоциями
```

---

## 12. Примеры Полных Цепочек

### 12.1 Пример 1: Love Emotion

```
Вход: Эмоция "love" (intensity: 0.7)
│
├── Цвет: #FF7AA2
│   ├── → BPM: (70, 100, 85) → default: 85
│   └── → Key: ["C major", "G major", "A major", "E major", "D major"] → выбран: "C major"
│
├── BPM: 85
│   └── Корректировка: -love * 25 * 0.3 = -5.25 → итого: ~80 BPM
│
├── Key: C major
│   └── Определено: love + hope > 0.55 → major
│
├── RDE:
│   ├── Resonance: 0.4 (средний - лирические повторения)
│   ├── Fracture: 0.2 (низкий - плавные переходы)
│   └── Entropy: 0.5 (средний)
│
├── Вокал: ["lyric_soprano", "soft_female_alto", "gentle_male_tenor", "breathy"]
│   └── Интенсивность: 0.7 → отфильтровано: ["lyric_soprano", "soft_female_alto", "gentle_male_tenor"]
│
├── Лирика: ballad (emotion_weight: 0.40)
│
└── Жанр:
    ├── Domain: lyrical (+0.20 boost)
    ├── Жанры: ["romantic_ballad", "lyrical", "soul", "R&B", "soft_pop"]
    └── Финальный: "romantic_ballad"
```

### 12.2 Пример 2: Pain Emotion

```
Вход: Эмоция "pain" (intensity: 0.8)
│
├── Цвет: #DC143C (crimson)
│   ├── → BPM: (50, 80, 65) → default: 65
│   └── → Key: ["D minor", "A minor", "E minor", "B minor"] → выбран: "A minor"
│
├── BPM: 65
│   └── Корректировка: +pain * 50 * 0.3 = +12 → итого: ~77 BPM
│
├── Key: A minor
│   └── Определено: sadness > 0.55 → minor
│
├── RDE:
│   ├── Resonance: 0.3 (низкий - меньше повторений)
│   ├── Fracture: 0.4 (высокий - больше разрывов)
│   └── Entropy: 0.6 (высокий - разнообразие)
│
├── Вокал: ["dramatic_baritone", "rasp", "grit"]
│   └── Интенсивность: 0.8 → все техники активны
│
├── Лирика: elegy или ballad_poem
│
└── Жанр:
    ├── Domain: hard (+0.18 boost) или lyrical (+0.15 для sorrow)
    ├── Жанры: ["gothic_rock", "darkwave", "neoclassical_dark", "ballad_poem"]
    └── Финальный: "gothic_rock" (если pain > 0.6) или "ballad_poem" (если sorrow > pain)
```

### 12.3 Пример 3: Joy Emotion

```
Вход: Эмоция "joy" (intensity: 0.9)
│
├── Цвет: #FFD93D (желтый)
│   ├── → BPM: (100, 140, 120) → default: 120
│   └── → Key: ["C major", "G major", "A minor", "F major", "D major"] → выбран: "C major"
│
├── BPM: 120
│   └── Корректировка: +joy * 15 * 0.3 = +4.05 → итого: ~124 BPM
│
├── Key: C major
│   └── Определено: joy > 0.5 → major
│
├── RDE:
│   ├── Resonance: 0.6 (высокий - повторения припева)
│   ├── Fracture: 0.2 (низкий - плавная структура)
│   └── Entropy: 0.4 (низкий - предсказуемость)
│
├── Вокал: ["lyric_soprano", "falsetto", "head_voice", "bright_tone"]
│   └── Интенсивность: 0.9 → все техники активны
│
├── Лирика: ode или lyrical_song
│
└── Жанр:
    ├── Domain: electronic (+0.18 boost)
    ├── Жанры: ["pop", "dance_pop", "electropop", "funk", "disco"]
    └── Финальный: "pop" или "dance_pop"
```

---

## 13. Таблицы Быстрого Доступа

### 13.1 Эмоция → Цвет → BPM → Key

| Эмоция | Цвет | BPM (min, max, default) | Key (предпочтительные) |
|--------|------|-------------------------|------------------------|
| love | #FF7AA2 | (70, 100, 85) | C/G/A/E/D major |
| love_soft | #FFC0CB | (60, 100, 80) | C/G/A minor/F major |
| love_deep | #C2185B | (70, 95, 82) | C/G/D/A/E major |
| pain | #DC143C | (50, 80, 65) | D/A/E/B minor |
| gothic_dark | #2C1A2E | (50, 80, 65) | D/A/E/B/G minor |
| truth | #4B0082 | (60, 90, 75) | C/G/A/F/D minor |
| joy | #FFD93D | (100, 140, 120) | C/G/A minor/F/D major |
| joy_bright | #FFD700 | (100, 140, 120) | C/G/A minor/F major |
| peace | #40E0D0 | (50, 100, 80) | C/F major/A/D minor |
| sorrow | #3E5C82 | (50, 80, 65) | D/A/E/G minor |
| sadness | #4A6FA5 | (50, 80, 65) | D/A/E/B minor |
| melancholy | #596E94 | (50, 80, 65) | A/D/E/G/C minor |
| nostalgia | #D8BFD8 | (60, 85, 72) | A/D/E/G/C minor |
| epic | #8A2BE2 | (70, 100, 85) | C/G/D/A major |

### 13.2 Эмоция → Вокал → Жанр

| Эмоция | Вокал (топ-3) | Жанр Domain | Жанры |
|--------|---------------|-------------|-------|
| love | lyric_soprano, soft_female_alto, gentle_male_tenor | lyrical (+0.20) | romantic_ballad, lyrical, soul, R&B |
| pain | dramatic_baritone, rasp, grit | hard (+0.18) | gothic_rock, darkwave, neoclassical_dark |
| joy | lyric_soprano, falsetto, head_voice | electronic (+0.18) | pop, dance_pop, electropop, funk |
| sadness | baritone, soft, vibrato | lyrical (+0.12) | darkwave, post_punk, coldwave, neo_folk |
| rage | dramatic_tenor, harsh, scream | hard (+0.18) | metal, thrash_metal, deathcore, drill |
| truth | tenor, clear, resonant | lyrical (+0.15) | confessional_lyric, poetic_narrative |
| epic | layered_choir, dramatic, powerful | cinematic (+0.20) | orchestral_cinematic, epic_light |

### 13.3 BPM → Эмоция → Жанр

| BPM Диапазон | Типичные Эмоции | Типичные Жанры |
|--------------|-----------------|----------------|
| 40-60 | deep_pain, collapsing_pain | ambient, dark ambient |
| 50-80 | pain, gothic, sorrow, sadness | gothic_rock, darkwave, ballad, elegy |
| 60-90 | truth, nostalgia | confessional_lyric, nostalgic_ballad |
| 70-100 | love, peace, epic | romantic_ballad, lyrical_song, epic, ode |
| 100-120 | joy, happiness | pop, dance_pop, funk |
| 120-140 | joy_bright, excitement | electropop, disco, electronic |
| 140-200 | rage, aggression, extreme | metal, hardcore, extreme_metal |

### 13.4 Key → Эмоция → Жанр

| Key Mode | Типичные Эмоции | Типичные Жанры |
|----------|-----------------|----------------|
| Major | love, joy, peace, hope | pop, jazz, lyrical, soft, folk |
| Minor | sadness, pain, sorrow, gothic | gothic, darkwave, metal, cinematic, ballad |
| Phrygian | awe, epic, dramatic | cinematic, orchestral, epic |
| Dark Minor | rage, extreme, dark | black_metal, death_metal, extreme |

---

## 14. Формулы Взаимосвязей

### 14.1 BPM Формулы

```python
# Базовая формула BPM
bpm_base = 92.0
bpm_base += aggression * 40.0
bpm_base -= sadness * 20.0
bpm_base += hope * 15.0
bpm_base += awe * 10.0

# TLP коррекция
bpm += pain * 50 * emotion_weight      # Pain boost
bpm -= love * 25 * emotion_weight      # Love smoothing
bpm += truth * 20 * emotion_weight    # Truth drive

# CF коррекция
bpm += (cf - 0.8) * 100 * emotion_weight

# Ограничение
bpm = clamp(bpm, 60.0, 190.0)
```

### 14.2 Key Формулы

```python
# Базовое правило
if sadness > 0.55:
    mode = "minor"
else:
    mode = "major"

# Love/Hope коррекция
if love + hope + tenderness > 0.55:
    mode = "major"

# Awe коррекция
if awe > 0.7:
    mode = "modal_phrygian_lydian"

# Rage коррекция
if rage > 0.7:
    mode = "minor_dark"

# Arousal shift
if arousal > 0.6:
    key_shift = +1
elif arousal < 0.3:
    key_shift = -1

# Valence mode
if valence > 0.3:
    mode = "major"
elif valence < -0.3:
    mode = "minor"
```

### 14.3 Genre Bias Формулы

```python
# Базовая bias (все жанры: 1.0)
bias = {genre: 1.0 for genre in GENRES}

# Anger влияние
bias["rock_metal"] += 0.65 * anger
bias["hip_hop"] += 0.55 * anger
bias["jazz"] -= 0.45 * anger
bias["folk"] -= 0.35 * anger
bias["pop"] -= 0.35 * anger

# Sadness влияние
bias["gothic"] += 0.60 * sadness
bias["folk"] += 0.28 * sadness
bias["edm"] -= 0.38 * sadness
bias["pop"] -= 0.28 * sadness

# Awe влияние
bias["orchestral"] += 0.70 * awe
bias["hip_hop"] -= 0.28 * awe

# Joy влияние
bias["pop"] += 0.50 * joy
bias["edm"] += 0.40 * joy
bias["gothic"] -= 0.30 * joy

# Pain влияние
bias["gothic"] += 0.55 * pain
bias["pop"] -= 0.25 * pain

# Love влияние
bias["lyrical"] += 0.60 * love
bias["pop"] += 0.30 * love
bias["metal"] -= 0.40 * love
```

---

## 15. Граф Зависимостей

```
ЭМОЦИИ
  │
  ├─> ЦВЕТА (прямое маппинг)
  │   └─> BPM (через EMOTION_COLOR_TO_BPM)
  │   └─> KEY (через EMOTION_COLOR_TO_KEY)
  │   └─> ДОМЕН (через color_to_domain_boost)
  │
  ├─> BPM (через compute_bpm_base + TLP коррекция)
  │   └─> KEY (влияет на выбор)
  │   └─> ЖАНР (влияет на выбор)
  │   └─> ВОКАЛ (влияет на интенсивность)
  │
  ├─> KEY (через compute_key_and_mode)
  │   └─> ЖАНР (major/minor влияет на жанр)
  │   └─> ВОКАЛ (влияет на техники)
  │
  ├─> RDE (влияет на эмоциональный профиль)
  │   └─> ЖАНР (уточняет выбор)
  │
  ├─> ВОКАЛ (через EMOTION_TO_VOCAL_MAP)
  │   └─> ЖАНР (влияет на выбор жанра)
  │
  └─> ЖАНР (через emotion_to_domain_boost + compute_genre_bias)
      └─> ЛИРИКА (форма определяется жанром)
```

---

## 16. Специальные Правила

### 16.1 Rage Mode

```
Условие: anger > 0.22 OR tension > 0.25
│
├── BPM: +40.0 * aggression (очень высокий)
├── Key: minor_dark (dark_minor mode)
├── Вокал: ["death_growl", "false_cord_scream", "harsh_vocals"]
├── Инструменты: ["distorted guitar", "industrial drums", "heavy bass synth"]
└── Жанр: ["black_metal", "death_metal", "martial_industrial"]
```

### 16.2 Epic Mode

```
Условие: epic > 0.35 AND NOT rage
│
├── BPM: 70-100 (средний)
├── Key: Major (C, G, D, A major)
├── Вокал: ["layered_choir", "dramatic", "powerful"]
├── Инструменты: ["brass", "orchestral percussion", "dramatic strings"]
└── Жанр: ["orchestral_cinematic", "epic_light", "cinematic"]
```

### 16.3 Lyrical Mode

```
Условие: love > 0.5 OR lyrical_emotion_score > 0.5
│
├── BPM: 60-100 (медленный)
├── Key: Major (преимущественно)
├── Вокал: ["lyric_soprano", "soft_female_alto", "gentle_male_tenor"]
├── Лирика: ballad, ode, sonnet
└── Жанр: ["romantic_ballad", "lyrical", "soul", "R&B"]
```

---

## 17. Иерархия Лирических Жанров

### 17.1 Литературные Формы

```
Литературные Формы
│
├── Поэтические
│   ├── баллада (ballad)
│   ├── ода (ode)
│   ├── сонет (sonnet)
│   ├── элегия (elegy)
│   └── верлибр (free verse)
│
├── Прозаические
│   ├── притча (parable)
│   └── эссе (essay)
│
└── Музыкальные
    ├── реп_текст (rap_text)
    └── spoken_word
```

### 17.2 Лирика → Эмоции Влияние

```
Лирические Формы влияют на:
│
├── emotion_weight (0.15 - 0.45)
│   └── Высокий → больше внимания к эмоциям
│
├── structure_weight (0.15 - 0.45)
│   └── Высокий → больше внимания к структуре
│
├── lexicon_weight (0.15 - 0.30)
│   └── Высокий → больше внимания к лексике
│
└── narrative_weight (0.10 - 0.30)
    └── Высокий → больше внимания к нарративу
```

---

## Резюме

**Основные иерархии:**
1. **Эмоции** - базовый уровень, определяет все остальное
2. **Цвета** - визуальное представление эмоций, влияет на BPM, Key, Domain
3. **BPM** - ритмическая характеристика, зависит от эмоций, влияет на Key, Genre
4. **Key** - тональность, зависит от эмоций и цвета, влияет на Genre, Вокал
5. **RDE** - структурные характеристики, уточняет эмоции
6. **Вокалы** - зависят от эмоций и жанра
7. **Лирика** - форма определяется жанром и эмоциями
8. **Жанры** - финальный выбор на основе всех факторов

**Ключевые маппинги:**
- `EMOTION_COLOR_MAP` - эмоции → цвета
- `EMOTION_COLOR_TO_BPM` - цвета → BPM диапазоны
- `EMOTION_COLOR_TO_KEY` - цвета → предпочтительные ключи
- `EMOTION_TO_VOCAL_MAP` - эмоции → вокальные техники
- `EMOTION_GROUPS` - эмоции → жанровые группы
- `emotion_to_domain_boost` - эмоции → доменные бусты
- `color_to_domain_boost` - цвета → доменные бусты

**Специальные режимы:**
- Rage Mode (anger > 0.22)
- Epic Mode (epic > 0.35)
- Lyrical Mode (love > 0.5)

---

**Создано:** Текущее состояние  
**Статус:** Полная иерархия элементов и взаимосвязей

