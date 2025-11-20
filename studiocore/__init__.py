# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e

"""StudioCore loader with MAXI fallback orchestration."""

from __future__ import annotations

import importlib
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple, Type

FINGERPRINT = "StudioCore-FP-2025-SB-9fd72e27"

from .core_v6 import StudioCoreV6
from .fallback import StudioCoreFallback

# Version fingerprint linked to FINGERPRINT: StudioCore-FP-2025-SB-9fd72e27
STUDIOCORE_VERSION = "v6.4.0-protected"
DEFAULT_MONOLITH = "monolith_v4_3_1"
DEFAULT_LOADER_ORDER = ("v6", "v5", "monolith", "fallback")


@dataclass(frozen=True)
class LoaderDiagnostics:
    """Structured runtime information about loader behaviour."""

    monolith_module: str | None
    monolith_version: str
    engine_variant: str
    fallback_used: bool
    engine_order: Tuple[str, ...]
    errors: Tuple[str, ...]
    attempted: Tuple[str, ...]
    active: str | None


LOADER_STATUS: Dict[str, Any] = {
    "active": None,
    "attempted": [],
    "errors": [],
    "version": None,
    "requested_order": list(DEFAULT_LOADER_ORDER),
}


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
        return DEFAULT_MONOLITH

    def _ver(name: str) -> Tuple[int, int, int]:
        match = re.search(r"(\d+)_(\d+)_(\d+)", name)
        return tuple(map(int, match.groups())) if match else (0, 0, 0)

    latest = sorted(candidates, key=_ver)[-1]
    return os.path.splitext(os.path.basename(latest))[0]


def _import_monolith(name: str) -> Tuple[Type[Any] | None, Type[Any] | None, str, str, str | None]:
    try:
        module = importlib.import_module(f".{name}", package=__name__)
    except ImportError as exc:  # pragma: no cover - diagnostics only
        return None, None, name, "missing", str(exc)
    except Exception as exc:  # pragma: no cover - diagnostics only
        message = f"Failed to import monolith '{name}': {type(exc).__name__}: {exc}"
        return None, None, name, "error", message

    version = getattr(module, "STUDIOCORE_VERSION", "unknown")
    return (
        getattr(module, "StudioCore", None),
        getattr(module, "StudioCoreV5", None),
        name,
        version,
        None,
    )


def _requested_loader_order(prefer_v6: bool | None = None) -> Tuple[str, ...]:
    env_order = os.getenv("STUDIOCORE_LOADER_ORDER", "")
    tokens: List[str] = []
    if env_order:
        for token in env_order.split(","):
            token = token.strip().lower()
            if token:
                tokens.append(token)
    mapping = {
        "v6": ("v6", "v5", "monolith", "fallback"),
        "latest": ("v6", "v5", "monolith", "fallback"),
        "v5": ("v5", "monolith", "v6", "fallback"),
        "monolith": ("monolith", "v5", "v6", "fallback"),
        "fallback": ("fallback", "monolith", "v5", "v6"),
    }
    preference = os.getenv("STUDIOCORE_ENGINE", "latest").strip().lower()
    base_order: Iterable[str] = mapping.get(preference, DEFAULT_LOADER_ORDER)
    if prefer_v6 is True:
        base_order = mapping["v6"]
    elif prefer_v6 is False:
        base_order = mapping["v5"]

    deduped: List[str] = []
    for key in (*tokens, *base_order, *DEFAULT_LOADER_ORDER):
        normalized = key.strip().lower()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


_LOGGER = _setup_loader_logging()
_FORCE_V5 = os.getenv("STUDIOCORE_FORCE_V5", "").strip().lower() in {"1", "true", "yes"}
_MONOLITH_OVERRIDE = os.getenv("STUDIOCORE_MONOLITH")

_MONOLITH_CLS, _MONOLITH_V5, MONOLITH_NAME, MONOLITH_VERSION, _LOAD_ERROR = _import_monolith(
    _MONOLITH_OVERRIDE or _detect_latest_monolith()
)
if _LOAD_ERROR:
    _LOGGER.warning("Monolith import issue (%s): %s", MONOLITH_NAME, _LOAD_ERROR)
elif _MONOLITH_CLS:
    _LOGGER.info("Loaded monolith %s (version=%s)", MONOLITH_NAME, MONOLITH_VERSION)

LOADER_GRAPH: Dict[str, Dict[str, Any]] = {
    "v6": {
        "name": "StudioCoreV6",
        "loader": StudioCoreV6,
        "available": StudioCoreV6 is not None,
        "version": STUDIOCORE_VERSION,
        "priority": 100,
    },
    "v5": {
        "name": "StudioCoreV5",
        "loader": _MONOLITH_V5,
        "available": _MONOLITH_V5 is not None,
        "version": MONOLITH_VERSION,
        "priority": 80,
    },
    "monolith": {
        "name": "StudioCore",
        "loader": _MONOLITH_CLS,
        "available": _MONOLITH_CLS is not None,
        "version": MONOLITH_VERSION,
        "priority": 60,
    },
    "fallback": {
        "name": "StudioCoreFallback",
        "loader": StudioCoreFallback,
        "available": True,
        "version": "fallback",
        "priority": 0,
    },
}

