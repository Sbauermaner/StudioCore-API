# 📊 ПОЛНЫЙ ОТЧЕТ: ЛОГИКА GENRE И ФОРМИРОВАНИЕ STYLE

## 🔍 КРИТИЧЕСКИЕ МЕСТА ПЕРЕЗАПИСИ GENRE

### ⚠️ ПРОБЛЕМА: genre = "lyrical_song" устанавливается в МНОЖЕСТВЕ мест как fallback

---

## 1️⃣ ОПЕРАЦИЯ (A): ЗАПИСЬ GENRE

### Файл: `studiocore/core_v6.py`

#### Место 1: Строки 2201, 2207, 2212, 2224, 2231, 2251, 2254, 2257, 2261, 2270, 2289, 2293
**Тип:** (D) Fallback-логика `genre = "lyrical_song"`

**Контекст:**
```python
# Строка 2200-2202
if love_level > 0.5 and pain_level < 0.5:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "love_lyric_conversion"

# Строка 2206-2208
elif truth_level > 0.5 and love_level > 0.3:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "confessional_lyric"

# Строка 2211-2213
elif domain_genre == "gothic_poetry" and love_level > 0.4:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "love_lyric_override"

# Строка 2223-2225
elif poetic_bias > 0.25 or lyric_bias > 0.25:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "lyrical_to_music_conversion"

# Строка 2230-2232
else:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ (fallback)
    genre_source = "lyrical_fallback"

# Строка 2250-2252
else:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "emotion_based"

# Строка 2254-2255
elif love_level > 0.6:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "emotion_based"

# Строка 2257-2258
elif dominant_emotion and dominant_emotion in ("sadness", "melancholy", "sorrow"):
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "emotion_based"

# Строка 2261-2262
elif (pain_level > 0.3 or love_level > 0.3) and (poetic_bias > 0.05 or lyric_bias > 0.05):
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "emotion_tlp_based"

# Строка 2270-2271
else:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "lyrical_conversion"

# Строка 2289-2290
else:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ
    genre_source = "final_tlp_fallback"

# Строка 2293-2294
else:
    domain_genre = "lyrical_song"  # ⚠️ ПЕРЕЗАПИСЬ (абсолютный fallback)
    genre_source = "final_fallback"
```

**Проблема:** `domain_genre` устанавливается в "lyrical_song" в 12+ местах как fallback, что перезаписывает любые другие значения.

---

#### Место 2: Строка 2469
**Тип:** (A) Запись genre в style_payload

**Контекст:**
```python
# Строка 2303-2308
style_genre = (
    style_commands.get("genre")
    or semantic_hints.get("style", {}).get("genre")
    or domain_genre  # ⚠️ domain_genre уже может быть "lyrical_song"
    or self.style_engine.genre_selection(emotion_profile, tlp_profile)
)

# Строка 2468-2470
style_payload = {
    "genre": style_genre,  # ⚠️ ЗАПИСЬ genre в style_payload
    "mood": style_mood,
    ...
}
```

**Проблема:** `style_genre` формируется из `domain_genre`, который уже может быть "lyrical_song".

---

#### Место 3: Строка 2505-2506
**Тип:** (A) Запись genre из macro_genre

**Контекст:**
```python
# Строка 2499
macro_genre, genre_reason = self.genre_router.route(router_input)

# Строка 2505-2506
if "genre" not in style_block or str(style_block.get("genre")).lower() in ("auto", "unknown", ""):
    style_block["genre"] = macro_genre  # ⚠️ ПЕРЕЗАПИСЬ если genre пустой
```

**Проблема:** Если genre не установлен, он берется из `macro_genre`, который может быть "lyrical_song".

---

#### Место 4: Строка 2564-2565
**Тип:** (A) Запись genre из final_genre

