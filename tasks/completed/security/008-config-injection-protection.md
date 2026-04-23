# Protect Against Config Injection

**GitHub Issue**: #137 - https://github.com/bdperkin/nhl-scrabble/issues/137

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Protect configuration system against injection attacks where malicious values in environment variables or config files could compromise security.

Currently, configuration values are read from environment variables and used directly without validation. This creates risks:

- Command injection via config values used in shell commands
- Path traversal via file path configurations
- Code injection via values used in eval/exec
- SQL injection if database added later

Need to:

- Validate all config values with strict schemas
- Sanitize values before use
- Prevent dangerous characters in configs
- Add config validation layer
- Test injection scenarios

## Current State

```python
# src/nhl_scrabble/config.py
class Config:
    def __init__(self):
        # Direct environment variable usage without validation
        self.api_timeout = int(os.getenv("NHL_SCRABBLE_API_TIMEOUT", "10"))
        self.output_file = os.getenv("NHL_SCRABBLE_OUTPUT_FILE")  # No validation!
        self.rate_limit_delay = float(os.getenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3"))
```

**Vulnerabilities**:

```bash
# Command injection risk
export NHL_SCRABBLE_OUTPUT_FILE="report.json; rm -rf /"

# Path traversal risk
export NHL_SCRABBLE_OUTPUT_FILE="../../etc/passwd"

# Type confusion
export NHL_SCRABBLE_API_TIMEOUT="not_a_number"
```

## Proposed Solution

### 1. Config Value Validators

```python
# src/nhl_scrabble/config_validators.py
import re
from pathlib import Path
from typing import Any


class ConfigValidationError(ValueError):
    """Raised when config value fails validation."""

    pass


def validate_positive_int(value: str, min_val: int = 1, max_val: int = 3600) -> int:
    """Validate positive integer in range."""
    try:
        num = int(value)
    except ValueError:
        raise ConfigValidationError(f"Invalid integer: {value}")

    if not min_val <= num <= max_val:
        raise ConfigValidationError(f"Value {num} outside range [{min_val}, {max_val}]")

    return num


def validate_positive_float(
    value: str, min_val: float = 0.0, max_val: float = 60.0
) -> float:
    """Validate positive float in range."""
    try:
        num = float(value)
    except ValueError:
        raise ConfigValidationError(f"Invalid float: {value}")

    if not min_val <= num <= max_val:
        raise ConfigValidationError(f"Value {num} outside range [{min_val}, {max_val}]")

    return num


def validate_safe_path(value: str, must_exist: bool = False) -> Path:
    """Validate file path is safe."""
    # Remove dangerous characters
    if any(char in value for char in [";", "&", "|", "$", "`", "\n", "\r"]):
        raise ConfigValidationError(f"Unsafe characters in path: {value}")

    path = Path(value).resolve()

    # Prevent path traversal
    try:
        path.relative_to(Path.cwd())
    except ValueError:
        raise ConfigValidationError(f"Path outside working directory: {path}")

    if must_exist and not path.exists():
        raise ConfigValidationError(f"Path does not exist: {path}")

    return path


def validate_enum(value: str, allowed_values: set[str]) -> str:
    """Validate value is in allowed set."""
    if value not in allowed_values:
        raise ConfigValidationError(
            f"Invalid value '{value}'. Allowed: {allowed_values}"
        )
    return value
```

### 2. Secure Config Class

```python
# src/nhl_scrabble/config.py
from nhl_scrabble.config_validators import (
    validate_positive_int,
    validate_positive_float,
    validate_safe_path,
    validate_enum,
)


