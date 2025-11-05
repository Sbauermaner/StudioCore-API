from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, JSONResponse
from StudioCore_Complete_v4 import StudioCore, load_config

app = FastAPI(title="StudioCore Pilgrim API", version="1.0")

# загрузка конфигурации и ядра
cfg = load_config()
core = StudioCore(cfg)


# ------------------------------
# МОДЕЛЬ ЗАПРОСА
# ------------------------------

class LyricsRequest(BaseModel):
    lyrics: str
    gender: str | None = "auto"


# ------------------------------
# ROOT UI — без f-строки
# ------------------------------

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html>
<head>
<title>StudioCore API</title>
<style>
body {
  background: #000;
  color: #21ffcb;
  font-family: monospace;
  padding: 30px;
}
h1 {
  color: #00eaff;
  font-size: 26px;
}
code {
  background: #111;
  padding: 10px;
  display: block;
  border-radius: 6px;
  color: #ffdf6e;
  white-space: pre-wrap;
}
a { color: #00ffaa; }
</style>
</head>

<body>
<h1>StudioCore Pilgrim API</h1>
<p>API активно. Отправь текст POST /analyze чтобы получить музыкальный стиль и Suno prompt.</p>

<p><strong>Пример curl:</strong></p>
<code>
curl -X POST https://sbauer8-studiocore-api.hf.space/analyze \\
 -H "Content-Type: application/json" \\
 -d '{"lyrics":"Пилигрим..."}'
</code>

<p>Документация:</p>
<ul>
<li><a href="/docs">/docs</a></li>
<li><a href="/openapi.json">/openapi.json</a></li>
<li><a href="/health">/health</a></li>
</ul>

</body>
</html>
"""


# ------------------------------
# API ENDPOINT: анализ текста
# ------------------------------

@app.post("/analyze")
async def analyze_text(req: LyricsRequest):
    result = core.analyze(req.lyrics, prefer_gender=req.gender)

    return JSONResponse({
        "genre": result.genre,
        "bpm": result.bpm,
        "tonality": result.tonality,
        "vocals": result.vocals,
        "instruments": result.instruments,
        "tlp": result.tlp,
        "emotions": result.emotions,
        "resonance": result.resonance,
        "integrity": result.integrity,
        "tonesync": result.tonesync,
        "prompt": result.prompt
    })


# ------------------------------
# HEALTH CHECK
# ------------------------------

@app.get("/health")
async def health():
    return {"status": "StudioCore FastAPI running"}