**Контекст:**
```python
# Строка 2548-2551
final_genre = emotion_engine.pick_final_genre(
    emotion_profile_v1.get("genre_scores", {}),
    legacy_genre=legacy_genre,  # legacy_genre = style_payload.get("genre")
)

# Строка 2564-2565
if "genre" not in overrides_block and isinstance(style_payload, dict):
    style_payload.setdefault("genre", final_genre)  # ⚠️ ПЕРЕЗАПИСЬ если genre не в overrides
```

**Проблема:** `final_genre` может перезаписать genre, если он не в overrides.

---

#### Место 5: Строка 1036-1040
**Тип:** (A) Запись genre из fusion_summary

**Контекст:**
```python
# Строка 1036-1040
final_genre = fusion_summary.get("final_genre") or fusion_summary.get("final_subgenre")
if final_genre:
    style_block = backend_updates.setdefault("style", {})
    style_block["genre"] = final_genre  # ⚠️ ПЕРЕЗАПИСЬ из fusion_engine
    style_block.setdefault("subgenre", final_genre)
```

**Проблема:** `fusion_summary` может перезаписать genre в `backend_updates["style"]`.

---

#### Место 6: Строка 1047-1048
**Тип:** (A) Запись genre из macro_genre

**Контекст:**
```python
# Строка 1043-1048
style_block = backend_payload.get("style")
if isinstance(style_block, dict):
    macro_genre = style_block.get("macro_genre") or style_block.get("subgenre")
    current_genre = style_block.get("genre")
    if macro_genre and (not current_genre or macro_genre not in current_genre):
        backend_updates.setdefault("style", {})["genre"] = macro_genre  # ⚠️ ПЕРЕЗАПИСЬ
```

**Проблема:** `macro_genre` может перезаписать genre, если `current_genre` пустой или не содержит `macro_genre`.

---

#### Место 7: Строка 2718
**Тип:** (C) Копирование style_block в result

**Контекст:**
```python
# Строка 2710-2718
style_block = result.get("style") if isinstance(result.get("style"), dict) else {}
style_block.setdefault("bpm", bpm)
# Сохраняем mood и color_wave из style_payload, если они есть
if isinstance(style_payload, dict):
    if style_payload.get("mood"):
        style_block["mood"] = style_payload.get("mood")
    if style_payload.get("color_wave"):
        style_block["color_wave"] = style_payload.get("color_wave")
result["style"] = style_block  # ⚠️ КОПИРОВАНИЕ style_block в result
```

**Проблема:** `style_block` копируется в `result["style"]`, но genre НЕ обновляется из `style_payload`.

---

#### Место 8: Строка 2951-2952
**Тип:** (C) Обновление result["style"] из style_payload

**Контекст:**
```python
# Строка 2949-2952
# Обновляем result["style"] с сохранением всех полей из style_payload
# Важно: используем update, чтобы не потерять существующие поля
style_result.update(style_payload)  # ⚠️ genre из style_payload перезаписывает genre в style_result
result["style"] = style_result
```

**Проблема:** `style_payload.update()` перезаписывает genre в `style_result`, но это происходит ДО `_apply_road_narrative_overrides`.

---

#### Место 9: Строка 3194 (MASTER-PATCH v2)
**Тип:** (A) Запись genre = "dark country rap ballad"

**Контекст:**
```python
# Строка 3190-3194
style = result.setdefault("style", {})
# 1) Genre / style
old_genre = style.get("genre")
if not old_genre or old_genre == "lyrical_song":
    style["genre"] = "dark country rap ballad"  # ✅ ПРАВИЛЬНАЯ ЗАПИСЬ
```

**Проблема:** Это происходит в `_apply_road_narrative_overrides`, который вызывается в `_build_final_result`, НО после этого может быть еще перезапись.

---

#### Место 10: Строка 3687-3692 (_finalize_result)
**Тип:** (C) Копирование genre из payload["style"]

