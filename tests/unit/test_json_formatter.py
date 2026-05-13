"""Unit tests for JSONFormatter class."""

import json

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import JSONFormatter


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    @pytest.fixture
    def formatter(self) -> JSONFormatter:
        """Create JSONFormatter instance."""
        return JSONFormatter()

    @pytest.fixture
    def sample_gaps(self) -> list[CoverageGap]:
        """Create sample coverage gaps."""
        return [
            CoverageGap(
                module="src/test.py",
                current_coverage=75.0,
                target_coverage=90.0,
                lines_needed=15,
                priority="medium",
            ),
        ]

    @pytest.fixture
    def sample_tests(self) -> list[TestPerformance]:
        """Create sample test performance data."""
        return [
            TestPerformance(
                test_name="test_example",
                avg_duration=2.5,
                max_duration=5.0,
                min_duration=1.0,
                failure_rate=0.05,
                flakiness_score=0.3,
            ),
        ]

    def test_format_coverage_gaps(
        self,
        formatter: JSONFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test JSON formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        parsed = json.loads(result)
        assert "coverage_gaps" in parsed
        assert len(parsed["coverage_gaps"]) == 1
        assert parsed["coverage_gaps"][0]["module"] == "src/test.py"
        assert parsed["coverage_gaps"][0]["current_coverage"] == 75.0
        assert parsed["coverage_gaps"][0]["priority"] == "medium"

    def test_format_slow_tests(
        self,
        formatter: JSONFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test JSON formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        parsed = json.loads(result)
        assert "slow_tests" in parsed
        assert len(parsed["slow_tests"]) == 1
        assert parsed["slow_tests"][0]["test_name"] == "test_example"
        assert parsed["slow_tests"][0]["avg_duration"] == 2.5
        assert parsed["slow_tests"][0]["max_duration"] == 5.0
        assert parsed["slow_tests"][0]["failure_rate"] == 0.05

    def test_format_flaky_tests(
        self,
        formatter: JSONFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test JSON formatting of flaky tests."""
        data = {"flaky_tests": sample_tests}
        result = formatter.format(data)

        parsed = json.loads(result)
        assert "flaky_tests" in parsed
        assert len(parsed["flaky_tests"]) == 1
        assert parsed["flaky_tests"][0]["test_name"] == "test_example"
        assert parsed["flaky_tests"][0]["flakiness_score"] == 0.3

    def test_format_coverage_trend(
        self,
        formatter: JSONFormatter,
    ) -> None:
        """Test JSON formatting of coverage trend."""
        data = {"coverage_trend": "improving"}
        result = formatter.format(data)

        parsed = json.loads(result)
        assert "coverage_trend" in parsed
        assert parsed["coverage_trend"] == "improving"

    def test_format_coverage_history(
        self,
        formatter: JSONFormatter,
    ) -> None:
        """Test JSON formatting of coverage history."""
        history = [
            {"coverage": 85.0, "commit": "abc123"},
            {"coverage": 80.0, "commit": "def456"},
        ]
        data = {"coverage_history": history}
        result = formatter.format(data)

        parsed = json.loads(result)
        assert "coverage_history" in parsed
        assert len(parsed["coverage_history"]) == 2
        assert parsed["coverage_history"][0]["coverage"] == 85.0

    def test_format_complete_data(
        self,
        formatter: JSONFormatter,
        sample_gaps: list[CoverageGap],
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test JSON formatting of complete analytics data."""
        data = {
            "coverage_gaps": sample_gaps,
            "slow_tests": sample_tests,
            "flaky_tests": sample_tests,
            "coverage_trend": "stable",
            "coverage_history": [{"coverage": 85.0, "commit": "abc"}],
        }
        result = formatter.format(data)

        parsed = json.loads(result)
        assert "coverage_gaps" in parsed
        assert "slow_tests" in parsed
        assert "flaky_tests" in parsed
        assert "coverage_trend" in parsed
        assert "coverage_history" in parsed

    def test_format_empty_data(
        self,
        formatter: JSONFormatter,
    ) -> None:
        """Test JSON formatting with empty data."""
        data = {}
        result = formatter.format(data)

        parsed = json.loads(result)
        assert parsed == {}

    def test_format_indented_output(
        self,
        formatter: JSONFormatter,
    ) -> None:
        """Test that JSON output is properly indented."""
        data = {"coverage_trend": "improving"}
        result = formatter.format(data)

        # Should have newlines and indentation
        assert "\n" in result
        assert "  " in result
