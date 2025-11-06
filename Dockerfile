FROM python:3.10-slim
WORKDIR /app

# 1) зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 2) код
COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY app_fastapi.py /app/app_fastapi.py

# 3) запуск
ENV PORT=7860
CMD ["uvicorn","app_fastapi:app","--host","0.0.0.0","--port","7860"]
