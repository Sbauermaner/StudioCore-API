# -*- coding: utf-8 -*-
"""
StudioCore IMMORTAL v7 — REST API (FastAPI)
Автор: Сергей Бауэр (@Sbauermaner)

REST API для интеграции StudioCore с внешними системами (например, Suno API).
"""

from __future__ import annotations

import os
import logging
import time
from collections import defaultdict
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from studiocore.core_v6 import StudioCoreV6
from studiocore.config import DEFAULT_CONFIG

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI
# Task 6.2: Import version from config instead of hardcoding
app = FastAPI(
    title="StudioCore API",
    description="REST API for StudioCore IMMORTAL v7 - Music Analysis Engine",
    version=DEFAULT_CONFIG.API_VERSION,
)

# CORS middleware для поддержки cross-origin запросов
# Task 3.2: Security fix - use environment variable instead of wildcard
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = (
    [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    if cors_origins_env
    else ["*"]  # Fallback to wildcard only if env var is not set
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация ядра
core = StudioCoreV6()

# Task 4.1: Rate Limiting - Simple in-memory rate limiter (60 req/min per IP)
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60  # seconds


def _cleanup_old_requests(ip: str, current_time: float) -> None:
    """Remove requests older than the rate limit window."""
    _rate_limit_store[ip] = [
        req_time
        for req_time in _rate_limit_store[ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]


def _check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit. Returns True if allowed, False if rate limited."""
    current_time = time.time()
    _cleanup_old_requests(ip, current_time)
    
    if len(_rate_limit_store[ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    _rate_limit_store[ip].append(current_time)
    return True


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Task 4.1: Rate limiting middleware - 60 requests per minute per IP."""
    # Skip rate limiting for health check endpoints
    if request.url.path in ["/", "/health"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not _check_rate_limit(client_ip):
        logger.warning("Rate limit exceeded for IP: %s", client_ip)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds allowed",
            },
        )
    
    return await call_next(request)

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
