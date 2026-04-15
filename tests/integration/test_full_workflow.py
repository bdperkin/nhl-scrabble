"""Integration tests for full workflow."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for the complete analysis workflow."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_full_analysis_workflow(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test the complete workflow from API calls to playoff standings."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        # First call is for standings, subsequent calls are for rosters
        mock_get.side_effect = [
            standings_response,
            roster_response,
            roster_response,
            roster_response,
        ]

        # Initialize components
        api_client = NHLApiClient(rate_limit_delay=0.0)
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)
        playoff_calculator = PlayoffCalculator()

        # Process all teams
        team_scores, all_players, _failed_teams = team_processor.process_all_teams()

        # Verify results
        assert len(team_scores) > 0
        assert len(all_players) > 0
        assert all(player.full_score > 0 for player in all_players)

        # Calculate standings
        division_standings = team_processor.calculate_division_standings(team_scores)
        conference_standings = team_processor.calculate_conference_standings(team_scores)
        playoff_standings = playoff_calculator.calculate_playoff_standings(team_scores)

        # Verify standings exist
        assert len(division_standings) > 0
        assert len(conference_standings) > 0
        assert len(playoff_standings) > 0

        # Verify data integrity
        for _division_name, standing in division_standings.items():
            assert standing.total > 0
            assert len(standing.teams) > 0
            assert standing.player_count > 0

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_workflow_handles_failed_teams(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
    ) -> None:
        """Test that workflow gracefully handles teams with missing roster data."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        # First roster succeeds, others return 404
        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = {
            "forwards": [{"firstName": {"default": "Test"}, "lastName": {"default": "Player"}}],
            "defensemen": [],
            "goalies": [],
        }

        not_found_response = Mock()
        not_found_response.status_code = 404

        mock_get.side_effect = [
            standings_response,
            roster_response,
            not_found_response,
            not_found_response,
        ]

        api_client = NHLApiClient(rate_limit_delay=0.0)
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        team_scores, _all_players, failed_teams = team_processor.process_all_teams()

        # Should have some successful teams and some failures
        assert len(team_scores) > 0
        assert len(failed_teams) > 0
        assert len(team_scores) + len(failed_teams) == len(sample_standings_data["standings"])
