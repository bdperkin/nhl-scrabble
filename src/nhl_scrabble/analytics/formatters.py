"""Output formatters for test analytics data."""

import json
from io import StringIO
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nhl_scrabble.analytics.analyzer import CoverageGap, TestPerformance


class TextFormatter:
    """Format analytics data as rich text output.

    Uses Rich library to create formatted tables and panels for terminal display.

    Example:
        >>> formatter = TextFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> print(output)
    """

    def __init__(self) -> None:
        """Initialize text formatter with Rich console."""
        self.console = Console()

    def _format_coverage_gaps(self, gaps: list[CoverageGap]) -> str:
        """Format coverage gaps as a table.

        Args:
            gaps: List of CoverageGap instances.

        Returns:
            str: Formatted table string.
        """
        table = Table(title="Coverage Gaps")
        table.add_column("Module", style="cyan")
        table.add_column("Current", justify="right")
        table.add_column("Target", justify="right")
        table.add_column("Lines Needed", justify="right")
        table.add_column("Priority", style="bold")

        for gap in gaps[:20]:  # Show top 20
            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }.get(gap.priority, "white")

            table.add_row(
                gap.module,
                f"{gap.current_coverage:.1f}%",
                f"{gap.target_coverage:.1f}%",
                str(gap.lines_needed),
                f"[{priority_color}]{gap.priority.upper()}[/{priority_color}]",
            )

        # Use console to render to string
        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=True)
        temp_console.print(table)
        return string_io.getvalue()

    def _format_slow_tests(self, tests: list[TestPerformance]) -> str:
        """Format slow tests as a table.

        Args:
            tests: List of TestPerformance instances.

        Returns:
            str: Formatted table string.
        """
        table = Table(title="Slowest Tests")
        table.add_column("Test", style="cyan")
        table.add_column("Avg Duration", justify="right")
        table.add_column("Max Duration", justify="right")
        table.add_column("Failure Rate", justify="right")

        for test in tests:
            table.add_row(
                test.test_name,
                f"{test.avg_duration:.2f}s",
                f"{test.max_duration:.2f}s",
                f"{test.failure_rate * 100:.1f}%",
            )

        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=True)
        temp_console.print(table)
        return string_io.getvalue()

    def _format_flaky_tests(self, tests: list[TestPerformance]) -> str:
        """Format flaky tests as a table.

        Args:
            tests: List of TestPerformance instances.

        Returns:
            str: Formatted table string.
        """
        table = Table(title="Flaky Tests")
        table.add_column("Test", style="cyan")
        table.add_column("Flakiness Score", justify="right")
        table.add_column("Failure Rate", justify="right")

        for test in tests:
            table.add_row(
                test.test_name,
                f"{test.flakiness_score:.3f}",
                f"{test.failure_rate * 100:.1f}%",
            )

        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=True)
        temp_console.print(table)
        return string_io.getvalue()

    def _format_trends(  # type: ignore[explicit-any]
        self,
        trend: str,
        history: list[dict[str, Any]],
    ) -> str:
        """Format coverage trend information.

        Args:
            trend: Trend status ("improving", "declining", "stable", etc.).
            history: List of historical coverage data.

        Returns:
            str: Formatted trend panel string.
        """
        trend_emoji = {
            "improving": "📈",
            "declining": "📉",
            "stable": "➡️",
            "insufficient_data": "❓",
        }.get(trend, "")

        current = history[0]["coverage"] if history else 0
        oldest = history[-1]["coverage"] if len(history) > 1 else 0
        change = current - oldest

        text = f"{trend_emoji} Coverage Trend: {trend.upper()}\n"
        text += f"Current: {current:.1f}%\n"
        text += f"Change (30 days): {change:+.1f}%"

        panel = Panel(text, title="Coverage Trends", border_style="blue")

        string_io = StringIO()
        temp_console = Console(file=string_io, force_terminal=True)
        temp_console.print(panel)
        return string_io.getvalue()

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as rich text.

        Args:
            data: Dictionary containing analytics data with keys like
                "coverage_gaps", "slow_tests", "flaky_tests", "coverage_trend".

        Returns:
            str: Formatted text output ready for display.
        """
        output = []

        # Coverage gaps
        if "coverage_gaps" in data:
            output.append(self._format_coverage_gaps(data["coverage_gaps"]))

        # Slow tests
        if "slow_tests" in data:
            output.append(self._format_slow_tests(data["slow_tests"]))

        # Flaky tests
        if "flaky_tests" in data:
            output.append(self._format_flaky_tests(data["flaky_tests"]))

        # Trends
        if "coverage_trend" in data:
            output.append(
                self._format_trends(
                    data["coverage_trend"],
                    data.get("coverage_history", []),
                ),
            )

        return "\n\n".join(output)


class JSONFormatter:
    """Format analytics data as JSON.

    Converts analytics data structures to JSON for programmatic consumption.

    Example:
        >>> formatter = JSONFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> data = json.loads(output)
    """

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as JSON.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: JSON-formatted string.
        """
        # Convert dataclasses to dicts for JSON serialization
        serializable_data = {}

        if "coverage_gaps" in data:
            serializable_data["coverage_gaps"] = [
                {
                    "module": gap.module,
                    "current_coverage": gap.current_coverage,
                    "target_coverage": gap.target_coverage,
                    "lines_needed": gap.lines_needed,
                    "priority": gap.priority,
                }
                for gap in data["coverage_gaps"]
            ]

        if "slow_tests" in data:
            serializable_data["slow_tests"] = [
                {
                    "test_name": test.test_name,
                    "avg_duration": test.avg_duration,
                    "max_duration": test.max_duration,
                    "min_duration": test.min_duration,
                    "failure_rate": test.failure_rate,
                    "flakiness_score": test.flakiness_score,
                }
                for test in data["slow_tests"]
            ]

        if "flaky_tests" in data:
            serializable_data["flaky_tests"] = [
                {
                    "test_name": test.test_name,
                    "flakiness_score": test.flakiness_score,
                    "failure_rate": test.failure_rate,
                    "avg_duration": test.avg_duration,
                }
                for test in data["flaky_tests"]
            ]

        if "coverage_trend" in data:
            serializable_data["coverage_trend"] = data["coverage_trend"]

        if "coverage_history" in data:
            serializable_data["coverage_history"] = data["coverage_history"]

        return json.dumps(serializable_data, indent=2, default=str)


