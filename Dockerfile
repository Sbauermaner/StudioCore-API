# ============================
# 🎧 StudioCore Pilgrim Dockerfile
# ============================

FROM python:3.10-slim

# Оптимизация: установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Рабочая директория
WORKDIR /app

# Копируем основные файлы студии
COPY app_fastapi.py /app/app_fastapi.py
COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY pilgrim_layer.py /app/pilgrim_layer.py

# Автоматически создаём studio_config.json, если он отсутствует
RUN echo '{
  "suno_version": "v5",
  "safety": {
    "max_peak_db": -1.0,
    "max_rms_db": -14.0,
    "avoid_freq_bands_hz": [18.0, 30.0],
    "safe_octaves": [2, 3, 4, 5],
    "max_session_minutes": 20,
    "fade_in_ms": 1000,
    "fade_out_ms": 1500
  }
}' > /app/studio_config.json

# Задаём порт по умолчанию (FastAPI)
EXPOSE 7860

# Точка запуска
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]