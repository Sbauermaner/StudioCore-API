# -*- coding: utf-8 -*-
"""
auto_sync_openapi.py — безопасная генерация OpenAPI файлов для StudioCore
Теперь без зависимости от шаблонов .template.*
"""

import os, json
from pathlib import Path

# === Версия ядра ===
try:
    from studiocore import STUDIOCORE_VERSION
    VERSION = STUDIOCORE_VERSION
except Exception:
    VERSION = os.environ.get("STUDIOCORE_VERSION", "v5.2")

# === URL Space ===
SPACE_URL = os.environ.get("SPACE_URL", "http://0.0.0.0:7860")

# === Папка проекта ===
root = Path(".")

# === Путь к OpenAPI файлам ===
openapi_main = root / "openapi_main.json"
openapi_gpt = root / "openapi_gpt.yaml"

# === Автоматическая генерация JSON ===
openapi_data = {
    "openapi": "3.0.0",
    "info": {
        "title": "StudioCore Adaptive API",
        "version": VERSION,
        "description": "Adaptive annotation & analysis engine for StudioCore"
    },
    "servers": [{"url": SPACE_URL}],
    "paths": {
        "/status": {
            "get": {
                "summary": "Check server status",
                "responses": {"200": {"description": "OK"}}
            }
        },
        "/api/predict": {
            "post": {
                "summary": "Analyze text",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "properties": {"text": {"type": "string"}}}
                        }
                    }
                },
                "responses": {"200": {"description": "Analysis result"}}
            }
        }
    }
}

try:
    openapi_main.write_text(json.dumps(openapi_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ OpenAPI JSON generated → {openapi_main}")
except Exception as e:
    print(f"⚠️ Error writing {openapi_main}: {e}")

# === Автоматическая генерация YAML (для GPT совместимости) ===
try:
    yaml_lines = [
        "openapi: 3.0.0",
        "info:",
        f"  title: StudioCore Adaptive API",
        f"  version: {VERSION}",
        "servers:",
        f"  - url: {SPACE_URL}",
        "paths:",
        "  /status:",
        "    get:",
        "      summary: Check server status",
        "      responses:",
        "        '200':",
        "          description: OK",
        "  /api/predict:",
        "    post:",
        "      summary: Analyze text",
        "      requestBody:",
        "        required: true",
        "        content:",
        "          application/json:",
        "            schema:",
        "              type: object",
        "              properties:",
        "                text:",
        "                  type: string",
        "      responses:",
        "        '200':",
        "          description: Analysis result",
    ]
    openapi_gpt.write_text("\n".join(yaml_lines), encoding="utf-8")
    print(f"✅ OpenAPI YAML generated → {openapi_gpt}")
except Exception as e:
    print(f"⚠️ Error writing {openapi_gpt}: {e}")

print(f"🎧 StudioCore API descriptors ready (version={VERSION})")
