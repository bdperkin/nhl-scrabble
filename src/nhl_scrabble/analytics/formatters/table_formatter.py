"""Table formatter for test analytics data."""

from typing import Any


class TableFormatter:
    """Format analytics data as simple ASCII tables.

    Outputs analytics data in simple ASCII table format using the
    tabulate library (simpler than Rich text output).

    Example:
        >>> formatter = TableFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> print(output)
    """

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as ASCII tables.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: ASCII table-formatted string.
        """
        from tabulate import (  # type: ignore[import-untyped]  # noqa: PLC0415  # lazy import for optional dependency
            tabulate,
        )

        output = []

        # Coverage gaps table
        if "coverage_gaps" in data:
            headers = ["Module", "Current", "Target", "Lines Needed", "Priority"]
            rows = [
                [
                    gap.module,
                    f"{gap.current_coverage:.1f}%",
                    f"{gap.target_coverage:.1f}%",
                    gap.lines_needed,
                    gap.priority.upper(),
                ]
                for gap in data["coverage_gaps"][:20]
            ]
            output.append("Coverage Gaps\n")
            output.append(tabulate(rows, headers=headers, tablefmt="grid"))

        # Slow tests table
        if "slow_tests" in data:
            headers = ["Test", "Avg Duration", "Max Duration", "Failure Rate"]
            rows = [
                [
                    test.test_name,
                    f"{test.avg_duration:.2f}s",
                    f"{test.max_duration:.2f}s",
                    f"{test.failure_rate * 100:.1f}%",
                ]
                for test in data["slow_tests"]
            ]
            output.append("Slowest Tests\n")
            output.append(tabulate(rows, headers=headers, tablefmt="grid"))

        # Flaky tests table
        if "flaky_tests" in data:
            headers = ["Test", "Flakiness Score", "Failure Rate"]
            rows = [
                [
                    test.test_name,
                    f"{test.flakiness_score:.3f}",
                    f"{test.failure_rate * 100:.1f}%",
                ]
                for test in data["flaky_tests"]
            ]
            output.append("Flaky Tests\n")
            output.append(tabulate(rows, headers=headers, tablefmt="grid"))

        return "\n\n".join(output)
