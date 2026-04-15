"""Division standings reporter."""

from nhl_scrabble.models.standings import DivisionStandings
from nhl_scrabble.reports.base import BaseReporter


class DivisionReporter(BaseReporter):
    """Generate division standings reports."""

    def generate(self, standings: dict[str, DivisionStandings]) -> str:
        """Generate division standings report.

        Args:
            standings: Dictionary mapping division names to DivisionStandings

        Returns:
            Formatted division report string

        """
        output = self._format_header("🗺️  DIVISION SCRABBLE SCORES")

        sorted_divisions = sorted(standings.items(), key=lambda x: x[1].total, reverse=True)

        for rank, (division, data) in enumerate(sorted_divisions, 1):
            output += f"\n\n#{rank} {division}"
            output += f"\n   Total: {data.total} points"
            output += f"\n   Teams: {len(data.teams)} ({', '.join(sorted(data.teams))})"
            output += f"\n   Players: {data.player_count}"
            output += f"\n   Avg per team: {data.avg_per_team:.1f}"

        return output
