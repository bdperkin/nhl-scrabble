"""Integration tests for test-analytics CLI command."""

import os
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli


class TestTestAnalyticsCommand:
    """Integration tests for test-analytics command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    def test_test_analytics_without_token(self, runner: CliRunner) -> None:
        """Test error handling when CODECOV_TOKEN is missing."""
        result = runner.invoke(
            cli,
            ["test-analytics"],
            env={"CODECOV_TOKEN": ""},
        )

        assert result.exit_code == 1
        assert "CODECOV_TOKEN environment variable not set" in result.output
        assert "https://app.codecov.io/account/gh/bdperkin/access" in result.output

    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_with_token(
        self,
        mock_client_class: Mock,
        runner: CliRunner,
    ) -> None:
        """Test successful execution with valid token."""
        # Mock the client to return test data
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)

        mock_client.get_test_analytics.return_value = {"test_analytics": {"tests": []}}
        mock_client.get_coverage_report.return_value = {
            "files": [
                {
                    "name": "src/example.py",
                    "totals": {"coverage": 75.0, "lines": 100, "hits": 75},
                },
            ],
        }
        mock_client.get_coverage_trends.return_value = [
            {"commit": "abc123", "timestamp": "2024-01-01", "coverage": 85.0},
        ]

        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            ["test-analytics"],
            env={"CODECOV_TOKEN": "test-token"},
        )

        assert result.exit_code == 0
        assert "Fetching data from Codecov API" in result.output
        assert "Coverage Gaps" in result.output or "Analysis complete" in result.output

    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_show_gaps_only(
        self,
        mock_client_class: Mock,
        runner: CliRunner,
    ) -> None:
        """Test showing only coverage gaps."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)

        mock_client.get_test_analytics.return_value = {"test_analytics": {"tests": []}}
        mock_client.get_coverage_report.return_value = {
            "files": [
                {
                    "name": "src/low_coverage.py",
                    "totals": {"coverage": 50.0, "lines": 100, "hits": 50},
                },
            ],
        }
        mock_client.get_coverage_trends.return_value = []

        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            ["test-analytics", "--show-gaps"],
            env={"CODECOV_TOKEN": "test-token"},
        )

        assert result.exit_code == 0
        assert "Coverage Gaps" in result.output

    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_json_output(
        self,
        mock_client_class: Mock,
        runner: CliRunner,
    ) -> None:
        """Test JSON format output."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)

        mock_client.get_test_analytics.return_value = {"test_analytics": {"tests": []}}
        mock_client.get_coverage_report.return_value = {"files": []}
        mock_client.get_coverage_trends.return_value = [
            {"commit": "abc123", "timestamp": "2024-01-01", "coverage": 85.0},
        ]

        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "json"],
            env={"CODECOV_TOKEN": "test-token"},
        )

        assert result.exit_code == 0
        # JSON output should contain valid JSON
        assert "{" in result.output
        assert "}" in result.output

    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_file_output(
        self,
        mock_client_class: Mock,
        runner: CliRunner,
        tmp_path: pytest.TempPathFactory,
    ) -> None:
        """Test output to file."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)

        mock_client.get_test_analytics.return_value = {"test_analytics": {"tests": []}}
        mock_client.get_coverage_report.return_value = {"files": []}
        mock_client.get_coverage_trends.return_value = [
            {"commit": "abc123", "timestamp": "2024-01-01", "coverage": 85.0},
        ]

        mock_client_class.return_value = mock_client

        output_file = tmp_path / "analytics.json"

        result = runner.invoke(
            cli,
            ["test-analytics", "--format", "json", "-o", str(output_file)],
            env={"CODECOV_TOKEN": "test-token"},
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Analytics report saved to" in result.output

    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_custom_target_coverage(
        self,
        mock_client_class: Mock,
        runner: CliRunner,
    ) -> None:
        """Test custom target coverage percentage."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)

        mock_client.get_test_analytics.return_value = {"test_analytics": {"tests": []}}
        mock_client.get_coverage_report.return_value = {
            "files": [
                {
                    "name": "src/example.py",
                    "totals": {"coverage": 85.0, "lines": 100, "hits": 85},
                },
            ],
        }
        mock_client.get_coverage_trends.return_value = []

        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            ["test-analytics", "--show-gaps", "--target-coverage", "95"],
            env={"CODECOV_TOKEN": "test-token"},
        )

        assert result.exit_code == 0
        # With 85% coverage and 95% target, should show a gap
        assert "Coverage Gaps" in result.output

    @patch("nhl_scrabble.analytics.codecov_client.CodecovClient")
    def test_test_analytics_api_error(
        self,
        mock_client_class: Mock,
        runner: CliRunner,
    ) -> None:
        """Test error handling when API request fails."""
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)

        # Simulate API error
        mock_client.get_test_analytics.side_effect = Exception("API Error")

        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            ["test-analytics"],
            env={"CODECOV_TOKEN": "test-token"},
        )

        assert result.exit_code == 1
        assert "Error:" in result.output

    def test_test_analytics_help(self, runner: CliRunner) -> None:
        """Test command help text."""
        result = runner.invoke(cli, ["test-analytics", "--help"])

        assert result.exit_code == 0
        assert "Analyze test analytics and coverage data from Codecov" in result.output
        assert "--show-gaps" in result.output
        assert "--show-slow-tests" in result.output
        assert "--show-flaky-tests" in result.output
        assert "--show-trends" in result.output
        assert "--format" in result.output
        assert "--output" in result.output
        assert "--target-coverage" in result.output


# Real integration test (only runs if CODECOV_TOKEN is set)
@pytest.mark.skipif(
    not os.getenv("CODECOV_TOKEN"),
    reason="Requires CODECOV_TOKEN environment variable for real API access",
)
class TestTestAnalyticsRealAPI:
    """Real API integration tests (requires CODECOV_TOKEN)."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    def test_test_analytics_real_api(self, runner: CliRunner) -> None:
        """Test with real Codecov API (integration test)."""
        result = runner.invoke(cli, ["test-analytics", "--show-gaps"])

        # Should succeed if token is valid
        assert result.exit_code == 0
        assert "Coverage Gaps" in result.output or "Fetching data" in result.output
