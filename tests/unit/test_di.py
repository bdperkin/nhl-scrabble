"""Unit tests for dependency injection container."""

from unittest.mock import Mock

import pytest

from nhl_scrabble.config import Config
from nhl_scrabble.di import DependencyContainer, create_dependencies
from nhl_scrabble.interfaces import APIClientProtocol, ScorerProtocol, TeamProcessorProtocol


class TestDependencyContainer:
    """Test dependency injection container."""

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration."""
        return Config(
            api_base_url="https://api-web.nhle.com/v1",
            api_timeout=30,
            api_retries=3,
            rate_limit_max_requests=30,
            rate_limit_window=60.0,
            backoff_factor=1.0,
            max_backoff=30.0,
            cache_enabled=False,  # Disable cache for testing
            cache_expiry=3600,
            cache_dir="/tmp/test_cache",  # noqa: PTH122
            dos_max_connections=100,
            dos_max_per_host=10,
            dos_circuit_breaker_threshold=5,
            dos_circuit_breaker_timeout=60,
        )

    @pytest.fixture
    def container(self, config: Config) -> DependencyContainer:
        """Create dependency container."""
        return DependencyContainer(config)

    def test_container_initialization(self, config: Config) -> None:
        """Test container initializes with config."""
        container = DependencyContainer(config)
        assert container.config == config

    def test_create_api_client_default(self, container: DependencyContainer) -> None:
        """Test API client creation with default settings."""
        client = container.create_api_client()

        assert client is not None
        # Client should implement protocol
        assert isinstance(client, APIClientProtocol)

        # Clean up
        client.close()

    def test_create_api_client_cache_override(self, container: DependencyContainer) -> None:
        """Test API client cache override."""
        # Create with cache disabled
        client = container.create_api_client(cache_enabled=False)
        assert client is not None

        # Clean up
        client.close()

    def test_create_api_client_cache_dir_override(self, container: DependencyContainer) -> None:
        """Test API client cache directory override."""
        # Create with custom cache directory
        client = container.create_api_client(cache_dir="/tmp/custom_cache")  # noqa: PTH122
        assert client is not None

        # Clean up
        client.close()

    def test_create_scorer_default(self, container: DependencyContainer) -> None:
        """Test scorer creation with standard values."""
        scorer = container.create_scorer()

        assert scorer is not None
        assert isinstance(scorer, ScorerProtocol)

        # Verify standard Scrabble scoring
        assert scorer.calculate_score("A") == 1
        assert scorer.calculate_score("Z") == 10

    def test_create_scorer_custom_values(self, container: DependencyContainer) -> None:
        """Test scorer with custom letter values."""
        # Create custom values where all letters = 1
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = container.create_scorer(letter_values=custom_values)

        assert scorer is not None

        # Verify custom scoring (use calculate_score_custom for custom values)
        assert scorer.calculate_score_custom("A") == 1
        assert scorer.calculate_score_custom("Z") == 1  # Custom value, not 10
        assert scorer.calculate_score_custom("ALEX") == 4  # 4 letters x 1 point each

    def test_create_team_processor_auto_dependencies(self, container: DependencyContainer) -> None:
        """Test processor creation with auto-created dependencies."""
        processor = container.create_team_processor()

        assert processor is not None
        assert isinstance(processor, TeamProcessorProtocol)

    def test_create_team_processor_injected_api_client(
        self,
        container: DependencyContainer,
    ) -> None:
        """Test processor with injected API client."""
        mock_client = Mock(spec=APIClientProtocol)
        processor = container.create_team_processor(api_client=mock_client)

        assert processor is not None
        assert isinstance(processor, TeamProcessorProtocol)

    def test_create_team_processor_injected_scorer(self, container: DependencyContainer) -> None:
        """Test processor with injected scorer."""
        mock_scorer = Mock(spec=ScorerProtocol)
        processor = container.create_team_processor(scorer=mock_scorer)

        assert processor is not None
        assert isinstance(processor, TeamProcessorProtocol)

    def test_create_team_processor_injected_dependencies(
        self,
        container: DependencyContainer,
    ) -> None:
        """Test processor with injected mock dependencies."""
        mock_client = Mock(spec=APIClientProtocol)
        mock_scorer = Mock(spec=ScorerProtocol)

        processor = container.create_team_processor(api_client=mock_client, scorer=mock_scorer)

        assert processor is not None
        assert isinstance(processor, TeamProcessorProtocol)

    def test_create_team_processor_custom_max_workers(self, container: DependencyContainer) -> None:
        """Test processor with custom max_workers."""
        processor = container.create_team_processor(max_workers=10)

        assert processor is not None
        assert isinstance(processor, TeamProcessorProtocol)


class TestCreateDependenciesFunction:
    """Test create_dependencies convenience function."""

    @pytest.fixture
    def config(self) -> Config:
        """Create test configuration."""
        return Config(
            api_base_url="https://api-web.nhle.com/v1",
            api_timeout=30,
            api_retries=3,
            rate_limit_max_requests=30,
            rate_limit_window=60.0,
            backoff_factor=1.0,
            max_backoff=30.0,
            cache_enabled=False,
            cache_expiry=3600,
            cache_dir="/tmp/test_cache",  # noqa: PTH122
            dos_max_connections=100,
            dos_max_per_host=10,
            dos_circuit_breaker_threshold=5,
            dos_circuit_breaker_timeout=60,
        )

    def test_create_dependencies_all_defaults(self, config: Config) -> None:
        """Test creating all dependencies with defaults."""
        api_client, scorer, processor = create_dependencies(config)

        assert isinstance(api_client, APIClientProtocol)
        assert isinstance(scorer, ScorerProtocol)
        assert isinstance(processor, TeamProcessorProtocol)

        # Clean up
        api_client.close()

    def test_create_dependencies_custom_scoring(self, config: Config) -> None:
        """Test creating dependencies with custom scoring values."""
        custom_values = {chr(i): 5 for i in range(65, 91)}
        api_client, scorer, processor = create_dependencies(config, scoring_values=custom_values)

        assert isinstance(api_client, APIClientProtocol)
        assert isinstance(scorer, ScorerProtocol)
        assert isinstance(processor, TeamProcessorProtocol)

        # Verify custom scoring (use calculate_score_custom for custom values)
        assert scorer.calculate_score_custom("A") == 5
        assert scorer.calculate_score_custom("ALEX") == 20  # 4 letters x 5 points each

        # Clean up
        api_client.close()

    def test_create_dependencies_cache_override(self, config: Config) -> None:
        """Test creating dependencies with cache override."""
        api_client, scorer, processor = create_dependencies(config, cache_enabled=True)

        assert isinstance(api_client, APIClientProtocol)
        assert isinstance(scorer, ScorerProtocol)
        assert isinstance(processor, TeamProcessorProtocol)

        # Clean up
        api_client.close()
