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
        parts = [self._format_header("🗺️  DIVISION SCRABBLE SCORES")]

        sorted_divisions = self._sort_by_key(
            standings.items(),
            key=lambda x: x[1].total,
            reverse=True,
        )

        for rank, (division, data) in enumerate(sorted_divisions, 1):
            parts.extend(
                [
                    f"\n\n#{rank} {division}",
                    f"\n   Total: {self._format_score(data.total)} points",
                    f"\n   Teams: {len(data.teams)} ({self._format_team_list(data.teams)})",
                    f"\n   Players: {data.player_count}",
                    f"\n   Avg per team: {self._format_average(data.avg_per_team, width=6, decimals=1)}",
                ],
            )

        return "".join(parts)
