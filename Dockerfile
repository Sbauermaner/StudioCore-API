# ========== Base ==========
FROM python:3.10-slim

# ========== Working dir ==========
WORKDIR /app

# ========== Dependencies ==========
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========== Copy project ==========
COPY StudioCore_Complete_v4_3.py /app/StudioCore_Complete_v4_3.py
COPY app_fastapi.py /app/app_fastapi.py
COPY studio_config.json /app/studio_config.json

# ========== Run server ==========
EXPOSE 8000
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
