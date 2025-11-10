# ===============================
# 🎧 StudioCore v5 — Safe Dockerfile
# Optimized for Hugging Face Spaces (≤2GB RAM)
# ===============================

FROM python:3.10-slim

# --- 🧹 Минимизируем систему ---
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    HF_HUB_DISABLE_CACHE=1 \
    TRANSFORMERS_CACHE="/tmp" \
    GRADIO_ANALYTICS_ENABLED="False" \
    GRADIO_TEMP_DIR="/tmp"

# --- 🔧 Установка системных зависимостей ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git curl tini \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- 🧩 Копируем requirements и устанавливаем зависимости ---
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --- 📦 Копируем исходники ---
COPY studiocore/ ./studiocore/
COPY app.py auto_sync_openapi.py update_readme_status.py ./
COPY README.md ./

# --- ⚡ Кеш / временные каталоги ---
RUN mkdir -p /tmp && chmod -R 777 /tmp

# --- 🧠 Старт приложения через tini (устойчивость процессов) ---
ENTRYPOINT ["/usr/bin/tini", "--"]

# --- 🚀 Запуск FastAPI/Gradio ---
CMD ["python", "app.py"]
