FROM python:3.10-slim

ENV PIP_NO_CACHE_DIR=true
ENV PYTHONUNBUFFERED=true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Исправление проблемы с HfFolder в gradio (правильное решение без заглушек)
RUN python3 -c "import os; import gradio; oauth_file = os.path.join(os.path.dirname(gradio.__file__), 'oauth.py'); content = open(oauth_file, 'r', encoding='utf-8').read(); fixed = content.replace('from huggingface_hub import HfFolder, whoami', 'from huggingface_hub import get_token, whoami').replace('HfFolder.path()', 'get_token() or None').replace('HfFolder.get_token()', 'get_token()'); open(oauth_file, 'w', encoding='utf-8').write(fixed) if fixed != content else None"

COPY studiocore/ ./studiocore/
COPY app.py .
COPY auto_sync_openapi.py .
COPY README.md .

EXPOSE 7860

CMD ["python3", "app.py"]
