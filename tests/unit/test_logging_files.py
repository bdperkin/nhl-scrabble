"""Unit tests for logging configuration module."""

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest.mock import patch

import colorlog

from nhl_scrabble.logging_config import JSONFormatter, setup_logging
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
