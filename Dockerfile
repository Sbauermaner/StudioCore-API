FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (минимум)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY studiocore_pilgrim.py /app/studiocore_pilgrim.py
COPY app_fastapi.py /app/app_fastapi.py

EXPOSE 7860
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
