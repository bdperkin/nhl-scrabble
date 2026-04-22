"""Markdown output formatter.

Converts NHL Scrabble analysis data to Markdown format with tables, suitable for documentation and
GitHub/GitLab reports.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class MarkdownFormatter:
    """Format analysis data as Markdown.

    Produces Markdown-formatted output with tables and headers, suitable for
    documentation, GitHub/GitLab reports, and wiki pages.

    Example:
        >>> formatter = MarkdownFormatter()
        >>> output = formatter.format(data)
        >>> "# NHL Scrabble Scores" in output
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to Markdown string.

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
            Markdown formatted string with tables and headers

        Example:
            >>> formatter = MarkdownFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> "| Rank |" in output
            True
        """
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = []

        # Title
        lines.append("# NHL Scrabble Scores\n")
        lines.append(f"*Generated: {timestamp}*\n")

        # Summary section
        if "summary" in data:
            summary = data["summary"]
            lines.append("## Summary\n")
            if "total_teams" in summary:
                lines.append(f"- **Total Teams:** {summary['total_teams']}")
            if "total_players" in summary:
                lines.append(f"- **Total Players:** {summary['total_players']}")
            lines.append("")

        # Team standings table
        if data.get("teams"):
            lines.append("## Team Standings\n")

            # Table header
            lines.append("| Rank | Team | Division | Conference | Total Score | Avg Per Player |")
            lines.append("|------|------|----------|------------|-------------|----------------|")

            # Sort teams by total score
            sorted_teams = sorted(
                data["teams"].items(),
                key=lambda x: x[1].get("total", 0),
                reverse=True,
            )

            # Table rows
            for rank, (abbrev, team_data) in enumerate(sorted_teams, 1):
                total = team_data.get("total", 0)
                avg = team_data.get("avg_per_player", 0)
                division = team_data.get("division", "N/A")
                conference = team_data.get("conference", "N/A")

                lines.append(
                    f"| {rank} | {abbrev} | {division} | {conference} | {total} | {avg:.2f} |"
                )

            lines.append("")

        return "\n".join(lines)
