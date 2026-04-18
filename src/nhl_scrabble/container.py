"""Dependency injection container.

This module provides a simple dependency injection container that creates and manages application
dependencies. The container pattern enables loose coupling and easier testing by allowing
dependencies to be overridden with mocks.
"""

from __future__ import annotations

from typing import Any

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.config import Config
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.protocols import (
    APIClientProtocol,
    PlayoffCalculatorProtocol,
    ScorerProtocol,
    TeamProcessorProtocol,
)
from nhl_scrabble.reports.conference_report import ConferenceReporter
from nhl_scrabble.reports.division_report import DivisionReporter
from nhl_scrabble.reports.playoff_report import PlayoffReporter
from nhl_scrabble.reports.stats_report import StatsReporter
from nhl_scrabble.reports.team_report import TeamReporter
from nhl_scrabble.scoring.scrabble import ScrabbleScorer


class Container:
    """Dependency injection container.

    This container creates and manages application dependencies using a factory pattern.
    Dependencies can be overridden for testing by passing custom implementations to the
    constructor or using the setter methods.

    Example:
        # Production usage with defaults
        >>> container = Container(config)
        >>> api_client = container.api_client()
        >>> scorer = container.scorer()

        # Testing with mocks
        >>> mock_client = Mock(spec=APIClientProtocol)
        >>> container = Container(config, api_client=mock_client)
        >>> assert container.api_client() is mock_client

    Attributes:
        config: Application configuration
    """

    def __init__(
        self,
        config: Config,
        api_client: APIClientProtocol | None = None,
        scorer: ScorerProtocol | None = None,
        team_processor: TeamProcessorProtocol | None = None,
        playoff_calculator: PlayoffCalculatorProtocol | None = None,
    ) -> None:
        """Initialize the dependency container.

        Args:
            config: Application configuration
            api_client: Optional API client override (for testing)
            scorer: Optional scorer override (for testing)
            team_processor: Optional team processor override (for testing)
            playoff_calculator: Optional playoff calculator override (for testing)
        """
        self.config = config
        self._api_client = api_client
        self._scorer = scorer
        self._team_processor = team_processor
        self._playoff_calculator = playoff_calculator

        # Reporter overrides
        self._conference_reporter: Any = None
        self._division_reporter: Any = None
        self._playoff_reporter: Any = None
        self._team_reporter: Any = None
        self._stats_reporter: Any = None

    def api_client(self) -> APIClientProtocol:
        """Get or create the API client.

        Returns:
            API client instance (real or mock)

        Examples:
            >>> container = Container(config)
            >>> client = container.api_client()
            >>> isinstance(client, NHLApiClient)
            True
        """
        if self._api_client is None:
            self._api_client = NHLApiClient(
                timeout=self.config.api_timeout,
                retries=self.config.api_retries,
                rate_limit_delay=self.config.rate_limit_delay,
                backoff_factor=self.config.backoff_factor,
                max_backoff=self.config.max_backoff,
                cache_enabled=self.config.cache_enabled,
                cache_expiry=self.config.cache_expiry,
            )
        return self._api_client

    def scorer(self) -> ScorerProtocol:
        """Get or create the Scrabble scorer.

        Returns:
            Scorer instance (real or mock)

        Examples:
            >>> container = Container(config)
            >>> scorer = container.scorer()
            >>> isinstance(scorer, ScrabbleScorer)
            True
        """
        if self._scorer is None:
            self._scorer = ScrabbleScorer()
        return self._scorer

    def team_processor(self) -> TeamProcessorProtocol:
        """Get or create the team processor.

        The team processor depends on api_client and scorer, which are injected
        automatically from this container.

        Returns:
            Team processor instance (real or mock)

        Examples:
            >>> container = Container(config)
            >>> processor = container.team_processor()
            >>> isinstance(processor, TeamProcessor)
            True
        """
        if self._team_processor is None:
            self._team_processor = TeamProcessor(
                api_client=self.api_client(),  # type: ignore[arg-type]
                scorer=self.scorer(),  # type: ignore[arg-type]
            )
        return self._team_processor

    def playoff_calculator(self) -> PlayoffCalculatorProtocol:
        """Get or create the playoff calculator.

        Returns:
            Playoff calculator instance (real or mock)

        Examples:
            >>> container = Container(config)
            >>> calculator = container.playoff_calculator()
            >>> isinstance(calculator, PlayoffCalculator)
            True
        """
        if self._playoff_calculator is None:
            self._playoff_calculator = PlayoffCalculator()
        return self._playoff_calculator

    def conference_reporter(self) -> Any:
        """Get or create the conference reporter.

        Returns:
            Conference reporter instance

        Examples:
            >>> container = Container(config)
            >>> reporter = container.conference_reporter()
            >>> isinstance(reporter, ConferenceReporter)
            True
        """
        if self._conference_reporter is None:
            self._conference_reporter = ConferenceReporter()
        return self._conference_reporter

    def division_reporter(self) -> Any:
        """Get or create the division reporter.

        Returns:
            Division reporter instance

        Examples:
            >>> container = Container(config)
            >>> reporter = container.division_reporter()
            >>> isinstance(reporter, DivisionReporter)
            True
        """
        if self._division_reporter is None:
            self._division_reporter = DivisionReporter()
        return self._division_reporter

    def playoff_reporter(self) -> Any:
        """Get or create the playoff reporter.

        Returns:
            Playoff reporter instance

        Examples:
            >>> container = Container(config)
            >>> reporter = container.playoff_reporter()
            >>> isinstance(reporter, PlayoffReporter)
            True
        """
        if self._playoff_reporter is None:
            self._playoff_reporter = PlayoffReporter()
        return self._playoff_reporter

    def team_reporter(self) -> Any:
        """Get or create the team reporter.

        Returns:
            Team reporter instance configured with top_players_per_team from config

        Examples:
            >>> container = Container(config)
            >>> reporter = container.team_reporter()
            >>> isinstance(reporter, TeamReporter)
            True
        """
        if self._team_reporter is None:
            self._team_reporter = TeamReporter(
                top_players_per_team=self.config.top_team_players_count
            )
        return self._team_reporter

    def stats_reporter(self) -> Any:
        """Get or create the stats reporter.

        Returns:
            Stats reporter instance configured with top_players_count from config

        Examples:
            >>> container = Container(config)
            >>> reporter = container.stats_reporter()
            >>> isinstance(reporter, StatsReporter)
            True
        """
        if self._stats_reporter is None:
            self._stats_reporter = StatsReporter(top_players_count=self.config.top_players_count)
        return self._stats_reporter

    def set_api_client(self, api_client: APIClientProtocol) -> None:
        """Override the API client (for testing).

        Args:
            api_client: API client instance to use

        Examples:
            >>> from unittest.mock import Mock
            >>> container = Container(config)
            >>> mock_client = Mock(spec=APIClientProtocol)
            >>> container.set_api_client(mock_client)
            >>> assert container.api_client() is mock_client
        """
        self._api_client = api_client

    def set_scorer(self, scorer: ScorerProtocol) -> None:
        """Override the scorer (for testing).

        Args:
            scorer: Scorer instance to use

        Examples:
            >>> from unittest.mock import Mock
            >>> container = Container(config)
            >>> mock_scorer = Mock(spec=ScorerProtocol)
            >>> container.set_scorer(mock_scorer)
            >>> assert container.scorer() is mock_scorer
        """
        self._scorer = scorer

    def set_team_processor(self, team_processor: TeamProcessorProtocol) -> None:
        """Override the team processor (for testing).

        Args:
            team_processor: Team processor instance to use

        Examples:
            >>> from unittest.mock import Mock
            >>> container = Container(config)
            >>> mock_processor = Mock(spec=TeamProcessorProtocol)
            >>> container.set_team_processor(mock_processor)
            >>> assert container.team_processor() is mock_processor
        """
        self._team_processor = team_processor

    def set_playoff_calculator(self, playoff_calculator: PlayoffCalculatorProtocol) -> None:
        """Override the playoff calculator (for testing).

        Args:
            playoff_calculator: Playoff calculator instance to use

        Examples:
            >>> from unittest.mock import Mock
            >>> container = Container(config)
            >>> mock_calculator = Mock(spec=PlayoffCalculatorProtocol)
            >>> container.set_playoff_calculator(mock_calculator)
            >>> assert container.playoff_calculator() is mock_calculator
        """
        self._playoff_calculator = playoff_calculator
