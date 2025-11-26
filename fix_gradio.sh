#!/bin/bash
# Скрипт для исправления проблемы с HfFolder в gradio
# Применяется в Docker контейнере после установки зависимостей

set -e

GRADIO_OAUTH_FILE=$(python3 -c "import gradio; import os; print(os.path.join(os.path.dirname(gradio.__file__), 'oauth.py'))" 2>/dev/null || echo "")

if [ -z "$GRADIO_OAUTH_FILE" ] || [ ! -f "$GRADIO_OAUTH_FILE" ]; then
    echo "⚠ gradio/oauth.py не найден, пропускаем патч"
    exit 0
fi

echo "Исправление gradio/oauth.py..."

# Создаем backup
if [ ! -f "${GRADIO_OAUTH_FILE}.backup" ]; then
    cp "$GRADIO_OAUTH_FILE" "${GRADIO_OAUTH_FILE}.backup"
    echo "✓ Backup создан"
fi

# Применяем патч
python3 << 'PYTHON_PATCH'
import sys
import os

oauth_file = os.environ.get('GRADIO_OAUTH_FILE')
if not oauth_file or not os.path.exists(oauth_file):
    sys.exit(0)

with open(oauth_file, 'r', encoding='utf-8') as f:
    content = f.read()

if 'from huggingface_hub import HfFolder, whoami' in content:
    fixed = content.replace(
        'from huggingface_hub import HfFolder, whoami',
        'from huggingface_hub import get_token, whoami'
    )
    fixed = fixed.replace('HfFolder.path()', 'get_token() or None')
    fixed = fixed.replace('HfFolder.get_token()', 'get_token()')
    
    if fixed != content:
        with open(oauth_file, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print("✓ gradio/oauth.py исправлен")
    else:
        print("⚠ Изменения не требуются")
else:
    print("✓ HfFolder не найден (возможно, уже исправлено)")
PYTHON_PATCH

echo "✓ Патч применен"
PYTHON_PATCH

