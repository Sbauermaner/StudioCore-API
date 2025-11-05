from fastapi import FastAPI
from pydantic import BaseModel
from StudioCore_Complete_v4 import StudioCore

app = FastAPI()
core = StudioCore()

class Payload(BaseModel):
    lyrics: str
    prefer_gender: str = "auto"

@app.post("/analyze")
def analyze(data: Payload):
    result = core.analyze(data.lyrics, prefer_gender=data.prefer_gender)
    return {
        "genre": result.genre,
        "bpm": result.bpm,
        "tonality": result.tonality,
        "prompt": result.prompt,
        "emotions": result.emotions,
        "tlp": result.tlp,
        "resonance": result.resonance,
        "tonesync": result.tonesync
    }
