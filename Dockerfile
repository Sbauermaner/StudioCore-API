# Use Python base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all sources
COPY StudioCore_Complete_v4_3.py /app/StudioCore_Complete_v4_3.py
COPY app_fastapi.py /app/app_fastapi.py
COPY pilgrim_layer.py /app/pilgrim_layer.py

# Auto-create default config
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

# Expose FastAPI port
EXPOSE 7860

# Start app
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "7860"]
