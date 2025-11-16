# -*- coding: utf-8 -*-
"""StudioCore loader helpers.

The goal of this module is to present a predictable import surface for both the
legacy v5 monolith and the evolving v6 compatibility layer.  Historically the
project relied on a side-effect heavy import that printed diagnostics and left
the caller to deal with failures.  The new loader keeps the behaviour but adds
structured diagnostics so downstream tooling (tests, services, CLIs) can inspect
the loader state without parsing stdout.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import os
from typing import Any, Optional, Tuple, Type

from .core_v6 import StudioCoreV6
from .fallback import StudioCoreFallback

# ============================================================
# 🔹 Версия ядра
# ============================================================
STUDIOCORE_VERSION = "v5.2.1"
DEFAULT_MONOLITH = "monolith_v4_3_1"


@dataclass(frozen=True)
class LoaderDiagnostics:
    """Runtime information about the loader state."""

    monolith_module: str
    monolith_version: str
    engine_variant: str
    fallback_used: bool
    errors: Tuple[str, ...] = ()

# ============================================================
# 🔹 Автоматическое определение Monolith
# ============================================================
def _detect_latest_monolith() -> str:
    import glob
    import re

    base = os.path.dirname(__file__)
    candidates = glob.glob(os.path.join(base, "monolith_*.py"))
    if not candidates:
        return DEFAULT_MONOLITH

    def _ver(path: str) -> Tuple[int, int, int]:
        match = re.search(r"(\d+)_(\d+)_(\d+)", path)
        return tuple(map(int, match.groups())) if match else (0, 0, 0)

    latest = sorted(candidates, key=_ver)[-1]
    return os.path.splitext(os.path.basename(latest))[0]


def _load_monolith(name: str) -> Tuple[Optional[Type[Any]], Optional[Type[Any]], str, Optional[str]]:
    """Import the requested monolith module if it exists."""

    try:
        module = importlib.import_module(f".{name}", package=__name__)
    except ImportError as exc:  # pragma: no cover - diagnostics only
        return None, None, "missing", str(exc)

    version = getattr(module, "STUDIOCORE_VERSION", "unknown")
    core_cls = getattr(module, "StudioCore", None)
    v5_cls = getattr(module, "StudioCoreV5", core_cls)
    return core_cls, v5_cls, version, None

# ============================================================
# 🔹 Попытка импорта ядра
# ============================================================
StudioCore: Optional[Type[Any]] = None
StudioCoreV5: Optional[Type[Any]] = None
MONOLITH_VERSION = "unknown"
monolith_name = os.getenv("STUDIOCORE_MONOLITH", _detect_latest_monolith())
preferred_engine = os.getenv("STUDIOCORE_ENGINE", "v6").lower()
_loader_diagnostics = LoaderDiagnostics(monolith_name, MONOLITH_VERSION, "uninitialized", True)


def _initialize_loader() -> None:
    global StudioCore, StudioCoreV5, MONOLITH_VERSION, _loader_diagnostics

    monolith_cls, legacy_cls, monolith_version, error = _load_monolith(monolith_name)
    StudioCoreV5 = legacy_cls or monolith_cls
    MONOLITH_VERSION = monolith_version

    candidate_map = {
        "v6": StudioCoreV6,
        "monolith": monolith_cls,
        "v5": StudioCoreV5,
        "fallback": StudioCoreFallback,
    }

    order: Tuple[str, ...]
    if preferred_engine in {"v6", "latest"}:
        order = ("v6", "monolith", "fallback")
    elif preferred_engine in {"v5", "monolith"}:
        order = ("monolith", "v6", "fallback")
    else:
        order = ("v6", "monolith", "fallback")

    selected = None
    variant = "fallback"
    for key in order:
        candidate = candidate_map.get(key)
        if candidate:
            selected = candidate
            variant = key
            break

    if not selected:
        selected = StudioCoreFallback
        variant = "fallback"

    StudioCore = selected
    fallback_used = selected is StudioCoreFallback
    errors: Tuple[str, ...] = tuple(filter(None, [error]))
    if fallback_used and not errors:
        errors = ("No engine candidates were available; fallback engaged.",)

    _loader_diagnostics = LoaderDiagnostics(
        monolith_module=monolith_name,
        monolith_version=MONOLITH_VERSION,
        engine_variant=variant,
        fallback_used=fallback_used,
        errors=errors,
    )


_initialize_loader()

# ============================================================
# 🔹 Обёртка безопасного вызова
# ============================================================
def _core_candidates(prefer_v6: Optional[bool]) -> Tuple[Type[Any], ...]:
    candidates = []
    if prefer_v6 is None and StudioCore:
        candidates.append(StudioCore)
    else:
        if prefer_v6 and StudioCoreV6:
            candidates.append(StudioCoreV6)
        if StudioCoreV5 and StudioCoreV5 not in candidates:
            candidates.append(StudioCoreV5)
        if StudioCore and StudioCore not in candidates:
            candidates.append(StudioCore)
    if StudioCoreFallback not in candidates:
        candidates.append(StudioCoreFallback)
    return tuple(candidates)


def get_core(*, prefer_v6: Optional[bool] = None, **kwargs: Any) -> Any:
    """Return an engine instance with graceful fallback behaviour."""

    errors = []
    for candidate in _core_candidates(prefer_v6):
        try:
            return candidate(**kwargs)
        except Exception as exc:  # pragma: no cover - defensive path
            errors.append(f"{candidate.__name__}: {exc}")
            continue

    raise RuntimeError(
        "Unable to initialize any StudioCore engine candidates: " + "; ".join(errors)
    )


def loader_diagnostics() -> LoaderDiagnostics:
    """Expose loader metadata for tests and debug tooling."""

    return _loader_diagnostics


__all__ = [
    "StudioCore",
    "StudioCoreV5",
    "StudioCoreV6",
    "StudioCoreFallback",
    "get_core",
    "loader_diagnostics",
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
