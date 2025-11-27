# Конфликты и Процессы Анализа - Таблицы

Полная документация конфликтов между элементами и процессов анализа от входа текста до выхода текста.

---

## 1. Таблица Конфликтов: Цвета ↔ BPM

| Цвет | Эмоция | BPM Диапазон | Конфликт | Условие Конфликта | Разрешение |
|------|--------|--------------|----------|------------------|------------|
| #FF7AA2 | love | (70, 100, 85) | Нет | BPM в диапазоне | Использовать default: 85 |
| #FFC0CB | love_soft | (60, 100, 80) | Нет | BPM в диапазоне | Использовать default: 80 |
| #DC143C | pain | (50, 80, 65) | Да | Если BPM > 100 | Снизить BPM до 80 |
| #2C1A2E | gothic_dark | (50, 80, 65) | Да | Если BPM > 100 | Снизить BPM до 65 |
| #4B0082 | truth | (60, 90, 75) | Нет | BPM в диапазоне | Использовать default: 75 |
| #FFD93D | joy | (100, 140, 120) | Да | Если BPM < 90 | Повысить BPM до 120 |
| #40E0D0 | peace | (50, 100, 80) | Нет | BPM в диапазоне | Использовать default: 80 |
| #3E5C82 | sorrow | (50, 80, 65) | Да | Если BPM > 100 | Снизить BPM до 65 |
| #8A2BE2 | epic | (70, 100, 85) | Нет | BPM в диапазоне | Использовать default: 85 |

**Правила разрешения конфликтов:**
- Если BPM выходит за пределы диапазона цвета → скорректировать BPM к default значению
- Приоритет: цвет → BPM (цвет определяет BPM диапазон)

---

## 2. Таблица Конфликтов: Цвета ↔ Key

| Цвет | Эмоция | Key Mode | Конфликт | Условие Конфликта | Разрешение |
|------|--------|----------|----------|------------------|------------|
| #FF7AA2 | love | Major (C, G, A, E, D) | Нет | Key в списке | Использовать первый: C major |
| #FFC0CB | love_soft | Major/Minor (C, G, A minor, F) | Нет | Key в списке | Использовать первый: C major |
| #DC143C | pain | Minor (D, A, E, B minor) | Да | Если Key = Major | Изменить на A minor |
| #2C1A2E | gothic_dark | Minor (D, A, E, B, G minor) | Да | Если Key = Major | Изменить на D minor |
| #4B0082 | truth | Minor (C, G, A, F, D minor) | Да | Если Key = Major | Изменить на C minor |
| #FFD93D | joy | Major (C, G, A minor, F, D) | Нет | Key в списке | Использовать первый: C major |
| #40E0D0 | peace | Major/Minor (C, F, A minor, D minor) | Нет | Key в списке | Использовать первый: C major |
| #3E5C82 | sorrow | Minor (D, A, E, G minor) | Да | Если Key = Major | Изменить на A minor |
| #8A2BE2 | epic | Major (C, G, D, A) | Да | Если Key = Minor | Изменить на C major |

**Правила разрешения конфликтов:**
- Если Key не в списке предпочтительных → выбрать первый из списка
- Приоритет: цвет → Key (цвет определяет предпочтительные ключи)

---

## 3. Таблица Конфликтов: BPM ↔ TLP

| BPM | TLP Pain | TLP Truth | Конфликт | Условие Конфликта | Разрешение |
|-----|----------|-----------|----------|------------------|------------|
| ≥ 130 | < 0.3 | < 0.3 | Да | BPM высокий, но TLP низкий | Снизить BPM или повысить TLP |
| ≤ 95 | > 0.6 | - | Да | BPM низкий, но Pain высокий | Повысить BPM или снизить Pain |
| 100-120 | 0.3-0.6 | 0.3-0.6 | Нет | BPM соответствует TLP | Без изменений |
| 60-90 | > 0.5 | > 0.5 | Нет | BPM низкий, TLP высокий (нормально) | Без изменений |
| 120-140 | < 0.2 | < 0.2 | Да | BPM высокий, TLP очень низкий | Снизить BPM |

**Правила разрешения конфликтов (из consistency_v8.py):**
- `bpm >= 130 AND pain + truth < 0.3` → конфликт (высокий BPM, низкий TLP)
- `bpm <= 95 AND pain > 0.6` → конфликт (низкий BPM, высокий Pain)
- Приоритет: TLP → BPM (TLP определяет ожидаемый BPM диапазон)

