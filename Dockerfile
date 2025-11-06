FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ядро и надстройки
COPY StudioCore_Complete_v4.py /app/StudioCore_Complete_v4.py
COPY pilgrim_layer.py /app/pilgrim_layer.py
COPY app_fastapi.py /app/app_fastapi.py

EXPOSE 7860
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"
