# -*- coding: utf-8 -*-
"""
🧩 StudioCore Converter: openapi.json → openapi_main.yaml
Автоматическая синхронизация между Main и GPT.

Функции:
1. Конвертирует JSON → YAML.
2. Проверяет корректность.
3. Копирует YAML в GPT/openapi_studiocore.yaml.
"""

import json
import yaml
import shutil
from pathlib import Path

# === Пути ===
main_dir = Path(__file__).parent
json_path = main_dir / "openapi.json"
yaml_path = main_dir / "openapi_main.yaml"
gpt_dir = main_dir / "GPT"
gpt_yaml = gpt_dir / "openapi_studiocore.yaml"

# === Проверка наличия JSON ===
if not json_path.exists():
    print("❌ Ошибка: файл openapi.json не найден в Main/.")
    exit(1)

# === Загрузка JSON ===
try:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"❌ Ошибка парсинга JSON: {e}")
    exit(1)

# === Конвертация JSON → YAML ===
try:
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"✅ Конвертация завершена: {yaml_path}")
except Exception as e:
    print(f"❌ Ошибка записи YAML: {e}")
    exit(1)

# === Проверка YAML ===
try:
    with open(yaml_path, "r", encoding="utf-8") as f:
        check = yaml.safe_load(f)
    if not isinstance(check, dict) or "openapi" not in check:
        raise ValueError("Некорректная структура YAML.")
    print("🔍 Проверка YAML: структура корректна.")
except Exception as e:
    print(f"⚠️ Предупреждение: ошибка при проверке YAML: {e}")

# === Копирование в GPT ===
try:
    gpt_dir.mkdir(exist_ok=True)
    shutil.copy2(yaml_path, gpt_yaml)
    print(f"📁 Файл успешно скопирован в {gpt_yaml}")
except Exception as e:
    print(f"❌ Ошибка при копировании в GPT: {e}")
    exit(1)

# === Итог ===
print("\n✅ Операция завершена успешно.")
print("Main → openapi_main.yaml ✅")
print("GPT → openapi_studiocore.yaml ✅")
