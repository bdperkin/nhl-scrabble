# Implement Log Sanitization for Secrets

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

The logging system currently does not sanitize sensitive information. URLs, headers, and error messages may inadvertently expose API keys, tokens, or other secrets in log files.

## Current State

```python
logger.debug(f"Making request to {url}")
logger.error(f"Request failed: {response.text}")
```

**Risk**: If NHL API changes to require authentication, API keys could be logged.

## Proposed Solution

Implement a logging filter to sanitize sensitive data:

```python
import re
import logging
from typing import Pattern

class SensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive data from log messages."""

    # Patterns for sensitive data
    PATTERNS: list[tuple[Pattern[str], str]] = [
        # API keys: key=xxx, api_key=xxx, apikey=xxx
        (re.compile(r'([&?]api[-_]?key=)[^&\s]+', re.IGNORECASE), r'\1***'),
        (re.compile(r'([&?]key=)[^&\s]+', re.IGNORECASE), r'\1***'),

        # Bearer tokens: Authorization: Bearer xxx
        (re.compile(r'(Authorization:\s*Bearer\s+)\S+', re.IGNORECASE), r'\1***'),
        (re.compile(r'(Bearer\s+)\S+', re.IGNORECASE), r'\1***'),

        # Basic auth: Authorization: Basic xxx
        (re.compile(r'(Authorization:\s*Basic\s+)\S+', re.IGNORECASE), r'\1***'),

        # Passwords in URLs: https://user:pass@host
        (re.compile(r'(https?://[^:]+:)([^@]+)(@)', re.IGNORECASE), r'\1***\3'),

        # Generic secrets: secret=xxx, token=xxx
        (re.compile(r'([&?]secret=)[^&\s]+', re.IGNORECASE), r'\1***'),
        (re.compile(r'([&?]token=)[^&\s]+', re.IGNORECASE), r'\1***'),

        # Environment variables in error messages
        (re.compile(r'(NHL_SCRABBLE_\w*(?:KEY|TOKEN|SECRET|PASSWORD)\s*=\s*)[^\s]+', re.IGNORECASE), r'\1***'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data from log record."""
        # Sanitize message
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)

        # Sanitize args (used in format strings)
        if record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.PATTERNS:
                        arg = pattern.sub(replacement, arg)
                sanitized_args.append(arg)
            record.args = tuple(sanitized_args)

        return True

# Apply filter to all loggers
def configure_logging_with_sanitization(verbose: bool = False) -> None:
    """Configure logging with sensitive data sanitization."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Add sanitization filter
    handler.addFilter(SensitiveDataFilter())

    # Configure formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Configure root logger
    logging.root.setLevel(level)
    logging.root.addHandler(handler)
```

Update `src/nhl_scrabble/logging_config.py`:

```python
from nhl_scrabble.security import SensitiveDataFilter

def configure_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    # ... existing setup ...

    # Add sanitization filter to all handlers
    for handler in logging.root.handlers:
        handler.addFilter(SensitiveDataFilter())
```

## Configuration

Add configuration to control sanitization:

```python
@dataclass
class Config:
    """Application configuration."""
    # ... existing fields ...
    sanitize_logs: bool = True  # Disable for debugging only
```

Environment variable:

- `NHL_SCRABBLE_SANITIZE_LOGS` (default: true)

## Testing Strategy

Add tests in `tests/unit/test_security.py`:

