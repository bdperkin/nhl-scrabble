"""Integration tests for config SSRF protection."""

import pytest

from nhl_scrabble.config import Config


class TestConfigSSRFProtection:
    """Integration tests for SSRF protection in configuration."""

    def test_config_default_api_url(self) -> None:
        """Test that config accepts default NHL API URL."""
        config = Config()
        assert config.api_base_url == "https://api-web.nhle.com/v1"

    def test_config_from_env_valid_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config accepts valid NHL API URL from environment."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://api-web.nhle.com/v1")
        config = Config.from_env()
        assert config.api_base_url == "https://api-web.nhle.com/v1"

    def test_config_from_env_alternative_nhl_domain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config accepts alternative NHL API domain."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://api.nhle.com")
        config = Config.from_env()
        assert config.api_base_url == "https://api.nhle.com"

    def test_config_rejects_private_ip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config rejects private IP addresses."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://192.168.1.1")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

    def test_config_rejects_localhost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config rejects localhost."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://localhost")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

    def test_config_rejects_localhost_ip(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config rejects localhost IP."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://127.0.0.1")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

    def test_config_rejects_metadata_endpoint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config rejects cloud metadata endpoints."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "http://169.254.169.254")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

    def test_config_rejects_http_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config rejects HTTP (not HTTPS) for API URL."""
        # Even for allowed domain, HTTP should be rejected for API base URL
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "http://api-web.nhle.com")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

    def test_config_rejects_non_allowed_domain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that config rejects non-allowed domains."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://evil.com")
        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

    def test_config_to_dict_includes_api_base_url(self) -> None:
        """Test that to_dict() includes api_base_url."""
        config = Config()
        config_dict = config.to_dict()
        assert "api_base_url" in config_dict
        assert config_dict["api_base_url"] == "https://api-web.nhle.com/v1"

    def test_config_from_env_preserves_other_settings(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that SSRF validation doesn't affect other config settings."""
        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://api-web.nhle.com/v1")
        monkeypatch.setenv("NHL_SCRABBLE_API_TIMEOUT", "15")
        monkeypatch.setenv("NHL_SCRABBLE_VERBOSE", "true")

        config = Config.from_env()

        # SSRF-validated setting
        assert config.api_base_url == "https://api-web.nhle.com/v1"

        # Other settings still work
        assert config.api_timeout == 15
        assert config.verbose is True

    def test_config_ssrf_error_logged(
        self,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that SSRF protection errors are logged."""
        import logging

        caplog.set_level(logging.ERROR)

        monkeypatch.setenv("NHL_SCRABBLE_API_BASE_URL", "https://192.168.1.1")

        with pytest.raises(ValueError, match="Invalid API base URL"):
            Config.from_env()

        # Should log SSRF protection block
        assert any("SSRF protection blocked" in record.message for record in caplog.records)
        assert any("192.168.1.1" in record.message for record in caplog.records)
