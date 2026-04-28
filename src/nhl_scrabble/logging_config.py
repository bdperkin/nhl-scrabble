"""Logging configuration for NHL Scrabble."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import colorlog

from nhl_scrabble.security import SensitiveDataFilter

logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON string representation of log record
        """
        import json

        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ):
                log_data[key] = value

        return json.dumps(log_data)


def setup_logging(
    verbose: bool = False,
    json_output: bool = False,
    sanitize_logs: bool = True,
    log_file: Path | None = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """Configure logging for the application.

    Args:
        verbose: Enable verbose (DEBUG level) logging
        json_output: Enable JSON structured logging (useful for log aggregation)
        sanitize_logs: Enable sanitization of sensitive data like API keys and tokens
            (default: True). Only disable for debugging in development.
        log_file: Optional path to log file (enables file logging with rotation)
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Examples:
        >>> setup_logging(verbose=True)
        >>> logger = logging.getLogger(__name__)
        >>> logger.debug("This will be shown")

        >>> # Enable file logging with rotation
        >>> setup_logging(log_file=Path("logs/app.log"))

    Security:
        By default, sensitive data like API keys, tokens, and passwords are
        sanitized from log messages. This prevents accidental exposure in log files.
        Only disable sanitization (sanitize_logs=False) in secure development
        environments when debugging is necessary.

        File logs receive the same security filters as console logs to prevent
        sensitive data exposure in persistent storage.
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers.copy():
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    # Add sensitive data filter (security measure)
    if sanitize_logs:
        console_handler.addFilter(SensitiveDataFilter())

    # Determine if we should use colors (only for console output)
    # Respect NO_COLOR standard (https://no-color.org/)
    use_colors = (
        sys.stderr.isatty()
        and not json_output  # Don't colorize JSON output
        and not os.getenv("NO_COLOR")  # Respect NO_COLOR environment variable
        and os.getenv("TERM") != "dumb"  # Don't colorize for dumb terminals
    )

    # Determine formatter for console
    console_formatter: logging.Formatter
    if json_output:
        # JSON formatter for structured logging
        console_formatter = JSONFormatter()
    elif use_colors:
        # Colorized formatter for terminal output
        console_formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )
    else:
        # Plain formatter for non-terminal output (files, pipes)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        # Create parent directories if they don't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # Add sensitive data filter to file handler too
        if sanitize_logs:
            file_handler.addFilter(SensitiveDataFilter())

        # File logs always use plain formatter (no colors)
        file_formatter: logging.Formatter
        if json_output:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        logger.info(f"File logging enabled: {log_file}")

    # Configure root logger
    root_logger.setLevel(log_level)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
