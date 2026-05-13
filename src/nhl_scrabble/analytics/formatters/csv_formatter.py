"""CSV formatter for test analytics data."""

import csv
from io import StringIO
from typing import Any


class CSVFormatter:
    """Format analytics data as CSV.

    Outputs analytics data in CSV format for spreadsheet import and data analysis.

    Example:
        >>> formatter = CSVFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> with open("analytics.csv", "w") as f:
        ...     f.write(output)
    """

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as CSV.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: CSV-formatted string.
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "section",
                "test_name",
                "module",
                "current_coverage",
                "target_coverage",
                "lines_needed",
                "priority",
                "avg_duration",
                "max_duration",
                "min_duration",
                "failure_rate",
                "flakiness_score",
            ],
        )

        # Write coverage gaps
        if "coverage_gaps" in data:
            for gap in data["coverage_gaps"]:
                writer.writerow(
                    [
                        "coverage_gaps",
                        "",
                        gap.module,
                        gap.current_coverage,
                        gap.target_coverage,
                        gap.lines_needed,
                        gap.priority,
                        "",
                        "",
                        "",
                        "",
                        "",
                    ],
                )

        # Write slow tests
        if "slow_tests" in data:
            for test in data["slow_tests"]:
                writer.writerow(
                    [
                        "slow_tests",
                        test.test_name,
                        "",
                        "",
                        "",
                        "",
                        "",
                        test.avg_duration,
                        test.max_duration,
                        test.min_duration,
                        test.failure_rate,
                        test.flakiness_score,
                    ],
                )

        # Write flaky tests
        if "flaky_tests" in data:
            for test in data["flaky_tests"]:
                writer.writerow(
                    [
                        "flaky_tests",
                        test.test_name,
                        "",
                        "",
                        "",
                        "",
                        "",
                        test.avg_duration,
                        "",
                        "",
                        test.failure_rate,
                        test.flakiness_score,
                    ],
                )

        return output.getvalue()