---

## 4. Таблица Конфликтов: BPM ↔ ToneSync

| BPM | Key Mode | Конфликт | Условие Конфликта | Разрешение | Coherence Score |
|-----|----------|----------|------------------|------------|-----------------|
| > 140 | Major | Да | Высокий BPM с Major | Minor более подходит | 0.6 |
| > 140 | Minor | Нет | Высокий BPM с Minor (нормально) | Без изменений | 0.9 |
| 60-140 | Minor | Нет | Средний BPM с Minor (нормально) | Без изменений | 0.9 |
| 60-140 | Major | Нет | Средний BPM с Major (нормально) | Без изменений | 0.8 |
| < 60 | Major | Да | Очень низкий BPM с Major | Minor более подходит | 0.7 |
| < 60 | Minor | Нет | Очень низкий BPM с Minor (нормально) | Без изменений | 0.9 |

**Правила разрешения конфликтов (из consistency_v8.py):**
- Minor keys принимают широкий диапазон BPM (coherence: 0.9)
- Major keys более узкий диапазон BPM (coherence: 0.8)
- При BPM > 140 → Minor предпочтительнее (coherence: 0.6 для Major)

---

## 5. Таблица Конфликтов: Genre ↔ RDE

| Genre | RDE Dynamic | Конфликт | Условие Конфликта | Разрешение |
|-------|-------------|----------|------------------|------------|
| gothic | ≥ 0.8 | Да | Gothic требует низкую динамику | Снизить dynamic до < 0.8 |
| gothic | < 0.8 | Нет | Gothic с низкой динамикой (нормально) | Без изменений |
| drum | ≤ 0.5 | Да | Drum требует высокую динамику | Повысить dynamic до > 0.5 |
| drum | > 0.5 | Нет | Drum с высокой динамикой (нормально) | Без изменений |
| lyrical | 0.3-0.7 | Нет | Lyrical с средней динамикой (нормально) | Без изменений |
| electronic | > 0.6 | Нет | Electronic с высокой динамикой (нормально) | Без изменений |

**Правила разрешения конфликтов (из consistency_v8.py):**
- `"gothic" in genre AND dynamic >= 0.8` → конфликт
- `"drum" in genre AND dynamic <= 0.5` → конфликт
- Приоритет: Genre → RDE (жанр определяет ожидаемую динамику)

---

## 6. Таблица Конфликтов: Emotion ↔ Style

| Эмоция | Style Genre | Конфликт | Условие Конфликта | Разрешение |
|--------|-------------|----------|------------------|------------|
| love | metal | Да | Love не совместим с metal | Изменить на lyrical или soft |
| rage | lyrical | Да | Rage не совместим с lyrical | Изменить на metal или hard |
| joy | gothic | Да | Joy не совместим с gothic | Изменить на pop или electronic |
| sadness | pop | Да | Sadness не совместим с pop | Изменить на gothic или darkwave |
| peace | metal | Да | Peace не совместим с metal | Изменить на soft или ambient |
| epic | folk | Да | Epic не совместим с folk | Изменить на cinematic или orchestral |

**Правила разрешения конфликтов:**
- Использовать `emotion_to_domain_boost` для определения правильного домена
- Приоритет: Эмоция → Style (эмоция определяет стиль)

---

## 7. Таблица Конфликтов: Rhythm (BPM Header ↔ Estimated)

| Header BPM | Estimated BPM | Разница | Конфликт | Условие Конфликта | Разрешение |
|------------|---------------|---------|----------|------------------|------------|
| 120 | 85 | 35 | Да | Разница > 30 | Использовать header (приоритет автора) |
| 120 | 100 | 20 | Нет | Разница ≤ 30 | Смешивание: header * 0.7 + estimated * 0.3 |
| 100 | 95 | 5 | Нет | Разница ≤ 30 | Смешивание: header * 0.7 + estimated * 0.3 |
| 80 | 120 | 40 | Да | Разница > 30 | Использовать header (приоритет автора) |
| 140 | 110 | 30 | Нет | Разница = 30 | Смешивание: header * 0.7 + estimated * 0.3 |

