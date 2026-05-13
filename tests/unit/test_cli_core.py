"""Comprehensive unit tests for CLI core functionality.

This module provides comprehensive coverage for the CLI module's core functionality,
including initialization, validation, and helper functions.

Target: Improve CLI coverage from 56.33% to 95%+
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

# CRITICAL: Import cli module directly to ensure coverage
import nhl_scrabble.cli as cli_module
from nhl_scrabble.cli import cli, validate_cli_arguments, validate_output_path
from nhl_scrabble.exceptions import ValidationError


class TestCLIInitialization:
    """Test CLI application initialization and structure."""

    def test_cli_group_exists(self) -> None:
        """Test CLI group is properly configured."""
        assert cli is not None
        assert hasattr(cli, "commands")
        assert callable(cli)

    def test_cli_commands_registered(self) -> None:
        """Test all commands are registered in the CLI group."""
        assert "analyze" in cli.commands
        assert "watch" in cli.commands
        assert "search" in cli.commands
        assert "interactive" in cli.commands
        assert "test-analytics" in cli.commands

    def test_version_option_configured(self) -> None:
        """Test version option displays correctly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "nhl-scrabble, version" in result.output
        # Version string should contain at least major.minor format
        assert any(char.isdigit() for char in result.output)

    def test_help_option_configured(self) -> None:
        """Test help option displays all commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Commands:" in result.output or "Commands" in result.output
        assert "analyze" in result.output
        assert "watch" in result.output
        assert "search" in result.output

    def test_cli_group_name(self) -> None:
        """Test CLI group has correct name."""
        assert cli.name == "cli" or cli.name is None  # Click default naming

    def test_cli_context_settings(self) -> None:
        """Test CLI group context settings are configured."""
        # Click groups have context_settings attribute
        assert hasattr(cli, "context_settings") or hasattr(cli, "context_class")


class TestOutputPathValidation:
    """Test output path validation function."""

    def test_validate_output_path_none(self) -> None:
        """Test None output path (stdout) is valid."""
        # Should not raise
        validate_output_path(None)

    def test_validate_output_path_valid_new_file(self, tmp_path: Path) -> None:
        """Test validation of new file in existing directory."""
        output_path = tmp_path / "output.txt"
        # Should not raise
        validate_output_path(str(output_path))

    def test_validate_output_path_valid_existing_file(self, tmp_path: Path) -> None:
        """Test validation of existing writable file."""
        output_path = tmp_path / "output.txt"
        output_path.write_text("existing")
        # Should not raise (will warn about overwrite)
        validate_output_path(str(output_path))

    def test_validate_output_path_nonexistent_directory(self) -> None:
        """Test validation fails for nonexistent parent directory."""
        with pytest.raises(click.ClickException) as exc_info:
            validate_output_path("/nonexistent/directory/output.txt")
        assert "does not exist" in str(exc_info.value).lower()

    @pytest.mark.skipif(sys.platform == "win32", reason="chmod doesn't work on Windows")
    def test_validate_output_path_readonly_directory(self, tmp_path: Path) -> None:
        """Test validation fails for read-only parent directory."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o555)  # Read+execute only

        output_path = readonly_dir / "output.txt"

        try:
            with pytest.raises(click.ClickException) as exc_info:
                validate_output_path(str(output_path))
            assert "not writable" in str(exc_info.value).lower()
        finally:
            # Cleanup: restore permissions
            readonly_dir.chmod(0o755)

    def test_validate_output_path_readonly_file(self, tmp_path: Path) -> None:
        """Test validation fails for read-only existing file."""
        output_path = tmp_path / "readonly.txt"
        output_path.write_text("readonly")
        output_path.chmod(0o444)  # Read-only

        try:
            with pytest.raises(click.ClickException) as exc_info:
                validate_output_path(str(output_path))
            assert "not writable" in str(exc_info.value).lower()
        finally:
            # Cleanup: restore permissions
            output_path.chmod(0o644)

    def test_validate_output_path_resolves_relative_paths(self, tmp_path: Path) -> None:
        """Test validation resolves relative paths to absolute."""
        # This should work without raising
        # The function resolves to absolute path internally
        validate_output_path("./test_output.txt")

    def test_validate_output_path_directory_not_file(self, tmp_path: Path) -> None:
        """Test validation with directory path (not a file)."""
        # Passing a directory as output path
        # Should not raise during validation (will fail on write later)
        validate_output_path(str(tmp_path))

    @patch("nhl_scrabble.cli.validators.logger")
    def test_validate_output_path_warns_on_overwrite(
        self,
        mock_logger: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test validation warns when overwriting existing file."""
        output_path = tmp_path / "existing.txt"
        output_path.write_text("existing content")

        validate_output_path(str(output_path))

        # Should log warning about overwrite
        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "overwritten" in warning_msg.lower()


class TestCLIArgumentsValidation:
    """Test CLI arguments validation function."""

    def test_validate_cli_arguments_none_output(self) -> None:
        """Test validation with None output (stdout)."""
        result = validate_cli_arguments(None)
        assert result is None

    def test_validate_cli_arguments_valid_path(self, tmp_path: Path) -> None:
        """Test validation with valid output path."""
        output_path = tmp_path / "output.txt"
        result = validate_cli_arguments(str(output_path))
        assert isinstance(result, Path)
        assert result == output_path

    def test_validate_cli_arguments_existing_file(self, tmp_path: Path) -> None:
        """Test validation with existing file (should allow overwrite)."""
        output_path = tmp_path / "existing.txt"
        output_path.write_text("existing")

        result = validate_cli_arguments(str(output_path))
        assert isinstance(result, Path)
        assert result == output_path

    @patch("nhl_scrabble.cli.validators.validate_file_path")
    def test_validate_cli_arguments_validation_error(
        self,
        mock_validate: MagicMock,
    ) -> None:
        """Test validation raises ClickException on ValidationError."""
        mock_validate.side_effect = ValidationError("Invalid path")

        with pytest.raises(click.ClickException) as exc_info:
            validate_cli_arguments("/invalid/path.txt")

        assert "Invalid path" in str(exc_info.value)

    @patch("nhl_scrabble.cli.validators.validate_file_path")
    def test_validate_cli_arguments_calls_validator(
        self,
        mock_validate: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test validation calls validate_file_path with correct arguments."""
        output_path = tmp_path / "output.txt"
        mock_validate.return_value = output_path

        result = validate_cli_arguments(str(output_path))

        # Should call validate_file_path with allow_overwrite=True
        mock_validate.assert_called_once_with(str(output_path), allow_overwrite=True)
        assert result == output_path


class TestCLIHelperFunctions:
    """Test CLI helper functions and utilities."""

    def test_cli_module_imports(self) -> None:
        """Test all required imports are available."""
        # Verify critical imports exist
        assert hasattr(cli_module, "cli")
        assert hasattr(cli_module, "validate_output_path")
        assert hasattr(cli_module, "validate_cli_arguments")
        assert hasattr(cli_module, "run_analysis")

    def test_cli_module_constants(self) -> None:
        """Test module-level constants are defined."""
        # Verify cli group is initialized
        assert cli_module.cli is not None
        assert callable(cli_module.cli)

    def test_cli_module_has_version(self) -> None:
        """Test module imports version correctly."""
        from nhl_scrabble import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)


