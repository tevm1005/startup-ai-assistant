"""Structured logging for the startup assistant."""

import logging
import sys
from pathlib import Path

from src.config import settings

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class AssistantLogger:
    """Centralized logging helper.

    Usage:
        from src.logging import get_logger
        log = get_logger(__name__)
        log.info("started", extra={"component": "pipeline"})
    """

    _configured = False

    @classmethod
    def configure(cls, level: str | None = None) -> None:
        """Configure root logger once."""
        if cls._configured:
            return

        log_level = (level or "DEBUG" if settings.debug else "INFO").upper()
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        handler.setLevel(log_level)

        root = logging.getLogger("src")
        root.setLevel(log_level)
        root.handlers.clear()
        root.addHandler(handler)

        # Keep third-party loggers quieter
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

        cls._configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.

    Strips the 'src.' prefix for readability.
    """
    AssistantLogger.configure()
    clean = name.replace("src.", "", 1) if name.startswith("src.") else name
    return logging.getLogger(f"src.{clean}")
