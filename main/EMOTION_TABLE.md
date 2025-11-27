# Таблица Эмоций - Анализ Лирики

Полная документация всех эмоций в StudioCore и как они проверяют лирику.

---

## 1. Основная Таблица: Эмоции в AutoEmotionalAnalyzer

**Класс:** `AutoEmotionalAnalyzer`  
**Файл:** `studiocore/emotion.py`  
**Метод анализа:** `analyze(text: str) -> Dict[str, float]`

| № | Эмоция | Количество Ключевых Слов | Примеры Ключевых Слов | Языки |
|---|--------|-------------------------|----------------------|-------|
| 1 | **joy** | 11 | joy, happy, laugh, смех, рад, улыб, счаст, весел, hope, bright, солнц | EN, RU |
| 2 | **sadness** | 11 | sad, печал, груст, слез, плач, cry, lonely, утрат, страда, тоск, один | EN, RU |
| 3 | **anger** | 10 | anger, rage, злост, гнев, ярост, fight, burn, ненави, крик, воин | EN, RU |
| 4 | **fear** | 7 | fear, страх, ужас, паник, тревог, боят, scared | EN, RU |
| 5 | **peace** | 8 | мир, тишин, calm, still, тихо, равновес, спокой, умиротвор | EN, RU |
| 6 | **epic** | 13 | epic, велич, геро, легенд, immortal, battle, rise, бог, судьб, огонь, шторм, неб, гимн | EN, RU |
| 7 | **awe** | 7 | восторг, awe, wow, чудо, вдохнов, удив, прекрас | EN, RU |
| 8 | **sensual** | 30 | тело, прикосновен, обнима, объятия, наслажден, мягк, шелк, плотск, сенсуальн, ласк, каса, запах, вкус, пожар, страст, touch, embrace, body, sensual, tender, soft, silk, pleasure, passion, intimate, caress, scent, taste, fire, desire | EN, RU |
| 9 | **nostalgia** | 19 | помню, вспоминаю, вспомнить, память, памят, вспомин, воспомина, прошл, был, было, была, remember, recall, memory, reminisce, recollection, past, was, were | EN, RU |
| 10 | **neutral** | 0 | (пустой список - используется как fallback) | - |

**Всего эмоций в AutoEmotionalAnalyzer:** 10  
**Всего ключевых слов:** 116

---

## 2. Процесс Проверки Лирики

### Шаг 1: Подготовка Текста
- Текст приводится к нижнему регистру: `s = text.lower()`
- Сохраняются все символы (включая пунктуацию и эмодзи)

### Шаг 2: Анализ Пунктуации и Эмодзи
**Файл:** `studiocore/emotion.py:542-546`

| Элемент | Вес | Описание |
|---------|-----|----------|
| `!` | 0.6 | Высокий вес - усиливает эмоцию |
| `?` | 0.4 | Средний вес |
| `…` | 0.5 | Эллипсис - пауза, размышление |
| `—` | 0.2 | Тире - пауза |
| `:` | 0.15 | Двоеточие |
| `;` | 0.1 | Точка с запятой |
| `.` | 0.1 | Точка |
| `, ` | 0.05 | Запятая - низкий вес |
| Эмодзи | 0.5 | Все эмодзи имеют единый вес |

**Формула энергии:**
```
punct_energy = sum(PUNCT_WEIGHTS.get(ch, 0.0) for ch in text)
emoji_energy = sum(EMOJI_WEIGHTS.get(ch, 0.0) for ch in text)
energy = min(1.0, (punct_energy + emoji_energy) ** 0.7)
```

### Шаг 3: Поиск Ключевых Слов (Regex Matching)
**Файл:** `studiocore/emotion.py:548-554`

- Для каждой эмоции создается regex-паттерн из ключевых слов
- Паттерн ищет **корни слов** (не полные совпадения)
- Подсчитывается количество совпадений для каждой эмоции

**Пример:**
```python
# Для "joy" создается паттерн: r"(joy|happy|laugh|смех|рад|улыб|счаст|весел|hope|bright|солнц)"
# Текст: "Я рад и счастлив!"
# Найдено: "рад", "счаст" → scores["joy"] = 2.0
```

### Шаг 4: Усиление (Amplification)
**Файл:** `studiocore/emotion.py:558-562`

Если `energy > 0.1` и найдены совпадения:
```
scores[field] *= 1 + energy**2
```

