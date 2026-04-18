"""Conference standings reporter."""

from nhl_scrabble.models.standings import ConferenceStandings
from nhl_scrabble.reports.base import BaseReporter


class ConferenceReporter(BaseReporter):
    """Generate conference standings reports."""

    def generate(self, standings: dict[str, ConferenceStandings]) -> str:
        """Generate conference standings report.

        Args:
            standings: Dictionary mapping conference names to ConferenceStandings

        Returns:
            Formatted conference report string
        """
        parts = [self._format_header("🌎 CONFERENCE SCRABBLE SCORES")]

        sorted_conferences = self._sort_by_key(
            standings.items(), key=lambda x: x[1].total, reverse=True
        )

        for rank, (conference, data) in enumerate(sorted_conferences, 1):
            parts.extend(
                [
                    f"\n\n#{rank} {conference}",
                    f"\n   Total: {self._format_score(data.total)} points",
                    f"\n   Teams: {len(data.teams)} ({self._format_team_list(data.teams)})",
                    f"\n   Players: {data.player_count}",
                    f"\n   Avg per team: {self._format_average(data.avg_per_team, width=6, decimals=1)}",
                ]
            )

        return "".join(parts)
