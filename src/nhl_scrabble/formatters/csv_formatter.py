"""CSV output formatter.

Converts NHL Scrabble analysis data to CSV format for spreadsheet import and data analysis tools.
"""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any


class CSVFormatter:
    """Format analysis data as CSV.

    Produces comma-separated values output suitable for Excel, Google Sheets,
    and other spreadsheet applications.

    Example:
        >>> formatter = CSVFormatter()
        >>> output = formatter.format(data)
        >>> "Rank,Team" in output
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to CSV string.

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
            CSV formatted string with headers and data rows

        Example:
            >>> formatter = CSVFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}}
            >>> output = formatter.format(data)
            >>> "TOR" in output
            True
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header row
        writer.writerow(
            [
                "Rank",
                "Team",
                "Division",
                "Conference",
                "Total Score",
                "Avg Per Player",
            ]
        )

        # Write data rows
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

                writer.writerow(
                    [
                        rank,
                        abbrev,
                        division,
                        conference,
                        total,
                        f"{avg:.2f}",
                    ]
                )

        return output.getvalue()
