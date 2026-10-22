# =============================================================================
# CivicSense AI — Structured Logging
# =============================================================================

import logging
import sys
from datetime import datetime, timezone

from app.config import get_settings


class CivicSenseFormatter(logging.Formatter):
    """
    Structured log formatter for CivicSense AI.

    Produces consistent, readable log output with timestamps,
    module context, and log level.
    """

    LEVEL_COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        level = record.levelname
        module = record.name
        message = record.getMessage()

        if self.use_colors and level in self.LEVEL_COLORS:
            level_str = f"{self.LEVEL_COLORS[level]}{level:<8}{self.RESET}"
        else:
            level_str = f"{level:<8}"

        formatted = f"{timestamp} | {level_str} | {module} | {message}"

        if record.exc_info and record.exc_info[0] is not None:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging() -> None:
    """
    Configure application-wide logging.

    Reads log level from settings and applies structured formatting.
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler with structured formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    use_colors = settings.debug
    formatter = CivicSenseFormatter(use_colors=use_colors)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a module.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"civicsense.{name}")
