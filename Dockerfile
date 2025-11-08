# ===============================
# StudioCore Pilgrim API v4.3 — FastAPI
# ===============================
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Проверка файлов
RUN ls -l /app && echo "✅ Files copied successfully"

# Создаём конфиг при отсутствии
RUN if [ ! -f /app/studio_config.json ]; then \
  echo '{ \
    "suno_version": "v5", \
    "safety": { \
      "max_peak_db": -1.0, \
      "max_rms_db": -14.0, \
      "avoid_freq_bands_hz": [18.0, 30.0], \
      "safe_octaves": [2, 3, 4, 5], \
      "max_session_minutes": 20, \
      "fade_in_ms": 1000, \
      "fade_out_ms": 1500 \
    } \
  }' > /app/studio_config.json; \
  fi

# Hugging Face Spaces слушает только 7860
EXPOSE 7860

# ===============================
# ВАЖНО: указываем запуск FastAPI через Uvicorn
# ===============================
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]