# Fix Config Validation in Config.from_env()

**GitHub Issue**: #38 - https://github.com/bdperkin/nhl-scrabble/issues/38

## Priority

**CRITICAL** - Must Do (Next Sprint)

## Estimated Effort

2-4 hours

## Description

The `Config.from_env()` method in `src/nhl_scrabble/config.py` lacks proper validation for environment variables. Invalid values (e.g., non-numeric strings for integer fields) will cause unhandled `ValueError` exceptions.

## Current State

```python
@classmethod
def from_env(cls) -> "Config":
    """Create config from environment variables."""
    return cls(
        api_timeout=int(os.getenv("NHL_SCRABBLE_API_TIMEOUT", "10")),
        api_retries=int(os.getenv("NHL_SCRABBLE_API_RETRIES", "3")),
        rate_limit_delay=float(os.getenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3")),
        top_players=int(os.getenv("NHL_SCRABBLE_TOP_PLAYERS", "20")),
        top_team_players=int(os.getenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5")),
        verbose=os.getenv("NHL_SCRABBLE_VERBOSE", "false").lower() == "true",
    )
```

**Issue**: If user sets `NHL_SCRABBLE_API_TIMEOUT=invalid`, the code crashes with unhandled `ValueError`.

## Proposed Solution

Add validation with helpful error messages:

```python
@classmethod
def from_env(cls) -> "Config":
    """Create config from environment variables."""
    def get_int(key: str, default: str, min_value: int = 0) -> int:
        """Get integer from env with validation."""
        value_str = os.getenv(key, default)
        try:
            value = int(value_str)
            if value < min_value:
                raise ValueError(f"{key} must be >= {min_value}, got {value}")
            return value
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"{key} must be a valid integer, got '{value_str}'") from e
            raise

    def get_float(key: str, default: str, min_value: float = 0.0) -> float:
        """Get float from env with validation."""
        value_str = os.getenv(key, default)
        try:
            value = float(value_str)
            if value < min_value:
                raise ValueError(f"{key} must be >= {min_value}, got {value}")
            return value
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError(f"{key} must be a valid number, got '{value_str}'") from e
            raise

    return cls(
        api_timeout=get_int("NHL_SCRABBLE_API_TIMEOUT", "10", min_value=1),
        api_retries=get_int("NHL_SCRABBLE_API_RETRIES", "3", min_value=0),
        rate_limit_delay=get_float("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3", min_value=0.0),
        top_players=get_int("NHL_SCRABBLE_TOP_PLAYERS", "20", min_value=1),
        top_team_players=get_int("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5", min_value=1),
        verbose=os.getenv("NHL_SCRABBLE_VERBOSE", "false").lower() == "true",
    )
```

## Testing Strategy

Add unit tests in `tests/unit/test_config.py`:

```python
import pytest
import os
from nhl_scrabble.config import Config

def test_from_env_invalid_timeout(monkeypatch):
    """Test Config.from_env() with invalid timeout."""
    monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "invalid")
    with pytest.raises(ValueError, match="must be a valid integer"):
        Config.from_env()

def test_from_env_negative_timeout(monkeypatch):
    """Test Config.from_env() with negative timeout."""
    monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "-5")
    with pytest.raises(ValueError, match="must be >= 1"):
        Config.from_env()

def test_from_env_invalid_rate_limit(monkeypatch):
    """Test Config.from_env() with invalid rate limit."""
    monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "not_a_number")
    with pytest.raises(ValueError, match="must be a valid number"):
        Config.from_env()

def test_from_env_valid_values(monkeypatch):
    """Test Config.from_env() with valid values."""
    monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "30")
    monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "5")
    monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.5")
    config = Config.from_env()
    assert config.api_timeout == 30
    assert config.api_retries == 5
    assert config.rate_limit_delay == 0.5
```

## Acceptance Criteria

- [ ] Invalid integer values raise `ValueError` with clear message
- [ ] Invalid float values raise `ValueError` with clear message
- [ ] Negative values are rejected for fields that require positive values
- [ ] Zero is allowed for retries and rate_limit_delay
- [ ] All validation has unit tests with 100% coverage
- [ ] Error messages include the environment variable name and invalid value
- [ ] Documentation updated with environment variable constraints

## Related Files

- `src/nhl_scrabble/config.py`
- `tests/unit/test_config.py`
- `README.md` (environment variables section)

## Dependencies

None - standalone fix
