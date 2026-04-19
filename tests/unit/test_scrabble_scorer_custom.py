"""Tests for ScrabbleScorer with custom scoring values."""

from __future__ import annotations

from nhl_scrabble.scoring.scrabble import ScrabbleScorer


class TestScrabbleScorerCustomValues:
    """Tests for ScrabbleScorer with custom letter values."""

    def test_scorer_default_values(self) -> None:
        """Test scorer with default Scrabble values using static method."""
        # Use static method for default scoring
        assert ScrabbleScorer.calculate_score("A") == 1
        assert ScrabbleScorer.calculate_score("Q") == 10
        assert ScrabbleScorer.calculate_score("Z") == 10
        assert ScrabbleScorer.calculate_score("ALEX") == 11  # A(1) + L(1) + E(1) + X(8)

    def test_scorer_uniform_values(self) -> None:
        """Test scorer with uniform values (all letters = 1)."""
        uniform_values = {chr(i): 1 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=uniform_values)

        assert scorer.calculate_score_custom("A") == 1
        assert scorer.calculate_score_custom("Q") == 1  # Different from default!
        assert scorer.calculate_score_custom("Z") == 1
        assert scorer.calculate_score_custom("ALEX") == 4  # All letters worth 1

    def test_scorer_custom_values(self) -> None:
        """Test scorer with completely custom values."""
        custom_values = {chr(i): i - 64 for i in range(65, 91)}  # A=1, B=2, ..., Z=26
        scorer = ScrabbleScorer(letter_values=custom_values)

        assert scorer.calculate_score_custom("A") == 1
        assert scorer.calculate_score_custom("Z") == 26
        assert scorer.calculate_score_custom("B") == 2
        assert scorer.calculate_score_custom("ABC") == 6  # A(1) + B(2) + C(3)

    def test_scorer_wordle_values(self) -> None:
        """Test scorer with Wordle-inspired values."""
        wordle_values = {
            # Common letters (1 point)
            **dict.fromkeys("EARIOTNS", 1),
            # Uncommon letters (2 points)
            **dict.fromkeys("LCUDPMHGBFYWKV", 2),
            # Rare letters (3 points)
            **dict.fromkeys("XZJQ", 3),
        }
        scorer = ScrabbleScorer(letter_values=wordle_values)

        assert scorer.calculate_score_custom("E") == 1  # Common
        assert scorer.calculate_score_custom("X") == 3  # Rare
        assert scorer.calculate_score_custom("QUIZ") == 9  # Q(3) + U(2) + I(1) + Z(3)

    def test_scorer_zero_values(self) -> None:
        """Test scorer with some zero values."""
        zero_values = {chr(i): 0 if i < 75 else 1 for i in range(65, 91)}  # A-J=0, K-Z=1
        scorer = ScrabbleScorer(letter_values=zero_values)

        assert scorer.calculate_score_custom("ALEX") == 2  # A(0) + L(1) + E(0) + X(1)
        assert scorer.calculate_score_custom("ABC") == 0  # All zero

    def test_scorer_case_insensitive(self) -> None:
        """Test that custom scoring is case-insensitive."""
        custom_values = {chr(i): 5 for i in range(65, 91)}  # All worth 5
        scorer = ScrabbleScorer(letter_values=custom_values)

        assert scorer.calculate_score_custom("ALEX") == 20
        assert scorer.calculate_score_custom("alex") == 20
        assert scorer.calculate_score_custom("Alex") == 20

    def test_scorer_ignores_non_letters(self) -> None:
        """Test that non-letter characters are ignored with custom values."""
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=custom_values)

        assert scorer.calculate_score_custom("A-B") == 2  # Hyphen ignored
        assert scorer.calculate_score_custom("O'Brien") == 6  # Apostrophe ignored
        assert scorer.calculate_score_custom("123") == 0  # Numbers ignored

    def test_scorer_with_spaces(self) -> None:
        """Test scoring names with spaces using custom values."""
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=custom_values)

        assert scorer.calculate_score_custom("Connor McDavid") == 13  # All letters worth 1

    def test_scorer_cache_with_custom_values(self) -> None:
        """Test that caching works with custom values."""
        custom_values = {chr(i): 2 for i in range(65, 91)}  # All worth 2
        scorer = ScrabbleScorer(letter_values=custom_values)

        # First call
        score1 = scorer.calculate_score_custom("ALEX")
        # Second call should hit cache
        score2 = scorer.calculate_score_custom("ALEX")

        assert score1 == score2 == 8  # 4 letters * 2

    def test_scorer_different_instances_different_values(self) -> None:
        """Test that different scorer instances can have different values."""
        scorer2 = ScrabbleScorer(letter_values={chr(i): 1 for i in range(65, 91)})  # Uniform

        # Same name, different scores
        assert ScrabbleScorer.calculate_score("ALEX") == 11  # Scrabble (static)
        assert scorer2.calculate_score_custom("ALEX") == 4  # Uniform (instance)

    def test_score_player_with_custom_values(self) -> None:
        """Test score_player method with custom values."""
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=custom_values)

        player_data = {
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
        }

        result = scorer.score_player(player_data, "EDM", "Pacific", "Western")

        assert result.first_name == "Connor"
        assert result.last_name == "McDavid"
        assert result.first_score == 6  # 6 letters
        assert result.last_score == 7  # 7 letters
        assert result.full_score == 13  # 6 + 7

    def test_scorer_empty_string(self) -> None:
        """Test scoring empty string with custom values."""
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=custom_values)

        assert scorer.calculate_score_custom("") == 0

    def test_scorer_cache_info_works(self) -> None:
        """Test that cache info methods work with custom values."""
        custom_values = {chr(i): 1 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=custom_values)

        # Clear cache first
        ScrabbleScorer.clear_cache()

        # Make some calls
        scorer.calculate_score_custom("ALEX")
        scorer.calculate_score_custom("ALEX")  # Should hit cache
        scorer.calculate_score_custom("BOB")

        info = ScrabbleScorer.get_cache_info()
        assert info["hits"] >= 1  # At least one cache hit
        assert info["misses"] >= 2  # At least two cache misses

    def test_scorer_high_values(self) -> None:
        """Test scorer with very high point values."""
        high_values = {chr(i): 100 for i in range(65, 91)}
        scorer = ScrabbleScorer(letter_values=high_values)

        assert scorer.calculate_score_custom("A") == 100
        assert scorer.calculate_score_custom("ALEX") == 400


