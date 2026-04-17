# Prevent PII Logging

**GitHub Issue**: #136 - https://github.com/bdperkin/nhl-scrabble/issues/136

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Prevent logging of Personally Identifiable Information (PII) and sensitive data to comply with privacy regulations and security best practices.

Currently, logging may inadvertently capture:

- Player personal data (names, birthdates, birthplaces)
- API request parameters
- Configuration values
- Error messages with sensitive context

Need to:

- Sanitize logs to remove PII
- Redact sensitive fields automatically
- Add PII detection patterns
- Implement safe logging wrappers
- Audit existing logs for PII

## Current State

```python
# src/nhl_scrabble/api/nhl_client.py
logger.info(f"Fetching roster for team: {team_abbrev}")
logger.debug(f"API response: {response.json()}")  # May contain PII!

# src/nhl_scrabble/processors/team_processor.py
logger.debug(f"Processing player: {player.firstName} {player.lastName}")  # PII!
```

**Risks**:

- Player names logged in debug mode
- API responses may contain sensitive data
- Log files could expose PII
- Compliance issues (GDPR, CCPA)

## Proposed Solution

### 1. PII Sanitization Filter

```python
# src/nhl_scrabble/logging_sanitizer.py
import re
import logging

class PIISanitizer(logging.Filter):
    """Filter to sanitize PII from log records."""

    PII_PATTERNS = {
        "player_name": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
        "birthdate": re.compile(r"\d{4}-\d{2}-\d{2}"),
        "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        "api_key": re.compile(r"(api[_-]?key|token)[:=]\s*['\"]?[\w-]+['\"]?", re.I),
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize PII from log message."""
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)

        if record.args:
            record.args = tuple(
                self._sanitize(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )

        return True

    def _sanitize(self, text: str) -> str:
        """Replace PII patterns with redacted placeholders."""
        for name, pattern in self.PII_PATTERNS.items():
            text = pattern.sub(f"[REDACTED-{name.upper()}]", text)
        return text
```

### 2. Safe Logging Wrappers

```python
# src/nhl_scrabble/utils/safe_logging.py
import logging
from typing import Any

def safe_log_player(logger: logging.Logger, player: Any) -> None:
    """Log player info with PII sanitization."""
    # Log only non-PII fields
    logger.debug(f"Processing player: position={player.positionCode}")

def safe_log_api_response(logger: logging.Logger, response: dict) -> None:
    """Log API response with sensitive fields redacted."""
    safe_response = {
        "status": response.get("status"),
        "team_count": len(response.get("teams", [])),
        # Don't log player details
    }
    logger.debug(f"API response: {safe_response}")
```

### 3. Integration

```python
# src/nhl_scrabble/logging_config.py
from nhl_scrabble.logging_sanitizer import PIISanitizer

def setup_logging(verbose: bool = False) -> None:
    logger = logging.getLogger("nhl_scrabble")

    # Add PII sanitizer to all handlers
    pii_filter = PIISanitizer()
    for handler in logger.handlers:
        handler.addFilter(pii_filter)

    logger.info("PII sanitization enabled")
```

### 4. Allowlist for Safe Data

```python
class PIISanitizer(logging.Filter):
    SAFE_FIELDS = {
        "team_abbrev",  # TOR, MTL, etc. - not PII
        "position",     # Forward, Defense
        "score",        # Scrabble score
        "division",     # Division name
    }

    def is_safe_field(self, field_name: str) -> bool:
        return field_name in self.SAFE_FIELDS
```

## Implementation Steps

1. Create `src/nhl_scrabble/logging_sanitizer.py`
1. Implement `PIISanitizer` filter with regex patterns
1. Add safe logging wrappers
1. Integrate filter into logging configuration
1. Audit existing log statements
1. Replace debug logs with sanitized versions
1. Add tests for PII detection
1. Document PII policies

## Testing Strategy

**Unit Tests**:

```python
def test_sanitizer_redacts_player_names():
    sanitizer = PIISanitizer()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Processing player: Connor McDavid",
        args=(),
        exc_info=None,
    )

    sanitizer.filter(record)
    assert "Connor McDavid" not in record.msg
    assert "[REDACTED-PLAYER_NAME]" in record.msg

def test_sanitizer_preserves_safe_data():
    sanitizer = PIISanitizer()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Team: TOR, Score: 150",
        args=(),
        exc_info=None,
    )

    sanitizer.filter(record)
    assert "TOR" in record.msg
    assert "150" in record.msg
```

**Log Audit**:

```bash
# Check for PII in logs
grep -r "firstName\|lastName\|birthDate" src/
```

## Acceptance Criteria

- [ ] PIISanitizer filter implemented
- [ ] PII patterns defined and tested
- [ ] Safe logging wrappers created
- [ ] Filter integrated into logging config
- [ ] Existing logs audited and sanitized
- [ ] No player names in logs
- [ ] No birthdates in logs
- [ ] Tests verify PII redaction
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/logging_sanitizer.py` - New module
- `src/nhl_scrabble/logging_config.py` - Add filter integration
- `src/nhl_scrabble/utils/safe_logging.py` - Safe wrappers
- `src/nhl_scrabble/api/nhl_client.py` - Update logging
- `tests/unit/test_pii_sanitization.py` - New tests

## Dependencies

- No new dependencies required
- Uses standard library logging

## Additional Notes

**PII Categories**:

- **Direct Identifiers**: Names, birthdates, birthplaces
- **Quasi-Identifiers**: Combinations that could identify individuals
- **Sensitive Data**: API keys, tokens, credentials

**Compliance**:

- GDPR: Right to privacy, data minimization
- CCPA: California privacy rights
- Best practices: Don't log what you don't need

**Performance**:

- Regex matching has minimal overhead
- Sanitizer runs only when logging
- Can disable in production if needed

**Alternatives**:

1. **Structured logging**: Log only safe fields
1. **Log levels**: Use INFO for safe, DEBUG for detailed (disabled in prod)
1. **Separate log streams**: PII logs go to secure storage

**Recommendations**:

- Default: Enable PII sanitization
- Production: Disable DEBUG logs entirely
- Development: Safe to see PII for debugging
- Compliance: Audit logs regularly

## Implementation Notes

*To be filled during implementation*
