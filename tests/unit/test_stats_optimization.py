"""Tests for stats report single-pass optimization."""

from __future__ import annotations

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.reports.stats_report import StatsReporter


@pytest.fixture
def sample_players() -> list[PlayerScore]:
    """Create sample players for testing."""
    return [
        PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=15,
            last_score=17,
            full_score=32,
            team="EDM",
            division="Pacific",
            conference="Western",
        ),
        PlayerScore(
            first_name="Auston",
            last_name="Matthews",
            full_name="Auston Matthews",
            first_score=18,
            last_score=20,
            full_score=38,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Nathan",
            last_name="MacKinnon",
            full_name="Nathan MacKinnon",
            first_score=16,
            last_score=25,
            full_score=41,
            team="COL",
            division="Central",
            conference="Western",
        ),
    ]


def test_single_pass_stats_calculation(sample_players: list[PlayerScore]) -> None:
    """Verify single-pass statistics are correct."""
    reporter = StatsReporter()

    # Calculate stats with optimized method
    stats = reporter._calculate_player_statistics(sample_players)  # noqa: SLF001

    # Verify maximums
    top_first_score = max(p.first_score for p in sample_players)
    assert stats["top_first"].first_score == top_first_score

    top_last_score = max(p.last_score for p in sample_players)
    assert stats["top_last"].last_score == top_last_score

    # Verify averages
    expected_avg_full = sum(p.full_score for p in sample_players) / len(sample_players)
    assert abs(stats["avg_full"] - expected_avg_full) < 0.01

    expected_avg_first = sum(p.first_score for p in sample_players) / len(sample_players)
    assert abs(stats["avg_first"] - expected_avg_first) < 0.01

    expected_avg_last = sum(p.last_score for p in sample_players) / len(sample_players)
    assert abs(stats["avg_last"] - expected_avg_last) < 0.01

    # Verify total players count
    assert stats["total_players"] == len(sample_players)


def test_stats_calculation_empty_list() -> None:
    """Verify handling of empty player list."""
    reporter = StatsReporter()
    stats = reporter._calculate_player_statistics([])  # noqa: SLF001

    assert stats["top_first"] is None
    assert stats["top_last"] is None
    assert stats["avg_full"] == 0.0
    assert stats["avg_first"] == 0.0
    assert stats["avg_last"] == 0.0
    assert stats["total_players"] == 0


def test_stats_calculation_single_player() -> None:
    """Verify handling of single player."""
    player = PlayerScore(
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

    reporter = StatsReporter()
    stats = reporter._calculate_player_statistics([player])  # noqa: SLF001

    assert stats["top_first"] == player
    assert stats["top_last"] == player
    assert stats["avg_full"] == 32.0
    assert stats["avg_first"] == 15.0
    assert stats["avg_last"] == 17.0
    assert stats["total_players"] == 1


def test_stats_identifies_correct_top_players(sample_players: list[PlayerScore]) -> None:
    """Verify correct players are identified as having highest scores."""
    reporter = StatsReporter()
    stats = reporter._calculate_player_statistics(sample_players)  # noqa: SLF001

    # Auston Matthews has highest first name score (18)
    assert stats["top_first"].first_name == "Auston"
    assert stats["top_first"].first_score == 18

    # Nathan MacKinnon has highest last name score (25)
    assert stats["top_last"].last_name == "MacKinnon"
    assert stats["top_last"].last_score == 25


def test_stats_calculation_with_ties() -> None:
    """Verify handling when multiple players tie for max score."""
    players = [
        PlayerScore(
            first_name="Test1",
            last_name="Player1",
            full_name="Test1 Player1",
            first_score=20,
            last_score=15,
            full_score=35,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Test2",
            last_name="Player2",
            full_name="Test2 Player2",
            first_score=20,
            last_score=15,
            full_score=35,
            team="MTL",
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    reporter = StatsReporter()
    stats = reporter._calculate_player_statistics(players)  # noqa: SLF001

    # Should pick first one encountered
    assert stats["top_first"].first_score == 20
    assert stats["top_last"].last_score == 15

    # Averages should still be correct
    assert stats["avg_full"] == 35.0
    assert stats["avg_first"] == 20.0
    assert stats["avg_last"] == 15.0


def test_stats_calculation_return_keys() -> None:
    """Verify all expected keys are in returned dictionary."""
    player = PlayerScore(
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

    reporter = StatsReporter()
    stats = reporter._calculate_player_statistics([player])  # noqa: SLF001

    expected_keys = {
        "top_first",
        "top_last",
        "avg_full",
        "avg_first",
        "avg_last",
        "total_players",
    }
    assert set(stats.keys()) == expected_keys
