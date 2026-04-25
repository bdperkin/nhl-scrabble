"""Tests for CSV exporter.

.. note::
    CSVExporter is deprecated in v2.1.0. These tests verify backward compatibility
    and proper deprecation warnings during the deprecation period.
"""

import warnings
from pathlib import Path

import pytest

from nhl_scrabble.exporters.csv_exporter import CSVExporter
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import PlayoffTeam
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def csv_exporter() -> CSVExporter:
    """Create CSV exporter instance (suppressing deprecation warning for tests)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
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


# ============================================================================
# DEPRECATION WARNING TESTS (v2.1.0+)
# ============================================================================


def test_csv_exporter_init_deprecated() -> None:
    """Test that CSVExporter.__init__ raises deprecation warning."""
    with pytest.warns(DeprecationWarning, match="CSVExporter is deprecated"):
        CSVExporter()


def test_csv_exporter_init_deprecation_message() -> None:
    """Test deprecation warning message provides migration guidance."""
    with pytest.warns(
        DeprecationWarning, match="CSVExporter is deprecated.*3.0.0.*get_formatter"
    ) as record:
        CSVExporter()

    # Check warning message is helpful
    assert len(record) == 1
    warning_message = str(record[0].message)
    assert "3.0.0" in warning_message  # Mentions removal version
    assert "get_formatter" in warning_message  # Mentions alternative


def test_export_team_scores_deprecated(sample_teams: dict[str, TeamScore], tmp_path: Path) -> None:
    """Test that export_team_scores raises deprecation warning."""
    output = tmp_path / "teams.csv"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()
        exporter.export_team_scores(sample_teams, output)

        # Should have at least 2 warnings: __init__ + method
        assert len(w) >= 2
        assert any("export_team_scores" in str(warning.message) for warning in w)
        assert any(warning.category is DeprecationWarning for warning in w)


def test_export_player_scores_deprecated(sample_players: list[PlayerScore], tmp_path: Path) -> None:
    """Test that export_player_scores raises deprecation warning."""
    output = tmp_path / "players.csv"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()
        exporter.export_player_scores(sample_players, output)

        # Check for method-specific deprecation
        assert any("export_player_scores" in str(warning.message) for warning in w)


def test_export_division_standings_deprecated(tmp_path: Path) -> None:
    """Test that export_division_standings raises deprecation warning."""
    output = tmp_path / "divisions.csv"

    teams = [
        TeamScore(
            abbrev="TOR",
            total=63,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    class StandingsWithTeams:
        def __init__(self, teams: list[TeamScore]) -> None:
            self.teams = teams

    division_standings = {"Atlantic": StandingsWithTeams(teams)}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()
        exporter.export_division_standings(division_standings, output)

        assert any("export_division_standings" in str(warning.message) for warning in w)


def test_export_conference_standings_deprecated(tmp_path: Path) -> None:
    """Test that export_conference_standings raises deprecation warning."""
    output = tmp_path / "conferences.csv"

    teams = [
        TeamScore(
            abbrev="TOR",
            total=63,
            players=[],
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    class StandingsWithTeams:
        def __init__(self, teams: list[TeamScore]) -> None:
            self.teams = teams

    conference_standings = {"Eastern": StandingsWithTeams(teams)}

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()
        exporter.export_conference_standings(conference_standings, output)

        assert any("export_conference_standings" in str(warning.message) for warning in w)


def test_export_playoff_standings_deprecated(tmp_path: Path) -> None:
    """Test that export_playoff_standings raises deprecation warning."""
    output = tmp_path / "playoffs.csv"

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
        ],
    }

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()
        exporter.export_playoff_standings(playoff_standings, output)

        assert any("export_playoff_standings" in str(warning.message) for warning in w)


def test_all_methods_raise_deprecation_warnings(
    sample_teams: dict[str, TeamScore], sample_players: list[PlayerScore], tmp_path: Path
) -> None:
    """Test that ALL CSVExporter methods raise deprecation warnings."""
    # Test that every public method triggers deprecation warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        exporter = CSVExporter()  # 1 warning

        # All 5 export methods
        exporter.export_team_scores(sample_teams, tmp_path / "teams.csv")  # +1
        exporter.export_player_scores(sample_players, tmp_path / "players.csv")  # +1

        teams = [
            TeamScore(
                abbrev="TOR",
                total=63,
                players=[],
                division="Atlantic",
                conference="Eastern",
            ),
        ]

        class StandingsWithTeams:
            def __init__(self, teams: list[TeamScore]) -> None:
                self.teams = teams

        exporter.export_division_standings(
            {"Atlantic": StandingsWithTeams(teams)}, tmp_path / "divisions.csv"
        )  # +1
        exporter.export_conference_standings(
            {"Eastern": StandingsWithTeams(teams)}, tmp_path / "conferences.csv"
        )  # +1

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
            ],
        }
        exporter.export_playoff_standings(playoff_standings, tmp_path / "playoffs.csv")  # +1

        # Should have 6 total warnings: 1 __init__ + 5 methods
        assert len(w) == 6
        assert all(warning.category is DeprecationWarning for warning in w)


def test_deprecated_functionality_still_works(
    sample_teams: dict[str, TeamScore], tmp_path: Path
) -> None:
    """Test that deprecated CSVExporter still produces correct output (backward compatibility)."""
    output = tmp_path / "teams.csv"

    # Suppress warnings to test functionality
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        exporter = CSVExporter()
        exporter.export_team_scores(sample_teams, output)

        # Verify output is still correct
        assert output.exists()
        content = output.read_text()
        assert "Team,Division,Conference,Total Score,Player Count,Average Score" in content
        assert "TOR" in content
        assert "MTL" in content