**Контекст:**
```python
# Строка 3687-3692
# Обновляем остальные поля из payload["style"], но НЕ перезаписываем mood и color_wave
if isinstance(style_from_payload, dict):
    for key, value in style_from_payload.items():
        # Пропускаем mood и color_wave, так как они уже установлены выше
        if key not in ("mood", "color_wave"):
            style_from_merged[key] = value  # ⚠️ genre перезаписывается из payload["style"]
```

**Проблема:** genre из `payload["style"]` перезаписывает genre в `style_from_merged`, который уже может содержать "dark country rap ballad" из `_apply_road_narrative_overrides`.

---

## 2️⃣ ОПЕРАЦИЯ (B): ЧТЕНИЕ GENRE

### Файл: `studiocore/core_v6.py`

#### Место 1: Строка 1046
**Тип:** (B) Чтение genre из style_block

```python
current_genre = style_block.get("genre")
```

#### Место 2: Строка 1095
**Тип:** (B) Чтение genre для genre_universe

```python
if isinstance(style_block, dict) and style_block.get("genre"):
    genre_info = genre_universe.detect_domain(str(style_block.get("genre")))
```

#### Место 3: Строка 1127
**Тип:** (B) Чтение genre для macro_genre

```python
macro_genre = (
    payload.get("style", {}).get("macro_genre")
    or payload.get("style", {}).get("genre")  # ⚠️ ЧТЕНИЕ genre
    or payload.get("style", {}).get("subgenre")
)
```

#### Место 4: Строка 1219
**Тип:** (B) Чтение genre для lyrics sections

```python
genre = style_block.get("genre", "adaptive")
```

#### Место 5: Строка 1822
**Тип:** (B) Чтение genre для vocal techniques

```python
genre=style_payload.get("genre") if isinstance(style_payload, dict) else None,
```

#### Место 6: Строка 2063
**Тип:** (B) Чтение genre из legacy_result

```python
genre=legacy_result.get("style", {}).get("genre") if isinstance(legacy_result, dict) else None,
```

#### Место 7: Строка 2176
**Тип:** (B) Чтение genre из legacy_result

```python
legacy_style_genre = legacy_result.get("style", {}).get("genre") if isinstance(legacy_result, dict) else None
```

#### Место 8: Строка 2304-2305
**Тип:** (B) Чтение genre из commands и semantic_hints

```python
style_genre = (
    style_commands.get("genre")  # ⚠️ ЧТЕНИЕ из commands
    or semantic_hints.get("style", {}).get("genre")  # ⚠️ ЧТЕНИЕ из semantic_hints
    or domain_genre
    or self.style_engine.genre_selection(emotion_profile, tlp_profile)
)
```

#### Место 9: Строка 2546
**Тип:** (B) Чтение genre из style_payload

```python
legacy_genre = style_payload.get("genre") if isinstance(style_payload, dict) else None
```

#### Место 10: Строка 2603
**Тип:** (B) Чтение genre для style_prompt

```python
"genre": style_payload.get("genre") if isinstance(style_payload, dict) else None,
```

#### Место 11: Строка 2679
**Тип:** (B) Чтение genre из result["style"]

```python
genre_hint=result["style"].get("genre") if "style" in result else None,
```

#### Место 12: Строка 3001
**Тип:** (B) Чтение genre для summary

```python
macro_genre = style_block.get("macro_genre") or style_block.get("genre") or style_block.get("subgenre")
```

#### Место 13: Строка 3192-3193
**Тип:** (B) Чтение genre в _apply_road_narrative_overrides

```python
old_genre = style.get("genre")
if not old_genre or old_genre == "lyrical_song":
```

---

## 3️⃣ ОПЕРАЦИЯ (C): КОПИРОВАНИЕ GENRE МЕЖДУ СЛОВАРЯМИ

### Файл: `studiocore/core_v6.py`

#### Место 1: Строка 770-812
**Тип:** (C) payload.update(backend_payload) - копирование style

