# ПЛАН РЕФАКТОРИНГА _backend_analyze()

## Текущее состояние:
- **Размер:** 1587 строк
- **Сложность:** 165 (критично!)
- **Проблема:** Слишком большая функция, затрудняет поддержку и тестирование

## Стратегия рефакторинга:

### Этап 1: Выделение логических блоков в отдельные методы

1. **`_extract_engines()`** - извлечение движков из словаря
2. **`_analyze_emotions()`** - анализ эмоций и эмоциональных кривых
3. **`_call_legacy_core()`** - вызов legacy core для полного анализа
4. **`_analyze_structure()`** - структурный анализ (секции, headers)
5. **`_analyze_tlp()`** - анализ TLP (Truth, Love, Pain)
6. **`_analyze_colors()`** - анализ цветов и стиля
7. **`_analyze_vocal()`** - анализ вокала
8. **`_analyze_breathing()`** - анализ дыхания
9. **`_analyze_bpm()`** - анализ BPM и ритма
10. **`_analyze_meaning()`** - анализ meaning velocity
11. **`_analyze_tonality()`** - анализ тональности
12. **`_analyze_frequency()`** - анализ частот
13. **`_analyze_instrumentation()`** - анализ инструментов
14. **`_analyze_commands()`** - анализ команд
15. **`_analyze_rem()`** - REM синхронизация
16. **`_analyze_zero_pulse()`** - анализ zero pulse
17. **`_build_feature_map()`** - построение feature map для жанров
18. **`_analyze_genre()`** - анализ жанров
19. **`_synthesize_style()`** - синтез стиля
20. **`_route_genre()`** - роутинг жанров
21. **`_build_emotion_matrix()`** - построение emotion matrix
22. **`_apply_final_adjustments()`** - финальные корректировки
23. **`_build_fanf_output()`** - построение FANF вывода

### Этап 2: Упрощение основной функции

После выделения методов, `_backend_analyze()` станет оркестратором:

```python
def _backend_analyze(self, ...):
    # 1. Инициализация
    engines = self._extract_engines(engines)
    sections = self._resolve_sections_from_hints(...)
    
    # 2. Анализ
    emotion_data = self._analyze_emotions(...)
    legacy_result = self._call_legacy_core(...)
    structure = self._analyze_structure(...)
    tlp_profile = self._analyze_tlp(...)
    color_data = self._analyze_colors(...)
    vocal_data = self._analyze_vocal(...)
    breathing_data = self._analyze_breathing(...)
    bpm_data = self._analyze_bpm(...)
    meaning_data = self._analyze_meaning(...)
    tonality_data = self._analyze_tonality(...)
    freq_data = self._analyze_frequency(...)
    instrument_data = self._analyze_instrumentation(...)
    command_data = self._analyze_commands(...)
    rem_data = self._analyze_rem(...)
    zero_pulse_data = self._analyze_zero_pulse(...)
    
    # 3. Жанры и стиль
    feature_map = self._build_feature_map(...)
    genre_data = self._analyze_genre(...)
    style_data = self._synthesize_style(...)
    genre_routing = self._route_genre(...)
    
    # 4. Финальные шаги
    emotion_matrix = self._build_emotion_matrix(...)
    result = self._apply_final_adjustments(...)
    fanf_output = self._build_fanf_output(...)
    
    return result
```

### Ожидаемый результат:
- **Размер `_backend_analyze()`:** ~100-150 строк (вместо 1587)
- **Сложность:** <20 (вместо 165)
- **Читаемость:** Значительно улучшена
- **Тестируемость:** Каждый метод можно тестировать отдельно
- **Поддерживаемость:** Легче добавлять новые функции

## Приоритет:
1. **Высокий:** Выделить самые большие блоки (feature_map, genre_analysis, structure)
2. **Средний:** Выделить остальные блоки анализа
3. **Низкий:** Оптимизация и дальнейшее упрощение

