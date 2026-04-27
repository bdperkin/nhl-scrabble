"""HTML output formatter.

Converts NHL Scrabble analysis data to styled HTML format for web viewing and browser-based
reporting.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class HTMLFormatter:
    """Format analysis data as HTML.

    Produces styled HTML output with CSS for web viewing, suitable for
    dashboards, reports, and browser-based display.

    Example:
        >>> formatter = HTMLFormatter()
        >>> data = {"teams": {}, "summary": {}}
        >>> output = formatter.format(data)
        >>> "<!DOCTYPE html>" in output
        True
    """

    def format(self, data: dict[str, Any]) -> str:
        """Format data to HTML string.

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
            Complete HTML document string with embedded CSS styling

        Example:
            >>> formatter = HTMLFormatter()
            >>> data = {"teams": {"TOR": {"total": 1234}}, "summary": {}}
            >>> output = formatter.format(data)
            >>> "<table>" in output
            True
        """
        timestamp = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Build HTML document
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>NHL Scrabble Scores</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            background-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 13px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        td.number {{
            text-align: right;
            font-family: "Courier New", monospace;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>🏒 NHL Scrabble Scores</h1>
    <div class="timestamp">Generated: {timestamp}</div>
"""

        # Add summary section if available
        if "summary" in data:
            summary = data["summary"]
            html += """
    <div class="summary">
        <h2>Summary</h2>
"""
            if "total_teams" in summary:
                html += f"        <p><strong>Total Teams:</strong> {summary['total_teams']}</p>\n"
            if "total_players" in summary:
                html += (
                    f"        <p><strong>Total Players:</strong> {summary['total_players']}</p>\n"
                )
            html += "    </div>\n"

        # Add teams table
        if data.get("teams"):
            html += """
    <h2>Team Standings</h2>
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Division</th>
                <th>Conference</th>
                <th>Total Score</th>
                <th>Avg Per Player</th>
            </tr>
        </thead>
        <tbody>
"""
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

                html += f"""            <tr>
                <td class="number">{rank}</td>
                <td><strong>{abbrev}</strong></td>
                <td>{division}</td>
                <td>{conference}</td>
                <td class="number">{total}</td>
                <td class="number">{avg:.2f}</td>
            </tr>
"""

            html += """        </tbody>
    </table>
"""

        # Close HTML document
        html += """</body>
</html>"""

        return html
