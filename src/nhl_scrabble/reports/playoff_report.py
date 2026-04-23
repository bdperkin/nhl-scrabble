"""Playoff standings reporter."""

from collections import defaultdict

from nhl_scrabble.models.standings import PlayoffTeam
from nhl_scrabble.reports.base import BaseReporter


class PlayoffReporter(BaseReporter):
    """Generate playoff standings reports in NHL wild card format."""

    def _group_teams_by_division(self, teams: list[PlayoffTeam]) -> dict[str, list[PlayoffTeam]]:
        """Group teams by division.

        Args:
            teams: List of PlayoffTeam objects

        Returns:
            Dictionary mapping division names to team lists
        """
        teams_by_division: dict[str, list[PlayoffTeam]] = defaultdict(list)
        for team in teams:
            teams_by_division[team.division].append(team)

        # Sort teams within each division by rank
        for division in teams_by_division:
            teams_by_division[division].sort(key=lambda x: x.division_rank)

        return teams_by_division

    def _format_team_line(self, team: PlayoffTeam, show_seed: bool = True) -> str:
        """Format a single team line for the playoff report.

        Args:
            team: PlayoffTeam object
            show_seed: Whether to show the seed type

        Returns:
            Formatted team line string
        """
        seed_part = f"{team.seed_type:20}" if show_seed else " " * 20
        return (
            f"\n    {seed_part} {team.abbrev:4} {self._format_score(team.total)} pts "
            f"({team.players:2} players, avg: {self._format_average(team.avg)}) "
            f"{team.status_indicator}"
        )

    def generate(self, standings: dict[str, list[PlayoffTeam]]) -> str:
        """Generate playoff standings report.

        Args:
            standings: Dictionary mapping conference names to lists of PlayoffTeam objects

        Returns:
            Formatted playoff report string
        """
        parts = [
            self._format_header("🎰 WILD CARD PLAYOFF STANDINGS (Scrabble Edition)"),
            "\nTop 3 from each division + 2 wild cards per conference",
            "\nTiebreaker: Average points per player",
            "\n\nLegend: x-Clinched Playoff, y-Clinched Division, z-Clinched Conference,",
            "\n        p-Presidents' Trophy, e-Eliminated",
        ]

        for conference in ["Eastern", "Western"]:
            if conference not in standings:
                continue

            parts.append(self._format_subheader(f"\n{conference} Conference"))

            # Group teams by division and playoff status
            teams_by_division = self._group_teams_by_division(standings[conference])
            wild_card_teams = [t for t in standings[conference] if "WC" in t.seed_type]
            eliminated_teams = [
                t for t in standings[conference] if not t.in_playoffs and "WC" not in t.seed_type
            ]

            # Print division leaders
            for division in sorted(teams_by_division.keys()):
                division_teams = teams_by_division[division]
                playoff_division_teams = [
                    t for t in division_teams if t.in_playoffs and "WC" not in t.seed_type
                ]

                if playoff_division_teams:
                    parts.append(f"\n\n  {division} Division:")
                    parts.extend(self._format_team_line(team) for team in playoff_division_teams)

            # Print wild cards
            if wild_card_teams:
                parts.append("\n\n  Wild Card:")
                parts.extend(self._format_team_line(team) for team in wild_card_teams)

            # Print eliminated teams
            if eliminated_teams:
                parts.append("\n\n  Eliminated from Playoff Contention:")
                parts.extend(
                    self._format_team_line(team, show_seed=False) for team in eliminated_teams
                )

        return "".join(parts)
