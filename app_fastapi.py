from fastapi import FastAPI
from pydantic import BaseModel
from StudioCore_Complete_v4 import StudioCore, load_config

app = FastAPI(title="StudioCore API")

core = StudioCore(load_config())

class LyricsRequest(BaseModel):
    lyrics: str
    gender: str = "auto"

@app.post("/analyze")
def analyze_lyrics(req: LyricsRequest):
    result = core.analyze(req.lyrics, req.gender)

    return {
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
        "prompt": result.prompt,
    }

@app.get("/")
def root():
    return {"status": "StudioCore FastAPI running"}