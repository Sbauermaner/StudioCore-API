# Сравнение с предоставленными таблицами StudioCore

## 📊 Предоставленные таблицы

### 1. StudioCore_MasterTable

#### Emotions (12 эмоций)
- joy: #FFD93D, weight: 0.10
- peace: #8FD3FE, weight: 0.12
- sadness: #5A6A86, weight: 0.20
- anger: #D62828, weight: 0.18
- fear: #4B3F72, weight: 0.16
- hope: #A9F04E, weight: 0.12
- passion: #B5179E, weight: 0.22
- nostalgia: #FFD1A1, weight: 0.14
- melancholy: #5A6A86, weight: 0.17
- despair: #3A0CA3, weight: 0.25
- tenderness: #FF6B6B, weight: 0.15
- longing: #A55EEA, weight: 0.18

#### TLP (3 оси)
- Truth: #A9F04E, weight: 0.30
- Love: #FF6B6B, weight: 0.50
- Pain: #3A0CA3, weight: 0.60

#### RDE (3 оси)
- Rhythm: #FF8C00, weight: 0.35
- Dynamics: #D62828, weight: 0.40
- Entropy: #8000FF, weight: 0.25

#### LyricalGenres (8 жанров)
- Лирика: #FFC0CB, weight: 0.40
- Элегия: #6A5ACD, weight: 0.50
- Сонет: #87CEFA, weight: 0.45
- Баллада: #FFD700, weight: 0.55
- Поэма: #FFA500, weight: 0.60
- Послание: #98FB98, weight: 0.30
- Эпиграмма: #FF6347, weight: 0.25
- Ода: #ADD8E6, weight: 0.35

#### MusicGenres (9 жанров)
- Rock: #FF5733, weight: 0.40
- Metal: #900C3F, weight: 0.60
- Pop: #FFB6C1, weight: 0.35
- Orchestral: #D9E4FF, weight: 0.55
- Ambient: #C0FFF4, weight: 0.25
- EDM: #9D00FF, weight: 0.50
- Trap: #171717, weight: 0.45
- Hip-Hop: #2B2BFF, weight: 0.42
- Jazz: #FFCC80, weight: 0.38

### 2. StudioCore_Relations

#### Emotion_To_Color
См. Emotions выше

#### Color_To_Key
- #FFD93D → C major
- #8FD3FE → F major
- #5A6A86 → A minor
- #D62828 → G minor
- #4B3F72 → D# minor
- #A9F04E → D major
- #B5179E → F# minor
- #FFD1A1 → E major
- #3A0CA3 → B minor
- #FF6B6B → A major
- #A55EEA → G# minor

#### TLP_To_Genre
- High_Truth → ["hiphop", "spoken_word", "narrative", "folk"]
- High_Love → ["pop", "rnb", "soul", "ballad"]
- High_Pain → ["metal", "trap", "industrial", "dnb"]

#### RDE_To_BPM
- low_rhythm → 60-80
- mid_rhythm → 80-110
- high_rhythm → 110-180
- high_entropy_bonus → +10-25

#### Lyrical_To_Music
- Лирика → ["pop", "ambient", "orchestral"]
- Элегия → ["ambient", "neoclassical"]
- Сонет → ["classical", "artpop"]
- Баллада → ["folk", "cinematic", "acoustic"]
- Поэма → ["orchestral", "epic", "cinematic"]
- Послание → ["hiphop", "spoken_word"]
- Эпиграмма → ["jazz", "funk", "hiphop"]
- Ода → ["cinematic", "symphonic_pop"]

#### Emotion_To_Vocal
- joy → tenor_soft
- peace → alto_air
- sadness → baritone_warm
- anger → fry_scream
- fear → whisper_mixed
- hope → tenor_open
- passion → belt_power
- melancholy → baritone_dark
- despair → baritone_break
- tenderness → alto_soft
- longing → mixed_head_voice

#### Emotion_To_Instruments
- joy → ["acoustic_guitar", "shakers", "piano_bright"]
- peace → ["pad_soft", "piano_clean", "ambient_textures"]
- sadness → ["piano_dark", "strings_soft"]
- anger → ["distorted_guitars", "heavy_drums"]
- fear → ["sub_bass", "reverse_fx"]
- hope → ["strings_high", "clean_guitar"]
- passion → ["synth_lead", "orchestral_brass"]
- melancholy → ["cello", "piano_reverb"]
- despair → ["viola", "low_strings"]
- tenderness → ["piano_solo", "light_pads"]
- longing → ["flute", "soft_synths"]

#### Section_Color_Rules
- intro → softest color of text
- verse → baseline color
- pre_chorus → warm shift +10%
- chorus → max saturation
- bridge → dark or cold tonal shift
- outro → fade to grayscale/light fade

---

## 🔍 Выявленные расхождения

### 1. EMOTION_COLOR_MAP
**Текущее состояние:** Используются разные цвета для некоторых эмоций
**Требуется:** Обновить цвета согласно предоставленной таблице

### 2. EMOTION_COLOR_TO_KEY
**Текущее состояние:** Используются списки ключей для каждого цвета
**Требуется:** Обновить на одиночные ключи согласно предоставленной таблице

### 3. EMOTION_TO_VOCAL_MAP
**Текущее состояние:** Используются списки вокальных техник с весами
**Требуется:** Обновить на одиночные вокальные техники согласно предоставленной таблице

### 4. TLP веса и цвета
**Текущее состояние:** Веса и цвета могут отличаться
**Требуется:** Обновить согласно предоставленной таблице

### 5. RDE веса и цвета
**Текущее состояние:** Веса и цвета могут отличаться
**Требуется:** Обновить согласно предоставленной таблице

---

## ✅ План обновления

1. Обновить `EMOTION_COLOR_MAP` в `color_engine_adapter.py`
2. Обновить `EMOTION_COLOR_TO_KEY` в `genre_colors.py`
3. Обновить `EMOTION_TO_VOCAL_MAP` в `vocal_techniques.py`
4. Добавить веса для эмоций, TLP, RDE
5. Обновить связи TLP_To_Genre, RDE_To_BPM, Lyrical_To_Music
6. Добавить Emotion_To_Instruments
7. Добавить Section_Color_Rules

