# ===============================
# StudioCore Pilgrim API v4.3
# ===============================

FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта в контейнер
COPY . /app

# Создаём конфиг StudioCore (если его нет)
RUN echo '{ \
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
}' > /app/studio_config.json

# Указываем порт
EXPOSE 7860

# Запуск FastAPI приложения
CMD ["python", "app_fastapi.py"]