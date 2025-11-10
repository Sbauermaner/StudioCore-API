FROM python:3.10-slim

# 🧹 Убираем кэш, снижаем слой установки
ENV PIP_NO_CACHE_DIR=true
ENV PYTHONUNBUFFERED=true

# 🛠 Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ⚙️ Копируем исходники
COPY studiocore/ ./studiocore/
COPY app.py auto_sync_openapi.py update_readme_status.py README.md ./

# 🌍 Порт
EXPOSE 7860

# 🚀 Старт приложения
CMD ["python", "app.py"]
