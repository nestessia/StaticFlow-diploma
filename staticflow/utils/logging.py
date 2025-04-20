"""
Logging configuration for StaticFlow.

This module provides a centralized logging setup for the StaticFlow framework.
"""

import logging
import os
import sys
from pathlib import Path
import datetime

# Базовый логгер для всего фреймворка
logger = logging.getLogger("staticflow")

# Форматирование: время | уровень | сообщение
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Уровни логирования
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def setup_logging(level="info", log_file=None, console=True):
    """
    Setup logging for StaticFlow.
    
    Args:
        level: Log level (debug, info, warning, error, critical)
        log_file: Path to log file (None for no file logging)
        console: Whether to log to console
    """
    # Определяем уровень логирования
    log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # Настраиваем базовый логгер
    logger.setLevel(log_level)
    
    # Создаем форматтер
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Если все обработчики нужно удалить
    if hasattr(logger, 'handlers'):
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    
    # Добавляем обработчик для вывода в консоль
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    
    # Добавляем обработчик для записи в файл
    if log_file:
        # Если передан только путь к директории, создаем имя файла с датой
        log_path = Path(log_file)
        if log_path.is_dir():
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = log_path / f"staticflow_{date_str}.log"
        
        # Создаем директорию для лога, если она не существует
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    if log_file:
        logger.info(f"Log file: {log_file}")


def get_logger(name):
    """
    Get a logger with the given name, as a child of the staticflow logger.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"staticflow.{name}")

# По умолчанию настраиваем базовое логирование
# Можно переопределить, вызвав setup_logging с другими параметрами
true_values = ("true", "1", "yes")
console_enabled = os.environ.get("STATICFLOW_LOG_CONSOLE", "true").lower() in true_values

setup_logging(
    level=os.environ.get("STATICFLOW_LOG_LEVEL", "info"),
    log_file=os.environ.get("STATICFLOW_LOG_FILE", None),
    console=console_enabled
) 