"""Unit tests for input validation utilities."""


import pytest

from nhl_scrabble.validators import (
    ValidationError,
    validate_float_range,
    validate_team_abbreviation,
)


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

    def test_no_min_or_max(self) -> None:
        """Test validation with no bounds."""
        result = validate_float_range(999.9)
        assert result == 999.9

    def test_min_only(self) -> None:
        """Test validation with only minimum bound."""
        result = validate_float_range(100.0, min_val=50.0)
        assert result == 100.0

    def test_max_only(self) -> None:
        """Test validation with only maximum bound."""
        result = validate_float_range(5.0, max_val=10.0)
        assert result == 5.0

    def test_exact_minimum(self) -> None:
        """Test value exactly at minimum (inclusive)."""
        result = validate_float_range(1.0, min_val=1.0, max_val=10.0)
        assert result == 1.0

    def test_exact_maximum(self) -> None:
        """Test value exactly at maximum (inclusive)."""
        result = validate_float_range(10.0, min_val=1.0, max_val=10.0)
        assert result == 10.0

    def test_custom_parameter_name_in_error(self) -> None:
        """Test custom parameter name appears in error message."""
        with pytest.raises(ValidationError, match="timeout"):
            validate_float_range(0.5, min_val=1.0, name="timeout")

    def test_negative_values(self) -> None:
        """Test validation with negative values."""
        result = validate_float_range(-5.0, min_val=-10.0, max_val=0.0)
        assert result == -5.0

    def test_zero_value(self) -> None:
        """Test validation with zero."""
        result = validate_float_range(0.0, min_val=-1.0, max_val=1.0)
        assert result == 0.0


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
