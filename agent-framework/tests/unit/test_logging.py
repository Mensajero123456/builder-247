"""Test logging utilities."""

import json
import logging
import pytest
from datetime import datetime, timezone
from io import StringIO
import sys

from prometheus_swarm.utils.logging import StructuredLogger, log_execution_time, add_file_logging, logger as global_logger


def parse_log_json(log_line):
    """Parse log output, handling JSON variations."""
    log_line = log_line.strip()
    try:
        return json.loads(log_line)
    except json.JSONDecodeError:
        return None


def test_structured_logger_json_output(caplog):
    """Test that logger outputs structured JSON."""
    caplog.set_level(logging.DEBUG)
    custom_logger = StructuredLogger("test_logger")

    custom_logger.info("Test message", extra={"key": "value"})

    # Verify log output
    records = caplog.records
    assert len(records) > 0
    log_record = records[0]
    
    # Check if the record message is a valid JSON
    log_data = parse_log_json(log_record.message)
    
    assert log_data is not None
    assert "timestamp" in log_data
    assert "level" in log_data
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert log_data.get("key") == "value"


def test_structured_logger_log_levels(caplog):
    """Test different log levels."""
    caplog.set_level(logging.DEBUG)
    custom_logger = StructuredLogger("test_logger")

    custom_logger.info("Info message")
    custom_logger.warning("Warning message")
    custom_logger.error("Error message")
    custom_logger.critical("Critical message")

    records = caplog.records
    log_data = [parse_log_json(record.message) for record in records]
    log_levels = [entry["level"] for entry in log_data if entry is not None]
    
    expected_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
    assert log_levels == expected_levels


def test_log_exception(caplog):
    """Test logging an exception."""
    caplog.set_level(logging.ERROR)
    custom_logger = StructuredLogger("test_logger")

    try:
        raise ValueError("Test exception")
    except ValueError as e:
        custom_logger.log_exception(e, context="Test context")

    # Verify log output
    records = caplog.records
    assert len(records) > 0
    log_record = records[0]
    
    log_data = parse_log_json(log_record.message)
    assert log_data is not None
    assert log_data["level"] == "ERROR"
    assert "Test exception" in log_data["exception_message"]
    assert log_data["context"] == "Test context"
    assert "traceback" in log_data


def test_log_execution_time(caplog):
    """Test log_execution_time decorator."""
    caplog.set_level(logging.INFO)

    @log_execution_time
    def dummy_function(x):
        return x * 2

    result = dummy_function(5)

    # Verify log output
    records = caplog.records
    assert len(records) > 0
    log_record = records[0]
    
    log_data = parse_log_json(log_record.message)
    assert log_data is not None
    assert result == 10
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