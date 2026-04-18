"""Protocol interfaces for dependency injection.

This module defines Protocol interfaces that components depend on, enabling dependency injection and
easier testing with mock implementations.
"""

from __future__ import annotations

from typing import Any, Protocol

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore


class APIClientProtocol(Protocol):
    """Protocol for NHL API clients.

    This protocol defines the interface for fetching NHL data. Any class implementing these methods
    can be used as an API client, enabling easy mocking in tests.
    """

    def get_teams(self) -> dict[str, dict[str, Any]]:
        """Fetch all NHL teams with metadata.

        Returns:
            Dictionary mapping team abbreviations to team metadata containing
            division and conference information.

        Raises:
            NHLApiError: If the API request fails
        """
        ...

    def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:
        """Fetch roster for a specific team.

        Args:
            team_abbrev: Team abbreviation (e.g., 'TOR', 'BOS')

        Returns:
            Dictionary containing roster data with player information

        Raises:
            NHLApiError: If the API request fails
            NHLApiNotFoundError: If the team roster is not found
        """
        ...

    def clear_cache(self) -> None:
        """Clear the API response cache.

        This method clears any cached API responses, forcing fresh data to be fetched on the next
        request.
        """
        ...

    def close(self) -> None:
        """Close the API client and clean up resources.

        This method should be called when the client is no longer needed to properly release
        resources like HTTP sessions.
        """
        ...


class ScorerProtocol(Protocol):
    """Protocol for Scrabble scorers.

    This protocol defines the interface for calculating Scrabble scores. Any class implementing
    these methods can be used as a scorer.
    """

    def calculate_score(self, text: str) -> int:
        """Calculate the Scrabble score for a text string.

        Args:
            text: Text to score (e.g., player name)

        Returns:
            Total Scrabble score based on letter values

        Examples:
            >>> scorer = ScrabbleScorer()
            >>> scorer.calculate_score("ALEX")
            11
        """
        ...

    def score_player(
        self, player_data: dict[str, Any], team: str, division: str, conference: str
    ) -> PlayerScore:
        """Calculate Scrabble score for a player.

        Args:
            player_data: Dictionary with 'firstName' and 'lastName' keys containing 'default' values
            team: Team abbreviation
            division: Division name
            conference: Conference name

        Returns:
            PlayerScore object with calculated scores

        Examples:
            >>> scorer = ScrabbleScorer()
            >>> player = {"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}
            >>> score = scorer.score_player(player, "EDM", "Pacific", "Western")
            >>> score.full_score > 0
            True
        """
        ...


class TeamProcessorProtocol(Protocol):
    """Protocol for team processors.

    This protocol defines the interface for processing NHL team data and calculating aggregate
    scores.
    """

    def process_all_teams(
        self,
    ) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
        """Process all NHL teams and calculate scores.

        Returns:
            Tuple containing:
                - Dictionary mapping team abbreviations to TeamScore objects
                - List of all PlayerScore objects across all teams
                - List of team abbreviations that failed to fetch

        Examples:
            >>> processor = TeamProcessor(client, scorer)
            >>> teams, players, failed = processor.process_all_teams()
            >>> len(teams) > 0
            True
        """
        ...

    def calculate_division_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, DivisionStandings]:
        """Calculate division-level standings.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary mapping division names to DivisionStandings objects

        Examples:
            >>> standings = processor.calculate_division_standings(team_scores)
            >>> "Metropolitan" in standings
            True
        """
        ...

    def calculate_conference_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, ConferenceStandings]:
        """Calculate conference-level standings.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary mapping conference names to ConferenceStandings objects

        Examples:
            >>> standings = processor.calculate_conference_standings(team_scores)
            >>> "Eastern" in standings
            True
        """
        ...


class PlayoffCalculatorProtocol(Protocol):
    """Protocol for playoff calculators.

    This protocol defines the interface for calculating NHL playoff standings based on team scores.
    """

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
        ...


class ReporterProtocol(Protocol):
    """Protocol for report generators.

    This protocol defines the interface for generating reports in different formats.
    """

    def generate(self, data: Any) -> str:
        """Generate a report from the provided data.

        Args:
            data: Report data (type varies by reporter)

        Returns:
            Formatted report string

        Examples:
            >>> reporter = TeamReporter()
            >>> report = reporter.generate(team_scores)
            >>> len(report) > 0
            True
        """
        ...
