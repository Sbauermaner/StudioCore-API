 StudioCore API (FastAPI)

- POST `/analyze`     — принимает **сырой текст** (text/plain) или JSON с полем `lyrics`.
- POST `/analyze-json` — строгий JSON: `{"lyrics":"...", "prefer_gender":"auto|male|female"}`.
- GET `/health`       — проверка.

Ответ содержит:
- `sections` — скелет песни с сохранением авторских пометок вида `[Verse 1] [Tagelharpa + throat singing]`
- `clean_text` — автопунктуация
- `stressed_text` — упрощенные ударения
- `style_prompt` — готовый prompt (ядро StudioCore)

## Примеры cURL

Сырой текст: