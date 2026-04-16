"""Unit tests for configuration management."""

import os

import pytest

from nhl_scrabble.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_config_defaults(self) -> None:
        """Test Config with default values."""
        config = Config()
        assert config.api_timeout == 10
        assert config.api_retries == 3
        assert config.rate_limit_delay == 0.3
        assert config.top_players_count == 20
        assert config.top_team_players_count == 5
        assert config.verbose is False
        assert config.output_format == "text"

    def test_config_custom_values(self) -> None:
        """Test Config with custom values."""
        config = Config(
            api_timeout=30,
            api_retries=5,
            rate_limit_delay=0.5,
            top_players_count=50,
            top_team_players_count=10,
            verbose=True,
            output_format="json",
        )
        assert config.api_timeout == 30
        assert config.api_retries == 5
        assert config.rate_limit_delay == 0.5
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


class TestConfigFromEnv:
    """Tests for Config.from_env() method."""

    def test_from_env_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with default values."""
        # Clear all NHL_SCRABBLE env vars
        for key in list(os.environ.keys()):
            if key.startswith("NHL_SCRABBLE_"):
                monkeypatch.delenv(key, raising=False)

        config = Config.from_env()
        assert config.api_timeout == 10
        assert config.api_retries == 3
        assert config.rate_limit_delay == 0.3
        assert config.top_players_count == 20
        assert config.top_team_players_count == 5
        assert config.verbose is False
        assert config.output_format == "text"

    def test_from_env_valid_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with valid custom values."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "30")
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "5")
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.5")
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "50")
        monkeypatch.setenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "10")
        monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", "true")
        monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", "json")

        config = Config.from_env()
        assert config.api_timeout == 30
        assert config.api_retries == 5
        assert config.rate_limit_delay == 0.5
        assert config.top_players_count == 50
        assert config.top_team_players_count == 10
        assert config.verbose is True
        assert config.output_format == "json"

    def test_from_env_invalid_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with invalid timeout."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "invalid")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_API_TIMEOUT must be a valid integer"):
            Config.from_env()

    def test_from_env_invalid_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with invalid retries."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "not_a_number")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_API_RETRIES must be a valid integer"):
            Config.from_env()

    def test_from_env_invalid_rate_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with invalid rate limit."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "not_a_number")
        with pytest.raises(
            ValueError, match="NHL_SCRABBLE_RATE_LIMIT_DELAY must be a valid number"
        ):
            Config.from_env()

    def test_from_env_invalid_top_players(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with invalid top_players."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "xyz")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_TOP_PLAYERS must be a valid integer"):
            Config.from_env()

    def test_from_env_invalid_top_team_players(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with invalid top_team_players."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "abc")
        with pytest.raises(
            ValueError, match="NHL_SCRABBLE_TOP_TEAM_PLAYERS must be a valid integer"
        ):
            Config.from_env()

    def test_from_env_negative_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with negative timeout."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "-5")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_API_TIMEOUT must be >= 1"):
            Config.from_env()

    def test_from_env_zero_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with zero timeout (invalid)."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "0")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_API_TIMEOUT must be >= 1"):
            Config.from_env()

    def test_from_env_negative_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with negative retries."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "-1")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_API_RETRIES must be >= 0"):
            Config.from_env()

    def test_from_env_zero_retries_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with zero retries (valid)."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "0")
        config = Config.from_env()
        assert config.api_retries == 0

    def test_from_env_negative_rate_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with negative rate limit."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "-0.5")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_RATE_LIMIT_DELAY must be >= 0"):
            Config.from_env()

    def test_from_env_zero_rate_limit_valid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with zero rate limit (valid)."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "0.0")
        config = Config.from_env()
        assert config.rate_limit_delay == 0.0

    def test_from_env_negative_top_players(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with negative top_players."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "-10")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_TOP_PLAYERS must be >= 1"):
            Config.from_env()

    def test_from_env_zero_top_players(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with zero top_players (invalid)."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "0")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_TOP_PLAYERS must be >= 1"):
            Config.from_env()

    def test_from_env_negative_top_team_players(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with negative top_team_players."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "-5")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_TOP_TEAM_PLAYERS must be >= 1"):
            Config.from_env()

    def test_from_env_zero_top_team_players(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with zero top_team_players (invalid)."""
        monkeypatch.setenv("NHL_SCRABBLE_TOP_TEAM_PLAYERS", "0")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_TOP_TEAM_PLAYERS must be >= 1"):
            Config.from_env()

    def test_from_env_verbose_true_variations(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with various true values for verbose."""
        for true_value in ["true", "True", "TRUE", "TrUe"]:
            monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", true_value)
            config = Config.from_env()
            assert config.verbose is True, f"Failed for value: {true_value}"

    def test_from_env_verbose_false_variations(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with various false values for verbose."""
        for false_value in ["false", "False", "FALSE", "no", "0", ""]:
            monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", false_value)
            config = Config.from_env()
            assert config.verbose is False, f"Failed for value: {false_value}"

    def test_from_env_float_as_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Config.from_env() with float value for rate_limit_delay."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "1.5")
        config = Config.from_env()
        assert config.rate_limit_delay == 1.5

    def test_from_env_error_message_includes_variable_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that error messages include the environment variable name."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "bad_value")
        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_TIMEOUT.*bad_value") as exc_info:
            Config.from_env()
        assert "NHL_SCRABBLE_API_TIMEOUT" in str(exc_info.value)
        assert "bad_value" in str(exc_info.value)

    def test_from_env_error_message_includes_invalid_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that error messages include the invalid value."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_DELAY", "invalid_float")
        with pytest.raises(
            ValueError, match=r"NHL_SCRABBLE_RATE_LIMIT_DELAY.*invalid_float"
        ) as exc_info:
            Config.from_env()
        assert "invalid_float" in str(exc_info.value)
