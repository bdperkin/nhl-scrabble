"""Integration tests for CLI output path validation."""

import os
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestOutputPathValidation:
    """Tests for output path validation in CLI."""

    def test_output_to_stdout(self) -> None:
        """Test that output to stdout (no --output) works."""
        runner = CliRunner()

        with patch("nhl_scrabble.cli.run_analysis") as mock_run:
            mock_run.return_value = "Test report"

            result = runner.invoke(cli, ["analyze"])

            assert result.exit_code == 0
            assert "Test report" in result.output

    def test_output_to_nonexistent_directory(self) -> None:
        """Test that output to nonexistent directory fails early."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["analyze", "--output", "/nonexistent/dir/output.txt"])

            assert result.exit_code != 0
            assert "directory does not exist" in result.output.lower()
            assert "mkdir -p" in result.output

    def test_output_to_readonly_directory(self, tmp_path: Path) -> None:
        """Test that output to read-only directory fails early."""
        runner = CliRunner()

        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o555)  # r-xr-xr-x

        output_path = readonly_dir / "output.txt"

        try:
            result = runner.invoke(cli, ["analyze", "--output", str(output_path)])

            assert result.exit_code != 0
            assert "not writable" in result.output.lower()
            assert "ls -ld" in result.output
        finally:
            # Cleanup - restore permissions before pytest cleanup
            readonly_dir.chmod(0o755)

    def test_output_to_readonly_file(self, tmp_path: Path) -> None:
        """Test that output to read-only file fails early."""
        runner = CliRunner()

        # Create read-only file
        readonly_file = tmp_path / "readonly.txt"
        readonly_file.write_text("existing content")
        readonly_file.chmod(0o444)  # r--r--r--

        try:
            result = runner.invoke(cli, ["analyze", "--output", str(readonly_file)])

            assert result.exit_code != 0
            assert "not writable" in result.output.lower()
            assert "ls -l" in result.output
        finally:
            # Cleanup - restore permissions
            readonly_file.chmod(0o644)

    def test_output_overwrites_existing_file(self, tmp_path: Path) -> None:
        """Test that output to existing file shows warning."""
        runner = CliRunner()

        # Create existing file
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("old content")

        with (
            patch("nhl_scrabble.cli.run_analysis") as mock_run,
            patch("nhl_scrabble.cli.logger") as mock_logger,
        ):
            mock_run.return_value = "new content"

            result = runner.invoke(cli, ["analyze", "--output", str(existing_file)])

            # Should succeed with warning
            assert result.exit_code == 0
            # Check that warning was logged
            mock_logger.warning.assert_called_once()
            warning_message = mock_logger.warning.call_args[0][0]
            assert "will be overwritten" in warning_message.lower()

            # File should be overwritten
            new_content = existing_file.read_text()
            assert new_content == "new content"
            assert "old content" not in new_content

    def test_output_to_valid_path(self, tmp_path: Path) -> None:
        """Test that output to valid path works."""
        runner = CliRunner()

        output_file = tmp_path / "output.txt"

        with patch("nhl_scrabble.cli.run_analysis") as mock_run:
            mock_run.return_value = "Test report content"

            result = runner.invoke(cli, ["analyze", "--output", str(output_file)])

            assert result.exit_code == 0
            assert output_file.exists()
            assert output_file.read_text() == "Test report content"

    def test_validation_happens_before_api_calls(self) -> None:
        """Test that validation happens before making API calls."""
        runner = CliRunner()

        with patch("nhl_scrabble.cli.run_analysis") as mock_run:
            # Invalid output path
            result = runner.invoke(cli, ["analyze", "--output", "/nonexistent/dir/output.txt"])

            # Should fail without calling run_analysis
            assert result.exit_code != 0
            mock_run.assert_not_called()

    def test_output_to_new_file_in_existing_directory(self, tmp_path: Path) -> None:
        """Test that output to new file in existing directory works."""
        runner = CliRunner()

        output_file = tmp_path / "new_file.txt"
        assert not output_file.exists()

        with patch("nhl_scrabble.cli.run_analysis") as mock_run:
            mock_run.return_value = "New file content"

            result = runner.invoke(cli, ["analyze", "--output", str(output_file)])

            assert result.exit_code == 0
            assert output_file.exists()
            assert output_file.read_text() == "New file content"

    def test_output_with_relative_path(self, tmp_path: Path) -> None:
        """Test that relative paths are resolved correctly."""
        runner = CliRunner()

        # Change to tmp_path
        original_cwd = Path.cwd()
        os.chdir(tmp_path)

        try:
            with patch("nhl_scrabble.cli.run_analysis") as mock_run:
                mock_run.return_value = "Relative path content"

                result = runner.invoke(cli, ["analyze", "--output", "relative_output.txt"])

                assert result.exit_code == 0
                assert (tmp_path / "relative_output.txt").exists()
        finally:
            os.chdir(original_cwd)

    def test_output_with_nested_new_directories_fails(self, tmp_path: Path) -> None:
        """Test that nested nonexistent directories fail early."""
        runner = CliRunner()

        nested_path = tmp_path / "nonexistent1" / "nonexistent2" / "output.txt"

        result = runner.invoke(cli, ["analyze", "--output", str(nested_path)])

        assert result.exit_code != 0
        assert "directory does not exist" in result.output.lower()

    def test_output_to_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test that attempting to write to a directory fails appropriately."""
        runner = CliRunner()

        # Try to use directory as output file
        result = runner.invoke(cli, ["analyze", "--output", str(tmp_path)])

        # This should fail when trying to write (IsADirectoryError)
        # The validation passes (directory is writable), but write fails
        assert result.exit_code != 0
