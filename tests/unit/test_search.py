"""Unit tests for player search functionality."""

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.search import PlayerSearch


@pytest.fixture
def sample_players() -> list[PlayerScore]:
    """Return a list of sample players for testing."""
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
            first_score=14,
            last_score=19,
            full_score=33,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Connor",
            last_name="Bedard",
            full_name="Connor Bedard",
            first_score=15,
            last_score=12,
            full_score=27,
            team="CHI",
            division="Central",
            conference="Western",
        ),
        PlayerScore(
            first_name="Alex",
            last_name="Ovechkin",
            full_name="Alex Ovechkin",
            first_score=8,
            last_score=23,
            full_score=31,
            team="WSH",
            division="Metropolitan",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Sidney",
            last_name="Crosby",
            full_name="Sidney Crosby",
            first_score=16,
            last_score=15,
            full_score=31,
            team="PIT",
            division="Metropolitan",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Nathan",
            last_name="MacKinnon",
            full_name="Nathan MacKinnon",
            first_score=14,
            last_score=20,
            full_score=34,
            team="COL",
            division="Central",
            conference="Western",
        ),
    ]


@pytest.fixture
def searcher(sample_players: list[PlayerScore]) -> PlayerSearch:
    """Return a PlayerSearch instance with sample data."""
    return PlayerSearch(sample_players)


class TestPlayerSearchInit:
    """Tests for PlayerSearch initialization."""

    def test_init_with_players(self, sample_players: list[PlayerScore]) -> None:
        """Test initialization with player list."""
        searcher = PlayerSearch(sample_players)
        assert searcher.players == sample_players
        assert len(searcher.players) == 6

    def test_init_with_empty_list(self) -> None:
        """Test initialization with empty player list."""
        searcher = PlayerSearch([])
        assert searcher.players == []
        assert len(searcher.players) == 0


class TestPlayerSearchExactSearch:
    """Tests for exact substring search."""

    def test_exact_search_full_name(self, searcher: PlayerSearch) -> None:
        """Test exact search with full name."""
        results = searcher.search("Connor McDavid")
        assert len(results) == 1
        assert results[0].full_name == "Connor McDavid"

    def test_exact_search_partial_name(self, searcher: PlayerSearch) -> None:
        """Test exact search with partial name."""
        results = searcher.search("Connor")
        assert len(results) == 2
        assert all("Connor" in p.full_name for p in results)

    def test_exact_search_last_name(self, searcher: PlayerSearch) -> None:
        """Test exact search with last name only."""
        results = searcher.search("McDavid")
        assert len(results) == 1
        assert results[0].full_name == "Connor McDavid"

    def test_exact_search_case_insensitive(self, searcher: PlayerSearch) -> None:
        """Test that exact search is case insensitive."""
        results_lower = searcher.search("mcdavid")
        results_upper = searcher.search("MCDAVID")
        results_mixed = searcher.search("McDavid")

        assert len(results_lower) == len(results_upper) == len(results_mixed) == 1
        assert results_lower[0].full_name == results_upper[0].full_name

    def test_exact_search_no_matches(self, searcher: PlayerSearch) -> None:
        """Test exact search with no matches."""
        results = searcher.search("Gretzky")
        assert len(results) == 0

    def test_exact_search_empty_query(self, searcher: PlayerSearch) -> None:
        """Test exact search with empty query returns all players."""
        results = searcher.search("")
        assert len(results) == 6


class TestPlayerSearchWildcardSearch:
    """Tests for wildcard search."""

    def test_wildcard_search_prefix(self, searcher: PlayerSearch) -> None:
        """Test wildcard search with prefix pattern."""
        results = searcher.search("Connor*")
        assert len(results) == 2
        assert all(p.first_name == "Connor" for p in results)

    def test_wildcard_search_suffix(self, searcher: PlayerSearch) -> None:
        """Test wildcard search with suffix pattern."""
        results = searcher.search("*Ovechkin")
        assert len(results) == 1
        assert results[0].last_name == "Ovechkin"

    def test_wildcard_search_middle(self, searcher: PlayerSearch) -> None:
        """Test wildcard search with middle pattern."""
        results = searcher.search("*Mac*")
        assert len(results) == 1
        assert all("Mac" in p.full_name for p in results)

    def test_wildcard_search_question_mark(self, searcher: PlayerSearch) -> None:
        """Test wildcard search using question mark for single character matching."""
        results = searcher.search("?lex Ovechkin")
        assert len(results) == 1
        assert results[0].full_name == "Alex Ovechkin"

    def test_wildcard_search_multiple_wildcards(self, searcher: PlayerSearch) -> None:
        """Test wildcard search with multiple wildcards."""
        results = searcher.search("*e*o*")
        # Should match names with 'e' before 'o'
        assert len(results) > 0


