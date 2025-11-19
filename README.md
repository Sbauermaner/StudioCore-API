# StudioCore v6.4 MAXI — Adaptive Music Intelligence / Адаптивный музыкальный интеллект

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-ready-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT%20+%20restrictions-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-Sbauermaner%2FStudioCore-black)](https://github.com/Sbauermaner/StudioCore)

**Автор / Author:** Сергей Бауэр (@Sbauermaner)

---

## 🇷🇺 Обзор
StudioCore v6.4 MAXI — статлес-движок для анализа лирики и генерации музыкальных подсказок. FastAPI и Gradio оборачивают ядро StudioCoreV6, обеспечивая HTTP API, публичный UI и встроенные самопроверки. Все лишние файлы удалены, конфигурация готова к публичному релизу.

### Возможности
- Анализ текста: жанр, BPM, тональность, эмоции, вокал, структурные секции.
- Suno-friendly подсказки и аннотированный текст для генераторов музыки.
- Диагностика: `/status`, `/version`, `/diagnostics`, `/healthcheck` с детализированными метриками загрузчика.
- UI на Gradio и CLI (`python -m studiocore.app`) для офлайн-проверок.
- Полностью статлес: каждый запрос создаёт свежий экземпляр ядра с блокировками на уровне загрузчика.

### Быстрый старт
1. Установите зависимости:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Запустите сервер:
   ```bash
   python app.py
   # или
   uvicorn app:app --host 0.0.0.0 --port 7860
   ```
3. Откройте браузер: `http://127.0.0.1:7860` для Gradio UI или `http://127.0.0.1:7860/docs` для OpenAPI.

### Тесты
- Inline-кнопка во вкладке «Логи и тесты» пытается запустить `pytest -q tests` (если установлен pytest).
- Локально:
  ```bash
  python -m pytest -q tests
  ```

### Структура API
- `POST /api/predict` — анализ текста.
- `POST /healthcheck` — форсированное создание ядра и проверка готовности.
- `GET /status` — агрегированная диагностика загрузчика.
- `GET /version` — версии ядра и монолита.
- `GET /diagnostics` — подробный трейс попыток загрузки.

---

## 🇬🇧 Overview
StudioCore v6.4 MAXI is a stateless lyric-analysis engine wrapped by FastAPI and Gradio. It exposes StudioCoreV6 with clean diagnostics, reload controls, and a public UI. The repository has been cleaned for a production-ready GitHub release.

### Features
- Text analysis: genre, BPM, key, emotions, vocal profile, and structural sections.
- Suno-friendly prompts and annotated lyrics for music generators.
- Diagnostics endpoints: `/status`, `/version`, `/diagnostics`, `/healthcheck`.
- Gradio UI and CLI (`python -m studiocore.app`) for offline validation.
- Stateless execution: every request gets a fresh core instance with guarded loader locks.

### Quickstart
1. Install dependencies:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python app.py
   # or
   uvicorn app:app --host 0.0.0.0 --port 7860
   ```
3. Open the browser: `http://127.0.0.1:7860` for Gradio UI or `http://127.0.0.1:7860/docs` for OpenAPI docs.

### Tests
- Inline button in the “Logs & Tests” tab triggers `pytest -q tests` when pytest is available.
- Locally:
  ```bash
  python -m pytest -q tests
  ```

### API Map
- `POST /api/predict` — analyze text.
- `POST /healthcheck` — force core creation and check readiness.
- `GET /status` — loader diagnostics snapshot.
- `GET /version` — core and monolith versions.
- `GET /diagnostics` — detailed loader trace.

---

## Репозиторий / Repository
- GitHub: [github.com/Sbauermaner/StudioCore](https://github.com/Sbauermaner/StudioCore)
- Issues & контакт: откройте issue или свяжитесь через GitHub (@Sbauermaner).

## Лицензия / License
MIT с дополнительными ограничениями (см. [LICENSE](LICENSE)).
