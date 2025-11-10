# auto_sync_openapi.py
import os, json, re
from pathlib import Path

# 1) пытаемся взять версию из Python-модуля
VERSION = None
try:
    from studiocore import STUDIOCORE_VERSION
    VERSION = STUDIOCORE_VERSION
except Exception:
    pass
if not VERSION:
    VERSION = os.environ.get("STUDIOCORE_VERSION", "v5.0")

# 2) определяем URL Space
SPACE_URL = os.environ.get("SPACE_URL", "http://0.0.0.0:7860")

def render(src: Path, dst: Path, mapping: dict):
    txt = src.read_text(encoding="utf-8")
    for k, v in mapping.items():
        txt = txt.replace("{{" + k + "}}", v)
    dst.write_text(txt, encoding="utf-8")
    print(f"✔️  Rendered {dst.name} (version={mapping['VERSION']}, url={mapping['SPACE_URL']})")

root = Path(".")
mapping = {"VERSION": VERSION, "SPACE_URL": SPACE_URL}

# JSON для Space
render(root / "openapi_main.template.json", root / "openapi_main.json", mapping)

# YAML для GPT
render(root / "openapi_gpt.template.yaml", root / "openapi_gpt.yaml", mapping)
