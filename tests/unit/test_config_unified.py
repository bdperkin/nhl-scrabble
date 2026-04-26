"""Tests for unified configuration management with pydantic-settings.

This module tests the new unified configuration system that uses pydantic-settings
to consolidate configuration from multiple sources with clear precedence:
1. CLI arguments (future)
2. Environment variables
3. .env files
4. Default values
"""

import os
from pathlib import Path

import pytest

from nhl_scrabble.config import Config


class TestUnifiedConfig:
    """Tests for unified configuration management."""

    def test_config_uses_pydantic_settings(self) -> None:
        """Test that Config uses pydantic BaseSettings."""
        from pydantic_settings import BaseSettings

        assert issubclass(Config, BaseSettings), "Config should extend pydantic BaseSettings"

    def test_config_precedence_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that default values are used when no env vars are set."""
        # Clear all NHL_SCRABBLE env vars
        for key in list(os.environ.keys()):
            if key.startswith("NHL_SCRABBLE_"):
                monkeypatch.delenv(key, raising=False)

        config = Config()
        assert config.api_timeout == 10  # default
        assert config.verbose is False  # default
        assert config.output_format == "text"  # default

    def test_config_precedence_env_over_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables override defaults."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "25")
        monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", "true")

        config = Config()
        assert config.api_timeout == 25  # from env var
        assert config.verbose is True  # from env var
        assert config.output_format == "text"  # default (no env var set)

    def test_config_precedence_dotenv_file(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that .env file values are loaded (lowest precedence)."""
        # Create a .env file
        env_file = tmp_path / ".env"
        env_file.write_text(
            "NHL_SCRABBLE_API_TIMEOUT=20\n"
            "NHL_SCRABBLE_VERBOSE=true\n"
            "NHL_SCRABBLE_OUTPUT_FORMAT=json\n",
        )

        # Change to temp directory so .env is found
        monkeypatch.chdir(tmp_path)

        # Clear env vars
        for key in list(os.environ.keys()):
            if key.startswith("NHL_SCRABBLE_"):
                monkeypatch.delenv(key, raising=False)

        config = Config()
        # Values should come from .env file
        assert config.api_timeout == 20
        assert config.verbose is True
        assert config.output_format == "json"

    def test_config_precedence_env_over_dotenv(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that environment variables override .env file (correct precedence)."""
        # Create a .env file
        env_file = tmp_path / ".env"
        env_file.write_text("NHL_SCRABBLE_API_TIMEOUT=20\n" "NHL_SCRABBLE_VERBOSE=false\n")

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Set env var that should override .env file
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "35")

        config = Config()
        # ENV var should win over .env file
        assert config.api_timeout == 35  # from env var
        assert config.verbose is False  # from .env file

    def test_config_direct_instantiation(self) -> None:
        """Test that Config can be instantiated directly with values (highest precedence)."""
        # This simulates future CLI argument passing
        config = Config(
            api_timeout=50,
            verbose=True,
            output_format="json",
        )
        assert config.api_timeout == 50
        assert config.verbose is True
        assert config.output_format == "json"

    def test_config_direct_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that direct instantiation overrides environment variables."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "25")

        # Direct value should override env var (future CLI args use case)
        config = Config(api_timeout=60)
        assert config.api_timeout == 60

    def test_config_maintains_backward_compatibility(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that Config.from_env() still works for backward compatibility."""
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "30")
        monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", "true")

        config = Config.from_env()
        assert config.api_timeout == 30
        assert config.verbose is True

    def test_config_maintains_security_validation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that security validation is maintained in unified config."""
        # Test injection protection
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "10; rm -rf /")
        with pytest.raises(ValueError, match="NHL_SCRABBLE_API_TIMEOUT"):
            Config()

        # Clear the problematic env var before testing SSRF
        monkeypatch.delenv("NHL_SCRABBLE_API_TIMEOUT")

        # Test SSRF protection
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "http://localhost:8000")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config()

    def test_config_model_dump(self) -> None:
        """Test that Config can be serialized to dict (pydantic feature)."""
        config = Config(api_timeout=15, verbose=True)
        data = config.model_dump()

        assert isinstance(data, dict)
        assert data["api_timeout"] == 15
        assert data["verbose"] is True
        # Should include all fields
        assert "api_base_url" in data
        assert "output_format" in data

    def test_config_to_dict_compatibility(self) -> None:
        """Test that to_dict() method still works for backward compatibility."""
        config = Config(api_timeout=15)
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["api_timeout"] == 15

    def test_config_env_prefix(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that NHL_SCRABBLE_ prefix is correctly handled."""
        # Should work with prefix
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "40")
        config = Config()
        assert config.api_timeout == 40

        # Should NOT work without prefix (regular env var should be ignored)
        monkeypatch.setenv("API_TIMEOUT", "99")
        config2 = Config()
        assert config2.api_timeout == 40  # Still from NHL_SCRABBLE_API_TIMEOUT

    def test_config_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variable names are case-insensitive."""
        # Should work with different casings
        monkeypatch.setenv("nhl_scrabble_api_timeout", "45")
        config = Config()
        assert config.api_timeout == 45

    def test_config_extra_fields_ignored(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that extra fields in .env file are ignored."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "NHL_SCRABBLE_API_TIMEOUT=20\n"
            "NHL_SCRABBLE_UNKNOWN_FIELD=value\n"  # Should be ignored
            "UNRELATED_VAR=value\n",  # Should be ignored
        )

        monkeypatch.chdir(tmp_path)

        # Clear env vars
        for key in list(os.environ.keys()):
            if key.startswith("NHL_SCRABBLE_"):
                monkeypatch.delenv(key, raising=False)

        # Should not raise error for extra fields
        config = Config()
        assert config.api_timeout == 20
        assert not hasattr(config, "unknown_field")

    def test_config_comprehensive_precedence(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test complete precedence chain: direct > env > .env > defaults."""
        # 1. Set defaults (implicit, baked into Config class)
        # 2. Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("NHL_SCRABBLE_API_TIMEOUT=20\n" "NHL_SCRABBLE_API_RETRIES=5\n")

        monkeypatch.chdir(tmp_path)

        # 3. Set environment variable (should override .env)
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "30")

        # 4. Direct instantiation (should override everything)
        config = Config(api_timeout=40)

        # Check precedence:
        assert config.api_timeout == 40  # Direct wins
        assert config.api_retries == 5  # From .env (no env var, no direct value)
        assert config.verbose is False  # Default (no .env, no env var, no direct)
