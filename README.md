---
sdk: docker
---
# 🎧 StudioCore Pilgrim API v4.3

**Author:** Bauer Synesthetic Studio  
**Engine:** StudioCore Complete v4.3 — Expressive Adaptive Engine  
**Purpose:** Analyze lyrics, detect genre, tonality, emotional range, and auto-generate prompt styles for Suno AI.

---

## 🧠 Features
- Adaptive emotion detection (`Truth × Love × Pain`)
- Auto genre, BPM, tonality, vocal & instrument mapping
- Harmonic frequency and safety (RNS)
- Integrated Pilgrim Layer (meta interpretation)
- JSON output for AI music generation

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
| ------- | -------- | ----------- |
| `GET` | `/` | Health check |
| `POST` | `/analyze` | Analyze lyrics text |

### Example request
```bash
curl -X POST "https://sbauer8-studiocore-api.hf.space/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text":"Cold snow, warm fire, a stark divide...", "preferred_gender":"auto"}'