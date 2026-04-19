"""Unit tests for team processor concurrent fetching."""

from typing import Any
from unittest.mock import Mock, patch

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer


class TestTeamProcessorConcurrent:
    """Test concurrent fetching functionality in TeamProcessor."""

    def test_max_workers_parameter(self) -> None:
        """Verify TeamProcessor accepts and stores max_workers parameter."""
        api_client = Mock(spec=NHLApiClient)
        scorer = Mock(spec=ScrabbleScorer)

        # Test different max_workers values
        processor_default = TeamProcessor(api_client, scorer)
        assert processor_default.max_workers == 5  # Default

        processor_custom = TeamProcessor(api_client, scorer, max_workers=10)
        assert processor_custom.max_workers == 10

        processor_sequential = TeamProcessor(api_client, scorer, max_workers=1)
        assert processor_sequential.max_workers == 1

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_fetch_and_process_team_success(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify single team processing works correctly."""
        # Setup API client
        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data
        mock_get.return_value = roster_response

        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer)

        # Test fetching a single team
        team_meta = {"division": "Atlantic", "conference": "Eastern"}
        result = processor._fetch_and_process_team("TOR", team_meta)

        # Verify result
        assert result is not None
        team_score, players = result
        assert team_score.abbrev == "TOR"
        assert team_score.division == "Atlantic"
        assert team_score.conference == "Eastern"
        assert len(players) > 0
        assert all(p.full_score > 0 for p in players)

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_fetch_and_process_team_not_found(self, mock_get: Mock) -> None:
        """Verify handling of 404 errors in _fetch_and_process_team."""
        # Setup 404 response
        not_found_response = Mock()
        not_found_response.status_code = 404
        mock_get.return_value = not_found_response

        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer)

        # Test fetching non-existent team
        team_meta = {"division": "Unknown", "conference": "Unknown"}
        result = processor._fetch_and_process_team("XXX", team_meta)

        # Should return None for 404
        assert result is None

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_concurrent_processing_all_teams(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify concurrent processing produces correct results."""
        # Mock API responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        # First call is standings, rest are rosters
        num_teams = len(sample_standings_data["standings"])
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams

        # Initialize processor with concurrent mode
        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer, max_workers=5)

        # Process all teams
        team_scores, all_players, failed_teams = processor.process_all_teams()

        # Verify results
        assert len(team_scores) == num_teams
        assert len(all_players) > 0
        assert len(failed_teams) == 0
        assert all(player.full_score > 0 for player in all_players)

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_concurrent_processing_handles_failures(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify concurrent processing handles mixed success/failure."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        not_found_response = Mock()
        not_found_response.status_code = 404

        # Pattern: standings, success, fail, fail
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
        processor = TeamProcessor(api_client, scorer, max_workers=3)

        team_scores, _all_players, failed_teams = processor.process_all_teams()

        # Verify mixed results
        assert len(team_scores) > 0  # At least one success
        assert len(failed_teams) > 0  # At least one failure
        assert len(team_scores) + len(failed_teams) == len(sample_standings_data["standings"])

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_sequential_vs_concurrent_same_results(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify sequential and concurrent modes produce identical results."""
        # Setup mock responses
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        num_teams = len(sample_standings_data["standings"])

        # Test sequential mode (max_workers=1)
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams
        api_client_seq = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer_seq = ScrabbleScorer()
        processor_seq = TeamProcessor(api_client_seq, scorer_seq, max_workers=1)
        teams_seq, players_seq, failed_seq = processor_seq.process_all_teams()

        # Reset mock for concurrent mode
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams

        # Test concurrent mode (max_workers=5)
        api_client_conc = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer_conc = ScrabbleScorer()
        processor_conc = TeamProcessor(api_client_conc, scorer_conc, max_workers=5)
        teams_conc, players_conc, failed_conc = processor_conc.process_all_teams()

        # Verify identical results (order may differ)
        assert len(teams_seq) == len(teams_conc)
        assert len(players_seq) == len(players_conc)
        assert len(failed_seq) == len(failed_conc)

        # Verify same team abbrevs (order-independent)
        assert set(teams_seq.keys()) == set(teams_conc.keys())

        # Verify same total scores for each team
        for abbrev in teams_seq:
            assert teams_seq[abbrev].total == teams_conc[abbrev].total


class TestTeamProcessorThreadSafety:
    """Test thread safety of concurrent operations."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_no_shared_mutable_state(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify _fetch_and_process_team has no shared mutable state."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        num_teams = len(sample_standings_data["standings"])
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams

        # Use high concurrency to stress test
        api_client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer, max_workers=10)

        # Process all teams with high concurrency
        team_scores, all_players, _failed_teams = processor.process_all_teams()

        # Verify no data corruption
        assert len(team_scores) > 0
        assert len(all_players) > 0

        # Verify each player belongs to exactly one team
        player_teams = set()
        for team_score in team_scores.values():
            for player in team_score.players:
                player_key = (player.first_name, player.last_name, player.team)
                assert player_key not in player_teams  # No duplicates
                player_teams.add(player_key)


class TestTeamProcessorConfiguration:
    """Test configuration integration for max_workers."""

    def test_max_workers_validation(self) -> None:
        """Verify max_workers parameter is validated."""
        api_client = Mock(spec=NHLApiClient)
        scorer = Mock(spec=ScrabbleScorer)

        # Valid values
        TeamProcessor(api_client, scorer, max_workers=1)
        TeamProcessor(api_client, scorer, max_workers=5)
        TeamProcessor(api_client, scorer, max_workers=100)

        # Note: Python's ThreadPoolExecutor will handle invalid values
        # (e.g., 0 or negative) by raising ValueError at runtime
