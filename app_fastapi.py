from __future__ import annotations
import json
from typing import Any, Dict
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pilgrim_layer import PilgrimInterface

app = FastAPI(title="StudioCore Pilgrim API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

pilgrim = PilgrimInterface()

@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "engine": "StudioCore v4 + Pilgrim Layer"}

# 1) Удобно для человека: сырая лирика в теле запроса (text/plain или любая)
@app.post("/analyze")
async def analyze_raw(req: Request):
    body_bytes = await req.body()
    # пробуем как JSON c ключом lyrics, иначе — как сырой текст
    text = ""
    ct = req.headers.get("content-type","").lower()
    if "application/json" in ct:
        try:
            payload = json.loads(body_bytes.decode("utf-8", errors="ignore"))
            text = payload.get("lyrics","")
            prefer = payload.get("prefer_gender","auto")
        except Exception:
            text = body_bytes.decode("utf-8", errors="ignore")
            prefer = "auto"
    else:
        text = body_bytes.decode("utf-8", errors="ignore")
        prefer = "auto"

    text = (text or "").strip()
    if not text:
        return {"error":"Empty input. Paste your lyrics as plain text or JSON {\"lyrics\": \"...\"}."}
    return pilgrim.process_raw(text, prefer_gender=prefer)

# 2) Явный JSON-вариант (строгий)
@app.post("/analyze-json")
async def analyze_json(payload: Dict[str, Any]):
    text = (payload.get("lyrics") or "").strip()
    prefer = (payload.get("prefer_gender") or "auto").strip()
    if not text:
        return {"error":"Field 'lyrics' is required."}
    return pilgrim.process_raw(text, prefer_gender=prefer)