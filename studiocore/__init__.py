# -*- coding: utf-8 -*-
"""
🎧 StudioCore v6.2 — Unified Adaptive Engine Loader (DIAGNOSTIC STABLE)
-----------------------------------------------------------------------
- [V6-SPEC v6.1]: Загрузчик теперь ищет StudioCoreV5 в монолите.
"""

from __future__ import annotations
import os
import sys
import glob
import re
import importlib
import logging
from typing import Any, Optional, Type


# =====================================================================
# 🔧 FIX: Гарантируем, что studiocore импортируем в контейнере HF
# =====================================================================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# V6-SPEC: Импортируем Fallback из его собственного файла
try:
    from .fallback import StudioCoreFallback
except ImportError:
    # Если даже fallback не импортируется, создаем его "на лету"
    class StudioCoreFallback:
        def __init__(self, *args, **kwargs):
            self.is_fallback = True
            print("CRITICAL FALLBACK ERROR: fallback.py not found.")
        def analyze(self, *_, **__):
            return {"error": "CRITICAL FALLBACK: Core components missing."}


# =====================================================================
# 🔹 Метаданные
# =====================================================================
STUDIOCORE_VERSION = "v6.2-DIAGNOSTIC"
CORE_LOADED_NAME: str = "none"
CORE_LOADED_SOURCE: str = "none"


# =====================================================================
# 🔹 Логгер загрузчика
# =====================================================================
def _setup_loader_logging() -> logging.Logger:
    """
    Создает логгер 'studiocore.loader' с выводом:
    - в консоль
    - в файл logs/studio_loader.log
    """
    logger = logging.getLogger("studiocore.loader")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "studio_loader.log")

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.debug(f"Loader logging initialized → {log_path}")
    return logger


log = _setup_loader_logging()


# =====================================================================
# 🔹 Fallback ядро (V6-SPEC: теперь импортируется)
# =====================================================================
# (Класс StudioCoreFallback теперь импортируется вверху файла)

# Текущий выбранный класс ядра
StudioCore: Type[Any] = StudioCoreFallback  # type: ignore


# =====================================================================
# 🔹 Попытка загрузки V6
# =====================================================================
def _try_load_v6() -> Optional[Type[Any]]:
    global CORE_LOADED_NAME, CORE_LOADED_SOURCE

    force_v5 = os.getenv("STUDIOCORE_FORCE_V5", "").lower() in ("1", "true", "yes")
    if force_v5:
        log.info("⚙️ STUDIOCORE_FORCE_V5=1 → пропускаем V6.")
        return None

    try:
        from .core_v6 import StudioCoreV6  # type: ignore
        CORE_LOADED_NAME = "StudioCoreV6"
        CORE_LOADED_SOURCE = "core_v6.py"
        log.info("🎧 V6 Orchestrator загружен.")
        return StudioCoreV6

    except ImportError as e:
        log.warning(f"⚠️ V6 Orchestrator отсутствует: {e}")

    except Exception as e:
        log.error(f"❌ Ошибка импорта core_v6.py: {e}", exc_info=True)

    return None


# =====================================================================
# 🔹 Поиск и загрузка V5 Monolith
# =====================================================================
def _detect_latest_monolith() -> str:
    base = os.path.dirname(__file__)
    candidates = glob.glob(os.path.join(base, "monolith_*.py"))

    if not candidates:
        log.warning("⚠️ Monolith не найден → монолит по умолчанию monolith_v4_3_1.")
        return "monolith_v4_3_1"

    def _v(path: str):
        name = os.path.basename(path)
        m = re.search(r"(\d+)_(\d+)_(\d+)", name)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)

    return os.path.splitext(os.path.basename(sorted(candidates, key=_v)[-1]))[0]


def _try_load_v5_monolith() -> Optional[Type[Any]]:
    global CORE_LOADED_NAME, CORE_LOADED_SOURCE

    monolith_name = os.getenv("STUDIOCORE_MONOLITH", "") or _detect_latest_monolith()

    try:
        module = importlib.import_module(f".{monolith_name}", package=__name__)
        # V6-SPEC: Ищем StudioCoreV5
        cls = getattr(module, "StudioCoreV5", None)
        if cls is None:
            # Fallback для старых версий
            cls = getattr(module, "StudioCore", None)
            if cls is None:
                raise AttributeError(f"Класс StudioCoreV5 или StudioCore отсутствует в {monolith_name}.py")

        CORE_LOADED_NAME = f"{cls.__name__} (V5)" # V6-SPEC: Динамическое имя
        CORE_LOADED_SOURCE = f"{monolith_name}.py"

        log.info(f"🎧 V5 Monolith загружен: {monolith_name}.py (Класс: {cls.__name__})")
        return cls

    except Exception as e:
        log.error(f"❌ Ошибка загрузки V5 Monolith ({monolith_name}): {e}", exc_info=True)

    return None


# =====================================================================
# 🔹 Логика выбора ядра
# =====================================================================
def _select_core_class() -> Type[Any]:
    log.debug("🔍 Старт выбора ядра...")

    # 1. V6
    v6 = _try_load_v6()
    if v6:
        return v6

    # 2. V5 Monolith
    v5 = _try_load_v5_monolith()
    if v5:
        return v5

    # 3. Fallback
    log.critical("❌ Не найдено V6 или V5 → активируем fallback.")
    return StudioCoreFallback


StudioCore = _select_core_class()


# =====================================================================
# 🔹 get_core() — безопасное создание экземпляра
# =====================================================================
def get_core() -> Any:
    """
    Создаёт экземпляр выбранного ядра.
    Если ядро падает при инициализации → fallback.
    """

    global StudioCore, CORE_LOADED_NAME, CORE_LOADED_SOURCE

    log.debug(f"🧠 get_core(): создаём экземпляр — {StudioCore.__name__}")

    try:
        core = StudioCore()

        if getattr(core, "is_fallback", False):
            log.warning(f"⚠️ get_core(): fallback ядро ({CORE_LOADED_SOURCE}).")
        else:
            log.info(f"✅ Ядро инициализировано: {CORE_LOADED_NAME} ({CORE_LOADED_SOURCE})")

        return core

    except Exception as e:
        log.error("❌ Ошибка инициализации ядра — fallback активирован.", exc_info=True)

        StudioCore = StudioCoreFallback
        CORE_LOADED_NAME = "StudioCoreFallback"
        CORE_LOADED_SOURCE = "runtime-fallback"

        return StudioCoreFallback()


# =====================================================================
# 🔹 Экспорт
# =====================================================================
__all__ = [
    "STUDIOCORE_VERSION",
    "StudioCore",
    "StudioCoreFallback",
    "get_core",
]


# =====================================================================
# 🔹 Локальный тест запуска
# =====================================================================
if __name__ == "__main__":
    print(f"\n🧠 StudioCore Loader {STUDIOCORE_VERSION}")
    core = get_core()
    if getattr(core, "is_fallback", False):
        print("⚠️ fallback режим. Подробности см. logs/studio_loader.log")
    else:
        print(f"✅ Загружено ядро: {CORE_LOADED_NAME} из {CORE_LOADED_SOURCE}")
