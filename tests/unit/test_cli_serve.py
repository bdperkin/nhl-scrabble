"""Comprehensive unit tests for CLI search and serve commands.

This module tests the search and serve commands for player search functionality
and web server startup.

Target: Improve coverage of search (lines 1186-1291) and serve (lines 1293-1401)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

# CRITICAL: Import cli module directly to ensure coverage
from nhl_scrabble.cli import cli

if TYPE_CHECKING:
    from pathlib import Path

class TestServeCommand:
    """Test serve command implementation."""

    @patch("nhl_scrabble.cli.Config")
    def test_serve_basic_execution(
        self,
        mock_config_class: MagicMock,
    ) -> None:
        """Test basic serve command execution."""
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config.log_max_bytes = 10485760
        mock_config.log_backup_count = 3
        mock_config_class.from_env.return_value = mock_config

        # Mock uvicorn module
        mock_uvicorn = MagicMock()
        with patch.dict("sys.modules", {"uvicorn": mock_uvicorn}):
            runner = CliRunner()
            result = runner.invoke(cli, ["serve"])

            assert result.exit_code == 0
            assert mock_uvicorn.run.called

    @patch("nhl_scrabble.cli.Config")
    def test_serve_with_custom_host_port(
        self,
        mock_config_class: MagicMock,
    ) -> None:
        """Test serve with custom host and port."""
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config.log_max_bytes = 10485760
        mock_config.log_backup_count = 3
        mock_config_class.from_env.return_value = mock_config

        # Mock uvicorn module
        mock_uvicorn = MagicMock()
        with patch.dict("sys.modules", {"uvicorn": mock_uvicorn}):
            runner = CliRunner()
            result = runner.invoke(
                cli,
                ["serve", "--host", "0.0.0.0", "--port", "5000"],  # noqa: S104
            )

            assert result.exit_code == 0
            # Verify uvicorn.run was called with correct host/port
            call_kwargs = mock_uvicorn.run.call_args[1]
            assert call_kwargs["host"] == "0.0.0.0"  # noqa: S104
            assert call_kwargs["port"] == 5000

    @patch("nhl_scrabble.cli.Config")
    def test_serve_with_reload(
        self,
        mock_config_class: MagicMock,
    ) -> None:
        """Test serve with reload flag."""
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config.log_max_bytes = 10485760
        mock_config.log_backup_count = 3
        mock_config_class.from_env.return_value = mock_config

        # Mock uvicorn module
        mock_uvicorn = MagicMock()
        with patch.dict("sys.modules", {"uvicorn": mock_uvicorn}):
            runner = CliRunner()
            result = runner.invoke(cli, ["serve", "--reload"])

            assert result.exit_code == 0
            # Verify reload was enabled and import string was passed
            call_args = mock_uvicorn.run.call_args
            # First argument should be string when reload=True
            assert isinstance(call_args[0][0], str)
            assert call_args[1]["reload"] is True

    @patch("nhl_scrabble.cli.Config")
    def test_serve_with_log_file(
        self,
        mock_config_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test serve with log file option."""
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config.log_max_bytes = 10485760
        mock_config.log_backup_count = 3
        mock_config_class.from_env.return_value = mock_config

        # Mock uvicorn module
        mock_uvicorn = MagicMock()
        with patch.dict("sys.modules", {"uvicorn": mock_uvicorn}):
            log_file = tmp_path / "server.log"
            runner = CliRunner()
            result = runner.invoke(cli, ["serve", "--log-file", str(log_file)])

            assert result.exit_code == 0

    @patch("nhl_scrabble.cli.Config")
    def test_serve_with_verbose(
        self,
        mock_config_class: MagicMock,
    ) -> None:
        """Test serve with verbose logging."""
        mock_config = MagicMock()
        mock_config.sanitize_logs = False
        mock_config.log_max_bytes = 10485760
        mock_config.log_backup_count = 3
        mock_config_class.from_env.return_value = mock_config

        # Mock uvicorn module
        mock_uvicorn = MagicMock()
        with patch.dict("sys.modules", {"uvicorn": mock_uvicorn}):
            runner = CliRunner()
            result = runner.invoke(cli, ["serve", "--verbose"])

            assert result.exit_code == 0

    def test_serve_missing_uvicorn(self) -> None:
        """Test serve fails gracefully when uvicorn not installed."""
        with patch.dict("sys.modules", {"uvicorn": None}):
            runner = CliRunner()
            result = runner.invoke(cli, ["serve"])

            # Should abort when uvicorn not available
            assert result.exit_code != 0

    @patch("nhl_scrabble.cli.Config")
    def test_serve_config_validation_error(self, mock_config_class: MagicMock) -> None:
        """Test serve handles config validation errors."""
        mock_config_class.from_env.side_effect = ValueError("Invalid config")

        runner = CliRunner()
        result = runner.invoke(cli, ["serve"])

        assert result.exit_code != 0
        assert "configuration error" in result.output.lower()

    def test_serve_invalid_port(self) -> None:
        """Test serve with invalid port number."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "99999"])

        # Click should validate port range
        assert result.exit_code != 0
