from __future__ import annotations
import json
from typing import Optional
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pilgrim_layer import PilgrimInterface

app = FastAPI(
    title="StudioCore Pilgrim API",
    description="Вставьте лирику (JSON или text/plain) — получите стиль, BPM, тональность и Suno style prompt.",
    version="1.0.0"
)

# CORS (на всякий)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

pilgrim = PilgrimInterface(default_mode="auto")

# ----- Models -----
class AnalyzeRequest(BaseModel):
    lyrics: str = Field(..., description="Лирика (можно с тегами [Verse]/[Chorus])")
    prefer_gender: str = Field("auto", description="auto|male|female|duet|choir")
    author_style: Optional[str] = Field(None, description="Подсказка стиля (опционально)")
    force_voice: Optional[str] = Field(None, description="Напр., 'raspy', 'angelic' и т.п.")
    genre_hint: Optional[str] = Field(None, description="Принудительно задать жанр")
    ret: str = Field("json", description="'json' или 'text' — в каком виде вернуть ответ")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html><body style="font-family: ui-monospace, Menlo, monospace; background: #0b0e14; color:#cde0ff; padding:24px;">
    <h1>StudioCore Pilgrim API</h1>
    <p>API активно. Отправьте текст POST <code>/analyze</code> чтобы получить стиль и Suno prompt.</p>
    <pre style="background:#111522; padding:12px; border-radius:8px;">
curl -X POST https://YOUR-SPACE-HERE/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"lyrics":"Пилигрим..."}'
    </pre>
    <p>Документация: <a href="/docs">/docs</a> • <a href="/openapi.json">/openapi.json</a> • <a href="/health">/health</a></p>
    </body></html>
    """

@app.get("/health")
async def health():
    return JSONResponse({"status": "StudioCore FastAPI running"})

# Основной endpoint (любит и JSON, и text/plain)
@app.post("/analyze")
async def analyze(request: Request, payload: Optional[AnalyzeRequest] = Body(None)):
    ctype = request.headers.get("content-type", "").split(";")[0].strip().lower()
    # 1) application/json (через pydantic)
    if ctype == "application/json":
        if payload is None or not payload.lyrics:
            return JSONResponse(status_code=400, content={"detail": "lyrics is required"})
        result = pilgrim.analyze_lyrics(
            lyrics=payload.lyrics,
            prefer_gender=payload.prefer_gender,
            author_style=payload.author_style,
            force_voice=payload.force_voice,
            genre_hint=payload.genre_hint,
            return_format=payload.ret
        )
        if payload.ret == "text":
            return PlainTextResponse(result["text"])
        return JSONResponse(result)

    # 2) text/plain — сырая лирика; параметры читаем из query (?return=text&prefer_gender=male)
    if ctype == "text/plain":
        raw = await request.body()
        lyrics = raw.decode("utf-8", errors="ignore").strip()
        ret = request.query_params.get("return", "json")
        prefer_gender = request.query_params.get("prefer_gender", "auto")
        author_style = request.query_params.get("author_style")
        force_voice = request.query_params.get("voice")
        genre_hint = request.query_params.get("genre_hint")
        if not lyrics:
            return JSONResponse(status_code=400, content={"detail": "plain text body is empty"})
        result = pilgrim.analyze_lyrics(
            lyrics=lyrics,
            prefer_gender=prefer_gender,
            author_style=author_style,
            force_voice=force_voice,
            genre_hint=genre_hint,
            return_format=ret
        )
        if ret == "text":
            return PlainTextResponse(result["text"])
        return JSONResponse(result)

    # fallback: пробуем прочитать тело как текст, чтобы не пугать пользователя
    raw = (await request.body()).decode("utf-8", errors="ignore").strip()
    if raw:
        result = pilgrim.analyze_lyrics(lyrics=raw, return_format="text")
        return PlainTextResponse(result["text"])

    return JSONResponse(status_code=415, content={"detail": f"Unsupported Content-Type: {ctype}. Use application/json or text/plain."})