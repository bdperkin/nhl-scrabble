"""Additional CLI tests to cover edge cases and increase coverage to 95%+.

This module targets specific uncovered lines in cli.py to push overall coverage
from 91.39% to 95%+.

Focus areas:
- Output format validation
- Error handling paths
- Invalid parameters
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from click.testing import CliRunner

from nhl_scrabble.cli import cli

if TYPE_CHECKING:
    from pathlib import Path


class TestCLICSVOutput:
    """Test CSV output format edge cases."""

    def test_analyze_csv_without_output_fails(self) -> None:
        """Test that CSV format requires output file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "csv"])

        # Should fail with helpful error
        assert result.exit_code != 0
        assert "CSV format requires --output" in result.output


class TestCLIExcelOutput:
    """Test Excel output format edge cases."""

    def test_analyze_excel_without_output_fails(self) -> None:
        """Test that Excel format requires output file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--format", "excel"])

        # Should fail with helpful error
        assert result.exit_code != 0
        assert "EXCEL format requires --output" in result.output


class TestCLIErrorHandling:
    """Test error handling paths in CLI."""

    def test_analyze_with_invalid_output_directory(self, tmp_path: Path) -> None:
        """Test analyze with output directory that doesn't exist."""
        output_file = tmp_path / "nonexistent_dir" / "output.txt"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--format",
                "text",
                "--output",
                str(output_file),
            ],
        )

        # Should fail with helpful error about directory
        assert result.exit_code != 0
        assert "directory" in result.output.lower() or "not exist" in result.output.lower()


class TestCLICommandHelp:
    """Test command help output."""

    def test_watch_command_help(self) -> None:
        """Test that watch command help is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--help"])

        # Should show help for watch command
        assert result.exit_code == 0
        assert "watch" in result.output.lower() or "interval" in result.output.lower()
