FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=true
ENV PYTHONUNBUFFERED=true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY studiocore/ ./studiocore/
COPY app.py .
COPY auto_sync_openapi.py .
COPY README.md .

EXPOSE 7860

CMD ["python3", "app.py"]
