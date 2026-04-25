"""Unit tests for Scrabble scoring module."""

import pytest

from nhl_scrabble.scoring.scrabble import ScrabbleScorer


class TestScrabbleScorer:
    """Tests for the ScrabbleScorer class."""

    def test_calculate_score_basic(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test basic score calculation."""
        assert scrabble_scorer.calculate_score("A") == 1
        assert scrabble_scorer.calculate_score("Z") == 10
        assert scrabble_scorer.calculate_score("Q") == 10

    def test_calculate_score_word(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test score calculation for words."""
        # ALEX = A(1) + L(1) + E(1) + X(8) = 11
        assert scrabble_scorer.calculate_score("ALEX") == 11

    def test_calculate_score_case_insensitive(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test that scoring is case insensitive."""
        assert scrabble_scorer.calculate_score("alex") == scrabble_scorer.calculate_score("ALEX")
        assert scrabble_scorer.calculate_score("Alex") == scrabble_scorer.calculate_score("ALEX")

    def test_calculate_score_with_spaces(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test score calculation with spaces (spaces should be worth 0)."""
        # "ALEX SMITH" = ALEX(11) + SMITH(10) = 21
        assert scrabble_scorer.calculate_score("ALEX SMITH") == 21

    def test_calculate_score_empty_string(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test score calculation for empty string."""
        assert scrabble_scorer.calculate_score("") == 0

    def test_calculate_score_special_characters(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test that special characters are worth 0 points."""
        assert scrabble_scorer.calculate_score("O'BRIEN") == scrabble_scorer.calculate_score(
            "OBRIEN"
        )
        assert scrabble_scorer.calculate_score("ALEX-123") == scrabble_scorer.calculate_score(
            "ALEX"
        )

    def test_score_player(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test scoring a player from API data format."""
        player_data = {"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}

        result = scrabble_scorer.score_player(player_data, "EDM", "Pacific", "Western")

        assert result.first_name == "Connor"
        assert result.last_name == "McDavid"
        assert result.full_name == "Connor McDavid"
        assert result.team == "EDM"
        assert result.division == "Pacific"
        assert result.conference == "Western"
        assert result.first_score > 0
        assert result.last_score > 0
        assert result.full_score == result.first_score + result.last_score

    def test_letter_values_complete(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test that all 26 letters have values."""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letter in alphabet:
            assert letter in scrabble_scorer.LETTER_VALUES
            assert scrabble_scorer.LETTER_VALUES[letter] > 0


class TestScrabbleScorerCaching:
    """Tests for ScrabbleScorer caching functionality."""

    @pytest.fixture(autouse=True)
    def clear_cache_before_test(self) -> None:
        """Clear cache before each test to ensure isolation."""
        ScrabbleScorer.clear_cache()

    def test_cache_basic_behavior(self) -> None:
        """Test that cache stores and retrieves scores correctly."""
        # Clear cache and verify empty
        ScrabbleScorer.clear_cache()
        stats = ScrabbleScorer.get_cache_info()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["currsize"] == 0

        # First call should be a miss
        score1 = ScrabbleScorer.calculate_score("McDavid")
        stats = ScrabbleScorer.get_cache_info()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
        assert stats["currsize"] == 1

        # Second call should be a hit
        score2 = ScrabbleScorer.calculate_score("McDavid")
        stats = ScrabbleScorer.get_cache_info()
        assert stats["misses"] == 1
        assert stats["hits"] == 1
        assert stats["currsize"] == 1

        # Scores should be identical
        assert score1 == score2

    def test_cache_different_names(self) -> None:
        """Test that different names are cached separately."""
        ScrabbleScorer.clear_cache()

        # Calculate scores for different names
        score1 = ScrabbleScorer.calculate_score("Connor")
        score2 = ScrabbleScorer.calculate_score("McDavid")
        score3 = ScrabbleScorer.calculate_score("Connor")  # Should hit cache

        stats = ScrabbleScorer.get_cache_info()
        assert stats["misses"] == 2  # Connor, McDavid
        assert stats["hits"] == 1  # Second Connor
        assert stats["currsize"] == 2  # Two unique names cached

        assert score1 != score2
        assert score1 == score3

    def test_cache_case_sensitivity(self) -> None:
        """Test that cache respects case differences in input."""
        ScrabbleScorer.clear_cache()

        # Different case = different cache keys
        score_lower = ScrabbleScorer.calculate_score("mcdavid")
        score_upper = ScrabbleScorer.calculate_score("MCDAVID")
        score_mixed = ScrabbleScorer.calculate_score("McDavid")

        stats = ScrabbleScorer.get_cache_info()
        assert stats["currsize"] == 3  # Three cache entries

        # But scores should be the same (case-insensitive scoring)
        assert score_lower == score_upper == score_mixed

    def test_get_cache_info(self) -> None:
        """Test cache info retrieval."""
        ScrabbleScorer.clear_cache()

        info = ScrabbleScorer.get_cache_info()
        assert "hits" in info
        assert "misses" in info
        assert "maxsize" in info
        assert "currsize" in info
        assert info["maxsize"] == 2048
        assert info["currsize"] == 0

        # Add some entries
        ScrabbleScorer.calculate_score("Test1")
        ScrabbleScorer.calculate_score("Test2")
        ScrabbleScorer.calculate_score("Test1")

        info = ScrabbleScorer.get_cache_info()
        assert info["hits"] == 1
        assert info["misses"] == 2
        assert info["currsize"] == 2

    def test_cache_clear(self) -> None:
        """Test cache clearing functionality."""
        # Populate cache
        for i in range(10):
            ScrabbleScorer.calculate_score(f"Player{i}")

        stats = ScrabbleScorer.get_cache_info()
        assert stats["currsize"] == 10

        # Clear cache
        ScrabbleScorer.clear_cache()

        stats = ScrabbleScorer.get_cache_info()
        assert stats["currsize"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_cache_with_duplicates(self) -> None:
        """Test cache performance with many duplicate names."""
        ScrabbleScorer.clear_cache()

        # Common NHL first names
        common_names = ["Alex", "Connor", "John", "Ryan", "Matt"]

        # Simulate scoring many players with duplicate first names
        for _ in range(10):  # 10 iterations
            for name in common_names:
                ScrabbleScorer.calculate_score(name)

        stats = ScrabbleScorer.get_cache_info()
        assert stats["currsize"] == 5  # Only 5 unique names
        assert stats["misses"] == 5  # First occurrence of each
        assert stats["hits"] == 45  # 9 more iterations x 5 names

        # Hit rate should be 90%
        hit_rate = stats["hits"] / (stats["hits"] + stats["misses"])
        assert hit_rate == 0.9

    def test_cache_maxsize(self) -> None:
        """Test cache maxsize configuration."""
        info = ScrabbleScorer.get_cache_info()
        assert info["maxsize"] == 2048

    def test_log_cache_stats(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test cache statistics logging."""
        ScrabbleScorer.clear_cache()

        # Add some cache activity
        ScrabbleScorer.calculate_score("Test1")
        ScrabbleScorer.calculate_score("Test2")
        ScrabbleScorer.calculate_score("Test1")

        # Log stats
        with caplog.at_level("DEBUG"):
            ScrabbleScorer.log_cache_stats()

        # Verify log message
        assert "Scrabble scoring cache stats:" in caplog.text
        assert "hits=1" in caplog.text
        assert "misses=2" in caplog.text
        assert "hit_rate=" in caplog.text

    def test_log_cache_stats_empty(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test logging stats when cache is empty."""
        ScrabbleScorer.clear_cache()

        with caplog.at_level("DEBUG"):
            ScrabbleScorer.log_cache_stats()

        assert "No calls yet" in caplog.text

    def test_performance_improvement(self) -> None:
        """Test that caching correctly handles repeated calls.

        Note: Performance benchmarking is done in tests/benchmarks/.
        This test validates functional correctness of cache behavior.
        """
        ScrabbleScorer.clear_cache()

        test_name = "Constantine"

        # Make cached calls (1 miss + 999 hits)
        for _ in range(1000):
            ScrabbleScorer.calculate_score(test_name)

        # Verify cache hits
        stats_after_cached = ScrabbleScorer.get_cache_info()
        assert stats_after_cached["hits"] == 999  # Second through thousandth calls
        assert stats_after_cached["misses"] == 1  # First call only

        # Make uncached calls (1000 misses)
        ScrabbleScorer.clear_cache()
        for i in range(1000):
            ScrabbleScorer.calculate_score(f"{test_name}{i}")

        # Verify all were misses
        stats_after_uncached = ScrabbleScorer.get_cache_info()
        assert stats_after_uncached["hits"] == 0
        assert stats_after_uncached["misses"] == 1000

    def test_cache_integration_with_score_player(self) -> None:
        """Test that cache works correctly with score_player method."""
        ScrabbleScorer.clear_cache()
        scorer = ScrabbleScorer()

        # Score multiple players with duplicate first/last names
        player1 = {"firstName": {"default": "Alex"}, "lastName": {"default": "Smith"}}
        player2 = {"firstName": {"default": "Alex"}, "lastName": {"default": "Johnson"}}
        player3 = {"firstName": {"default": "John"}, "lastName": {"default": "Smith"}}

        scorer.score_player(player1, "TOR", "Atlantic", "Eastern")
        scorer.score_player(player2, "MTL", "Atlantic", "Eastern")
        scorer.score_player(player3, "BOS", "Atlantic", "Eastern")

        stats = ScrabbleScorer.get_cache_info()
        # Should have cached: "Alex", "Smith", "Johnson", "John"
        assert stats["currsize"] == 4
        # Alex: miss, Smith: miss, Alex: hit, Johnson: miss, John: miss, Smith: hit
        assert stats["hits"] == 2
        assert stats["misses"] == 4
