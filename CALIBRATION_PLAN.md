# План калибровки проекта StudioCore-API

## Результаты аудита

### Критичные проблемы:
1. ❌ Отсутствуют функции Color_Formula (6 функций)
2. ❌ Неправильный порядок движков (отсутствует StylePrompt)
3. ⚠️ Конфликты цветов (41 - но это нормально, один цвет для разных жанров)
4. ✅ Безопасность (2 проблемы - уже исправлены в комментариях)

### План исправлений:

#### 1. Добавить функции Color_Formula
**Файл:** `studiocore/color_engine_adapter.py`
- `blend(color1, color2, factor)` - смешивание цветов
- `gradient(colors, weights)` - градиент цветов
- `soften(color, factor)` - смягчение цвета
- `warm_shift(color, factor)` - теплый сдвиг
- `saturate(color, factor)` - насыщение
- `darken(color, factor)` - затемнение
- `fade(color, factor)` - затухание

#### 2. Выровнять порядок движков
**Файл:** `studiocore/core_v6.py`
**Текущий порядок:**
1. Structure ✅
2. Emotion ✅
3. TLP ✅
4. RDE ✅ (но вызывается поздно)
5. Color ✅
6. Vocal ✅
7. BPM ✅
8. Tonality ✅
9. Genre ✅
10. Instrumentation ✅
11. Annotations ✅
12. StylePrompt ❌ (отсутствует)
13. Suno ✅
14. Output ✅

**Нужно:**
- Переместить RDE после TLP (сейчас вызывается в строке 2415)
- Добавить этап StylePrompt после Annotations

#### 3. Калибровка цветов лирики по формуле
**Формула:** `LyricalColor = blend(BaseColor, LyricalShade[lyrical_genre], 0.35)`
- Применить формулу для всех лирических жанров
- Обновить `LYRICAL_GENRE_COLORS` в `genre_colors.py`

#### 4. Проверка иерархии
- Убедиться, что все движки вызываются в правильном порядке
- Проверить зависимости между движками

