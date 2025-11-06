FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY StudioCore_v4_1_Pilgrim.py /app/StudioCore_v4_1_Pilgrim.py
COPY app_fastapi.py /app/app_fastapi.py
EXPOSE 7860
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
