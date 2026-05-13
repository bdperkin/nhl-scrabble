"""Unit tests for web fixtures module."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from nhl_scrabble.scoring import ScrabbleScorer
from nhl_scrabble.web.fixtures import _load_fixture_data, _process_fixture_data


class TestLoadFixtureData:
    """Tests for _load_fixture_data function."""

    def test_load_fixture_data_success(self) -> None:
        """Test successful loading of fixture data."""
        # Use the real fixture files that exist in the project
        loaded_standings, loaded_rosters = _load_fixture_data()

        # Verify structure of loaded data
        assert "standings" in loaded_standings
        assert isinstance(loaded_standings["standings"], list)
        assert len(loaded_standings["standings"]) > 0

        # Verify at least one team in rosters
        assert isinstance(loaded_rosters, dict)
        assert len(loaded_rosters) > 0

        # Verify a team has the expected structure
        first_team = next(iter(loaded_rosters.values()))
        assert "forwards" in first_team or "defensemen" in first_team or "goalies" in first_team

    def test_load_fixture_data_directory_not_found(self) -> None:
        """Test FileNotFoundError when fixture directory doesn't exist."""

        # Mock path existence to simulate no fixture directory
        def mock_exists(self: Path) -> bool:
            return False

        with (
            mock.patch.object(Path, "exists", mock_exists),
            pytest.raises(FileNotFoundError, match="Fixture directory not found"),
        ):
            _load_fixture_data()

    def test_load_fixture_data_standings_file_missing(self, tmp_path: Path) -> None:
        """Test FileNotFoundError when standings file is missing."""
        # Create fixture directory without standings file
        fixture_dir = tmp_path / "qa" / "web" / "tests" / "visual" / "fixtures"
        fixture_dir.mkdir(parents=True)

        # Only create rosters file
        rosters_file = fixture_dir / "nhl_rosters.json"
        rosters_file.write_text(json.dumps({}))

        # Mock to make our fixture_dir exist but standings file doesn't
        original_exists = Path.exists

        def mock_exists(self: Path) -> bool:
            path_str = str(self)
            if "nhl_standings.json" in path_str:
                return False
            if "nhl_rosters.json" in path_str:
                return path_str == str(rosters_file)
            if "fixtures" in path_str:
                return path_str == str(fixture_dir)
            return original_exists(self)

        with (
            mock.patch("nhl_scrabble.web.fixtures.Path.cwd", return_value=tmp_path),
            mock.patch.object(Path, "exists", mock_exists),
            pytest.raises(FileNotFoundError, match="Standings fixture not found"),
        ):
            _load_fixture_data()

    def test_load_fixture_data_rosters_file_missing(self, tmp_path: Path) -> None:
        """Test FileNotFoundError when rosters file is missing."""
        # Create fixture directory without rosters file
        fixture_dir = tmp_path / "qa" / "web" / "tests" / "visual" / "fixtures"
        fixture_dir.mkdir(parents=True)

        # Only create standings file
        standings_file = fixture_dir / "nhl_standings.json"
        standings_file.write_text(json.dumps({"standings": []}))

        # Mock to make our fixture_dir and standings exist but rosters doesn't
        original_exists = Path.exists

        def mock_exists(self: Path) -> bool:
            path_str = str(self)
            if "nhl_rosters.json" in path_str:
                return False
            if "nhl_standings.json" in path_str:
                return path_str == str(standings_file)
            if "fixtures" in path_str:
                return path_str == str(fixture_dir)
            return original_exists(self)

        with (
            mock.patch("nhl_scrabble.web.fixtures.Path.cwd", return_value=tmp_path),
            mock.patch.object(Path, "exists", mock_exists),
            pytest.raises(FileNotFoundError, match="Rosters fixture not found"),
        ):
            _load_fixture_data()

    def test_load_fixture_data_invalid_standings_json(self, tmp_path: Path) -> None:
        """Test JSONDecodeError when standings file has invalid JSON."""
        # Create fixture directory with invalid JSON in standings
        fixture_dir = tmp_path / "qa" / "web" / "tests" / "visual" / "fixtures"
        fixture_dir.mkdir(parents=True)

        standings_file = fixture_dir / "nhl_standings.json"
        rosters_file = fixture_dir / "nhl_rosters.json"

        # Write invalid JSON to standings file
        standings_file.write_text("{ invalid json }")
        rosters_file.write_text(json.dumps({}))

        # Mock path methods to use our test files
        original_exists = Path.exists

        def mock_exists(self: Path) -> bool:
            path_str = str(self)
            if "nhl_standings.json" in path_str:
                return path_str == str(standings_file)
            if "nhl_rosters.json" in path_str:
                return path_str == str(rosters_file)
            if "fixtures" in path_str:
                return path_str == str(fixture_dir)
            return original_exists(self)

        with (
            mock.patch("nhl_scrabble.web.fixtures.Path.cwd", return_value=tmp_path),
            mock.patch.object(Path, "exists", mock_exists),
            pytest.raises(json.JSONDecodeError),
        ):
            _load_fixture_data()

    def test_load_fixture_data_invalid_rosters_json(self, tmp_path: Path) -> None:
        """Test JSONDecodeError when rosters file has invalid JSON."""
        # Create fixture directory with invalid JSON in rosters
        fixture_dir = tmp_path / "qa" / "web" / "tests" / "visual" / "fixtures"
        fixture_dir.mkdir(parents=True)

        standings_file = fixture_dir / "nhl_standings.json"
        rosters_file = fixture_dir / "nhl_rosters.json"

        standings_file.write_text(json.dumps({"standings": []}))
        # Write invalid JSON to rosters file
        rosters_file.write_text("{ invalid json }")

        # Mock path methods to use our test files
        original_exists = Path.exists

        def mock_exists(self: Path) -> bool:
            path_str = str(self)
            if "nhl_standings.json" in path_str:
                return path_str == str(standings_file)
            if "nhl_rosters.json" in path_str:
                return path_str == str(rosters_file)
            if "fixtures" in path_str:
                return path_str == str(fixture_dir)
            return original_exists(self)

        with (
            mock.patch("nhl_scrabble.web.fixtures.Path.cwd", return_value=tmp_path),
            mock.patch.object(Path, "exists", mock_exists),
            pytest.raises(json.JSONDecodeError),
        ):
            _load_fixture_data()