**Пример:**
- Найдено 2 совпадения для "joy"
- Энергия пунктуации: 0.5
- Усиление: `2.0 * (1 + 0.5²) = 2.0 * 1.25 = 2.5`

### Шаг 5: Нормализация (Softmax)
**Файл:** `studiocore/emotion.py:524-536, 565`

**Алгоритм Softmax:**
1. Находится максимальный score: `max_score = max(scores.values())`
2. Вычисляются экспоненты: `exp(v - max_score)` для каждого значения
3. Нормализация: `exp(v) / sum(all_exps)`

**Fallback при OverflowError:**
- Используется линейная нормализация: `v / sum(all_values)`

**Результат:** Все эмоции получают значения от 0.0 до 1.0, сумма = 1.0

### Шаг 6: Fallback для Пустого Текста
**Файл:** `studiocore/emotion.py:567-570`

Если не найдено совпадений или все значения < 0.05:
```python
normalized = {"peace": 0.6, "joy": 0.3, "neutral": 0.1}
```

### Шаг 7: Специальные Правила

#### Правило 1: Peace vs Sensual
**Файл:** `studiocore/emotion.py:572-591`

Если `peace > 0.5` и найдено > 2 сенсуальных слов:
- `peace` снижается на 70%: `peace * 0.3`
- Перераспределение на `sensual`: `peace * 0.4`
- Повторная нормализация

#### Правило 2: Rage Mode (в logical_engines.py)
**Файл:** `studiocore/logical_engines.py:358-378`

Если `anger > 0.22` ИЛИ `tension > 0.25`:
- Удаляются: `peace`, `calm`, `serenity` (устанавливаются в 0.0)
- Если `anger > 0.20`: `tension` повышается минимум до 0.25

#### Правило 3: Road Narrative Filter
**Файл:** `studiocore/logical_engines.py:345-356`

Если `sensual > 0.15` и `(sorrow + determination) > 0.5`:
- `sensual` снижается до 0.15
- Перераспределение: `sorrow += 0.6 * delta`, `determination += 0.4 * delta`

### Шаг 8: Финальная Очистка
**Файл:** `studiocore/emotion.py:593-600`

- Удаляется `neutral` из результата
- Удаляются значения < 0.001
- Округление до 3 знаков после запятой

---

## 3. Расширенная Таблица: EmotionEngineV64

**Класс:** `EmotionEngineV64`  
**Файл:** `studiocore/emotion_engine.py`  
**Количество эмоций:** 24+ (расширенный спектр)

| Категория | Эмоции | Количество |
|-----------|--------|------------|
| **Joy Spectrum** | joy, joy_bright, happiness, delight | 4 |
| **Calm Spectrum** | calm, serenity, trust | 3 |
| **Love Spectrum** | love, love_soft, love_deep, infinite_love, healing_love, maternal_love, radiant_love, longing_love, gentle_love, unconditional_love | 10 |
| **Sadness Spectrum** | sadness, disappointment, melancholy, sorrow, loneliness, grief, regret, guilt, shame | 9 |
| **Pain Spectrum** | deep_pain, phantom_pain, burning_pain, soul_pain, silent_pain, explosive_pain, collapsing_pain | 7 |
| **Rage Spectrum** | rage, rage_extreme, aggression, anger, bitterness, jealousy, envy, betrayal, resentment | 9 |
| **Fear/Conflict Spectrum** | fear, anxiety, panic, disgust, aversion, confusion, frustration | 7 |
| **Awe/Hope Spectrum** | awe, wonder, hope, relief, admiration | 5 |
| **Dark Spectrum** | gothic_dark, dark_poetic, dark_romantic | 3 |
| **Hiphop Spectrum** | hiphop_conflict, street_power | 2 |
| **Truth Spectrum** | clear_truth, cold_truth, sharp_truth, brutal_honesty | 4 |

**Всего эмоций в EmotionEngineV64:** 63+

---

## 4. Таблица: EmotionEngineV2

**Класс:** `EmotionEngineV2`  
**Файл:** `studiocore/emotion.py:628-689`

