# StudioCore Pilgrim Logic API (v4.2)
FROM python:3.10-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы приложения
COPY StudioCore_Complete_v4.py .
COPY pilgrim_layer.py .
COPY app_fastapi.py .

EXPOSE 7860

# Запуск сервера
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