StudioCore: Type[Any] = _MONOLITH_CLS or StudioCoreFallback
StudioCoreV5: Type[Any] | None = _MONOLITH_V5 or _MONOLITH_CLS
if _FORCE_V5 and StudioCoreV5:
    StudioCore = StudioCoreV5

if StudioCore is StudioCoreFallback and not _LOAD_ERROR:
    _LOAD_ERROR = "Monolith module was not available; fallback engaged."

_LOADER_DIAGNOSTICS = LoaderDiagnostics(
    monolith_module=MONOLITH_NAME,
    monolith_version=MONOLITH_VERSION,
    engine_variant="fallback" if StudioCore is StudioCoreFallback else ("v6" if StudioCore is StudioCoreV6 else "monolith"),
    fallback_used=StudioCore is StudioCoreFallback,
    engine_order=_requested_loader_order(),
    errors=tuple(filter(None, [_LOAD_ERROR] if _LOAD_ERROR else [])),
    attempted=(),
    active=None,
)


def _update_diagnostics(*, active: str | None, attempted: List[str], errors: List[str]) -> None:
    global _LOADER_DIAGNOSTICS
    _LOADER_DIAGNOSTICS = LoaderDiagnostics(
        monolith_module=MONOLITH_NAME,
        monolith_version=MONOLITH_VERSION,
        engine_variant=active or _LOADER_DIAGNOSTICS.engine_variant,
        fallback_used=active == "fallback",
        engine_order=_requested_loader_order(),
        errors=tuple(errors),
        attempted=tuple(attempted),
        active=active,
    )


def get_core(*, prefer_v6: bool | None = None, **kwargs: Any) -> Any:
    """Return an instantiated core following the fallback chain."""

    attempts: List[str] = []
    errors: List[str] = []
    for loader_key in _requested_loader_order(prefer_v6):
        meta = LOADER_GRAPH.get(loader_key)
        loader_cls = meta.get("loader") if meta else None
        if not loader_cls:
            continue
        attempts.append(loader_key)
        try:
            instance = loader_cls(**kwargs)
            LOADER_STATUS.update(
                {
                    "active": loader_key,
                    "attempted": attempts,
                    "errors": errors,
                    "version": meta.get("version"),
                    "requested_order": list(_requested_loader_order(prefer_v6)),
                }
            )
            _update_diagnostics(active=loader_key, attempted=attempts, errors=errors)
            return instance
        except Exception as exc:  # pragma: no cover - defensive guard
            message = f"{meta['name']} failed: {exc}"
            _LOGGER.warning(message)
            errors.append(message)

    LOADER_STATUS.update({"active": None, "errors": errors, "attempted": attempts})
    _update_diagnostics(active=None, attempted=attempts, errors=errors)
    raise RuntimeError("Нет доступных загрузчиков StudioCore")


def loader_diagnostics() -> LoaderDiagnostics:
    """Expose loader metadata for tests and debug tooling."""

    return _LOADER_DIAGNOSTICS


__all__ = [
    "StudioCore",
    "StudioCoreV5",
    "StudioCoreV6",
    "StudioCoreFallback",
    "get_core",
    "loader_diagnostics",
    "FINGERPRINT",
    "STUDIOCORE_VERSION",
    "MONOLITH_VERSION",
    "DEFAULT_LOADER_ORDER",
    "LOADER_GRAPH",
    "LOADER_STATUS",
]


if __name__ == "__main__":  # pragma: no cover - manual smoke-test only
    print(f"\n🧠 Инициализация StudioCore {STUDIOCORE_VERSION}...")
    try:
        core = get_core()
        if getattr(core, "is_fallback", False):
            print(f"⚠️ Используется fallback ядро ({MONOLITH_VERSION})")
        else:
            print(f"✅ Ядро загружено успешно ({MONOLITH_VERSION})")
            subsystems = [
                s
                for s in [
                    "emotion",
                    "tlp",
                    "rhythm",
                    "freq",
                    "safety",
                    "integrity",
                    "vocals",
                    "style",
                    "tone",
                ]
                if hasattr(core, s)
            ]
            print(f"⚙️ Активные подсистемы: {', '.join(subsystems)}\n")
    except Exception as exc:
        print(f"❌ Ошибка инициализации: {exc}")

# StudioCore Signature Block (Do Not Remove)
# Author: Сергей Бауэр (@Sbauermaner)
# Fingerprint: StudioCore-FP-2025-SB-9fd72e27
# Hash: 22ae-df91-bc11-6c7e
