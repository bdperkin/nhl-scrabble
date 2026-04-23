"""Integration tests for full workflow.

This module tests complete end-to-end workflows including:
- API interaction through data processing to report generation
- Error recovery and graceful degradation
- Caching behavior and performance
- Data flow integrity across components
- Multi-component interactions
"""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.playoff_calculator import PlayoffCalculator
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.reports.conference_report import ConferenceReporter
from nhl_scrabble.reports.division_report import DivisionReporter
from nhl_scrabble.reports.playoff_report import PlayoffReporter
from nhl_scrabble.reports.team_report import TeamReporter
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

# All integration tests get 5 minute timeout
pytestmark = [
    pytest.mark.integration,
    pytest.mark.timeout(300),  # 5 minutes for integration tests
]


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
        api_client = NHLApiClient(rate_limit_max_requests=1000, rate_limit_window=1.0)
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

        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        team_scores, _all_players, failed_teams = team_processor.process_all_teams()

        # Should have some successful teams and some failures
        assert len(team_scores) > 0
        assert len(failed_teams) > 0
        assert len(team_scores) + len(failed_teams) == len(sample_standings_data["standings"])


class TestEndToEndReportGeneration:
    """Test end-to-end workflow from API to report output."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_api_to_report_generation(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test complete flow: API → scoring → processing → report generation."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        mock_get.side_effect = [
            standings_response,
            *[roster_response] * len(sample_standings_data["standings"]),
        ]

        # Initialize components
        api_client = NHLApiClient(rate_limit_max_requests=1000, rate_limit_window=1.0)
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)
        playoff_calculator = PlayoffCalculator()

        # Step 1: Fetch and process data
        team_scores, all_players, failed_teams = team_processor.process_all_teams()

        # Step 2: Calculate standings
        division_standings = team_processor.calculate_division_standings(team_scores)
        conference_standings = team_processor.calculate_conference_standings(team_scores)
        playoff_standings = playoff_calculator.calculate_playoff_standings(team_scores)

        # Step 3: Generate reports
        team_reporter = TeamReporter()
        division_reporter = DivisionReporter()
        conference_reporter = ConferenceReporter()
        playoff_reporter = PlayoffReporter()

        # Verify reports generate successfully
        team_output = team_reporter.generate(team_scores)
        division_output = division_reporter.generate(division_standings)
        conference_output = conference_reporter.generate(conference_standings)
        playoff_output = playoff_reporter.generate(playoff_standings)

        # Verify report content
        assert len(team_output) > 0
        assert len(division_output) > 0
        assert len(conference_output) > 0
        assert len(playoff_output) > 0

        # Verify data integrity across pipeline
        total_players_in_teams = sum(len(ts.players) for ts in team_scores.values())
        assert len(all_players) == total_players_in_teams
        assert len(failed_teams) == 0

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_data_flow_integrity(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test data integrity throughout the processing pipeline."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        mock_get.side_effect = [
            standings_response,
            *[roster_response] * len(sample_standings_data["standings"]),
        ]

        # Initialize components
        api_client = NHLApiClient(rate_limit_max_requests=1000, rate_limit_window=1.0)
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        # Process teams
        team_scores, all_players, _ = team_processor.process_all_teams()

        # Verify data integrity
        for team_score in team_scores.values():
            # Team total should equal sum of player scores
            player_total = sum(p.full_score for p in team_score.players)
            assert team_score.total == player_total

            # All players should have positive scores
            assert all(p.full_score > 0 for p in team_score.players)

            # Team should have metadata
            assert team_score.division is not None
            assert team_score.conference is not None

        # Verify all players are accounted for (allowing for some filtered due to validation)
        all_team_players = []
        for team_score in team_scores.values():
            all_team_players.extend(team_score.players)

        # Player counts should be very close (within 1% due to possible validation filtering)
        assert abs(len(all_team_players) - len(all_players)) <= max(1, len(all_players) * 0.01)

        # Verify most players are unique (allowing for rare duplicate names across teams)
        player_names = [f"{p.first_name} {p.last_name}" for p in all_players]
        unique_ratio = len(set(player_names)) / len(player_names)
        assert unique_ratio > 0.99  # At least 99% unique names


class TestCachingWorkflow:
    """Test caching behavior and performance improvements."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_caching_reduces_api_calls(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test that caching reduces API calls on subsequent requests."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        # Provide enough responses for first call
        num_teams = len(sample_standings_data["standings"])
        mock_get.side_effect = [
            standings_response,
            *[roster_response] * num_teams,
            # No more responses - if cache doesn't work, it will fail
        ]

        # Initialize with caching enabled
        api_client = NHLApiClient(
            cache_enabled=True,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        # First call - should hit API
        team_scores_1, _, _ = team_processor.process_all_teams()
        first_call_count = mock_get.call_count

        # Second call - should use cache (no new API calls)
        team_scores_2, _, _ = team_processor.process_all_teams()
        second_call_count = mock_get.call_count

        # Verify caching worked
        assert second_call_count == first_call_count  # No new API calls
        assert len(team_scores_1) == len(team_scores_2)  # Same results

        # Verify data integrity
        for abbrev in team_scores_1:
            assert abbrev in team_scores_2
            assert team_scores_1[abbrev].total == team_scores_2[abbrev].total


class TestErrorRecoveryWorkflow:
    """Test error recovery and resilience in workflows."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_partial_failure_recovery(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test workflow continues with partial failures."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        # 404 responses are properly handled by raising NHLApiNotFoundError
        not_found_response = Mock()
        not_found_response.status_code = 404

        # Mix successful and failed responses
        mock_get.side_effect = [
            standings_response,
            roster_response,  # Success
            not_found_response,  # Failure (404)
            roster_response,  # Success
        ]

        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        team_scores, _all_players, failed_teams = team_processor.process_all_teams()

        # Should have some successes and some failures
        assert len(team_scores) > 0  # At least some teams succeeded
        assert len(failed_teams) > 0  # At least some teams failed
        assert len(team_scores) + len(failed_teams) == len(sample_standings_data["standings"])

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_complete_failure_handling(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
    ) -> None:
        """Test handling when all roster fetches fail."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        # 404 responses are properly handled by raising NHLApiNotFoundError
        not_found_response = Mock()
        not_found_response.status_code = 404

        # All roster calls fail with 404
        num_teams = len(sample_standings_data["standings"])
        mock_get.side_effect = [
            standings_response,
            *[not_found_response] * num_teams,
        ]

        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        team_scores, all_players, failed_teams = team_processor.process_all_teams()

        # All teams should fail
        assert len(team_scores) == 0
        assert len(all_players) == 0
        assert len(failed_teams) == num_teams


class TestMultiComponentInteraction:
    """Test interactions between multiple components."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_api_processor_playoff_integration(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test integration between API client, processors, and playoff calculator."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        mock_get.side_effect = [
            standings_response,
            *[roster_response] * len(sample_standings_data["standings"]),
        ]

        # Initialize all components
        api_client = NHLApiClient(rate_limit_max_requests=1000, rate_limit_window=1.0)
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)
        playoff_calculator = PlayoffCalculator()

        # Execute full workflow
        team_scores, all_players, failed_teams = team_processor.process_all_teams()
        playoff_standings = playoff_calculator.calculate_playoff_standings(team_scores)

        # Verify component interactions
        assert len(team_scores) > 0
        assert len(all_players) > 0
        assert len(playoff_standings) > 0
        assert len(failed_teams) == 0

        # Verify playoff logic applied correctly
        # playoff_standings is a dict with 'Eastern' and 'Western' keys
        all_playoff_teams = []
        for conference_teams in playoff_standings.values():
            all_playoff_teams.extend(conference_teams)

        # Verify we have playoff teams
        assert len(all_playoff_teams) > 0

        # Verify playoff teams have correct status
        playoff_qualifiers = [pt for pt in all_playoff_teams if pt.in_playoffs]
        assert len(playoff_qualifiers) > 0

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_scorer_processor_report_integration(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test integration between scorer, processor, and report generators."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        mock_get.side_effect = [
            standings_response,
            *[roster_response] * len(sample_standings_data["standings"]),
        ]

        # Initialize components
        api_client = NHLApiClient(rate_limit_max_requests=1000, rate_limit_window=1.0)
        scorer = ScrabbleScorer()
        team_processor = TeamProcessor(api_client, scorer)

        # Process teams
        team_scores, _, _ = team_processor.process_all_teams()
        division_standings = team_processor.calculate_division_standings(team_scores)

        # Generate reports
        division_reporter = DivisionReporter()
        report_output = division_reporter.generate(division_standings)

        # Verify integration
        assert len(report_output) > 0
        assert len(division_standings) > 0

        # Verify scores from scorer made it through to reports
        for team_score in team_scores.values():
            assert all(p.full_score > 0 for p in team_score.players)
            assert team_score.total > 0
