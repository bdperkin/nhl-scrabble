"""Unit tests for PlayerScore birthplace fields and TeamScore model."""

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


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


class TestTeamScore:
    """Test TeamScore model methods."""

    def test_to_dict_with_players(self) -> None:
        """Test to_dict() includes players when include_players=True."""
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
        )

        team = TeamScore(
            abbrev="EDM",
            name="Oilers",
            total=35,
            players=[player],
            division="Pacific",
            conference="Western",
        )

        result = team.to_dict(include_players=True)

        assert "players" in result
        assert len(result["players"]) == 1
        assert result["abbrev"] == "EDM"
        assert result["name"] == "Oilers"
        assert result["total"] == 35
        assert result["division"] == "Pacific"
        assert result["conference"] == "Western"
        assert result["avg_per_player"] == 35.0
        assert result["player_count"] == 1

    def test_to_dict_without_players(self) -> None:
        """Test to_dict() excludes players when include_players=False."""
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
        )

        team = TeamScore(
            abbrev="EDM",
            name="Oilers",
            total=35,
            players=[player],
            division="Pacific",
            conference="Western",
        )

        result = team.to_dict(include_players=False)

        assert "players" not in result
        assert result["abbrev"] == "EDM"
        assert result["player_count"] == 1

    def test_player_count_property(self) -> None:
        """Test player_count property returns correct count."""
        player1 = PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
        )
        player2 = PlayerScore(
            first_name="Leon",
            last_name="Draisaitl",
            full_name="Leon Draisaitl",
            first_score=15,
            last_score=25,
            full_score=40,
            team="EDM",
            division="Pacific",
            conference="Western",
        )

        team = TeamScore(
            abbrev="EDM",
            name="Oilers",
            total=75,
            players=[player1, player2],
            division="Pacific",
            conference="Western",
        )

        assert team.player_count == 2
