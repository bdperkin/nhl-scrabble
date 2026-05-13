"""Pytest configuration and fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.scoring.scrabble import ScrabbleScorer


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_standings_data(fixtures_dir: Path) -> dict[str, Any]:
    """Load sample standings data from fixture file."""
    with open(fixtures_dir / "sample_standings.json") as f:
        data: dict[str, Any] = json.load(f)
        return data


@pytest.fixture
def sample_roster_data(fixtures_dir: Path) -> dict[str, Any]:
    """Load sample roster data from fixture file."""
    with open(fixtures_dir / "sample_roster.json") as f:
        data: dict[str, Any] = json.load(f)
        return data


@pytest.fixture
def scrabble_scorer() -> ScrabbleScorer:
    """Return a ScrabbleScorer instance."""
    return ScrabbleScorer()


@pytest.fixture
def api_client() -> NHLApiClient:
    """Return an NHLApiClient instance with test configuration."""
    return NHLApiClient(timeout=5, retries=2, rate_limit_max_requests=1000, rate_limit_window=1.0)


@pytest.fixture
def sample_player() -> PlayerScore:
    """Return a sample PlayerScore object."""
    return PlayerScore(
        first_name="Connor",
        last_name="McDavid",
        full_name="Connor McDavid",
        first_score=15,
        last_score=17,
        full_score=32,
        team="EDM",
        division="Pacific",
        conference="Western",
    )


@pytest.fixture
def sample_team_score(sample_player: PlayerScore) -> TeamScore:
    """Return a sample TeamScore object."""
    return TeamScore(
        abbrev="EDM",
        name="Edmonton Oilers",
        total=100,
        players=[sample_player],
        division="Pacific",
        conference="Western",
    )


@pytest.fixture
def mock_config() -> Any:
    """Return a mock Config object for testing."""
    from unittest.mock import MagicMock

    from nhl_scrabble.config import Config

    config = MagicMock(spec=Config)
    config.output_format = "text"
    config.api_timeout = 30
    config.api_retries = 3
    config.rate_limit_delay = 0.3
    config.verbose = False
    config.sanitize_logs = False
    config.top_players_count = 20
    config.top_team_players_count = 5
    return config


@pytest.fixture
def mock_team_scores(sample_team_score: TeamScore) -> dict[str, TeamScore]:
    """Return a dictionary of mock TeamScore objects for testing."""
    return {
        "EDM": sample_team_score,
        "TOR": TeamScore(
            abbrev="TOR",
            name="Toronto Maple Leafs",
            total=95,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
    }
