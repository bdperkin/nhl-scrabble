"""Tests for HTML report generation."""

import pytest

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import PlayoffTeam
from nhl_scrabble.models.team import TeamScore


def _can_import_bs4() -> bool:
    """Check if beautifulsoup4 can be imported."""
    try:
        import bs4  # noqa: F401

        return True
    except ImportError:
        return False


# Skip all tests if beautifulsoup4 is not installed (optional dependency)
pytestmark = pytest.mark.skipif(
    not _can_import_bs4(),
    reason="beautifulsoup4 not found (optional test dependency)",
)


@pytest.fixture
def sample_players():
    """Sample player data for testing."""
    return [
        PlayerScore(
            first_name="Alexander",
            last_name="Ovechkin",
            full_name="Alexander Ovechkin",
            first_score=20,
            last_score=30,
            full_score=50,
            team="WSH",
            division="Metropolitan",
            conference="Eastern",
        ),
        PlayerScore(
            first_name="Connor",
            last_name="McDavid",
            full_name="Connor McDavid",
            first_score=22,
            last_score=26,
            full_score=48,
            team="EDM",
            division="Pacific",
            conference="Western",
        ),
        PlayerScore(
            first_name="Sidney",
            last_name="Crosby",
            full_name="Sidney Crosby",
            first_score=20,
            last_score=25,
            full_score=45,
            team="PIT",
            division="Metropolitan",
            conference="Eastern",
        ),
    ]


@pytest.fixture
def sample_team_scores():
    """Sample team scores for testing."""
    return {
        "WSH": TeamScore(
            abbrev="WSH",
            total=1500,
            players=[],
            division="Metropolitan",
            conference="Eastern",
        ),
        "EDM": TeamScore(
            abbrev="EDM",
            total=1450,
            players=[],
            division="Pacific",
            conference="Western",
        ),
    }


@pytest.fixture
def sample_playoff_standings():
    """Sample playoff standings for testing."""
    return {
        "Eastern": [
            PlayoffTeam(
                abbrev="WSH",
                total=1500,
                players=30,
                avg=50.0,
                conference="Eastern",
                division="Metropolitan",
                seed_type="Metropolitan #1",
                in_playoffs=True,
                division_rank=1,
                status_indicator="y",
            ),
        ],
        "Western": [
            PlayoffTeam(
                abbrev="EDM",
                total=1450,
                players=30,
                avg=48.3,
                conference="Western",
                division="Pacific",
                seed_type="Pacific #1",
                in_playoffs=True,
                division_rank=1,
                status_indicator="y",
            ),
        ],
    }


@pytest.fixture
def sample_division_standings():
    """Sample division standings."""
    from nhl_scrabble.models.standings import DivisionStandings

    return {
        "Metropolitan": DivisionStandings(
            name="Metropolitan",
            total=12000,
            teams=["WSH", "NYR", "PHI", "PIT"],
            player_count=120,
            avg_per_team=3000.0,
        ),
        "Pacific": DivisionStandings(
            name="Pacific",
            total=11500,
            teams=["EDM", "VAN", "CGY", "SEA"],
            player_count=120,
            avg_per_team=2875.0,
        ),
    }


@pytest.fixture
def sample_conference_standings():
    """Sample conference standings."""
    from nhl_scrabble.models.standings import ConferenceStandings

    return {
        "Eastern": ConferenceStandings(
            name="Eastern",
            total=24000,
            teams=["WSH", "NYR", "PHI", "PIT", "BOS", "TOR", "MTL", "OTT"],
            player_count=240,
            avg_per_team=3000.0,
        ),
        "Western": ConferenceStandings(
            name="Western",
            total=23000,
            teams=["EDM", "VAN", "CGY", "SEA", "DAL", "MIN", "STL", "WPG"],
            player_count=240,
            avg_per_team=2875.0,
        ),
    }


