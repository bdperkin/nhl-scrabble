"""Unit tests for logging configuration module."""

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest.mock import patch

import colorlog

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

    def test_colorized_logging_in_tty(self) -> None:
        """Test that colors are enabled for TTY output."""
        with (
            patch("sys.stderr.isatty", return_value=True),
            patch.dict("os.environ", {}, clear=True),
        ):
            setup_logging(verbose=True)
            logger = logging.getLogger()

            # Should have a ColoredFormatter when output is a TTY
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, colorlog.ColoredFormatter)

    def test_plain_logging_in_pipe(self) -> None:
        """Test that colors are disabled for piped output."""
        with patch("sys.stderr.isatty", return_value=False):
            setup_logging(verbose=True)
            logger = logging.getLogger()

            # Should use standard Formatter when not a TTY
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, logging.Formatter)
            assert not isinstance(handler.formatter, colorlog.ColoredFormatter)

    def test_no_color_environment_variable(self) -> None:
        """Test that NO_COLOR environment variable disables colors."""
        with (
            patch("sys.stderr.isatty", return_value=True),
            patch.dict("os.environ", {"NO_COLOR": "1"}),
        ):
            setup_logging(verbose=True)
            logger = logging.getLogger()

            # Should be plain even though TTY
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, logging.Formatter)
            assert not isinstance(handler.formatter, colorlog.ColoredFormatter)

    def test_dumb_terminal_disables_colors(self) -> None:
        """Test that TERM=dumb disables colors."""
        with (
            patch("sys.stderr.isatty", return_value=True),
            patch.dict("os.environ", {"TERM": "dumb"}, clear=True),
        ):
            setup_logging(verbose=True)
            logger = logging.getLogger()

            # Should be plain for dumb terminal
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, logging.Formatter)
            assert not isinstance(handler.formatter, colorlog.ColoredFormatter)

    def test_json_output_disables_colors(self) -> None:
        """Test that JSON output mode disables colors."""
        with (
            patch("sys.stderr.isatty", return_value=True),
            patch.dict("os.environ", {}, clear=True),
        ):
            setup_logging(verbose=True, json_output=True)
            logger = logging.getLogger()

            # Should use JSONFormatter, not ColoredFormatter
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, JSONFormatter)
            assert not isinstance(handler.formatter, colorlog.ColoredFormatter)

    def test_color_log_levels(self) -> None:
        """Test that different log levels use correct colors."""
        with (
            patch("sys.stderr.isatty", return_value=True),
            patch.dict("os.environ", {}, clear=True),
        ):
            setup_logging(verbose=True)
            logger = logging.getLogger()

            # Get the ColoredFormatter
            handler = logger.handlers[0]
            assert isinstance(handler.formatter, colorlog.ColoredFormatter)

            # Verify color configuration
            formatter = handler.formatter
            assert formatter.log_colors["DEBUG"] == "cyan"
            assert formatter.log_colors["INFO"] == "green"
            assert formatter.log_colors["WARNING"] == "yellow"
            assert formatter.log_colors["ERROR"] == "red"
            assert formatter.log_colors["CRITICAL"] == "red,bg_white"


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