| Эмоция | Ключевые Слова (RU) | Ключевые Слова (EN) | Веса |
|--------|---------------------|---------------------|------|
| **joy** | радость (1.0), счастье (1.0), улыбка (0.8), смех (0.9) | joy (1.0), happy (1.0), smile (0.8) | 0.8-1.0 |
| **sadness** | грусть (1.0), печаль (1.0), слёзы (1.0), одиночество (0.8) | sad (1.0), tears (1.0) | 0.8-1.0 |
| **anger** | злость (1.0), ярость (1.0), ненависть (1.0), гнев (1.0) | anger (1.0), hate (1.0) | 1.0 |
| **fear** | страх (1.0), ужас (1.0), паника (0.9), бояться (0.8) | fear (1.0), scared (1.0) | 0.8-1.0 |
| **hope** | надежда (1.0), верю (0.8), свет (0.7), рассвет (0.7) | hope (1.0) | 0.7-1.0 |
| **despair** | безнадёжность (1.0), бессилие (0.9), крах (0.8), "я устал" (0.7) | despair (1.0) | 0.7-1.0 |
| **calm** | тихо (0.8), спокойно (1.0), тишина (0.9) | calm (1.0), silence (0.9) | 0.8-1.0 |
| **tension** | напряжение (1.0), стресс (0.9), тревога (0.8) | tension (1.0), stress (0.9) | 0.8-1.0 |

**Всего эмоций в EmotionEngineV2:** 8

---

## 5. Сводная Таблица: Все Эмоции

| Источник | Количество Эмоций | Основное Использование |
|----------|------------------|------------------------|
| **AutoEmotionalAnalyzer** | 10 | Основной анализатор (используется в monolith) |
| **EmotionEngineV64** | 63+ | Расширенный спектр для детального анализа |
| **EmotionEngineV2** | 8 | Альтернативный анализатор |
| **EmotionSignal** | 8 | Структура данных для сигналов |

---

## 6. Таблица: Процесс Анализа Лирики (Пошагово)

| Шаг | Действие | Метод/Функция | Строка Кода | Результат |
|-----|----------|---------------|-------------|-----------|
| 1 | Нормализация текста | `text.lower()` | `emotion.py:540` | Текст в нижнем регистре |
| 2 | Анализ пунктуации | `PUNCT_WEIGHTS.get(ch, 0.0)` | `emotion.py:543` | `punct_energy` (0.0-1.0) |
| 3 | Анализ эмодзи | `EMOJI_WEIGHTS.get(ch, 0.0)` | `emotion.py:544` | `emoji_energy` (0.0-1.0) |
| 4 | Расчет общей энергии | `(punct_energy + emoji_energy) ** 0.7` | `emotion.py:545` | `energy` (0.0-1.0) |
| 5 | Поиск ключевых слов | `pattern.findall(s)` | `emotion.py:552` | `scores[emotion]` (количество совпадений) |
| 6 | Усиление через энергию | `scores[field] *= 1 + energy**2` | `emotion.py:561` | Усиленные scores |
| 7 | Нормализация (softmax) | `_softmax(scores)` | `emotion.py:565` | Нормализованные значения (0.0-1.0) |
| 8 | Fallback для пустого | `{"peace": 0.6, "joy": 0.3, "neutral": 0.1}` | `emotion.py:570` | Дефолтные значения |
| 9 | Правило Peace/Sensual | Проверка `peace > 0.5` и сенсуальных слов | `emotion.py:574-591` | Скорректированные значения |
| 10 | Финальная очистка | Удаление `neutral` и значений < 0.001 | `emotion.py:594-598` | Финальный результат |

---

## 7. Таблица: Веса Пунктуации для Анализа Эмоций

| Символ | Вес | Влияние на Эмоцию |
|--------|-----|-------------------|
| `!` | 0.6 | Высокое - усиливает anger, joy, epic |
| `?` | 0.4 | Среднее - усиливает fear, confusion |
| `…` | 0.5 | Высокое - усиливает sadness, nostalgia, peace |
| `—` | 0.2 | Низкое - пауза, размышление |
| `:` | 0.15 | Низкое - объяснение, акцент |
| `;` | 0.1 | Очень низкое - разделение |
| `.` | 0.1 | Очень низкое - завершение |
| `, ` | 0.05 | Минимальное - пауза |

**Формула усиления:**
```
Если energy > 0.1 и найдены совпадения:
    scores[emotion] *= (1 + energy²)
```

**Пример:**
- Найдено 3 совпадения для "anger"
- Энергия пунктуации: 0.6 (много "!")
- Усиление: `3.0 * (1 + 0.6²) = 3.0 * 1.36 = 4.08`

---

## 8. Таблица: Специальные Правила Обработки

