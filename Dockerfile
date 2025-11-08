# Python slim
FROM python:3.10-slim

# системные минимальные
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# рабочая директория
WORKDIR /app

# зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# исходники
COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY pilgrim_layer.py /app/pilgrim_layer.py
COPY app_fastapi.py /app/app_fastapi.py

# порт
EXPOSE 7860

# запуск
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]

