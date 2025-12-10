"""Logging helpers for the demo project."""

from __future__ import annotations

import logging
from typing import Optional

_configured = False


def configure_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure root logger with console and optional file handler."""
    global _configured
    if _configured:
        return
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )
    _configured = True


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a configured logger instance."""
    configure_logging(level=level)
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
