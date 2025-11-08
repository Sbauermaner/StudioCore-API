from fastapi import FastAPI, Query
from pydantic import BaseModel
from StudioCore_Complete_v4_3 import StudioCore

app = FastAPI(title="StudioCore Pilgrim API", version="4.3")

core = StudioCore()

class LyricInput(BaseModel):
    text: str
    author_style: str | None = None
    preferred_gender: str | None = "auto"

@app.post("/analyze")
def analyze_text(payload: LyricInput):
    result = core.analyze(
        text=payload.text,
        author_style=payload.author_style,
        preferred_gender=payload.preferred_gender
    )
    return result.__dict__

@app.get("/")
def root():
    return {"status": "ok", "engine": "StudioCore Complete v4.3", "author": "Bauer Synesthetic Studio"}