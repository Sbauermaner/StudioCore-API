# Отчет об отладке style.mood и style.color_wave

## Проблема

В отладочном логе видно, что в `_backend_analyze()` `style_payload` содержит:
- `mood: 'melancholic'`
- `color_wave: ['#40E0D0', '#E0F7FA', '#FFFFFF', '#FFD93D', '#FFD93D']`

Но в финальном результате `style` содержит только:
- `['bpm', 'key', 'genre', 'subgenre']`

## Причина

`result["style"]` перезаписывается в нескольких местах:
1. В строке 2241: `result["style"] = style_block` (после установки BPM)
2. В строке 2421: `result["style"] = style_block` (после color_adapter)
3. В строке 2473: `result["style"] = style_result` (после обновления style_payload)
4. В `_finalize_result()`: `merged["style"] = payload.get("style", {})` (строка 3026)

## Исправления

1. **В `_build_final_result()`**: Добавлена проверка и восстановление `mood` и `color_wave` из `payload["style"]` перед возвратом
2. **В `build_fanf_output()`**: Добавлена проверка и восстановление `mood` и `color_wave` из параметра `style`
3. **В `_backend_analyze()`**: Добавлено сохранение `mood` и `color_wave` в нескольких местах

## Статус

Исправления применены. Требуется проверка.

