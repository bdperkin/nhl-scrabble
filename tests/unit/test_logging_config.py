"""Unit tests for logging configuration module."""

import json
import logging

from nhl_scrabble.logging_config import JSONFormatter, setup_logging


class TestLoggingConfig:
    """Tests for logging configuration."""

    def test_setup_logging_default(self) -> None:
        """Test setup_logging with default settings (INFO level)."""
        setup_logging(verbose=False)
        logger = logging.getLogger("nhl_scrabble")

        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_setup_logging_verbose(self) -> None:
        """Test setup_logging with verbose=True (DEBUG level)."""
        setup_logging(verbose=True)
        logger = logging.getLogger()

        # Root logger should be DEBUG
        assert logger.level == logging.DEBUG

    def test_setup_logging_has_handlers(self) -> None:
        """Test that configured logger has handlers."""
        setup_logging(verbose=False)
        logger = logging.getLogger()

        assert len(logger.handlers) > 0

    def test_setup_logging_console_handler(self) -> None:
        """Test that logger has console handler."""
        setup_logging(verbose=False)
        logger = logging.getLogger()

        # Should have at least one StreamHandler
        handlers = logger.handlers
        has_console = any(isinstance(h, logging.StreamHandler) for h in handlers)
        assert has_console

    def test_setup_logging_formatting(self) -> None:
        """Test that handlers have formatters."""
        setup_logging(verbose=False)
        logger = logging.getLogger()

        for handler in logger.handlers:
            assert handler.formatter is not None

    def test_setup_logging_json_output(self) -> None:
        """Test setup_logging with JSON output."""
        setup_logging(verbose=False, json_output=True)
        logger = logging.getLogger()

        # Should have handlers
        assert len(logger.handlers) > 0

    def test_logger_can_log_messages(self) -> None:
        """Test that configured logger can log messages."""
        setup_logging(verbose=True)
        logger = logging.getLogger("test_logger")

        # Should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_setup_logging_suppresses_third_party(self) -> None:
        """Test that third-party loggers are suppressed."""
        setup_logging(verbose=False)

        # Check that urllib3 and requests loggers are set to WARNING
        urllib3_logger = logging.getLogger("urllib3")
        requests_logger = logging.getLogger("requests")

        assert urllib3_logger.level == logging.WARNING
        assert requests_logger.level == logging.WARNING

    def test_setup_logging_sanitize_disabled(self) -> None:
        """Test setup_logging with sanitize_logs=False."""
        setup_logging(verbose=False, sanitize_logs=False)
        logger = logging.getLogger()

        # Should still have handlers
        assert len(logger.handlers) > 0

        # Check that no SensitiveDataFilter is attached
        handler = logger.handlers[0]
        filter_names = [f.__class__.__name__ for f in handler.filters]
        assert "SensitiveDataFilter" not in filter_names

    def test_setup_logging_sanitize_enabled(self) -> None:
        """Test setup_logging with sanitize_logs=True (default)."""
        setup_logging(verbose=False, sanitize_logs=True)
        logger = logging.getLogger()

        # Should have handlers with SensitiveDataFilter
        handler = logger.handlers[0]
        filter_names = [f.__class__.__name__ for f in handler.filters]
        assert "SensitiveDataFilter" in filter_names


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
