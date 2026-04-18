"""Configuration value validators for injection protection.

This module provides validators to protect against:
- Command injection via shell metacharacters
- Path traversal attacks
- Type confusion attacks
- Range validation bypass
- Enum value injection

All validators follow the principle of fail-fast with clear error messages.
"""

import re
from pathlib import Path


class ConfigValidationError(ValueError):
    """Raised when configuration value fails validation."""


def validate_positive_int(
    value: str,
    min_val: int = 1,
    max_val: int = 3600,
) -> int:
    """Validate positive integer within specified range.

    Args:
        value: String value to validate and convert
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Validated integer value

    Raises:
        ConfigValidationError: If value is not a valid integer or outside range

    Examples:
        >>> validate_positive_int("10", min_val=1, max_val=100)
        10
        >>> validate_positive_int("10; rm -rf /", min_val=1, max_val=100)  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        ConfigValidationError: Invalid integer: 10; rm -rf /
    """
    # Strip whitespace to be lenient with user input
    value = value.strip()

    # Check for injection attempts via shell metacharacters
    dangerous_chars = [";", "&", "|", "$", "`", "\n", "\r", "\\", "<", ">"]
    for char in dangerous_chars:
        if char in value:
            raise ConfigValidationError(
                f"Invalid integer: {value!r} (contains dangerous character: {char!r})"
            )

    # Validate it's a valid integer
    try:
        num = int(value)
    except ValueError as e:
        raise ConfigValidationError(f"Invalid integer: {value!r}") from e

    # Validate range
    if not min_val <= num <= max_val:
        raise ConfigValidationError(f"Value {num} outside allowed range [{min_val}, {max_val}]")

    return num


def validate_positive_float(
    value: str,
    min_val: float = 0.0,
    max_val: float = 60.0,
) -> float:
    """Validate positive float within specified range.

    Args:
        value: String value to validate and convert
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        Validated float value

    Raises:
        ConfigValidationError: If value is not a valid float or outside range

    Examples:
        >>> validate_positive_float("0.5", min_val=0.0, max_val=10.0)
        0.5
        >>> validate_positive_float("1.5; cat /etc/passwd", min_val=0.0, max_val=10.0)
        ... # doctest: +SKIP
        Traceback (most recent call last):
        ...
        ConfigValidationError: Invalid float: '1.5; cat /etc/passwd' ...
    """
    # Strip whitespace
    value = value.strip()

    # Check for injection attempts
    dangerous_chars = [";", "&", "|", "$", "`", "\n", "\r", "\\", "<", ">"]
    for char in dangerous_chars:
        if char in value:
            raise ConfigValidationError(
                f"Invalid float: {value!r} (contains dangerous character: {char!r})"
            )

    # Validate it's a valid float
    try:
        num = float(value)
    except ValueError as e:
        raise ConfigValidationError(f"Invalid float: {value!r}") from e

    # Validate range
    if not min_val <= num <= max_val:
        raise ConfigValidationError(f"Value {num} outside allowed range [{min_val}, {max_val}]")

    return num


def validate_safe_path(
    value: str,
    must_exist: bool = False,
    allow_absolute: bool = False,
) -> Path:
    """Validate file path is safe from injection and traversal attacks.

    Args:
        value: Path string to validate
        must_exist: Whether path must already exist
        allow_absolute: Whether to allow absolute paths (default: False, relative only)

    Returns:
        Validated Path object

    Raises:
        ConfigValidationError: If path contains dangerous characters, traverses outside
            working directory, or doesn't exist when required

    Examples:
        >>> import tempfile
        >>> import os
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     os.chdir(tmpdir)
        ...     path = validate_safe_path("output/report.json")
        ...     str(path).endswith("output/report.json")
        True
        >>> validate_safe_path("../../etc/passwd")  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        ConfigValidationError: Path outside working directory: ...
    """
    # Check for shell metacharacters that could enable command injection
    dangerous_chars = [";", "&", "|", "$", "`", "\n", "\r"]
    for char in dangerous_chars:
        if char in value:
            raise ConfigValidationError(
                f"Unsafe characters in path: {value!r} (contains: {char!r})"
            )

    # Convert to Path and resolve
    try:
        path = Path(value)
    except (ValueError, TypeError) as e:
        raise ConfigValidationError(f"Invalid path format: {value!r}") from e

    # Check for absolute paths if not allowed
    if not allow_absolute and path.is_absolute():
        raise ConfigValidationError(
            f"Absolute paths not allowed: {value!r}. Use relative paths only."
        )

    # Resolve to absolute path for traversal checking
    try:
        resolved_path = path.resolve()
    except (OSError, RuntimeError) as e:
        raise ConfigValidationError(f"Cannot resolve path: {value!r}") from e

    # Prevent path traversal outside working directory
    # This is a defense-in-depth measure even for output files
    try:
        cwd = Path.cwd().resolve()
        resolved_path.relative_to(cwd)
    except ValueError as e:
        raise ConfigValidationError(
            f"Path outside working directory: {resolved_path} (working directory: {cwd})"
        ) from e

    # Check existence if required
    if must_exist and not resolved_path.exists():
        raise ConfigValidationError(f"Path does not exist: {resolved_path}")

    return resolved_path


