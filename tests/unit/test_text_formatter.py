"""Unit tests for TextFormatter class."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import TextFormatter


class TestTextFormatter:
    """Tests for TextFormatter class."""

    @pytest.fixture
    def formatter(self) -> TextFormatter:
        """Create TextFormatter instance."""
        return TextFormatter()

    @pytest.fixture
    def sample_gaps(self) -> list[CoverageGap]:
        """Create sample coverage gaps."""
        return [
            CoverageGap(
                module="src/high_priority.py",
                current_coverage=50.0,
                target_coverage=90.0,
                lines_needed=40,
                priority="high",
            ),
            CoverageGap(
                module="src/medium_priority.py",
                current_coverage=75.0,
                target_coverage=90.0,
                lines_needed=15,
                priority="medium",
            ),
            CoverageGap(
                module="src/low_priority.py",
                current_coverage=85.0,
                target_coverage=90.0,
                lines_needed=5,
                priority="low",
            ),
        ]

    @pytest.fixture
    def sample_tests(self) -> list[TestPerformance]:
        """Create sample test performance data."""
        return [
            TestPerformance(
                test_name="test_slow_operation",
                avg_duration=5.5,
                max_duration=10.0,
                min_duration=3.0,
                failure_rate=0.1,
                flakiness_score=0.8,
            ),
            TestPerformance(
                test_name="test_flaky_test",
                avg_duration=1.0,
                max_duration=2.0,
                min_duration=0.5,
                failure_rate=0.3,
                flakiness_score=0.95,
            ),
        ]

    def test_format_coverage_gaps(
        self,
        formatter: TextFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test formatting coverage gaps."""
        result = formatter._format_coverage_gaps(sample_gaps)

        assert "Coverage Gaps" in result
        assert "src/high_priority.py" in result
        assert "50.0%" in result
        assert "90.0%" in result
        assert "HIGH" in result
        assert "MEDIUM" in result
        assert "LOW" in result

    def test_format_coverage_gaps_truncates_at_20(
        self,
        formatter: TextFormatter,
    ) -> None:
        """Test coverage gaps are truncated to 20 items."""
        gaps = [
            CoverageGap(
                module=f"module_{i}.py",
                current_coverage=50.0,
                target_coverage=90.0,
                lines_needed=40,
                priority="high",
            )
            for i in range(30)
        ]

        result = formatter._format_coverage_gaps(gaps)

        # Should only show first 20
        assert "module_0.py" in result
        assert "module_19.py" in result
        assert "module_20.py" not in result

    def test_format_slow_tests(
        self,
        formatter: TextFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test formatting slow tests."""
        result = formatter._format_slow_tests(sample_tests)

        assert "Slowest Tests" in result
        assert "test_slow_operation" in result
        assert "5.50s" in result
        assert "10.00s" in result
        assert "10.0%" in result  # failure rate

    def test_format_flaky_tests(
        self,
        formatter: TextFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test formatting flaky tests."""
        result = formatter._format_flaky_tests(sample_tests)

        assert "Flaky Tests" in result
        assert "test_flaky_test" in result
        assert "0.950" in result  # flakiness score
        assert "30.0%" in result  # failure rate

    def test_format_trends_improving(
        self,
        formatter: TextFormatter,
    ) -> None:
        """Test formatting improving coverage trend."""
        history = [
            {"coverage": 85.0, "commit": "abc123"},
            {"coverage": 82.0, "commit": "def456"},
            {"coverage": 80.0, "commit": "ghi789"},
        ]

        result = formatter._format_trends("improving", history)

        assert "Coverage Trends" in result
        assert "IMPROVING" in result
        assert "85.0%" in result
        assert "+5.0%" in result  # change from 80 to 85

    def test_format_trends_declining(
        self,
        formatter: TextFormatter,
    ) -> None:
        """Test formatting declining coverage trend."""
        history = [
            {"coverage": 80.0, "commit": "abc123"},
            {"coverage": 85.0, "commit": "def456"},
        ]

        result = formatter._format_trends("declining", history)

        assert "DECLINING" in result
        assert "80.0%" in result
        assert "-5.0%" in result

    def test_format_trends_stable(
        self,
        formatter: TextFormatter,
    ) -> None:
        """Test formatting stable coverage trend."""
        history = [
            {"coverage": 85.0, "commit": "abc123"},
            {"coverage": 85.5, "commit": "def456"},
        ]

        result = formatter._format_trends("stable", history)

        assert "STABLE" in result
        assert "85.0%" in result

    def test_format_trends_insufficient_data(
        self,
        formatter: TextFormatter,
    ) -> None:
        """Test formatting with insufficient data."""
        history = [{"coverage": 85.0, "commit": "abc123"}]

        result = formatter._format_trends("insufficient_data", history)

        assert "INSUFFICIENT_DATA" in result

    def test_format_trends_empty_history(
        self,
        formatter: TextFormatter,
    ) -> None:
        """Test formatting with empty history."""
        result = formatter._format_trends("insufficient_data", [])

        assert "0.0%" in result

    def test_format_complete_report(
        self,
        formatter: TextFormatter,
        sample_gaps: list[CoverageGap],
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test formatting complete analytics report."""
        data = {
            "coverage_gaps": sample_gaps,
            "slow_tests": sample_tests,
            "flaky_tests": sample_tests,
            "coverage_trend": "improving",
            "coverage_history": [
                {"coverage": 85.0, "commit": "abc"},
                {"coverage": 80.0, "commit": "def"},
            ],
        }

        result = formatter.format(data)

        # All sections should be present
        assert "Coverage Gaps" in result
        assert "Slowest Tests" in result
        assert "Flaky Tests" in result
        assert "Coverage Trends" in result

    def test_format_partial_data(
        self,
        formatter: TextFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test formatting with only some data fields."""
        data = {"coverage_gaps": sample_gaps}

        result = formatter.format(data)

        assert "Coverage Gaps" in result
        assert "Slowest Tests" not in result
