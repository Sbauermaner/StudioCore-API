# -*- coding: utf-8 -*-
"""StudioCore loader that follows the Codex fallback chain.

Features required by the specification:
* Diagnostic logger for loader decisions
* Env overrides (STUDIOCORE_FORCE_V5 / STUDIOCORE_MONOLITH)
* Primary selection of StudioCoreV6, fallback to V5 monolith, then StudioCoreFallback
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Any, Tuple, Type

from .core_v6 import StudioCoreV6
from .fallback import StudioCoreFallback

STUDIOCORE_VERSION = "v6.3"


def _setup_loader_logging() -> logging.Logger:
    logger = logging.getLogger("studiocore.loader")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[StudioCore Loader] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def _detect_latest_monolith() -> str:
    import glob
    import os as _os
    import re

    base = _os.path.dirname(__file__)
    candidates = glob.glob(_os.path.join(base, "monolith_*.py"))
    if not candidates:
        return "monolith_v4_3_1"

    def _ver(name: str) -> Tuple[int, int, int]:
        match = re.search(r"(\d+)_(\d+)_(\d+)", name)
        return tuple(map(int, match.groups())) if match else (0, 0, 0)

    latest = sorted(candidates, key=_ver)[-1]
    return os.path.splitext(os.path.basename(latest))[0]


def _try_load_v6(logger: logging.Logger) -> Type[Any] | None:
    try:
        logger.info("StudioCoreV6 ready.")
        return StudioCoreV6
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.warning("StudioCoreV6 unavailable: %s", exc)
        return None


def _try_load_v5_monolith(logger: logging.Logger, monolith_name: str | None = None):
    resolved_name = monolith_name or _detect_latest_monolith()
    try:
        module = importlib.import_module(f".{resolved_name}", package=__name__)
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.warning("Monolith import failed (%s): %s", resolved_name, exc)
        return None, None, resolved_name, "unknown"

    core_cls = getattr(module, "StudioCore", None)
    v5_cls = getattr(module, "StudioCoreV5", None) or core_cls
    version = getattr(module, "STUDIOCORE_VERSION", "unknown")
    if core_cls:
        logger.info("Loaded monolith %s (version=%s)", resolved_name, version)
    else:
        logger.warning("Monolith %s loaded but StudioCore class missing", resolved_name)
    return core_cls, v5_cls, resolved_name, version


def _select_core_class(
    logger: logging.Logger,
    *,
    force_v5: bool = False,
    monolith_name: str | None = None,
):
    v6_cls = None if force_v5 else _try_load_v6(logger)
    monolith_core, monolith_v5, resolved_name, version = _try_load_v5_monolith(logger, monolith_name)

    if v6_cls:
        logger.info("StudioCoreV6 selected as primary core")
        return v6_cls, monolith_v5, "core_v6", STUDIOCORE_VERSION

    if monolith_core:
        logger.info("StudioCore monolith selected (%s)", resolved_name)
        return monolith_core, monolith_v5 or monolith_core, resolved_name, version

    logger.error("Falling back to StudioCoreFallback")
    return StudioCoreFallback, StudioCoreFallback, "fallback", "fallback"


_LOGGER = _setup_loader_logging()
_FORCE_V5 = os.getenv("STUDIOCORE_FORCE_V5", "").strip().lower() in {"1", "true", "yes"}
_MONOLITH_OVERRIDE = os.getenv("STUDIOCORE_MONOLITH")

StudioCore, StudioCoreV5, MONOLITH_NAME, MONOLITH_VERSION = _select_core_class(
    _LOGGER,
    force_v5=_FORCE_V5,
    monolith_name=_MONOLITH_OVERRIDE,
)


def get_core() -> Any:
    """Return an instantiated core following the fallback chain."""

    try:
        return StudioCore()
    except Exception as exc:  # pragma: no cover - defensive guard
        _LOGGER.error("Core init failed (%s). Falling back to StudioCoreFallback.", exc)
        return StudioCoreFallback()


__all__ = [
    "StudioCore",
    "StudioCoreV5",
    "StudioCoreV6",
    "StudioCoreFallback",
    "get_core",
    "STUDIOCORE_VERSION",
    "MONOLITH_VERSION",
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
