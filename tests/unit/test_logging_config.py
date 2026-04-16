"""Unit tests for logging configuration module."""

import logging

from nhl_scrabble.logging_config import setup_logging


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
