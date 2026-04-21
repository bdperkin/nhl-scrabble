"""Fun statistics reporter."""

from __future__ import annotations

import heapq
from typing import Any

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

    def _calculate_player_statistics(self, players: list[PlayerScore]) -> dict[str, Any]:
        """Calculate all player statistics in a single pass.

        Args:
            players: List of all players

        Returns:
            Dictionary with statistics:
            - top_first: Player with highest first name score
            - top_last: Player with highest last name score
            - avg_full: Average full name score
            - avg_first: Average first name score
            - avg_last: Average last name score
            - total_players: Total number of players

        Complexity:
            O(n) - single pass over all players
        """
        if not players:
            return {
                "top_first": None,
                "top_last": None,
                "avg_full": 0.0,
                "avg_first": 0.0,
                "avg_last": 0.0,
                "total_players": 0,
            }

        # Initialize with first player
        top_first = top_last = players[0]
        total_full = total_first = total_last = 0

        # Single pass - O(n)
        for player in players:
            # Track maximums
            if player.first_score > top_first.first_score:
                top_first = player
            if player.last_score > top_last.last_score:
                top_last = player

            # Accumulate totals for averages
            total_full += player.full_score
            total_first += player.first_score
            total_last += player.last_score

        # Calculate averages
        count = len(players)
        avg_full = total_full / count
        avg_first = total_first / count
        avg_last = total_last / count

        return {
            "top_first": top_first,
            "top_last": top_last,
            "avg_full": avg_full,
            "avg_first": avg_first,
            "avg_last": avg_last,
            "total_players": count,
        }

    def generate(
        self,
        data: tuple[
            list[PlayerScore], dict[str, DivisionStandings], dict[str, ConferenceStandings]
        ],
    ) -> str:
        """Generate statistics report.

        Args:
            data: Tuple containing (all_players, division_standings, conference_standings)

        Returns:
            Formatted statistics report string
        """
        all_players, division_standings, conference_standings = data
        parts = []

        # Top players overall
        parts.append(
            self._format_header(
                f"🌟 TOP {self.top_players_count} HIGHEST-SCORING PLAYERS (Across All Teams)"
            )
        )

        top_players = heapq.nlargest(
            self.top_players_count, all_players, key=lambda x: x.full_score
        )

        parts.extend(
            f"\n{rank:2}. {player.full_name:30} ({player.team:3}/{div_abbrev}): "
            f"{self._format_score(player.full_score, width=3)} points "
            f"[First: {self._format_score(player.first_score, width=2)}, "
            f"Last: {self._format_score(player.last_score, width=2)}]"
            for rank, player in enumerate(top_players, 1)
            for div_abbrev in [player.division.split()[0][:3].upper()]
        )

        # Fun stats
        parts.append(self._format_header("🎯 FUN STATS"))

        # Calculate all statistics in a single pass
        stats = self._calculate_player_statistics(all_players)

        # Highest scoring first name
        top_first = stats["top_first"]
        if top_first is not None:
            parts.append(
                f"\nHighest First Name: {top_first.first_name} "
                f"({top_first.full_name}, {top_first.team}) = "
                f"{self._format_score(top_first.first_score)} points"
            )
        else:
            parts.append("\nHighest First Name: N/A (no players)")

        # Highest scoring last name
        top_last = stats["top_last"]
        if top_last is not None:
            parts.append(
                f"\nHighest Last Name: {top_last.last_name} "
                f"({top_last.full_name}, {top_last.team}) = "
                f"{self._format_score(top_last.last_score)} points"
            )
        else:
            parts.append("\nHighest Last Name: N/A (no players)")

        # Average scores overall
        parts.extend(
            [
                "\n\nLeague-Wide Average Scores:",
                f"\n  Full Name: {self._format_average(stats['avg_full'], width=5)}",
                f"\n  First Name: {self._format_average(stats['avg_first'], width=5)}",
                f"\n  Last Name: {self._format_average(stats['avg_last'], width=5)}",
            ]
        )

        # Division with highest average per player
        division_avg_per_player = {
            div: data.total / data.player_count if data.player_count else 0.0
            for div, data in division_standings.items()
        }

        if division_avg_per_player:
            top_division = max(division_avg_per_player.items(), key=lambda x: x[1])
            parts.append(
                f"\n\nHighest Avg Division (per player): "
                f"{top_division[0]} = {self._format_average(top_division[1])} points/player"
            )

        # Conference with highest average per player
        conference_avg_per_player = {
            conf: data.total / data.player_count if data.player_count else 0.0
            for conf, data in conference_standings.items()
        }

        if conference_avg_per_player:
            top_conference = max(conference_avg_per_player.items(), key=lambda x: x[1])
            parts.append(
                f"\nHighest Avg Conference (per player): "
                f"{top_conference[0]} = {self._format_average(top_conference[1])} points/player"
            )

        return "".join(parts)