class TestCLIErrorMessages:
    """Test CLI error messages are user-friendly."""

    def test_nonexistent_directory_error_message(self) -> None:
        """Test error message for nonexistent directory is helpful."""
        with pytest.raises(click.ClickException) as exc_info:
            validate_output_path("/nonexistent/directory/file.txt")

        error_msg = str(exc_info.value)
        assert "does not exist" in error_msg.lower()
        # Should suggest creating directory
        assert "mkdir" in error_msg.lower() or "create" in error_msg.lower()

    @pytest.mark.skipif(sys.platform == "win32", reason="chmod doesn't work on Windows")
    def test_readonly_directory_error_message(self, tmp_path: Path) -> None:
        """Test error message for read-only directory is helpful."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o555)

        output_path = readonly_dir / "output.txt"

        try:
            with pytest.raises(click.ClickException) as exc_info:
                validate_output_path(str(output_path))

            error_msg = str(exc_info.value)
            assert "not writable" in error_msg.lower()
            # Should suggest checking permissions
            assert "permission" in error_msg.lower() or "ls" in error_msg.lower()
        finally:
            readonly_dir.chmod(0o755)

    def test_readonly_file_error_message(self, tmp_path: Path) -> None:
        """Test error message for read-only file is helpful."""
        readonly_file = tmp_path / "readonly.txt"
        readonly_file.write_text("content")
        readonly_file.chmod(0o444)

        try:
            with pytest.raises(click.ClickException) as exc_info:
                validate_output_path(str(readonly_file))

            error_msg = str(exc_info.value)
            assert "not writable" in error_msg.lower()
        finally:
            readonly_file.chmod(0o644)


class TestCLIIntegration:
    """Test CLI integration with Click framework."""

    def test_cli_runner_invocation(self) -> None:
        """Test CLI can be invoked via CliRunner."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_cli_command_help(self) -> None:
        """Test all commands have help text."""
        runner = CliRunner()

        # Test analyze command help
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "analyze" in result.output.lower()

        # Test watch command help
        result = runner.invoke(cli, ["watch", "--help"])
        assert result.exit_code == 0
        assert "watch" in result.output.lower()

        # Test search command help
        result = runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0
        assert "search" in result.output.lower()

    def test_cli_invalid_command(self) -> None:
        """Test invalid command shows helpful error."""
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-command"])

        assert result.exit_code != 0
        # Click shows "No such command" error
        assert "no such command" in result.output.lower() or "error" in result.output.lower()
