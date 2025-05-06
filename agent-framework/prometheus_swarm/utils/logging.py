"""Enhanced logging configuration and utilities."""

import logging
import sys
import traceback
import json
from typing import Any, Dict, Optional
from functools import wraps
from datetime import datetime, timezone
from pathlib import Path

from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init(strip=False)  # Force color output even when not in a terminal


class JsonFormatter(logging.Formatter):
    """Custom JSON log formatter."""

    def format(self, record):
        """Convert log record to JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Include extra attributes
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        # Include exception information
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class StructuredLogger:
    """Enhanced logger with structured logging support."""

    def __init__(self, name: str, log_level: int = logging.INFO):
        """
        Initialize a structured logger.

        Args:
            name: Logger name
            log_level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False
        self._configure_console_handler()

    def _configure_console_handler(self):
        """Configure console handler for structured logging."""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a debug message."""
        self.logger.debug(message, extra={'extra': extra or {}})

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an info message."""
        self.logger.info(message, extra={'extra': extra or {}})

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a warning message."""
        self.logger.warning(message, extra={'extra': extra or {}})

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an error message."""
        self.logger.error(message, extra={'extra': extra or {}})

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a critical message."""
        self.logger.critical(message, extra={'extra': extra or {}})

    def log_exception(
        self,
        exception: Exception,
        context: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log an exception with detailed traceback.

        Args:
            exception: Exception to log
            context: Optional context string
            extra: Additional context
        """
        extra = extra or {}
        error_details = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            "context": context,
            **extra
        }

        self.logger.error(
            f"Exception occurred{f': {context}' if context else ''}",
            extra={'extra': error_details},
            exc_info=exception
        )


# Create a global structured logger
logger = StructuredLogger("prometheus_swarm")


def log_execution_time(func):
    """
    Decorator to log function execution time.

    Args:
        func: Function to decorate
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now(timezone.utc)
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(
                "Function executed",
                extra={
                    "function_name": func.__name__,
                    "execution_time_seconds": duration
                }
            )
            return result
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(
                "Function execution failed",
                extra={
                    "function_name": func.__name__,
                    "execution_time_seconds": duration,
                    "exception": str(e)
                }
            )
            raise

    return wrapper


def add_file_logging(
    log_file: str,
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
):
    """
    Add file logging with rotation.

    Args:
        log_file: Path to the log file
        log_level: Logging level
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    try:
        from logging.handlers import RotatingFileHandler

        # Create log directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JsonFormatter())
        logger.logger.addHandler(file_handler)
        logger.info(
            "File logging enabled", 
            extra={"log_file": str(log_file)}
        )
    except Exception as e:
        logger.error(
            "Failed to set up file logging",
            extra={"log_file": str(log_file), "error": str(e)}
        )