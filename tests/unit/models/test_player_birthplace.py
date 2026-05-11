"""Unit tests for PlayerScore birthplace fields."""

from nhl_scrabble.models.player import PlayerScore


class TestPlayerScoreBirthplaceFields:
    """Test PlayerScore birthplace-related fields."""

    def test_player_with_full_birthplace_data(self) -> None:
        """Test creating player with all birthplace fields."""
        player = PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
            birthplace="Richmond Hill, ON",
            birth_country="CAN",
            nationality="Canada",
        )

        assert player.birthplace == "Richmond Hill, ON"
        assert player.birth_country == "CAN"
        assert player.nationality == "Canada"

    def test_player_with_default_birthplace(self) -> None:
        """Test creating player without birthplace data (uses defaults)."""
        player = PlayerScore(
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            first_score=10,
            last_score=10,
            full_score=20,
            team="TST",
            division="Test",
            conference="Test",
        )

        assert player.birthplace == ""
        assert player.birth_country == ""
        assert player.nationality == ""

    def test_to_dict_includes_birthplace(self) -> None:
        """Test that to_dict() includes birthplace fields."""
        player = PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
            birthplace="Richmond Hill, ON",
            birth_country="CAN",
            nationality="Canada",
        )

        player_dict = player.to_dict()

        assert "birthplace" in player_dict
        assert "birth_country" in player_dict
        assert "nationality" in player_dict

        assert player_dict["birthplace"] == "Richmond Hill, ON"
        assert player_dict["birth_country"] == "CAN"
        assert player_dict["nationality"] == "Canada"

    def test_repr_still_works(self) -> None:
        """Test that __repr__ still works with new fields."""
        player = PlayerScore(
            player_id=8478402,
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
            birthplace="Richmond Hill, ON",
            birth_country="CAN",
            nationality="Canada",
        )

        repr_str = repr(player)
        assert "Connor McDavid" in repr_str
        assert "8478402" in repr_str
        assert "35" in repr_str
        assert "EDM" in repr_str
