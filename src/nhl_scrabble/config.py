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
        """Load configuration from environment variables.

        Environment variables:
            NHL_SCRABBLE_API_TIMEOUT: API request timeout in seconds
            NHL_SCRABBLE_API_RETRIES: Number of API retry attempts
            NHL_SCRABBLE_RATE_LIMIT_DELAY: Delay between API requests
            NHL_SCRABBLE_TOP_PLAYERS: Number of top players to show
            NHL_SCRABBLE_TOP_TEAM_PLAYERS: Number of top players per team
            NHL_SCRABBLE_VERBOSE: Enable verbose logging (true/false)
            NHL_SCRABBLE_OUTPUT_FORMAT: Output format (text/json/html)

        Returns:
            Config instance with values from environment

        Examples:
            >>> import os
            >>> os.environ["NHL_SCRABBLE_API_TIMEOUT"] = "15"
            >>> config = Config.from_env()
            >>> config.api_timeout
            15
        """
        # Load .env file if it exists
        load_dotenv()

        return cls(
            api_timeout=int(os.getenv("NHL_SCRABBLE_API_TIMEOUT", "10")),
            api_retries=int(os.getenv("NHL_SCRABBLE_API_RETRIES", "3")),
            rate_limit_delay=float(os.getenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.3")),
            top_players_count=int(os.getenv("NHL_SCRABBLE_TOP_PLAYERS", "20")),
            top_team_players_count=int(os.getenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "5")),
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
