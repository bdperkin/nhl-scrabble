"""Comprehensive unit tests for CLI test-analytics command.

This module tests the test-analytics command for fetching and analyzing
test coverage data from Codecov API.

Target: Improve coverage of test-analytics command (lines 1920-2001)
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

# CRITICAL: Import cli module directly to ensure coverage
from nhl_scrabble.cli import cli

if TYPE_CHECKING:
    from pathlib import Path


class TestAnalyticsCommandBasics:
    """Test basic test-analytics command functionality."""

    def test_test_analytics_missing_token(self) -> None:
        """Test test-analytics fails without CODECOV_TOKEN."""
        runner = CliRunner()

        with patch("nhl_scrabble.analytics.codecov_client.CodecovConfig") as mock_config_class:
            mock_config = MagicMock()
            mock_config.token = None
            mock_config_class.from_env.return_value = mock_config

            result = runner.invoke(cli, ["test-analytics"])

            assert result.exit_code == 1
            assert "CODECOV_TOKEN" in result.output
            assert "not set" in result.output.lower()

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_default_all_sections(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics shows all sections by default."""
        # Setup config
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        # Setup client
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = [{"commit": "abc", "coverage": 90}]
        mock_client_class.return_value = mock_client

        # Setup analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.return_value = []
        mock_analyzer.analyze_test_performance.return_value = []
        mock_analyzer.get_coverage_trend.return_value = {"trend": "up"}
        mock_analyzer_class.return_value = mock_analyzer

        # Setup formatter
        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Test analytics report"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics"])

        assert result.exit_code == 0
        assert "Test analytics report" in result.output
        # Verify all analyses were called (default shows all)
        assert mock_analyzer.find_coverage_gaps.called
        assert mock_analyzer.analyze_test_performance.called
        assert mock_analyzer.get_coverage_trend.called

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_show_gaps_only(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with --show-gaps flag."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.return_value = [
            {"file": "test.py", "coverage": 50, "target": 90},
        ]
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Coverage gaps report"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--show-gaps"])

        assert result.exit_code == 0
        assert mock_analyzer.find_coverage_gaps.called

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_show_slow_tests(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with --show-slow-tests flag."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_perf = MagicMock()
        mock_perf.test_name = "slow_test"
        mock_perf.duration = 10.5
        mock_analyzer.analyze_test_performance.return_value = [mock_perf]
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Slow tests report"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--show-slow-tests"])

        assert result.exit_code == 0
        assert mock_analyzer.analyze_test_performance.called

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_show_flaky_tests(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with --show-flaky-tests flag."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_perf = MagicMock()
        mock_perf.test_name = "flaky_test"
        mock_perf.flakiness_score = 0.5
        mock_analyzer.analyze_test_performance.return_value = [mock_perf]
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Flaky tests report"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--show-flaky-tests"])

        assert result.exit_code == 0
        assert mock_analyzer.analyze_test_performance.called

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_show_trends(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with --show-trends flag."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = [{"commit": "abc", "coverage": 91}]
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.get_coverage_trend.return_value = {"trend": "improving"}
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Coverage trends report"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--show-trends"])

        assert result.exit_code == 0
        assert mock_analyzer.get_coverage_trend.called


class TestAnalyticsCommandOutputFormats:
    """Test test-analytics output format options."""

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.JSONFormatter")
    def test_test_analytics_json_format(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with JSON output format."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.return_value = []
        mock_analyzer.analyze_test_performance.return_value = []
        mock_analyzer.get_coverage_trend.return_value = {}
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = '{"result": "json"}'
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--format", "json"])

        assert result.exit_code == 0
        assert mock_formatter_class.called
        assert mock_formatter.format.called

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.HTMLFormatter")
    def test_test_analytics_html_format(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with HTML output format."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.return_value = []
        mock_analyzer.analyze_test_performance.return_value = []
        mock_analyzer.get_coverage_trend.return_value = {}
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "<html>report</html>"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--format", "html"])

        assert result.exit_code == 0
        assert mock_formatter_class.called

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_with_output_file(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test test-analytics writes to output file."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.return_value = []
        mock_analyzer.analyze_test_performance.return_value = []
        mock_analyzer.get_coverage_trend.return_value = {}
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Analytics report content"
        mock_formatter_class.return_value = mock_formatter

        output_file = tmp_path / "analytics.txt"
        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Analytics report content" in output_file.read_text()

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    @patch("nhl_scrabble.analytics.formatters.TextFormatter")
    def test_test_analytics_with_custom_target_coverage(
        self,
        mock_formatter_class: MagicMock,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics with custom target coverage."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.return_value = []
        mock_analyzer.analyze_test_performance.return_value = []
        mock_analyzer.get_coverage_trend.return_value = {}
        mock_analyzer_class.return_value = mock_analyzer

        mock_formatter = MagicMock()
        mock_formatter.format.return_value = "Report"
        mock_formatter_class.return_value = mock_formatter

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics", "--target-coverage", "95"])

        assert result.exit_code == 0
        # Verify target coverage was passed to find_coverage_gaps
        mock_analyzer.find_coverage_gaps.assert_called_with(95.0)


class TestAnalyticsCommandErrorHandling:
    """Test test-analytics error handling."""

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_api_error(
        self,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics handles API errors gracefully."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.side_effect = Exception("API unavailable")
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics"])

        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()

    @patch("nhl_scrabble.analytics.codecov_client.CodecovConfig")
    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    @patch("nhl_scrabble.analytics.analyzer.TestAnalyzer")
    def test_test_analytics_analyzer_error(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        mock_config_class: MagicMock,
    ) -> None:
        """Test test-analytics handles analyzer errors gracefully."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.token = "test-token"  # noqa: S105
        mock_config_class.from_env.return_value = mock_config

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get_test_analytics.return_value = {"tests": []}
        mock_client.get_coverage_report.return_value = {"coverage": 90}
        mock_client.get_coverage_trends.return_value = []
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.find_coverage_gaps.side_effect = Exception("Analysis failed")
        mock_analyzer_class.return_value = mock_analyzer

        runner = CliRunner()
        result = runner.invoke(cli, ["test-analytics"])

        assert result.exit_code == 1
