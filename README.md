# 🎧 StudioCore API v4.3

> **Truth × Love × Pain = Conscious Frequency**  
> Built by **Bauer Synesthetic Studio**

---

## 🧠 Description

**StudioCore v4.3** — движок анализа и синтеза эмоциональных, частотных и смысловых слоёв текста.  
Он автоматически строит профиль **Truth × Love × Pain**, определяет BPM, жанр, вокал и инструментальный состав, создаёт промт для Suno AI (`v3 – v5`).

---

## ⚙️ Deployment Environment (Hugging Face Spaces)

| Параметр | Значение |
|-----------|-----------|
| **SDK** | `docker` |
| **App Port** | `8000` |
| **Entrypoint** | `uvicorn app_fastapi:app --host 0.0.0.0 --port 8000` |
| **Base Image** | `python:3.10-slim` |
| **Healthcheck** | `curl -f http://localhost:8000/ || exit 1` |
| **Status Endpoint** | `/` |
| **Main Endpoint** | `/analyze` |
| **Docs** | `/docs` |

---

## 🧩 Installation (Local)

```bash
git clone https://huggingface.co/spaces/SBauer8/StudioCore-API
cd StudioCore-API
pip install -r requirements.txt
uvicorn app_fastapi:app --reload --port 8000
