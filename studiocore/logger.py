# -*- coding: utf-8 -*-
"""
StudioCore v5 — Централизованный конфигуратор логов.
Настраивает подробный вывод для отладки вызовов функций.
"""
import logging
import sys

# Определяем собственный формат, который включает имя функции и номер строки
LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)-5s] "
    "[%(name)s.%(funcName)s:%(lineno)d] "
    "- %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Устанавливаем уровень DEBUG, чтобы ловить АБСОЛЮТНО ВСЕ
LOG_LEVEL = logging.DEBUG 

_is_configured = False

def setup_logging():
    """
    Применяет конфигурацию логов ко всей системе.
    Вызывается один раз из app.py или test_all.py.
    """
    global _is_configured
    if _is_configured:
        return

    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Удаляем все существующие обработчики (чтобы избежать дублирования в HF)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Создаем новый обработчик для вывода в консоль (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)

    # Применяем наш подробный формат
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(formatter)

    # Добавляем обработчик к корню
    root_logger.addHandler(console_handler)

    # Приглушаем слишком "болтливые" сторонние библиотеки
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    root_logger.info("=" * 50)
    root_logger.info("🚀 Централизованное логирование (УРОВЕНЬ DEBUG) активировано.")
    root_logger.info("=" * 50)
    _is_configured = True