"""Text output formatter.

Converts NHL Scrabble analysis data to plain text format with readable formatting and alignment.
"""

from __future__ import annotations

from typing import Any


class TextFormatter:
    """Format analysis data as plain text.

    Produces human-readable plain text output with proper alignment and
    formatting, suitable for terminal display and text files.

    Example:
        >>> formatter = TextFormatter()
        >>> output = formatter.format(data)
        >>> "NHL Scrabble Scores" in output
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to plain text string.

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
            Plain text formatted string with proper alignment

        Example:
            >>> formatter = TextFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> "TOR" in output
            True
        """
        lines = []

        # Title
        lines.append("")
        lines.append("=" * 80)
        lines.append("NHL SCRABBLE SCORES")
        lines.append("=" * 80)
        lines.append("")

        # Summary section
        if "summary" in data:
            summary = data["summary"]
            lines.append("SUMMARY")
            lines.append("-" * 80)
            if "total_teams" in summary:
                lines.append(f"Total Teams:   {summary['total_teams']}")
            if "total_players" in summary:
                lines.append(f"Total Players: {summary['total_players']}")
            lines.append("")

        # Team standings
        if data.get("teams"):
            lines.append("TEAM STANDINGS")
            lines.append("-" * 80)
            lines.append(
                f"{'Rank':<6} {'Team':<6} {'Division':<15} {'Conference':<12} {'Score':>8} {'Avg':>8}"
            )
            lines.append("-" * 80)

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

                lines.append(
                    f"{rank:<6} {abbrev:<6} {division:<15} {conference:<12} {total:>8} {avg:>8.2f}"
                )

            lines.append("")

        lines.append("=" * 80)
        lines.append("")

        return "\n".join(lines)
