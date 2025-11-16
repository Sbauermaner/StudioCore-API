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
from typing import Any, Dict, List

from .fallback import StudioCoreFallback
from .core_v6 import StudioCoreV6

# ============================================================
# 🔹 Версия ядра
# ============================================================
STUDIOCORE_VERSION = "v5.2.1"

DEFAULT_LOADER_ORDER = (
    "v6",
    "monolith",
    "fallback",
)

LOADER_STATUS: Dict[str, Any] = {
    "active": None,
    "errors": [],
    "attempted": [],
    "version": None,
    "requested_order": list(DEFAULT_LOADER_ORDER),
}

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
StudioCoreV5 = None
MONOLITH_VERSION = "unknown"

try:
    core_mod = importlib.import_module(f".{monolith_name}", package=__name__)
    StudioCore = getattr(core_mod, "StudioCore", None)
    StudioCoreV5 = getattr(core_mod, "StudioCoreV5", None)
    MONOLITH_VERSION = getattr(
        core_mod,
        "MONOLITH_VERSION",
        getattr(core_mod, "STUDIOCORE_VERSION", MONOLITH_VERSION),
    )
    print(f"🎧 [StudioCore Loader] Loaded {monolith_name} (version={MONOLITH_VERSION})")
except ImportError as e:
    print(f"⚠️ [StudioCore Loader] ImportError: {e}")
except Exception as e:
    print(f"❌ [StudioCore Loader] Failed to load {monolith_name}: {e}")

_MONOLITH_LOADER = StudioCore

# ============================================================
# 🔹 Fallback: если Monolith не загрузился
# ============================================================
if not StudioCore:
    print("⚠️ [StudioCore Loader] Основное ядро не найдено — создаётся fallback-заглушка.")
    StudioCore = StudioCoreFallback

# ============================================================
# 🔹 Обёртка безопасного вызова
# ============================================================
LOADER_GRAPH: Dict[str, Dict[str, Any]] = {
    "v6": {
        "name": "StudioCoreV6",
        "loader": StudioCoreV6,
        "available": StudioCoreV6 is not None,
        "version": getattr(StudioCoreV6, "STUDIOCORE_VERSION", "v6"),
        "priority": 100,
    },
    "monolith": {
        "name": "StudioCore",
        "loader": _MONOLITH_LOADER,
        "available": _MONOLITH_LOADER is not None,
        "version": MONOLITH_VERSION,
        "priority": 50,
    },
    "fallback": {
        "name": "StudioCoreFallback",
        "loader": StudioCoreFallback,
        "available": True,
        "version": "fallback",
        "priority": 0,
    },
}


def _normalize_loader_key(key: str) -> str:
    return key.strip().lower()


def _requested_loader_order(prefer_v6: bool = True) -> List[str]:
    env_order = os.getenv("STUDIOCORE_LOADER_ORDER")
    order: List[str]
    if env_order:
        order = [_normalize_loader_key(part) for part in env_order.split(",") if part.strip()]
    else:
        order = list(DEFAULT_LOADER_ORDER)
    if prefer_v6 and "v6" not in order:
        order.insert(0, "v6")
    if not prefer_v6 and "v6" in order:
        order = [item for item in order if item != "v6"] + ["v6"]
    deduped: List[str] = []
    for key in order:
        if key not in deduped:
            deduped.append(key)
    for fallback_key in DEFAULT_LOADER_ORDER:
        if fallback_key not in deduped:
            deduped.append(fallback_key)
    LOADER_STATUS["requested_order"] = deduped
    return deduped


def get_core(*, prefer_v6: bool = True) -> Any:
    """Возвращает экземпляр ядра с безопасным fallback."""

    attempts: List[str] = []
    errors: List[str] = []
    for loader_key in _requested_loader_order(prefer_v6=prefer_v6):
        meta = LOADER_GRAPH.get(loader_key)
        if not meta:
            continue
        loader_cls = meta.get("loader")
        if not loader_cls:
            continue
        attempts.append(loader_key)
        try:
            instance = loader_cls()
            LOADER_STATUS.update({
                "active": loader_key,
                "errors": errors,
                "attempted": attempts,
                "version": meta.get("version"),
            })
            return instance
        except Exception as e:  # pragma: no cover - defensive logging
            error_message = f"{meta['name']} failed: {e}"
            print(f"⚠️ [StudioCore Loader] {error_message}")
            errors.append(error_message)

    LOADER_STATUS.update({"active": None, "errors": errors, "attempted": attempts})
    raise RuntimeError("Нет доступных загрузчиков StudioCore")


__all__ = [
    "StudioCore",
    "StudioCoreV5",
    "StudioCoreV6",
    "StudioCoreFallback",
    "get_core",
    "STUDIOCORE_VERSION",
    "MONOLITH_VERSION",
    "DEFAULT_LOADER_ORDER",
    "LOADER_GRAPH",
    "LOADER_STATUS",
]

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
