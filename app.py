from fastapi import FastAPI
from pydantic import BaseModel
from StudioCore_Complete_v4 import StudioCore

app = FastAPI()
core = StudioCore()

class Request(BaseModel):
    lyrics: str
    prefer_gender: str = "auto"

@app.post("/analyze")
def analyze(req: Request):
    r = core.analyze(req.lyrics, prefer_gender=req.prefer_gender)
    return {
        "genre": r.genre,
        "bpm": r.bpm,
        "tonality": r.tonality,
        "prompt": r.prompt,
        "emotions": r.emotions,
        "tlp": r.tlp,
        "resonance": r.resonance,
        "tonesync": r.tonesync
    }
