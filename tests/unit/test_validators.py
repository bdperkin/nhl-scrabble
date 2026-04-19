"""Unit tests for input validation utilities."""

from pathlib import Path

import pytest

from nhl_scrabble.validators import (
    ValidationError,
    validate_api_response_structure,
    validate_file_path,
    validate_float_range,
    validate_integer_range,
    validate_output_format,
    validate_player_name,
    validate_team_abbreviation,
    validate_url,
)


class TestValidateFilePath:
    """Tests for validate_file_path()."""

    def test_valid_path(self, tmp_path: Path) -> None:
        """Test valid file path."""
        file_path = tmp_path / "output.txt"
        result = validate_file_path(str(file_path))
        assert isinstance(result, Path)
        assert result.name == "output.txt"

    def test_path_traversal_blocked(self) -> None:
        """Test path traversal attack is blocked."""
        with pytest.raises(ValidationError, match="suspicious pattern"):
            validate_file_path("../../../etc/passwd")

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test error when parent directory doesn't exist."""
        # Make tmp_path the current directory for this test
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(ValidationError, match="does not exist"):
                validate_file_path("nonexistent/dir/file.txt")
        finally:
            os.chdir(original_cwd)

    def test_invalid_filename_characters(self, tmp_path: Path) -> None:
        """Test filename with invalid characters is rejected."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_file_path(str(tmp_path / "file<>.txt"))

    def test_existing_file_no_overwrite(self, tmp_path: Path) -> None:
        """Test error when file exists and overwrite not allowed."""
        existing = tmp_path / "existing.txt"
        existing.write_text("data")

        with pytest.raises(ValidationError, match="already exists"):
            validate_file_path(str(existing), allow_overwrite=False)

    def test_existing_file_with_overwrite(self, tmp_path: Path) -> None:
        """Test success when file exists but overwrite allowed."""
        existing = tmp_path / "existing.txt"
        existing.write_text("data")

        result = validate_file_path(str(existing), allow_overwrite=True)
        assert result == existing

    def test_path_with_dangerous_characters(self, tmp_path: Path) -> None:
        """Test filename with dangerous special chars is rejected."""
        # Note: Spaces would be rejected by our \w pattern which only allows alphanumeric
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_file_path(str(tmp_path / "dangerous!file.txt"))

    def test_hidden_file(self) -> None:
        """Test hidden file (starting with dot) is allowed."""
        # Use current directory to avoid path traversal check
        result = validate_file_path(".hidden")
        assert result.name == ".hidden"


class TestValidateIntegerRange:
    """Tests for validate_integer_range()."""

    def test_valid_integer(self) -> None:
        """Test valid integer within range."""
        result = validate_integer_range(5, min_val=1, max_val=10)
        assert result == 5

    def test_below_minimum(self) -> None:
        """Test error when value below minimum."""
        with pytest.raises(ValidationError, match="must be at least"):
            validate_integer_range(0, min_val=1, max_val=10)

    def test_above_maximum(self) -> None:
        """Test error when value above maximum."""
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_integer_range(11, min_val=1, max_val=10)

    def test_non_integer_value(self) -> None:
        """Test error when value is not an integer."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_integer_range("abc", min_val=1, max_val=10)

    def test_string_convertible_to_int(self) -> None:
        """Test string that can be converted to int."""
        result = validate_integer_range("5", min_val=1, max_val=10)
        assert result == 5

    def test_no_minimum(self) -> None:
        """Test validation with no minimum bound."""
        result = validate_integer_range(-100, max_val=100)
        assert result == -100

    def test_no_maximum(self) -> None:
        """Test validation with no maximum bound."""
        result = validate_integer_range(1000, min_val=1)
        assert result == 1000

    def test_custom_name_in_error(self) -> None:
        """Test custom parameter name appears in error message."""
        with pytest.raises(ValidationError, match="timeout"):
            validate_integer_range(0, min_val=1, name="timeout")


class TestValidateFloatRange:
    """Tests for validate_float_range()."""

    def test_valid_float(self) -> None:
        """Test valid float within range."""
        result = validate_float_range(2.5, min_val=1.0, max_val=10.0)
        assert result == 2.5

    def test_valid_integer_as_float(self) -> None:
        """Test integer value is converted to float."""
        result = validate_float_range(5, min_val=1.0, max_val=10.0)
        assert result == 5.0
        assert isinstance(result, float)

    def test_below_minimum(self) -> None:
        """Test error when value below minimum."""
        with pytest.raises(ValidationError, match="must be at least"):
            validate_float_range(0.5, min_val=1.0)

    def test_above_maximum(self) -> None:
        """Test error when value above maximum."""
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_float_range(10.5, max_val=10.0)

    def test_non_numeric_value(self) -> None:
        """Test error when value is not numeric."""
        with pytest.raises(ValidationError, match="must be a number"):
            validate_float_range("abc", min_val=1.0)

    def test_string_convertible_to_float(self) -> None:
        """Test string that can be converted to float."""
        result = validate_float_range("2.5", min_val=1.0, max_val=10.0)
        assert result == 2.5


