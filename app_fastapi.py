from __future__ import annotations
from typing import Optional, Dict, Any
import textwrap

from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from StudioCore_Complete_v4 import load_config  # ядро не трогаем
from pilgrim_layer import PilgrimInterface       # новый слой

app = FastAPI(title="StudioCore Pilgrim API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

_cfg = load_config()         # загружаем твой конфиг
_pilgrim = PilgrimInterface()  # инициализируем слой поверх ядра

# --- Модели для /analyze (но тело может быть и «сырым» текстом)
class AnalyzePayload(BaseModel):
    lyrics: str
    prefer_gender: Optional[str] = "auto"
    author_style: Optional[str] = None
    autoskeleton: Optional[bool] = True

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(textwrap.dedent("""
    <html>
    <head>
      <meta charset="utf-8"/>
      <title>StudioCore Pilgrim API</title>
      <style>
        body{background:#0a0f14;color:#b7f7c6;font-family:ui-monospace,Menlo,Consolas,monospace;padding:32px}
        pre{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;padding:16px;border-radius:8px;overflow:auto}
        a{color:#7ee787;text-decoration:none}
      </style>
    </head>
    <body>
      <h1>StudioCore Pilgrim API</h1>
      <p>API активно. Отправь текст на <code>POST /analyze</code> (можно <b>просто сырой текст</b>) — получишь стиль и Suno prompt.</p>
      <h3>curl (RAW TEXT):</h3>
      <pre>curl -X POST https://sbauer8-studiocore-api.hf.space/analyze \\
  -H "Content-Type: text/plain; charset=utf-8" \\
  --data-binary $'Пилигрим, одинокий как век...'</pre>

      <h3>curl (JSON):</h3>
      <pre>curl -X POST https://sbauer8-studiocore-api.hf.space/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"lyrics":"Пилигрим...","prefer_gender":"male","autoskeleton":true}'</pre>

      <h3>Документация:</h3>
      <ul>
        <li><a href="/docs">/docs</a></li>
        <li><a href="/openapi.json">/openapi.json</a></li>
        <li><a href="/health">/health</a></li>
      </ul>
    </body>
    </html>
    """))

@app.get("/health")
def health():
    return {"status": "StudioCore Pilgrim running"}

@app.post("/analyze")
async def analyze(request: Request):
    """
    Принимает ИЛИ:
    1) application/json: { "lyrics": "...", ... }
    2) text/plain: сырая лирика (без JSON, без скобок)
    """
    ctype = request.headers.get("content-type", "")
    try:
        if "application/json" in ctype:
            data = await request.json()
            if not isinstance(data, dict):
                return JSONResponse({"detail": "Invalid JSON object"}, status_code=400)
            return _pilgrim.analyze_structured(data)

        # Иначе читаем как сырой текст
        body = await request.body()
        lyrics_raw = body.decode("utf-8", errors="replace")
        return _pilgrim.analyze_plain(lyrics_raw=lyrics_raw, prefer_gender="auto", author_style=None, autoskeleton=True)

    except Exception as e:
        return JSONResponse({"detail": f"Error: {e.__class__.__name__}: {e}"}, status_code=500)