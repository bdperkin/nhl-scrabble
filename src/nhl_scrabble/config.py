"""Configuration management for NHL Scrabble."""

# ruff: noqa: RUF100

import logging
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from nhl_scrabble.security.ssrf_protection import SSRFProtectionError, validate_api_base_url
from nhl_scrabble.validators import (
    validate_float_range,
    validate_integer_range,
    validate_output_format,
)

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
        """Load configuration from environment variables with comprehensive validation.

        Uses validators from validators module to ensure all configuration values
        are within safe, reasonable bounds to prevent DoS attacks and invalid states.
        Also validates API base URL with SSRF protection.

        Environment variables:
            NHL_SCRABBLE_API_BASE_URL: Base URL for NHL API (must be HTTPS, validated for SSRF)
            NHL_SCRABBLE_API_TIMEOUT: API timeout in seconds (1-300, default: 10)
            NHL_SCRABBLE_API_RETRIES: Retry attempts (0-10, default: 3)
            NHL_SCRABBLE_RATE_LIMIT_DELAY: Delay between requests (0.0-60.0, default: 0.3)
            NHL_SCRABBLE_BACKOFF_FACTOR: Backoff multiplier (1.0-10.0, default: 2.0)
            NHL_SCRABBLE_MAX_BACKOFF: Max backoff delay (1.0-300.0, default: 30.0)
            NHL_SCRABBLE_CACHE_ENABLED: Enable caching (true/false, default: true)
            NHL_SCRABBLE_CACHE_EXPIRY: Cache expiry seconds (1-86400, default: 3600)
            NHL_SCRABBLE_MAX_CONCURRENT: Max concurrent API requests (must be >= 1)
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

        # Validate API timeout (1-300 seconds)
        api_timeout = validate_integer_range(
            os.getenv("NHL_SCRABBLE_API_TIMEOUT", "10"),
            min_val=1,
            max_val=300,
            name="NHL_SCRABBLE_API_TIMEOUT",
        )

        # Validate API retries (0-10 attempts)
        api_retries = validate_integer_range(
            os.getenv("NHL_SCRABBLE_API_RETRIES", "3"),
            min_val=0,
            max_val=10,
            name="NHL_SCRABBLE_API_RETRIES",
        )

        # Validate rate limit delay (0.0-60.0 seconds)
        rate_limit_delay = validate_float_range(
            os.getenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3"),
            min_val=0.0,
            max_val=60.0,
            name="NHL_SCRABBLE_RATE_LIMIT_DELAY",
        )

        # Validate backoff factor (1.0-10.0)
        backoff_factor = validate_float_range(
            os.getenv("NHL_SCRABBLE_BACKOFF_FACTOR", "2.0"),
            min_val=1.0,
            max_val=10.0,
            name="NHL_SCRABBLE_BACKOFF_FACTOR",
        )

        # Validate max backoff (1.0-300.0 seconds)
        max_backoff = validate_float_range(
            os.getenv("NHL_SCRABBLE_MAX_BACKOFF", "30.0"),
            min_val=1.0,
            max_val=300.0,
            name="NHL_SCRABBLE_MAX_BACKOFF",
        )

        # Validate cache expiry (1-86400 seconds = 1 day max)
        cache_expiry = validate_integer_range(
            os.getenv("NHL_SCRABBLE_CACHE_EXPIRY", "3600"),
            min_val=1,
            max_val=86400,
            name="NHL_SCRABBLE_CACHE_EXPIRY",
        )

        # Validate top players count (1-100)
        top_players_count = validate_integer_range(
            os.getenv("NHL_SCRABBLE_TOP_PLAYERS", "20"),
            min_val=1,
            max_val=100,
            name="NHL_SCRABBLE_TOP_PLAYERS",
        )

        # Validate top team players count (1-50)
        top_team_players_count = validate_integer_range(
            os.getenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5"),
            min_val=1,
            max_val=50,
            name="NHL_SCRABBLE_TOP_TEAM_PLAYERS",
        )

        # Validate max concurrent requests (1-50)
        max_concurrent_requests = validate_integer_range(
            os.getenv("NHL_SCRABBLE_MAX_CONCURRENT", "5"),
            min_val=1,
            max_val=50,
            name="NHL_SCRABBLE_MAX_CONCURRENT",
        )

        # Validate output format
        output_format = validate_output_format(os.getenv("NHL_SCRABBLE_OUTPUT_FORMAT", "text"))

        # Boolean values (true/false)
        cache_enabled = os.getenv("NHL_SCRABBLE_CACHE_ENABLED", "true").lower() == "true"
        verbose = os.getenv("NHL_SCRABBLE_VERBOSE", "false").lower() == "true"
        sanitize_logs = os.getenv("NHL_SCRABBLE_SANITIZE_LOGS", "true").lower() == "true"

        return cls(
            api_base_url=validated_url,
            api_timeout=api_timeout,
            api_retries=api_retries,
            rate_limit_delay=rate_limit_delay,
            backoff_factor=backoff_factor,
            max_backoff=max_backoff,
            cache_enabled=cache_enabled,
            cache_expiry=cache_expiry,
            max_concurrent_requests=max_concurrent_requests,
            top_players_count=top_players_count,
            top_team_players_count=top_team_players_count,
            verbose=verbose,
            output_format=output_format,
            sanitize_logs=sanitize_logs,
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
