"""Sistema centralizado de logging para a aplicação.

Fornece uma função factory para criar loggers configurados de forma
consistente em toda a aplicação.
"""
import logging
import sys
from pathlib import Path

from src.config import settings


def setup_logger(
    name: str,
    log_file: Path | None = None,
    level: str = settings.LOG_LEVEL,
) -> logging.Logger:
    """Configura e retorna um logger com handlers padrão.

    Args:
        name: Nome do logger (geralmente __name__ do módulo).
        log_file: Caminho opcional para arquivo de log.
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        Logger configurado com console handler e, opcionalmente, file handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()

    # Formatter padrão
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
