"""Protocol interfaces for dependency injection.

This module defines Protocol interfaces that enable loose coupling between components
through dependency injection. Using Protocols instead of concrete classes makes testing
easier (mock implementations) and reduces coupling between modules.

Design Pattern:
    - Protocol-based dependency injection (PEP 544)
    - Constructor injection pattern
    - Interface segregation principle

Benefits:
    - Easier testing with Protocol-based mocks
    - Reduced coupling between components
    - Flexibility to swap implementations
    - Type safety with static type checking

Examples:
    >>> # Testing with mock implementations
    >>> class MockAPIClient:
    ...     def get_teams(self) -> dict[str, dict[str, str]]:
    ...         return {"TOR": {"division": "Atlantic", "conference": "Eastern"}}
    ...
    >>> # Mock satisfies APIClientProtocol without inheritance
    >>> def use_client(client: APIClientProtocol) -> None:
    ...     teams = client.get_teams()
    ...
    >>> use_client(MockAPIClient())  # Type-safe!
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from nhl_scrabble.models.player import PlayerScore
    from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings
    from nhl_scrabble.models.team import TeamScore


class APIClientProtocol(Protocol):
    """Protocol for NHL API client operations.

    Defines the interface for fetching NHL data from the API. Any class that implements
    these methods can be used as an API client, enabling easy mocking in tests.

    Thread Safety:
        Implementations should be thread-safe for concurrent roster fetching.

    Resource Management:
        Implementations should support context manager protocol for session cleanup.
    """

    def get_teams(self, season: str | None = None) -> dict[str, dict[str, str]]:
        """Fetch all NHL teams with division and conference information.

        Args:
            season: Optional season in format 'YYYYYYYY' (e.g., '20222023').
                If None, fetches current season data.

        Returns:
            Dictionary mapping team abbreviations to their metadata:
            {
                'TOR': {'division': 'Atlantic', 'conference': 'Eastern'},
                'MTL': {'division': 'Atlantic', 'conference': 'Eastern'},
                ...
            }

        Raises:
            NHLApiError: If unable to fetch teams data
        """
        ...

    def get_team_roster(
        self, team_abbrev: str, season: str | None = None
    ) -> dict[str, list[dict[str, object]]]:
        """Fetch the roster for a specific team.

        Args:
            team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL')
            season: Optional season in format 'YYYYYYYY' (e.g., '20222023').
                If None, fetches current season roster.

        Returns:
            Dictionary containing roster data with 'forwards', 'defensemen', and 'goalies' keys

        Raises:
            NHLApiNotFoundError: If roster is not found (404 response)
            NHLApiError: For other API errors
        """
        ...

    def clear_cache(self) -> None:
        """Clear the HTTP cache.

        Clears all cached API responses, forcing fresh fetches on next requests.
        """
        ...

    def close(self) -> None:
        """Close the client session and release resources.

        Should be called when the client is no longer needed to properly clean up network
        connections and resources.
        """
        ...


class ScorerProtocol(Protocol):
    """Protocol for scoring operations.

    Defines the interface for calculating scores from player names. Supports both
    standard Scrabble scoring and custom scoring systems.

    Performance:
        Implementations should use caching for repeated name scoring to improve performance.
    """

    def score_player(
        self, player_data: dict[str, dict[str, str]], team: str, division: str, conference: str
    ) -> PlayerScore:
        """Score a player and return a PlayerScore object.

        Args:
            player_data: Dictionary with 'firstName' and 'lastName' keys containing 'default' values
            team: Team abbreviation
            division: Division name
            conference: Conference name

        Returns:
            PlayerScore object with all scoring information including first/last/full scores

        Examples:
            >>> player = {"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}
            >>> scorer.score_player(player, "EDM", "Pacific", "Western")
            PlayerScore(first_name="Connor", last_name="McDavid", full_score=24, ...)
        """
        ...


class TeamProcessorProtocol(Protocol):
    """Protocol for team processing operations.

    Defines the interface for processing NHL team rosters, calculating scores, and
    aggregating standings. Orchestrates API client and scorer to produce team-level
    and league-level statistics.

    Concurrency:
        Implementations may fetch team rosters concurrently for improved performance.
    """

    def process_all_teams(
        self,
        progress_callback: Callable[[str], None] | None = None,
        season: str | None = None,
    ) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
        """Process all NHL teams and calculate scores.

        Args:
            progress_callback: Optional callback to report progress after each team.
                Called with team abbreviation after successfully processing each team.
            season: Optional season to analyze (format: YYYYYYYY, e.g., 20222023).
                If None, fetches current season data.

        Returns:
            Tuple containing:
                - Dictionary mapping team abbreviations to TeamScore objects
                - List of all PlayerScore objects across all teams
                - List of team abbreviations that failed to fetch

        Examples:
            >>> teams, players, failed = processor.process_all_teams()
            >>> len(teams) > 0
            True
            >>> teams_2022, players_2022, failed = processor.process_all_teams(season="20222023")
            >>> len(teams_2022) > 0
            True
        """
        ...

    def calculate_division_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, DivisionStandings]:
        """Calculate division-level standings from team scores.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary mapping division names to DivisionStandings objects

        Examples:
            >>> standings = processor.calculate_division_standings(teams)
            >>> "Atlantic" in standings
            True
        """
        ...

    def calculate_conference_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, ConferenceStandings]:
        """Calculate conference-level standings from team scores.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary mapping conference names to ConferenceStandings objects

        Examples:
            >>> standings = processor.calculate_conference_standings(teams)
            >>> "Eastern" in standings
            True
        """
        ...