class HTMLFormatter:
    """Format analytics data as HTML.

    Generates HTML tables and styled output for web display.

    Example:
        >>> formatter = HTMLFormatter()
        >>> output = formatter.format({"coverage_gaps": gaps})
        >>> Path("report.html").write_text(output)
    """

    def _format_coverage_gaps_html(self, gaps: list[CoverageGap]) -> str:
        """Format coverage gaps as HTML table.

        Args:
            gaps: List of CoverageGap instances.

        Returns:
            str: HTML table string.
        """
        html = ["<h2>Coverage Gaps</h2>", "<table>", "<tr>"]
        html.append("<th>Module</th>")
        html.append("<th>Current</th>")
        html.append("<th>Target</th>")
        html.append("<th>Lines Needed</th>")
        html.append("<th>Priority</th>")
        html.append("</tr>")

        for gap in gaps[:20]:  # Show top 20
            html.append("<tr>")
            html.append(f"<td>{gap.module}</td>")
            html.append(f"<td>{gap.current_coverage:.1f}%</td>")
            html.append(f"<td>{gap.target_coverage:.1f}%</td>")
            html.append(f"<td>{gap.lines_needed}</td>")
            html.append(
                f'<td class="{gap.priority}">{gap.priority.upper()}</td>',
            )
            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _format_slow_tests_html(self, tests: list[TestPerformance]) -> str:
        """Format slow tests as HTML table.

        Args:
            tests: List of TestPerformance instances.

        Returns:
            str: HTML table string.
        """
        html = ["<h2>Slowest Tests</h2>", "<table>", "<tr>"]
        html.append("<th>Test</th>")
        html.append("<th>Avg Duration</th>")
        html.append("<th>Max Duration</th>")
        html.append("<th>Failure Rate</th>")
        html.append("</tr>")

        for test in tests:
            html.append("<tr>")
            html.append(f"<td>{test.test_name}</td>")
            html.append(f"<td>{test.avg_duration:.2f}s</td>")
            html.append(f"<td>{test.max_duration:.2f}s</td>")
            html.append(f"<td>{test.failure_rate * 100:.1f}%</td>")
            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _format_flaky_tests_html(self, tests: list[TestPerformance]) -> str:
        """Format flaky tests as HTML table.

        Args:
            tests: List of TestPerformance instances.

        Returns:
            str: HTML table string.
        """
        html = ["<h2>Flaky Tests</h2>", "<table>", "<tr>"]
        html.append("<th>Test</th>")
        html.append("<th>Flakiness Score</th>")
        html.append("<th>Failure Rate</th>")
        html.append("</tr>")

        for test in tests:
            html.append("<tr>")
            html.append(f"<td>{test.test_name}</td>")
            html.append(f"<td>{test.flakiness_score:.3f}</td>")
            html.append(f"<td>{test.failure_rate * 100:.1f}%</td>")
            html.append("</tr>")

        html.append("</table>")
        return "\n".join(html)

    def _format_trends_html(  # type: ignore[explicit-any]
        self,
        trend: str,
        history: list[dict[str, Any]],
    ) -> str:
        """Format coverage trend as HTML.

        Args:
            trend: Trend status.
            history: Historical coverage data.

        Returns:
            str: HTML div string.
        """
        trend_emoji = {
            "improving": "📈",
            "declining": "📉",
            "stable": "➡️",
            "insufficient_data": "❓",
        }.get(trend, "")

        current = history[0]["coverage"] if history else 0
        oldest = history[-1]["coverage"] if len(history) > 1 else 0
        change = current - oldest

        html = ['<div class="trend">', "<h2>Coverage Trends</h2>"]
        html.append(f"<p>{trend_emoji} <strong>Trend:</strong> {trend.upper()}</p>")
        html.append(f"<p><strong>Current:</strong> {current:.1f}%</p>")
        html.append(f"<p><strong>Change (30 days):</strong> {change:+.1f}%</p>")
        html.append("</div>")

        return "\n".join(html)

    def format(self, data: dict[str, Any]) -> str:  # type: ignore[explicit-any]
        """Format analytics data as HTML.

        Args:
            data: Dictionary containing analytics data.

        Returns:
            str: HTML-formatted string.
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Test Analytics Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h1 { color: #333; }",
            "h2 { color: #666; margin-top: 30px; }",
            "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #4CAF50; color: white; }",
            "tr:nth-child(even) { background-color: #f2f2f2; }",
            ".high { color: red; font-weight: bold; }",
            ".medium { color: orange; font-weight: bold; }",
            ".low { color: green; font-weight: bold; }",
            ".trend { padding: 20px; background-color: #e7f3ff; border-left: 4px solid #2196F3; margin: 20px 0; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Test Analytics Report</h1>",
        ]

        # Coverage gaps
        if "coverage_gaps" in data:
            html_parts.append(self._format_coverage_gaps_html(data["coverage_gaps"]))

        # Slow tests
        if "slow_tests" in data:
            html_parts.append(self._format_slow_tests_html(data["slow_tests"]))

        # Flaky tests
        if "flaky_tests" in data:
            html_parts.append(self._format_flaky_tests_html(data["flaky_tests"]))

        # Trends
        if "coverage_trend" in data:
            html_parts.append(
                self._format_trends_html(
                    data["coverage_trend"],
                    data.get("coverage_history", []),
                ),
            )

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)
