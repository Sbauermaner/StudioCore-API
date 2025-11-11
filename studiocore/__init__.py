# -*- coding: utf-8 -*-
"""
🎧 StudioCore v5.2.1 — Unified Adaptive Engine (Safe Loader)
Truth × Love × Pain = Conscious Frequency

🧩 Особенности:
- Автоматический поиск последнего monolith_*.py
- Устойчивый импорт: fallback при отсутствии StyleMatrix
- Безопасный вызов get_core() даже при ошибках импорта
"""

from __future__ import annotations
import os
import importlib
from typing import Any

# ============================================================
# 🔹 Версия ядра
# ============================================================
STUDIOCORE_VERSION = "v5.2.1"

# ============================================================
# 🔹 Автоматическое определение Monolith
# ============================================================
def _detect_latest_monolith() -> str:
    import glob, re
    base = os.path.dirname(__file__)
    candidates = glob.glob(os.path.join(base, "monolith_*.py"))
    if not candidates:
        return "monolith_v4_3_1"
    def _ver(x: str) -> tuple:
        match = re.search(r"(\d+)_(\d+)_(\d+)", x)
        return tuple(map(int, match.groups())) if match else (0, 0, 0)
    latest = sorted(candidates, key=_ver)[-1]
    return os.path.splitext(os.path.basename(latest))[0]

monolith_name = os.getenv("STUDIOCORE_MONOLITH", _detect_latest_monolith())

# ============================================================
# 🔹 Попытка импорта ядра
# ============================================================
StudioCore = None
MONOLITH_VERSION = "unknown"

try:
    core_mod = importlib.import_module(f".{monolith_name}", package=__name__)
    StudioCore = getattr(core_mod, "StudioCore", None)
    MONOLITH_VERSION = getattr(core_mod, "STUDIOCORE_VERSION", "unknown")
    print(f"🎧 [StudioCore Loader] Loaded {monolith_name} (version={MONOLITH_VERSION})")
except ImportError as e:
    print(f"⚠️ [StudioCore Loader] ImportError: {e}")
except Exception as e:
    print(f"❌ [StudioCore Loader] Failed to load {monolith_name}: {e}")

# ============================================================
# 🔹 Fallback: если Monolith не загрузился
# ============================================================
if not StudioCore:
    print("⚠️ [StudioCore Loader] Основное ядро не найдено — создаётся fallback-заглушка.")

    class StudioCoreFallback:
        """Fallback ядро: позволяет системе работать, пока StudioCore не готов."""
        def __init__(self, *args, **kwargs):
            print("🧩 [StudioCoreFallback] Активен временный режим.")
            self.is_fallback = True
            self.status = "safe-mode"
            self.subsystems = []
        def analyze(self, *_, **__):
            raise RuntimeError("⚠️ StudioCoreFallback: анализ недоступен — основное ядро не загружено.")

    StudioCore = StudioCoreFallback
    MONOLITH_VERSION = "fallback"

# ============================================================
# 🔹 Обёртка безопасного вызова
# ============================================================
def get_core() -> Any:
    """Возвращает экземпляр ядра с безопасным fallback."""
    try:
        return StudioCore()
    except Exception as e:
        print(f"⚠️ [StudioCore] Ошибка инициализации: {e}")
        return StudioCoreFallback()

# ============================================================
# 🔹 Тестовый запуск
# ============================================================
if __name__ == "__main__":
    print(f"\n🧠 Инициализация StudioCore {STUDIOCORE_VERSION}...")
    try:
        core = get_core()
        if getattr(core, "is_fallback", False):
            print(f"⚠️ Используется fallback ядро ({MONOLITH_VERSION})")
        else:
            print(f"✅ Ядро загружено успешно ({MONOLITH_VERSION})")
            subsystems = [s for s in [
                "emotion","tlp","rhythm","freq","safety",
                "integrity","vocals","style","tone"
            ] if hasattr(core, s)]
            print(f"⚙️ Активные подсистемы: {', '.join(subsystems)}\n")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
