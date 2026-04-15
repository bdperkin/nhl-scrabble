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
        output = self._format_header("🌎 CONFERENCE SCRABBLE SCORES")

        sorted_conferences = sorted(standings.items(), key=lambda x: x[1].total, reverse=True)

        for rank, (conference, data) in enumerate(sorted_conferences, 1):
            output += f"\n\n#{rank} {conference}"
            output += f"\n   Total: {data.total} points"
            output += f"\n   Teams: {len(data.teams)} ({', '.join(sorted(data.teams))})"
            output += f"\n   Players: {data.player_count}"
            output += f"\n   Avg per team: {data.avg_per_team:.1f}"

        return output
