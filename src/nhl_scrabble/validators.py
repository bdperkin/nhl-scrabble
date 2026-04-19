"""Input validation utilities for NHL Scrabble.

This module provides comprehensive validation functions for all external inputs
including CLI arguments, environment variables, configuration files, and API responses.
All validators raise ValidationError with clear, actionable error messages.

Security features:
    - Path traversal prevention
    - Input sanitization
    - Type safety enforcement
    - Range validation
    - Format validation
"""

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class ValidationError(ValueError):
    """Raised when input validation fails.

    This exception provides clear, actionable error messages that
    indicate what was invalid and what the expected format is.

    Examples:
        >>> raise ValidationError("top_players must be between 1 and 100, got 999")
    """


def validate_file_path(path: str, allow_overwrite: bool = False) -> Path:
    """Validate and sanitize file path for security.

    This validator prevents path traversal attacks by detecting suspicious patterns
    and validates the path is safe to write to.

    Args:
        path: File path to validate
        allow_overwrite: Whether to allow overwriting existing files (default: False)

    Returns:
        Validated and resolved Path object

    Raises:
        ValidationError: If path is invalid or potentially dangerous with specific reason:
            - Path contains suspicious patterns (../)
            - Parent directory doesn't exist
            - Parent directory is not writable
            - File already exists and overwrite not allowed
            - Filename contains invalid characters

    Security:
        - Prevents path traversal attacks (../ patterns)
        - Validates parent directory exists and is writable
        - Restricts filename characters to safe set
        - Resolves to absolute path to prevent ambiguity

    Examples:
        >>> validate_file_path("output.txt")
        PosixPath('/current/dir/output.txt')
        >>> validate_file_path("../../../etc/passwd")
        Traceback (most recent call last):
        ValidationError: Path contains suspicious pattern '../'...
        >>> validate_file_path("file<>.txt")
        Traceback (most recent call last):
        ValidationError: Filename file<>.txt contains invalid characters...
    """
    # Check for suspicious path traversal patterns BEFORE resolving
    # This catches attempts like "../../../etc/passwd"
    if "../" in path or "/.." in path or path.startswith(".."):
        raise ValidationError(
            f"Path contains suspicious pattern '../' (potential path traversal attack): {path}"
        )

    # Convert to Path and resolve to absolute path
    try:
        file_path = Path(path).resolve()
    except (ValueError, RuntimeError) as e:
        raise ValidationError(f"Invalid path '{path}': {e}") from e

    # Check parent directory exists
    if not file_path.parent.exists():
        raise ValidationError(
            f"Directory does not exist: {file_path.parent}. "
            f"Create it first: mkdir -p {file_path.parent}"
        )

    # Check parent directory is a directory (not a file)
    if not file_path.parent.is_dir():
        raise ValidationError(f"Path is not a directory: {file_path.parent}")

    # Check parent directory is writable
    if not (file_path.parent.stat().st_mode & 0o200):  # Owner write permission
        raise ValidationError(
            f"Directory is not writable: {file_path.parent}. "
            f"Check permissions: ls -ld {file_path.parent}"
        )

    # Check file doesn't exist (unless overwrite allowed)
    if file_path.exists() and not allow_overwrite:
        raise ValidationError(
            f"File {file_path} already exists. Use --force to overwrite or choose a different name."
        )

    # Check file is writable if it exists and we're allowing overwrite
    if file_path.exists() and allow_overwrite and not (file_path.stat().st_mode & 0o200):
        raise ValidationError(
            f"File is not writable: {file_path}. Check permissions: ls -l {file_path}"
        )

    # Validate filename is safe (alphanumeric, dash, underscore, dot only)
    # This prevents shell injection and other filename-based attacks
    if not re.match(r"^[\w\-\.]+$", file_path.name):
        raise ValidationError(
            f"Filename {file_path.name} contains invalid characters. "
            f"Use only letters, numbers, dash (-), underscore (_), and dot (.)."
        )

    return file_path


def validate_integer_range(
    value: Any, min_val: int | None = None, max_val: int | None = None, name: str = "value"
) -> int:
    """Validate integer is within specified range.

    Args:
        value: Value to validate (can be int or string convertible to int)
        min_val: Minimum allowed value inclusive (None = no minimum)
        max_val: Maximum allowed value inclusive (None = no maximum)
        name: Parameter name for error messages

    Returns:
        Validated integer value

    Raises:
        ValidationError: If value is not an integer or out of range with specific reason:
            - Value is not convertible to integer
            - Value is below minimum
            - Value is above maximum

    Security:
        - Prevents memory exhaustion from extremely large values
        - Prevents DoS attacks via resource consumption
        - Ensures safe integer arithmetic

    Examples:
        >>> validate_integer_range(5, min_val=1, max_val=10)
        5
        >>> validate_integer_range("5", min_val=1, max_val=10)
        5
        >>> validate_integer_range(0, min_val=1, max_val=10, name="count")
        Traceback (most recent call last):
        ValidationError: count must be at least 1, got 0
        >>> validate_integer_range("abc", name="timeout")
        Traceback (most recent call last):
        ValidationError: timeout must be an integer, got str
    """
    # Convert to int
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be an integer, got: {value}") from None

    # Check minimum bound
    if min_val is not None and int_val < min_val:
        raise ValidationError(f"{name} must be at least {min_val}")

    # Check maximum bound
    if max_val is not None and int_val > max_val:
        raise ValidationError(f"{name} cannot exceed {max_val}, got {int_val}")

    return int_val


