"""Tests for analytics XML formatter."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance
from nhl_scrabble.analytics.formatters.xml_formatter import XMLFormatter


@pytest.fixture
def xml_formatter() -> XMLFormatter:
    """Provide XMLFormatter instance."""
    return XMLFormatter()


@pytest.fixture
def sample_coverage_gaps() -> list[CoverageGap]:
    """Provide sample coverage gap data."""
    return [
        CoverageGap(
            module="src/app/module1.py",
            current_coverage=75.5,
            target_coverage=90.0,
            lines_needed=25,
            priority="high",
        ),
        CoverageGap(
            module="src/app/module2.py",
            current_coverage=82.3,
            target_coverage=90.0,
            lines_needed=10,
            priority="medium",
        ),
    ]


@pytest.fixture
def sample_slow_tests() -> list[TestPerformance]:
    """Provide sample slow test data."""
    return [
        TestPerformance(
            test_name="tests/test_slow.py::test_integration",
            avg_duration=5.234,
            max_duration=6.789,
            min_duration=4.123,
            failure_rate=0.05,
            flakiness_score=0.1,
        ),
        TestPerformance(
            test_name="tests/test_another.py::test_slow_query",
            avg_duration=3.456,
            max_duration=4.567,
            min_duration=2.345,
            failure_rate=0.0,
            flakiness_score=0.0,
        ),
    ]


@pytest.fixture
def sample_flaky_tests() -> list[TestPerformance]:
    """Provide sample flaky test data."""
    return [
        TestPerformance(
            test_name="tests/test_flaky.py::test_intermittent",
            avg_duration=1.234,
            max_duration=2.345,
            min_duration=0.987,
            failure_rate=0.25,
            flakiness_score=0.5,
        ),
    ]


def test_format_empty_data(xml_formatter: XMLFormatter) -> None:
    """Test formatting empty data dictionary."""
    result = xml_formatter.format({})

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    assert root.tag == "test_analytics"
    assert len(root) == 0  # No child elements


def test_format_coverage_gaps_only(
    xml_formatter: XMLFormatter,
    sample_coverage_gaps: list[CoverageGap],
) -> None:
    """Test formatting with only coverage gaps."""
    data = {"coverage_gaps": sample_coverage_gaps}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    assert root.tag == "test_analytics"

    gaps_elem = root.find("coverage_gaps")
    assert gaps_elem is not None

    gap_elems = gaps_elem.findall("gap")
    assert len(gap_elems) == 2

    # Verify first gap
    first_gap = gap_elems[0]
    assert first_gap.find("module").text == "src/app/module1.py"
    assert first_gap.find("current_coverage").text == "75.5"
    assert first_gap.find("target_coverage").text == "90.0"
    assert first_gap.find("lines_needed").text == "25"
    assert first_gap.find("priority").text == "high"

    # Verify second gap
    second_gap = gap_elems[1]
    assert second_gap.find("module").text == "src/app/module2.py"
    assert second_gap.find("current_coverage").text == "82.3"
    assert second_gap.find("target_coverage").text == "90.0"
    assert second_gap.find("lines_needed").text == "10"
    assert second_gap.find("priority").text == "medium"


def test_format_slow_tests_only(
    xml_formatter: XMLFormatter,
    sample_slow_tests: list[TestPerformance],
) -> None:
    """Test formatting with only slow tests."""
    data = {"slow_tests": sample_slow_tests}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    tests_elem = root.find("slow_tests")
    assert tests_elem is not None

    test_elems = tests_elem.findall("test")
    assert len(test_elems) == 2

    # Verify first test
    first_test = test_elems[0]
    assert first_test.find("test_name").text == "tests/test_slow.py::test_integration"
    assert first_test.find("avg_duration").text == "5.234"
    assert first_test.find("max_duration").text == "6.789"
    assert first_test.find("min_duration").text == "4.123"
    assert first_test.find("failure_rate").text == "0.05"
    assert first_test.find("flakiness_score").text == "0.1"

    # Verify second test
    second_test = test_elems[1]
    assert second_test.find("test_name").text == "tests/test_another.py::test_slow_query"
    assert second_test.find("avg_duration").text == "3.456"
    assert second_test.find("max_duration").text == "4.567"
    assert second_test.find("min_duration").text == "2.345"
    assert second_test.find("failure_rate").text == "0.0"
    assert second_test.find("flakiness_score").text == "0.0"


def test_format_flaky_tests_only(
    xml_formatter: XMLFormatter,
    sample_flaky_tests: list[TestPerformance],
) -> None:
    """Test formatting with only flaky tests."""
    data = {"flaky_tests": sample_flaky_tests}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    flaky_elem = root.find("flaky_tests")
    assert flaky_elem is not None

    test_elems = flaky_elem.findall("test")
    assert len(test_elems) == 1

    test = test_elems[0]
    assert test.find("test_name").text == "tests/test_flaky.py::test_intermittent"
    assert test.find("flakiness_score").text == "0.5"
    assert test.find("failure_rate").text == "0.25"
    assert test.find("avg_duration").text == "1.234"


def test_format_coverage_trend_only(xml_formatter: XMLFormatter) -> None:
    """Test formatting with only coverage trend."""
    data = {"coverage_trend": "improving"}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    trend_elem = root.find("coverage_trend")
    assert trend_elem is not None
    assert trend_elem.text == "improving"


def test_format_coverage_history_only(xml_formatter: XMLFormatter) -> None:
    """Test formatting with only coverage history."""
    history = [
        {"timestamp": "2026-05-13T10:00:00", "coverage": 85.5},
        {"timestamp": "2026-05-12T10:00:00", "coverage": 84.2},
        {"timestamp": "2026-05-11T10:00:00", "coverage": 83.1},
    ]
    data = {"coverage_history": history}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    history_elem = root.find("coverage_history")
    assert history_elem is not None

    record_elems = history_elem.findall("record")
    assert len(record_elems) == 3

    # Verify first record
    first_record = record_elems[0]
    assert first_record.find("timestamp").text == "2026-05-13T10:00:00"
    assert first_record.find("coverage").text == "85.5"

    # Verify second record
    second_record = record_elems[1]
    assert second_record.find("timestamp").text == "2026-05-12T10:00:00"
    assert second_record.find("coverage").text == "84.2"

    # Verify third record
    third_record = record_elems[2]
    assert third_record.find("timestamp").text == "2026-05-11T10:00:00"
    assert third_record.find("coverage").text == "83.1"


def test_format_complete_data(
    xml_formatter: XMLFormatter,
    sample_coverage_gaps: list[CoverageGap],
    sample_slow_tests: list[TestPerformance],
    sample_flaky_tests: list[TestPerformance],
) -> None:
    """Test formatting with all data types combined."""
    history = [
        {"timestamp": "2026-05-13T10:00:00", "coverage": 85.5},
        {"timestamp": "2026-05-12T10:00:00", "coverage": 84.2},
    ]
    data = {
        "coverage_gaps": sample_coverage_gaps,
        "slow_tests": sample_slow_tests,
        "flaky_tests": sample_flaky_tests,
        "coverage_trend": "improving",
        "coverage_history": history,
    }
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    assert root.tag == "test_analytics"

    # Verify all sections are present
    assert root.find("coverage_gaps") is not None
    assert root.find("slow_tests") is not None
    assert root.find("flaky_tests") is not None
    assert root.find("coverage_trend") is not None
    assert root.find("coverage_history") is not None

    # Quick counts
    assert len(root.find("coverage_gaps").findall("gap")) == 2
    assert len(root.find("slow_tests").findall("test")) == 2
    assert len(root.find("flaky_tests").findall("test")) == 1
    assert len(root.find("coverage_history").findall("record")) == 2


def test_format_coverage_history_with_missing_fields(
    xml_formatter: XMLFormatter,
) -> None:
    """Test formatting coverage history with missing timestamp/coverage fields."""
    history = [
        {"timestamp": "2026-05-13T10:00:00"},  # Missing coverage
        {"coverage": 84.2},  # Missing timestamp
        {},  # Missing both
    ]
    data = {"coverage_history": history}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    history_elem = root.find("coverage_history")
    assert history_elem is not None

    record_elems = history_elem.findall("record")
    assert len(record_elems) == 3

    # First record - missing coverage defaults to 0
    first = record_elems[0]
    assert first.find("timestamp").text == "2026-05-13T10:00:00"
    assert first.find("coverage").text == "0"

    # Second record - missing timestamp defaults to empty string (None in ElementTree)
    second = record_elems[1]
    assert second.find("timestamp").text is None or second.find("timestamp").text == ""
    assert second.find("coverage").text == "84.2"

    # Third record - both missing
    third = record_elems[2]
    assert third.find("timestamp").text is None or third.find("timestamp").text == ""
    assert third.find("coverage").text == "0"


def test_format_returns_valid_xml_unicode(xml_formatter: XMLFormatter) -> None:
    """Test that format returns valid XML with unicode encoding."""
    data = {"coverage_trend": "improving"}
    result = xml_formatter.format(data)

    # Should be a string (unicode)
    assert isinstance(result, str)

    # Should be parseable as XML
    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    assert root is not None


def test_format_empty_coverage_gaps_list(xml_formatter: XMLFormatter) -> None:
    """Test formatting with empty coverage gaps list."""
    data = {"coverage_gaps": []}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    gaps_elem = root.find("coverage_gaps")
    assert gaps_elem is not None
    assert len(gaps_elem.findall("gap")) == 0


def test_format_empty_slow_tests_list(xml_formatter: XMLFormatter) -> None:
    """Test formatting with empty slow tests list."""
    data = {"slow_tests": []}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    tests_elem = root.find("slow_tests")
    assert tests_elem is not None
    assert len(tests_elem.findall("test")) == 0


def test_format_empty_flaky_tests_list(xml_formatter: XMLFormatter) -> None:
    """Test formatting with empty flaky tests list."""
    data = {"flaky_tests": []}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    flaky_elem = root.find("flaky_tests")
    assert flaky_elem is not None
    assert len(flaky_elem.findall("test")) == 0


def test_format_empty_coverage_history_list(xml_formatter: XMLFormatter) -> None:
    """Test formatting with empty coverage history list."""
    data = {"coverage_history": []}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    history_elem = root.find("coverage_history")
    assert history_elem is not None
    assert len(history_elem.findall("record")) == 0


def test_format_with_special_characters_in_strings(
    xml_formatter: XMLFormatter,
) -> None:
    """Test formatting with special XML characters in strings."""
    gaps = [
        CoverageGap(
            module="src/app/module<>&.py",
            current_coverage=75.5,
            target_coverage=90.0,
            lines_needed=25,
            priority="high & critical",
        ),
    ]
    data = {"coverage_gaps": gaps}
    result = xml_formatter.format(data)

    # Should be valid XML even with special characters
    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML
    gap = root.find("coverage_gaps/gap")
    assert gap is not None

    # ElementTree automatically escapes special characters
    assert gap.find("module").text == "src/app/module<>&.py"
    assert gap.find("priority").text == "high & critical"


def test_format_with_numeric_edge_cases(xml_formatter: XMLFormatter) -> None:
    """Test formatting with numeric edge cases (0, negative, very large)."""
    gaps = [
        CoverageGap(
            module="src/app/zero_coverage.py",
            current_coverage=0.0,
            target_coverage=100.0,
            lines_needed=999999,
            priority="high",
        ),
    ]
    tests = [
        TestPerformance(
            test_name="tests/test_edge.py::test_zero",
            avg_duration=0.0,
            max_duration=0.0,
            min_duration=0.0,
            failure_rate=1.0,  # 100% failure
            flakiness_score=0.0,
        ),
    ]
    data = {"coverage_gaps": gaps, "slow_tests": tests}
    result = xml_formatter.format(data)

    root = ET.fromstring(result)  # noqa: S314  # nosec B314  # parsing our own generated XML

    # Verify coverage gap with zero coverage
    gap = root.find("coverage_gaps/gap")
    assert gap.find("current_coverage").text == "0.0"
    assert gap.find("lines_needed").text == "999999"

    # Verify test with zero duration
    test = root.find("slow_tests/test")
    assert test.find("avg_duration").text == "0.0"
    assert test.find("failure_rate").text == "1.0"