class TestValidateTeamAbbreviation:
    """Tests for validate_team_abbreviation()."""

    def test_valid_abbreviation(self) -> None:
        """Test valid team abbreviation."""
        result = validate_team_abbreviation("TOR")
        assert result == "TOR"

    def test_lowercase_converted(self) -> None:
        """Test lowercase is converted to uppercase."""
        result = validate_team_abbreviation("tor")
        assert result == "TOR"

    def test_whitespace_stripped(self) -> None:
        """Test whitespace is stripped."""
        result = validate_team_abbreviation("  MTL  ")
        assert result == "MTL"

    def test_two_character_abbreviation(self) -> None:
        """Test two-character abbreviation is valid."""
        result = validate_team_abbreviation("LA")
        assert result == "LA"

    def test_three_character_abbreviation(self) -> None:
        """Test three-character abbreviation is valid."""
        result = validate_team_abbreviation("VGK")
        assert result == "VGK"

    def test_too_short(self) -> None:
        """Test error when abbreviation too short."""
        with pytest.raises(ValidationError, match="2-3 characters"):
            validate_team_abbreviation("T")

    def test_too_long(self) -> None:
        """Test error when abbreviation too long."""
        with pytest.raises(ValidationError, match="2-3 characters"):
            validate_team_abbreviation("TORX")

    def test_contains_numbers(self) -> None:
        """Test error when abbreviation contains numbers."""
        with pytest.raises(ValidationError, match="only letters"):
            validate_team_abbreviation("T0R")

    def test_empty_string(self) -> None:
        """Test error when abbreviation is empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_team_abbreviation("")

    def test_whitespace_only(self) -> None:
        """Test error when abbreviation is only whitespace."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_team_abbreviation("   ")


class TestValidatePlayerName:
    """Tests for validate_player_name()."""

    def test_valid_simple_name(self) -> None:
        """Test valid simple name."""
        result = validate_player_name("Connor McDavid")
        assert result == "Connor McDavid"

    def test_valid_hyphenated_name(self) -> None:
        """Test valid hyphenated name."""
        result = validate_player_name("Jean-Gabriel Pageau")
        assert result == "Jean-Gabriel Pageau"

    def test_valid_name_with_apostrophe(self) -> None:
        """Test valid name with apostrophe."""
        result = validate_player_name("Ryan O'Reilly")
        assert result == "Ryan O'Reilly"

    def test_valid_name_with_period(self) -> None:
        """Test valid name with period."""
        result = validate_player_name("P.K. Subban")
        assert result == "P.K. Subban"

    def test_whitespace_stripped(self) -> None:
        """Test leading/trailing whitespace is stripped."""
        result = validate_player_name("  Connor McDavid  ")
        assert result == "Connor McDavid"

    def test_empty_name(self) -> None:
        """Test error when name is empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_player_name("")

    def test_whitespace_only(self) -> None:
        """Test error when name is only whitespace."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_player_name("   ")

    def test_name_too_long(self) -> None:
        """Test error when name too long."""
        with pytest.raises(ValidationError, match="too long"):
            validate_player_name("A" * 101)

    def test_invalid_characters_script_tag(self) -> None:
        """Test error when name contains script tag (XSS attempt)."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor<script>alert(1)</script>")

    def test_invalid_characters_numbers(self) -> None:
        """Test error when name contains numbers."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor123")

    def test_invalid_characters_special(self) -> None:
        """Test error when name contains special characters."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor@McDavid")


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


class TestValidateApiResponseStructure:
    """Tests for validate_api_response_structure()."""

    def test_valid_structure(self) -> None:
        """Test valid API response structure."""
        data: dict[str, list[str]] = {"forwards": [], "defensemen": [], "goalies": []}
        result = validate_api_response_structure(
            data, required_keys=["forwards", "defensemen", "goalies"]
        )
        assert result == data

    def test_missing_single_key(self) -> None:
        """Test error when single required key missing."""
        data: dict[str, list[str]] = {"forwards": [], "defensemen": []}
        with pytest.raises(ValidationError, match="missing required keys"):
            validate_api_response_structure(
                data, required_keys=["forwards", "defensemen", "goalies"]
            )

    def test_missing_multiple_keys(self) -> None:
        """Test error when multiple required keys missing."""
        data: dict[str, list[str]] = {"forwards": []}
        with pytest.raises(ValidationError, match="missing required keys"):
            validate_api_response_structure(
                data, required_keys=["forwards", "defensemen", "goalies"]
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
