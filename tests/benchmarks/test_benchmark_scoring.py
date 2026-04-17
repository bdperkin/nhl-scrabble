"""Benchmark tests for Scrabble scoring performance.

These benchmarks measure the performance of Scrabble scoring operations,
which are critical for the application as they're called ~700 times per analysis.

Performance targets:
- Short name (2-5 chars): <100 ns
- Medium name (6-10 chars): <150 ns
- Long name (11+ chars): <200 ns
- Full roster (23 players): <5 μs
- All teams (~700 players): <100 μs

Regression threshold: 20% (configurable in pyproject.toml)
"""

from typing import Any

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.scoring.scrabble import ScrabbleScorer


@pytest.fixture
def scorer() -> ScrabbleScorer:
    """Create ScrabbleScorer instance for benchmarking.

    Returns:
        ScrabbleScorer instance
    """
    return ScrabbleScorer()


class TestScoringSingleName:
    """Benchmark individual scoring operations.

    Tests cover different name lengths to ensure performance scales linearly.
    """

    def test_benchmark_short_name(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring short names (2-5 characters).

        Short names are common (OVI, ROY, ORR, etc.).
        Target: <100 ns

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        result = benchmark(scorer.calculate_score, "OVI")
        assert result > 0

    def test_benchmark_medium_name(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring medium names (6-10 characters).

        Medium names are the most common case (MATTHEWS, MARNER, etc.).
        Target: <150 ns

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        result = benchmark(scorer.calculate_score, "MATTHEWS")
        assert result > 0

    def test_benchmark_long_name(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring long names (11+ characters).

        Long names are edge cases (KONSTANTINOV, etc.).
        Target: <200 ns

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        result = benchmark(scorer.calculate_score, "KONSTANTINOV")
        assert result > 0

    def test_benchmark_full_name(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring full player name (first + last).

        This is the typical usage pattern in the application.
        Target: <300 ns

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        result = benchmark(scorer.calculate_score, "Alexander Ovechkin")
        assert result > 0


class TestScoringBulkOperations:
    """Benchmark batch scoring operations.

    These tests simulate real-world usage where multiple players are scored in a single analysis
    run.
    """

    def test_benchmark_team_roster(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring full team roster (23 players).

        This simulates scoring a complete NHL team roster.
        Target: <5 μs

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        # Generate realistic player names (23 players per roster)
        names = [f"Player{i} Name{i}" for i in range(23)]

        def score_all() -> list[int]:
            return [scorer.calculate_score(name) for name in names]

        result = benchmark(score_all)
        assert len(result) == 23
        assert all(score > 0 for score in result)

    def test_benchmark_full_league(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring all NHL players (~700).

        This simulates scoring all NHL rosters in a single analysis.
        Target: <100 μs

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        # Generate ~700 player names (32 teams * ~23 players)
        names = [f"Player{i} Name{i}" for i in range(700)]

        def score_all() -> list[int]:
            return [scorer.calculate_score(name) for name in names]

        result = benchmark(score_all)
        assert len(result) == 700
        assert all(score > 0 for score in result)


class TestScoringPlayerModels:
    """Benchmark scoring with player data dictionaries.

    These tests use actual player data structures to ensure no performance degradation from model
    overhead.
    """

    def test_benchmark_score_player(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring player data.

        This is the actual usage pattern in the application.
        Target: <500 ns

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        player_data = {
            "firstName": {"default": "Alexander"},
            "lastName": {"default": "Ovechkin"},
        }
        result = benchmark(scorer.score_player, player_data, "WSH", "Metropolitan", "Eastern")
        assert result.full_score > 0
        assert result.full_name == "Alexander Ovechkin"

    def test_benchmark_score_player_roster(self, benchmark: Any, scorer: ScrabbleScorer) -> None:
        """Benchmark scoring roster of player data.

        This simulates scoring a complete team roster using player data.
        Target: <10 μs

        Args:
            benchmark: pytest-benchmark fixture
            scorer: ScrabbleScorer instance
        """
        # Create realistic roster
        players = [
            {
                "firstName": {"default": f"FirstName{i}"},
                "lastName": {"default": f"LastName{i}"},
            }
            for i in range(23)
        ]

        def score_all() -> list[PlayerScore]:
            return [scorer.score_player(p, "TOR", "Atlantic", "Eastern") for p in players]

        result = benchmark(score_all)
        assert len(result) == 23
        assert all(ps.full_score > 0 for ps in result)
