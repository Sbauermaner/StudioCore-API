# --- StudioCore Pilgrim Logic API ---
FROM python:3.10-slim

# Устанавливаем зависимости
RUN pip install --no-cache-dir fastapi==0.115.4 uvicorn==0.32.0 pydantic==2.9.2 typing-extensions numpy

# Рабочая директория
WORKDIR /app

# Копируем файлы
COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY app_fastapi.py /app/app_fastapi.py

# Устанавливаем стандартный порт
EXPOSE 7860

# Точка запуска
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
