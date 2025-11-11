# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2 — Unified Adaptive Engine (Auto Monolith Loader)
Truth × Love × Pain = Conscious Frequency

🧩 Особенности:
- Автоматически выбирает последнюю доступную версию монолита (v4_3_5, v5 и т.д.)
- Поддерживает ручное указание версии через переменную окружения STUDIOCORE_VERSION
- Совместим с FastAPI, Gradio и CLI
"""

from __future__ import annotations
import os
import importlib
from typing import Any

# ============================================================
# 🔹 Версия ядра
# ============================================================
STUDIOCORE_VERSION = "v5.2"

# ============================================================
# 🔹 Определение актуальной версии Monolith
# ============================================================
def _detect_latest_monolith() -> str:
    """Автоматически ищет последнюю версию monolith_* в папке studiocore."""
    import glob
    import re
    base = os.path.dirname(__file__)
    candidates = glob.glob(os.path.join(base, "monolith_*.py"))
    if not candidates:
        return "monolith_v4_3_1"
    # сортировка по версии
    def _ver(x: str) -> tuple:
        match = re.search(r"(\d+)_(\d+)_(\d+)", x)
        return tuple(map(int, match.groups())) if match else (0, 0, 0)
    latest = sorted(candidates, key=_ver)[-1]
    return os.path.splitext(os.path.basename(latest))[0]

# Если указано явно через ENV, используем его
monolith_name = os.getenv("STUDIOCORE_MONOLITH", _detect_latest_monolith())

# ============================================================
# 🔹 Импорт ядра
# ============================================================
try:
    core_mod = importlib.import_module(f".{monolith_name}", package=__name__)
    StudioCore = core_mod.StudioCore
    MONOLITH_VERSION = getattr(core_mod, "STUDIOCORE_VERSION", "unknown")
    print(f"🎧 [StudioCore Loader] Loaded {monolith_name} (version={MONOLITH_VERSION})")
except Exception as e:
    StudioCore = None
    MONOLITH_VERSION = "error"
    print(f"❌ [StudioCore Loader] Failed to load {monolith_name}: {e}")

# ============================================================
# 🔹 Обёртка для безопасного вызова
# ============================================================
def get_core() -> Any:
    """Возвращает экземпляр ядра с безопасным фоллбеком."""
    if StudioCore:
        return StudioCore()
    raise ImportError("❌ Основное ядро StudioCore не найдено.")

# ============================================================
# 🔹 Тестовая инициализация при локальном запуске
# ============================================================
if __name__ == "__main__":
    print(f"\n🧠 Инициализация StudioCore {STUDIOCORE_VERSION}...")
    try:
        core = get_core()
        print(f"✅ Ядро загружено успешно ({MONOLITH_VERSION}).")
        active = [s for s in [
            "emotion", "tlp", "rhythm", "freq", "safety",
            "integrity", "vocals", "style", "tone"
        ] if hasattr(core, s)]
        print(f"⚙️ Активные подсистемы: {', '.join(active)}\n")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