**Правила разрешения конфликтов (из rhythm.py):**
- Если `abs(header_bpm - estimated_bpm) > 30` → использовать header (приоритет автора)
- Если `abs(header_bpm - estimated_bpm) ≤ 30` → смешивание: `header * 0.7 + estimated * 0.3`
- `conflict_level = clamp(abs(header - estimated) / 60.0, 0.0, 1.0)`
- `has_conflict = conflict_level > 0.2`

---

## 8. Таблица Конфликтов: Vocals ↔ Emotions

| Эмоция | Рекомендуемый Вокал | Конфликт | Условие Конфликта | Разрешение |
|--------|---------------------|----------|------------------|------------|
| love | lyric_soprano, soft_female_alto | Нет | Вокал соответствует эмоции | Без изменений |
| rage | death_growl, false_cord_scream | Нет | Вокал соответствует эмоции | Без изменений |
| love | death_growl | Да | Love требует мягкий вокал | Изменить на lyric_soprano |
| rage | lyric_soprano | Да | Rage требует агрессивный вокал | Изменить на death_growl |
| sadness | baritone, soft, vibrato | Нет | Вокал соответствует эмоции | Без изменений |
| joy | falsetto, head_voice | Нет | Вокал соответствует эмоции | Без изменений |

**Правила разрешения конфликтов:**
- Использовать `EMOTION_TO_VOCAL_MAP` для определения правильного вокала
- Приоритет: Эмоция → Вокал (эмоция определяет вокал)

---

## 9. Таблица Конфликтов: Genre ↔ Lyrics Form

| Genre | Лирическая Форма | Конфликт | Условие Конфликта | Разрешение |
|-------|------------------|----------|------------------|------------|
| lyrical | ballad | Нет | Форма соответствует жанру | Без изменений |
| lyrical | rap_text | Да | Lyrical не использует rap_text | Изменить на ballad или ode |
| hip_hop | ballad | Да | Hip-hop не использует ballad | Изменить на rap_text |
| hip_hop | rap_text | Нет | Форма соответствует жанру | Без изменений |
| gothic | sonnet | Нет | Форма соответствует жанру | Без изменений |
| pop | elegy | Да | Pop не использует elegy | Изменить на lyrical_song |

**Правила разрешения конфликтов:**
- Использовать `genre_profiles` для определения правильной формы
- Приоритет: Genre → Lyrics Form (жанр определяет форму)

---

## 10. Таблица Конфликтов: REM Layer Conflicts

| Структура | BPM Curve | Instrumentation Energy | Конфликт | Условие Конфликта | Разрешение |
|-----------|-----------|------------------------|----------|------------------|------------|
| 4 секции | 4 значения | 0.5 | Нет | Количество совпадает | Без изменений |
| 4 секции | 6 значений | - | Да | Длина BPM curve ≠ количеству секций | Выровнять длины |
| 3 секции | 3 значения | 0.9 | Да | Высокая энергия с медленным темпом (min < 90) | Повысить BPM или снизить энергию |
| 5 секций | 5 значений | 0.6 | Нет | Энергия соответствует темпу | Без изменений |

**Правила разрешения конфликтов (из logical_engines.py):**
- Если `len(sections) != len(bpm_curve)` → конфликт (level += 0.3)
- Если `energy > 0.8 AND min(bpm_curve) < 90` → конфликт (level += 0.4)
- Разрешение: "Re-balance percussion energy", "Adjust arrangement dynamics"

---

## 11. Таблица Процессов: Полная Цепь Анализа (Вход → Выход)

