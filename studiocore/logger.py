# -*- coding: utf-8 -*-
"""
StudioCore v6 — Централизованный конфигуратор логов. (v2 - TypeError ИСПРАВЛЕН)
Настраивает подробный вывод для отладки вызовов функций.
"""
import logging
import sys
import os # v2: Добавлен os для определения уровня лога

# v2: Уровень по умолчанию INFO, но можно переопределить через app.py
LOG_LEVEL = logging.DEBUG if os.environ.get("STUDIOCORE_DEBUG") else logging.INFO

# Определяем собственный формат, который включает имя функции и номер строки
LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)-5s] "
    "[%(name)s.%(funcName)s:%(lineno)d] "
    "- %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


_is_configured = False

# v2: Исправлена ошибка TypeError
# Теперь функция принимает 'level' (по умолчанию INFO), 
# но app.py может передать DEBUG
def setup_logging(level=logging.INFO):
    """
    Применяет конфигурацию логов ко всей системе.
    Вызывается один раз из app.py или test_all.py.
    """
    global _is_configured
    if _is_configured:
        return

    # Получаем корневой логгер
    root_logger = logging.getLogger()
    
    # v2: Используем 'level', переданный из app.py
    CURRENT_LOG_LEVEL = level 
    root_logger.setLevel(CURRENT_LOG_LEVEL)

    # Удаляем все существующие обработчики (чтобы избежать дублирования в HF)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Создаем новый обработчик для вывода в консоль (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(CURRENT_LOG_LEVEL)

    # Применяем наш подробный формат
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(formatter)

    # Добавляем обработчик к корню
    root_logger.addHandler(console_handler)

    # Приглушаем слишком "болтливые" сторонние библиотеки
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("gradio_client").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    log = logging.getLogger(__name__)
    log.info("=" * 50)
    log.info(f"🚀 Централизованное логирование (УРОВЕНЬ {logging.getLevelName(CURRENT_LOG_LEVEL)}) активировано.")
    log.info("=" * 50)
    _is_configured = True