```python
# Строка 792
payload.update(backend_payload)  # ⚠️ backend_payload["style"]["genre"] копируется в payload["style"]["genre"]

# Строка 796-812
if isinstance(backend_style, dict):
    payload_style = payload.get("style", {})
    # ...
    # Обновляем остальные поля из backend_style, но НЕ перезаписываем mood и color_wave
    for key, value in backend_style.items():
        if key not in ("mood", "color_wave"):
            payload_style[key] = value  # ⚠️ genre перезаписывается
    payload["style"] = payload_style
```

**Проблема:** genre из `backend_payload["style"]` перезаписывает genre в `payload["style"]`, но mood и color_wave защищены.

---

#### Место 2: Строка 1078-1090
**Тип:** (C) payload.update(backend_payload) в _build_diagnostics_blocks

```python
# Строка 1078
payload.update(backend_payload)  # ⚠️ genre копируется

# Строка 1082-1090
if saved_mood or saved_color_wave:
    payload_style_after = payload.get("style", {})
    # ...
    payload["style"] = payload_style_after  # ⚠️ genre НЕ защищен
```

**Проблема:** genre не защищен от перезаписи, в отличие от mood и color_wave.

---

#### Место 3: Строка 1333 (_finalize_result)
**Тип:** (C) final_result = _finalize_result(payload)

```python
final_result = self._finalize_result(payload)  # ⚠️ payload["style"]["genre"] копируется в final_result["style"]["genre"]
```

---

#### Место 4: Строка 3687-3692 (_finalize_result)
**Тип:** (C) Копирование genre из payload["style"] в merged["style"]

```python
# Обновляем остальные поля из payload["style"], но НЕ перезаписываем mood и color_wave
if isinstance(style_from_payload, dict):
    for key, value in style_from_payload.items():
        if key not in ("mood", "color_wave"):
            style_from_merged[key] = value  # ⚠️ genre перезаписывается
```

**Проблема:** genre НЕ защищен от перезаписи, в отличие от mood и color_wave.

---

## 4️⃣ ОПЕРАЦИЯ (D): FALLBACK-ЛОГИКА

### Файл: `studiocore/core_v6.py`

#### Место 1: Строки 2201, 2207, 2212, 2224, 2231, 2251, 2254, 2257, 2261, 2270, 2289, 2293
**Тип:** (D) Множественные fallback на "lyrical_song"

**Проблема:** В 12+ местах `domain_genre = "lyrical_song"` устанавливается как fallback, что перезаписывает любые другие значения.

---

### Файл: `studiocore/genre_weights.py`

#### Место 2: Строка 442
**Тип:** (D) Fallback на "lyrical_song"

```python
if domain == "electronic" and (poetic > 0.35 or lyric > 0.35 or gothic > 0.25):
    return "lyrical_song"  # ⚠️ FALLBACK
```

---

## 5️⃣ ОПЕРАЦИЯ (E): ФОРМИРОВАНИЕ ФИНАЛЬНОГО ВЫВОДА

### Файл: `studiocore/core_v6.py`

#### Место 1: Строка 841
**Тип:** (E) return final_result

```python
return final_result  # ⚠️ ФИНАЛЬНЫЙ ВЫВОД
```

**Проблема:** `final_result` формируется в `_build_final_result`, но `_apply_road_narrative_overrides` вызывается ДО `_finalize_result`, который может перезаписать genre.

---

## 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА

### Цепочка перезаписи genre:

