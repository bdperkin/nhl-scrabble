"""Unit tests for __main__ module."""

import subprocess
import sys


class TestMain:
    """Tests for __main__ entry point."""

    def test_main_module_help(self) -> None:
        """Test that python -m nhl_scrabble --help works."""
        result = subprocess.run(  # noqa: PLW1510
            [sys.executable, "-m", "nhl_scrabble", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "Scrabble" in result.stdout
        assert "analyze" in result.stdout

    def test_main_module_analyze_help(self) -> None:
        """Test that python -m nhl_scrabble analyze --help works."""
        result = subprocess.run(  # noqa: PLW1510
            [sys.executable, "-m", "nhl_scrabble", "analyze", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "analyze" in result.stdout.lower() or "Scrabble" in result.stdout
        assert "--format" in result.stdout
        assert "--output" in result.stdout

    def test_main_module_version(self) -> None:
        """Test that python -m nhl_scrabble --version works."""
        result = subprocess.run(  # noqa: PLW1510
            [sys.executable, "-m", "nhl_scrabble", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        # Should contain version number
        assert "version" in result.stdout.lower() or "." in result.stdout
