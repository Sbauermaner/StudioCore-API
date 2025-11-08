from fastapi import FastAPI, Request
from StudioCore_Complete_v4_3 import analyze_and_style

app = FastAPI()

@app.post("/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    # Принимаем также query-параметры
    query = dict(request.query_params)
    text = data.get("text") or query.get("text")
    preferred_gender = data.get("preferred_gender") or query.get("preferred_gender", "auto")

    if not text:
        return {"error": "Missing required field: text"}

    result = analyze_and_style(text, preferred_vocal=preferred_gender)
    return {
        "engine": "StudioCore v4.3",
        "genre": result.genre,
        "bpm": result.bpm,
        "tonality": result.tonality,
        "style": result.prompt
    }