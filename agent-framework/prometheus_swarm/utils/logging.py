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
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def _log_structured(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """
        Log a structured message.

        Args:
            level: Logging level
            message: Log message
            extra: Additional context
        """
        extra = extra or {}
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": logging.getLevelName(level),
            "message": message,
            **extra
        }

        # Log to console in JSON
        try:
            console_message = json.dumps(log_entry, default=str)
            self.logger.log(level, console_message)
        except (TypeError, ValueError):
            # Fallback if JSON serialization fails
            self.logger.log(level, message)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a debug message."""
        self._log_structured(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an info message."""
        self._log_structured(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a warning message."""
        self._log_structured(logging.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log an error message."""
        self._log_structured(logging.ERROR, message, extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log a critical message."""
        self._log_structured(logging.CRITICAL, message, extra)

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
            "context": context
        }
        error_details.update(extra)

        self.error(
            f"Exception occurred{f': {context}' if context else ''}",
            extra=error_details
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
        file_formatter = logging.Formatter(
            '%(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.logger.addHandler(file_handler)
        logger.info(
            "File logging enabled", 
            extra={"log_file": log_file}
        )
    except Exception as e:
        logger.error(
            "Failed to set up file logging",
            extra={"log_file": log_file, "error": str(e)}
        )