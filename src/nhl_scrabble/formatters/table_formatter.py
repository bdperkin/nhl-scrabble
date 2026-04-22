"""Table output formatter.

Converts NHL Scrabble analysis data to pretty-printed terminal tables using the Rich library for
enhanced visual display.
"""

from __future__ import annotations

from typing import Any


class TableFormatter:
    """Format analysis data as pretty-printed tables.

    Uses Rich library to create beautifully formatted terminal tables with
    colors, borders, and alignment for maximum readability.

    Example:
        >>> formatter = TableFormatter()
        >>> output = formatter.format(data)
        >>> "┃" in output  # Rich uses box-drawing characters
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to Rich table string.

        Args:
            data: Analysis data dictionary with structure:
                {
                    "teams": {...},
                    "divisions": {...},
                    "conferences": {...},
                    "playoffs": {...},
                    "summary": {...}
                }

        Returns:
            Rich-formatted table string with box-drawing characters

        Example:
            >>> formatter = TableFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> len(output) > 0
            True
        """
        from rich.console import Console
        from rich.table import Table

        # Create console to capture output
        console = Console()

        # Build table for team standings
        table = Table(title="🏒 NHL Scrabble Scores")

        # Add columns
        table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
        table.add_column("Team", style="magenta", no_wrap=True)
        table.add_column("Division", style="blue")
        table.add_column("Conference", style="blue")
        table.add_column("Total Score", justify="right", style="green")
        table.add_column("Avg Per Player", justify="right", style="yellow")

        # Add rows from teams data
        if data.get("teams"):
            # Sort teams by total score
            sorted_teams = sorted(
                data["teams"].items(),
                key=lambda x: x[1].get("total", 0),
                reverse=True,
            )

            for rank, (abbrev, team_data) in enumerate(sorted_teams, 1):
                total = team_data.get("total", 0)
                avg = team_data.get("avg_per_player", 0)
                division = team_data.get("division", "N/A")
                conference = team_data.get("conference", "N/A")

                table.add_row(
                    str(rank),
                    abbrev,
                    division,
                    conference,
                    str(total),
                    f"{avg:.2f}",
                )

        # Capture table output to string
        with console.capture() as capture:
            console.print(table)

        return capture.get()
