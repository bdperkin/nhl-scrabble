"""Edge case tests for all report types."""

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings, PlayoffTeam
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.reports.conference_report import ConferenceReporter
from nhl_scrabble.reports.division_report import DivisionReporter
from nhl_scrabble.reports.playoff_report import PlayoffReporter
from nhl_scrabble.reports.stats_report import StatsReporter
from nhl_scrabble.reports.team_report import TeamReporter


class TestConferenceReporterEdgeCases:
    """Test edge cases for ConferenceReporter."""

    def test_empty_standings(self):
        """Test conference report with empty standings."""
        reporter = ConferenceReporter()
        result = reporter.generate({})
        assert "🌎 CONFERENCE SCRABBLE SCORES" in result
        assert "Eastern" not in result
        assert "Western" not in result

    def test_single_conference(self):
        """Test conference report with only one conference."""
        standings = {
            "Eastern": ConferenceStandings(
                name="Eastern",
                total=5000,
                teams=["WSH", "NYR", "PIT"],
                player_count=90,
                avg_per_team=1666.67,
            ),
        }
        reporter = ConferenceReporter()
        result = reporter.generate(standings)
        assert "Eastern" in result
        assert "5000" in result
        assert "NYR, PIT, WSH" in result  # Sorted alphabetically

    def test_conference_with_zero_teams(self):
        """Test conference with zero teams."""
        standings = {
            "Empty": ConferenceStandings(
                name="Empty",
                total=0,
                teams=[],
                player_count=0,
                avg_per_team=0.0,
            ),
        }
        reporter = ConferenceReporter()
        result = reporter.generate(standings)
        assert "Empty" in result
        assert "0" in result

    def test_large_conference_stats(self):
        """Test conference with large team counts."""
        standings = {
            "Mega": ConferenceStandings(
                name="Mega",
                total=999999,
                teams=["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08"],
                player_count=240,
                avg_per_team=124999.875,
            ),
        }
        reporter = ConferenceReporter()
        result = reporter.generate(standings)
        assert "Mega" in result
        assert "999999" in result or "999,999" in result
        assert "8" in result


class TestDivisionReporterEdgeCases:
    """Test edge cases for DivisionReporter."""

    def test_empty_standings(self):
        """Test division report with empty standings."""
        reporter = DivisionReporter()
        result = reporter.generate({})
        assert "🗺️  DIVISION SCRABBLE SCORES" in result

    def test_single_division(self):
        """Test division report with only one division."""
        standings = {
            "Metropolitan": DivisionStandings(
                name="Metropolitan",
                total=4500,
                teams=["WSH", "NYR", "PIT"],
                player_count=90,
                avg_per_team=1500.0,
            ),
        }
        reporter = DivisionReporter()
        result = reporter.generate(standings)
        assert "Metropolitan" in result
        assert "4500" in result

    def test_division_with_many_teams(self):
        """Test division with many teams."""
        standings = {
            "MegaDivision": DivisionStandings(
                name="MegaDivision",
                total=50000,
                teams=[f"T{i:02d}" for i in range(1, 11)],
                player_count=300,
                avg_per_team=5000.0,
            ),
        }
        reporter = DivisionReporter()
        result = reporter.generate(standings)
        assert "MegaDivision" in result
        assert "50000" in result or "50,000" in result
        assert "10" in result


class TestPlayoffReporterEdgeCases:
    """Test edge cases for PlayoffReporter."""

    def test_empty_standings(self):
        """Test playoff report with empty standings."""
        reporter = PlayoffReporter()
        result = reporter.generate({})
        assert "🎰 WILD CARD PLAYOFF STANDINGS" in result

    def test_conference_without_wild_cards(self):
        """Test conference with only division leaders."""
        standings = {
            "Eastern": [
                PlayoffTeam(
                    abbrev="WSH",
                    total=1500,
                    players=30,
                    avg=50.0,
                    conference="Eastern",
                    division="Metropolitan",
                    seed_type="Metropolitan #1",
                    status_indicator="z-y",
                    in_playoffs=True,
                    division_rank=1,
                ),
            ],
        }
        reporter = PlayoffReporter()
        result = reporter.generate(standings)
        assert "Eastern Conference" in result
        assert "WSH" in result
        assert "1500" in result

    def test_conference_with_eliminated_teams(self):
        """Test conference with eliminated teams."""
        standings = {
            "Eastern": [
                PlayoffTeam(
                    abbrev="WSH",
                    total=1500,
                    players=30,
                    avg=50.0,
                    conference="Eastern",
                    division="Metropolitan",
                    seed_type="Metropolitan #1",
                    status_indicator="y",
                    in_playoffs=True,
                    division_rank=1,
                ),
                PlayoffTeam(
                    abbrev="PHI",
                    total=1200,
                    players=28,
                    avg=42.86,
                    conference="Eastern",
                    division="Metropolitan",
                    seed_type="",
                    status_indicator="e",
                    in_playoffs=False,
                    division_rank=5,
                ),
            ],
        }
        reporter = PlayoffReporter()
        result = reporter.generate(standings)
        assert "Eliminated from Playoff Contention" in result
        assert "PHI" in result

    def test_conference_with_wild_cards_only(self):
        """Test conference with wild card teams."""
        standings = {
            "Western": [
                PlayoffTeam(
                    abbrev="EDM",
                    total=1450,
                    players=29,
                    avg=50.0,
                    conference="Western",
                    division="Pacific",
                    seed_type="WC1",
                    status_indicator="x",
                    in_playoffs=True,
                    division_rank=4,
                ),
                PlayoffTeam(
                    abbrev="VAN",
                    total=1400,
                    players=28,
                    avg=50.0,
                    conference="Western",
                    division="Pacific",
                    seed_type="WC2",
                    status_indicator="x",
                    in_playoffs=True,
                    division_rank=5,
                ),
            ],
        }
        reporter = PlayoffReporter()
        result = reporter.generate(standings)
        assert "Wild Card" in result
        assert "EDM" in result
        assert "VAN" in result


