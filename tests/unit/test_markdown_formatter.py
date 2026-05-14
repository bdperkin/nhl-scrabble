"""Unit tests for MarkdownFormatter class."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import MarkdownFormatter


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter class."""

    @pytest.fixture
    def formatter(self) -> MarkdownFormatter:
        """Create MarkdownFormatter instance."""
        return MarkdownFormatter()

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
        formatter: MarkdownFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test markdown formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        assert "# Test Analytics Report" in result
        assert "## Coverage Gaps" in result
        assert "| Module |" in result
        assert "src/api/client.py" in result
        assert "85.5%" in result
        assert "HIGH" in result

    def test_format_slow_tests(
        self,
        formatter: MarkdownFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test markdown formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        assert "## Slowest Tests" in result
        assert "test_api_fetch" in result
        assert "2.45s" in result

    def test_format_flaky_tests(
        self,
        formatter: MarkdownFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test markdown formatting of flaky tests."""
        data = {"flaky_tests": sample_tests}
        result = formatter.format(data)

        assert "## Flaky Tests" in result
        assert "test_api_fetch" in result
        assert "0.123" in result  # Flakiness score
        assert "5.0%" in result  # Failure rate

    def test_format_trends(
        self,
        formatter: MarkdownFormatter,
    ) -> None:
        """Test markdown formatting of coverage trends."""
        data = {
            "coverage_trend": "improving",
            "coverage_history": [
                {"coverage": 90.0, "timestamp": "2026-05-01"},
                {"coverage": 85.0, "timestamp": "2026-04-01"},
            ],
        }
        result = formatter.format(data)

        assert "## Coverage Trends" in result
        assert "📈" in result
        assert "IMPROVING" in result
        assert "90.0%" in result

    def test_format_empty_data(
        self,
        formatter: MarkdownFormatter,
    ) -> None:
        """Test markdown formatting with empty data."""
        data = {}
        result = formatter.format(data)

        assert "# Test Analytics Report" in result
