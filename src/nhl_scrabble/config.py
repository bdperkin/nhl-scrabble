"""Configuration management for NHL Scrabble.

This module provides a unified configuration system using pydantic-settings that supports:
- Environment variables (NHL_SCRABBLE_*)
- .env files
- Default values
- Future: CLI arguments

Configuration precedence (highest to lowest):
1. CLI arguments (future)
2. Environment variables
3. .env file
4. Default values

All configuration values are validated for security and correctness.
"""

import logging
import os
from typing import Annotated, Any

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from nhl_scrabble.config_validators import (
    ConfigValidationError,
    validate_boolean,
    validate_enum,
    validate_positive_float,
    validate_positive_int,
)
from nhl_scrabble.security.ssrf_protection import SSRFProtectionError, validate_api_base_url

logger = logging.getLogger(__name__)


class Config(BaseSettings):  # type: ignore[misc]
    """Application configuration with unified settings management.

    Uses pydantic-settings for automatic environment variable loading and validation.
    Supports multiple configuration sources with clear precedence:
    1. CLI arguments (future)
    2. Environment variables (NHL_SCRABBLE_*)
    3. .env file
    4. Default values

    All values are validated for security and correctness using custom validators
    that protect against injection attacks, SSRF, and invalid values.

    Attributes:
        api_base_url: Base URL for NHL API (validated with SSRF protection)
        api_timeout: Request timeout in seconds for NHL API calls
        api_retries: Number of retry attempts for failed API requests
        rate_limit_max_requests: Maximum requests allowed per time window
        rate_limit_window: Time window for rate limiting in seconds
        backoff_factor: Exponential backoff multiplier for retries
        max_backoff: Maximum backoff delay in seconds
        cache_enabled: Enable HTTP caching for API responses
        cache_expiry: Cache expiration time in seconds
        max_concurrent_requests: Maximum number of concurrent API requests
        top_players_count: Number of top players to show in reports
        top_team_players_count: Number of top players per team to show
        verbose: Enable verbose logging
        output_format: Output format (text, json, html)
        sanitize_logs: Sanitize sensitive data from logs (disable only for debugging)
        dos_max_connections: Maximum number of connection pool connections (DoS prevention)
        dos_max_per_host: Maximum connections per host (DoS prevention)
        dos_circuit_breaker_threshold: Number of failures before circuit opens
        dos_circuit_breaker_timeout: Circuit breaker timeout in seconds

    Examples:
        >>> import os
        >>> os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "15"
        >>> config = Config()
        >>> config.api_timeout
        15

        >>> # Using from_env() for backward compatibility
        >>> config = Config.from_env()
        >>> config.api_timeout
        15
    """

    model_config = SettingsConfigDict(
        env_prefix="NHL_SCRABBLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env file
        # Disable automatic validation to use custom validators
        validate_assignment=True,
    )

    # API Configuration
    api_base_url: Annotated[
        str,
        Field(
            default="https://api-web.nhle.com/v1",
            description="Base URL for NHL API (must be HTTPS, validated for SSRF)",
        ),
    ]
    api_timeout: Annotated[
        int,
        Field(
            default=10,
            description="API timeout in seconds (1-300)",
        ),
    ]
    api_retries: Annotated[
        int,
        Field(
            default=3,
            description="Retry attempts (0-10)",
        ),
    ]

    # Rate Limiting
    rate_limit_max_requests: Annotated[
        int,
        Field(
            default=30,
            description="Maximum requests per time window (1-1000)",
        ),
    ]
    rate_limit_window: Annotated[
        float,
        Field(
            default=60.0,
            description="Time window for rate limiting in seconds (1.0-3600.0)",
        ),
    ]
    backoff_factor: Annotated[
        float,
        Field(
            default=2.0,
            description="Backoff multiplier (1.0-10.0)",
        ),
    ]
    max_backoff: Annotated[
        float,
        Field(
            default=30.0,
            description="Max backoff delay (1.0-300.0)",
        ),
    ]

    # Caching
    cache_enabled: Annotated[
        bool,
        Field(
            default=True,
            description="Enable caching (true/false)",
        ),
    ]
    cache_expiry: Annotated[
        int,
        Field(
            default=3600,
            description="Cache expiry seconds (1-86400)",
        ),
    ]

    # Concurrency
    max_concurrent_requests: Annotated[
        int,
        Field(
            default=5,
            description="Max concurrent API requests (1-50)",
        ),
    ]

    # Display Options
    top_players_count: Annotated[
        int,
        Field(
            default=20,
            description="Top players to show (1-1000)",
        ),
    ]
    top_team_players_count: Annotated[
        int,
        Field(
            default=5,
            description="Top players per team (1-100)",
        ),
    ]
    verbose: Annotated[
        bool,
        Field(
            default=False,
            description="Verbose logging (true/false)",
        ),
    ]
    output_format: Annotated[
        str,
        Field(
            default="text",
            description="Output format (text/json/html)",
        ),
    ]
    sanitize_logs: Annotated[
        bool,
        Field(
            default=True,
            description="Sanitize logs (true/false)",
        ),
    ]

    # DoS Protection
    dos_max_connections: Annotated[
        int,
        Field(
            default=10,
            description="Max connection pool connections (1-100)",
        ),
    ]
    dos_max_per_host: Annotated[
        int,
        Field(
            default=5,
            description="Max connections per host (1-50)",
        ),
    ]
    dos_circuit_breaker_threshold: Annotated[
        int,
        Field(
            default=5,
            description="Circuit breaker failure threshold (1-20)",
        ),
    ]
    dos_circuit_breaker_timeout: Annotated[
        float,
        Field(
            default=60.0,
            description="Circuit breaker timeout seconds (1.0-300.0)",
        ),
    ]

    @model_validator(mode="before")
    @classmethod
    def validate_env_values(cls, data: Any) -> Any:  # noqa: ANN401, C901, PLR0915
        """Validate environment variable values before pydantic processing.

        This validator runs before pydantic's built-in validation and uses our
        custom validators to check for injection attempts and invalid values.
        It maintains backward compatibility with the original Config.from_env()
        behavior and error messages.

        Args:
            data: Input data dictionary

        Returns:
            Validated and converted data dictionary

        Raises:
            ValueError: If any value fails validation with detailed error message
        """
        if not isinstance(data, dict):
            return data

        # Helper function to get env var with proper error context
        def get_int(
            key: str,
            env_var: str,
            default: int,
            min_value: int,
            max_value: int,
        ) -> int:
            """Get and validate integer from environment or data."""
            # Check if value is in data dict (from direct instantiation)
            if key in data:
                value = data[key]
                # If already an int and in range, return it
                if isinstance(value, int):
                    if not min_value <= value <= max_value:
                        raise ValueError(
                            f"{env_var}: Value {value} outside allowed range "
                            f"[{min_value}, {max_value}]"
                        )
                    return value
                # Convert to string for validation
                value_str = str(value)
            else:
                # Get from environment
                value_str = os.getenv(env_var, str(default))

            try:
                return validate_positive_int(value_str, min_val=min_value, max_val=max_value)
            except ConfigValidationError as e:
                raise ValueError(f"{env_var}: {e}") from e

        def get_float(
            key: str,
            env_var: str,
            default: float,
            min_value: float,
            max_value: float,
        ) -> float:
            """Get and validate float from environment or data."""
            if key in data:
                value = data[key]
                if isinstance(value, (int, float)):
                    value_float = float(value)
                    if not min_value <= value_float <= max_value:
                        raise ValueError(
                            f"{env_var}: Value {value} outside allowed range "
                            f"[{min_value}, {max_value}]"
                        )
                    return value_float
                value_str = str(value)
            else:
                value_str = os.getenv(env_var, str(default))

            try:
                return validate_positive_float(value_str, min_val=min_value, max_val=max_value)
            except ConfigValidationError as e:
                raise ValueError(f"{env_var}: {e}") from e

        def get_bool(key: str, env_var: str, default: bool) -> bool:
            """Get and validate boolean from environment or data."""
            if key in data:
                value = data[key]
                if isinstance(value, bool):
                    return value
                value_str = str(value)
            else:
                value_str = os.getenv(env_var, str(default).lower())

            try:
                return validate_boolean(value_str)
            except ConfigValidationError as e:
                raise ValueError(f"{env_var}: {e}") from e

        def get_enum(key: str, env_var: str, default: str, allowed: set[str]) -> str:
            """Get and validate enum from environment or data."""
            value_str = str(data[key]) if key in data else os.getenv(env_var, default)

            try:
                return validate_enum(value_str, allowed)
            except ConfigValidationError as e:
                raise ValueError(f"{env_var}: {e}") from e

        # Validate all fields using custom validators
        validated_data = {
            "api_timeout": get_int("api_timeout", "NHL_SCRABBLE_API_TIMEOUT", 10, 1, 300),
            "api_retries": get_int("api_retries", "NHL_SCRABBLE_API_RETRIES", 3, 0, 10),
            "rate_limit_max_requests": get_int(
                "rate_limit_max_requests", "NHL_SCRABBLE_RATE_LIMIT_MAX_REQUESTS", 30, 1, 1000
            ),
            "rate_limit_window": get_float(
                "rate_limit_window", "NHL_SCRABBLE_RATE_LIMIT_WINDOW", 60.0, 1.0, 3600.0
            ),
            "backoff_factor": get_float(
                "backoff_factor", "NHL_SCRABBLE_BACKOFF_FACTOR", 2.0, 1.0, 10.0
            ),
            "max_backoff": get_float("max_backoff", "NHL_SCRABBLE_MAX_BACKOFF", 30.0, 1.0, 300.0),
            "cache_enabled": get_bool(
                "cache_enabled", "NHL_SCRABBLE_CACHE_ENABLED", True  # noqa: FBT003
            ),
            "cache_expiry": get_int("cache_expiry", "NHL_SCRABBLE_CACHE_EXPIRY", 3600, 1, 86400),
            "max_concurrent_requests": get_int(
                "max_concurrent_requests", "NHL_SCRABBLE_MAX_CONCURRENT", 5, 1, 50
            ),
            "top_players_count": get_int(
                "top_players_count", "NHL_SCRABBLE_TOP_PLAYERS", 20, 1, 1000
            ),
            "top_team_players_count": get_int(
                "top_team_players_count", "NHL_SCRABBLE_TOP_TEAM_PLAYERS", 5, 1, 100
            ),
            "verbose": get_bool("verbose", "NHL_SCRABBLE_VERBOSE", False),  # noqa: FBT003
            "output_format": get_enum(
                "output_format", "NHL_SCRABBLE_OUTPUT_FORMAT", "text", {"text", "json", "html"}
            ),
            "sanitize_logs": get_bool(
                "sanitize_logs", "NHL_SCRABBLE_SANITIZE_LOGS", True  # noqa: FBT003
            ),
            "dos_max_connections": get_int(
                "dos_max_connections", "NHL_SCRABBLE_DOS_MAX_CONNECTIONS", 10, 1, 100
            ),
            "dos_max_per_host": get_int(
                "dos_max_per_host", "NHL_SCRABBLE_DOS_MAX_PER_HOST", 5, 1, 50
            ),
            "dos_circuit_breaker_threshold": get_int(
                "dos_circuit_breaker_threshold",
                "NHL_SCRABBLE_DOS_CIRCUIT_BREAKER_THRESHOLD",
                5,
                1,
                20,
            ),
            "dos_circuit_breaker_timeout": get_float(
                "dos_circuit_breaker_timeout",
                "NHL_SCRABBLE_DOS_CIRCUIT_BREAKER_TIMEOUT",
                60.0,
                1.0,
                300.0,
            ),
        }

        # Handle API base URL separately with SSRF validation
        if "api_base_url" in data:
            api_base_url = data["api_base_url"]
        else:
            api_base_url = os.getenv("NHL_SCRABBLE_API_BASE_URL", "https://api-web.nhle.com/v1")

        try:
            validated_data["api_base_url"] = validate_api_base_url(api_base_url)
        except SSRFProtectionError as e:
            logger.error(
                f"SSRF protection blocked API base URL '{api_base_url}': {e}. "
                "Only official NHL API domains are allowed for security."
            )
            raise ValueError(f"Invalid API base URL: {e}") from e

        return validated_data

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Provided for backward compatibility with existing code.
        Uses pydantic-settings to automatically load from environment
        variables and .env file with proper precedence.

        Returns:
            Config instance with validated values

        Raises:
            ValueError: If any configuration value is invalid

        Examples:
            >>> config = Config.from_env()
            >>> config.api_timeout >= 1
            True
        """
        return cls()

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration

        Examples:
            >>> config = Config()
            >>> config_dict = config.to_dict()
            >>> "api_timeout" in config_dict
            True
        """
        return self.model_dump()  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        """Return string representation of config.

        Returns:
            String representation

        Examples:
            >>> config = Config()
            >>> "Config" in repr(config)
            True
        """
        return f"Config({self.to_dict()})"
