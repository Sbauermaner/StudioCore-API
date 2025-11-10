# -*- coding: utf-8 -*-
"""
🧠 StudioCore OpenAPI Auto-Sync Utility
Синхронизирует openapi.json → openapi_studiocore.yaml
и проверяет валидность перед пушем в GPT Actions.
"""

import json
import yaml
import os
from datetime import datetime
from openapi_spec_validator import validate_spec

JSON_FILE = "openapi.json"
YAML_FILE = "openapi_studiocore.yaml"

def sync_openapi():
    if not os.path.exists(JSON_FILE):
        print(f"❌ Не найден {JSON_FILE}")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Преобразование структуры в YAML
    yaml_data = yaml.dump(data, allow_unicode=True, sort_keys=False, width=120)

    with open(YAML_FILE, "w", encoding="utf-8") as f:
        f.write(yaml_data)

    # Проверяем корректность
    try:
        validate_spec(data)
        print("✅ OpenAPI схема валидна.")
    except Exception as e:
        print("⚠️ Ошибка валидации:", e)

    print(f"🪄 {YAML_FILE} обновлён {datetime.utcnow().isoformat()}")

if __name__ == "__main__":
    sync_openapi()
