from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Optional
from StudioCore_Complete_v4 import StudioCore

app = FastAPI(title="StudioCore Pilgrim API",
              description="Вставь свою лирику — получи Скелет и Style Prompt. Поддерживает сырой ввод без JSON.",
              version="4.2")

core = StudioCore()

# ------------------------------
# Модель для JSON-запросов
# ------------------------------
class LyricsRequest(BaseModel):
    lyrics: str
    prefer_gender: Optional[str] = "auto"
    author_style: Optional[str] = None

# ------------------------------
# Маршруты
# ------------------------------
@app.get("/")
def root():
    return PlainTextResponse("StudioCore Pilgrim API — ядро активно. Отправь POST /analyze с лирикой.")

@app.get("/health")
def health():
    return {"status": "ok", "version": "4.2", "core": "StudioCore_Complete_v4.py"}

@app.post("/analyze")
async def analyze(request: Request):
    """
    Принимает либо:
    - application/json: {"lyrics": "...", "prefer_gender": "..."}
    - text/plain: просто лирику без JSON
    Возвращает: text/plain (сформированный скелет и style prompt)
    """
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in content_type:
            data = await request.json()
            lyrics = data.get("lyrics", "")
            gender = data.get("prefer_gender", "auto")
            author_style = data.get("author_style")
        else:
            lyrics = (await request.body()).decode("utf-8")
            gender = "auto"
            author_style = None
    except Exception as e:
        return JSONResponse({"error": f"Ошибка парсинга данных: {e}"}, status_code=400)

    if not lyrics.strip():
        return JSONResponse({"error": "Пустой текст. Введите лирику."}, status_code=400)

    result = core.analyze(lyrics, prefer_gender=gender, author_style=author_style)

    # Формируем финальный текст для вывода
    text_output = (
        f"{result.skeleton_text}\n\n"
        f"Style Prompt:\n{result.prompt}\n\n"
        f"Vocal Profile: {result.vocal_profile}"
    )

    # Определяем формат ответа по Accept
    accept_header = request.headers.get("accept", "").lower()
    if "application/json" in accept_header:
        return JSONResponse({
            "genre": result.genre,
            "bpm": result.bpm,
            "tonality": result.tonality,
            "vocals": result.vocals,
            "instruments": result.instruments,
            "prompt": result.prompt,
            "vocal_profile": result.vocal_profile,
            "skeleton_text": result.skeleton_text,
        })
    else:
        return PlainTextResponse(text_output)

# ------------------------------
# Swagger описание
# ------------------------------
@app.get("/docs_info")
def docs_info():
    return {
        "usage": "POST /analyze",
        "input_formats": ["application/json", "text/plain"],
        "output_formats": ["application/json", "text/plain"],
        "example_json": {"lyrics": "your text...", "prefer_gender": "auto"},
        "example_plain": "Cold snow, warm fire, a stark divide...",
    }