class TestPlayerSearchFuzzySearch:
    """Tests for fuzzy search."""

    def test_fuzzy_search_close_match(self, searcher: PlayerSearch) -> None:
        """Test fuzzy search with close match."""
        results = searcher.search("McDavd", fuzzy=True)  # Typo
        assert len(results) >= 1
        # Should still find McDavid

    def test_fuzzy_search_partial_name(self, searcher: PlayerSearch) -> None:
        """Test fuzzy search with partial name."""
        results = searcher.search("Ovechkn", fuzzy=True)  # Missing 'i'
        assert len(results) >= 1

    def test_fuzzy_search_exact_match(self, searcher: PlayerSearch) -> None:
        """Test fuzzy search with exact match."""
        results = searcher.search("Connor McDavid", fuzzy=True)
        assert len(results) >= 1
        assert results[0].full_name == "Connor McDavid"

    def test_fuzzy_search_no_close_matches(self, searcher: PlayerSearch) -> None:
        """Test fuzzy search with no close matches."""
        results = searcher.search("XYZ123", fuzzy=True)
        assert len(results) == 0


class TestPlayerSearchScoreFiltering:
    """Tests for score filtering."""

    def test_filter_by_min_score(self, searcher: PlayerSearch) -> None:
        """Test filtering by minimum score."""
        results = searcher.search("", min_score=32)
        assert len(results) == 3  # McDavid (32), Matthews (33), MacKinnon (34)
        assert all(p.full_score >= 32 for p in results)

    def test_filter_by_max_score(self, searcher: PlayerSearch) -> None:
        """Test filtering by maximum score."""
        results = searcher.search("", max_score=31)
        assert len(results) == 3  # Bedard (27), Ovechkin (31), Crosby (31)
        assert all(p.full_score <= 31 for p in results)

    def test_filter_by_score_range(self, searcher: PlayerSearch) -> None:
        """Test filtering by score range."""
        results = searcher.search("", min_score=31, max_score=33)
        assert len(results) == 4  # Ovechkin, Crosby, McDavid, Matthews
        assert all(31 <= p.full_score <= 33 for p in results)

    def test_filter_score_with_name(self, searcher: PlayerSearch) -> None:
        """Test combining score filter with name search."""
        results = searcher.search("Connor", min_score=30)
        assert len(results) == 1
        assert results[0].full_name == "Connor McDavid"
        assert results[0].full_score >= 30


class TestPlayerSearchTeamFiltering:
    """Tests for team filtering."""

    def test_filter_by_team(self, searcher: PlayerSearch) -> None:
        """Test filtering by team."""
        results = searcher.search("", team="EDM")
        assert len(results) == 1
        assert results[0].team == "EDM"

    def test_filter_by_team_case_insensitive(self, searcher: PlayerSearch) -> None:
        """Test team filtering is case insensitive."""
        results_lower = searcher.search("", team="edm")
        results_upper = searcher.search("", team="EDM")
        assert len(results_lower) == len(results_upper)

    def test_filter_team_with_name(self, searcher: PlayerSearch) -> None:
        """Test combining team filter with name search."""
        results = searcher.search("Connor", team="EDM")
        assert len(results) == 1
        assert results[0].full_name == "Connor McDavid"


class TestPlayerSearchDivisionFiltering:
    """Tests for division filtering."""

    def test_filter_by_division(self, searcher: PlayerSearch) -> None:
        """Test filtering by division."""
        results = searcher.search("", division="Pacific")
        assert len(results) == 1
        assert results[0].division == "Pacific"

    def test_filter_by_division_case_insensitive(self, searcher: PlayerSearch) -> None:
        """Test division filtering is case insensitive."""
        results_lower = searcher.search("", division="pacific")
        results_upper = searcher.search("", division="PACIFIC")
        assert len(results_lower) == len(results_upper)


