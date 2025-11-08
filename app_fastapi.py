from fastapi import FastAPI, Request
from pydantic import BaseModel
from StudioCore_Complete_v4_3 import analyze_and_style  # ✅ Исправленный импорт

app = FastAPI(title="StudioCore Pilgrim API v4.3", version="4.3")

class InputPayload(BaseModel):
    text: str
    preferred_vocal: str | None = "auto"
    author_style_hint: str | None = None

@app.get("/")
def root():
    return {"status": "ok", "engine": "StudioCore v4.3", "author": "Bauer Synesthetic Studio"}

@app.post("/analyze")
async def analyze(payload: InputPayload):
    result = analyze_and_style(
        raw_text=payload.text,
        preferred_vocal=payload.preferred_vocal,
        author_style_hint=payload.author_style_hint
    )
    return {
        "genre": result.genre,
        "bpm": result.bpm,
        "tonality": result.tonality,
        "vocals": result.vocals,
        "instruments": result.instruments,
        "techniques": result.techniques,
        "prompt": result.prompt,
        "tlp": result.tlp,
        "emotions": result.emotions,
        "resonance": result.resonance,
        "tonesync": result.tonesync,
        "integrity": result.integrity,
        "safety_notes": result.safety_notes,
    }