# ==== Base image ====
FROM python:3.10-slim

# ==== Workdir ====
WORKDIR /workspace

# ==== Copy project ====
COPY . /workspace

# ==== Dependencies ====
RUN pip install --no-cache-dir -r requirements.txt

# ==== Expose Gradio default port ====
EXPOSE 7860

# ==== Run the app (absolute path) ====
CMD ["python", "/workspace/app.py"]

