"""Unit tests for configuration validators and injection protection."""

import sys
import tempfile
from pathlib import Path

import pytest

from nhl_scrabble.config_validators import (
    ConfigValidationError,
    validate_boolean,
    validate_enum,
    validate_safe_path,
)


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
        # Use platform-specific absolute paths
        absolute_path = "C:\\Windows\\System32" if sys.platform == "win32" else "/etc/passwd"
        with pytest.raises(
            ConfigValidationError,
            match=r"Absolute paths not allowed",
        ):
            validate_safe_path(absolute_path)

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

    def test_invalid_path_format_type_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test handling of invalid path format (TypeError from Path)."""
        from pathlib import Path as PathClass

        original_new = PathClass.__new__

        def mock_new(cls, *args, **kwargs):
            # Trigger TypeError for a specific input
            if args and args[0] == "trigger-type-error":
                raise TypeError("Invalid path type")
            return original_new(cls, *args, **kwargs)

        monkeypatch.setattr(PathClass, "__new__", mock_new)

        with pytest.raises(ConfigValidationError, match=r"Invalid path format"):
            validate_safe_path("trigger-type-error")

    def test_path_resolve_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test handling of path resolution failures."""
        from pathlib import Path

        def mock_resolve(*args, **kwargs):
            raise OSError("Symbolic link loop or permission denied")

        monkeypatch.setattr(Path, "resolve", mock_resolve)

        with pytest.raises(ConfigValidationError, match=r"Cannot resolve path"):
            validate_safe_path("some_path.txt")


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

    def test_empty_string_as_false(self) -> None:
        """Test empty string returns False."""
        assert validate_boolean("") is False
        assert validate_boolean("   ") is False  # Whitespace only

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
