"""Integration tests for concurrent team processing."""

import time
from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.processors.team_processor import TeamProcessor
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

# All integration tests get 5 minute timeout
pytestmark = [
    pytest.mark.integration,
    pytest.mark.timeout(300),  # 5 minutes for integration tests
]


class TestConcurrentProcessingPerformance:
    """Integration tests for concurrent processing performance."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_concurrent_faster_than_sequential(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify concurrent fetching is faster than sequential.

        This test validates that concurrent processing provides a measurable speedup compared to
        sequential processing. The speedup should be at least 2x with max_workers=5 vs
        max_workers=1.
        """
        # Setup mock responses with realistic delay
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        num_teams = len(sample_standings_data["standings"])

        # Test sequential mode (max_workers=1) with small delay
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams
        api_client_seq = NHLApiClient(
            cache_enabled=False,
            rate_limit_delay=0.05,  # 50ms delay to simulate network
        )
        scorer_seq = ScrabbleScorer()
        processor_seq = TeamProcessor(api_client_seq, scorer_seq, max_workers=1)

        start_seq = time.perf_counter()
        teams_seq, _players_seq, _failed_seq = processor_seq.process_all_teams()
        sequential_time = time.perf_counter() - start_seq

        # Reset mock for concurrent mode
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams

        # Test concurrent mode (max_workers=5)
        api_client_conc = NHLApiClient(
            cache_enabled=False,
            rate_limit_delay=0.05,  # Same delay
        )
        scorer_conc = ScrabbleScorer()
        processor_conc = TeamProcessor(api_client_conc, scorer_conc, max_workers=5)

        start_conc = time.perf_counter()
        teams_conc, _players_conc, _failed_conc = processor_conc.process_all_teams()
        concurrent_time = time.perf_counter() - start_conc

        # Calculate speedup
        speedup = sequential_time / concurrent_time

        # Log performance metrics
        print(f"\nPerformance Results ({num_teams} teams):")  # noqa: T201
        print(f"  Sequential (max_workers=1): {sequential_time:.3f}s")  # noqa: T201
        print(f"  Concurrent (max_workers=5): {concurrent_time:.3f}s")  # noqa: T201
        print(f"  Speedup: {speedup:.2f}x")  # noqa: T201

        # Verify concurrent is faster (at least 2x with 5 workers)
        # Note: In practice with real network delays, speedup would be 3-5x
        # With mocked delays, we expect at least 2x improvement
        assert speedup >= 2.0, (
            f"Expected at least 2x speedup, got {speedup:.2f}x. "
            f"Sequential: {sequential_time:.3f}s, Concurrent: {concurrent_time:.3f}s"
        )

        # Verify same number of teams processed
        assert len(teams_seq) == len(teams_conc)

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_different_worker_counts(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test performance with different worker counts."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        num_teams = len(sample_standings_data["standings"])

        results = {}

        for worker_count in [1, 3, 5, 10]:
            # Reset mock
            mock_get.side_effect = [standings_response] + [roster_response] * num_teams

            api_client = NHLApiClient(cache_enabled=False, rate_limit_delay=0.03)
            scorer = ScrabbleScorer()
            processor = TeamProcessor(api_client, scorer, max_workers=worker_count)

            start = time.perf_counter()
            teams, _players, _failed = processor.process_all_teams()
            elapsed = time.perf_counter() - start

            results[worker_count] = {"time": elapsed, "teams": len(teams)}

        # Log results
        print("\nWorker Count Performance:")  # noqa: T201
        for workers, data in sorted(results.items()):
            print(  # noqa: T201
                f"  max_workers={workers:2d}: {data['time']:.3f}s ({data['teams']} teams)"
            )

        # Verify all produced same results
        team_counts = [data["teams"] for data in results.values()]
        assert len(set(team_counts)) == 1, "All worker counts should process same number of teams"

        # Verify increasing workers generally improves performance
        # (up to a point - diminishing returns with high worker counts)
        time_1_worker = results[1]["time"]
        time_5_workers = results[5]["time"]
        assert time_5_workers < time_1_worker, "5 workers should be faster than 1 worker"

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_concurrent_with_failures(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Verify concurrent processing handles failures gracefully."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        not_found_response = Mock()
        not_found_response.status_code = 404

        # Mix successes and failures
        num_teams = len(sample_standings_data["standings"])
        responses = [standings_response]
        responses.extend(
            not_found_response if i % 3 == 0 else roster_response for i in range(num_teams)
        )

        mock_get.side_effect = responses

        api_client = NHLApiClient(cache_enabled=False, rate_limit_delay=0.01)
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer, max_workers=5)

        # Should not raise exception despite some failures
        team_scores, all_players, failed_teams = processor.process_all_teams()

        # Verify partial success
        assert len(team_scores) > 0, "Should have some successful teams"
        assert len(failed_teams) > 0, "Should have some failed teams"
        assert len(team_scores) + len(failed_teams) == num_teams, "All teams accounted for"
        assert len(all_players) > 0, "Should have some players from successful teams"

        print(  # noqa: T201
            f"\nFailure Handling: {len(team_scores)} succeeded, {len(failed_teams)} failed"
        )

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_concurrent_progress_logging(
        self,
        mock_get: Mock,
        sample_standings_data: dict[str, Any],
        sample_roster_data: dict[str, Any],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify progress logging works correctly with concurrent fetching."""
        standings_response = Mock()
        standings_response.status_code = 200
        standings_response.json.return_value = sample_standings_data

        roster_response = Mock()
        roster_response.status_code = 200
        roster_response.json.return_value = sample_roster_data

        num_teams = len(sample_standings_data["standings"])
        mock_get.side_effect = [standings_response] + [roster_response] * num_teams

        api_client = NHLApiClient(cache_enabled=False, rate_limit_delay=0.0)
        scorer = ScrabbleScorer()
        processor = TeamProcessor(api_client, scorer, max_workers=5)

        with caplog.at_level("INFO"):
            team_scores, _players, _failed = processor.process_all_teams()

        # Verify logging includes concurrent mode message
        log_messages = [record.message for record in caplog.records]
        assert any(
            "concurrent mode" in msg.lower() for msg in log_messages
        ), "Should log concurrent mode"

        # Verify progress logging for each team
        processed_logs = [msg for msg in log_messages if "Processed" in msg]
        assert len(processed_logs) == len(
            team_scores
        ), "Should log each successfully processed team"


class TestConcurrentProcessingRealWorld:
    """Real-world concurrent processing tests (require network access)."""

    @pytest.mark.skip(reason="Requires real NHL API access")
    def test_real_api_concurrent_performance(self) -> None:
        """Test concurrent performance with real NHL API.

        This test is skipped by default as it requires network access.
        Run with: pytest -v -m "not skip" to include it.

        Expected results with real API:
        - Sequential (max_workers=1): ~10-12 seconds
        - Concurrent (max_workers=5): ~2-3 seconds
        - Speedup: 4-5x
        """
        # Sequential mode
        api_client_seq = NHLApiClient(cache_enabled=False, rate_limit_delay=0.3)
        scorer_seq = ScrabbleScorer()
        processor_seq = TeamProcessor(api_client_seq, scorer_seq, max_workers=1)

        start_seq = time.perf_counter()
        teams_seq, _players_seq, _failed_seq = processor_seq.process_all_teams()
        sequential_time = time.perf_counter() - start_seq

        # Concurrent mode
        api_client_conc = NHLApiClient(cache_enabled=False, rate_limit_delay=0.3)
        scorer_conc = ScrabbleScorer()
        processor_conc = TeamProcessor(api_client_conc, scorer_conc, max_workers=5)

        start_conc = time.perf_counter()
        teams_conc, _players_conc, _failed_conc = processor_conc.process_all_teams()
        concurrent_time = time.perf_counter() - start_conc

        speedup = sequential_time / concurrent_time

        print(f"\nReal API Performance ({len(teams_seq)} teams):")  # noqa: T201
        print(f"  Sequential: {sequential_time:.2f}s")  # noqa: T201
        print(f"  Concurrent: {concurrent_time:.2f}s")  # noqa: T201
        print(f"  Speedup: {speedup:.2f}x")  # noqa: T201

        # Real API should show at least 3x speedup
        assert speedup >= 3.0, f"Expected >=3x speedup, got {speedup:.2f}x"
        assert len(teams_seq) == len(teams_conc), "Same number of teams"
