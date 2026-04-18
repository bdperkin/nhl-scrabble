"""Configuration management for NHL Scrabble."""

# ruff: noqa: RUF100

import logging
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from nhl_scrabble.config_validators import (
    ConfigValidationError,
    validate_boolean,
    validate_enum,
    validate_positive_float,
    validate_positive_int,
)
from nhl_scrabble.security.ssrf_protection import SSRFProtectionError, validate_api_base_url

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration.

    Attributes:
        api_base_url: Base URL for NHL API (validated with SSRF protection)
        api_timeout: Request timeout in seconds for NHL API calls
        api_retries: Number of retry attempts for failed API requests
        rate_limit_max_requests: Maximum requests allowed per time window
        rate_limit_window: Time window for rate limiting in seconds
        cache_enabled: Enable HTTP caching for API responses
        cache_expiry: Cache expiration time in seconds
        max_concurrent_requests: Maximum number of concurrent API requests
        top_players_count: Number of top players to show in reports
        top_team_players_count: Number of top players per team to show
        verbose: Enable verbose logging
        output_format: Output format (text, json, html)
        sanitize_logs: Sanitize sensitive data from logs (disable only for debugging)
    """

    api_base_url: str = "https://api-web.nhle.com/v1"
    api_timeout: int = 10
    api_retries: int = 3
    rate_limit_max_requests: int = 30
    rate_limit_window: float = 60.0
    backoff_factor: float = 2.0
    max_backoff: float = 30.0
    cache_enabled: bool = True
    cache_expiry: int = 3600
    max_concurrent_requests: int = 5
    top_players_count: int = 20
    top_team_players_count: int = 5
    verbose: bool = False
    output_format: str = "text"
    sanitize_logs: bool = True

    @classmethod
    def from_env(cls) -> "Config":  # noqa: C901
        """Load configuration from environment variables with comprehensive validation.

        Uses validators from config_validators module to ensure all configuration values
        are within safe, reasonable bounds to prevent DoS attacks and invalid states.
        Also validates API base URL with SSRF protection.

        Environment variables:
            NHL_SCRABBLE_API_BASE_URL: Base URL for NHL API (must be HTTPS, validated for SSRF)
            NHL_SCRABBLE_API_TIMEOUT: API timeout in seconds (1-300, default: 10)
            NHL_SCRABBLE_API_RETRIES: Retry attempts (0-10, default: 3)
            NHL_SCRABBLE_RATE_LIMIT_MAX_REQUESTS: Maximum requests per time window (1-1000, default: 30)
            NHL_SCRABBLE_RATE_LIMIT_WINDOW: Time window for rate limiting in seconds (1.0-3600.0, default: 60.0)
            NHL_SCRABBLE_BACKOFF_FACTOR: Backoff multiplier (1.0-10.0, default: 2.0)
            NHL_SCRABBLE_MAX_BACKOFF: Max backoff delay (1.0-300.0, default: 30.0)
            NHL_SCRABBLE_CACHE_ENABLED: Enable caching (true/false, default: true)
            NHL_SCRABBLE_CACHE_EXPIRY: Cache expiry seconds (1-86400, default: 3600)
            NHL_SCRABBLE_MAX_CONCURRENT: Max concurrent API requests (1-50, default: 5)
            NHL_SCRABBLE_TOP_PLAYERS: Top players to show (1-100, default: 20)
            NHL_SCRABBLE_TOP_TEAM_PLAYERS: Top players per team (1-50, default: 5)
            NHL_SCRABBLE_VERBOSE: Verbose logging (true/false, default: false)
            NHL_SCRABBLE_OUTPUT_FORMAT: Output format (text/json/html, default: text)
            NHL_SCRABBLE_SANITIZE_LOGS: Sanitize logs (true/false, default: true)

        Returns:
            Config instance with validated values from environment

        Raises:
            ValueError: If any environment variable has an invalid value with specific
                error message indicating the problem and valid range
            SSRFProtectionError: If API base URL fails SSRF protection validation

        Security:
            - Validates API base URL with SSRF protection
            - Validates all numeric values have max bounds to prevent DoS
            - Validates output format to prevent injection
            - Validates boolean values
            - Provides clear error messages for invalid configuration

        Examples:
            >>> import os
            >>> os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "15"
            >>> config = Config.from_env()
            >>> config.api_timeout
            15
            >>> os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "99999"
            >>> Config.from_env()
            Traceback (most recent call last):
            ValueError: NHL_SCRABBLE_API_TIMEOUT cannot exceed 300, got 99999
        """
        # Load .env file if it exists
        load_dotenv()

        # Validate API base URL with SSRF protection
        api_base_url = os.getenv("NHL_SCRABBLE_API_BASE_URL", "https://api-web.nhle.com/v1")
        try:
            validated_url = validate_api_base_url(api_base_url)
        except SSRFProtectionError as e:
            logger.error(
                f"SSRF protection blocked API base URL '{api_base_url}': {e}. "
                "Only official NHL API domains are allowed for security."
            )
            raise ValueError(f"Invalid API base URL: {e}") from e

        def get_int(
            key: str,
            default: str,
            min_value: int = 0,
            max_value: int = 3600,
        ) -> int:
            """Get integer from environment variable with injection protection.

            Args:
                key: Environment variable name
                default: Default value if variable not set
                min_value: Minimum allowed value
                max_value: Maximum allowed value

            Returns:
                Validated integer value

            Raises:
                ValueError: If value is not a valid integer, contains injection attempts,
                    or is outside allowed range
            """
            value_str = os.getenv(key, default)
            try:
                return validate_positive_int(value_str, min_val=min_value, max_val=max_value)
            except ConfigValidationError as e:
                raise ValueError(f"{key}: {e}") from e

        def get_float(
            key: str,
            default: str,
            min_value: float = 0.0,
            max_value: float = 60.0,
        ) -> float:
            """Get float from environment variable with injection protection.

            Args:
                key: Environment variable name
                default: Default value if variable not set
                min_value: Minimum allowed value
                max_value: Maximum allowed value

            Returns:
                Validated float value

            Raises:
                ValueError: If value is not a valid float, contains injection attempts,
                    or is outside allowed range
            """
            value_str = os.getenv(key, default)
            try:
                return validate_positive_float(value_str, min_val=min_value, max_val=max_value)
            except ConfigValidationError as e:
                raise ValueError(f"{key}: {e}") from e

        def get_bool(key: str, default: str) -> bool:
            """Get boolean from environment variable with injection protection.

            Args:
                key: Environment variable name
                default: Default value if variable not set

            Returns:
                Validated boolean value

            Raises:
                ValueError: If value is not a valid boolean or contains injection attempts
            """
            value_str = os.getenv(key, default)
            try:
                return validate_boolean(value_str)
            except ConfigValidationError as e:
                raise ValueError(f"{key}: {e}") from e

        def get_enum(
            key: str,
            default: str,
            allowed_values: set[str],
        ) -> str:
            """Get enum value from environment variable with injection protection.

            Args:
                key: Environment variable name
                default: Default value if variable not set
                allowed_values: Set of allowed values

            Returns:
                Validated enum value (normalized to lowercase)

            Raises:
                ValueError: If value is not in allowed set or contains injection attempts
            """
            value_str = os.getenv(key, default)
            try:
                return validate_enum(value_str, allowed_values)
            except ConfigValidationError as e:
                raise ValueError(f"{key}: {e}") from e

        return cls(
            api_base_url=validated_url,
            api_timeout=get_int("NHL_SCRABBLE_API_TIMEOUT", "10", min_value=1, max_value=300),
            api_retries=get_int("NHL_SCRABBLE_API_RETRIES", "3", min_value=0, max_value=10),
            rate_limit_max_requests=get_int(
                "NHL_SCRABBLE_RATE_LIMIT_MAX_REQUESTS", "30", min_value=1, max_value=1000
            ),
            rate_limit_window=get_float(
                "NHL_SCRABBLE_RATE_LIMIT_WINDOW", "60.0", min_value=1.0, max_value=3600.0
            ),
            backoff_factor=get_float(
                "NHL_SCRABBLE_BACKOFF_FACTOR", "2.0", min_value=1.0, max_value=10.0
            ),
            max_backoff=get_float(
                "NHL_SCRABBLE_MAX_BACKOFF", "30.0", min_value=1.0, max_value=300.0
            ),
            cache_enabled=get_bool("NHL_SCRABBLE_CACHE_ENABLED", "true"),
            cache_expiry=get_int(
                "NHL_SCRABBLE_CACHE_EXPIRY", "3600", min_value=1, max_value=86400
            ),
            max_concurrent_requests=get_int(
                "NHL_SCRABBLE_MAX_CONCURRENT", "5", min_value=1, max_value=50
            ),
            top_players_count=get_int(
                "NHL_SCRABBLE_TOP_PLAYERS", "20", min_value=1, max_value=1000
            ),
            top_team_players_count=get_int(
                "NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5", min_value=1, max_value=100
            ),
            verbose=get_bool("NHL_SCRABBLE_VERBOSE", "false"),
            output_format=get_enum(
                "NHL_SCRABBLE_OUTPUT_FORMAT", "text", {"text", "json", "html"}
            ),
            sanitize_logs=get_bool("NHL_SCRABBLE_SANITIZE_LOGS", "true"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "api_base_url": self.api_base_url,
            "api_timeout": self.api_timeout,
            "api_retries": self.api_retries,
            "rate_limit_max_requests": self.rate_limit_max_requests,
            "rate_limit_window": self.rate_limit_window,
            "backoff_factor": self.backoff_factor,
            "max_backoff": self.max_backoff,
            "cache_enabled": self.cache_enabled,
            "cache_expiry": self.cache_expiry,
            "max_concurrent_requests": self.max_concurrent_requests,
            "top_players_count": self.top_players_count,
            "top_team_players_count": self.top_team_players_count,
            "verbose": self.verbose,
            "output_format": self.output_format,
            "sanitize_logs": self.sanitize_logs,
        }

    def __repr__(self) -> str:
        """Return string representation of config."""
        return f"Config({self.to_dict()})"
