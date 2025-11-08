# StudioCore_API_v4.3 — контейнер для FastAPI
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники
COPY StudioCore_Complete_v4_3.py /app/StudioCore_Complete_v4_3.py
COPY app_fastapi.py /app/app_fastapi.py
COPY studio_config.json /app/studio_config.json

EXPOSE 8080

# Запуск
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8080"]
