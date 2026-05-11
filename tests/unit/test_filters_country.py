"""Unit tests for AnalysisFilters country filtering."""

import pytest

from nhl_scrabble.filters import AnalysisFilters, filter_players
from nhl_scrabble.models.player import PlayerScore


@pytest.fixture
def sample_players_with_countries() -> list[PlayerScore]:
    """Create sample players with different nationalities."""
    return [
        PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=20,
            last_score=15,
            full_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
            birth_country="CAN",
            nationality="Canada",
        ),
        PlayerScore(
            first_name="Leon",
            last_name="Draisaitl",
            full_name="Leon Draisaitl",
            first_score=18,
            last_score=24,
            full_score=42,
            team="EDM",
            division="Pacific",
            conference="Western",
            birth_country="DEU",
            nationality="Germany",
        ),
        PlayerScore(
            first_name="Auston",
            last_name="Matthews",
            full_name="Auston Matthews",
            first_score=18,
            last_score=22,
            full_score=40,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
            birth_country="USA",
            nationality="United States",
        ),
        PlayerScore(
            first_name="Mitch",
            last_name="Marner",
            full_name="Mitch Marner",
            first_score=15,
            last_score=18,
            full_score=33,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
            birth_country="CAN",
            nationality="Canada",
        ),
    ]


class TestAnalysisFiltersCountries:
    """Test AnalysisFilters with country filtering."""

    def test_from_options_with_countries(self) -> None:
        """Test creating filters with countries option."""
        filters = AnalysisFilters.from_options(countries="CAN,USA")

        assert filters.countries is not None
        assert "CAN" in filters.countries
        assert "USA" in filters.countries
        assert len(filters.countries) == 2

    def test_from_options_countries_uppercase(self) -> None:
        """Test that country codes are converted to uppercase."""
        filters = AnalysisFilters.from_options(countries="can,usa")

        assert "CAN" in filters.countries
        assert "USA" in filters.countries

    def test_from_options_countries_strips_whitespace(self) -> None:
        """Test that whitespace is stripped from country codes."""
        filters = AnalysisFilters.from_options(countries=" CAN , USA , SWE ")

        assert filters.countries is not None
        assert len(filters.countries) == 3
        assert "CAN" in filters.countries
        assert "USA" in filters.countries
        assert "SWE" in filters.countries

    def test_from_options_no_countries(self) -> None:
        """Test creating filters without countries."""
        filters = AnalysisFilters.from_options()

        assert filters.countries is None

    def test_is_active_with_countries(self) -> None:
        """Test that filters with countries are considered active."""
        filters = AnalysisFilters(countries=frozenset(["CAN"]))

        assert filters.is_active() is True

    def test_should_include_player_country_match(
        self,
        sample_players_with_countries: list[PlayerScore],
    ) -> None:
        """Test that player with matching country is included."""
        filters = AnalysisFilters(countries=frozenset(["CAN"]))
        canadian_player = sample_players_with_countries[0]  # Connor McDavid

        assert filters.should_include_player(canadian_player) is True

    def test_should_include_player_country_no_match(
        self,
        sample_players_with_countries: list[PlayerScore],
    ) -> None:
        """Test that player without matching country is excluded."""
        filters = AnalysisFilters(countries=frozenset(["CAN"]))
        german_player = sample_players_with_countries[1]  # Leon Draisaitl

        assert filters.should_include_player(german_player) is False

    def test_filter_players_by_country(
        self,
        sample_players_with_countries: list[PlayerScore],
    ) -> None:
        """Test filtering players by country."""
        filters = AnalysisFilters.from_options(countries="CAN")
        filtered = filter_players(sample_players_with_countries, filters)

        assert len(filtered) == 2
        assert all(p.birth_country == "CAN" for p in filtered)
        assert {p.full_name for p in filtered} == {"Connor McDavid", "Mitch Marner"}

    def test_filter_players_multiple_countries(
        self,
        sample_players_with_countries: list[PlayerScore],
    ) -> None:
        """Test filtering players by multiple countries."""
        filters = AnalysisFilters.from_options(countries="CAN,USA")
        filtered = filter_players(sample_players_with_countries, filters)

        assert len(filtered) == 3
        countries = {p.birth_country for p in filtered}
        assert countries == {"CAN", "USA"}

    def test_filter_players_country_with_other_filters(
        self,
        sample_players_with_countries: list[PlayerScore],
    ) -> None:
        """Test combining country filter with other filters."""
        # Filter Canadian players with min score 35
        filters = AnalysisFilters.from_options(countries="CAN", min_score=35)
        filtered = filter_players(sample_players_with_countries, filters)

        # Should only get Connor McDavid (CAN, score=35)
        # Mitch Marner is CAN but score=33
        assert len(filtered) == 1
        assert filtered[0].full_name == "Connor McDavid"

    def test_filter_players_country_and_team(
        self,
        sample_players_with_countries: list[PlayerScore],
    ) -> None:
        """Test combining country and team filters."""
        # Filter Canadian players on TOR
        filters = AnalysisFilters.from_options(countries="CAN", teams="TOR")
        filtered = filter_players(sample_players_with_countries, filters)

        # Should only get Mitch Marner
        assert len(filtered) == 1
        assert filtered[0].full_name == "Mitch Marner"
