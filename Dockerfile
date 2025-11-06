FROM python:3.10-slim

WORKDIR /app

# только нужные системные пакеты (минимум)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# ВАЖНО: имена не меняем
COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY pilgrim_layer.py           /app/pilgrim_layer.py
COPY app_fastapi.py             /app/app_fastapi.py

EXPOSE 7860
ENV PORT=7860

CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
