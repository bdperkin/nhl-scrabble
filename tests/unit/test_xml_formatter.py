"""Unit tests for XMLFormatter class."""

import xml.etree.ElementTree as ET

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters import XMLFormatter


class TestXMLFormatter:
    """Tests for XMLFormatter class."""

    @pytest.fixture
    def formatter(self) -> XMLFormatter:
        """Create XMLFormatter instance."""
        return XMLFormatter()

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
        formatter: XMLFormatter,
        sample_gaps: list[CoverageGap],
    ) -> None:
        """Test XML formatting of coverage gaps."""
        data = {"coverage_gaps": sample_gaps}
        result = formatter.format(data)

        # Parse XML and verify structure
        root = ET.fromstring(  # noqa: S314  # parsing our own generated XML, not untrusted data
            result,
        )

        assert root.tag == "test_analytics"
        gaps = root.find("coverage_gaps")
        assert gaps is not None
        assert len(gaps.findall("gap")) == 1

        gap = gaps.find("gap")
        assert gap is not None
        assert gap.find("module").text == "src/api/client.py"  # type: ignore[union-attr]
        assert gap.find("current_coverage").text == "85.5"  # type: ignore[union-attr]
        assert gap.find("priority").text == "high"  # type: ignore[union-attr]

    def test_format_slow_tests(
        self,
        formatter: XMLFormatter,
        sample_tests: list[TestPerformance],
    ) -> None:
        """Test XML formatting of slow tests."""
        data = {"slow_tests": sample_tests}
        result = formatter.format(data)

        root = ET.fromstring(  # noqa: S314  # parsing our own generated XML, not untrusted data
            result,
        )
        tests = root.find("slow_tests")
        assert tests is not None
        assert len(tests.findall("test")) == 1

    def test_format_empty_data(
        self,
        formatter: XMLFormatter,
    ) -> None:
        """Test XML formatting with empty data."""
        data = {}
        result = formatter.format(data)

        root = ET.fromstring(  # noqa: S314  # parsing our own generated XML, not untrusted data
            result,
        )
        assert root.tag == "test_analytics"
        # Should have no child elements
        assert len(list(root)) == 0
