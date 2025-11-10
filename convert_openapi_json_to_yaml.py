# -*- coding: utf-8 -*-
"""
🧩 Конвертер OpenAPI JSON → YAML
Преобразует openapi.json в openapi_main.yaml для StudioCore.
"""

import json
import yaml
from pathlib import Path

# Пути
json_path = Path("openapi.json")
yaml_path = Path("openapi_main.yaml")

if not json_path.exists():
    print("❌ Файл openapi.json не найден в текущей директории.")
else:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Сохраняем как YAML
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print(f"✅ Конвертация завершена: {yaml_path}")