| Шаг | Процесс | Вход | Выход | Зависимости | Следующий Шаг |
|-----|---------|------|-------|-------------|---------------|
| 1 | **Инициализация** | text, preferred_gender | core объект | - | 2 |
| 2 | **Нормализация текста** | text | normalized_text | - | 3 |
| 3 | **Извлечение блоков** | normalized_text | text_blocks[] | - | 4 |
| 4 | **Эмоциональный анализ** | normalized_text | emotions{} | - | 5, 6, 7 |
| 5 | **TLP анализ** | normalized_text | tlp{} | - | 6, 7, 8 |
| 6 | **Rhythm анализ** | normalized_text, emotions, tlp | rhythm_analysis{} | emotions, tlp | 7, 8 |
| 7 | **Tone анализ** | normalized_text | tone_hint{} | - | 8 |
| 8 | **BPM извлечение** | rhythm_analysis | bpm (int) | rhythm_analysis | 9 |
| 9 | **Key извлечение** | tone_hint | key (str) | tone_hint | 10 |
| 10 | **Секционный анализ** | text_blocks, preferred_gender | section_profiles[] | text_blocks | 11 |
| 11 | **Семантические слои** | emotions, tlp, bpm, key | semantic_layers{} | emotions, tlp, bpm, key | 12 |
| 12 | **Style построение** | emotions, tlp, text, bpm | style{} | emotions, tlp, bpm | 13 |
| 13 | **Genre разрешение** | emotions, tlp, style | genre (str) | emotions, tlp, style | 14 |
| 14 | **Vocal аллокация** | emotions, tlp, bpm, text | vocal{} | emotions, tlp, bpm | 15 |
| 15 | **Color разрешение** | emotions, tlp, style | color_wave[] | emotions, tlp, style | 16 |
| 16 | **RDE анализ** | text, tlp | rde{} | text, tlp | 17 |
| 17 | **Integrity сканирование** | text | integrity{} | text | 18 |
| 18 | **Аннотация текста** | text_blocks, section_profiles, semantic_layers | annotated_text_ui, annotated_text_suno | text_blocks, section_profiles, semantic_layers | 19 |
| 19 | **Сборка результата** | Все предыдущие результаты | result{} | Все | 20 |
| 20 | **Выход** | result{} | JSON/Response | - | - |

---

## 12. Таблица Процессов: Детальная Цепь Эмоционального Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Нормализация текста | text | normalized_text | `normalize_text_preserve_symbols()` |
| 2 | Построение raw вектора | normalized_text | raw_emotion_vector{} | `build_raw_emotion_vector()` |
| 2.1 | Анализ ключевых слов | normalized_text | keyword_scores{} | Поиск в словарях эмоций |
| 2.2 | Анализ пунктуации | normalized_text | punct_scores{} | `PUNCT_WEIGHTS` |
| 2.3 | Анализ эмодзи | normalized_text | emoji_scores{} | `EMOJI_WEIGHTS` |
| 2.4 | Агрегация | keyword_scores, punct_scores, emoji_scores | raw_emotion_vector{} | Суммирование весов |
| 3 | Проекция на кластеры | raw_emotion_vector | cluster_vector{} | `project_to_clusters()` |
| 3.1 | Загрузка модели | - | emotion_model{} | `emotion_model_v1.json` |
| 3.2 | Проекция | raw_emotion_vector, emotion_model | cluster_vector{} | Агрегация по кластерам |
| 4 | Определение доминирующей | cluster_vector | dominant_emotion (str) | `max(cluster_vector.values())` |
| 5 | Расчет BPM базового | cluster_vector | bpm_base (float) | `compute_bpm_base()` |
| 6 | Расчет Key и Mode | cluster_vector | key_info{} | `compute_key_and_mode()` |
| 7 | Расчет Genre scores | cluster_vector | genre_scores{} | `compute_genre_scores()` |
| 8 | Выбор финального жанра | genre_scores | final_genre (str) | `pick_final_genre()` |
| 9 | Построение профиля | Все предыдущие | emotion_profile{} | `build_emotion_profile()` |

---

## 13. Таблица Процессов: Детальная Цепь Rhythm Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Поиск header BPM | text | header_bpm (float\|None) | `_extract_header_bpm()` |
| 2 | Удаление header строк | text | stripped_text (str) | `_strip_header_lines()` |
| 3 | Построение секций | stripped_text | sections{} | `_build_sections()` |
| 4 | Density BPM расчет | stripped_text, emotions, tlp | density_bpm (float) | `_density_bpm()` |
| 4.1 | Анализ строк | stripped_text | lines[] | Разделение по `\n` |
| 4.2 | Расчет базового BPM | lines | base_bpm (float) | Эвристика на основе длины строк |
| 4.3 | Эмоциональная коррекция | base_bpm, emotions | emotion_adjusted_bpm | `emotion_weight` коррекция |
| 4.4 | TLP коррекция | emotion_adjusted_bpm, tlp | tlp_adjusted_bpm | Pain boost, Love smoothing, Truth drive |
| 4.5 | CF коррекция | tlp_adjusted_bpm, cf | final_density_bpm | `(cf - 0.8) * 100 * emotion_weight` |
| 5 | Section BPM расчет | sections | section_bpms{} | `_heuristic_section_bpm()` для каждой секции |
| 6 | Estimated BPM | section_bpms, density_bpm | estimated_bpm (float\|None) | `0.65 * section_avg + 0.35 * density` |
| 7 | Global BPM разрешение | header_bpm, estimated_bpm | global_bpm (float) | `resolve_global_bpm()` |
| 8 | Конфликт детекция | header_bpm, estimated_bpm | conflict{} | `RhythmConflict` |
| 9 | Возврат анализа | Все предыдущие | rhythm_analysis{} | `RhythmAnalysis` TypedDict |

