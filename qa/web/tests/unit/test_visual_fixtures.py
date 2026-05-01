"""Unit tests for visual test fixtures.

Tests fixture file loading, structure validation, and data completeness.
"""

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "visual" / "fixtures"


def test_fixtures_directory_exists() -> None:
    """Test that fixtures directory exists."""
    assert FIXTURES_DIR.exists(), f"Fixtures directory not found: {FIXTURES_DIR}"
    assert FIXTURES_DIR.is_dir(), f"Fixtures path is not a directory: {FIXTURES_DIR}"


def test_standings_fixture_exists() -> None:
    """Test that standings fixture file exists."""
    standings_file = FIXTURES_DIR / "nhl_standings.json"
    assert standings_file.exists(), f"Standings fixture not found: {standings_file}"
    assert standings_file.is_file(), f"Standings fixture is not a file: {standings_file}"


def test_rosters_fixture_exists() -> None:
    """Test that rosters fixture file exists."""
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"
    assert rosters_file.exists(), f"Rosters fixture not found: {rosters_file}"
    assert rosters_file.is_file(), f"Rosters fixture is not a file: {rosters_file}"


def test_standings_fixture_valid_json() -> None:
    """Test that standings fixture contains valid JSON."""
    standings_file = FIXTURES_DIR / "nhl_standings.json"
    with open(standings_file) as f:
        data = json.load(f)

    # Should be a dictionary
    assert isinstance(data, dict), "Standings fixture should be a dictionary"


def test_rosters_fixture_valid_json() -> None:
    """Test that rosters fixture contains valid JSON."""
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"
    with open(rosters_file) as f:
        data = json.load(f)

    # Should be a dictionary
    assert isinstance(data, dict), "Rosters fixture should be a dictionary"


def test_standings_fixture_structure() -> None:
    """Test that standings fixture matches NHL API schema."""
    standings_file = FIXTURES_DIR / "nhl_standings.json"
    with open(standings_file) as f:
        data = json.load(f)

    # Should have 'standings' key
    assert "standings" in data, "Standings fixture missing 'standings' key"

    # Standings should be a list
    assert isinstance(data["standings"], list), "Standings should be a list"

    # Should have teams
    assert len(data["standings"]) > 0, "Standings should contain teams"

    # Check first team structure
    team = data["standings"][0]
    required_keys = ["teamAbbrev", "divisionName", "conferenceName"]
    for key in required_keys:
        assert key in team, f"Team missing required key: {key}"

    # Team abbreviation should have 'default' key
    assert "default" in team["teamAbbrev"], "teamAbbrev missing 'default' key"


def test_rosters_fixture_structure() -> None:
    """Test that rosters fixture matches NHL API schema."""
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"
    with open(rosters_file) as f:
        data = json.load(f)

    # Should have teams
    assert len(data) > 0, "Rosters fixture should contain teams"

    # Check first team structure
    team_abbrev = list(data.keys())[0]
    roster = data[team_abbrev]

    # Should have position keys
    required_keys = ["forwards", "defensemen", "goalies"]
    for key in required_keys:
        assert key in roster, f"Roster missing required key: {key}"
        assert isinstance(roster[key], list), f"Roster {key} should be a list"


def test_standings_fixture_completeness() -> None:
    """Test that standings fixture contains all 32 NHL teams."""
    standings_file = FIXTURES_DIR / "nhl_standings.json"
    with open(standings_file) as f:
        data = json.load(f)

    # NHL has 32 teams
    assert len(data["standings"]) == 32, f"Expected 32 teams, got {len(data['standings'])}"

    # Check for unique team abbreviations
    team_abbrevs = [team["teamAbbrev"]["default"] for team in data["standings"]]
    assert len(team_abbrevs) == len(set(team_abbrevs)), "Duplicate team abbreviations found"


def test_rosters_fixture_completeness() -> None:
    """Test that rosters fixture contains data for all teams."""
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"
    with open(rosters_file) as f:
        data = json.load(f)

    # Should have data for multiple teams (at least 30)
    assert len(data) >= 30, f"Expected at least 30 teams, got {len(data)}"

    # Each team should have players
    empty_rosters = []
    for team_abbrev, roster in data.items():
        total_players = (
            len(roster.get("forwards", []))
            + len(roster.get("defensemen", []))
            + len(roster.get("goalies", []))
        )
        if total_players == 0:
            empty_rosters.append(team_abbrev)

    assert len(empty_rosters) == 0, f"Teams with empty rosters: {empty_rosters}"


def test_rosters_have_required_positions() -> None:
    """Test that each roster has forwards, defensemen, and goalies."""
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"
    with open(rosters_file) as f:
        data = json.load(f)

    for team_abbrev, roster in data.items():
        # Each team should have at least one player in each position
        assert len(roster.get("forwards", [])) > 0, f"{team_abbrev} has no forwards"
        assert len(roster.get("defensemen", [])) > 0, f"{team_abbrev} has no defensemen"
        assert len(roster.get("goalies", [])) > 0, f"{team_abbrev} has no goalies"


def test_player_data_structure() -> None:
    """Test that player data has required fields."""
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"
    with open(rosters_file) as f:
        data = json.load(f)

    # Check first team's first forward
    team_abbrev = list(data.keys())[0]
    roster = data[team_abbrev]

    if roster.get("forwards"):
        player = roster["forwards"][0]

        # Player should have firstName and lastName with default values
        assert "firstName" in player, "Player missing firstName"
        assert "lastName" in player, "Player missing lastName"

        # Names should have 'default' key
        if isinstance(player["firstName"], dict):
            assert "default" in player["firstName"], "firstName missing 'default' key"
        if isinstance(player["lastName"], dict):
            assert "default" in player["lastName"], "lastName missing 'default' key"


def test_fixture_data_consistency() -> None:
    """Test that standings and rosters have consistent team lists."""
    standings_file = FIXTURES_DIR / "nhl_standings.json"
    rosters_file = FIXTURES_DIR / "nhl_rosters.json"

    with open(standings_file) as f:
        standings_data = json.load(f)
    with open(rosters_file) as f:
        rosters_data = json.load(f)

    # Get team abbreviations from standings
    standings_teams = {team["teamAbbrev"]["default"] for team in standings_data["standings"]}

    # Get team abbreviations from rosters
    rosters_teams = set(rosters_data.keys())

    # Most teams should be in both (allowing for some variance)
    common_teams = standings_teams & rosters_teams
    assert len(common_teams) >= 30, f"Only {len(common_teams)} teams in both fixtures"
