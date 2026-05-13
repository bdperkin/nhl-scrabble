"""Unit tests for basic configuration management."""

import pytest

from nhl_scrabble.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_config_defaults(self) -> None:
        """Test Config with default values."""
        config = Config()
        assert config.api_timeout == 10
        assert config.api_retries == 3
        assert config.rate_limit_max_requests == 30
        assert config.rate_limit_window == 60.0
        assert config.max_concurrent_requests == 5
        assert config.top_players_count == 20
        assert config.top_team_players_count == 5
        assert config.verbose is False
        assert config.output_format == "text"

    def test_config_custom_values(self) -> None:
        """Test Config with custom values."""
        config = Config(
            api_timeout=30,
            api_retries=5,
            rate_limit_max_requests=50,
            rate_limit_window=120.0,
            max_concurrent_requests=10,
            top_players_count=50,
            top_team_players_count=10,
            verbose=True,
            output_format="json",
        )
        assert config.api_timeout == 30
        assert config.api_retries == 5
        assert config.rate_limit_max_requests == 50
        assert config.rate_limit_window == 120.0
        assert config.max_concurrent_requests == 10
        assert config.top_players_count == 50
        assert config.top_team_players_count == 10
        assert config.verbose is True
        assert config.output_format == "json"

    def test_to_dict(self) -> None:
        """Test Config.to_dict() method."""
        config = Config(api_timeout=15, verbose=True)
        config_dict = config.to_dict()
        assert config_dict["api_timeout"] == 15
        assert config_dict["verbose"] is True
        assert config_dict["api_retries"] == 3  # default

    def test_repr(self) -> None:
        """Test Config.__repr__() method."""
        config = Config()
        repr_str = repr(config)
        assert "Config(" in repr_str
        assert "api_timeout" in repr_str


class TestConfigLogging:
    """Tests for Config logging configuration fields."""

    def test_config_logging_defaults(self) -> None:
        """Test Config logging fields have correct default values."""
        config = Config()
        assert config.log_file is None
        assert config.log_max_bytes == 10485760  # 10MB
        assert config.log_backup_count == 5

    def test_config_logging_custom_values(self) -> None:
        """Test Config with custom logging values."""
        config = Config(
            log_file="logs/app.log",
            log_max_bytes=20971520,  # 20MB
            log_backup_count=10,
        )
        assert config.log_file == "logs/app.log"
        assert config.log_max_bytes == 20971520
        assert config.log_backup_count == 10

    def test_logging_config_in_to_dict(self) -> None:
        """Test that logging config fields appear in to_dict()."""
        config = Config(log_file="logs/app.log", log_max_bytes=20971520, log_backup_count=10)
        config_dict = config.to_dict()

        assert "log_file" in config_dict
        assert "log_max_bytes" in config_dict
        assert "log_backup_count" in config_dict
        assert config_dict["log_file"] == "logs/app.log"
        assert config_dict["log_max_bytes"] == 20971520
        assert config_dict["log_backup_count"] == 10
