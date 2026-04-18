"""Tests for CSV exporter."""

from pathlib import Path

import pytest

from nhl_scrabble.exporters.csv_exporter import CSVExporter
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import PlayoffTeam
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def csv_exporter() -> CSVExporter:
    """Create CSV exporter instance."""
    return CSVExporter()


@pytest.fixture
def sample_teams() -> dict[str, TeamScore]:
    """Create sample team scores."""
    players_tor = [
        PlayerScore(
            first_name="John",
            last_name="Tavares",
            full_name="John Tavares",
            first_score=10,
            last_score=15,
            full_score=25,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Auston",
            last_name="Matthews",
            full_name="Auston Matthews",
            first_score=18,
            last_score=20,
            full_score=38,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    players_mtl = [
        PlayerScore(
            first_name="Nick",
            last_name="Suzuki",
            full_name="Nick Suzuki",
            first_score=8,
            last_score=25,
            full_score=33,
            team="MTL",
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    return {
        "TOR": TeamScore(
            abbrev="TOR",
            total=63,
            players=players_tor,
            division="Atlantic",
            conference="Eastern",
        ),
        "MTL": TeamScore(
            abbrev="MTL",
            total=33,
            players=players_mtl,
            division="Atlantic",
            conference="Eastern",
        ),
    }


@pytest.fixture
def sample_players() -> list[PlayerScore]:
    """Create sample player scores."""
    return [
        PlayerScore(
            first_name="John",
            last_name="Tavares",
            full_name="John Tavares",
            first_score=10,
            last_score=15,
            full_score=25,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Auston",
            last_name="Matthews",
            full_name="Auston Matthews",
            first_score=18,
            last_score=20,
            full_score=38,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Nick",
            last_name="Suzuki",
            full_name="Nick Suzuki",
            first_score=8,
            last_score=25,
            full_score=33,
            team="MTL",
            division="Atlantic",
            conference="Eastern",
        ),
    ]


def test_export_team_scores_dict(
    csv_exporter: CSVExporter, sample_teams: dict[str, TeamScore], tmp_path: Path
) -> None:
    """Test exporting team scores from dictionary."""
    output = tmp_path / "teams.csv"

    csv_exporter.export_team_scores(sample_teams, output)

    assert output.exists()
    content = output.read_text()

    # Check header
    assert "Team,Division,Conference,Total Score,Player Count,Average Score" in content

    # Check data rows (sorted by total score descending)
    lines = content.strip().split("\n")
    assert len(lines) == 3  # header + 2 teams

    # TOR should be first (higher score)
    assert "TOR,Atlantic,Eastern,63,2,31.50" in content
    assert "MTL,Atlantic,Eastern,33,1,33.00" in content


def test_export_team_scores_list(
    csv_exporter: CSVExporter, sample_teams: dict[str, TeamScore], tmp_path: Path
) -> None:
    """Test exporting team scores from list."""
    output = tmp_path / "teams.csv"
    teams_list = list(sample_teams.values())

    csv_exporter.export_team_scores(teams_list, output)

    assert output.exists()
    content = output.read_text()
    assert "Team,Division,Conference,Total Score,Player Count,Average Score" in content


def test_export_player_scores(
    csv_exporter: CSVExporter, sample_players: list[PlayerScore], tmp_path: Path
) -> None:
    """Test exporting player scores."""
    output = tmp_path / "players.csv"

    csv_exporter.export_player_scores(sample_players, output)

    assert output.exists()
    content = output.read_text()

    # Check header
    assert (
        "Player Name,Team,Division,Conference,First Name Score,Last Name Score,Total Score"
        in content
    )

    # Check data rows (sorted by score descending)
    lines = content.strip().split("\n")
    assert len(lines) == 4  # header + 3 players

    # Auston Matthews should be first (highest score: 38)
    assert "Auston Matthews,TOR,Atlantic,Eastern,18,20,38" in content
    assert "Nick Suzuki,MTL,Atlantic,Eastern,8,25,33" in content
    assert "John Tavares,TOR,Atlantic,Eastern,10,15,25" in content


def test_export_division_standings(csv_exporter: CSVExporter, tmp_path: Path) -> None:
    """Test exporting division standings."""
    output = tmp_path / "divisions.csv"

    # Create sample division standings with TeamScore objects
    teams = [
        TeamScore(
            abbrev="TOR",
            total=63,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
        TeamScore(
            abbrev="MTL",
            total=33,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    # Create a standings object with teams attribute containing TeamScore objects
    class StandingsWithTeams:
        def __init__(self, teams: list[TeamScore]) -> None:
            self.teams = teams

    division_standings = {
        "Atlantic": StandingsWithTeams(teams),
    }

    csv_exporter.export_division_standings(division_standings, output)

    assert output.exists()
    content = output.read_text()

    # Check header
    assert "Division,Team,Total Score,Player Count,Average Score" in content

    # Check data
    assert "Atlantic,TOR,63,0,0.00" in content
    assert "Atlantic,MTL,33,0,0.00" in content


def test_export_conference_standings(csv_exporter: CSVExporter, tmp_path: Path) -> None:
    """Test exporting conference standings."""
    output = tmp_path / "conferences.csv"

    # Create sample conference standings with TeamScore objects
    teams = [
        TeamScore(
            abbrev="TOR",
            total=63,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
        TeamScore(
            abbrev="MTL",
            total=33,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    # Create a standings object with teams attribute containing TeamScore objects
    class StandingsWithTeams:
        def __init__(self, teams: list[TeamScore]) -> None:
            self.teams = teams

    conference_standings = {
        "Eastern": StandingsWithTeams(teams),
    }

    csv_exporter.export_conference_standings(conference_standings, output)

    assert output.exists()
    content = output.read_text()

    # Check header
    assert "Conference,Team,Division,Total Score,Player Count,Average Score" in content

    # Check data
    assert "Eastern,TOR,Atlantic,63,0,0.00" in content
    assert "Eastern,MTL,Atlantic,33,0,0.00" in content


def test_export_playoff_standings(csv_exporter: CSVExporter, tmp_path: Path) -> None:
    """Test exporting playoff standings."""
    output = tmp_path / "playoffs.csv"

    # Create sample playoff standings using the PlayoffTeam model
    playoff_standings = {
        "Eastern": [
            PlayoffTeam(
                abbrev="TOR",
                total=63,
                players=2,
                avg=31.5,
                conference="Eastern",
                division="Atlantic",
                status_indicator="y",
            ),
            PlayoffTeam(
                abbrev="MTL",
                total=33,
                players=1,
                avg=33.0,
                conference="Eastern",
                division="Atlantic",
                status_indicator="x",
            ),
        ],
    }

    csv_exporter.export_playoff_standings(playoff_standings, output)

    assert output.exists()
    content = output.read_text()

    # Check header
    assert "Conference,Seed,Team,Division,Total Score,Average Score,Status" in content

    # Check data
    assert "Eastern,1,TOR,Atlantic,63,31.50,y" in content
    assert "Eastern,2,MTL,Atlantic,33,33.00,x" in content


def test_csv_encoding(csv_exporter: CSVExporter, tmp_path: Path) -> None:
    """Test CSV handles UTF-8 encoding correctly."""
    output = tmp_path / "players.csv"

    # Create player with accented name
    players = [
        PlayerScore(
            first_name="François",
            last_name="Beauchemin",
            full_name="François Beauchemin",
            first_score=20,
            last_score=25,
            full_score=45,
            team="MTL",
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    csv_exporter.export_player_scores(players, output)

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "François Beauchemin" in content


def test_csv_sorting(csv_exporter: CSVExporter, tmp_path: Path) -> None:
    """Test that CSV exports are properly sorted."""
    output = tmp_path / "teams.csv"

    teams = [
        TeamScore(
            abbrev="MTL",
            total=30,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
        TeamScore(
            abbrev="TOR",
            total=50,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
        TeamScore(
            abbrev="BOS",
            total=40,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    csv_exporter.export_team_scores(teams, output)

    content = output.read_text()
    lines = content.strip().split("\n")

    # Check sorting (descending by total score)
    assert "TOR" in lines[1]  # 50 points
    assert "BOS" in lines[2]  # 40 points
    assert "MTL" in lines[3]  # 30 points
