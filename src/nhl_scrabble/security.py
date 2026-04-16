"""Security utilities for sanitizing sensitive data from logs."""

import logging
import re
from re import Pattern
from typing import ClassVar


class SensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive data from log messages.

    This filter removes or masks potentially sensitive information like
    API keys, tokens, passwords, and other secrets from log records to
    prevent accidental exposure in log files.

    Attributes:
        PATTERNS: List of regex patterns and their replacement strings
            for sanitizing sensitive data.

    Example:
        >>> import logging
        >>> handler = logging.StreamHandler()
        >>> handler.addFilter(SensitiveDataFilter())
        >>> logger = logging.getLogger(__name__)
        >>> logger.addHandler(handler)
        >>> logger.info("API key: api_key=secret123")
        # Logs: "API key: api_key=***"
    """

    # Patterns for sensitive data (compiled at class definition time)
    PATTERNS: ClassVar[list[tuple[Pattern[str], str]]] = [
        # API keys: key=xxx, api_key=xxx, apikey=xxx
        (re.compile(r"([&?]api[-_]?key=)[^&\s]+", re.IGNORECASE), r"\1***"),
        (re.compile(r"([&?]key=)[^&\s]+", re.IGNORECASE), r"\1***"),
        # Bearer tokens: Authorization: Bearer xxx
        (re.compile(r"(Authorization:\s*Bearer\s+)\S+", re.IGNORECASE), r"\1***"),
        (re.compile(r"(Bearer\s+)\S+", re.IGNORECASE), r"\1***"),
        # Basic auth: Authorization: Basic xxx
        (re.compile(r"(Authorization:\s*Basic\s+)\S+", re.IGNORECASE), r"\1***"),
        # Passwords in URLs: https://user:pass@host
        # Match from : after username to @ before hostname (hostname starts with alnum/hyphen/dot)
        # Use greedy .+ to consume everything including @ in password, stopping at @ before host
        (re.compile(r"(https?://[^:/\s]+:)(.+)(@[a-z0-9.-])", re.IGNORECASE), r"\1***\3"),
        # Generic secrets: secret=xxx, token=xxx
        (re.compile(r"([&?]secret=)[^&\s]+", re.IGNORECASE), r"\1***"),
        (re.compile(r"([&?]token=)[^&\s]+", re.IGNORECASE), r"\1***"),
        # Environment variables in error messages
        (
            re.compile(
                r"(NHL_SCRABBLE_\w*(?:KEY|TOKEN|SECRET|PASSWORD)\s*=\s*)[^\s]+",
                re.IGNORECASE,
            ),
            r"\1***",
        ),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data from log record.

        Processes both the message string and any arguments used in
        formatting, replacing sensitive patterns with '***'.

        Args:
            record: Log record to sanitize.

        Returns:
            True (always allows the record to be logged after sanitization).
        """
        # Sanitize message
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)

        # Sanitize args (used in format strings like "Request to %s")
        if record.args:
            sanitized_args: list[object] = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_arg = arg
                    for pattern, replacement in self.PATTERNS:
                        sanitized_arg = pattern.sub(replacement, sanitized_arg)
                    sanitized_args.append(sanitized_arg)
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)

        return True