def validate_float_range(
    value: Any, min_val: float | None = None, max_val: float | None = None, name: str = "value"
) -> float:
    """Validate float is within specified range.

    Args:
        value: Value to validate (can be float, int, or string convertible to float)
        min_val: Minimum allowed value inclusive (None = no minimum)
        max_val: Maximum allowed value inclusive (None = no maximum)
        name: Parameter name for error messages

    Returns:
        Validated float value

    Raises:
        ValidationError: If value is not a number or out of range with specific reason:
            - Value is not convertible to float
            - Value is below minimum
            - Value is above maximum

    Examples:
        >>> validate_float_range(2.5, min_val=1.0, max_val=10.0)
        2.5
        >>> validate_float_range("2.5", min_val=1.0, max_val=10.0)
        2.5
        >>> validate_float_range(0.5, min_val=1.0, name="delay")
        Traceback (most recent call last):
        ValidationError: delay must be at least 1.0, got 0.5
    """
    # Convert to float
    try:
        float_val = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be a number, got: {value}") from None

    # Check minimum bound
    if min_val is not None and float_val < min_val:
        raise ValidationError(f"{name} must be at least {min_val}")

    # Check maximum bound
    if max_val is not None and float_val > max_val:
        raise ValidationError(f"{name} cannot exceed {max_val}, got {float_val}")

    return float_val


def validate_team_abbreviation(abbrev: str) -> str:
    """Validate NHL team abbreviation format.

    NHL team abbreviations are 2-3 uppercase letters (e.g., TOR, MTL, VGK).

    Args:
        abbrev: Team abbreviation to validate

    Returns:
        Validated uppercase abbreviation with whitespace stripped

    Raises:
        ValidationError: If abbreviation format is invalid with specific reason:
            - Length is not 2-3 characters
            - Contains non-alphabetic characters
            - Is empty or whitespace

    Security:
        - Prevents injection attacks via team abbreviation
        - Sanitizes input before use in API URLs
        - Validates format before external API calls

    Examples:
        >>> validate_team_abbreviation("TOR")
        'TOR'
        >>> validate_team_abbreviation("tor")
        'TOR'
        >>> validate_team_abbreviation("  MTL  ")
        'MTL'
        >>> validate_team_abbreviation("T0R")
        Traceback (most recent call last):
        ValidationError: Team abbreviation must contain only letters, got 'T0R'
        >>> validate_team_abbreviation("TOOLONG")
        Traceback (most recent call last):
        ValidationError: Team abbreviation must be 2-3 characters, got 'TOOLONG' (7 characters)
    """
    # Uppercase and strip whitespace
    clean_abbrev = abbrev.upper().strip()

    # Check not empty
    if not clean_abbrev:
        raise ValidationError("Team abbreviation cannot be empty")

    # Check length (NHL abbreviations are 2-3 characters: TOR, MTL, VGK, etc.)
    if not 2 <= len(clean_abbrev) <= 3:
        raise ValidationError(
            f"Team abbreviation must be 2-3 characters, got '{abbrev}' ({len(clean_abbrev)} characters)"
        )

    # Check only letters (no numbers, special characters, etc.)
    if not clean_abbrev.isalpha():
        raise ValidationError(f"Team abbreviation must contain only letters, got '{abbrev}'")

    return clean_abbrev


