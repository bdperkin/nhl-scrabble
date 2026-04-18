"""Team scores reporter."""

import heapq

from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.reports.base import BaseReporter


class TeamReporter(BaseReporter):
    """Generate team scores reports with top players."""

    def __init__(self, top_players_per_team: int = 5) -> None:
        """Initialize team reporter.

        Args:
            top_players_per_team: Number of top players to show per team
        """
        self.top_players_per_team = top_players_per_team

    def generate(self, team_scores: dict[str, TeamScore]) -> str:
        """Generate team scores report.

        Args:
            team_scores: Dictionary mapping team abbreviations to TeamScore objects

        Returns:
            Formatted team report string
        """
        output = self._format_header("📊 TEAM SCRABBLE SCORES (Sorted by Total Score)")

        sorted_teams = self._sort_by_key(
            team_scores.items(), key=lambda x: x[1].total, reverse=True
        )

        for rank, (team_abbrev, team_data) in enumerate(sorted_teams, 1):
            output += (
                f"\n\n#{rank} {team_abbrev} ({team_data.division}): "
                f"{self._format_score(team_data.total)} points ({team_data.player_count} players)"
            )

            # Show top players from each team
            top_players = heapq.nlargest(
                self.top_players_per_team, team_data.players, key=lambda x: x.full_score
            )

            for i, player in enumerate(top_players, 1):
                output += (
                    f"\n   {i}. {player.full_name}: {self._format_score(player.full_score)} "
                    f"({player.first_name}={self._format_score(player.first_score, width=2)}, "
                    f"{player.last_name}={self._format_score(player.last_score, width=2)})"
                )

        return output
