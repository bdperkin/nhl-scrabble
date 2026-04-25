"""Integration tests for configuration security and injection prevention."""

import os

import pytest

from nhl_scrabble.config import Config


class TestConfigInjectionPrevention:
    """Test config loading prevents injection attacks."""

    def test_rejects_command_injection_in_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects command injection in API timeout."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "10; rm -rf /")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_TIMEOUT.*dangerous character"):
            Config.from_env()

    def test_rejects_command_injection_in_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects command injection in API retries."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "3 & cat /etc/passwd")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_RETRIES.*dangerous character"):
            Config.from_env()

    def test_rejects_command_injection_in_window(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects command injection in rate limit window."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_WINDOW", "60.0 | whoami")

        with pytest.raises(
            ValueError, match=r"NHL_SCRABBLE_RATE_LIMIT_WINDOW.*dangerous character"
        ):
            Config.from_env()

    def test_rejects_non_integer_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects non-integer timeout value."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "not_a_number")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_TIMEOUT.*Invalid integer"):
            Config.from_env()

    def test_rejects_non_float_window(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects non-float window value."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_WINDOW", "not_a_float")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_RATE_LIMIT_WINDOW.*Invalid float"):
            Config.from_env()

    def test_rejects_timeout_below_minimum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects timeout below minimum."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "0")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_TIMEOUT.*outside allowed range"):
            Config.from_env()

    def test_rejects_timeout_above_maximum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects timeout above maximum."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "500")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_TIMEOUT.*outside allowed range"):
            Config.from_env()

    def test_rejects_retries_below_minimum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects retries below minimum."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "-1")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_RETRIES.*outside allowed range"):
            Config.from_env()

    def test_rejects_retries_above_maximum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects retries above maximum."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "20")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_API_RETRIES.*outside allowed range"):
            Config.from_env()

    def test_rejects_window_below_minimum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects window below minimum."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_WINDOW", "0.5")

        with pytest.raises(
            ValueError, match=r"NHL_SCRABBLE_RATE_LIMIT_WINDOW.*outside allowed range"
        ):
            Config.from_env()

    def test_rejects_window_above_maximum(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects window above maximum."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_WINDOW", "5000.0")

        with pytest.raises(
            ValueError, match=r"NHL_SCRABBLE_RATE_LIMIT_WINDOW.*outside allowed range"
        ):
            Config.from_env()

    def test_rejects_invalid_output_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects invalid output format."""
        monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", "invalid_format")

        with pytest.raises(
            ValueError,
            match=r"NHL_SCRABBLE_OUTPUT_FORMAT.*Invalid value.*Allowed values",
        ):
            Config.from_env()

    def test_rejects_format_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects injection in output format."""
        monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", "json; rm -rf /")

        with pytest.raises(
            ValueError,
            match=r"NHL_SCRABBLE_OUTPUT_FORMAT.*dangerous character",
        ):
            Config.from_env()

    def test_rejects_invalid_boolean(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects invalid boolean value."""
        monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", "maybe")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_VERBOSE.*Invalid boolean"):
            Config.from_env()

    def test_rejects_boolean_injection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config rejects injection in boolean value."""
        monkeypatch.setenv("NHL_SCRABBLE_CACHE_ENABLED", "true; cat /etc/passwd")

        with pytest.raises(ValueError, match=r"NHL_SCRABBLE_CACHE_ENABLED.*dangerous character"):
            Config.from_env()


class TestConfigValidValues:
    """Test config accepts valid values."""

    def test_accepts_valid_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts valid timeout value."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "15")
        config = Config.from_env()
        assert config.api_timeout == 15

    def test_accepts_valid_retries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts valid retries value."""
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "5")
        config = Config.from_env()
        assert config.api_retries == 5

    def test_accepts_valid_window(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts valid window value."""
        monkeypatch.setenv("NHL_SCRABBLE_RATE_LIMIT_WINDOW", "120.0")
        config = Config.from_env()
        assert config.rate_limit_window == 120.0

    def test_accepts_valid_output_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts valid output format."""
        monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", "json")
        config = Config.from_env()
        assert config.output_format == "json"

    def test_accepts_output_format_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts output format in any case."""
        monkeypatch.setenv("NHL_SCRABBLE_OUTPUT_FORMAT", "JSON")
        config = Config.from_env()
        assert config.output_format == "json"

    def test_accepts_boolean_true_variations(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts various true boolean representations."""
        for value in ["true", "TRUE", "True", "1", "yes", "YES", "on", "ON"]:
            monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", value)
            config = Config.from_env()
            assert config.verbose is True

    def test_accepts_boolean_false_variations(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts various false boolean representations."""
        for value in ["false", "FALSE", "False", "0", "no", "NO", "off", "OFF"]:
            monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", value)
            config = Config.from_env()
            assert config.verbose is False

    def test_accepts_value_with_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts values with surrounding whitespace."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "  20  ")
        config = Config.from_env()
        assert config.api_timeout == 20

    def test_accepts_boundary_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config accepts values at boundaries."""
        # Minimum timeout
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "1")
        config = Config.from_env()
        assert config.api_timeout == 1

        # Maximum timeout
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "300")
        config = Config.from_env()
        assert config.api_timeout == 300

        # Minimum retries
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "0")
        config = Config.from_env()
        assert config.api_retries == 0

        # Maximum retries
        monkeypatch.setenv("NHL_SCRABBLE_API_RETRIES", "10")
        config = Config.from_env()
        assert config.api_retries == 10


class TestConfigDefaults:
    """Test config uses correct defaults when env vars not set."""

    def test_default_timeout(self) -> None:
        """Test default API timeout."""
        # Clear any env vars
        for key in list(os.environ):
            if key.startswith("NHL_SCRABBLE_"):
                del os.environ[key]

        config = Config.from_env()
        assert config.api_timeout == 10

    def test_default_retries(self) -> None:
        """Test default API retries."""
        config = Config.from_env()
        assert config.api_retries == 3

    def test_default_window(self) -> None:
        """Test default rate limit window."""
        config = Config.from_env()
        assert config.rate_limit_window == 60.0

    def test_default_output_format(self) -> None:
        """Test default output format."""
        config = Config.from_env()
        assert config.output_format == "text"

    def test_default_verbose(self) -> None:
        """Test default verbose setting."""
        config = Config.from_env()
        assert config.verbose is False

    def test_default_cache_enabled(self) -> None:
        """Test default cache enabled setting."""
        config = Config.from_env()
        assert config.cache_enabled is True


class TestRangeValidation:
    """Test comprehensive range validation."""

    def test_timeout_min_boundary(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test timeout minimum boundary validation."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "1")
        config = Config.from_env()
        assert config.api_timeout == 1

    def test_timeout_max_boundary(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test timeout maximum boundary validation."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "300")
        config = Config.from_env()
        assert config.api_timeout == 300

    def test_cache_expiry_range(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cache expiry range validation."""
        # Valid value
        monkeypatch.setenv("NHL_SCRABBLE_CACHE_EXPIRY", "7200")
        config = Config.from_env()
        assert config.cache_expiry == 7200

        # Above maximum
        monkeypatch.setenv("NHL_SCRABBLE_CACHE_EXPIRY", "100000")
        with pytest.raises(ValueError, match=r"outside allowed range"):
            Config.from_env()

    def test_top_players_range(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test top players count range validation."""
        # Valid value
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "50")
        config = Config.from_env()
        assert config.top_players_count == 50

        # Above maximum
        monkeypatch.setenv("NHL_SCRABBLE_TOP_PLAYERS", "2000")
        with pytest.raises(ValueError, match=r"outside allowed range"):
            Config.from_env()
