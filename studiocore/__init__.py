# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2 — Unified Adaptive Engine
Truth × Love × Pain = Conscious Frequency

Инициализация ядра:
- Подключает актуальный монолит (monolith_v4_3_1.py — обновлённый)
- Устанавливает STUDIOCORE_VERSION
- Проверяет наличие OpenAPI шаблонов
- Обеспечивает совместимость с FastAPI, Gradio и CLI
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any

# === Версия ядра ===
STUDIOCORE_VERSION = "v5.2"

# === Импорт ядра (актуальный monolith_v4_3_1.py) ===
try:
    from .monolith_v4_3_1 import StudioCore, STUDIOCORE_VERSION as MONOLITH_VERSION
except ImportError:
    StudioCore = None
    MONOLITH_VERSION = "unknown"
    print("⚠️ Не удалось импортировать StudioCore из monolith_v4_3_1.py")

# === Обёртка для безопасного вызова ===
def get_core() -> StudioCore:
    """Возвращает экземпляр ядра с безопасным фоллбеком."""
    if StudioCore is not None:
        return StudioCore()
    else:
        raise ImportError("❌ Основное ядро StudioCore не найдено.")


# === Проверка наличия OpenAPI шаблона ===
def _check_openapi_template() -> bool:
    path = os.path.join(os.getcwd(), "openapi_main.template.json")
    if not os.path.exists(path):
        print("⚠️ openapi_main.template.json отсутствует — OpenAPI sync пропущен.")
        return False
    return True


# === Автозапуск при локальном запуске ===
if __name__ == "__main__":
    print(f"\n🧠 Инициализация StudioCore {STUDIOCORE_VERSION}...")
    _check_openapi_template()

    try:
        core = get_core()
        print(f"✅ Ядро загружено успешно.")
        print(f"🧩 Активная версия монолита: {MONOLITH_VERSION}")
        subsystems = [
            "emotion", "tlp", "rhythm", "freq", "safety",
            "integrity", "vocals", "style", "tone"
        ]
        active = [s for s in subsystems if hasattr(core, s)]
        print(f"⚙️ Активные подсистемы: {', '.join(active)}\n")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
