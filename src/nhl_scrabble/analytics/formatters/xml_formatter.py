"""XML formatter for test analytics data."""

import xml.etree.ElementTree as ET
from typing import Any


class XMLFormatter:
    """Format analytics data as XML.

    Outputs analytics data in XML format for enterprise systems and
    legacy integrations.

    Example:
        >>> formatter = XMLFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> with open("analytics.xml", "w") as f:
        ...     f.write(output)
    """

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as XML.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: XML-formatted string.
        """
        root = ET.Element("test_analytics")

        # Add coverage gaps
        if "coverage_gaps" in data:
            gaps_elem = ET.SubElement(root, "coverage_gaps")
            for gap in data["coverage_gaps"]:
                gap_elem = ET.SubElement(gaps_elem, "gap")
                ET.SubElement(gap_elem, "module").text = gap.module
                ET.SubElement(gap_elem, "current_coverage").text = str(
                    gap.current_coverage,
                )
                ET.SubElement(gap_elem, "target_coverage").text = str(
                    gap.target_coverage,
                )
                ET.SubElement(gap_elem, "lines_needed").text = str(gap.lines_needed)
                ET.SubElement(gap_elem, "priority").text = gap.priority

        # Add slow tests
        if "slow_tests" in data:
            tests_elem = ET.SubElement(root, "slow_tests")
            for test in data["slow_tests"]:
                test_elem = ET.SubElement(tests_elem, "test")
                ET.SubElement(test_elem, "test_name").text = test.test_name
                ET.SubElement(test_elem, "avg_duration").text = str(test.avg_duration)
                ET.SubElement(test_elem, "max_duration").text = str(test.max_duration)
                ET.SubElement(test_elem, "min_duration").text = str(test.min_duration)
                ET.SubElement(test_elem, "failure_rate").text = str(test.failure_rate)
                ET.SubElement(test_elem, "flakiness_score").text = str(
                    test.flakiness_score,
                )

        # Add flaky tests
        if "flaky_tests" in data:
            flaky_elem = ET.SubElement(root, "flaky_tests")
            for test in data["flaky_tests"]:
                test_elem = ET.SubElement(flaky_elem, "test")
                ET.SubElement(test_elem, "test_name").text = test.test_name
                ET.SubElement(test_elem, "flakiness_score").text = str(
                    test.flakiness_score,
                )
                ET.SubElement(test_elem, "failure_rate").text = str(test.failure_rate)
                ET.SubElement(test_elem, "avg_duration").text = str(test.avg_duration)

        # Add coverage trend
        if "coverage_trend" in data:
            trend_elem = ET.SubElement(root, "coverage_trend")
            trend_elem.text = data["coverage_trend"]

        # Add coverage history
        if "coverage_history" in data:
            history_elem = ET.SubElement(root, "coverage_history")
            for record in data["coverage_history"]:
                record_elem = ET.SubElement(history_elem, "record")
                ET.SubElement(record_elem, "timestamp").text = str(
                    record.get("timestamp", ""),
                )
                ET.SubElement(record_elem, "coverage").text = str(
                    record.get("coverage", 0),
                )

        return ET.tostring(root, encoding="unicode", method="xml")
