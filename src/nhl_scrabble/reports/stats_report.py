"""Fun statistics reporter."""

from __future__ import annotations

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings
from nhl_scrabble.reports.base import BaseReporter


class StatsReporter(BaseReporter):
    """Generate fun statistics and top players reports."""

    def __init__(self, top_players_count: int = 20) -> None:
        """Initialize stats reporter.

        Args:
            top_players_count: Number of top players to show
        """
        self.top_players_count = top_players_count

    def generate(  # type: ignore[override]
        self,
        all_players: list[PlayerScore],
        division_standings: dict[str, DivisionStandings],
        conference_standings: dict[str, ConferenceStandings],
    ) -> str:
        """Generate statistics report.

        Args:
            all_players: List of all PlayerScore objects
            division_standings: Division standings data
            conference_standings: Conference standings data

        Returns:
            Formatted statistics report string
        """
        output = ""

        # Top players overall
        output += self._format_header(
            f"🌟 TOP {self.top_players_count} HIGHEST-SCORING PLAYERS (Across All Teams)"
        )

        top_players = sorted(all_players, key=lambda x: x.full_score, reverse=True)[
            : self.top_players_count
        ]

        for rank, player in enumerate(top_players, 1):
            div_abbrev = player.division.split()[0][:3].upper()
            output += (
                f"\n{rank:2}. {player.full_name:30} ({player.team:3}/{div_abbrev}): "
                f"{player.full_score:3} points "
                f"[First: {player.first_score:2}, Last: {player.last_score:2}]"
            )

        # Fun stats
        output += self._format_header("🎯 FUN STATS")

        # Highest scoring first name
        top_first = max(all_players, key=lambda x: x.first_score)
        output += (
            f"\nHighest First Name: {top_first.first_name} "
            f"({top_first.full_name}, {top_first.team}) = {top_first.first_score} points"
        )

        # Highest scoring last name
        top_last = max(all_players, key=lambda x: x.last_score)
        output += (
            f"\nHighest Last Name: {top_last.last_name} "
            f"({top_last.full_name}, {top_last.team}) = {top_last.last_score} points"
        )

        # Average scores overall
        avg_full = sum(p.full_score for p in all_players) / len(all_players)
        avg_first = sum(p.first_score for p in all_players) / len(all_players)
        avg_last = sum(p.last_score for p in all_players) / len(all_players)

        output += "\n\nLeague-Wide Average Scores:"
        output += f"\n  Full Name: {avg_full:.2f}"
        output += f"\n  First Name: {avg_first:.2f}"
        output += f"\n  Last Name: {avg_last:.2f}"

        # Division with highest average per player
        division_avg_per_player = {
            div: data.total / data.player_count if data.player_count else 0.0
            for div, data in division_standings.items()
        }

        if division_avg_per_player:
            top_division = max(division_avg_per_player.items(), key=lambda x: x[1])
            output += (
                f"\n\nHighest Avg Division (per player): "
                f"{top_division[0]} = {top_division[1]:.2f} points/player"
            )

        # Conference with highest average per player
        conference_avg_per_player = {
            conf: data.total / data.player_count if data.player_count else 0.0
            for conf, data in conference_standings.items()
        }

        if conference_avg_per_player:
            top_conference = max(conference_avg_per_player.items(), key=lambda x: x[1])
            output += (
                f"\nHighest Avg Conference (per player): "
                f"{top_conference[0]} = {top_conference[1]:.2f} points/player"
            )

        return output