---

## 14. Таблица Процессов: Детальная Цепь Style Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Извлечение TLP | tlp{} | truth, love, pain (float) | `tlp.get("truth/love/pain")` |
| 2 | Извлечение CF | tlp{} | cf (float) | `tlp.get("conscious_frequency")` |
| 3 | Определение доминирующей эмоции | emotions{} | dominant_mood (str) | `max(emotions.values())` |
| 4 | Resolve Style и Form | tlp, cf, mood, bpm | resolved{} | `resolve_style_and_form()` |
| 4.1 | Определение key_mode | tlp, cf, mood | key_mode (str) | "minor" если sadness > 0.55, иначе "major" |
| 4.2 | Определение narrative | tlp | narrative (tuple) | ("search", "struggle", "transformation") |
| 4.3 | Определение user_mode | - | user_mode (str) | "auto" или из hints |
| 5 | Расчет Key | tlp, bpm, key_mode | key (str) | Формула на основе bpm, tlp, key_mode |
| 6 | Построение Style | Все предыдущие | style{} | `PatchedStyleMatrix.build()` |
| 7 | Genre разрешение | style, emotions | genre (str) | `HybridGenreEngine.resolve()` |
| 8 | Color разрешение | emotions, tlp, style | color_wave[] | `ColorEngineAdapter.resolve_color_wave()` |
| 9 | Возврат Style | Все предыдущие | style_payload{} | Полный style словарь |

---

## 15. Таблица Процессов: Детальная Цепь Vocal Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Грамматический анализ | text_blocks[] | genders[] | `detect_gender_from_grammar()` |
| 2 | Voice hint анализ | text_blocks[] | voice_hints[] | `detect_voice_profile()` |
| 3 | Агрегация профилей | genders[], voice_hints[] | section_profiles[] | Объединение результатов |
| 4 | Определение финального пола | section_profiles[], preferred_gender | final_gender (str) | Приоритет: UI > mixed > male > female > auto |
| 5 | Эмоциональный анализ | text | emotions{} | `AutoEmotionalAnalyzer.analyze()` |
| 6 | Определение вокальной формы | emotions, final_gender | vocal_form (str) | `VocalProfileRegistry.get()` |
| 7 | Маппинг эмоций к вокалам | emotions | vocal_techniques[] | `EMOTION_TO_VOCAL_MAP` |
| 8 | Фильтрация по интенсивности | vocal_techniques[], emotion_intensity | filtered_vocals[] | Фильтр по весам |
| 9 | Выбор топ-3 техник | filtered_vocals[] | top_vocals[] | Сортировка по весам, выбор топ-3 |
| 10 | Возврат Vocal | Все предыдущие | vocal{} | Полный vocal словарь |

---

## 16. Таблица Процессов: Детальная Цепь Genre Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Эмоциональный анализ | text | emotions{} | `AutoEmotionalAnalyzer.analyze()` |
| 2 | TLP анализ | text | tlp{} | `TruthLovePainEngine.analyze()` |
| 3 | Проекция на кластеры | emotions | clusters{} | `project_to_clusters()` |
| 4 | Расчет Genre scores | clusters | genre_scores{} | `compute_genre_scores()` |
| 5 | Color boost | emotions, style | color_boost{} | `color_to_domain_boost` |
| 6 | Emotion boost | emotions | emotion_boost{} | `emotion_to_domain_boost` |
| 7 | Domain scores | genre_scores, color_boost, emotion_boost | domain_scores{} | Агрегация всех бустов |
| 8 | Выбор домена | domain_scores | domain (str) | `max(domain_scores.values())` |
| 9 | Genre разрешение | domain, genre_scores | genre (str) | `HybridGenreEngine.resolve()` |
| 10 | Fallback проверка | genre | final_genre (str) | Если genre пустой → fallback_by_domain |
| 11 | Возврат Genre | Все предыдущие | genre{} | Полный genre словарь |