class Config:
    """Secure configuration with validation."""

    def __init__(self):
        # Validated integer configs
        self.api_timeout = self._get_int(
            "NHL_SCRABBLE_API_TIMEOUT",
            default=10,
            min_val=1,
            max_val=300,
        )

        self.api_retries = self._get_int(
            "NHL_SCRABBLE_API_RETRIES",
            default=3,
            min_val=0,
            max_val=10,
        )

        # Validated float configs
        self.rate_limit_delay = self._get_float(
            "NHL_SCRABBLE_RATE_LIMIT_DELAY",
            default=0.3,
            min_val=0.0,
            max_val=10.0,
        )

        # Validated path configs
        self.output_file = self._get_path(
            "NHL_SCRABBLE_OUTPUT_FILE",
            default=None,
            must_exist=False,
        )

        # Validated enum configs
        self.log_level = self._get_enum(
            "NHL_SCRABBLE_LOG_LEVEL",
            default="INFO",
            allowed={"DEBUG", "INFO", "WARNING", "ERROR"},
        )

    def _get_int(
        self,
        key: str,
        default: int,
        min_val: int,
        max_val: int,
    ) -> int:
        """Get validated integer config."""
        value = os.getenv(key)
        if value is None:
            return default

        return validate_positive_int(value, min_val, max_val)

    def _get_float(
        self,
        key: str,
        default: float,
        min_val: float,
        max_val: float,
    ) -> float:
        """Get validated float config."""
        value = os.getenv(key)
        if value is None:
            return default

        return validate_positive_float(value, min_val, max_val)

    def _get_path(
        self,
        key: str,
        default: Path | None,
        must_exist: bool,
    ) -> Path | None:
        """Get validated path config."""
        value = os.getenv(key)
        if value is None:
            return default

        return validate_safe_path(value, must_exist)

    def _get_enum(
        self,
        key: str,
        default: str,
        allowed: set[str],
    ) -> str:
        """Get validated enum config."""
        value = os.getenv(key, default)
        return validate_enum(value, allowed)
```

### 3. Pydantic Config Model (Alternative)

```python
from pydantic import BaseSettings, Field, validator
from pathlib import Path


class Config(BaseSettings):
    """Type-safe config with Pydantic validation."""

    api_timeout: int = Field(10, ge=1, le=300)
    api_retries: int = Field(3, ge=0, le=10)
    rate_limit_delay: float = Field(0.3, ge=0.0, le=10.0)
    output_file: Path | None = None
    log_level: str = Field("INFO", regex="^(DEBUG|INFO|WARNING|ERROR)$")

    @validator("output_file")
    def validate_output_path(cls, v):
        if v is None:
            return v

        # Prevent path traversal
        resolved = v.resolve()
        try:
            resolved.relative_to(Path.cwd())
        except ValueError:
            raise ValueError("Path outside working directory")

        return resolved

    class Config:
        env_prefix = "NHL_SCRABBLE_"
        case_sensitive = False
```

## Implementation Steps

1. Create `src/nhl_scrabble/config_validators.py`
1. Implement validators for each config type
1. Update `Config` class to use validators
1. Add validation error handling
1. Add tests for injection scenarios
1. Audit all config usage
1. Document safe config practices

## Testing Strategy

**Unit Tests**:

```python
def test_validate_int_rejects_injection():
    with pytest.raises(ConfigValidationError):
        validate_positive_int("10; rm -rf /")


def test_validate_path_prevents_traversal():
    with pytest.raises(ConfigValidationError):
        validate_safe_path("../../etc/passwd")


def test_validate_path_rejects_shell_chars():
    with pytest.raises(ConfigValidationError):
        validate_safe_path("file.txt; cat /etc/passwd")


def test_config_validates_env_vars():
    os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "not_a_number"

    with pytest.raises(ConfigValidationError):
        Config()
```

**Integration Tests**:

```bash
# Test config injection scenarios
export NHL_SCRABBLE_OUTPUT_FILE="../../../etc/passwd"
pytest tests/integration/test_config_security.py
```

## Acceptance Criteria

- [ ] Config validators implemented
- [ ] All config values validated
- [ ] Path traversal prevented
- [ ] Command injection prevented
- [ ] Type validation enforced
- [ ] Range validation enforced
- [ ] Enum validation for string configs
- [ ] Tests verify injection prevention
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/config_validators.py` - New module
- `src/nhl_scrabble/config.py` - Add validation
- `tests/unit/test_config_validators.py` - New tests
- `tests/integration/test_config_security.py` - Security tests

## Dependencies

- Optional: `pydantic` for advanced validation (already installed)
- No blocking dependencies

## Additional Notes

**Injection Types to Prevent**:

1. **Command Injection**: Shell metacharacters in configs
1. **Path Traversal**: `../` in file paths
1. **Code Injection**: Eval/exec with user input
1. **Type Confusion**: Non-numeric values for numbers

**Defense in Depth**:

- Validate at config load time
- Sanitize before use
- Use type hints for safety
- Principle of least privilege

**Performance**:

- Validation happens once at startup
- Negligible overhead
- Fail fast on invalid config

**Best Practices**:

- Allowlist valid values, don't blocklist bad ones
- Use strong types (int, float, Path, Enum)
- Validate ranges and formats
- Log validation failures

## Implementation Notes

*To be filled during implementation*
