# ================================
# 🎧 StudioCore v5 — Slim Build
# ================================
FROM python:3.10-slim

# 💡 Ускоряем установку и уменьшаем размер
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# --- Устанавливаем минимальные системные зависимости ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git && \
    rm -rf /var/lib/apt/lists/*

# --- Копируем и устанавливаем зависимости Python ---
COPY requirements.txt /workspace/requirements.txt
WORKDIR /workspace
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# --- Копируем только нужные файлы ядра ---
COPY studiocore/ ./studiocore/
COPY app.py auto_sync_openapi.py update_readme_status.py ./
COPY README.md ./

# --- Порт и команда запуска ---
EXPOSE 7860
CMD ["python", "app.py"]