# 🎧 StudioCore Pilgrim API

AI-композитор и аналитическое ядро на базе **StudioCore**, адаптированное для Hugging Face Spaces.  
Производит полный анализ лирики: эмоции, жанр, BPM, тональность, инструменты, философию текста и генерирует готовый **Style Prompt**.

---

### 🚀 Как использовать

#### Вариант 1 — Через Web UI
Открой:
👉 https://sbauer8-studiocore-api.hf.space/ui  
Вставь свою лирику и нажми **Analyze** или **Build**.

---

#### Вариант 2 — Через API (cURL)

```bash
# Анализ лирики (JSON)
curl -X POST \
  'https://sbauer8-studiocore-api.hf.space/analyze?prefer_gender=auto' \
  -H 'Content-Type: text/plain' \
  --data-binary $'Cold snow, warm fire, a stark divide...'