def validate_enum(
    value: str,
    allowed_values: set[str],
    case_sensitive: bool = False,
) -> str:
    """Validate value is in allowed set.

    Args:
        value: String value to validate
        allowed_values: Set of allowed values
        case_sensitive: Whether comparison is case-sensitive

    Returns:
        Validated string value (in original case if case_sensitive=False,
        normalized to lowercase if case_sensitive=True)

    Raises:
        ConfigValidationError: If value is not in allowed set

    Examples:
        >>> validate_enum("json", {"text", "json", "html"})
        'json'
        >>> validate_enum("JSON", {"text", "json", "html"})
        'json'
        >>> validate_enum("xml", {"text", "json", "html"})  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        ConfigValidationError: Invalid value 'xml'. Allowed values: ...
    """
    # Strip whitespace
    value = value.strip()

    # Check for injection attempts
    dangerous_chars = [";", "&", "|", "$", "`", "\n", "\r", "\\", "<", ">"]
    for char in dangerous_chars:
        if char in value:
            raise ConfigValidationError(
                f"Invalid value {value!r} (contains dangerous character: {char!r})"
            )

    # Normalize case for comparison if not case-sensitive
    check_value = value if case_sensitive else value.lower()
    allowed_normalized = allowed_values if case_sensitive else {v.lower() for v in allowed_values}

    # Validate against allowed values
    if check_value not in allowed_normalized:
        allowed_display = ", ".join(sorted(allowed_values))
        raise ConfigValidationError(f"Invalid value {value!r}. Allowed values: {allowed_display}")

    # Return normalized value if case-insensitive
    return check_value if not case_sensitive else value


def validate_boolean(value: str) -> bool:
    """Validate and convert string to boolean.

    Args:
        value: String value to validate ("true", "false", "1", "0", "yes", "no", or empty string)

    Returns:
        Boolean value (empty string returns False)

    Raises:
        ConfigValidationError: If value is not a valid boolean representation

    Examples:
        >>> validate_boolean("true")
        True
        >>> validate_boolean("FALSE")
        False
        >>> validate_boolean("1")
        True
        >>> validate_boolean("yes")
        True
        >>> validate_boolean("")
        False
        >>> validate_boolean("maybe")  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        ConfigValidationError: Invalid boolean: 'maybe'. Allowed: true, false, 1, 0, yes, no
    """
    # Strip whitespace
    value = value.strip()

    # Empty string is treated as False (common default behavior)
    if not value:
        return False

    # Check for injection attempts
    dangerous_chars = [";", "&", "|", "$", "`", "\n", "\r", "\\", "<", ">"]
    for char in dangerous_chars:
        if char in value:
            raise ConfigValidationError(
                f"Invalid boolean: {value!r} (contains dangerous character: {char!r})"
            )

    # Normalize to lowercase
    normalized = value.lower()

    # Map of valid boolean representations
    true_values = {"true", "1", "yes", "y", "on"}
    false_values = {"false", "0", "no", "n", "off"}

    if normalized in true_values:
        return True
    if normalized in false_values:
        return False
    raise ConfigValidationError(
        f"Invalid boolean: {value!r}. "
        "Allowed: true, false, 1, 0, yes, no, on, off (empty string = false)"
    )


def validate_url(value: str, require_https: bool = True) -> str:
    """Validate URL format and security requirements.

    Args:
        value: URL string to validate
        require_https: Whether to require HTTPS protocol

    Returns:
        Validated URL string

    Raises:
        ConfigValidationError: If URL is invalid or doesn't meet security requirements

    Examples:
        >>> validate_url("https://api.example.com")
        'https://api.example.com'
        >>> validate_url("http://api.example.com", require_https=False)
        'http://api.example.com'
        >>> validate_url("http://api.example.com")  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        ConfigValidationError: URL must use HTTPS protocol: ...
    """
    # Strip whitespace
    value = value.strip()

    # Check for injection attempts
    dangerous_chars = [";", "&", "|", "$", "`", "\n", "\r", " ", "<", ">"]
    for char in dangerous_chars:
        if char in value:
            raise ConfigValidationError(
                f"Invalid URL: {value!r} (contains dangerous character: {char!r})"
            )

    # Basic URL format validation
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(value):
        raise ConfigValidationError(f"Invalid URL format: {value!r}")

    # Require HTTPS if specified
    if require_https and not value.startswith("https://"):
        raise ConfigValidationError(
            f"URL must use HTTPS protocol: {value!r} (HTTP is insecure for API communication)"
        )

    return value
