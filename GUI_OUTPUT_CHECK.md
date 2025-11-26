# Проверка вывода в GUI

## Результаты проверки

### ✅ Structure (Структура)
- **Секций:** 5
- **Имена секций:** Intro, Verse, Pre-Chorus, Chorus, Outro
- **Headers:** Правильно передаются в результат

### ✅ Lyrics Prompt
Правильно отображаются имена секций:
```
[INTRO: mood=neutral, energy=mid, arr=standard]
Не жалею, не зову, не плачу,
...

[VERSE: mood=neutral, energy=mid, arr=standard]
Ты теперь не так уж будешь биться,
...

[PRE-CHORUS: mood=neutral, energy=mid, arr=standard]
Дух бродяжий! ты все реже, реже
...

[CHORUS: mood=neutral, energy=mid, arr=standard]
Я теперь скупее стал в желаньях,
...

[OUTRO: mood=neutral, energy=mid, arr=standard]
Все мы, все мы в этом мире тленны,
...
```

### ✅ UI Text
Текст правильно форматируется без лишних аннотаций для отображения в UI.

### ✅ RDE / Sections Panel
Функция `build_rde_section_text` в `app.py` обновлена для правильного отображения имен секций из headers.

## Исправления

1. **`app.py` - `build_rde_section_text`:**
   - Использует `headers` из структуры для получения имен секций
   - Правильно подсчитывает количество строк в секциях
   - Отображает имена: Intro, Verse, Pre-Chorus, Chorus, Outro

2. **`studiocore/core_v6.py` - `build_fanf_output`:**
   - Использует правильные имена секций из `lyrics_sections`
   - Fallback логика для правильного именования секций согласно структуре

3. **`studiocore/core_v6.py` - формирование `lyrics_sections`:**
   - Использует `tag` из headers в первую очередь
   - Правильно преобразует секции в список строк для `lines`

## Вывод

Все выходные данные для GUI правильно форматируются и отображают имена секций согласно структуре песни.