class TestProcessFixtureData:
    """Tests for _process_fixture_data function."""

    def test_process_fixture_data_success(self) -> None:
        """Test successful processing of fixture data with real fixtures."""
        scorer = ScrabbleScorer()

        team_scores, all_players, _failed_teams = _process_fixture_data(scorer)

        # Verify we got some teams
        assert len(team_scores) > 0

        # Verify all players list is populated
        assert len(all_players) > 0

        # Check structure of a team
        first_team = next(iter(team_scores.values()))
        assert hasattr(first_team, "abbrev")
        assert hasattr(first_team, "name")
        assert hasattr(first_team, "division")
        assert hasattr(first_team, "conference")
        assert hasattr(first_team, "players")
        assert hasattr(first_team, "total")

        # Verify a player has correct structure
        first_player = all_players[0]
        assert hasattr(first_player, "first_name")
        assert hasattr(first_player, "last_name")
        assert hasattr(first_player, "full_name")
        assert hasattr(first_player, "first_score")
        assert hasattr(first_player, "last_score")
        assert hasattr(first_player, "full_score")
        assert first_player.full_score == first_player.first_score + first_player.last_score

    def test_process_fixture_data_missing_roster(self) -> None:
        """Test handling of teams with missing roster data."""
        standings_data = {
            "standings": [
                {
                    "teamAbbrev": {"default": "COL"},
                    "teamName": {"default": "Colorado Avalanche"},
                    "divisionName": "Central",
                    "conferenceName": "Western",
                },
                {
                    "teamAbbrev": {"default": "WSH"},
                    "teamName": {"default": "Washington Capitals"},
                    "divisionName": "Metropolitan",
                    "conferenceName": "Eastern",
                },
            ],
        }
        # Only include COL roster, WSH is missing
        rosters_data = {
            "COL": {
                "forwards": [
                    {
                        "firstName": {"default": "Ross"},
                        "lastName": {"default": "Colton"},
                    },
                ],
                "defensemen": [],
                "goalies": [],
            },
        }

        scorer = ScrabbleScorer()

        # Mock _load_fixture_data to return our test data
        with mock.patch(
            "nhl_scrabble.web.fixtures._load_fixture_data",
            return_value=(standings_data, rosters_data),
        ):
            team_scores, _all_players, failed_teams = _process_fixture_data(scorer)

        # Only COL should be processed
        assert len(team_scores) == 1
        assert "COL" in team_scores
        assert "WSH" not in team_scores

        # WSH should be in failed teams
        assert "WSH" in failed_teams

    def test_process_fixture_data_missing_player_names(self) -> None:
        """Test handling of players with missing first or last names."""
        standings_data = {
            "standings": [
                {
                    "teamAbbrev": {"default": "COL"},
                    "teamName": {"default": "Colorado Avalanche"},
                    "divisionName": "Central",
                    "conferenceName": "Western",
                },
            ],
        }
        rosters_data = {
            "COL": {
                "forwards": [
                    # Valid player
                    {
                        "firstName": {"default": "Ross"},
                        "lastName": {"default": "Colton"},
                    },
                    # Missing first name
                    {
                        "firstName": {"default": ""},
                        "lastName": {"default": "MacKinnon"},
                    },
                    # Missing last name
                    {
                        "firstName": {"default": "Nathan"},
                        "lastName": {"default": ""},
                    },
                    # Missing both
                    {
                        "firstName": {"default": ""},
                        "lastName": {"default": ""},
                    },
                ],
                "defensemen": [],
                "goalies": [],
            },
        }

        scorer = ScrabbleScorer()

        # Mock _load_fixture_data to return our test data
        with mock.patch(
            "nhl_scrabble.web.fixtures._load_fixture_data",
            return_value=(standings_data, rosters_data),
        ):
            team_scores, _all_players, _failed_teams = _process_fixture_data(scorer)

        # Only 1 valid player should be processed
        assert len(team_scores) == 1
        col_team = team_scores["COL"]
        assert len(col_team.players) == 1
        assert col_team.players[0].first_name == "Ross"
        assert col_team.players[0].last_name == "Colton"

    def test_process_fixture_data_score_calculation(self) -> None:
        """Test that scores are calculated correctly."""
        standings_data = {
            "standings": [
                {
                    "teamAbbrev": {"default": "COL"},
                    "teamName": {"default": "Colorado Avalanche"},
                    "divisionName": "Central",
                    "conferenceName": "Western",
                },
            ],
        }
        rosters_data = {
            "COL": {
                "forwards": [
                    {
                        "firstName": {"default": "Ross"},
                        "lastName": {"default": "Colton"},
                    },
                ],
                "defensemen": [],
                "goalies": [],
            },
        }

        scorer = ScrabbleScorer()

        # Mock _load_fixture_data to return our test data
        with mock.patch(
            "nhl_scrabble.web.fixtures._load_fixture_data",
            return_value=(standings_data, rosters_data),
        ):
            team_scores, all_players, _failed_teams = _process_fixture_data(scorer)

        # Verify score calculation
        player = all_players[0]
        assert player.first_name == "Ross"
        assert player.last_name == "Colton"
        assert player.full_name == "Ross Colton"

        # Calculate expected scores
        expected_first = scorer.calculate_score("Ross")
        expected_last = scorer.calculate_score("Colton")
        expected_full = expected_first + expected_last

        assert player.first_score == expected_first
        assert player.last_score == expected_last
        assert player.full_score == expected_full

        # Verify team total
        col_team = team_scores["COL"]
        assert col_team.total == expected_full

    def test_process_fixture_data_all_position_groups(self) -> None:
        """Test that all position groups (forwards, defensemen, goalies) are processed."""
        standings_data = {
            "standings": [
                {
                    "teamAbbrev": {"default": "COL"},
                    "teamName": {"default": "Colorado Avalanche"},
                    "divisionName": "Central",
                    "conferenceName": "Western",
                },
            ],
        }
        rosters_data = {
            "COL": {
                "forwards": [
                    {
                        "firstName": {"default": "Ross"},
                        "lastName": {"default": "Colton"},
                    },
                ],
                "defensemen": [
                    {
                        "firstName": {"default": "Cale"},
                        "lastName": {"default": "Makar"},
                    },
                ],
                "goalies": [
                    {
                        "firstName": {"default": "Alexandar"},
                        "lastName": {"default": "Georgiev"},
                    },
                ],
            },
        }

        scorer = ScrabbleScorer()

        # Mock _load_fixture_data to return our test data
        with mock.patch(
            "nhl_scrabble.web.fixtures._load_fixture_data",
            return_value=(standings_data, rosters_data),
        ):
            _team_scores, all_players, _failed_teams = _process_fixture_data(scorer)

        # Should have 3 players (1 forward, 1 defenseman, 1 goalie)
        assert len(all_players) == 3

        player_names = {p.full_name for p in all_players}
        assert "Ross Colton" in player_names
        assert "Cale Makar" in player_names
        assert "Alexandar Georgiev" in player_names
