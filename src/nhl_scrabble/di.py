"""Dependency injection container and factory functions.

This module provides factory functions for creating application dependencies with proper
configuration. It centralizes dependency creation, making it easier to:

- Configure dependencies consistently
- Swap implementations for testing
- Manage dependency lifecycles
- Follow dependency inversion principle

Design Pattern:
    - Factory pattern for dependency creation
    - Dependency injection container (lightweight)
    - Configuration-based instantiation

Benefits:
    - Single source of truth for dependency creation
    - Easy to mock dependencies in tests
    - Consistent configuration across the application
    - Testability without modifying production code

Examples:
    >>> # Production usage
    >>> from nhl_scrabble.config import Config
    >>> config = Config.from_env()
    >>> container = DependencyContainer(config)
    >>> api_client = container.create_api_client()
    >>> scorer = container.create_scorer()
    >>> processor = container.create_team_processor()

    >>> # Testing with custom dependencies
    >>> class MockAPIClient: ...
    >>> container = DependencyContainer(config)
    >>> processor = container.create_team_processor(
    ...     api_client=MockAPIClient(),
    ...     scorer=scorer
    ... )
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nhl_scrabble.config import Config
    from nhl_scrabble.interfaces import APIClientProtocol, ScorerProtocol, TeamProcessorProtocol

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

logger = logging.getLogger(__name__)


class DependencyContainer:
    """Lightweight dependency injection container.

    Centralizes creation of application dependencies with configuration. Supports
    dependency injection for testing by allowing custom implementations to be passed.

    This is a lightweight container - it doesn't manage lifecycles or automatic
    wiring. Instead, it provides factory methods that create properly configured
    instances based on the application config.

    Attributes:
        config: Application configuration object
    """

    def __init__(self, config: Config) -> None:
        """Initialize the dependency container.

        Args:
            config: Application configuration object

        Examples:
            >>> from nhl_scrabble.config import Config
            >>> config = Config.from_env()
            >>> container = DependencyContainer(config)
        """
        self.config = config
        logger.debug("DependencyContainer initialized")

    def create_api_client(
        self,
        cache_enabled: bool | None = None,
    ) -> APIClientProtocol:
        """Create NHL API client with configuration.

        Creates a properly configured NHLApiClient instance using settings from the
        application config. The client handles API communication, rate limiting,
        caching, and retry logic.

        Args:
            cache_enabled: Override cache setting from config. If None, uses config value.

        Returns:
            Configured API client implementing APIClientProtocol

        Resource Management:
            Caller is responsible for calling close() on the client when done,
            or using it as a context manager:

            >>> with container.create_api_client() as client:
            ...     teams = client.get_teams()

        Examples:
            >>> client = container.create_api_client()
            >>> teams = client.get_teams()
            >>> client.close()

            >>> # Disable caching for fresh data
            >>> client = container.create_api_client(cache_enabled=False)
        """
        # Use override if provided, otherwise use config value
        use_cache = cache_enabled if cache_enabled is not None else self.config.cache_enabled

        client = NHLApiClient(
            base_url=self.config.api_base_url,
            timeout=self.config.api_timeout,
            retries=self.config.api_retries,
            rate_limit_max_requests=self.config.rate_limit_max_requests,
            rate_limit_window=self.config.rate_limit_window,
            backoff_factor=self.config.backoff_factor,
            max_backoff=self.config.max_backoff,
            cache_enabled=use_cache,
            cache_expiry=self.config.cache_expiry,
            dos_max_connections=self.config.dos_max_connections,
            dos_max_per_host=self.config.dos_max_per_host,
            dos_circuit_breaker_threshold=self.config.dos_circuit_breaker_threshold,
            dos_circuit_breaker_timeout=self.config.dos_circuit_breaker_timeout,
        )

        logger.debug(f"Created API client (cache_enabled={use_cache})")
        return client

    def create_scorer(
        self,
        letter_values: dict[str, int] | None = None,
    ) -> ScorerProtocol:
        """Create Scrabble scorer with optional custom values.

        Creates a ScrabbleScorer instance with either standard Scrabble letter values
        or custom scoring values (e.g., Wordle scoring, uniform values).

        Args:
            letter_values: Optional custom letter-to-point value mapping.
                If None, uses standard Scrabble values.

        Returns:
            Configured scorer implementing ScorerProtocol

        Examples:
            >>> # Standard Scrabble scoring
            >>> scorer = container.create_scorer()
            >>> scorer.calculate_score("ALEX")
            11

            >>> # Custom uniform scoring (all letters = 1 point)
            >>> uniform_values = {chr(i): 1 for i in range(65, 91)}
            >>> scorer = container.create_scorer(letter_values=uniform_values)
            >>> scorer.calculate_score("ALEX")
            4
        """
        scorer = ScrabbleScorer(letter_values=letter_values)

        if letter_values is not None:
            logger.debug(f"Created scorer with custom letter values ({len(letter_values)} letters)")
        else:
            logger.debug("Created scorer with standard Scrabble values")

        return scorer

    def create_team_processor(
        self,
        api_client: APIClientProtocol | None = None,
        scorer: ScorerProtocol | None = None,
        max_workers: int = 5,
    ) -> TeamProcessorProtocol:
        """Create team processor with dependencies.

        Creates a TeamProcessor instance with injected dependencies. If dependencies
        are not provided, creates them using the container's factory methods.

        This enables both production usage (automatic dependency creation) and testing
        usage (inject mock dependencies).

        Args:
            api_client: Optional API client. If None, creates one using create_api_client().
            scorer: Optional scorer. If None, creates one using create_scorer().
            max_workers: Maximum concurrent workers for team fetching (default: 5)

        Returns:
            Configured team processor implementing TeamProcessorProtocol

        Examples:
            >>> # Production usage - auto-create dependencies
            >>> processor = container.create_team_processor()

            >>> # Testing usage - inject mocks
            >>> mock_client = MockAPIClient()
            >>> mock_scorer = MockScorer()
            >>> processor = container.create_team_processor(
            ...     api_client=mock_client,
            ...     scorer=mock_scorer
            ... )
        """
        # Create dependencies if not provided
        if api_client is None:
            api_client = self.create_api_client()
            logger.debug("Auto-created API client for team processor")

        if scorer is None:
            scorer = self.create_scorer()
            logger.debug("Auto-created scorer for team processor")

        processor = TeamProcessor(
            api_client=api_client,
            scorer=scorer,
            max_workers=max_workers,
        )

        logger.debug(f"Created team processor (max_workers={max_workers})")
        return processor


def create_dependencies(
    config: Config,
    scoring_values: dict[str, int] | None = None,
    cache_enabled: bool | None = None,
) -> tuple[APIClientProtocol, ScorerProtocol, TeamProcessorProtocol]:
    """Create all core dependencies at once.

    This is a helper function for the common case where you need all three core
    dependencies configured consistently.

    Args:
        config: Application configuration
        scoring_values: Optional custom scoring values for the scorer
        cache_enabled: Optional cache override for API client

    Returns:
        Tuple of (api_client, scorer, team_processor)

    Examples:
        >>> from nhl_scrabble.config import Config
        >>> config = Config.from_env()
        >>> api_client, scorer, processor = create_dependencies(config)

        >>> # With custom scoring
        >>> custom_values = {"A": 5, "B": 10, ...}
        >>> api_client, scorer, processor = create_dependencies(
        ...     config,
        ...     scoring_values=custom_values
        ... )
    """
    container = DependencyContainer(config)

    api_client = container.create_api_client(cache_enabled=cache_enabled)
    scorer = container.create_scorer(letter_values=scoring_values)
    team_processor = container.create_team_processor(
        api_client=api_client,
        scorer=scorer,
    )

    logger.info("Created all core dependencies")
    return api_client, scorer, team_processor
