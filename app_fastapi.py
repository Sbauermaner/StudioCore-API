from fastapi import FastAPI, Body, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn

from StudioCore_v4_1_Pilgrim import StudioCore, load_config

app = FastAPI(title="StudioCore Pilgrim API", version="4.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

core = StudioCore(load_config())

class AnalyzeRequest(BaseModel):
    lyrics: str = Field(..., description="Raw lyrics text. Newlines allowed.")
    prefer_gender: Optional[str] = Field("auto", description="'male'|'female'|'auto'")
    author_style: Optional[str] = Field(None, description="Optional author overrides for style words")

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "engine": "StudioCore v4.1 Pilgrim"}

@app.post("/analyze", response_model=None)
async def analyze(req: Request, payload: Optional[AnalyzeRequest] = Body(default=None)) -> Dict[str, Any]:
    """
    Accepts:
      1) JSON: { "lyrics": "...", "prefer_gender": "male", "author_style": "Tagelharpa + throat singing" }
      2) text/plain body with raw lyrics
    """
    content_type = req.headers.get("content-type", "").lower()
    if payload is None:
        # try text/plain
        if "text/plain" in content_type:
            raw = await req.body()
            lyrics = raw.decode("utf-8", errors="ignore")
            result = core.analyze(lyrics, prefer_gender="auto", author_style=None)
        else:
            # No body or wrong type
            return {"detail": "Pass JSON with 'lyrics' or text/plain body"}
    else:
        result = core.analyze(payload.lyrics, prefer_gender=(payload.prefer_gender or "auto"),
                              author_style=payload.author_style)

    out = {
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
        "sections": result.sections,
        "prompt": result.prompt
    }
    return out

if __name__ == "__main__":
    # HF Spaces Docker expects port 7860 by default
    uvicorn.run("app_fastapi:app", host="0.0.0.0", port=7860, reload=False)