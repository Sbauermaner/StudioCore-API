# -*- coding: utf-8 -*-
"""StudioCore loader stack.

The loader follows the Codex specification for StudioCore v6 by exposing a
predictable fallback chain:

1. :class:`StudioCoreV6` — the modern compatibility surface.
2. :class:`StudioCoreV5` — the legacy monolith (auto-detected).
3. :class:`StudioCoreFallback` — last resort safe mode.

The helpers below keep the import side-effects isolated and provide structured
loader diagnostics that can be asserted inside the unit tests.
"""
from __future__ import annotations

from dataclasses import dataclass
import importlib
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type

from .core_v6 import StudioCoreV6
from .fallback import StudioCoreFallback

# ============================================================
# 🔹 Версия ядра / публичный идентификатор
# ============================================================
STUDIOCORE_VERSION = "v6.3-dev"

# ============================================================
# 🔹 Поиск и загрузка monolith_v* файлов
# ============================================================

def _detect_latest_monolith() -> str:
    import glob
    import re

    base = os.path.dirname(__file__)
    candidates = glob.glob(os.path.join(base, "monolith_*.py"))
    if not candidates:
        return "monolith_v4_3_1"

    def _ver(path: str) -> Tuple[int, int, int]:
        match = re.search(r"(\d+)_(\d+)_(\d+)", path)
        return tuple(map(int, match.groups())) if match else (0, 0, 0)

    latest = sorted(candidates, key=_ver)[-1]
    return os.path.splitext(os.path.basename(latest))[0]


MONOLITH_MODULE = os.getenv("STUDIOCORE_MONOLITH", _detect_latest_monolith())
MONOLITH_VERSION = "unloaded"
_MONOLITH_ERRORS: List[str] = []
StudioCoreV5: Optional[Type[Any]] = None


def _import_monolith() -> None:
    """Best-effort import of the V5 monolith."""
    global StudioCoreV5, MONOLITH_VERSION

    try:
        core_mod = importlib.import_module(f".{MONOLITH_MODULE}", package=__name__)
    except Exception as exc:  # pragma: no cover - logged through diagnostics
        _MONOLITH_ERRORS.append(f"Import failed: {exc}")
        StudioCoreV5 = None
        MONOLITH_VERSION = "missing"
        return

    candidate = getattr(core_mod, "StudioCoreV5", None) or getattr(core_mod, "StudioCore", None)
    if candidate is None:
        _MONOLITH_ERRORS.append("Module does not expose StudioCoreV5")
    else:
        StudioCoreV5 = candidate
    MONOLITH_VERSION = getattr(core_mod, "STUDIOCORE_VERSION", "unknown")


_import_monolith()


# ============================================================
# 🔹 Реестр доступных ядер
# ============================================================

@dataclass
class _CoreCandidate:
    key: str
    cls: Type[Any]
    version: str
    source: str
    priority: int


class _StudioCoreLoader:
    """Stateful helper that knows how to instantiate the best available core."""

    def __init__(self) -> None:
        self._candidates: Dict[str, _CoreCandidate] = {}
        self._errors: Dict[str, str] = {}
        self._selected: Optional[str] = None
        self._bootstrap()

    def _bootstrap(self) -> None:
        self._candidates.clear()
        self._errors.clear()
        self._selected = None
        self.register("v6", StudioCoreV6, STUDIOCORE_VERSION, "core_v6", priority=0)
        if StudioCoreV5 is not None:
            self.register("v5", StudioCoreV5, MONOLITH_VERSION, MONOLITH_MODULE, priority=10)
        self.register("fallback", StudioCoreFallback, "fallback", "fallback", priority=100)

    def reset(self) -> None:
        """Rebuild the registry (mainly used in tests)."""
        self._bootstrap()

    # --------------------------------------------------------
    # Registry helpers
    # --------------------------------------------------------
    def register(self, key: str, cls: Type[Any], version: str, source: str, *, priority: int) -> None:
        if key in self._candidates:
            raise ValueError(f"Core '{key}' is already registered")
        self._candidates[key] = _CoreCandidate(key, cls, version, source, priority)

    @property
    def ordered_candidates(self) -> List[_CoreCandidate]:
        return sorted(self._candidates.values(), key=lambda item: item.priority)

    # --------------------------------------------------------
    # Core resolution
    # --------------------------------------------------------
    def get(self, preferred_stack: Iterable[str] | None = None) -> Any:
        """Return the best available core respecting an optional order."""
        order = list(preferred_stack or [])
        seen = set(order)
        for candidate in self.ordered_candidates:
            if candidate.key not in seen:
                order.append(candidate.key)
        for key in order:
            candidate = self._candidates.get(key)
            if not candidate:
                continue
            try:
                instance = candidate.cls()
            except Exception as exc:  # pragma: no cover - exercised indirectly via fallback
                self._errors[key] = repr(exc)
                continue
            self._selected = key
            return instance
        self._selected = "fallback"
        return StudioCoreFallback()

    # --------------------------------------------------------
    # Diagnostics
    # --------------------------------------------------------
    def diagnostics(self) -> Dict[str, Any]:
        available = [
            {
                "key": c.key,
                "class": c.cls.__name__,
                "version": c.version,
                "source": c.source,
                "priority": c.priority,
            }
            for c in self.ordered_candidates
        ]
        return {
            "monolith": {
                "module": MONOLITH_MODULE,
                "version": MONOLITH_VERSION,
                "loaded": StudioCoreV5 is not None,
                "errors": list(_MONOLITH_ERRORS),
            },
            "available": available,
            "selected": self._selected,
            "errors": dict(self._errors),
        }


_LOADER = _StudioCoreLoader()

# StudioCore alias for backwards compatibility — instantiating the class is
# equivalent to directly constructing StudioCoreV6.
StudioCore = StudioCoreV6


# ============================================================
# 🔹 Публичные хелперы
# ============================================================

def get_core(
    preferred_stack: Iterable[str] | None = None,
    *,
    force_reload: bool = False,
) -> Any:
    """Return an initialized StudioCore instance.

    Parameters
    ----------
    preferred_stack:
        Optional tuple/list specifying the desired order (e.g. ("v6", "v5")).
    force_reload:
        When True the loader registry is rebuilt before instantiation.
    """

    if force_reload:
        _LOADER.reset()
    return _LOADER.get(preferred_stack)


def loader_diagnostics() -> Dict[str, Any]:
    """Expose the loader state for tests and observability."""

    return _LOADER.diagnostics()


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
# 🔹 CLI диагностика
# ============================================================
if __name__ == "__main__":  # pragma: no cover - manual diagnostics
    print(f"\n🧠 StudioCore {STUDIOCORE_VERSION} — loader diagnostics\n")
    diag = loader_diagnostics()
    for candidate in diag["available"]:
        prefix = "✅" if candidate["key"] != "fallback" else "ℹ️"
        print(
            f"{prefix} {candidate['key']} | class={candidate['class']} | "
            f"version={candidate['version']} | source={candidate['source']}"
        )
    if diag["errors"]:
        print("\n⚠️ Ошибки инициализации:")
        for key, message in diag["errors"].items():
            print(f" - {key}: {message}")
    if diag["monolith"]["errors"]:
        print("\n⚠️ Monolith import warnings:")
        for message in diag["monolith"]["errors"]:
            print(f" - {message}")
    print("\nГотово.\n")
