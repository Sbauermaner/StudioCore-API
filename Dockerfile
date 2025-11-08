# ---- Base Python image ----
FROM python:3.10-slim

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Copy files ----
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY pilgrim_layer.py /app/pilgrim_layer.py
COPY app_fastapi.py /app/app_fastapi.py
COPY studio_config.json /app/studio_config.json

# ---- Start API ----
EXPOSE 7860
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
