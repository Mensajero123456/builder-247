"""Test logging utilities."""

import json
import logging
import pytest
from io import StringIO
import sys
import re

from prometheus_swarm.utils.logging import StructuredLogger, log_execution_time, add_file_logging


def parse_log_json(log_line):
    """Parse log output, handling JSON variations."""
    try:
        return json.loads(log_line)
    except json.JSONDecodeError:
        return None


def test_structured_logger_json_output(caplog):
    """Test that logger outputs structured JSON."""
    caplog.set_level(logging.DEBUG)
    logger = StructuredLogger("test_logger")

    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    logger.info("Test message", extra={"key": "value"})

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Parse the logged JSON
    log_output = captured_output.getvalue().strip()
    log_data = parse_log_json(log_output)
    
    assert log_data is not None
    assert "timestamp" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert log_data.get("key") == "value"


def test_structured_logger_log_levels():
    """Test different log levels."""
    logger = StructuredLogger("test_logger")

    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Capture log lines and parse
    log_output = captured_output.getvalue()
    log_lines = log_output.strip().split('\n')
    log_data = [parse_log_json(line) for line in log_lines if parse_log_json(line)]

    # Validate log levels
    expected_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
    log_levels = [entry["level"] for entry in log_data]
    
    assert log_levels == expected_levels


def test_log_exception():
    """Test logging an exception."""
    logger = StructuredLogger("test_logger")

    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger.log_exception(e, context="Test context")

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Parse the logged JSON
    log_output = captured_output.getvalue().strip()
    log_data = parse_log_json(log_output)

    assert log_data is not None
    assert log_data["level"] == "ERROR"
    assert "Test exception" in log_data["exception_message"]
    assert log_data["context"] == "Test context"
    assert "traceback" in log_data


def test_log_execution_time():
    """Test log_execution_time decorator."""
    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    @log_execution_time
    def dummy_function(x):
        return x * 2

    result = dummy_function(5)
    
    # Restore stdout
    sys.stdout = sys.__stdout__

    # Parse the logged JSON
    log_output = captured_output.getvalue().strip()
    log_data = parse_log_json(log_output)

    assert result == 10
    assert log_data is not None
    assert log_data["level"] == "INFO"
    assert "execution_time_seconds" in log_data
    assert "function_name" in log_data


def test_add_file_logging(tmpdir):
    """Test adding file logging."""
    log_file = tmpdir.join("test.log")
    add_file_logging(str(log_file))

    # Verify log file exists
    assert log_file.check(file=1)

    # Check file contents
    with open(str(log_file), 'r') as f:
        log_entry_str = f.read().strip()
        log_entry = parse_log_json(log_entry_str)
        
        assert log_entry is not None
        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "message" in log_entry