"""Benchmark for logging level guard optimization."""

from __future__ import annotations

import logging
import time

import pytest

from nhl_scrabble.models.player import PlayerScore


@pytest.mark.benchmark(group="logging-guards")
def test_benchmark_without_guard(benchmark: pytest.fixture) -> None:
    """Benchmark expensive logging without guard."""
    logger = logging.getLogger("benchmark_test")
    logger.setLevel(logging.INFO)  # DEBUG disabled

    # Create test data
    players = [
        PlayerScore(
            first_name=f"Test{i}",
            last_name=f"Player{i}",
            full_name=f"Test{i} Player{i}",
            first_score=4,
            last_score=5,
            full_score=9,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        )
        for i in range(100)
    ]

    def log_without_guard() -> None:
        # This always computes sum even though DEBUG is disabled
        logger.debug(f"Total: {sum(p.full_score for p in players)}")

    result = benchmark(log_without_guard)
    assert result is None


@pytest.mark.benchmark(group="logging-guards")
def test_benchmark_with_guard(benchmark: pytest.fixture) -> None:
    """Benchmark expensive logging with guard."""
    logger = logging.getLogger("benchmark_test")
    logger.setLevel(logging.INFO)  # DEBUG disabled

    # Create test data
    players = [
        PlayerScore(
            first_name=f"Test{i}",
            last_name=f"Player{i}",
            full_name=f"Test{i} Player{i}",
            first_score=4,
            last_score=5,
            full_score=9,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        )
        for i in range(100)
    ]

    def log_with_guard() -> None:
        # This skips sum when DEBUG is disabled
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Total: {sum(p.full_score for p in players)}")

    result = benchmark(log_with_guard)
    assert result is None


def test_simple_performance_comparison() -> None:
    """Simple performance comparison to show improvement."""
    logger = logging.getLogger("test_perf")
    logger.setLevel(logging.INFO)  # DEBUG disabled

    # Create test data with 1000 players
    players = [
        PlayerScore(
            first_name=f"Test{i}",
            last_name=f"Player{i}",
            full_name=f"Test{i} Player{i}",
            first_score=4,
            last_score=5,
            full_score=9,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        )
        for i in range(1000)
    ]

    # Test without guard (sum always executes)
    iterations = 1000
    start = time.perf_counter()
    for _ in range(iterations):
        # This always computes sum even though DEBUG is disabled
        logger.debug(f"Total: {sum(p.full_score for p in players)}")
    time_without_guard = time.perf_counter() - start

    # Test with guard (sum is skipped)
    start = time.perf_counter()
    for _ in range(iterations):
        # This skips sum when DEBUG is disabled
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Total: {sum(p.full_score for p in players)}")
    time_with_guard = time.perf_counter() - start

    # Calculate speedup
    speedup = time_without_guard / time_with_guard if time_with_guard > 0 else float("inf")

    # Log results for manual testing (not displayed in pytest)
    import sys

    sys.stderr.write("\nPerformance Comparison (1000 iterations, 1000 players):\n")
    sys.stderr.write(f"  Without guard: {time_without_guard:.4f}s\n")
    sys.stderr.write(f"  With guard:    {time_with_guard:.4f}s\n")
    sys.stderr.write(f"  Speedup:       {speedup:.2f}x\n")

    # Guard version should be significantly faster
    assert time_with_guard < time_without_guard


if __name__ == "__main__":
    # Run simple performance comparison
    test_simple_performance_comparison()
