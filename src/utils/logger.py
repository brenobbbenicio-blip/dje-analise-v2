"""
Sistema de logging
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from src.config import settings


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: str = settings.LOG_LEVEL
) -> logging.Logger:
    """
    Configura e retorna um logger

    Args:
        name: Nome do logger
        log_file: Arquivo de log (opcional)
        level: Nível de log

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove handlers existentes
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (se especificado)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