class TestScrabbleScorerBackwardsCompatibility:
    """Tests to ensure backwards compatibility with existing code."""

    def test_default_scorer_unchanged(self) -> None:
        """Test that default scorer behavior is unchanged (using static method)."""
        # Static method should work exactly as before
        assert ScrabbleScorer.calculate_score("ALEX") == 11
        assert ScrabbleScorer.calculate_score("Ovechkin") == 20
        assert ScrabbleScorer.calculate_score("A") == 1
        assert ScrabbleScorer.calculate_score("Q") == 10
        assert ScrabbleScorer.calculate_score("Z") == 10

    def test_class_variable_unchanged(self) -> None:
        """Test that class variable LETTER_VALUES is unchanged."""
        assert ScrabbleScorer.LETTER_VALUES["A"] == 1
        assert ScrabbleScorer.LETTER_VALUES["Q"] == 10
        assert ScrabbleScorer.LETTER_VALUES["Z"] == 10
        assert len(ScrabbleScorer.LETTER_VALUES) == 26

    def test_cache_methods_unchanged(self) -> None:
        """Test that cache methods still work."""
        ScrabbleScorer.clear_cache()
        info = ScrabbleScorer.get_cache_info()
        assert "hits" in info
        assert "misses" in info
        assert "maxsize" in info
        assert "currsize" in info

    def test_score_player_unchanged(self) -> None:
        """Test that score_player method works as before."""
        scorer = ScrabbleScorer()

        player_data = {
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
        }

        result = scorer.score_player(player_data, "EDM", "Pacific", "Western")

        assert result.full_score == 24
