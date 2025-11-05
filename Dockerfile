FROM python:3.10-slim

# Создаём пользователя
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# Рабочая директория
WORKDIR /app

# Установка зависимостей
COPY --chown=user ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY --chown=user ./ /app

# Запуск FastAPI через uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