```python
import logging
import pytest
from nhl_scrabble.security import SensitiveDataFilter

def test_sanitize_api_key_in_url():
    """Test that API keys in URLs are sanitized."""
    filter = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Making request to https://api.example.com?api_key=secret123",
        args=(),
        exc_info=None
    )

    filter.filter(record)

    assert "secret123" not in record.msg
    assert "api_key=***" in record.msg

def test_sanitize_bearer_token():
    """Test that Bearer tokens are sanitized."""
    filter = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        args=(),
        exc_info=None
    )

    filter.filter(record)

    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg
    assert "Bearer ***" in record.msg

def test_sanitize_password_in_url():
    """Test that passwords in URLs are sanitized."""
    filter = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Connecting to https://user:MyP@ssw0rd@api.example.com",
        args=(),
        exc_info=None
    )

    filter.filter(record)

    assert "MyP@ssw0rd" not in record.msg
    assert "user:***@api.example.com" in record.msg

def test_sanitize_environment_variables():
    """Test that environment variables with secrets are sanitized."""
    filter = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="",
        lineno=0,
        msg="Config error: NHL_SCRABBLE_API_KEY=sk-1234567890abcdef",
        args=(),
        exc_info=None
    )

    filter.filter(record)

    assert "sk-1234567890abcdef" not in record.msg
    assert "NHL_SCRABBLE_API_KEY=***" in record.msg

def test_sanitize_with_args():
    """Test that args in format strings are sanitized."""
    filter = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Request to %s failed",
        args=("https://api.example.com?token=secret123",),
        exc_info=None
    )

    filter.filter(record)

    assert "secret123" not in record.args[0]
    assert "token=***" in record.args[0]

def test_non_string_args_not_affected():
    """Test that non-string args are not modified."""
    filter = SensitiveDataFilter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Processed %d items in %f seconds",
        args=(42, 1.5),
        exc_info=None
    )

    filter.filter(record)

    assert record.args == (42, 1.5)

def test_integration_with_logger(caplog):
    """Test that filter works with actual logger."""
    logger = logging.getLogger("test")
    logger.addHandler(logging.StreamHandler())
    logger.handlers[0].addFilter(SensitiveDataFilter())

    with caplog.at_level(logging.INFO):
        logger.info("API request: https://api.example.com?api_key=secret123")

    assert "secret123" not in caplog.text
    assert "api_key=***" in caplog.text
```

## Acceptance Criteria

- [ ] `SensitiveDataFilter` class sanitizes common secret patterns
- [ ] Filter is applied to all log handlers by default
- [ ] Unit tests verify all sanitization patterns
- [ ] Integration tests verify filter works with real logging
- [ ] Configuration allows disabling for debugging
- [ ] Documentation warns about sensitive data in logs
- [ ] Performance impact is minimal (regex compilation is one-time)

## Related Files

- `src/nhl_scrabble/security.py` (new module)
- `src/nhl_scrabble/logging_config.py`
- `tests/unit/test_security.py` (new)
- `README.md` (add security section)

## Dependencies

None - uses Python stdlib `re` module

## Performance Impact

- Regex compilation: One-time at module import (~1ms)
- Per-log overhead: ~0.1ms per log message
- Acceptable for production use

## Additional Notes

**Trade-offs**:

- **Pro**: Prevents accidental secret exposure
- **Con**: May over-sanitize (false positives)
- **Con**: Adds small overhead to logging

**False Positives**: Patterns like `key=value` might match non-sensitive data. This is acceptable - better safe than sorry.

**Debugging**: If sanitization interferes with debugging:

```bash
# Temporarily disable
export NHL_SCRABBLE_SANITIZE_LOGS=false
nhl-scrabble analyze --verbose
```

**Future Enhancement**: Allow custom patterns via configuration:

```python
# Custom patterns for organization-specific secrets
custom_patterns = [
    (re.compile(r'(X-Custom-Token:\s*)\S+'), r'\1***'),
]
```

## Common Secrets Covered

- ✅ API keys
- ✅ Bearer tokens
- ✅ Basic auth credentials
- ✅ OAuth tokens
- ✅ Passwords in URLs
- ✅ Environment variables with SECRET/KEY/TOKEN/PASSWORD
- ✅ Generic secret= and token= parameters

## Not Covered (Intentional)

- ❌ NHL player names (not sensitive)
- ❌ Team names (not sensitive)
- ❌ Scrabble scores (not sensitive)
- ❌ URLs without credentials (not sensitive)
