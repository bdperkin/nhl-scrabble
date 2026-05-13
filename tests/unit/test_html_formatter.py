"""Unit tests for HTMLFormatter class."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import HTMLFormatter


class TestHTMLFormatter:
    """Tests for HTMLFormatter class."""

    @pytest.fixture
    def formatter(self) -> HTMLFormatter:
        """Create HTMLFormatter instance."""
        return HTMLFormatter()

    @pytest.fixture
    def sample_gaps(self) -> list[CoverageGap]:
        """Create sample coverage gaps."""
        return [
            CoverageGap(
                module="src/test.py",
                current_coverage=60.0,
                target_coverage=90.0,
                lines_needed=30,
                priority="high",
            ),
        ]

    @pytest.fixture
    def sample_tests(self) -> list[TestPerformance]:
        """Create sample test performance data."""
        return [
            TestPerformance(
                test_name="test_slow",
                avg_duration=3.5,
                max_duration=7.0,
                min_duration=2.0,
                failure_rate=0.15,
                flakiness_score=0.6,
            ),
        ]

    def test_format_coverage_gaps_html(
        self,
        formatter: HTMLFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test HTML formatting of coverage gaps."""
        result = formatter._format_coverage_gaps_html(sample_gaps)

        assert "<h2>Coverage Gaps</h2>" in result
        assert "<table>" in result
        assert "src/test.py" in result
        assert "60.0%" in result
        assert "90.0%" in result
        assert "30" in result
        assert 'class="high"' in result
        assert "HIGH" in result

    def test_format_coverage_gaps_html_truncates_at_20(
        self,
        formatter: HTMLFormatter,
    ) -> None:
        """Test HTML coverage gaps are truncated to 20 items."""
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

        result = formatter._format_coverage_gaps_html(gaps)

        assert "module_0.py" in result
        assert "module_19.py" in result
        assert "module_20.py" not in result

    def test_format_slow_tests_html(
        self,
        formatter: HTMLFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test HTML formatting of slow tests."""
        result = formatter._format_slow_tests_html(sample_tests)

        assert "<h2>Slowest Tests</h2>" in result
        assert "<table>" in result
        assert "test_slow" in result
        assert "3.50s" in result
        assert "7.00s" in result
        assert "15.0%" in result

    def test_format_flaky_tests_html(
        self,
        formatter: HTMLFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test HTML formatting of flaky tests."""
        result = formatter._format_flaky_tests_html(sample_tests)

        assert "<h2>Flaky Tests</h2>" in result
        assert "<table>" in result
        assert "test_slow" in result
        assert "0.600" in result
        assert "15.0%" in result

    def test_format_trends_html_improving(
        self,
        formatter: HTMLFormatter,
    ) -> None:
        """Test HTML formatting of improving trend."""
        history = [
            {"coverage": 85.0, "commit": "abc"},
            {"coverage": 80.0, "commit": "def"},
        ]

        result = formatter._format_trends_html("improving", history)

        assert "<h2>Coverage Trends</h2>" in result
        assert "📈" in result
        assert "IMPROVING" in result
        assert "85.0%" in result
        assert "+5.0%" in result

    def test_format_trends_html_declining(
        self,
        formatter: HTMLFormatter,
    ) -> None:
        """Test HTML formatting of declining trend."""
        history = [
            {"coverage": 75.0, "commit": "abc"},
            {"coverage": 80.0, "commit": "def"},
        ]

        result = formatter._format_trends_html("declining", history)

        assert "📉" in result
        assert "DECLINING" in result
        assert "-5.0%" in result

    def test_format_trends_html_stable(
        self,
        formatter: HTMLFormatter,
    ) -> None:
        """Test HTML formatting of stable trend."""
        history = [{"coverage": 85.0, "commit": "abc"}]

        result = formatter._format_trends_html("stable", history)

        assert "➡️" in result
        assert "STABLE" in result

    def test_format_trends_html_empty_history(
        self,
        formatter: HTMLFormatter,
    ) -> None:
        """Test HTML formatting with empty history."""
        result = formatter._format_trends_html("insufficient_data", [])

        assert "❓" in result
        assert "0.0%" in result

    def test_format_complete_html(
        self,
        formatter: HTMLFormatter,
        sample_gaps: list[CoverageGap],
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test complete HTML report generation."""
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

        # Check HTML structure
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "<head>" in result
        assert "<title>Test Analytics Report</title>" in result
        assert "<style>" in result
        assert "<body>" in result
        assert "<h1>Test Analytics Report</h1>" in result

        # Check all sections are included
        assert "Coverage Gaps" in result
        assert "Slowest Tests" in result
        assert "Flaky Tests" in result
        assert "Coverage Trends" in result

        # Check CSS is present
        assert "border-collapse" in result
        assert ".high" in result
        assert ".medium" in result
        assert ".low" in result

    def test_format_partial_html(
        self,
        formatter: HTMLFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test HTML formatting with only some data fields."""
        data = {"coverage_gaps": sample_gaps}

        result = formatter.format(data)

        assert "Coverage Gaps" in result
        assert "Slowest Tests" not in result
        assert "<!DOCTYPE html>" in result

    def test_format_empty_html(
        self,
        formatter: HTMLFormatter,
    ) -> None:
        """Test HTML formatting with no data."""
        data = {}
        result = formatter.format(data)

        # Should still have valid HTML structure
        assert "<!DOCTYPE html>" in result
        assert "<h1>Test Analytics Report</h1>" in result
        assert "</html>" in result