---

## 17. Таблица Процессов: Детальная Цепь RDE Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | TLP анализ | text | tlp{} | `TruthLovePainEngine.analyze()` |
| 2 | Расчет Resonance | text, tlp | resonance (float) | Анализ повторений, рефренов |
| 3 | Расчет Fracture | text | fracture (float) | Анализ структурных разрывов |
| 4 | Расчет Entropy | text | entropy (float) | Анализ разнообразия токенов |
| 5 | Smoothing (если низкие эмоции) | resonance, fracture, entropy, tlp | smoothed_rde{} | Применение smoothing factors |
| 6 | Построение RDE профиля | resonance, fracture, entropy | rde{} | `RDESnapshot` |
| 7 | Экспорт Emotion Vector | rde, tlp | emotion_vector{} | `export_emotion_vector()` |
| 8 | Возврат RDE | Все предыдущие | rde{} | Полный RDE словарь |

---

## 18. Таблица Процессов: Детальная Цепь Color Анализа

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Проверка locked color | style{} | locked_color[] | `style.get("_color_locked")` |
| 2 | Если locked → возврат | locked_color[] | color_wave[] | `ColorResolution(colors=locked_color)` |
| 3 | Извлечение TLP | result{} | tlp{} | `result.get("tlp")` |
| 4 | Извлечение эмоций | result{} | emotions{} | `result.get("emotion")` |
| 5 | Проверка low-emotion | tlp | is_low_emotion (bool) | `pain <= LOW_EMOTION_TLP_PAIN_MAX AND truth <= LOW_EMOTION_TLP_TRUTH_MIN` |
| 6 | Если low-emotion → neutral | - | neutral_color[] | `NEUTRAL_COLOR_WAVE` |
| 7 | Определение доминирующей эмоции | emotions | dominant_emotion (str) | `max(emotions.values())` |
| 8 | Маппинг эмоции к цветам | dominant_emotion | colors[] | `get_emotion_colors(dominant)` |
| 9 | Проверка hybrid genre | style{} | is_hybrid (bool) | `"hybrid" in genre_label.lower()` |
| 10 | Если hybrid → смешивание | colors, genre_label | hybrid_colors[] | `_resolve_hybrid_colors()` |
| 11 | Возврат Color | Все предыдущие | color_wave[] | `ColorResolution` |

---

## 19. Таблица Процессов: Детальная Цепь Annotation

| Шаг | Процесс | Вход | Выход | Метод/Функция |
|-----|---------|------|-------|---------------|
| 1 | Построение semantic map | text_blocks[] | semantic_map[] | Маппинг блоков к секциям (Intro, Verse, Chorus, etc.) |
| 2 | Извлечение секций | semantic_sections[] | sec_defs{} | Словарь определений секций |
| 3 | Итерация по блокам | text_blocks[], section_profiles[], semantic_map | - | Для каждого блока |
| 4 | Определение тега | semantic_map[i] | tag_name (str) | "intro", "verse", "chorus", etc. |
| 5 | Извлечение семантики | tag_name, sec_defs | sem{} | Mood, energy, arrangement, bpm, key |
| 6 | Извлечение gender | section_profiles[i] | gender_tag (str) | "MALE", "FEMALE", "MIXED", "AUTO" |
| 7 | Построение Suno тега | tag_name, gender_tag, sem | suno_tag (str) | `[VERSE - vocal: MALE - mood: narrative - energy: mid - arrangement: standard]` |
| 8 | Построение UI тега | tag_name, gender_tag, sem | ui_tag (str) | `[VERSE - MALE - narrative, mid, standard, BPM≈85]` |
| 9 | Добавление блока | suno_tag, ui_tag, block_text | - | Добавление в suno_blocks и ui_blocks |
| 10 | Финальный тег | final_bpm, final_key | end_tag (str) | `[End – BPM≈85, Tone=Am]` |
| 11 | Возврат аннотаций | Все предыдущие | annotated_text_ui, annotated_text_suno | Две версии аннотированного текста |

