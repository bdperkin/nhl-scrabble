"""Filtering logic for NHL Scrabble analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore


@dataclass(frozen=True, slots=True)
class AnalysisFilters:
    """Configuration for filtering NHL Scrabble analysis results.

    Attributes:
        divisions: Set of division names to include (e.g., {'Atlantic', 'Metropolitan'})
        conferences: Set of conference names to include (e.g., {'Eastern', 'Western'})
        teams: Set of team abbreviations to include (e.g., {'TOR', 'MTL'})
        excluded_teams: Set of team abbreviations to exclude (e.g., {'BOS', 'NYR'})
        min_score: Minimum player score to include (inclusive)
        max_score: Maximum player score to include (inclusive)
    """

    divisions: frozenset[str] | None = None
    conferences: frozenset[str] | None = None
    teams: frozenset[str] | None = None
    excluded_teams: frozenset[str] | None = None
    min_score: int | None = None
    max_score: int | None = None

    @classmethod
    def from_options(
        cls,
        division: str | None = None,
        conference: str | None = None,
        teams: str | None = None,
        exclude: str | None = None,
        min_score: int | None = None,
        max_score: int | None = None,
    ) -> AnalysisFilters:
        """Create filters from CLI options.

        Args:
            division: Comma-separated list of division names
            conference: Comma-separated list of conference names
            teams: Comma-separated list of team abbreviations
            exclude: Comma-separated list of team abbreviations to exclude
            min_score: Minimum player score (inclusive)
            max_score: Maximum player score (inclusive)

        Returns:
            AnalysisFilters instance

        Example:
            >>> filters = AnalysisFilters.from_options(
            ...     division="Atlantic,Metropolitan",
            ...     teams="TOR,MTL",
            ...     min_score=50
            ... )
        """
        return cls(
            divisions=frozenset(d.strip() for d in division.split(",")) if division else None,
            conferences=(
                frozenset(c.strip() for c in conference.split(",")) if conference else None
            ),
            teams=frozenset(t.strip().upper() for t in teams.split(",")) if teams else None,
            excluded_teams=(
                frozenset(e.strip().upper() for e in exclude.split(",")) if exclude else None
            ),
            min_score=min_score,
            max_score=max_score,
        )

    def is_active(self) -> bool:
        """Check if any filters are active.

        Returns:
            True if at least one filter is set, False otherwise
        """
        return any(
            [
                self.divisions,
                self.conferences,
                self.teams,
                self.excluded_teams,
                self.min_score is not None,
                self.max_score is not None,
            ]
        )

    def should_include_team(self, team: TeamScore | PlayoffTeam) -> bool:
        """Check if a team should be included based on filters.

        Args:
            team: Team to check (TeamScore or PlayoffTeam)

        Returns:
            True if team passes all active filters, False otherwise
        """
        # Check exclusion first (takes precedence)
        if self.excluded_teams and team.abbrev in self.excluded_teams:
            return False

        # Check team filter
        if self.teams and team.abbrev not in self.teams:
            return False

        # Check division filter
        if self.divisions and team.division not in self.divisions:
            return False

        # Check conference filter
        return not (self.conferences and team.conference not in self.conferences)

    def should_include_player(self, player: PlayerScore) -> bool:
        """Check if a player should be included based on score filters.

        Args:
            player: Player to check

        Returns:
            True if player passes all active score filters, False otherwise
        """
        # Check minimum score
        if self.min_score is not None and player.full_score < self.min_score:
            return False

        # Check maximum score
        return not (self.max_score is not None and player.full_score > self.max_score)


def filter_teams(
    team_scores: dict[str, TeamScore], filters: AnalysisFilters
) -> dict[str, TeamScore]:
    """Filter team scores based on filters.

    Args:
        team_scores: Dictionary of team abbreviation to TeamScore
        filters: Filters to apply

    Returns:
        Filtered dictionary of team scores
    """
    if not filters.is_active():
        return team_scores

    return {
        abbrev: team for abbrev, team in team_scores.items() if filters.should_include_team(team)
    }


def filter_players(players: list[PlayerScore], filters: AnalysisFilters) -> list[PlayerScore]:
    """Filter player list based on score filters.

    Args:
        players: List of players
        filters: Filters to apply

    Returns:
        Filtered list of players
    """
    if not filters.is_active():
        return players

    # First filter by team (via team filters)
    filtered = []
    for player in players:
        # Check if player's team would be excluded
        if filters.excluded_teams and player.team in filters.excluded_teams:
            continue

        # Check team filter
        if filters.teams and player.team not in filters.teams:
            continue

        # Check division filter
        if filters.divisions and player.division not in filters.divisions:
            continue

        # Check conference filter
        if filters.conferences and player.conference not in filters.conferences:
            continue

        # Check score filters
        if not filters.should_include_player(player):
            continue

        filtered.append(player)

    return filtered


def filter_division_standings(
    division_standings: dict[str, DivisionStandings], filters: AnalysisFilters
) -> dict[str, DivisionStandings]:
    """Filter division standings based on filters.

    Args:
        division_standings: Dictionary of division name to DivisionStandings
        filters: Filters to apply

    Returns:
        Filtered dictionary of division standings
    """
    if not filters.is_active():
        return division_standings

    # If division filter is active, only include those divisions
    if filters.divisions:
        return {
            name: standings
            for name, standings in division_standings.items()
            if name in filters.divisions
        }

    # If no division filter but conference filter, filter by conference
    if filters.conferences:
        # Need to filter divisions that belong to the filtered conferences
        # Division-to-conference mapping (NHL structure)
        division_to_conference = {
            "Atlantic": "Eastern",
            "Metropolitan": "Metropolitan",
            "Central": "Western",
            "Pacific": "Western",
        }
        return {
            name: standings
            for name, standings in division_standings.items()
            if division_to_conference.get(name) in filters.conferences
        }

    return division_standings


def filter_conference_standings(
    conference_standings: dict[str, Any], filters: AnalysisFilters
) -> dict[str, Any]:
    """Filter conference standings based on filters.

    Args:
        conference_standings: Dictionary of conference name to standings
        filters: Filters to apply

    Returns:
        Filtered dictionary of conference standings
    """
    if not filters.is_active():
        return conference_standings

    # If conference filter is active, only include those conferences
    if filters.conferences:
        return {
            name: standings
            for name, standings in conference_standings.items()
            if name in filters.conferences
        }

    return conference_standings


def filter_playoff_standings(
    playoff_standings: dict[str, list[PlayoffTeam]], filters: AnalysisFilters
) -> dict[str, list[PlayoffTeam]]:
    """Filter playoff standings based on filters.

    Args:
        playoff_standings: Dictionary of conference to list of playoff teams
        filters: Filters to apply

    Returns:
        Filtered dictionary of playoff standings
    """
    if not filters.is_active():
        return playoff_standings

    filtered_standings: dict[str, list[PlayoffTeam]] = {}

    for conference, teams in playoff_standings.items():
        # Skip conference if filtered out
        if filters.conferences and conference not in filters.conferences:
            continue

        # Filter teams within this conference
        filtered_teams = [team for team in teams if filters.should_include_team(team)]

        # Only include conference if it has teams after filtering
        if filtered_teams:
            filtered_standings[conference] = filtered_teams

    return filtered_standings
