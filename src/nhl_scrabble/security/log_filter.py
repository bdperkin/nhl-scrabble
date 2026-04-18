"""Security utilities for sanitizing sensitive data from logs."""

import logging
from re import IGNORECASE, Pattern
from re import compile as re_compile
from typing import ClassVar


class SensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive data from log messages.

    This filter removes or masks potentially sensitive information including:
    - Credentials: API keys, tokens, passwords, secrets
    - PII: Player names, birthdates, emails, birthplaces

    This prevents accidental exposure in log files and helps maintain
    compliance with privacy regulations (GDPR, CCPA).

    Attributes:
        PATTERNS: List of regex patterns and their replacement strings
            for sanitizing sensitive data.
        SAFE_PHRASES: Set of multi-word phrases that should not be redacted
            as PII (e.g., division names, conference names).

    Example:
        >>> import logging
        >>> handler = logging.StreamHandler()
        >>> handler.addFilter(SensitiveDataFilter())
        >>> logger = logging.getLogger(__name__)
        >>> logger.addHandler(handler)
        >>> logger.info("API key: api_key=secret123")
        # Logs: "API key: api_key=***"
        >>> logger.info("Player: Connor McDavid")
        # Logs: "Player: [REDACTED-NAME]"
    """

    # Safe multi-word phrases that should NOT be redacted (not PII)
    SAFE_PHRASES: ClassVar[set[str]] = {
        # NHL divisions
        "Atlantic Division",
        "Metropolitan Division",
        "Central Division",
        "Pacific Division",
        # NHL conferences
        "Eastern Conference",
        "Western Conference",
        # Common technical terms
        "Processing NHL",
        "NHL API",
        "NHL Client",
        "NHL Team",
        "NHL Scrabble",
    }

    # Patterns for sensitive data (compiled at class definition time)
    PATTERNS: ClassVar[list[tuple[Pattern[str], str]]] = [
        # API keys: key=xxx, api_key=xxx, apikey=xxx (in URLs and anywhere)
        (re_compile(r"([&?]api[-_]?key=)[^&\s]+", IGNORECASE), r"\1***"),
        (re_compile(r"([&?]key=)[^&\s]+", IGNORECASE), r"\1***"),
        # API keys not in URL context
        (re_compile(r"\b(api[-_]?key\s*[=:]\s*)[^\s,&]+", IGNORECASE), r"\1***"),
        # Bearer tokens: Authorization: Bearer xxx
        (re_compile(r"(Authorization:\s*Bearer\s+)\S+", IGNORECASE), r"\1***"),
        (re_compile(r"(Bearer\s+)\S+", IGNORECASE), r"\1***"),
        # Basic auth: Authorization: Basic xxx
        (re_compile(r"(Authorization:\s*Basic\s+)\S+", IGNORECASE), r"\1***"),
        # Passwords in URLs: https://user:pass@host
        # Match from : after username to @ before hostname (hostname starts with alnum/hyphen/dot)
        # Use greedy .+ to consume everything including @ in password, stopping at @ before host
        (re_compile(r"(https?://[^:/\s]+:)(.+)(@[a-z0-9.-])", IGNORECASE), r"\1***\3"),
        # Generic secrets: secret=xxx, token=xxx
        (re_compile(r"([&?]secret=)[^&\s]+", IGNORECASE), r"\1***"),
        (re_compile(r"([&?]token=)[^&\s]+", IGNORECASE), r"\1***"),
        # Environment variables in error messages
        (
            re_compile(
                r"(NHL_SCRABBLE_\w*(?:KEY|TOKEN|SECRET|PASSWORD)\s*=\s*)[^\s]+",
                IGNORECASE,
            ),
            r"\1***",
        ),
        # PII: Player names in PlayerScore repr format
        # Matches PlayerScore objects with name='...' in repr
        (
            re_compile(
                r"(PlayerScore\([^)]*name=['\"])([^'\"]+)(['\"][^)]*\))",
                IGNORECASE,
            ),
            r"\1[REDACTED-NAME]\3",
        ),
        # PII: Player names in common logging patterns
        # Examples: "player: First Last", "Player Name: 'First Last'", "player: Name, ..."
        # Handles names like "Connor McDavid", "Marc-Andre Fleury", "Ryan O'Reilly"
        # Apostrophes only allowed mid-word (O'Reilly), not at end
        (
            re_compile(
                r"([Pp]layer(?:\s+[Nn]ame)?:?\s+)(['\"])?([A-Z](?:[a-zA-Z]*'[a-zA-Z]+|[a-zA-Z]+)(?:[-\s][A-Z](?:[a-zA-Z]*'[a-zA-Z]+|[a-zA-Z]+))+)(\2)?"
            ),
            r"\1\2[REDACTED-NAME]\4",
        ),
        # PII: Standalone player names (entire string is just a name)
        # Handles names like "Connor McDavid", "Marc-Andre Fleury", "Ryan O'Reilly"
        # Only matches when the entire string is a name (anchored) to avoid false positives
        # Apostrophes only allowed mid-word (O'Reilly), not at end
        (
            re_compile(
                r"^([A-Z](?:[a-zA-Z]*'[a-zA-Z]+|[a-zA-Z]+)(?:[-\s][A-Z](?:[a-zA-Z]*'[a-zA-Z]+|[a-zA-Z]+))+)$"
            ),
            "[REDACTED-NAME]",
        ),
        # PII: firstName/lastName field patterns in logs
        # Examples: "firstName: Connor", "lastName='McDavid'"
        # Apostrophes only allowed mid-word
        (
            re_compile(
                r"((?:first|last)Name\s*[:=]\s*['\"]?)([A-Z](?:[a-zA-Z]*'[a-zA-Z]+|[a-zA-Z]+))(['\"]?)",
                IGNORECASE,
            ),
            r"\1[REDACTED]\3",
        ),
        # PII: Email addresses
        (
            re_compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            ),
            "[REDACTED-EMAIL]",
        ),
        # PII: Birthdates in various formats
        # YYYY-MM-DD, YYYY/MM/DD
        (
            re_compile(
                r"(birth(?:date|_date|Date)?[:=\s]+['\"]?)(\d{4}[-/]\d{2}[-/]\d{2})(['\"]?)",
                IGNORECASE,
            ),
            r"\1[REDACTED-DATE]\3",
        ),
        # MM/DD/YYYY, MM-DD-YYYY (less common but possible)
        (
            re_compile(
                r"(birth(?:date|_date|Date)?[:=\s]+['\"]?)(\d{2}[-/]\d{2}[-/]\d{4})(['\"]?)",
                IGNORECASE,
            ),
            r"\1[REDACTED-DATE]\3",
        ),
        # PII: Birthplace patterns
        # Examples: "birthplace: Toronto, ON", "birthCity='Montreal'"
        (
            re_compile(
                r"(birth(?:place|city|City|Place|_city|_place)[:=\s]+['\"]?)([A-Z][a-zA-Z\s,.-]+?)(['\"]?(?:\s|,|$))"
            ),
            r"\1[REDACTED-PLACE]\3",
        ),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data from log record.

        Processes both the message string and any arguments used in
        formatting, replacing sensitive patterns with '***' or '[REDACTED-*]'.

        Safe phrases (division names, conference names, etc.) are preserved
        and not redacted even if they match name patterns.

        Args:
            record: Log record to sanitize.

        Returns:
            True (always allows the record to be logged after sanitization).
        """
        # Sanitize message
        if isinstance(record.msg, str):
            record.msg = self._sanitize_text(record.msg)

        # Sanitize args (used in format strings like "Request to %s")
        if record.args:
            sanitized_args: list[object] = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_args.append(self._sanitize_text(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)

        return True

    def _sanitize_text(self, text: str) -> str:
        """Sanitize a text string by applying all patterns.

        Args:
            text: Text to sanitize.

        Returns:
            Sanitized text with sensitive data replaced.
        """
        # Skip sanitization if text is a known safe phrase
        if text in self.SAFE_PHRASES:
            return text

        # Apply all sanitization patterns
        sanitized = text
        for pattern, replacement in self.PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)

        return sanitized
