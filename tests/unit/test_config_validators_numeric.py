"""Unit tests for configuration validators and injection protection."""


import pytest

from nhl_scrabble.config_validators import (
    ConfigValidationError,
    validate_positive_float,
    validate_positive_int,
)


class TestValidatePositiveInt:
    """Test integer validation with injection protection."""

    def test_valid_integer(self) -> None:
        """Test validation of valid integer."""
        assert validate_positive_int("10", min_val=1, max_val=100) == 10

    def test_valid_integer_at_min(self) -> None:
        """Test validation at minimum boundary."""
        assert validate_positive_int("1", min_val=1, max_val=100) == 1

    def test_valid_integer_at_max(self) -> None:
        """Test validation at maximum boundary."""
        assert validate_positive_int("100", min_val=1, max_val=100) == 100

    def test_integer_with_whitespace(self) -> None:
        """Test integer with surrounding whitespace."""
        assert validate_positive_int("  42  ", min_val=1, max_val=100) == 42

    def test_rejects_command_injection_semicolon(self) -> None:
        """Test rejection of command injection with semicolon."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid integer.*contains dangerous character.*';'",
        ):
            validate_positive_int("10; rm -rf /", min_val=1, max_val=100)

    def test_rejects_command_injection_ampersand(self) -> None:
        """Test rejection of command injection with ampersand."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid integer.*contains dangerous character.*'&'",
        ):
            validate_positive_int("10 & cat /etc/passwd", min_val=1, max_val=100)

    def test_rejects_command_injection_pipe(self) -> None:
        """Test rejection of command injection with pipe."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid integer.*contains dangerous character.*'\|'",
        ):
            validate_positive_int("10 | whoami", min_val=1, max_val=100)

    def test_rejects_command_injection_backtick(self) -> None:
        """Test rejection of command injection with backtick."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid integer.*contains dangerous character.*'`'",
        ):
            validate_positive_int("10`whoami`", min_val=1, max_val=100)

    def test_rejects_command_injection_dollar(self) -> None:
        """Test rejection of command injection with dollar sign."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid integer.*contains dangerous character.*'\$'",
        ):
            validate_positive_int("10$((1+1))", min_val=1, max_val=100)

    def test_rejects_newline(self) -> None:
        """Test rejection of newline character."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid integer.*contains dangerous character",
        ):
            validate_positive_int("10\nrm -rf /", min_val=1, max_val=100)

    def test_rejects_non_integer(self) -> None:
        """Test rejection of non-integer value."""
        with pytest.raises(ConfigValidationError, match=r"Invalid integer: 'not_a_number'"):
            validate_positive_int("not_a_number", min_val=1, max_val=100)

    def test_rejects_float(self) -> None:
        """Test rejection of float value."""
        with pytest.raises(ConfigValidationError, match=r"Invalid integer: '10.5'"):
            validate_positive_int("10.5", min_val=1, max_val=100)

    def test_rejects_below_minimum(self) -> None:
        """Test rejection of value below minimum."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Value 0 outside allowed range \[1, 100\]",
        ):
            validate_positive_int("0", min_val=1, max_val=100)

    def test_rejects_above_maximum(self) -> None:
        """Test rejection of value above maximum."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Value 101 outside allowed range \[1, 100\]",
        ):
            validate_positive_int("101", min_val=1, max_val=100)


class TestValidatePositiveFloat:
    """Test float validation with injection protection."""

    def test_valid_float(self) -> None:
        """Test validation of valid float."""
        assert validate_positive_float("0.5", min_val=0.0, max_val=10.0) == 0.5

    def test_valid_integer_as_float(self) -> None:
        """Test validation of integer as float."""
        assert validate_positive_float("5", min_val=0.0, max_val=10.0) == 5.0

    def test_valid_float_at_min(self) -> None:
        """Test validation at minimum boundary."""
        assert validate_positive_float("0.0", min_val=0.0, max_val=10.0) == 0.0

    def test_valid_float_at_max(self) -> None:
        """Test validation at maximum boundary."""
        assert validate_positive_float("10.0", min_val=0.0, max_val=10.0) == 10.0

    def test_float_with_whitespace(self) -> None:
        """Test float with surrounding whitespace."""
        assert validate_positive_float("  3.14  ", min_val=0.0, max_val=10.0) == 3.14

    def test_rejects_command_injection_semicolon(self) -> None:
        """Test rejection of command injection with semicolon."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid float.*contains dangerous character.*';'",
        ):
            validate_positive_float("1.5; cat /etc/passwd", min_val=0.0, max_val=10.0)

    def test_rejects_command_injection_pipe(self) -> None:
        """Test rejection of command injection with pipe."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid float.*contains dangerous character.*'\|'",
        ):
            validate_positive_float("2.0 | ls", min_val=0.0, max_val=10.0)

    def test_rejects_non_float(self) -> None:
        """Test rejection of non-float value."""
        with pytest.raises(ConfigValidationError, match=r"Invalid float: 'not_a_float'"):
            validate_positive_float("not_a_float", min_val=0.0, max_val=10.0)

    def test_rejects_below_minimum(self) -> None:
        """Test rejection of value below minimum."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Value -1\.0 outside allowed range \[0\.0, 10\.0\]",
        ):
            validate_positive_float("-1.0", min_val=0.0, max_val=10.0)

    def test_rejects_above_maximum(self) -> None:
        """Test rejection of value above maximum."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Value 11\.0 outside allowed range \[0\.0, 10\.0\]",
        ):
            validate_positive_float("11.0", min_val=0.0, max_val=10.0)
