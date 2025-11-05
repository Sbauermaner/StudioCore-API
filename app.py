from fastapi import FastAPI
from pydantic import BaseModel
from StudioCore_Complete_v4 import StudioCore

app = FastAPI()
core = StudioCore()

class LyricsInput(BaseModel):
    lyrics: str
    prefer_gender: str = "auto"

@app.post("/analyze")
def analyze(data: LyricsInput):
    result = core.analyze(data.lyrics, prefer_gender=data.prefer_gender)
    return {
        "prompt": result.prompt,
        "genre": result.genre,
        "bpm": result.bpm,
        "tonality": result.tonality,
        "tlp": result.tlp,
        "emotions": result.emotions,
        "resonance": result.resonance
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
