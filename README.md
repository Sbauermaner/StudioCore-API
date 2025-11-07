---
title: StudioCore Pilgrim API
emoji: 🎛️
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# StudioCore Pilgrim (API)

**Назначение:** вставляешь *чистую лирику* → ядро автоматически:
- нормализует и строит скелет `[Verse/Chorus/Bridge]`
- определяет эмоции + T×L×P
- подбирает жанр, тональность, BPM, вокал (male/female/duet/choir + тембровые подсказки)
- рассчитывает резонансную зону и режим (healing / rage→truth / pain→light / ritual / sacred_silence / neutral)
- собирает **Style Prompt** для Suno v3–v5 (с авто-сжатием под лимит версии)

## Эндпоинты

### 1) Health
`GET /` → `{ "status": "StudioCore Pilgrim running" }`

### 2) Анализ (вход: текст ИЛИ JSON)
- `POST /analyze`  
  - **Text**: `Content-Type: text/plain` — сырая лирика в теле  
  - **JSON**: `{"lyrics":"...", "prefer_gender":"auto|male|female|duet|choir", "author_style":"..."}`  
  - **Ответ**: JSON (жанр, bpm, tlp, emotions, prompt, skeleton, mode)

### 3) Готовый текст (скелет + prompt)
- `POST /build`  
  - **Text**: `Content-Type: text/plain` — сырая лирика в теле  
  - **Ответ**: `text/plain` (готовый текст + Style Prompt)

### 4) Быстрая форма
- `GET /ui` — простая HTML-форма для ручной проверки.

## Примеры

**curl (чистый текст → JSON):**
```bash
curl -X POST 'https://sbauer8-studiocore-api.hf.space/analyze?prefer_gender=auto' \
  -H 'Content-Type: text/plain' \
  --data-binary $'Cold snow, warm fire...'
