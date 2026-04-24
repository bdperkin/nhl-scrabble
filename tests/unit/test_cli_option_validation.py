"""Tests for CLI option validation via Click IntRange.

This module tests the standardized CLI option validation introduced in task refactoring/012-cli-
options-audit. Tests verify that numeric options use Click's IntRange for immediate validation
feedback.
"""

from unittest.mock import patch

from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestTopPlayersValidation:
    """Tests for --top-players option validation (IntRange: 1-100)."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_top_players_valid_min(self, mock_run):
        """Test --top-players accepts minimum value (1)."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "1"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_top_players_valid_max(self, mock_run):
        """Test --top-players accepts maximum value (100)."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "100"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_top_players_valid_mid(self, mock_run):
        """Test --top-players accepts middle value (50)."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "50"])
        assert result.exit_code == 0

    def test_top_players_invalid_zero(self):
        """Test --top-players rejects 0 (below min)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "0"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_top_players_invalid_negative(self):
        """Test --top-players rejects negative value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "-10"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_top_players_invalid_too_large(self):
        """Test --top-players rejects value above max (101)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "101"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_top_players_invalid_way_too_large(self):
        """Test --top-players rejects extremely large value (10000)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-players", "10000"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output


class TestTopTeamPlayersValidation:
    """Tests for --top-team-players option validation (IntRange: 1-50)."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_top_team_players_valid_min(self, mock_run):
        """Test --top-team-players accepts minimum value (1)."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "1"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.cli.run_analysis")
    def test_top_team_players_valid_max(self, mock_run):
        """Test --top-team-players accepts maximum value (50)."""
        mock_run.return_value = "Test output"
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "50"])
        assert result.exit_code == 0

    def test_top_team_players_invalid_zero(self):
        """Test --top-team-players rejects 0."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "0"])
        assert result.exit_code != 0

    def test_top_team_players_invalid_too_large(self):
        """Test --top-team-players rejects value above max (51)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--top-team-players", "51"])
        assert result.exit_code != 0


class TestSearchLimitValidation:
    """Tests for search --limit option validation (IntRange: 1-500)."""

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_limit_valid_min(self, mock_client, mock_processor):
        """Test --limit accepts minimum value (1)."""
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--limit", "1", "--quiet"])
        assert result.exit_code == 0

    @patch("nhl_scrabble.di.TeamProcessor")
    @patch("nhl_scrabble.di.NHLApiClient")
    def test_limit_valid_max(self, mock_client, mock_processor):
        """Test --limit accepts maximum value (500)."""
        mock_processor.return_value.process_all_teams.return_value = ({}, [], [])
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--limit", "500", "--quiet"])
        assert result.exit_code == 0

    def test_limit_invalid_zero(self):
        """Test --limit rejects 0."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--limit", "0"])
        assert result.exit_code != 0

    def test_limit_invalid_negative(self):
        """Test --limit rejects negative value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--limit", "-5"])
        assert result.exit_code != 0

    def test_limit_invalid_too_large(self):
        """Test --limit rejects value above max (501)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "--limit", "501"])
        assert result.exit_code != 0


class TestServePortValidation:
    """Tests for serve --port option validation (IntRange: 1-65535)."""

    @patch("uvicorn.run")
    def test_port_valid_min(self, mock_uvicorn):
        """Test --port accepts minimum value (1)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "1"])
        # Port validation should pass
        assert "not in the range" not in result.output

    @patch("uvicorn.run")
    def test_port_valid_default(self, mock_uvicorn):
        """Test --port accepts default value (8000)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "8000"])
        assert "not in the range" not in result.output

    @patch("uvicorn.run")
    def test_port_valid_max(self, mock_uvicorn):
        """Test --port accepts maximum value (65535)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "65535"])
        assert "not in the range" not in result.output

    def test_port_invalid_zero(self):
        """Test --port rejects 0."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "0"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_port_invalid_negative(self):
        """Test --port rejects negative value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "-1"])
        assert result.exit_code != 0

    def test_port_invalid_too_large(self):
        """Test --port rejects value above max (65536)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--port", "65536"])
        assert result.exit_code != 0
        assert "not in the range" in result.output


class TestWatchIntervalValidation:
    """Tests for watch --interval option validation (IntRange: 1+)."""

    @patch("nhl_scrabble.cli.run_analysis")
    def test_interval_valid_min(self, mock_run):
        """Test --interval accepts minimum value (1)."""
        # Make command exit immediately by raising KeyboardInterrupt
        mock_run.side_effect = KeyboardInterrupt
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "1"])
        # Should exit cleanly (0) from KeyboardInterrupt handling
        # Interval validation should pass (no "not in the range")
        assert "not in the range" not in result.output

    @patch("nhl_scrabble.cli.run_analysis")
    def test_interval_valid_default(self, mock_run):
        """Test --interval accepts default value (300)."""
        mock_run.side_effect = KeyboardInterrupt
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "300"])
        assert "not in the range" not in result.output

    @patch("nhl_scrabble.cli.run_analysis")
    def test_interval_valid_large(self, mock_run):
        """Test --interval accepts large value (86400 = 1 day)."""
        mock_run.side_effect = KeyboardInterrupt
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "86400"])
        assert "not in the range" not in result.output

    def test_interval_invalid_zero(self):
        """Test --interval rejects 0."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "0"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_interval_invalid_negative(self):
        """Test --interval rejects negative value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["watch", "--interval", "-10"])
        assert result.exit_code != 0


class TestDashboardDurationValidation:
    """Tests for dashboard --duration option validation (IntRange: 1+)."""

    def test_duration_valid_min(self):
        """Test --duration accepts minimum value (1)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--duration", "1", "--static"])
        # May fail for other reasons, but not duration validation
        assert "not in the range" not in result.output or result.exit_code != 2

    def test_duration_valid_typical(self):
        """Test --duration accepts typical value (60)."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--duration", "60", "--static"])
        assert "not in the range" not in result.output or result.exit_code != 2

    def test_duration_invalid_zero(self):
        """Test --duration rejects 0."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--duration", "0"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "not in the range" in result.output

    def test_duration_invalid_negative(self):
        """Test --duration rejects negative value."""
        runner = CliRunner()
        result = runner.invoke(cli, ["dashboard", "--duration", "-30"])
        assert result.exit_code != 0
