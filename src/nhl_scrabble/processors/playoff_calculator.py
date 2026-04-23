"""Playoff standings calculator module."""

import heapq
import logging
from collections import defaultdict

from nhl_scrabble.models.standings import PlayoffTeam, StatusIndicator
from nhl_scrabble.models.team import TeamScore

logger = logging.getLogger(__name__)


class PlayoffCalculator:
    """Calculate NHL-style playoff standings based on Scrabble scores.

    This class implements the NHL playoff structure:
    - Top 3 teams from each division automatically qualify
    - 2 wild card spots per conference (next best teams by points)
    - Tiebreaker: average points per player
    - Status indicators: p (Presidents' Trophy), z (Conference leader),
      y (Division leader), x (Playoff spot), e (Eliminated)
    """

    def _group_teams_by_division(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, list[PlayoffTeam]]:
        """Group teams by division and convert to PlayoffTeam objects.

        Args:
            team_scores: Dictionary of TeamScore objects

        Returns:
            Dictionary mapping division names to lists of PlayoffTeam objects
        """
        teams_by_division: dict[str, list[PlayoffTeam]] = defaultdict(list)

        for team_abbrev, team_score in team_scores.items():
            playoff_team = PlayoffTeam(
                abbrev=team_abbrev,
                total=team_score.total,
                players=team_score.player_count,
                avg=team_score.avg_per_player,
                conference=team_score.conference,
                division=team_score.division,
            )
            teams_by_division[team_score.division].append(playoff_team)

        return teams_by_division

    def _determine_division_leaders(
        self, teams_by_division: dict[str, list[PlayoffTeam]]
    ) -> tuple[dict[str, PlayoffTeam], list[PlayoffTeam]]:
        """Determine top 3 teams from each division (automatic playoff spots).

        Args:
            teams_by_division: Teams grouped by division

        Returns:
            Tuple of (playoff_teams dict, all_teams list)
        """
        playoff_teams: dict[str, PlayoffTeam] = {}
        all_teams: list[PlayoffTeam] = []

        for division, teams in teams_by_division.items():
            # Get top 3 from each division using heapq for O(n log k) complexity
            top_3 = heapq.nlargest(3, teams, key=lambda x: (x.total, x.avg))

            # Top 3 from each division make playoffs
            for i, team in enumerate(top_3):
                team.seed_type = f"{division} #{i + 1}"
                team.in_playoffs = True
                team.division_rank = i + 1
                playoff_teams[team.abbrev] = team

            # Get remaining teams (not in top 3)
            remaining = [t for t in teams if t not in top_3]

            # Mark division rank for remaining teams
            for i, team in enumerate(remaining, start=4):
                team.in_playoffs = False
                team.division_rank = i

            all_teams.extend(top_3 + remaining)

        return playoff_teams, all_teams

    def _determine_wild_cards(
        self,
        teams_by_division: dict[str, list[PlayoffTeam]],
        playoff_teams: dict[str, PlayoffTeam],
    ) -> dict[str, list[PlayoffTeam]]:
        """Determine wild card teams for each conference.

        Args:
            teams_by_division: Teams grouped by division
            playoff_teams: Dictionary of teams already in playoffs

        Returns:
            Dictionary mapping conference names to lists of wild card teams
        """
        wild_cards: dict[str, list[PlayoffTeam]] = {}

        for conference in ["Eastern", "Western"]:
            # Get all teams in this conference not in top 3 of their division
            wild_card_candidates: list[PlayoffTeam] = []

            for _division, teams in teams_by_division.items():
                # Check if this division is in this conference
                if teams and teams[0].conference == conference:
                    # Add teams not already in playoffs (not in top 3 of their division)
                    wild_card_candidates.extend(
                        team for team in teams if team.abbrev not in playoff_teams
                    )

            # Get top 2 wild cards using heapq for O(n log k) complexity
            conference_wild_cards = heapq.nlargest(
                2, wild_card_candidates, key=lambda x: (x.total, x.avg)
            )

            for i, team in enumerate(conference_wild_cards):
                team.seed_type = f"{conference} WC{i + 1}"
                team.in_playoffs = True
                playoff_teams[team.abbrev] = team

            # Mark remaining teams as eliminated
            eliminated = [t for t in wild_card_candidates if t not in conference_wild_cards]
            for team in eliminated:
                team.seed_type = "Eliminated"
                team.in_playoffs = False

            wild_cards[conference] = conference_wild_cards

        return wild_cards

    def _get_presidents_trophy_team(self, all_teams: list[PlayoffTeam]) -> PlayoffTeam:
        """Determine the Presidents' Trophy winner (highest total points).

        Args:
            all_teams: List of all teams

        Returns:
            The team with the highest total points
        """
        return max(all_teams, key=lambda x: (x.total, x.avg))

    def _get_conference_leaders(self, all_teams: list[PlayoffTeam]) -> dict[str, PlayoffTeam]:
        """Determine the top team in each conference.

        Args:
            all_teams: List of all teams

        Returns:
            Dictionary mapping conference names to their leader teams
        """
        conference_leaders: dict[str, PlayoffTeam] = {}

        for conference in ["Eastern", "Western"]:
            conf_teams = [t for t in all_teams if t.conference == conference]
            if conf_teams:
                conference_leaders[conference] = max(conf_teams, key=lambda x: (x.total, x.avg))

        return conference_leaders

    def _get_status_indicator(
        self,
        team: PlayoffTeam,
        presidents_trophy_team: PlayoffTeam,
        conference_leaders: dict[str, PlayoffTeam],
    ) -> StatusIndicator:
        """Get the status indicator for a team.

        Args:
            team: The team to evaluate
            presidents_trophy_team: Presidents' Trophy winner
            conference_leaders: Dictionary of conference leaders

        Returns:
            Status indicator character
        """
        # Presidents' Trophy (most significant)
        if team.abbrev == presidents_trophy_team.abbrev:
            return "p"

        # Clinched Conference
        conf_leader = conference_leaders.get(team.conference)
        if conf_leader and team.abbrev == conf_leader.abbrev:
            return "z"

        # Clinched Division (first in division)
        if team.division_rank == 1:
            return "y"

        # Clinched Playoff
        if team.in_playoffs:
            return "x"

        # Eliminated
        return "e"

    def _assign_status_indicators(
        self,
        all_teams: list[PlayoffTeam],
        _playoff_teams: dict[str, PlayoffTeam],
        presidents_trophy_team: PlayoffTeam,
        conference_leaders: dict[str, PlayoffTeam],
    ) -> None:
        """Assign status indicators to all teams.

        Status indicators (in order of precedence):
        - p: Presidents' Trophy (highest points overall)
        - z: Conference leader
        - y: Division leader (first in division)
        - x: Clinched playoff spot
        - e: Eliminated from playoffs

        Args:
            all_teams: List of all teams
            playoff_teams: Dictionary of teams in playoffs
            presidents_trophy_team: Presidents' Trophy winner
            conference_leaders: Dictionary of conference leaders
        """
        for team in all_teams:
            team.status_indicator = self._get_status_indicator(
                team, presidents_trophy_team, conference_leaders
            )

    def _group_by_conference(self, all_teams: list[PlayoffTeam]) -> dict[str, list[PlayoffTeam]]:
        """Group teams by conference for final output.

        Args:
            all_teams: List of all teams with status indicators assigned

        Returns:
            Dictionary mapping conference names to team lists
        """
        result: dict[str, list[PlayoffTeam]] = defaultdict(list)

        for team in all_teams:
            result[team.conference].append(team)

        # Sort within each conference by playoff status and score
        for conference in result:
            result[conference].sort(key=lambda x: (not x.in_playoffs, -x.total, -x.avg))

        return result

    def calculate_playoff_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, list[PlayoffTeam]]:
        """Calculate complete playoff standings with all teams.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary with structure:
            {
                'Eastern': [list of PlayoffTeam objects for Eastern Conference],
                'Western': [list of PlayoffTeam objects for Western Conference],
            }

        Examples:
            >>> calculator = PlayoffCalculator()
            >>> standings = calculator.calculate_playoff_standings(team_scores)
            >>> "Eastern" in standings
            True
        """
        logger.info("Calculating playoff standings")

        # Group teams by division
        teams_by_division = self._group_teams_by_division(team_scores)

        # Determine division leaders (top 3 from each division)
        playoff_teams, all_teams = self._determine_division_leaders(teams_by_division)

        # Determine wild card teams
        _ = self._determine_wild_cards(teams_by_division, playoff_teams)

        # Determine special status teams
        presidents_trophy_team = self._get_presidents_trophy_team(all_teams)
        conference_leaders = self._get_conference_leaders(all_teams)

        # Assign status indicators
        self._assign_status_indicators(
            all_teams, playoff_teams, presidents_trophy_team, conference_leaders
        )

        # Group results by conference
        result = self._group_by_conference(all_teams)

        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Playoff standings calculated for {len(all_teams)} teams")
        return result
