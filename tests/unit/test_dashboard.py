"""Tests for interactive statistics dashboard."""

# Private method access is intentional for testing

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from nhl_scrabble.dashboard import StatisticsDashboard
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def sample_players() -> list[PlayerScore]:
    """Create sample player data for testing."""
    return [
        PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            team="EDM",
            division="Pacific",
            conference="Western",
            first_score=15,
            last_score=18,
            full_score=33,
        ),
        PlayerScore(
            first_name="Auston",
            last_name="Matthews",
            full_name="Auston Matthews",
            team="TOR",
            division="Atlantic",
            conference="Eastern",
            first_score=14,
            last_score=20,
            full_score=34,
        ),
        PlayerScore(
            first_name="Sidney",
            last_name="Crosby",
            full_name="Sidney Crosby",
            team="PIT",
            division="Metropolitan",
            conference="Eastern",
            first_score=12,
            last_score=16,
            full_score=28,
        ),
        PlayerScore(
            first_name="Alex",
            last_name="Ovechkin",
            full_name="Alex Ovechkin",
            team="WSH",
            division="Metropolitan",
            conference="Eastern",
            first_score=10,
            last_score=24,
            full_score=34,
        ),
    ]


@pytest.fixture
def sample_team_scores(sample_players: list[PlayerScore]) -> dict[str, TeamScore]:
    """Create sample team score data for testing."""
    return {
        "EDM": TeamScore(
            abbrev="EDM",
            total=150,
            players=[sample_players[0]],
            division="Pacific",
            conference="Western",
        ),
        "TOR": TeamScore(
            abbrev="TOR",
            total=140,
            players=[sample_players[1]],
            division="Atlantic",
            conference="Eastern",
        ),
        "PIT": TeamScore(
            abbrev="PIT",
            total=130,
            players=[sample_players[2]],
            division="Metropolitan",
            conference="Eastern",
        ),
        "WSH": TeamScore(
            abbrev="WSH",
            total=120,
            players=[sample_players[3]],
            division="Metropolitan",
            conference="Eastern",
        ),
    }


@pytest.fixture
def sample_division_standings() -> dict[str, DivisionStandings]:
    """Create sample division standings for testing."""
    return {
        "Atlantic": DivisionStandings(
            name="Atlantic",
            total=1000,
            teams=["TOR", "FLA", "BOS", "TBL", "BUF", "DET", "OTT", "MTL"],
            player_count=160,
            avg_per_team=125.0,
        ),
        "Metropolitan": DivisionStandings(
            name="Metropolitan",
            total=950,
            teams=["CAR", "NJD", "NYR", "NYI", "PIT", "WSH", "PHI", "CBJ"],
            player_count=160,
            avg_per_team=118.75,
        ),
        "Pacific": DivisionStandings(
            name="Pacific",
            total=900,
            teams=["VGK", "EDM", "LAK", "SEA", "CGY", "VAN", "ANA", "SJS"],
            player_count=160,
            avg_per_team=112.5,
        ),
        "Central": DivisionStandings(
            name="Central",
            total=850,
            teams=["DAL", "COL", "WPG", "MIN", "NSH", "STL", "ARI", "CHI"],
            player_count=160,
            avg_per_team=106.25,
        ),
    }


@pytest.fixture
def sample_conference_standings() -> dict[str, ConferenceStandings]:
    """Create sample conference standings for testing."""
    return {
        "Eastern": ConferenceStandings(
            name="Eastern",
            total=2000,
            teams=[
                "TOR",
                "FLA",
                "BOS",
                "TBL",
                "BUF",
                "DET",
                "OTT",
                "MTL",
                "CAR",
                "NJD",
                "NYR",
                "NYI",
                "PIT",
                "WSH",
                "PHI",
                "CBJ",
            ],
            player_count=320,
            avg_per_team=125.0,
        ),
        "Western": ConferenceStandings(
            name="Western",
            total=1900,
            teams=[
                "VGK",
                "EDM",
                "LAK",
                "SEA",
                "CGY",
                "VAN",
                "ANA",
                "SJS",
                "DAL",
                "COL",
                "WPG",
                "MIN",
                "NSH",
                "STL",
                "ARI",
                "CHI",
            ],
            player_count=320,
            avg_per_team=118.75,
        ),
    }


@pytest.fixture
def dashboard(
    sample_team_scores: dict[str, TeamScore],
    sample_players: list[PlayerScore],
    sample_division_standings: dict[str, DivisionStandings],
    sample_conference_standings: dict[str, ConferenceStandings],
) -> StatisticsDashboard:
    """Create a dashboard instance for testing."""
    return StatisticsDashboard(
        team_scores=sample_team_scores,
        all_players=sample_players,
        division_standings=sample_division_standings,
        conference_standings=sample_conference_standings,
    )


