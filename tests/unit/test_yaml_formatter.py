"""Unit tests for YAMLFormatter class."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import YAMLFormatter


class TestYAMLFormatter:
    """Tests for YAMLFormatter class."""

    @pytest.fixture
    def formatter(self) -> YAMLFormatter:
        """Create YAMLFormatter instance."""
        return YAMLFormatter()

    @pytest.fixture
    def sample_gaps(self) -> list[CoverageGap]:
        """Create sample coverage gaps."""
        return [
            CoverageGap(
                module="src/api/client.py",
                current_coverage=85.5,
                target_coverage=90.0,
                lines_needed=12,
                priority="high",
            ),
        ]

    @pytest.fixture
    def sample_tests(self) -> list[TestPerformance]:
        """Create sample test performance data."""
        return [
            TestPerformance(
                test_name="test_api_fetch",
                avg_duration=2.45,
                max_duration=3.21,
                min_duration=1.89,
                failure_rate=0.05,
                flakiness_score=0.123,
            ),
        ]

    def test_format_coverage_gaps(
        self,
        formatter: YAMLFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test YAML formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        # Parse YAML and verify structure
        import yaml

        parsed = yaml.safe_load(result)

        assert "coverage_gaps" in parsed
        assert len(parsed["coverage_gaps"]) == 1
        assert parsed["coverage_gaps"][0]["module"] == "src/api/client.py"
        assert parsed["coverage_gaps"][0]["current_coverage"] == 85.5
        assert parsed["coverage_gaps"][0]["priority"] == "high"

    def test_format_slow_tests(
        self,
        formatter: YAMLFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test YAML formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        import yaml

        parsed = yaml.safe_load(result)

        assert "slow_tests" in parsed
        assert len(parsed["slow_tests"]) == 1
        assert parsed["slow_tests"][0]["test_name"] == "test_api_fetch"
        assert parsed["slow_tests"][0]["avg_duration"] == 2.45

    def test_format_empty_data(
        self,
        formatter: YAMLFormatter,
    ) -> None:
        """Test YAML formatting with empty data."""
        from typing import Any

        data: dict[str, Any] = {}
        result = formatter.format(data)

        assert result == "{}\n"

    def test_format_flaky_tests(
        self,
        formatter: YAMLFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test YAML formatting of flaky tests."""
        data = {"flaky_tests": sample_tests}
        result = formatter.format(data)

        import yaml

        parsed = yaml.safe_load(result)

        assert "flaky_tests" in parsed
        assert len(parsed["flaky_tests"]) == 1
        assert parsed["flaky_tests"][0]["test_name"] == "test_api_fetch"
        assert parsed["flaky_tests"][0]["flakiness_score"] == 0.123
        assert parsed["flaky_tests"][0]["failure_rate"] == 0.05

    def test_format_coverage_trend(
        self,
        formatter: YAMLFormatter,
    ) -> None:
        """Test YAML formatting of coverage trend."""
        trend_data = {
            "direction": "increasing",
            "change_rate": 0.5,
            "recent_values": [85.0, 87.5, 90.0],
        }
        data = {"coverage_trend": trend_data}
        result = formatter.format(data)

        import yaml

        parsed = yaml.safe_load(result)

        assert "coverage_trend" in parsed
        assert parsed["coverage_trend"]["direction"] == "increasing"
        assert parsed["coverage_trend"]["change_rate"] == 0.5

    def test_format_coverage_history(
        self,
        formatter: YAMLFormatter,
    ) -> None:
        """Test YAML formatting of coverage history."""
        history_data = [
            {"date": "2024-01-01", "coverage": 85.0},
            {"date": "2024-01-02", "coverage": 87.5},
        ]
        data = {"coverage_history": history_data}
        result = formatter.format(data)

        import yaml

        parsed = yaml.safe_load(result)

        assert "coverage_history" in parsed
        assert len(parsed["coverage_history"]) == 2
        assert parsed["coverage_history"][0]["date"] == "2024-01-01"
        assert parsed["coverage_history"][0]["coverage"] == 85.0

    def test_format_combined_data(
        self,
        formatter: YAMLFormatter,
        sample_gaps: list[CoverageGap],
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test YAML formatting with multiple data types."""
        data = {
            "coverage_gaps": sample_gaps,
            "slow_tests": sample_tests,
            "flaky_tests": sample_tests,
            "coverage_trend": {
                "direction": "stable",
                "change_rate": 0.0,
            },
            "coverage_history": [{"date": "2024-01-01", "coverage": 90.0}],
        }
        result = formatter.format(data)

        import yaml

        parsed = yaml.safe_load(result)

        assert "coverage_gaps" in parsed
        assert "slow_tests" in parsed
        assert "flaky_tests" in parsed
        assert "coverage_trend" in parsed
        assert "coverage_history" in parsed
        assert len(parsed["coverage_gaps"]) == 1
        assert len(parsed["slow_tests"]) == 1
        assert len(parsed["flaky_tests"]) == 1