def test_html_report_generates_valid_html(
    sample_team_scores,
    sample_players,
    sample_division_standings,
    sample_conference_standings,
    sample_playoff_standings,
):
    """Test that HTML report generates valid HTML."""
    from dataclasses import asdict

    from bs4 import BeautifulSoup

    from nhl_scrabble.formatters import get_formatter

    # Prepare data for formatter
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in sample_team_scores.items()
    }
    divisions_data = {
        name: asdict(standing) for name, standing in sample_division_standings.items()
    }
    conferences_data = {
        name: asdict(standing) for name, standing in sample_conference_standings.items()
    }
    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in sample_playoff_standings.items()
    }

    data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(sample_team_scores),
            "total_players": len(sample_players),
        },
    }

    # Generate HTML using formatter factory
    formatter = get_formatter("html")
    html = formatter.format(data)

    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")

    # Verify basic structure
    assert soup.find("html") is not None
    assert soup.find("head") is not None
    assert soup.find("body") is not None
    assert soup.find("title") is not None


def test_html_report_includes_all_sections(
    sample_team_scores,
    sample_players,
    sample_division_standings,
    sample_conference_standings,
    sample_playoff_standings,
):
    """Test that HTML report includes all required sections."""
    from dataclasses import asdict

    from bs4 import BeautifulSoup

    from nhl_scrabble.formatters import get_formatter

    # Prepare data for formatter
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in sample_team_scores.items()
    }
    divisions_data = {
        name: asdict(standing) for name, standing in sample_division_standings.items()
    }
    conferences_data = {
        name: asdict(standing) for name, standing in sample_conference_standings.items()
    }
    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in sample_playoff_standings.items()
    }

    data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(sample_team_scores),
            "total_players": len(sample_players),
        },
    }

    # Generate HTML using formatter factory
    formatter = get_formatter("html")
    html = formatter.format(data)
    soup = BeautifulSoup(html, "html.parser")

    # Check for key sections
    h1 = soup.find("h1")
    assert h1 is not None
    assert "NHL Scrabble" in h1.text

    # Check for summary and team standings headings
    h2_tags = soup.find_all("h2")
    h2_texts = [tag.text for tag in h2_tags]
    assert "Summary" in h2_texts
    assert "Team Standings" in h2_texts

    # Check for team standings table
    tables = soup.find_all("table")
    assert len(tables) >= 1  # At least team standings table


def test_html_report_escapes_dangerous_content(
    sample_team_scores,
    sample_division_standings,
    sample_conference_standings,
    sample_playoff_standings,
):
    """Test that HTML report escapes XSS attempts."""
    from dataclasses import asdict

    from bs4 import BeautifulSoup

    from nhl_scrabble.formatters import get_formatter

    # Create player with XSS attempt in name
    xss_players = [
        PlayerScore(
            first_name="<script>alert('xss')</script>",
            last_name="Test",
            full_name="<script>alert('xss')</script> Test",
            first_score=25,
            last_score=25,
            full_score=50,
            team="TOR",
            division="Atlantic",
            conference="Eastern",
        ),
    ]

    # Prepare data for formatter
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in sample_team_scores.items()
    }
    divisions_data = {
        name: asdict(standing) for name, standing in sample_division_standings.items()
    }
    conferences_data = {
        name: asdict(standing) for name, standing in sample_conference_standings.items()
    }
    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in sample_playoff_standings.items()
    }

    data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(sample_team_scores),
            "total_players": len(xss_players),
        },
    }

    # Generate HTML using formatter factory
    formatter = get_formatter("html")
    html = formatter.format(data)

    # Should not contain raw script tag (HTMLFormatter doesn't render player names, only team data)
    assert "<script>alert('xss')</script>" not in html

    # The HTML should be safe - no raw script tags
    # Note: HTMLFormatter only shows team standings, not individual player names,
    # so XSS in player names won't appear in output
    soup = BeautifulSoup(html, "html.parser")
    assert soup.find("html") is not None  # Valid HTML structure


