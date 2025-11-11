# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2 — Unified Adaptive Engine
Truth × Love × Pain = Conscious Frequency

Инициализация ядра:
- Подключает основное ядро (monolith_v4_3_1.py → v4.3.2)
- Устанавливает STUDIOCORE_VERSION
- Обеспечивает совместимость с FastAPI, Gradio и CLI
"""

from __future__ import annotations
import json
from typing import Dict, Any

# === Версия ядра ===
STUDIOCORE_VERSION = "v5.2"

# === Импорт основного ядра ===
try:
    from .monolith_v4_3_1 import StudioCore  # 🔹 актуальное ядро
except Exception as e:
    print(f"⚠️ Import warning: {e}")
    StudioCore = None


# === Обёртка для безопасного вызова (совместимость с app.py) ===
def get_core() -> StudioCore:
    """Возвращает экземпляр ядра с безопасным фоллбеком."""
    if StudioCore is not None:
        return StudioCore()
    else:
        raise ImportError("❌ Не удалось загрузить основное ядро StudioCore (monolith_v4_3_1.py).")


# === Совместимый интерфейс ===
if __name__ == "__main__":
    try:
        core = get_core()
        print(f"✅ StudioCore {STUDIOCORE_VERSION} успешно инициализировано.")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
