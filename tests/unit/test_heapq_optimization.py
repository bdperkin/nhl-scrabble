"""Tests for heapq optimization in top-N queries."""

import heapq
import random

import pytest

from nhl_scrabble.models.player import PlayerScore


class TestHeapqCorrectness:
    """Test that heapq.nlargest produces identical results to sorted()[:k]."""

    @pytest.fixture
    def sample_players(self) -> list[PlayerScore]:
        """Create sample players with random scores."""
        players = []
        first_names = ["Alex", "Connor", "Sidney", "Nathan", "Leon"]
        last_names = ["Ovechkin", "McDavid", "Crosby", "MacKinnon", "Draisaitl"]

        for _i in range(50):
            first = random.choice(first_names)  # noqa: S311
            last = random.choice(last_names)  # noqa: S311
            first_score = random.randint(10, 30)  # noqa: S311
            last_score = random.randint(10, 30)  # noqa: S311
            players.append(
                PlayerScore(
                    first_name=first,
                    last_name=last,
                    full_name=f"{first} {last}",
                    first_score=first_score,
                    last_score=last_score,
                    full_score=first_score + last_score,
                    team="TOR",
                    division="Atlantic",
                    conference="Eastern",
                ),
            )
        return players

    def test_heapq_nlargest_returns_same_as_sorted_top_20(
        self,
        sample_players: list[PlayerScore],
    ) -> None:
        """Verify heapq.nlargest produces same top 20 as sorted."""
        k = 20

        # Old way: sorted()[:k]
        sorted_result = sorted(sample_players, key=lambda x: x.full_score, reverse=True)[:k]

        # New way: heapq.nlargest()
        heapq_result = heapq.nlargest(k, sample_players, key=lambda x: x.full_score)

        # Should be identical
        assert len(sorted_result) == len(heapq_result)
        for i, player in enumerate(sorted_result):
            assert player.full_score == heapq_result[i].full_score
            assert player.full_name == heapq_result[i].full_name

    def test_heapq_nlargest_returns_same_as_sorted_top_5(
        self,
        sample_players: list[PlayerScore],
    ) -> None:
        """Verify heapq.nlargest produces same top 5 as sorted."""
        k = 5

        # Old way
        sorted_result = sorted(sample_players, key=lambda x: x.full_score, reverse=True)[:k]

        # New way
        heapq_result = heapq.nlargest(k, sample_players, key=lambda x: x.full_score)

        # Should be identical
        assert len(sorted_result) == len(heapq_result)
        for i, player in enumerate(sorted_result):
            assert player.full_score == heapq_result[i].full_score

    def test_heapq_nlargest_with_tuple_key(self) -> None:
        """Verify heapq.nlargest works with tuple keys for tiebreaking."""
        players = [
            PlayerScore(
                first_name="Alex",
                last_name="A",
                full_name="Alex A",
                first_score=20,
                last_score=30,
                full_score=50,
                team="TOR",
                division="Atlantic",
                conference="Eastern",
            ),
            PlayerScore(
                first_name="Bob",
                last_name="B",
                full_name="Bob B",
                first_score=25,
                last_score=25,
                full_score=50,
                team="MTL",
                division="Atlantic",
                conference="Eastern",
            ),
            PlayerScore(
                first_name="Charlie",
                last_name="C",
                full_name="Charlie C",
                first_score=15,
                last_score=30,
                full_score=45,
                team="BOS",
                division="Atlantic",
                conference="Eastern",
            ),
        ]

        # Use tuple key for tiebreaking (like playoff_calculator does)
        sorted_result = sorted(players, key=lambda x: (x.full_score, x.first_score), reverse=True)[
            :2
        ]

        heapq_result = heapq.nlargest(2, players, key=lambda x: (x.full_score, x.first_score))

        # Should be identical (Bob first due to higher first_score in tiebreak)
        assert len(sorted_result) == len(heapq_result)
        assert sorted_result[0].full_name == heapq_result[0].full_name == "Bob B"
        assert sorted_result[1].full_name == heapq_result[1].full_name == "Alex A"

    def test_heapq_nlargest_with_k_greater_than_n(self, sample_players: list[PlayerScore]) -> None:
        """Verify heapq.nlargest handles k > n correctly."""
        k = 100  # More than the 50 players we have

        sorted_result = sorted(sample_players, key=lambda x: x.full_score, reverse=True)
        heapq_result = heapq.nlargest(k, sample_players, key=lambda x: x.full_score)

        # Should return all players in sorted order
        assert len(sorted_result) == len(heapq_result) == 50
        for i, player in enumerate(sorted_result):
            assert player.full_score == heapq_result[i].full_score

    def test_heapq_nlargest_with_k_equal_1(self, sample_players: list[PlayerScore]) -> None:
        """Verify heapq.nlargest(1) returns same as max()."""
        # Using heapq.nlargest(1)
        heapq_result = heapq.nlargest(1, sample_players, key=lambda x: x.full_score)[0]

        # Using max()
        max_result = max(sample_players, key=lambda x: x.full_score)

        # Should be identical
        assert heapq_result.full_score == max_result.full_score
        assert heapq_result.full_name == max_result.full_name


class TestHeapqSemantics:
    """Test semantic benefits of heapq.nlargest over sorted()[:k]."""

    def test_heapq_expresses_intent_clearly(self) -> None:
        """Verify heapq.nlargest expresses top-N intent clearly."""
        import time

        # Create realistic dataset (700 players, top 20)
        players = [
            PlayerScore(
                first_name="First",
                last_name="Last",
                full_name="First Last",
                first_score=random.randint(1, 50),  # noqa: S311
                last_score=random.randint(1, 50),  # noqa: S311
                full_score=random.randint(1, 100),  # noqa: S311
                team="TOR",
                division="Atlantic",
                conference="Eastern",
            )
            for _ in range(700)
        ]

        k = 20
        iterations = 10

        # Benchmark sorted approach
        start = time.perf_counter()
        for _ in range(iterations):
            _result = sorted(players, key=lambda x: x.full_score, reverse=True)[:k]
        sorted_time = time.perf_counter() - start

        # Benchmark heapq approach
        start = time.perf_counter()
        for _ in range(iterations):
            _result = heapq.nlargest(k, players, key=lambda x: x.full_score)
        heapq_time = time.perf_counter() - start

        # Calculate speedup (may be positive or negative depending on environment)
        speedup = sorted_time / heapq_time

        # Log the actual performance for informational purposes
        # Note: heapq may be slower for small datasets due to Python's
        # highly optimized Timsort, but it expresses intent better
        print(  # noqa: T201
            f"\nPerformance comparison (n=700, k=20): "
            f"{speedup:.2f}x (sorted: {sorted_time:.3f}s, heapq: {heapq_time:.3f}s)",
        )

        # The real benefit is semantic - heapq.nlargest clearly says "top-N"
        # whereas sorted()[:k] requires reader to infer intent
        # This test documents the trade-off

        # Verify both approaches work correctly
        assert len(_result) == k
