# -*- coding: utf-8 -*-
"""
📘 Auto-Update README for StudioCore v6.x
-----------------------------------------
Обновляет README.md при запуске Space:
— Обновляет статус API (online/offline)
— Фиксирует дату последней синхронизации
— Вставляет актуальные ссылки на OpenAPI схемы (YAML + JSON)
— Автоматически корректирует заголовок версии (v5.x → v6.x и т.д.)
"""

import requests
from datetime import datetime
from pathlib import Path
import re

# === CONFIG ===
README_PATH = Path("README.md")
API_STATUS_URL = "https://sbauer8-studiocore-api.hf.space/status"
SERVER_URL = "https://sbauer8-studiocore-api.hf.space"
OPENAPI_YAML = f"{SERVER_URL}/openapi_gpt.yaml"
OPENAPI_JSON = f"{SERVER_URL}/openapi_main.json"

# === MAIN FUNCTIONS ===
def get_api_info():
    """Проверяет состояние API и возвращает данные."""
    try:
        r = requests.get(API_STATUS_URL, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return {
                "status": "🟢 **API online**" if data.get("ready") else "🟡 **API partial**",
                "version": data.get("version", "v6.0.0"),
            }
    except Exception:
        pass
    return {"status": "🔴 **API offline**", "version": "—"}


def update_readme():
    """Обновляет README.md с актуальной информацией."""
    if not README_PATH.exists():
        print("❌ README.md не найден, пропускаю обновление.")
        return

    try:
        lines = README_PATH.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"❌ Ошибка чтения README.md: {e}")
        return

    info = get_api_info()
    status_line = f"> {info['status']} | Last sync: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Version: `{info['version']}`"

    # --- 1️⃣ Удаляем старые строки статуса
    lines = [ln for ln in lines if not ln.strip().startswith("> 🟢") and not ln.strip().startswith("> 🔴") and not ln.strip().startswith("> 🟡")]

    # --- 2️⃣ Обновляем заголовок версии (title: ... в YAML-фронтматтере)
    lines = [
        re.sub(r"(title:\s+StudioCore\s+v[\d\.]+)", f"title: StudioCore {info['version']}", ln)
        if ln.strip().startswith("title: StudioCore") else ln
        for ln in lines
    ]

    # --- 3️⃣ Вставляем строку статуса после заголовка README
    for i, line in enumerate(lines):
        if line.strip().startswith("# 🎧 StudioCoreAPI"):
            lines.insert(i + 1, status_line)
            break

    # --- 4️⃣ Удаляем старые ссылки OpenAPI
    lines = [
        ln for ln in lines
        if not ln.strip().startswith("📡 **Server:**")
        and not ln.strip().startswith("🧩 **Schema (YAML):**")
        and not ln.strip().startswith("🧩 **Schema (JSON):**")
        and not ln.strip().startswith("🕓 **Auto-updated:**")
    ]

    # --- 5️⃣ Добавляем обновлённые ссылки в конец файла
    lines += [
        "",
        "---",
        f"📡 **Server:** [StudioCore API – Hugging Face Space]({SERVER_URL})",
        f"🧩 **Schema (YAML):** [{OPENAPI_YAML}]({OPENAPI_YAML})",
        f"🧩 **Schema (JSON):** [{OPENAPI_JSON}]({OPENAPI_JSON})",
        f"🕓 **Auto-updated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "---",
    ]

    try:
        README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"✅ README.md обновлён: {info['status']} ({info['version']})")
    except Exception as e:
        print(f"❌ Ошибка записи README.md: {e}")


if __name__ == "__main__":
    update_readme()