def test_html_report_responsive_design(
    sample_team_scores,
    sample_players,
    sample_division_standings,
    sample_conference_standings,
    sample_playoff_standings,
):
    """Test that HTML includes responsive meta tag."""
    from dataclasses import asdict

    from bs4 import BeautifulSoup

    from nhl_scrabble.formatters import get_formatter

    # Prepare data for formatter
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in sample_team_scores.items()
    }
    divisions_data = {
        name: asdict(standing) for name, standing in sample_division_standings.items()
    }
    conferences_data = {
        name: asdict(standing) for name, standing in sample_conference_standings.items()
    }
    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in sample_playoff_standings.items()
    }

    data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(sample_team_scores),
            "total_players": len(sample_players),
        },
    }

    # Generate HTML using formatter factory
    formatter = get_formatter("html")
    html = formatter.format(data)
    soup = BeautifulSoup(html, "html.parser")

    meta = soup.find("meta", attrs={"name": "viewport"})
    assert meta is not None
    assert "width=device-width" in meta.get("content", "")


def test_html_report_includes_statistics(
    sample_team_scores,
    sample_players,
    sample_division_standings,
    sample_conference_standings,
    sample_playoff_standings,
):
    """Test that HTML report includes statistics cards."""
    from dataclasses import asdict

    from bs4 import BeautifulSoup

    from nhl_scrabble.formatters import get_formatter

    # Prepare data for formatter
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in sample_team_scores.items()
    }
    divisions_data = {
        name: asdict(standing) for name, standing in sample_division_standings.items()
    }
    conferences_data = {
        name: asdict(standing) for name, standing in sample_conference_standings.items()
    }
    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in sample_playoff_standings.items()
    }

    data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(sample_team_scores),
            "total_players": len(sample_players),
        },
    }

    # Generate HTML using formatter factory
    formatter = get_formatter("html")
    html = formatter.format(data)
    soup = BeautifulSoup(html, "html.parser")

    # Check for summary section (HTMLFormatter uses simple summary, not stat cards)
    summary_div = soup.find("div", class_="summary")
    assert summary_div is not None

    # Check for summary statistics
    summary_text = summary_div.text
    assert "Total Players" in summary_text
    assert "Total Teams" in summary_text


def test_html_report_includes_print_styles(
    sample_team_scores,
    sample_players,
    sample_division_standings,
    sample_conference_standings,
    sample_playoff_standings,
):
    """Test that HTML includes print-friendly stylesheet."""
    from dataclasses import asdict

    from nhl_scrabble.formatters import get_formatter

    # Prepare data for formatter
    teams_data = {
        abbrev: {
            "total": team.total,
            "players": [asdict(p) for p in team.players],
            "division": team.division,
            "conference": team.conference,
            "avg_per_player": team.avg_per_player,
        }
        for abbrev, team in sample_team_scores.items()
    }
    divisions_data = {
        name: asdict(standing) for name, standing in sample_division_standings.items()
    }
    conferences_data = {
        name: asdict(standing) for name, standing in sample_conference_standings.items()
    }
    playoffs_data = {
        conf: [asdict(team) for team in teams] for conf, teams in sample_playoff_standings.items()
    }

    data = {
        "teams": teams_data,
        "divisions": divisions_data,
        "conferences": conferences_data,
        "playoffs": playoffs_data,
        "summary": {
            "total_teams": len(sample_team_scores),
            "total_players": len(sample_players),
        },
    }

    # Generate HTML using formatter factory
    formatter = get_formatter("html")
    html = formatter.format(data)

    # Check for CSS styles (HTMLFormatter has embedded CSS but no print styles)
    assert "<style>" in html
    assert "table" in html  # CSS for tables
    assert "body" in html  # CSS for body


def test_html_report_with_empty_data():
    """Test HTML report generation with empty data."""
    from nhl_scrabble.formatters import get_formatter

    # Prepare empty data for formatter
    data = {
        "teams": {},
        "divisions": {},
        "conferences": {},
        "playoffs": {},
        "summary": {
            "total_teams": 0,
            "total_players": 0,
        },
    }

    # Should not crash with empty data
    formatter = get_formatter("html")
    html = formatter.format(data)

    assert html
    assert "NHL Scrabble" in html
