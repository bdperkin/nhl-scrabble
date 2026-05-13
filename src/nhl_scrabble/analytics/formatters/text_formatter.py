"""Text formatter for test analytics data."""

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
