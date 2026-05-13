"""Unit tests for CSVFormatter class."""

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import CSVFormatter


class TestCSVFormatter:
    """Tests for CSVFormatter class."""

    @pytest.fixture
    def formatter(self) -> CSVFormatter:
        """Create CSVFormatter instance."""
        return CSVFormatter()

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
        formatter: CSVFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test CSV formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        lines = result.strip().split("\n")

        # Check header
        assert "section" in lines[0]
        assert "module" in lines[0]

        # Check data
        assert "coverage_gaps" in lines[1]
        assert "src/api/client.py" in lines[1]
        assert "85.5" in lines[1]

    def test_format_slow_tests(
        self,
        formatter: CSVFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test CSV formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        lines = result.strip().split("\n")

        # Check data
        assert "slow_tests" in lines[1]
        assert "test_api_fetch" in lines[1]
        assert "2.45" in lines[1]

    def test_format_empty_data(
        self,
        formatter: CSVFormatter,
    ) -> None:
        """Test CSV formatting with empty data."""
        data = {}
        result = formatter.format(data)

        lines = result.strip().split("\n")
        # Should only have header
        assert len(lines) == 1
        assert "section" in lines[0]
