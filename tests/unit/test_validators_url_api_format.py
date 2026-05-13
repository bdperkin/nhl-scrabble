"""Unit tests for input validation utilities."""

from pathlib import Path

import pytest

from nhl_scrabble.validators import (
    ValidationError,
    normalize_player_name,
    validate_api_response_structure,
    validate_file_path,
    validate_float_range,
    validate_output_format,
    validate_player_name,
    validate_team_abbreviation,
    validate_url,
)


class TestValidateUrl:
    """Tests for validate_url()."""

    def test_valid_https_url(self) -> None:
        """Test valid HTTPS URL."""
        result = validate_url("https://api-web.nhle.com")
        assert result == "https://api-web.nhle.com"

    def test_valid_http_url(self) -> None:
        """Test valid HTTP URL."""
        result = validate_url("http://example.com")
        assert result == "http://example.com"

    def test_url_with_path(self) -> None:
        """Test URL with path components."""
        result = validate_url("https://api-web.nhle.com/v1/standings")
        assert result == "https://api-web.nhle.com/v1/standings"

    def test_invalid_scheme_ftp(self) -> None:
        """Test error with FTP scheme (not allowed by default)."""
        with pytest.raises(ValidationError, match="scheme must be"):
            validate_url("ftp://example.com")

    def test_invalid_scheme_file(self) -> None:
        """Test error with file:// scheme (security risk)."""
        with pytest.raises(ValidationError, match="scheme must be"):
            validate_url("file:///etc/passwd")

    def test_missing_domain(self) -> None:
        """Test error when domain missing."""
        with pytest.raises(ValidationError, match="must include domain"):
            validate_url("https://")

    def test_custom_allowed_schemes(self) -> None:
        """Test custom allowed schemes."""
        result = validate_url("ws://example.com", allowed_schemes=["ws", "wss"])
        assert result == "ws://example.com"

    def test_custom_schemes_validation(self) -> None:
        """Test custom schemes still validates."""
        with pytest.raises(ValidationError, match="scheme must be"):
            validate_url("http://example.com", allowed_schemes=["ws", "wss"])

    def test_url_with_query_params(self) -> None:
        """Test URL with query parameters."""
        url = "https://api.example.com/v1/resource?param1=value1&param2=value2"
        result = validate_url(url)
        assert result == url

    def test_url_with_fragment(self) -> None:
        """Test URL with fragment identifier."""
        url = "https://example.com/page#section"
        result = validate_url(url)
        assert result == url

    def test_url_with_port(self) -> None:
        """Test URL with port number."""
        url = "https://example.com:8443/api"
        result = validate_url(url)
        assert result == url

    def test_url_with_username_password(self) -> None:
        """Test URL with authentication credentials."""
        url = "https://user:pass@example.com"
        result = validate_url(url)
        assert result == url

    def test_url_localhost(self) -> None:
        """Test localhost URL."""
        url = "http://localhost:8000"
        result = validate_url(url)
        assert result == url

    def test_url_ip_address(self) -> None:
        """Test URL with IP address."""
        url = "http://192.168.1.1"
        result = validate_url(url)
        assert result == url

    def test_no_scheme(self) -> None:
        """Test URL without scheme."""
        with pytest.raises(ValidationError, match="scheme must be"):
            validate_url("example.com")

    def test_empty_allowed_schemes(self) -> None:
        """Test with empty allowed schemes list."""
        with pytest.raises(ValidationError, match="scheme must be"):
            validate_url("https://example.com", allowed_schemes=[])

    def test_malformed_url(self) -> None:
        """Test completely malformed URL."""
        # Create a URL that would fail parsing
        with pytest.raises(ValidationError):
            # URL with only a scheme (no netloc)
            validate_url("http://")

    def test_relative_url_rejected(self) -> None:
        """Test relative URL is rejected."""
        with pytest.raises(ValidationError):
            validate_url("/api/v1/resource")


class TestValidateApiResponseStructure:
    """Tests for validate_api_response_structure()."""

    def test_valid_structure(self) -> None:
        """Test valid API response structure."""
        data: dict[str, list[str]] = {"forwards": [], "defensemen": [], "goalies": []}
        result = validate_api_response_structure(
            data,
            required_keys=["forwards", "defensemen", "goalies"],
        )
        assert result == data

    def test_missing_single_key(self) -> None:
        """Test error when single required key missing."""
        data: dict[str, list[str]] = {"forwards": [], "defensemen": []}
        with pytest.raises(ValidationError, match="missing required keys"):
            validate_api_response_structure(
                data,
                required_keys=["forwards", "defensemen", "goalies"],
            )

    def test_missing_multiple_keys(self) -> None:
        """Test error when multiple required keys missing."""
        data: dict[str, list[str]] = {"forwards": []}
        with pytest.raises(ValidationError, match="missing required keys"):
            validate_api_response_structure(
                data,
                required_keys=["forwards", "defensemen", "goalies"],
            )

    def test_extra_keys_allowed(self) -> None:
        """Test extra keys are allowed in response."""
        data = {"forwards": [], "extra": "data", "another": 123}
        result = validate_api_response_structure(data, required_keys=["forwards"])
        assert result == data

    def test_custom_context_in_error(self) -> None:
        """Test custom context appears in error message."""
        data: dict[str, list[str]] = {}
        with pytest.raises(ValidationError, match="Team roster"):
            validate_api_response_structure(data, required_keys=["forwards"], context="Team roster")

    def test_empty_required_keys(self) -> None:
        """Test validation passes with no required keys."""
        data = {"anything": "goes"}
        result = validate_api_response_structure(data, required_keys=[])
        assert result == data

    def test_available_keys_in_error_message(self) -> None:
        """Test error message lists available keys."""
        data = {"available1": "data", "available2": 123}
        with pytest.raises(ValidationError) as exc_info:
            validate_api_response_structure(
                data,
                required_keys=["missing1", "missing2"],
            )
        error_msg = str(exc_info.value)
        assert "available1" in error_msg
        assert "available2" in error_msg
        assert "missing1" in error_msg
        assert "missing2" in error_msg


class TestValidateOutputFormat:
    """Tests for validate_output_format()."""

    def test_valid_text(self) -> None:
        """Test valid text format."""
        result = validate_output_format("text")
        assert result == "text"

    def test_valid_json(self) -> None:
        """Test valid json format."""
        result = validate_output_format("json")
        assert result == "json"

    def test_valid_html(self) -> None:
        """Test valid html format."""
        result = validate_output_format("html")
        assert result == "html"

    def test_uppercase_converted(self) -> None:
        """Test uppercase is converted to lowercase."""
        result = validate_output_format("JSON")
        assert result == "json"

    def test_whitespace_stripped(self) -> None:
        """Test whitespace is stripped."""
        result = validate_output_format("  text  ")
        assert result == "text"

    def test_invalid_format(self) -> None:
        """Test error with invalid format."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_output_format("xml")

    def test_empty_string(self) -> None:
        """Test error with empty string."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_output_format("")


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_is_value_error(self) -> None:
        """Test ValidationError is a ValueError."""
        assert issubclass(ValidationError, ValueError)

    def test_error_message(self) -> None:
        """Test error message is preserved."""
        error = ValidationError("Test message")
        assert str(error) == "Test message"

    def test_can_be_caught_as_value_error(self) -> None:
        """Test ValidationError can be caught as ValueError."""
        with pytest.raises(ValueError, match="test"):
            raise ValidationError("test")

    def test_can_be_caught_specifically(self) -> None:
        """Test ValidationError can be caught specifically."""
        with pytest.raises(ValidationError):
            raise ValidationError("test")
