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
                raise ValueError(
                    f"{key} must be a valid integer, got '{value_str}'"
                ) from e
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
                raise ValueError(
                    f"{key} must be a valid number, got '{value_str}'"
                ) from e
            raise

    return cls(
        api_timeout=get_int("NHL_SCRABBLE_API_TIMEOUT", "10", min_value=1),
        api_retries=get_int("NHL_SCRABBLE_API_RETRIES", "3", min_value=0),
        rate_limit_delay=get_float(
            "NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3", min_value=0.0
        ),
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

- [x] Invalid integer values raise `ValueError` with clear message
- [x] Invalid float values raise `ValueError` with clear message
- [x] Negative values are rejected for fields that require positive values
- [x] Zero is allowed for retries and rate_limit_delay
- [x] All validation has unit tests with 100% coverage
- [x] Error messages include the environment variable name and invalid value
- [x] Documentation updated with environment variable constraints

## Related Files

- `src/nhl_scrabble/config.py`
- `tests/unit/test_config.py`
- `README.md` (environment variables section)

## Dependencies

None - standalone fix

## Implementation Notes

**Implemented**: 2026-04-16
**Branch**: bug-fixes/001-config-validation
**PR**: #72 - https://github.com/bdperkin/nhl-scrabble/pull/72
**Commits**: 1 commit (e9982d8)

### Actual Implementation

Followed the proposed solution with minor improvements to comply with ruff's ALL rules:

- Implemented `get_int()` helper function with validation
- Implemented `get_float()` helper function with validation
- Restructured validation to avoid TRY301 (abstract raise to inner function)
- Added comprehensive error messages with variable names and invalid values
- Enhanced docstrings with validation constraints documentation
- Created 26 comprehensive unit tests covering all edge cases

### Challenges Encountered

1. **Ruff TRY301 error**: Initial implementation had raise statements inside try-except blocks

   - Solution: Restructured to separate type conversion from range validation
   - Moved int/float conversion to try block, then validated min_value separately

1. **Ruff PT011 error**: Tests needed specific match patterns for pytest.raises()

   - Solution: Added regex match patterns to all pytest.raises() calls
   - Used raw strings (r"...") to avoid RUF043 metacharacter warning

1. **Black auto-formatting**: Pre-commit hook reformatted files during commit

   - Solution: Re-staged formatted files and committed again
   - All 55 pre-commit hooks passed on second attempt

### Deviations from Plan

Minor improvements to error handling:

- Simplified error checking logic (removed string matching for error types)
- Used exception chaining consistently with "from e" syntax
- Validated minimum values separately from type conversion for cleaner code flow

### Actual vs Estimated Effort

- **Estimated**: 2-4h
- **Actual**: ~3h
- **Breakdown**:
  - Implementation: 30 minutes
  - Testing: 1 hour
  - Fixing ruff errors: 1 hour
  - CI/CD and PR: 30 minutes

### Related PRs

- PR #72 - Main implementation (merged)

### Lessons Learned

1. Ruff's ALL rules catch subtle code quality issues (TRY301, PT011, RUF043)
1. Separating validation concerns (type vs range) leads to cleaner error handling
1. pytest.raises() should always include match parameter for precise error checking
1. Pre-commit hooks may reformat code, requiring re-staging before commit
1. 100% test coverage is achievable with comprehensive edge case testing

### Test Coverage

- **config.py**: 100% coverage (41 statements, 8 branches)
- **Total tests**: 26 unit tests
- **Test categories**:
  - Config initialization (4 tests)
  - Valid environment variables (2 tests)
  - Invalid type conversions (5 tests)
  - Negative value validation (5 tests)
  - Zero value edge cases (3 tests)
  - Error message format (2 tests)
  - Boolean verbose flag variations (2 tests)
  - Miscellaneous (3 tests)
