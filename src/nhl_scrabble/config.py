"""Configuration management for NHL Scrabble."""

# ruff: noqa: RUF100

import logging
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from nhl_scrabble.security.ssrf_protection import SSRFProtectionError, validate_api_base_url

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration.

    Attributes:
        api_base_url: Base URL for NHL API (validated with SSRF protection)
        api_timeout: Request timeout in seconds for NHL API calls
        api_retries: Number of retry attempts for failed API requests
        rate_limit_delay: Delay in seconds between API requests
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
    rate_limit_delay: float = 0.3
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
        """Load configuration from environment variables with validation.

        Environment variables:
            NHL_SCRABBLE_API_BASE_URL: Base URL for NHL API (must be HTTPS, validated for SSRF)
            NHL_SCRABBLE_API_TIMEOUT: API request timeout in seconds (must be >= 1)
            NHL_SCRABBLE_API_RETRIES: Number of API retry attempts (must be >= 0)
            NHL_SCRABBLE_RATE_LIMIT_DELAY: Delay between API requests (must be >= 0.0)
            NHL_SCRABBLE_BACKOFF_FACTOR: Exponential backoff multiplier (must be >= 1.0)
            NHL_SCRABBLE_MAX_BACKOFF: Maximum backoff delay in seconds (must be >= 1.0)
            NHL_SCRABBLE_CACHE_ENABLED: Enable HTTP caching (true/false)
            NHL_SCRABBLE_CACHE_EXPIRY: Cache expiration in seconds (must be >= 1)
            NHL_SCRABBLE_MAX_CONCURRENT: Max concurrent API requests (must be >= 1)
            NHL_SCRABBLE_TOP_PLAYERS: Number of top players to show (must be >= 1)
            NHL_SCRABBLE_TOP_TEAM_PLAYERS: Number of top players per team (must be >= 1)
            NHL_SCRABBLE_VERBOSE: Enable verbose logging (true/false)
            NHL_SCRABBLE_OUTPUT_FORMAT: Output format (text/json/html)
            NHL_SCRABBLE_SANITIZE_LOGS: Sanitize sensitive data from logs (true/false)

        Returns:
            Config instance with values from environment

        Raises:
            ValueError: If any environment variable has an invalid value,
                including if API base URL fails SSRF protection validation

        Examples:
            >>> import os
            >>> os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "15"  # Setting is safe
            >>> config = Config.from_env()
            >>> config.api_timeout
            15
            >>> # Note: Reading should always use os.getenv() with default:
            >>> timeout = os.getenv("NHL_SCRABBLE_API_TIMEOUT", "10")  # Safe
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

        def get_int(key: str, default: str, min_value: int = 0) -> int:
            """Get integer from environment variable with validation.

            Args:
                key: Environment variable name
                default: Default value if variable not set
                min_value: Minimum allowed value

            Returns:
                Validated integer value

            Raises:
                ValueError: If value is not a valid integer or is below minimum
            """
            value_str = os.getenv(key, default)
            try:
                value = int(value_str)
            except ValueError as e:
                raise ValueError(f"{key} must be a valid integer, got '{value_str}'") from e

            if value < min_value:
                msg = f"{key} must be >= {min_value}, got {value}"
                raise ValueError(msg)
            return value

        def get_float(key: str, default: str, min_value: float = 0.0) -> float:
            """Get float from environment variable with validation.

            Args:
                key: Environment variable name
                default: Default value if variable not set
                min_value: Minimum allowed value

            Returns:
                Validated float value

            Raises:
                ValueError: If value is not a valid number or is below minimum
            """
            value_str = os.getenv(key, default)
            try:
                value = float(value_str)
            except ValueError as e:
                raise ValueError(f"{key} must be a valid number, got '{value_str}'") from e

            if value < min_value:
                msg = f"{key} must be >= {min_value}, got {value}"
                raise ValueError(msg)
            return value

        return cls(
            api_base_url=validated_url,
            api_timeout=get_int("NHL_SCRABBLE_API_TIMEOUT", "10", min_value=1),
            api_retries=get_int("NHL_SCRABBLE_API_RETRIES", "3", min_value=0),
            rate_limit_delay=get_float("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3", min_value=0.0),
            backoff_factor=get_float("NHL_SCRABBLE_BACKOFF_FACTOR", "2.0", min_value=1.0),
            max_backoff=get_float("NHL_SCRABBLE_MAX_BACKOFF", "30.0", min_value=1.0),
            cache_enabled=os.getenv("NHL_SCRABBLE_CACHE_ENABLED", "true").lower() == "true",
            cache_expiry=get_int("NHL_SCRABBLE_CACHE_EXPIRY", "3600", min_value=1),
            max_concurrent_requests=get_int("NHL_SCRABBLE_MAX_CONCURRENT", "5", min_value=1),
            top_players_count=get_int("NHL_SCRABBLE_TOP_PLAYERS", "20", min_value=1),
            top_team_players_count=get_int("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5", min_value=1),
            verbose=os.getenv("NHL_SCRABBLE_VERBOSE", "false").lower() == "true",
            output_format=os.getenv("NHL_SCRABBLE_OUTPUT_FORMAT", "text"),
            sanitize_logs=os.getenv("NHL_SCRABBLE_SANITIZE_LOGS", "true").lower() == "true",
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
            "rate_limit_delay": self.rate_limit_delay,
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
