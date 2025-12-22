"""Structured logging utilities.

T089 - Implements structured JSON logging for the application.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Optional

from src.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON formatted log string.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data)


class StructuredLogger:
    """Structured logger wrapper with context support."""

    def __init__(self, name: str, level: int = logging.INFO):
        """Initialize structured logger.

        Args:
            name: Logger name.
            level: Logging level.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self._context: dict[str, Any] = {}

        # Only add handler if none exist
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def with_context(self, **kwargs) -> "StructuredLogger":
        """Create logger with additional context.

        Args:
            **kwargs: Context key-value pairs.

        Returns:
            New logger instance with context.
        """
        new_logger = StructuredLogger(self.logger.name, self.logger.level)
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal log method.

        Args:
            level: Log level.
            message: Log message.
            **kwargs: Additional data.
        """
        extra_data = {**self._context, **kwargs}
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None,
        )
        record.extra_data = extra_data
        self.logger.handle(record)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message.

        Args:
            message: Log message.
            **kwargs: Additional data.
        """
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message.

        Args:
            message: Log message.
            **kwargs: Additional data.
        """
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message.

        Args:
            message: Log message.
            **kwargs: Additional data.
        """
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message.

        Args:
            message: Log message.
            **kwargs: Additional data.
        """
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message.

        Args:
            message: Log message.
            **kwargs: Additional data.
        """
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback.

        Args:
            message: Log message.
            **kwargs: Additional data.
        """
        self.logger.exception(message, extra={"extra_data": {**self._context, **kwargs}})


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
) -> None:
    """Setup application logging.

    Args:
        level: Log level string.
        json_format: Whether to use JSON formatting.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

    root_logger.addHandler(handler)

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name.

    Returns:
        StructuredLogger instance.
    """
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    return StructuredLogger(name, level)


# Application logger
app_logger = get_logger("rag_chatbot")
