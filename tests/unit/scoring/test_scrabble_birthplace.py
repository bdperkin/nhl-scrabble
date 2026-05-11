"""Unit tests for ScrabbleScorer birthplace extraction."""

from nhl_scrabble.scoring.scrabble import ScrabbleScorer


class TestScorerBirthplaceExtraction:
    """Test that scorer correctly extracts birthplace data."""

    def test_score_player_with_full_birthplace(self) -> None:
        """Test scoring player with complete birthplace data."""
        scorer = ScrabbleScorer()

        player_data = {
            "id": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthCity": {"default": "Richmond Hill"},
            "birthStateProvince": {"default": "ON"},
            "birthCountry": "CAN",
        }

        player_score = scorer.score_player(
            player_data,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        assert player_score.birthplace == "Richmond Hill, ON"
        assert player_score.birth_country == "CAN"
        assert player_score.nationality == "Canada"

    def test_score_player_city_only(self) -> None:
        """Test scoring player with city but no state/province."""
        scorer = ScrabbleScorer()

        player_data = {
            "id": 8477934,
            "firstName": {"default": "Leon"},
            "lastName": {"default": "Draisaitl"},
            "birthCity": {"default": "Cologne"},
            "birthStateProvince": {"default": ""},
            "birthCountry": "DEU",
        }

        player_score = scorer.score_player(
            player_data,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        assert player_score.birthplace == "Cologne"
        assert player_score.birth_country == "DEU"
        assert player_score.nationality == "Germany"

    def test_score_player_no_birthplace(self) -> None:
        """Test scoring player with missing birthplace data."""
        scorer = ScrabbleScorer()

        player_data = {
            "id": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
        }

        player_score = scorer.score_player(
            player_data,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        assert player_score.birthplace == ""
        assert player_score.birth_country == ""
        assert player_score.nationality == ""

    def test_score_player_string_birth_city(self) -> None:
        """Test scoring player with birthCity as string instead of dict."""
        scorer = ScrabbleScorer()

        player_data = {
            "id": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthCity": "Richmond Hill",  # String instead of dict
            "birthStateProvince": "ON",  # String instead of dict
            "birthCountry": "CAN",
        }

        player_score = scorer.score_player(
            player_data,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        assert player_score.birthplace == "Richmond Hill, ON"
        assert player_score.birth_country == "CAN"
        assert player_score.nationality == "Canada"

    def test_score_player_unknown_country(self) -> None:
        """Test scoring player with unknown country code."""
        scorer = ScrabbleScorer()

        player_data = {
            "id": 8478402,
            "firstName": {"default": "Test"},
            "lastName": {"default": "Player"},
            "birthCity": {"default": "Test City"},
            "birthStateProvince": {"default": "TS"},
            "birthCountry": "XXX",  # Unknown country code
        }

        player_score = scorer.score_player(
            player_data,
            team="TST",
            division="Test",
            conference="Test",
        )

        assert player_score.birthplace == "Test City, TS"
        assert player_score.birth_country == "XXX"
        # Unknown code returns the code itself
        assert player_score.nationality == "XXX"

    def test_score_player_maintains_scoring(self) -> None:
        """Test that adding birthplace fields doesn't break scoring."""
        scorer = ScrabbleScorer()

        player_data = {
            "id": 8478402,
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
            "birthCity": {"default": "Richmond Hill"},
            "birthStateProvince": {"default": "ON"},
            "birthCountry": "CAN",
        }

        player_score = scorer.score_player(
            player_data,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        # Verify scoring still works correctly
        assert player_score.first_name == "Connor"
        assert player_score.last_name == "McDavid"
        assert player_score.full_name == "Connor McDavid"
        assert player_score.full_score == player_score.first_score + player_score.last_score
        assert player_score.full_score > 0
