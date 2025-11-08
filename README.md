---
title: StudioCore Pilgrim API
emoji: 🎧
colorFrom: purple
colorTo: pink
sdk: docker
app_file: app_fastapi.py
pinned: false
license: mit
---

# 🎵 StudioCore Pilgrim API

AI-композитор и философское ядро **StudioCore Pilgrim** —  
проект, соединяющий музыку, эмоции и осознанность через алгоритмы Truth × Love × Pain.  
Развёрнуто в Hugging Face Spaces (Docker SDK).

---

## 🚀 Как использовать

### 🖥 Через Web UI
Перейди по ссылке:
👉 [https://sbauer8-studiocore-api.hf.space/ui](https://sbauer8-studiocore-api.hf.space/ui)

Вставь свою лирику — система автоматически:
- расставит пунктуацию и структуру (`[Verse]`, `[Chorus]`, `[Bridge]`)
- подберёт вокал, тембр, BPM, тональность
- создаст готовый **Style Prompt** для SunoAI или других генераторов

---

### 💡 Через API (cURL)

```bash
# Анализ лирики (JSON)
curl -X POST "https://sbauer8-studiocore-api.hf.space/analyze?prefer_gender=auto" \
     -H "Content-Type: text/plain" \
     --data-binary "Cold snow, warm fire, a stark divide..."
