# =============================
# 🐍 StudioCore v5 — Slim Build
# =============================
FROM python:3.10-slim

# Ускоряем установку
ENV PIP_NO_CACHE_DIR=1

# Устанавливаем системные зависимости (минимально)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем только нужные файлы
COPY studiocore/ ./studiocore/
COPY app.py auto_sync_openapi.py update_readme_status.py ./
COPY README.md ./

EXPOSE 7860
CMD ["python", "app.py"]