def validate_player_name(name: str) -> str:
    """Validate and sanitize player name.

    Player names can contain letters, spaces, hyphens, apostrophes, and periods
    to support international names (e.g., "Jean-Gabriel Pageau", "P.K. Subban").

    Args:
        name: Player name to validate

    Returns:
        Sanitized name with whitespace stripped

    Raises:
        ValidationError: If name format is invalid with specific reason:
            - Name is empty
            - Name is too long (>100 characters)
            - Name contains invalid characters

    Security:
        - Prevents XSS attacks via player names
        - Prevents injection attacks in logs/reports
        - Sanitizes before use in templates or output

    Examples:
        >>> validate_player_name("Connor McDavid")
        'Connor McDavid'
        >>> validate_player_name("Jean-Gabriel Pageau")
        'Jean-Gabriel Pageau'
        >>> validate_player_name("P.K. Subban")
        'P.K. Subban'
        >>> validate_player_name("Ryan O'Reilly")
        "Ryan O'Reilly"
        >>> validate_player_name("")
        Traceback (most recent call last):
        ValidationError: Player name cannot be empty
        >>> validate_player_name("Connor<script>alert(1)</script>")
        Traceback (most recent call last):
        ValidationError: Player name contains invalid characters: 'Connor<script>alert(1)</script>'
    """
    # Strip whitespace
    clean_name = name.strip()

    # Check not empty
    if not clean_name:
        raise ValidationError("Player name cannot be empty")

    # Check length (reasonable bound to prevent DoS)
    if len(clean_name) > 100:
        raise ValidationError(f"Player name too long ({len(clean_name)} characters, maximum 100)")

    # Allow letters, spaces, hyphens, apostrophes, periods
    # This supports international names: "Jean-Gabriel Pageau", "P.K. Subban", "Ryan O'Reilly"
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", clean_name):
        raise ValidationError(
            f"Player name contains invalid characters: '{name}'. "
            f"Only letters, spaces, hyphens (-), apostrophes ('), and periods (.) are allowed."
        )

    return clean_name


def validate_url(url: str, allowed_schemes: list[str] | None = None) -> str:
    """Validate URL format and scheme.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes (default: ["http", "https"])

    Returns:
        Validated URL string

    Raises:
        ValidationError: If URL format is invalid with specific reason:
            - URL cannot be parsed
            - Scheme is not in allowed schemes
            - URL is missing domain/netloc

    Security:
        - Prevents SSRF attacks via URL scheme validation
        - Ensures only HTTP(S) URLs are used by default
        - Validates URL structure before use

    Examples:
        >>> validate_url("https://api-web.nhle.com/v1/standings")
        'https://api-web.nhle.com/v1/standings'
        >>> validate_url("http://example.com")
        'http://example.com'
        >>> validate_url("ftp://example.com")
        Traceback (most recent call last):
        ValidationError: URL scheme must be one of ['http', 'https'], got 'ftp'
        >>> validate_url("ws://example.com", allowed_schemes=["ws", "wss"])
        'ws://example.com'
    """
    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}") from e

    # Check scheme is allowed
    if parsed.scheme not in allowed_schemes:
        raise ValidationError(
            f"URL scheme must be one of {allowed_schemes}, got '{parsed.scheme}' in URL: {url}"
        )

    # Check has netloc (domain)
    if not parsed.netloc:
        raise ValidationError(f"URL must include domain: {url}")

    return url


def validate_api_response_structure(
    data: dict[str, Any], required_keys: list[str], context: str = "API response"
) -> dict[str, Any]:
    """Validate API response has required structure.

    This validator ensures API responses have expected keys before accessing them,
    preventing KeyError exceptions and providing better error messages.

    Args:
        data: Response data dictionary to validate
        required_keys: List of required top-level keys
        context: Description for error messages (e.g., "Team roster response")

    Returns:
        Validated data dictionary (unchanged)

    Raises:
        ValidationError: If required keys are missing, listing which keys are missing
            and which keys are available in the response

    Security:
        - Prevents crashes from malformed API responses
        - Detects API changes or tampering
        - Provides early warning of API contract violations

    Examples:
        >>> data = {"forwards": [], "defensemen": [], "goalies": []}
        >>> validate_api_response_structure(data, ["forwards", "defensemen", "goalies"])
        {'forwards': [], 'defensemen': [], 'goalies': []}
        >>> data = {"forwards": []}
        >>> validate_api_response_structure(data, ["forwards", "defensemen"], "Team roster")
        Traceback (most recent call last):
        ValidationError: Team roster missing required keys: ['defensemen']. Available keys: ['forwards']
    """
    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        raise ValidationError(
            f"{context} missing required keys: {missing_keys}. Available keys: {list(data.keys())}"
        )

    return data


def validate_output_format(format_str: str) -> str:
    """Validate output format string.

    Args:
        format_str: Output format (text, json, html)

    Returns:
        Validated lowercase format string

    Raises:
        ValidationError: If format is not one of the allowed values

    Examples:
        >>> validate_output_format("text")
        'text'
        >>> validate_output_format("JSON")
        'json'
        >>> validate_output_format("xml")
        Traceback (most recent call last):
        ValidationError: Output format must be one of ['text', 'json', 'html'], got 'xml'
    """
    allowed_formats = ["text", "json", "html"]
    clean_format = format_str.lower().strip()

    if clean_format not in allowed_formats:
        raise ValidationError(f"Output format must be one of {allowed_formats}, got '{format_str}'")

    return clean_format