class TestPlayerSearchConferenceFiltering:
    """Tests for conference filtering."""

    def test_filter_by_conference(self, searcher: PlayerSearch) -> None:
        """Test filtering by conference."""
        results = searcher.search("", conference="Western")
        assert len(results) == 3  # EDM, CHI, COL
        assert all(p.conference == "Western" for p in results)

    def test_filter_by_conference_case_insensitive(self, searcher: PlayerSearch) -> None:
        """Test conference filtering is case insensitive."""
        results_lower = searcher.search("", conference="western")
        results_upper = searcher.search("", conference="WESTERN")
        assert len(results_lower) == len(results_upper)


class TestPlayerSearchCombinedFiltering:
    """Tests for combining multiple filters."""

    def test_combined_name_score_team(self, searcher: PlayerSearch) -> None:
        """Test combining name, score, and team filters."""
        results = searcher.search("Connor", min_score=30, team="EDM")
        assert len(results) == 1
        assert results[0].full_name == "Connor McDavid"

    def test_combined_division_conference(self, searcher: PlayerSearch) -> None:
        """Test combining division and conference filters."""
        results = searcher.search("", division="Metropolitan", conference="Eastern")
        assert len(results) == 2  # Ovechkin, Crosby
        assert all(p.division == "Metropolitan" for p in results)
        assert all(p.conference == "Eastern" for p in results)

    def test_combined_all_filters(self, searcher: PlayerSearch) -> None:
        """Test combining all filters."""
        results = searcher.search(
            "Connor",
            min_score=25,
            max_score=35,
            team="EDM",
            division="Pacific",
            conference="Western",
        )
        assert len(results) == 1
        assert results[0].full_name == "Connor McDavid"


class TestPlayerSearchSorting:
    """Tests for result sorting."""

    def test_results_sorted_by_score(self, searcher: PlayerSearch) -> None:
        """Test that results are sorted by score descending."""
        results = searcher.search("")
        scores = [p.full_score for p in results]
        assert scores == sorted(scores, reverse=True)

    def test_results_sorted_by_name_when_tied(self, searcher: PlayerSearch) -> None:
        """Test that results with same score are sorted by name."""
        results = searcher.search("", min_score=31, max_score=31)
        # Ovechkin and Crosby both have 31
        assert len(results) == 2
        assert results[0].full_name < results[1].full_name  # Alphabetical


class TestPlayerSearchTopPlayers:
    """Tests for get_top_players method."""

    def test_get_top_players_default(self, searcher: PlayerSearch) -> None:
        """Test getting top players with default count."""
        results = searcher.get_top_players()
        assert len(results) <= 20

    def test_get_top_players_custom_count(self, searcher: PlayerSearch) -> None:
        """Test getting top players with custom count."""
        results = searcher.get_top_players(n=3)
        assert len(results) == 3
        assert results[0].full_score >= results[1].full_score >= results[2].full_score

    def test_get_top_players_more_than_available(self, searcher: PlayerSearch) -> None:
        """Test requesting more players than available."""
        results = searcher.get_top_players(n=100)
        assert len(results) == 6  # Only 6 players available


class TestPlayerSearchStats:
    """Tests for get_stats method."""

    def test_get_stats_with_players(self, searcher: PlayerSearch) -> None:
        """Test getting statistics with players."""
        stats = searcher.get_stats()

        assert stats["total_players"] == 6
        assert stats["avg_score"] > 0
        assert stats["min_score"] == 27  # Bedard
        assert stats["max_score"] == 34  # MacKinnon
        assert stats["total_teams"] == 6

    def test_get_stats_empty(self) -> None:
        """Test getting statistics with no players."""
        searcher = PlayerSearch([])
        stats = searcher.get_stats()

        assert stats["total_players"] == 0
        assert stats["avg_score"] == 0.0
        assert stats["min_score"] == 0
        assert stats["max_score"] == 0
        assert stats["total_teams"] == 0

    def test_get_stats_avg_calculation(self, sample_players: list[PlayerScore]) -> None:
        """Test average score calculation."""
        searcher = PlayerSearch(sample_players)
        stats = searcher.get_stats()

        # Manual calculation: (32+33+27+31+31+34)/6 = 188/6 ≈ 31.33
        expected_avg = sum(p.full_score for p in sample_players) / len(sample_players)
        assert stats["avg_score"] == pytest.approx(expected_avg)
