"""Unit tests for Scrabble scoring module."""

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
