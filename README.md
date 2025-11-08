---
sdk: docker
---
# 🎧 StudioCore API v4.3
Truth × Love × Pain = Conscious Frequency  
Built by Bauer Synesthetic Studio

### 🧠 Description
StudioCore — это движок анализа и синтеза эмоциональных, частотных и смысловых слоёв текста.  
Он выстраивает профиль Truth × Love × Pain, определяет BPM, жанр, вокал и инструментальный состав.

### 🚀 API Endpoints
**GET /** — проверка состояния  
**POST /analyze** — анализ текста  
Пример:
```bash
curl -X POST [https://<space-url>/analyze](https://SBauer8-StudioCore-API.hf.space/analyze) \
-H "Content-Type: application/json" \
-d '{"text":"Я сварю себе зелье из грёз"}'