1. **Строка 2293:** `domain_genre = "lyrical_song"` (абсолютный fallback)
2. **Строка 2303-2307:** `style_genre = domain_genre or ...` → `style_genre = "lyrical_song"`
3. **Строка 2469:** `style_payload["genre"] = style_genre` → `style_payload["genre"] = "lyrical_song"`
4. **Строка 2505-2506:** `style_block["genre"] = macro_genre` (может быть "lyrical_song")
5. **Строка 2564-2565:** `style_payload.setdefault("genre", final_genre)` (может быть "lyrical_song")
6. **Строка 1036-1040:** `backend_updates["style"]["genre"] = final_genre` (из fusion_summary)
7. **Строка 1047-1048:** `backend_updates["style"]["genre"] = macro_genre` (если current_genre пустой)
8. **Строка 792:** `payload.update(backend_payload)` → genre копируется в payload
9. **Строка 2951:** `style_result.update(style_payload)` → genre перезаписывается в result["style"]
10. **Строка 3065-3105:** `_apply_road_narrative_overrides` → устанавливает genre = "dark country rap ballad"
11. **Строка 1333:** `final_result = _finalize_result(payload)` → genre может быть перезаписан
12. **Строка 3687-3692:** genre из `payload["style"]` перезаписывает genre в `merged["style"]` (НЕ защищен!)

---

## ✅ РЕШЕНИЕ

### Нужно защитить genre от перезаписи в `_finalize_result`, аналогично mood и color_wave:

```python
# В _finalize_result, строка 3687-3692
# Обновляем остальные поля из payload["style"], но НЕ перезаписываем mood, color_wave И genre
if isinstance(style_from_payload, dict):
    for key, value in style_from_payload.items():
        # Пропускаем mood, color_wave И genre, если они уже установлены в merged
        if key not in ("mood", "color_wave", "genre"):
            style_from_merged[key] = value
        # Или проверяем, не был ли genre установлен в _apply_road_narrative_overrides
        elif key == "genre" and style_from_merged.get("genre") not in (None, "lyrical_song", "auto", "unknown", ""):
            # Не перезаписываем genre, если он уже установлен в merged (например, "dark country rap ballad")
            pass
```

---

## 📋 ИТОГОВАЯ ТАБЛИЦА ОПЕРАЦИЙ С GENRE

| Строка | Файл | Тип | Операция | Проблема |
|--------|------|-----|----------|----------|
| 2201, 2207, 2212, 2224, 2231, 2251, 2254, 2257, 2261, 2270, 2289, 2293 | core_v6.py | (D) | `domain_genre = "lyrical_song"` | Fallback перезаписывает genre |
| 2469 | core_v6.py | (A) | `style_payload["genre"] = style_genre` | Запись genre в style_payload |
| 2505-2506 | core_v6.py | (A) | `style_block["genre"] = macro_genre` | Перезапись если genre пустой |
| 2564-2565 | core_v6.py | (A) | `style_payload.setdefault("genre", final_genre)` | Перезапись если genre не в overrides |
| 1036-1040 | core_v6.py | (A) | `style_block["genre"] = final_genre` | Перезапись из fusion_summary |
| 1047-1048 | core_v6.py | (A) | `backend_updates["style"]["genre"] = macro_genre` | Перезапись если current_genre пустой |
| 792 | core_v6.py | (C) | `payload.update(backend_payload)` | Копирование genre |
| 1078 | core_v6.py | (C) | `payload.update(backend_payload)` | Копирование genre |
| 2951 | core_v6.py | (C) | `style_result.update(style_payload)` | Перезапись genre |
| 3194 | core_v6.py | (A) | `style["genre"] = "dark country rap ballad"` | ✅ ПРАВИЛЬНАЯ ЗАПИСЬ (MASTER-PATCH v2) |
| 3687-3692 | core_v6.py | (C) | `style_from_merged[key] = value` | ⚠️ genre перезаписывается (НЕ защищен!) |
| 841 | core_v6.py | (E) | `return final_result` | Финальный вывод |

---

## 🎯 ВЫВОД

**Проблема:** genre перезаписывается в `_finalize_result` (строка 3687-3692), где он НЕ защищен от перезаписи, в отличие от mood и color_wave.

**Решение:** Добавить защиту genre в `_finalize_result`, аналогично mood и color_wave, чтобы genre из `_apply_road_narrative_overrides` не был перезаписан.

