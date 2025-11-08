# ================================
# StudioCore Pilgrim v4.3 — Dockerfile
# ================================

# Базовый образ с Python 3.10 (совместим с Hugging Face docker runtime)
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем исходные файлы проекта
COPY StudioCore_Complete_v4_3.py /app/StudioCore_Complete_v4_3.py
COPY pilgrim_layer.py /app/pilgrim_layer.py
COPY app_fastapi.py /app/app_fastapi.py

# Создаём стандартный файл конфигурации (если не существует)
RUN echo '{ \
  "suno_version": "v5", \
  "safety": { \
    "max_peak_db": -1.0, \
    "max_rms_db": -14.0, \
    "avoid_freq_bands_hz": [18.0, 30.0], \
    "safe_octaves": [2, 3, 4, 5], \
    "max_session_minutes": 20, \
    "fade_in_ms": 1000, \
    "fade_out_ms": 1500 \
  } \
}' > /app/studio_config.json

# Указываем порт (должен совпадать с README.md)
EXPOSE 7860

# Устанавливаем переменные среды
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]