---

## 20. Таблица Процессов: Полная Цепь от Входа до Выхода (Сводная)

| Этап | Процессы | Вход | Промежуточные Результаты | Выход |
|------|----------|------|--------------------------|-------|
| **ВХОД** | - | text, preferred_gender | - | - |
| **1. Предобработка** | Нормализация, Извлечение блоков | text | normalized_text, text_blocks[] | text_blocks[] |
| **2. Базовый Анализ** | Emotion, TLP, Rhythm, Tone | text_blocks[] | emotions{}, tlp{}, rhythm_analysis{}, tone_hint{} | Базовые метрики |
| **3. Извлечение Параметров** | BPM, Key | rhythm_analysis{}, tone_hint{} | bpm (int), key (str) | bpm, key |
| **4. Секционный Анализ** | Грамматика, Voice hints | text_blocks[], preferred_gender | section_profiles[] | section_profiles[] |
| **5. Семантические Слои** | Построение слоев | emotions{}, tlp{}, bpm, key | semantic_layers{} | semantic_layers{} |
| **6. Style Анализ** | Style, Genre, Color | emotions{}, tlp{}, text, bpm | style{}, genre{}, color_wave[] | style{}, genre{}, color_wave[] |
| **7. Vocal Анализ** | Vocal аллокация | emotions{}, tlp{}, bpm, text | vocal{} | vocal{} |
| **8. RDE Анализ** | RDE расчет | text, tlp{} | rde{} | rde{} |
| **9. Integrity** | Integrity сканирование | text | integrity{} | integrity{} |
| **10. Аннотация** | Аннотация текста | text_blocks[], section_profiles[], semantic_layers{} | annotated_text_ui, annotated_text_suno | annotated_text_ui, annotated_text_suno |
| **11. Сборка** | Сборка результата | Все предыдущие | result{} | result{} |
| **ВЫХОД** | - | result{} | - | JSON/Response |

---

## 21. Таблица Конфликтов: Сводная (Все Типы)

| Тип Конфликта | Элемент 1 | Элемент 2 | Условие | Разрешение | Приоритет |
|---------------|-----------|-----------|---------|-----------|-----------|
| **Color ↔ BPM** | Цвет | BPM | BPM вне диапазона цвета | Скорректировать BPM к default | Цвет → BPM |
| **Color ↔ Key** | Цвет | Key | Key не в списке предпочтительных | Выбрать первый из списка | Цвет → Key |
| **BPM ↔ TLP** | BPM | TLP | BPM не соответствует TLP интенсивности | Скорректировать BPM или TLP | TLP → BPM |
| **BPM ↔ ToneSync** | BPM | Key Mode | Высокий BPM с Major | Изменить на Minor | BPM → Key |
| **Genre ↔ RDE** | Genre | RDE Dynamic | Dynamic не соответствует жанру | Скорректировать dynamic | Genre → RDE |
| **Emotion ↔ Style** | Эмоция | Style Genre | Эмоция не совместима с жанром | Изменить жанр | Эмоция → Style |
| **Rhythm Conflict** | Header BPM | Estimated BPM | Разница > 30 | Использовать header | Header → Estimated |
| **Vocals ↔ Emotions** | Эмоция | Вокал | Вокал не соответствует эмоции | Изменить вокал | Эмоция → Вокал |
| **Genre ↔ Lyrics** | Genre | Lyrics Form | Форма не соответствует жанру | Изменить форму | Genre → Lyrics |
| **REM Layer** | Структура | BPM Curve | Длины не совпадают | Выровнять длины | Структура → BPM |

---

## 22. Таблица Процессов: Параллельные Цепи

| Параллельная Цепь | Процессы | Зависимости | Результат |
|-------------------|----------|-------------|-----------|
| **Цепь 1: Emotion** | Emotion анализ → TLP анализ → RDE анализ | Emotion → TLP → RDE | emotions{}, tlp{}, rde{} |
| **Цепь 2: Rhythm** | Rhythm анализ → BPM извлечение → Tone анализ → Key извлечение | Rhythm → BPM, Tone → Key | bpm, key |
| **Цепь 3: Style** | Style анализ → Genre разрешение → Color разрешение | Style → Genre → Color | style{}, genre{}, color_wave[] |
| **Цепь 4: Vocal** | Секционный анализ → Vocal аллокация → Vocal маппинг | Секции → Vocal | vocal{} |
| **Цепь 5: Annotation** | Semantic слои → Аннотация → Сборка | Semantic → Annotation → Result | annotated_text_ui, annotated_text_suno |