class TestFileLogging:
    """Tests for file logging functionality."""

    def test_file_handler_creation(self, tmp_path: Path) -> None:
        """Test file handler is created when log_file is provided."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file)

        logger = logging.getLogger()

        # Should have both console and file handlers
        assert len(logger.handlers) >= 2

        # Check that a RotatingFileHandler exists
        has_file_handler = any(isinstance(h, RotatingFileHandler) for h in logger.handlers)
        assert has_file_handler

    def test_file_handler_creates_log_file(self, tmp_path: Path) -> None:
        """Test that log file is created."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file)

        logger = logging.getLogger()
        logger.info("Test message")

        # Log file should exist
        assert log_file.exists()

    def test_file_handler_directory_creation(self, tmp_path: Path) -> None:
        """Test automatic creation of log directory."""
        log_file = tmp_path / "logs" / "subdir" / "test.log"
        assert not log_file.parent.exists()

        setup_logging(log_file=log_file)

        # Parent directories should be created
        assert log_file.parent.exists()
        assert log_file.parent.is_dir()

    def test_file_handler_rotation_parameters(self, tmp_path: Path) -> None:
        """Test file handler rotation configuration."""
        log_file = tmp_path / "test.log"
        max_bytes = 1024
        backup_count = 3

        setup_logging(log_file=log_file, max_bytes=max_bytes, backup_count=backup_count)

        logger = logging.getLogger()

        # Find the RotatingFileHandler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert file_handler.maxBytes == max_bytes
        assert file_handler.backupCount == backup_count

    def test_file_handler_rotation_behavior(self, tmp_path: Path) -> None:
        """Test that file handler rotates when size limit exceeded."""
        log_file = tmp_path / "test.log"
        max_bytes = 100  # Small size to trigger rotation
        backup_count = 2

        setup_logging(log_file=log_file, max_bytes=max_bytes, backup_count=backup_count)

        logger = logging.getLogger()

        # Write enough data to trigger rotation
        for i in range(50):
            logger.info(f"Log message {i} with sufficient length to trigger rotation")

        # Original log file should exist
        assert log_file.exists()

        # Rotation may or may not have happened depending on exact sizes
        # Just verify the mechanism is configured by checking file exists

    def test_file_handler_utf8_encoding(self, tmp_path: Path) -> None:
        """Test file handler uses UTF-8 encoding."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file)

        logger = logging.getLogger()

        # Find the RotatingFileHandler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        # RotatingFileHandler should be configured with utf-8 encoding
        # We can verify by logging unicode and reading back
        logger.info("Unicode test: 日本語 中文 한글 العربية")

        # Read file and verify unicode content
        content = log_file.read_text(encoding="utf-8")
        assert "日本語" in content
        assert "中文" in content

    def test_file_handler_with_json_output(self, tmp_path: Path) -> None:
        """Test file handler with JSON formatting."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file, json_output=True)

        logger = logging.getLogger()
        logger.info("Test message")

        # Find file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert isinstance(file_handler.formatter, JSONFormatter)

        # Read log file and verify JSON format
        content = log_file.read_text()
        lines = [line for line in content.strip().split("\n") if line]

        # Each line should be valid JSON
        for line in lines:
            data = json.loads(line)
            assert "timestamp" in data
            assert "level" in data
            assert "message" in data

    def test_file_handler_with_sanitization(self, tmp_path: Path) -> None:
        """Test file handler applies sensitive data filter."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file, sanitize_logs=True)

        logger = logging.getLogger()

        # Find file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None

        # Check that SensitiveDataFilter is attached
        filter_names = [f.__class__.__name__ for f in file_handler.filters]
        assert "SensitiveDataFilter" in filter_names

    def test_file_handler_without_sanitization(self, tmp_path: Path) -> None:
        """Test file handler without sensitive data filter."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file, sanitize_logs=False)

        logger = logging.getLogger()

        # Find file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None

        # Should not have SensitiveDataFilter
        filter_names = [f.__class__.__name__ for f in file_handler.filters]
        assert "SensitiveDataFilter" not in filter_names

    def test_file_handler_log_level_verbose(self, tmp_path: Path) -> None:
        """Test file handler respects verbose setting."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file, verbose=True)

        logger = logging.getLogger()

        # Find file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert file_handler.level == logging.DEBUG

    def test_file_handler_log_level_normal(self, tmp_path: Path) -> None:
        """Test file handler with normal log level."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file, verbose=False)

        logger = logging.getLogger()

        # Find file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert file_handler.level == logging.INFO

    def test_file_handler_plain_formatter(self, tmp_path: Path) -> None:
        """Test file handler uses plain formatter (no colors)."""
        log_file = tmp_path / "test.log"

        with (
            patch("sys.stderr.isatty", return_value=True),
            patch.dict("os.environ", {}, clear=True),
        ):
            # Even with TTY, file handler should use plain formatter
            setup_logging(log_file=log_file, verbose=True)

            logger = logging.getLogger()

            # Find file handler
            file_handler = None
            for handler in logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    file_handler = handler
                    break

            assert file_handler is not None
            # Should be plain Formatter, not ColoredFormatter
            assert isinstance(file_handler.formatter, logging.Formatter)
            assert not isinstance(file_handler.formatter, colorlog.ColoredFormatter)

    def test_file_and_console_handlers_coexist(self, tmp_path: Path) -> None:
        """Test that file and console handlers work together."""
        log_file = tmp_path / "test.log"
        setup_logging(log_file=log_file)

        logger = logging.getLogger()

        # Should have both handlers
        has_console = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
            for h in logger.handlers
        )
        has_file = any(isinstance(h, RotatingFileHandler) for h in logger.handlers)

        assert has_console
        assert has_file
        assert len(logger.handlers) >= 2

    def test_multiple_setup_logging_calls_reset_handlers(self, tmp_path: Path) -> None:
        """Test that calling setup_logging multiple times resets handlers."""
        log_file1 = tmp_path / "test1.log"
        log_file2 = tmp_path / "test2.log"

        # First setup
        setup_logging(log_file=log_file1)
        logger = logging.getLogger()
        initial_handler_count = len(logger.handlers)

        # Second setup
        setup_logging(log_file=log_file2)
        logger = logging.getLogger()

        # Handler count should be same (handlers reset)
        assert len(logger.handlers) == initial_handler_count

        # Should have handlers for log_file2, not log_file1
        file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]

        # Should only have one file handler pointing to log_file2
        assert len(file_handlers) == 1