class TestTeamReporterEdgeCases:
    """Test edge cases for TeamReporter."""

    def test_empty_teams(self):
        """Test team report with no teams."""
        reporter = TeamReporter()
        result = reporter.generate({})
        assert "📊 TEAM SCRABBLE SCORES" in result

    def test_team_with_no_players(self):
        """Test team with zero players."""
        teams = {
            "WSH": TeamScore(
                abbrev="WSH",
                total=0,
                players=[],
                division="Metropolitan",
                conference="Eastern",
            ),
        }
        reporter = TeamReporter()
        result = reporter.generate(teams)
        assert "WSH" in result
        assert "0 players" in result

    def test_team_with_fewer_players_than_top_count(self):
        """Test team with fewer players than requested top count."""
        players = [
            PlayerScore(
                first_name="Alex",
                last_name="Ovechkin",
                full_name="Alex Ovechkin",
                first_score=20,
                last_score=30,
                full_score=50,
                team="WSH",
                division="Metropolitan",
                conference="Eastern",
            ),
        ]
        teams = {
            "WSH": TeamScore(
                abbrev="WSH",
                total=50,
                players=players,
                division="Metropolitan",
                conference="Eastern",
            ),
        }
        reporter = TeamReporter(top_players_per_team=5)
        result = reporter.generate(teams)
        assert "WSH" in result
        assert "Alex Ovechkin" in result

    def test_custom_top_players_count(self):
        """Test team reporter with custom top players count."""
        players = [
            PlayerScore(
                first_name=f"Player{i}",
                last_name=f"Last{i}",
                full_name=f"Player{i} Last{i}",
                first_score=10 + i,
                last_score=20 + i,
                full_score=30 + i,
                team="WSH",
                division="Metropolitan",
                conference="Eastern",
            )
            for i in range(10)
        ]
        teams = {
            "WSH": TeamScore(
                abbrev="WSH",
                total=sum(p.full_score for p in players),
                players=players,
                division="Metropolitan",
                conference="Eastern",
            ),
        }
        reporter = TeamReporter(top_players_per_team=3)
        result = reporter.generate(teams)
        assert "WSH" in result
        # Should show only top 3 players
        assert "Player9" in result  # Highest score


class TestStatsReporterEdgeCases:
    """Test edge cases for StatsReporter."""

    def test_empty_players(self):
        """Test stats report with no players."""
        reporter = StatsReporter()
        data = ([], {}, {})
        result = reporter.generate(data)
        assert "🌟 TOP" in result
        assert "🎯 FUN STATS" in result

    def test_fewer_players_than_top_count(self):
        """Test with fewer players than requested top count."""
        players = [
            PlayerScore(
                first_name="Alex",
                last_name="Ovechkin",
                full_name="Alex Ovechkin",
                first_score=20,
                last_score=30,
                full_score=50,
                team="WSH",
                division="Metropolitan",
                conference="Eastern",
            ),
        ]
        div_standings = {
            "Metropolitan": DivisionStandings(
                name="Metropolitan",
                total=50,
                teams=["WSH"],
                player_count=1,
                avg_per_team=50.0,
            ),
        }
        conf_standings = {
            "Eastern": ConferenceStandings(
                name="Eastern",
                total=50,
                teams=["WSH"],
                player_count=1,
                avg_per_team=50.0,
            ),
        }
        reporter = StatsReporter(top_players_count=20)
        data = (players, div_standings, conf_standings)
        result = reporter.generate(data)
        assert "Alex Ovechkin" in result

    def test_division_with_zero_player_count(self):
        """Test division with zero player count (edge case for avg calculation)."""
        players = []
        div_standings = {
            "Empty": DivisionStandings(
                name="Empty",
                total=0,
                teams=[],
                player_count=0,
                avg_per_team=0.0,
            ),
        }
        conf_standings = {}
        reporter = StatsReporter()
        data = (players, div_standings, conf_standings)
        result = reporter.generate(data)
        assert "🎯 FUN STATS" in result

    def test_conference_with_zero_player_count(self):
        """Test conference with zero player count."""
        players = []
        div_standings = {}
        conf_standings = {
            "Empty": ConferenceStandings(
                name="Empty",
                total=0,
                teams=[],
                player_count=0,
                avg_per_team=0.0,
            ),
        }
        reporter = StatsReporter()
        data = (players, div_standings, conf_standings)
        result = reporter.generate(data)
        assert "🎯 FUN STATS" in result

    def test_single_player(self):
        """Test with exactly one player."""
        player = PlayerScore(
            first_name="Sidney",
            last_name="Crosby",
            full_name="Sidney Crosby",
            first_score=25,
            last_score=28,
            full_score=53,
            team="PIT",
            division="Metropolitan",
            conference="Eastern",
        )
        div_standings = {
            "Metropolitan": DivisionStandings(
                name="Metropolitan",
                total=53,
                teams=["PIT"],
                player_count=1,
                avg_per_team=53.0,
            ),
        }
        conf_standings = {
            "Eastern": ConferenceStandings(
                name="Eastern",
                total=53,
                teams=["PIT"],
                player_count=1,
                avg_per_team=53.0,
            ),
        }
        reporter = StatsReporter(top_players_count=10)
        data = ([player], div_standings, conf_standings)
        result = reporter.generate(data)
        assert "Sidney Crosby" in result
        assert "53" in result
