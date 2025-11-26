# Цепочка определения BPM и Key от цвета эмоции

## 📊 Общая схема

```
ЭМОЦИЯ (из анализа текста)
  ↓
[СЛОВАРЬ: EMOTION_COLOR_MAP]
  ↓
ЦВЕТ ЭМОЦИИ (HEX)
  ↓
[СЛОВАРЬ: EMOTION_COLOR_TO_BPM]
  ↓
BPM (min, max, default)
  ↓
[СРАВНЕНИЕ С: BPM жанров музыки]
  ↓
ОБНОВЛЕНИЕ bpm_payload
```

```
ЭМОЦИЯ (из анализа текста)
  ↓
[СЛОВАРЬ: EMOTION_COLOR_MAP]
  ↓
ЦВЕТ ЭМОЦИИ (HEX)
  ↓
[СЛОВАРЬ: EMOTION_COLOR_TO_KEY]
  ↓
KEY (список предпочтительных ключей)
  ↓
[СРАВНЕНИЕ С: Key жанров музыки]
  ↓
ОБНОВЛЕНИЕ tonality_payload
```

---

## 🔗 Детальная последовательность

### Шаг 1: Эмоция → Цвет эмоции

**Словарь:** `EMOTION_COLOR_MAP` (93 эмоции)

**Функция:** `get_emotion_colors(dominant_emotion)`

**Результат:**
```python
emotion_color = "#40E0D0"  # Например, для peace
```

**Статус:** ✅ Работает

---

### Шаг 2: Цвет эмоции → BPM

**Словарь:** `EMOTION_COLOR_TO_BPM` (30+ цветов)

**Функция:** `get_bpm_from_emotion_color(emotion_color)`

**Логика:**
- LOVE цвета → лирические BPM (60-100)
- PAIN/GOTHIC цвета → низкие BPM (50-80)
- TRUTH цвета → средние BPM (60-90)
- JOY цвета → высокие BPM (100-140)
- PEACE цвета → средние BPM (50-100)
- SORROW цвета → низкие BPM (50-80)
- NOSTALGIA цвета → средние BPM (60-85)
- EPIC цвета → средние BPM (70-100)

**Результат:**
```python
bpm_range = (50, 100, 80)  # (min_bpm, max_bpm, default_bpm)
```

**Статус:** ✅ Реализовано

---

### Шаг 3: BPM → Обновление bpm_payload

**Модуль:** `studiocore.core_v6.StudioCoreV6._backend_analyze()`

**Логика:**
1. Определяется `bpm_payload` на основе текста и эмоций
2. Определяется цвет эмоции
3. Определяется BPM из цвета эмоции
4. Обновляется `bpm_payload["estimate"]` (только если не установлен пользователем)

**Результат:**
```python
bpm_payload = {
    "estimate": 80,  # Обновлено из цвета эмоции
    "emotion_color_bpm": 80,
    "emotion_color_source": "#40E0D0",
    # ... остальные поля
}
```

**Статус:** ✅ Реализовано

---

### Шаг 4: Цвет эмоции → Key

**Словарь:** `EMOTION_COLOR_TO_KEY` (30+ цветов)

**Функция:** `get_key_from_emotion_color(emotion_color)`

**Логика:**
- LOVE цвета → major ключи
- PAIN/GOTHIC цвета → minor ключи
- TRUTH цвета → minor ключи (исповедальность)
- JOY цвета → major ключи
- PEACE цвета → major/minor ключи
- SORROW цвета → minor ключи
- NOSTALGIA цвета → minor ключи
- EPIC цвета → major ключи

**Результат:**
```python
emotion_keys = ["C major", "F major", "A minor", "D minor"]  # Для peace
```

**Статус:** ✅ Реализовано

---

### Шаг 5: Key → Обновление tonality_payload

**Модуль:** `studiocore.core_v6.StudioCoreV6._backend_analyze()`

**Логика:**
1. Определяется `tonality_payload` на основе текста и эмоций
2. Определяется цвет эмоции
3. Определяется Key из цвета эмоции
4. Обновляется `tonality_payload["key"]` (только если не установлен пользователем)

**Результат:**
```python
tonality_payload = {
    "key": "C major",  # Обновлено из цвета эмоции
    "emotion_color_key": "C major",
    "emotion_color_source": "#40E0D0",
    "anchor_key": "C major",  # Также обновлено
    "fallback_key": "C major",  # Также обновлено
    # ... остальные поля
}
```

**Статус:** ✅ Реализовано

---

### Шаг 6: Сравнение BPM и Key с жанрами музыки

**Модуль:** `studiocore.genre_colors.find_matching_music_genre_by_bpm_key()`

**Логика:**
1. Берем BPM и Key из `bpm_payload` и `tonality_payload`
2. Сравниваем с BPM и Key жанров музыки из `GENRE_DATABASE`
3. Находим наиболее подходящий жанр
4. Обновляем `style_genre` (если найден более подходящий)

