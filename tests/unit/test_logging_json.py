"""Unit tests for logging configuration module."""

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest.mock import patch

import colorlog

from nhl_scrabble.logging_config import JSONFormatter, setup_logging


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_json_formatter_basic(self) -> None:
        """Test JSONFormatter with basic log record."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should be valid JSON
        data = json.loads(result)
        assert data["name"] == "test_logger"
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_json_formatter_with_exception(self) -> None:
        """Test JSONFormatter with exception info."""
        formatter = JSONFormatter()

        def _raise_exception() -> None:
            """Raise exception for testing."""
            msg = "Test exception"
            raise ValueError(msg)

        try:
            _raise_exception()
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert "exception" in data
        assert "ValueError" in data["exception"]
        assert "Test exception" in data["exception"]

    def test_json_formatter_with_extra_fields(self) -> None:
        """Test JSONFormatter with extra fields in log record."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.user_id = "user123"
        record.request_id = "req456"

        result = formatter.format(record)
        data = json.loads(result)

        # Extra fields should be included
        assert data["user_id"] == "user123"
        assert data["request_id"] == "req456"

        # Standard fields should still be present
        assert data["name"] == "test_logger"
        assert data["message"] == "Test message"

    def test_json_formatter_timestamp(self) -> None:
        """Test JSONFormatter timestamp formatting."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        # Timestamp should be present and non-empty
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)
        assert len(data["timestamp"]) > 0

    def test_json_formatter_excludes_internal_fields(self) -> None:
        """Test JSONFormatter excludes internal LogRecord fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        # Internal fields should not be in output
        internal_fields = [
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_text",
            "stack_info",
        ]

        for field in internal_fields:
            assert field not in data

    def test_json_formatter_message_interpolation(self) -> None:
        """Test JSONFormatter handles message interpolation."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="User %s logged in from %s",
            args=("alice", "192.168.1.1"),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        # Message should be interpolated
        assert data["message"] == "User alice logged in from 192.168.1.1"
