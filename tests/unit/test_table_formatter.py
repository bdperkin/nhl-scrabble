"""Unit tests for TableFormatter class."""

from importlib.util import find_spec

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import TableFormatter

# Skip all tests if tabulate (optional dependency) is not installed
pytestmark = pytest.mark.skipif(
    find_spec("tabulate") is None,
    reason="tabulate not found (optional 'export' dependencies not installed)",
)


class TestTableFormatter:
    """Tests for TableFormatter class."""

    @pytest.fixture
    def formatter(self) -> TableFormatter:
        """Create TableFormatter instance."""
        return TableFormatter()

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
        formatter: TableFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test table formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        assert "Coverage Gaps" in result
        assert "src/api/client.py" in result
        assert "85.5%" in result
        assert "HIGH" in result
        assert "+" in result  # Grid table borders

    def test_format_slow_tests(
        self,
        formatter: TableFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test table formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        assert "Slowest Tests" in result
        assert "test_api_fetch" in result
        assert "2.45s" in result

    def test_format_empty_data(
        self,
        formatter: TableFormatter,
    ) -> None:
        """Test table formatting with empty data."""
        data = {}
        result = formatter.format(data)

        # Empty string expected
        assert result == ""
