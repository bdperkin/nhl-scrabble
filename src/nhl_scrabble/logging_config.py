"""Logging configuration for NHL Scrabble."""

import logging
import sys
from typing import Any

from nhl_scrabble.security import SensitiveDataFilter


def setup_logging(
    verbose: bool = False, json_output: bool = False, sanitize_logs: bool = True
) -> None:
    """Configure logging for the application.

    Args:
        verbose: Enable verbose (DEBUG level) logging
        json_output: Enable JSON structured logging (useful for log aggregation)
        sanitize_logs: Enable sanitization of sensitive data like API keys and tokens
            (default: True). Only disable for debugging in development.

    Examples:
        >>> setup_logging(verbose=True)
        >>> logger = logging.getLogger(__name__)
        >>> logger.debug("This will be shown")

    Security:
        By default, sensitive data like API keys, tokens, and passwords are
        sanitized from log messages. This prevents accidental exposure in log files.
        Only disable sanitization (sanitize_logs=False) in secure development
        environments when debugging is necessary.
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    # Add sensitive data filter (security measure)
    if sanitize_logs:
        handler.addFilter(SensitiveDataFilter())

    formatter: logging.Formatter
    if json_output:
        # JSON formatter for structured logging
        formatter = JSONFormatter()
    else:
        # Standard formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


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
            if key not in [
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
            ]:
                log_data[key] = value

        return json.dumps(log_data)
