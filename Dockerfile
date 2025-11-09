# ==== Base image ====
FROM python:3.10-slim

# ==== Workdir ====
WORKDIR /app

# ==== Copy project ====
COPY . .

# ==== Install dependencies ====
RUN pip install --no-cache-dir -r requirements.txt

# ==== Expose Gradio default port ====
EXPOSE 7860

# ==== Run the app ====
CMD ["python", "app.py"]
