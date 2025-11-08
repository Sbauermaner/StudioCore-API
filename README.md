---
sdk: docker
sdk_version: 0.0.1
app_port: 7860
entrypoint: Dockerfile
---
# 🎧 StudioCore Pilgrim API v4.3

Author: Bauer Synesthetic Studio  
Engine: StudioCore Complete v4.3 — Expressive Adaptive Engine  
Purpose: Analyze lyrics, detect genre and tonality, generate adaptive style prompts for Suno AI.

---

## 🧠 Features
- Truth × Love × Pain emotional spectrum  
- Genre / BPM / tonality analysis  
- Vocal & instrument mapping  
- Harmonic safety module (RNS)  
- Pilgrim Layer meta-interpretation  
- JSON API ready for Suno AI integration

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|:-------:|:----------|:-------------|
| GET | / | Health check |
| POST | /analyze | Analyze lyrics and return Suno-style prompt |

### Example request
`bash
curl -X POST "https://sbauer8-studiocore-api.hf.space/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Cold snow, warm fire, a stark divide...",
    "preferred_vocal": "auto"
  }'