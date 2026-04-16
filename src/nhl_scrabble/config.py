"""Configuration management for NHL Scrabble."""

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration.

    Attributes:
        api_timeout: Request timeout in seconds for NHL API calls
        api_retries: Number of retry attempts for failed API requests
        rate_limit_delay: Delay in seconds between API requests
        top_players_count: Number of top players to show in reports
        top_team_players_count: Number of top players per team to show
        verbose: Enable verbose logging
        output_format: Output format (text, json, html)
    """

    api_timeout: int = 10
    api_retries: int = 3
    rate_limit_delay: float = 0.3
    top_players_count: int = 20
    top_team_players_count: int = 5
    verbose: bool = False
    output_format: str = "text"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables with validation.

        Environment variables:
            NHL_SCRABBLE_API_TIMEOUT: API request timeout in seconds (must be >= 1)
            NHL_SCRABBLE_API_RETRIES: Number of API retry attempts (must be >= 0)
            NHL_SCRABBLE_RATE_LIMIT_DELAY: Delay between API requests (must be >= 0.0)
            NHL_SCRABBLE_TOP_PLAYERS: Number of top players to show (must be >= 1)
            NHL_SCRABBLE_TOP_TEAM_PLAYERS: Number of top players per team (must be >= 1)
            NHL_SCRABBLE_VERBOSE: Enable verbose logging (true/false)
            NHL_SCRABBLE_OUTPUT_FORMAT: Output format (text/json/html)

        Returns:
            Config instance with values from environment

        Raises:
            ValueError: If any environment variable has an invalid value

        Examples:
            >>> import os
            >>> os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "15"
            >>> config = Config.from_env()
            >>> config.api_timeout
            15
        """
        # Load .env file if it exists
        load_dotenv()

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
            api_timeout=get_int("NHL_SCRABBLE_API_TIMEOUT", "10", min_value=1),
            api_retries=get_int("NHL_SCRABBLE_API_RETRIES", "3", min_value=0),
            rate_limit_delay=get_float("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3", min_value=0.0),
            top_players_count=get_int("NHL_SCRABBLE_TOP_PLAYERS", "20", min_value=1),
            top_team_players_count=get_int("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5", min_value=1),
            verbose=os.getenv("NHL_SCRABBLE_VERBOSE", "false").lower() == "true",
            output_format=os.getenv("NHL_SCRABBLE_OUTPUT_FORMAT", "text"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "api_timeout": self.api_timeout,
            "api_retries": self.api_retries,
            "rate_limit_delay": self.rate_limit_delay,
            "top_players_count": self.top_players_count,
            "top_team_players_count": self.top_team_players_count,
            "verbose": self.verbose,
            "output_format": self.output_format,
        }

    def __repr__(self) -> str:
        """Return string representation of config."""
        return f"Config({self.to_dict()})"