| Правило | Условие | Действие | Файл | Строка |
|---------|---------|----------|------|--------|
| **Peace/Sensual** | `peace > 0.5` и `sensual_words > 2` | `peace *= 0.3`, `sensual += peace * 0.4` | `emotion.py` | `574-591` |
| **Rage Mode** | `anger > 0.22` ИЛИ `tension > 0.25` | Удалить `peace`, `calm`, `serenity` | `logical_engines.py` | `364-378` |
| **Road Narrative** | `sensual > 0.15` и `(sorrow + determination) > 0.5` | `sensual = 0.15`, перераспределить в `sorrow` и `determination` | `logical_engines.py` | `351-356` |
| **Empty Text Fallback** | `total_hits == 0` или все значения < 0.05 | `{"peace": 0.6, "joy": 0.3, "neutral": 0.1}` | `emotion.py` | `568-570` |

---

## 9. Таблица: Примеры Анализа

### Пример 1: Радостный Текст
**Текст:** "Я рад и счастлив! Улыбка на лице, смех в сердце!"

**Анализ:**
- Найдено: "рад", "счаст", "улыб", "смех" → `joy = 4`
- Пунктуация: "!" → `energy = 0.6`
- Усиление: `4 * (1 + 0.6²) = 4 * 1.36 = 5.44`
- Нормализация: `joy ≈ 0.85`, другие эмоции ≈ 0.0-0.15

**Результат:** `{"joy": 0.85, "peace": 0.10, ...}`

---

### Пример 2: Грустный Текст
**Текст:** "Печаль в сердце... Слезы на глазах. Одиночество."

**Анализ:**
- Найдено: "печал", "слез", "один" → `sadness = 3`
- Пунктуация: "…", "." → `energy = 0.6`
- Усиление: `3 * (1 + 0.6²) = 3 * 1.36 = 4.08`
- Нормализация: `sadness ≈ 0.75`, другие эмоции ≈ 0.0-0.25

**Результат:** `{"sadness": 0.75, "peace": 0.15, ...}`

---

### Пример 3: Агрессивный Текст
**Текст:** "Гнев! Ярость! Ненависть! Крик!"

**Анализ:**
- Найдено: "гнев", "ярост", "ненави", "крик" → `anger = 4`
- Пунктуация: "!" (4 раза) → `energy = 0.6 * 4 = 2.4` (clamped to 1.0)
- Усиление: `4 * (1 + 1.0²) = 4 * 2.0 = 8.0`
- Rage Mode: `anger > 0.22` → удалить `peace`, `calm`
- Нормализация: `anger ≈ 0.90`, другие эмоции ≈ 0.0-0.10

**Результат:** `{"anger": 0.90, "tension": 0.10}`

---

### Пример 4: Пустой/Нейтральный Текст
**Текст:** "Привет. Как дела?"

**Анализ:**
- Найдено: 0 совпадений
- Пунктуация: ".", "?" → `energy = 0.5`
- Fallback: `total_hits == 0` → используется дефолт

**Результат:** `{"peace": 0.6, "joy": 0.3, "neutral": 0.1}`

---

## 10. Итоговая Статистика

| Метрика | Значение |
|---------|----------|
| **Всего эмоций в AutoEmotionalAnalyzer** | 10 |
| **Всего ключевых слов** | 116 |
| **Языки поддержки** | Русский, Английский |
| **Типы анализа** | Regex matching, Пунктуация, Эмодзи |
| **Нормализация** | Softmax (с fallback на линейную) |
| **Специальные правила** | 4 (Peace/Sensual, Rage Mode, Road Narrative, Empty Fallback) |
| **Расширенные эмоции (V64)** | 63+ |
| **Альтернативные анализаторы** | 2 (EmotionEngineV2, EmotionEngineV64) |

---

## 11. Формулы и Алгоритмы

### Формула Энергии Пунктуации
```
punct_energy = Σ(PUNCT_WEIGHTS[char] for char in text)
emoji_energy = Σ(EMOJI_WEIGHTS[emoji] for emoji in text)
energy = min(1.0, (punct_energy + emoji_energy) ** 0.7)
```

### Формула Усиления
```
if energy > 0.1 and total_hits > 0:
    scores[emotion] *= (1 + energy²)
```

### Формула Softmax
```
max_score = max(scores.values())
exps = {k: exp(v - max_score) for k, v in scores.items()}
total = sum(exps.values())
normalized = {k: exps[k] / total for k in scores}
```

### Формула Fallback
```
if total_hits == 0 or all(v < 0.05 for v in normalized.values()):
    normalized = {"peace": 0.6, "joy": 0.3, "neutral": 0.1}
```

---

**Создано:** Текущее состояние  
**Статус:** Полная документация эмоций и процесса анализа лирики

