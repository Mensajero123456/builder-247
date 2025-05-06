"""Enhanced error handling for the Prometheus Swarm framework."""

import sys
import traceback
from typing import Any, Dict, Optional


class PrometheusSwarmError(Exception):
    """Base error class for Prometheus Swarm framework."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a Prometheus Swarm error.

        Args:
            message: Human-readable error description
            error_code: Unique error identifier
            details: Additional context about the error
            original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNSPECIFIED_ERROR"
        self.details = details or {}
        self.original_error = original_error
        self.traceback = None

        if original_error:
            self.traceback = ''.join(traceback.format_exception(
                type(original_error), original_error, original_error.__traceback__
            ))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to a dictionary representation.

        Returns:
            A dictionary with error details
        """
        error_dict = {
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }
        if self.traceback:
            error_dict["traceback"] = self.traceback
        return error_dict

    def __str__(self) -> str:
        """
        String representation of the error.

        Returns:
            Formatted error message
        """
        base_str = f"[{self.error_code}] {self.message}"
        if self.details:
            base_str += f" (Details: {self.details})"
        return base_str


class ClientAPIError(PrometheusSwarmError):
    """Specialized error for API client interactions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a Client API Error.

        Args:
            message: Error description
            status_code: HTTP status code
            error_code: API-specific error code
            details: Additional error context
            original_error: Original exception
        """
        super().__init__(
            message=message,
            error_code=error_code or f"API_ERROR_{status_code}",
            details=details or {},
            original_error=original_error
        )
        self.status_code = status_code


class ConfigurationError(PrometheusSwarmError):
    """Error raised for configuration-related issues."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize a Configuration Error.

        Args:
            message: Configuration error description
            config_key: Configuration key causing the error
            original_error: Original exception
        """
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details,
            original_error=original_error
        )


class IntegrationError(PrometheusSwarmError):
    """Error raised for integration or third-party service issues."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize an Integration Error.

        Args:
            message: Integration error description
            service_name: Name of the service causing the error
            original_error: Original exception
        """
        details = {"service_name": service_name} if service_name else {}
        super().__init__(
            message=message,
            error_code="INTEGRATION_ERROR",
            details=details,
            original_error=original_error
        )


def capture_and_log_error(
    error: Exception,
    logger=None,
    context: Optional[str] = None
) -> PrometheusSwarmError:
    """
    Capture, log, and transform an exception into a PrometheusSwarmError.

    Args:
        error: Original exception
        logger: Optional logger to use for logging
        context: Optional additional context about the error

    Returns:
        A PrometheusSwarmError instance
    """
    context = context or "Error Capture"
    swarm_error = PrometheusSwarmError(
        message=str(error),
        error_code="UNEXPECTED_ERROR",
        details={"context": context},
        original_error=error
    )

    if logger:
        logger.error(
            f"{context}: {swarm_error}",
            extra={"error": swarm_error.to_dict()}
        )
    else:
        # Fallback logging if no logger is provided
        print(f"ERROR: {swarm_error}", file=sys.stderr)
        traceback.print_exc()

    return swarm_error