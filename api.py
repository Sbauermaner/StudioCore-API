# -*- coding: utf-8 -*-
"""
StudioCore IMMORTAL v7 — REST API (FastAPI)
Автор: Сергей Бауэр (@Sbauermaner)

REST API для интеграции StudioCore с внешними системами (например, Suno API).
"""

from __future__ import annotations

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from studiocore.core_v6 import StudioCoreV6

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI
app = FastAPI(
    title="StudioCore API",
    description="REST API for StudioCore IMMORTAL v7 - Music Analysis Engine",
    version="1.0.0",
)

# CORS middleware для поддержки cross-origin запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация ядра
core = StudioCoreV6()

# API Key authentication (опционально)
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []


def verify_api_key(api_key: Optional[str] = Depends(API_KEY_HEADER)) -> Optional[str]:
    """
    Проверка API ключа (опционально, если API_KEYS не установлен - пропускает).

    Args:
        api_key: API ключ из заголовка

    Returns:
        API ключ если валиден

    Raises:
        HTTPException: Если ключ невалиден и API_KEYS установлен
    """
    if not API_KEYS or not any(API_KEYS):
        # Если API_KEYS не установлен, пропускаем проверку
        return None

    if not api_key or api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key


# Pydantic модели для запросов и ответов
class AnalyzeRequest(BaseModel):
    """Запрос на анализ текста."""

    text: str = Field(
        ..., description="Текст для анализа", min_length=1, max_length=16000
    )
    preferred_gender: Optional[str] = Field(
        "auto", description="Предпочтительный пол вокала"
    )
    bpm: Optional[int] = Field(None, description="BPM override", ge=40, le=200)
    key: Optional[str] = Field(None, description="Музыкальный ключ override")
    genre: Optional[str] = Field(None, description="Жанр override")
    mood: Optional[str] = Field(None, description="Настроение override")

    @field_validator("preferred_gender")
    @classmethod
    def validate_gender(cls, v):
        if v not in ["auto", "male", "female", "neutral", "mixed"]:
            raise ValueError(
                "preferred_gender must be one of: auto, male, female, neutral, mixed"
            )
        return v


class AnalyzeResponse(BaseModel):
    """Ответ с результатами анализа."""

    ok: bool
    result: dict
    error: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Корневой endpoint."""
    return {"name": "StudioCore API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "StudioCore API"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest, api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Анализ текста с возвратом полного результата.

    Args:
        request: Запрос с текстом и параметрами
        api_key: API ключ (опционально)

    Returns:
        Результат анализа

    Raises:
        HTTPException: При ошибках анализа
    """
    try:
        # Подготовка параметров
        kwargs = {}
        if request.preferred_gender and request.preferred_gender != "auto":
            kwargs["preferred_gender"] = request.preferred_gender
        if request.bpm:
            kwargs["bpm"] = request.bpm
        if request.key:
            kwargs["key"] = request.key
        if request.genre:
            kwargs["genre"] = request.genre
        if request.mood:
            kwargs["mood"] = request.mood

        # Выполнение анализа
        result = core.analyze(text=request.text, **kwargs)

        # Проверка результата
        if not result.get("ok", True):
            error_msg = result.get("error", "Unknown error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
            )

        return AnalyzeResponse(ok=True, result=result)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/analyze/lyrics-prompt")
async def get_lyrics_prompt(
    request: AnalyzeRequest, api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Получить только lyrics_prompt для Suno.

    Args:
        request: Запрос с текстом и параметрами
        api_key: API ключ (опционально)

    Returns:
        Lyrics prompt строка
    """
    try:
        kwargs = {}
        if request.preferred_gender and request.preferred_gender != "auto":
            kwargs["preferred_gender"] = request.preferred_gender

        result = core.analyze(text=request.text, **kwargs)

        if not result.get("ok", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Analysis failed"),
            )

        lyrics_prompt = (
            result.get("fanf", {}).get("lyrics_prompt")
            or result.get("lyrics_prompt")
            or ""
        )

        return {"lyrics_prompt": lyrics_prompt}

    except Exception as e:
        logger.exception(f"Error getting lyrics prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/analyze/style-prompt")
async def get_style_prompt(
    request: AnalyzeRequest, api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Получить только style_prompt для Suno.

    Args:
        request: Запрос с текстом и параметрами
        api_key: API ключ (опционально)

    Returns:
        Style prompt строка
    """
    try:
        kwargs = {}
        if request.preferred_gender and request.preferred_gender != "auto":
            kwargs["preferred_gender"] = request.preferred_gender

        result = core.analyze(text=request.text, **kwargs)

        if not result.get("ok", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Analysis failed"),
            )

        style_prompt = (
            result.get("fanf", {}).get("style_prompt")
            or result.get("style_prompt")
            or ""
        )

        return {"style_prompt": style_prompt}

    except Exception as e:
        logger.exception(f"Error getting style prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")

    uvicorn.run(app, host=host, port=port)