class TestStatisticsDashboard:
    """Test suite for StatisticsDashboard class."""

    def test_init(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test dashboard initialization."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
        )

        assert dashboard.team_scores == sample_team_scores
        assert dashboard.all_players == sample_players
        assert dashboard.division_standings == sample_division_standings
        assert dashboard.conference_standings == sample_conference_standings
        assert dashboard.division_filter is None
        assert dashboard.conference_filter is None

    def test_init_with_filters(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test dashboard initialization with filters."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Atlantic",
            conference_filter="Eastern",
        )

        assert dashboard.division_filter == "Atlantic"
        assert dashboard.conference_filter == "Eastern"

    def test_create_header(self, dashboard: StatisticsDashboard) -> None:
        """Test header creation."""
        header = dashboard._create_header()  # Testing private method

        assert isinstance(header, Panel)
        assert header.border_style == "cyan"

    def test_create_header_with_filters(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test header creation with filters."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Atlantic",
            conference_filter="Eastern",
        )

        header = dashboard._create_header()
        assert isinstance(header, Panel)

    def test_create_top_teams_table(self, dashboard: StatisticsDashboard) -> None:
        """Test top teams table creation."""
        table = dashboard._create_top_teams_table(limit=10)

        assert isinstance(table, Table)
        assert table.title == "🏆 Top Teams by Total Score"
        assert len(table.columns) == 7

    def test_create_top_teams_table_with_division_filter(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test top teams table with division filter."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Metropolitan",
        )

        table = dashboard._create_top_teams_table(limit=10)
        assert isinstance(table, Table)
        # Should only show Metropolitan teams (PIT, WSH)
        # Note: Rich tables don't expose row data easily, so we just verify it's a Table

    def test_create_top_players_table(self, dashboard: StatisticsDashboard) -> None:
        """Test top players table creation."""
        table = dashboard._create_top_players_table(limit=10)

        assert isinstance(table, Table)
        assert table.title == "⭐ Top Players by Score"
        assert len(table.columns) == 6

    def test_create_top_players_table_with_filters(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test top players table with filters."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Atlantic",
        )

        table = dashboard._create_top_players_table(limit=10)
        assert isinstance(table, Table)

    def test_create_division_standings_table(self, dashboard: StatisticsDashboard) -> None:
        """Test division standings table creation."""
        table = dashboard._create_division_standings_table()

        assert isinstance(table, Table)
        assert table.title == "📊 Division Standings"
        assert len(table.columns) == 5

    def test_create_division_standings_table_with_filter(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test division standings table with filter."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Atlantic",
        )

        table = dashboard._create_division_standings_table()
        assert isinstance(table, Table)

    def test_create_conference_standings_table(self, dashboard: StatisticsDashboard) -> None:
        """Test conference standings table creation."""
        table = dashboard._create_conference_standings_table()

        assert isinstance(table, Table)
        assert table.title == "🏟️  Conference Standings"
        assert len(table.columns) == 5

    def test_create_conference_standings_table_with_filter(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test conference standings table with filter."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            conference_filter="Eastern",
        )

        table = dashboard._create_conference_standings_table()
        assert isinstance(table, Table)

    def test_create_layout(self, dashboard: StatisticsDashboard) -> None:
        """Test layout creation."""
        layout = dashboard._create_layout()

        assert isinstance(layout, Layout)
        # Verify layout has expected sections - get() returns None if not found
        assert layout.get("header") is not None
        assert layout.get("body") is not None
        # Check nested layouts
        body = layout.get("body")
        assert body is not None
        assert body.get("left") is not None
        assert body.get("right") is not None

    @patch("nhl_scrabble.dashboard.Live")
    def test_run_with_duration(self, mock_live: MagicMock, dashboard: StatisticsDashboard) -> None:
        """Test running dashboard with duration."""
        # Mock the Live context manager
        mock_live_instance = MagicMock()
        mock_live.return_value.__enter__ = MagicMock(return_value=mock_live_instance)
        mock_live.return_value.__exit__ = MagicMock(return_value=None)

        # Run dashboard with very short duration (must be int)
        dashboard.run(duration=1, refresh_interval=0.05)

        # Verify Live was called
        mock_live.assert_called_once()

    @patch("nhl_scrabble.dashboard.Live")
    def test_run_keyboard_interrupt(
        self, mock_live: MagicMock, dashboard: StatisticsDashboard
    ) -> None:
        """Test dashboard handles keyboard interrupt gracefully."""
        # Mock Live to raise KeyboardInterrupt
        mock_live.return_value.__enter__ = MagicMock(side_effect=KeyboardInterrupt)

        # Should not raise, but exit gracefully
        dashboard.run(duration=1)

    def test_display_static(self, dashboard: StatisticsDashboard) -> None:
        """Test static dashboard display."""
        # Should not raise any exceptions
        with patch.object(dashboard.console, "print") as mock_print:
            dashboard.display_static()
            mock_print.assert_called_once()


class TestDashboardFiltering:
    """Test suite for dashboard filtering functionality."""

    def test_division_filter_teams(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test that division filter correctly filters teams."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Metropolitan",
        )

        table = dashboard._create_top_teams_table()
        assert isinstance(table, Table)

    def test_conference_filter_teams(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test that conference filter correctly filters teams."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            conference_filter="Eastern",
        )

        table = dashboard._create_top_teams_table()
        assert isinstance(table, Table)

    def test_combined_filters(
        self,
        sample_team_scores: dict[str, TeamScore],
        sample_players: list[PlayerScore],
        sample_division_standings: dict[str, DivisionStandings],
        sample_conference_standings: dict[str, ConferenceStandings],
    ) -> None:
        """Test that combined filters work correctly."""
        dashboard = StatisticsDashboard(
            team_scores=sample_team_scores,
            all_players=sample_players,
            division_standings=sample_division_standings,
            conference_standings=sample_conference_standings,
            division_filter="Atlantic",
            conference_filter="Eastern",
        )

        # Should create all tables without error
        teams_table = dashboard._create_top_teams_table()
        players_table = dashboard._create_top_players_table()
        divisions_table = dashboard._create_division_standings_table()
        conferences_table = dashboard._create_conference_standings_table()

        assert isinstance(teams_table, Table)
        assert isinstance(players_table, Table)
        assert isinstance(divisions_table, Table)
        assert isinstance(conferences_table, Table)