**Результат:**
```python
matching_genre = "lyrical_song"  # Найден на основе BPM и Key
match_score = 0.85  # Оценка совпадения (0.0-1.0)
```

**Статус:** ✅ Реализовано (частично - нужна загрузка из GENRE_DATABASE.json)

---

## 📋 Словари, которые используются

### ✅ Используются:

1. **EMOTION_COLOR_MAP:**
   - 93 эмоции → цвета

2. **EMOTION_COLOR_TO_BPM:**
   - 30+ цветов → (min_bpm, max_bpm, default_bpm)

3. **EMOTION_COLOR_TO_KEY:**
   - 30+ цветов → список ключей

4. **GENRE_DATABASE:**
   - BPM и Key для всех жанров музыки

---

## 🔧 Реализация

### 1. Определение BPM из цвета эмоции

```python
# В studiocore/genre_colors.py
EMOTION_COLOR_TO_BPM = {
    "#40E0D0": (50, 100, 80),   # peace
    "#FF7AA2": (70, 100, 85),   # love
    # ... и т.д.
}

def get_bpm_from_emotion_color(emotion_color: str) -> tuple[int, int, int] | None:
    return EMOTION_COLOR_TO_BPM.get(emotion_color)
```

### 2. Определение Key из цвета эмоции

```python
# В studiocore/genre_colors.py
EMOTION_COLOR_TO_KEY = {
    "#40E0D0": ["C major", "F major", "A minor", "D minor"],  # peace
    "#FF7AA2": ["C major", "G major", "A major", "E major", "D major"],  # love
    # ... и т.д.
}

def get_key_from_emotion_color(emotion_color: str) -> List[str] | None:
    return EMOTION_COLOR_TO_KEY.get(emotion_color)
```

### 3. Обновление bpm_payload

```python
# В studiocore/core_v6.py, после определения bpm_payload
if emotion_color:
    bpm_range = get_bpm_from_emotion_color(emotion_color)
    if bpm_range:
        emotion_bpm = bpm_range[2]  # default_bpm
        if not bpm_payload.get("manual_override"):
            bpm_payload["estimate"] = emotion_bpm
            bpm_payload["emotion_color_bpm"] = emotion_bpm
            bpm_payload["emotion_color_source"] = emotion_color
```

### 4. Обновление tonality_payload

```python
# В studiocore/core_v6.py, после определения tonality_payload
if emotion_color:
    emotion_keys = get_key_from_emotion_color(emotion_color)
    if emotion_keys:
        emotion_key = emotion_keys[0]
        if not tonality_payload.get("manual_override"):
            tonality_payload["key"] = emotion_key
            tonality_payload["emotion_color_key"] = emotion_key
            tonality_payload["emotion_color_source"] = emotion_color
```

### 5. Сравнение с жанрами музыки

```python
# В studiocore/core_v6.py, при выборе жанра
current_bpm = bpm_payload.get("estimate")
current_key = tonality_payload.get("key")

if current_bpm and current_key:
    matching_genre, match_score = find_matching_music_genre_by_bpm_key(
        current_bpm,
        current_key,
        genre_bpm_ranges,  # Из GENRE_DATABASE
        genre_keys,  # Из GENRE_DATABASE
    )
    
    if match_score > 0.5:
        style_genre = matching_genre
```

---

## 📊 Пример полной цепочки

```
Текст: "Вы помните, Вы всё, конечно, помните..."

1. Эмоция: peace (0.60)
   ↓
2. Цвет эмоции: #40E0D0 (turquoise)
   ↓
3. BPM из цвета: (50, 100, 80)
   ↓
4. Обновление bpm_payload:
   bpm_payload["estimate"] = 80
   bpm_payload["emotion_color_bpm"] = 80
   bpm_payload["emotion_color_source"] = "#40E0D0"
   ↓
5. Key из цвета: ["C major", "F major", "A minor", "D minor"]
   ↓
6. Обновление tonality_payload:
   tonality_payload["key"] = "C major"
   tonality_payload["emotion_color_key"] = "C major"
   tonality_payload["emotion_color_source"] = "#40E0D0"
   ↓
7. Сравнение с жанрами музыки:
   - lyrical_song: BPM 60-100 (80), Key C major → ✅ Совпадает
   - pop: BPM 100-140 (120), Key C major → ❌ BPM не совпадает
   ↓
8. Выбор жанра: lyrical_song (на основе BPM и Key)
```

---

## ✅ Выводы

1. **BPM определяется от цвета эмоции** ✅
2. **Key определяется от цвета эмоции** ✅
3. **BPM и Key сравниваются с жанрами музыки** ✅
4. **Жанр выбирается на основе совпадения BPM и Key** ✅

---

## 🎯 Итоговые рекомендации

1. ✅ **Все словари используются** для определения BPM и Key
2. ✅ **BPM и Key обновляются** в `bpm_payload` и `tonality_payload`
3. ⚠️ **Нужно загрузить** BPM и Key для всех жанров из `GENRE_DATABASE.json`
4. ✅ **Сравнение реализовано** через `find_matching_music_genre_by_bpm_key()`

