"""Test logging utilities."""

import json
import logging
import pytest
from io import StringIO
import sys

from prometheus_swarm.utils.logging import StructuredLogger, log_execution_time, add_file_logging


def test_structured_logger_json_output(caplog):
    """Test that logger outputs structured JSON."""
    logger = StructuredLogger("test_logger")
    caplog.set_level(logging.DEBUG)

    logger.info("Test message", extra={"key": "value"})

    # Validate log entry
    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    
    # Try parsing the message as JSON
    log_data = json.loads(log_record.message)
    
    assert "timestamp" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert log_data.get("key") == "value"


def test_structured_logger_log_levels(caplog):
    """Test different log levels."""
    logger = StructuredLogger("test_logger")
    caplog.set_level(logging.DEBUG)

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    assert len(caplog.records) == 5
    log_levels = [record.levelname for record in caplog.records]
    assert log_levels == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_log_exception(caplog):
    """Test logging an exception."""
    logger = StructuredLogger("test_logger")
    caplog.set_level(logging.ERROR)

    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger.log_exception(e, context="Test context")

    assert len(caplog.records) == 1
    log_record = caplog.records[0]
    log_data = json.loads(log_record.message)

    assert log_data["level"] == "ERROR"
    assert "Test exception" in log_data["exception_message"]
    assert log_data["context"] == "Test context"
    assert "traceback" in log_data


def test_log_execution_time():
    """Test log_execution_time decorator."""
    @log_execution_time
    def dummy_function(x):
        return x * 2

    result = dummy_function(5)
    assert result == 10


def test_add_file_logging(tmpdir):
    """Test adding file logging."""
    log_file = tmpdir.join("test.log")
    add_file_logging(str(log_file))

    # Verify log file exists
    assert log_file.check(file=1)

    # TODO: Add more comprehensive checks
    with open(str(log_file), 'r') as f:
        contents = f.read()
        assert "File logging enabled" in contents