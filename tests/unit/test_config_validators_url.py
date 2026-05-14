"""Unit tests for URL validation in config_validators."""

import pytest

from nhl_scrabble.config_validators import ConfigValidationError, validate_url


class TestValidateURL:
    """Tests for validate_url function."""

    def test_validate_https_url(self) -> None:
        """Test validation of valid HTTPS URL."""
        url = validate_url("https://api.example.com")
        assert url == "https://api.example.com"

    def test_validate_http_url_when_allowed(self) -> None:
        """Test validation of HTTP URL when HTTPS not required."""
        url = validate_url("http://localhost:8080", require_https=False)
        assert url == "http://localhost:8080"

    def test_reject_http_url_when_https_required(self) -> None:
        """Test rejection of HTTP URL when HTTPS is required."""
        with pytest.raises(ConfigValidationError, match="must use HTTPS protocol"):
            validate_url("http://api.example.com")

    def test_validate_url_with_port(self) -> None:
        """Test validation of URL with port number."""
        url = validate_url("https://api.example.com:8443")
        assert url == "https://api.example.com:8443"

    def test_validate_url_with_path(self) -> None:
        """Test validation of URL with path."""
        url = validate_url("https://api.example.com/v1/endpoint")
        assert url == "https://api.example.com/v1/endpoint"

    def test_validate_localhost_url(self) -> None:
        """Test validation of localhost URL."""
        url = validate_url("https://localhost/api", require_https=True)
        assert url == "https://localhost/api"

    def test_validate_ip_address_url(self) -> None:
        """Test validation of IP address URL."""
        url = validate_url("https://192.168.1.1:443", require_https=True)
        assert url == "https://192.168.1.1:443"

    def test_reject_url_with_dangerous_chars(self) -> None:
        """Test rejection of URL with dangerous characters."""
        dangerous_urls = [
            "https://api.example.com;rm -rf /",
            "https://api.example.com&whoami",
            "https://api.example.com|cat /etc/passwd",
            "https://api.example.com$USER",
            "https://api.example.com`whoami`",
            "https://api.example.com\nmalicious",
            "https://api.example.com\rmalicious",
            "https://api.example com",  # Space
            "https://api.example.com<script>",
            "https://api.example.com>output",
        ]

        for bad_url in dangerous_urls:
            with pytest.raises(ConfigValidationError, match="dangerous character"):
                validate_url(bad_url)

    def test_reject_invalid_url_format(self) -> None:
        """Test rejection of invalid URL format."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong protocol
            "//example.com",  # Missing protocol
            "https://",  # Missing domain
            "https:///path",  # Missing domain
        ]

        for bad_url in invalid_urls:
            with pytest.raises(ConfigValidationError, match="Invalid URL format"):
                validate_url(bad_url)

    def test_strip_whitespace_from_url(self) -> None:
        """Test that whitespace is stripped from URL."""
        url = validate_url("  https://api.example.com  ")
        assert url == "https://api.example.com"
