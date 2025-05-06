"""Test error handling utilities."""

import pytest
import sys
import traceback
from typing import Dict, Any

from prometheus_swarm.utils.errors import (
    PrometheusSwarmError,
    ClientAPIError,
    ConfigurationError,
    IntegrationError,
    capture_and_log_error
)


def test_prometheus_swarm_error_basic():
    """Test basic PrometheusSwarmError instantiation."""
    error = PrometheusSwarmError("Test message", error_code="TEST_CODE")
    assert str(error) == "[TEST_CODE] Test message"
    assert error.error_code == "TEST_CODE"
    assert error.details == {}


def test_prometheus_swarm_error_with_details():
    """Test PrometheusSwarmError with additional details."""
    details = {"key": "value"}
    error = PrometheusSwarmError(
        "Detailed error",
        error_code="DETAIL_CODE",
        details=details
    )
    assert str(error) == "[DETAIL_CODE] Detailed error (Details: {'key': 'value'})"
    assert error.to_dict() == {
        "message": "Detailed error",
        "error_code": "DETAIL_CODE",
        "details": {"key": "value"}
    }


def test_client_api_error():
    """Test ClientAPIError specialized error."""
    error = ClientAPIError(
        "API request failed",
        status_code=404,
        error_code="NOT_FOUND"
    )
    assert str(error) == "[NOT_FOUND] API request failed"
    assert error.status_code == 404
    assert error.to_dict()["error_code"] == "NOT_FOUND"


def test_configuration_error():
    """Test ConfigurationError specialized error."""
    error = ConfigurationError(
        "Invalid configuration",
        config_key="database.host"
    )
    assert str(error) == "[CONFIG_ERROR] Invalid configuration (Details: {'config_key': 'database.host'})"
    assert error.details["config_key"] == "database.host"


def test_integration_error():
    """Test IntegrationError specialized error."""
    error = IntegrationError(
        "Third-party service failed",
        service_name="external_api"
    )
    assert str(error) == "[INTEGRATION_ERROR] Third-party service failed (Details: {'service_name': 'external_api'})"
    assert error.details["service_name"] == "external_api"


def test_capture_and_log_error(caplog):
    """Test capture_and_log_error utility."""
    try:
        raise ValueError("Original error")
    except ValueError as ve:
        caplog.set_level(10)  # Set to DEBUG
        captured_error = capture_and_log_error(ve, context="Test Capture")

    assert isinstance(captured_error, PrometheusSwarmError)
    assert "Original error" in str(captured_error)
    assert captured_error.details["context"] == "Test Capture"
    assert "UNEXPECTED_ERROR" in captured_error.error_code