# ========= BASE =========
FROM python:3.10-slim

# ========= WORKDIR =========
WORKDIR /app

# ========= DEPENDENCIES =========
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

# ========= COPY FILES =========
COPY StudioCore_Complete_v4_3.py app_fastapi.py studio_config.json ./

# ========= EXPOSE =========
EXPOSE 8000

# ========= HEALTHCHECK =========
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# ========= RUN =========
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
