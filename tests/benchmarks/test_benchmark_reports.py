"""Benchmark tests for data processing performance.

These benchmarks measure the performance of data processing operations,
which are critical for overall application performance.

Performance targets:
- Player sorting (32 teams): <1 ms
- Team aggregation: <1 ms
- Data structure operations: <100 μs

Regression threshold: 20% (configurable in pyproject.toml)
"""

from typing import Any

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def sample_players() -> list[PlayerScore]:
    """Generate sample player data for benchmarking.

    Creates realistic player data for performance testing.

    Returns:
        List of ~700 PlayerScore objects (simulating NHL rosters)
    """
    players = []
    for i in range(700):
        player = PlayerScore(
            first_name=f"Player{i}",
            last_name=f"Name{i}",
            full_name=f"Player{i} Name{i}",
            first_score=10 + (i % 20),
            last_score=15 + (i % 25),
            full_score=25 + (i % 45),
            team=f"T{i % 32:02d}",
            division=["Atlantic", "Metropolitan", "Central", "Pacific"][i % 4],
            conference=["Eastern", "Western"][i % 2],
        )
        players.append(player)
    return players


@pytest.fixture
def sample_teams(sample_players: list[PlayerScore]) -> list[TeamScore]:
    """Generate sample team data for benchmarking.

    Creates realistic team data with players for performance testing.

    Args:
        sample_players: List of PlayerScore objects

    Returns:
        List of 32 TeamScore objects (simulating NHL teams)
    """
    teams = []
    # Group players by team
    team_players: dict[str, list[PlayerScore]] = {}
    for player in sample_players:
        if player.team not in team_players:
            team_players[player.team] = []
        team_players[player.team].append(player)

    for i in range(32):
        team_abbrev = f"T{i:02d}"
        players = team_players.get(team_abbrev, [])
        total = sum(p.full_score for p in players)

        team = TeamScore(
            abbrev=team_abbrev,
            total=total,
            players=players,
            division=["Atlantic", "Metropolitan", "Central", "Pacific"][i % 4],
            conference=["Eastern", "Western"][i % 2],
        )
        teams.append(team)

    return teams


class TestPlayerSortingPerformance:
    """Benchmark player sorting operations.

    Sorting is used extensively in report generation and must be fast.
    """

    def test_benchmark_sort_players_by_score(
        self,
        benchmark: Any,
        sample_players: list[PlayerScore],
    ) -> None:
        """Benchmark sorting all players by score.

        This is the most common sorting operation.
        Target: <1 ms

        Args:
            benchmark: pytest-benchmark fixture
            sample_players: List of PlayerScore objects
        """

        def sort_players() -> list[PlayerScore]:
            return sorted(sample_players, key=lambda x: x.full_score, reverse=True)

        result = benchmark(sort_players)
        assert len(result) == 700
        assert result[0].full_score >= result[-1].full_score

    def test_benchmark_sort_teams_by_total(
        self,
        benchmark: Any,
        sample_teams: list[TeamScore],
    ) -> None:
        """Benchmark sorting teams by total score.

        This is used for team standings.
        Target: <100 μs

        Args:
            benchmark: pytest-benchmark fixture
            sample_teams: List of TeamScore objects
        """

        def sort_teams() -> list[TeamScore]:
            return sorted(sample_teams, key=lambda x: x.total, reverse=True)

        result = benchmark(sort_teams)
        assert len(result) == 32
        assert result[0].total >= result[-1].total


class TestDataAggregationPerformance:
    """Benchmark data aggregation operations.

    Aggregations are used to build standings and statistics.
    """

    def test_benchmark_aggregate_by_division(
        self,
        benchmark: Any,
        sample_players: list[PlayerScore],
    ) -> None:
        """Benchmark grouping players by division.

        This is used for division standings.
        Target: <500 μs

        Args:
            benchmark: pytest-benchmark fixture
            sample_players: List of PlayerScore objects
        """

        def aggregate_by_division() -> dict[str, list[PlayerScore]]:
            divisions: dict[str, list[PlayerScore]] = {}
            for player in sample_players:
                if player.division not in divisions:
                    divisions[player.division] = []
                divisions[player.division].append(player)
            return divisions

        result = benchmark(aggregate_by_division)
        assert len(result) == 4  # 4 divisions
        assert sum(len(players) for players in result.values()) == 700

    def test_benchmark_calculate_team_totals(
        self,
        benchmark: Any,
        sample_teams: list[TeamScore],
    ) -> None:
        """Benchmark calculating team totals.

        This is used to build team scores.
        Target: <1 ms

        Args:
            benchmark: pytest-benchmark fixture
            sample_teams: List of TeamScore objects
        """

        def calculate_totals() -> list[int]:
            return [team.total for team in sample_teams]

        result = benchmark(calculate_totals)
        assert len(result) == 32


class TestStringOperationsPerformance:
    """Benchmark string operations used in reports.

    String formatting is used extensively in report generation.
    """

    def test_benchmark_format_player_lines(
        self,
        benchmark: Any,
        sample_players: list[PlayerScore],
    ) -> None:
        """Benchmark formatting player data as strings.

        This simulates report string building.
        Target: <5 ms

        Args:
            benchmark: pytest-benchmark fixture
            sample_players: List of PlayerScore objects
        """

        def format_players() -> list[str]:
            return [
                f"{p.full_name} ({p.team}): {p.full_score} [{p.first_score} + {p.last_score}]"
                for p in sample_players
            ]

        result = benchmark(format_players)
        assert len(result) == 700

    def test_benchmark_join_large_report(
        self,
        benchmark: Any,
        sample_teams: list[TeamScore],
    ) -> None:
        """Benchmark joining large reports.

        Tests string concatenation performance for large reports.
        Target: <2 ms

        Args:
            benchmark: pytest-benchmark fixture
            sample_teams: List of TeamScore objects
        """

        def build_report() -> str:
            lines = []
            for team in sample_teams:
                lines.append(f"{team.abbrev}: {team.total}")
                for player in team.players:
                    lines.append(f"  {player.full_name}: {player.full_score}")  # noqa: PERF401
            return "\n".join(lines)

        result = benchmark(build_report)
        assert len(result) > 0