**Порядок выполнения:**
1. Цепь 1 и Цепь 2 выполняются параллельно (независимы)
2. Цепь 3 зависит от Цепи 1 и Цепи 2
3. Цепь 4 зависит от Цепи 1
4. Цепь 5 зависит от всех предыдущих цепей

---

## 23. Таблица Процессов: Временная Сложность

| Процесс | Временная Сложность | Зависит от | Оптимизация |
|---------|-------------------|------------|------------|
| Нормализация текста | O(n) | Длина текста | Кэширование |
| Эмоциональный анализ | O(n * m) | Длина текста, количество эмоций | Предкомпиляция словарей |
| TLP анализ | O(n * k) | Длина текста, количество TLP слов | Предкомпиляция словарей |
| Rhythm анализ | O(n * s) | Длина текста, количество секций | Параллельная обработка секций |
| Tone анализ | O(n) | Длина текста | Кэширование |
| Style анализ | O(1) | Константа | - |
| Genre разрешение | O(g) | Количество жанров | Предкомпиляция маппингов |
| Vocal аллокация | O(v) | Количество вокалов | Предкомпиляция маппингов |
| Color разрешение | O(1) | Константа | - |
| RDE анализ | O(n) | Длина текста | - |
| Integrity сканирование | O(n) | Длина текста | - |
| Аннотация | O(b) | Количество блоков | - |

**Общая сложность:** O(n * m) где n = длина текста, m = количество эмоций

---

## 24. Таблица Процессов: Порядок Разрешения Конфликтов

| Приоритет | Конфликт | Разрешение | Когда Применяется |
|-----------|----------|-----------|------------------|
| 1 | Header BPM vs Estimated BPM | Использовать header если разница > 30 | Сразу после Rhythm анализа |
| 2 | Color vs BPM | Скорректировать BPM к default цвета | После Color разрешения |
| 3 | Color vs Key | Выбрать первый Key из списка цвета | После Color разрешения |
| 4 | BPM vs TLP | Скорректировать BPM или TLP | После BPM и TLP анализа |
| 5 | BPM vs ToneSync | Изменить Key Mode | После Tone анализа |
| 6 | Genre vs RDE | Скорректировать RDE dynamic | После Genre разрешения |
| 7 | Emotion vs Style | Изменить Genre | После Style анализа |
| 8 | Vocals vs Emotions | Изменить Вокал | После Vocal аллокации |
| 9 | Genre vs Lyrics | Изменить Lyrics Form | После Genre разрешения |
| 10 | REM Layer Conflicts | Выровнять длины | После всех анализов |

---

## Резюме

**Основные конфликты:**
1. **Color ↔ BPM/Key** - цвета определяют BPM диапазоны и предпочтительные ключи
2. **BPM ↔ TLP** - BPM должен соответствовать эмоциональной интенсивности TLP
3. **Genre ↔ RDE** - жанр определяет ожидаемую динамику RDE
4. **Emotion ↔ Style/Vocals** - эмоции определяют стиль и вокалы
5. **Rhythm Conflicts** - конфликты между header BPM и estimated BPM

**Основные процессы:**
1. **Предобработка** - нормализация и извлечение блоков
2. **Базовый анализ** - Emotion, TLP, Rhythm, Tone
3. **Извлечение параметров** - BPM, Key
4. **Секционный анализ** - грамматика, voice hints
5. **Семантические слои** - построение слоев
6. **Style анализ** - Style, Genre, Color
7. **Vocal анализ** - аллокация вокалов
8. **RDE анализ** - расчет RDE
9. **Аннотация** - аннотация текста
10. **Сборка** - сборка финального результата

**Порядок разрешения конфликтов:**
1. Header BPM (приоритет автора)
2. Color (определяет BPM/Key)
3. TLP (определяет BPM)
4. Genre (определяет RDE)
5. Emotion (определяет Style/Vocals)

---

**Создано:** Текущее состояние  
**Статус:** Полные таблицы конфликтов и процессов

