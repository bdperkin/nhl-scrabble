"""Unit tests for NHL API client retry logic and rate limiting."""

import time
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests

from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiConnectionError
from nhl_scrabble.utils.retry import _calculate_backoff_delay


class TestRetryLogic:
    """Tests for retry logic with exponential backoff."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_get_team_roster_retry(
        self,
        mock_get: Mock,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test retry logic on failure."""
        # First two calls fail, third succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data

        mock_get.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            mock_response,
        ]

        client = NHLApiClient(
            cache_enabled=False,
            retries=3,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )
        roster = client.get_team_roster("EDM")

        assert roster is not None
        assert mock_get.call_count == 3

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_calculate_backoff_delay_exponential(self):
        """Test that backoff delay increases exponentially."""
        # Use utility function directly
        backoff_factor = 2.0
        max_backoff = 30.0

        # Test exponential growth (with jitter tolerance)
        delay_0 = _calculate_backoff_delay(0, backoff_factor=backoff_factor, max_backoff=max_backoff)
        delay_1 = _calculate_backoff_delay(1, backoff_factor=backoff_factor, max_backoff=max_backoff)
        delay_2 = _calculate_backoff_delay(2, backoff_factor=backoff_factor, max_backoff=max_backoff)
        delay_3 = _calculate_backoff_delay(3, backoff_factor=backoff_factor, max_backoff=max_backoff)

        # Attempt 0: 1.0 * (2.0 ** 0) = 1.0 ± 25%
        assert 0.75 <= delay_0 <= 1.25

        # Attempt 1: 1.0 * (2.0 ** 1) = 2.0 ± 25%
        assert 1.5 <= delay_1 <= 2.5

        # Attempt 2: 1.0 * (2.0 ** 2) = 4.0 ± 25%
        assert 3.0 <= delay_2 <= 5.0

        # Attempt 3: 1.0 * (2.0 ** 3) = 8.0 ± 25%
        assert 6.0 <= delay_3 <= 10.0

        # Verify exponential growth
        assert delay_0 < delay_1 < delay_2 < delay_3

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_calculate_backoff_delay_respects_max(self):
        """Test that backoff delay respects max_backoff limit."""
        # Use utility function directly
        backoff_factor = 2.0
        max_backoff = 5.0

        # High attempt number would normally give huge delay
        # 1.0 * (2.0 ** 10) = 1024.0, but max_backoff = 5.0
        delay = _calculate_backoff_delay(10, backoff_factor=backoff_factor, max_backoff=max_backoff)

        # Should be capped at max_backoff ± jitter (25% of 5.0 = 1.25)
        assert 0.0 <= delay <= 6.25  # max_backoff + jitter

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_calculate_backoff_delay_respects_retry_after(self):
        """Test that backoff delay respects Retry-After header."""
        # Use utility function directly
        backoff_factor = 2.0
        max_backoff = 30.0

        # Retry-After value should override exponential backoff
        delay = _calculate_backoff_delay(0, backoff_factor=backoff_factor, max_backoff=max_backoff, retry_after=10)
        assert delay == 10.0

        # Retry-After should still respect max_backoff
        delay_capped = _calculate_backoff_delay(0, backoff_factor=backoff_factor, max_backoff=max_backoff, retry_after=50)
        assert delay_capped == 30.0  # Capped at max_backoff

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_retry_with_exponential_backoff(self, mock_get, sample_roster_data):
        """Test that retries use exponential backoff instead of fixed delay."""
        client = NHLApiClient(
            cache_enabled=False,
            backoff_factor=2.0,
            max_backoff=30.0,
            retries=3,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )

        # First two attempts timeout, third succeeds
        timeout_error = requests.exceptions.Timeout("Connection timeout")
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = sample_roster_data

        mock_get.side_effect = [timeout_error, timeout_error, success_response]

        start = time.time()
        client.get_team_roster("TOR")
        elapsed = time.time() - start

        # Expected delays:
        # Attempt 0 fails: backoff ~1.0s ± 25% = 0.75-1.25s
        # Attempt 1 fails: backoff ~2.0s ± 25% = 1.5-2.5s
        # Attempt 2 succeeds: no backoff
        # Total: ~3.0s ± tolerance
        assert 2.0 <= elapsed <= 4.5  # 3.0s ± 50% for jitter variation

        # Verify 3 calls were made
        assert mock_get.call_count == 3

        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_429_rate_limit_with_retry_after(self, mock_get, sample_roster_data):
        """Test that 429 responses respect Retry-After header."""
        client = NHLApiClient(
            cache_enabled=False,
            backoff_factor=2.0,
            max_backoff=30.0,
            retries=3,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )
        # First attempt returns 429 with Retry-After, second succeeds
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "2"}

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = sample_roster_data

        mock_get.side_effect = [rate_limit_response, success_response]

        start = time.time()
        client.get_team_roster("TOR")
        elapsed = time.time() - start

        # Should have slept for Retry-After value (2 seconds)
        assert 1.9 <= elapsed <= 2.5

        # Verify 2 calls were made
        assert mock_get.call_count == 2

        client.close()


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_rate_limiting_between_successful_requests(
        self,
        mock_get: Mock,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test that rate limiting applies between successful requests."""
        # Mock successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data
        mock_response.from_cache = False  # Not cached
        mock_get.return_value = mock_response

        # Use very low rate limit: 1 request per second
        client = NHLApiClient(cache_enabled=False, rate_limit_max_requests=1, rate_limit_window=1.0)

        # First request should be fast
        start = time.time()
        client.get_team_roster("EDM")

        # Second request should wait for token refill (1 second)
        client.get_team_roster("TOR")
        elapsed = time.time() - start

        # Should take at least 0.9s (allow small tolerance)
        assert elapsed >= 0.9, f"Expected >= 0.9s, got {elapsed}s"

        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_no_rate_limiting_on_first_request(
        self,
        mock_get: Mock,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test that first request has no delay."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data
        mock_get.return_value = mock_response

        client = NHLApiClient(
            cache_enabled=False,
            rate_limit_max_requests=60,
            rate_limit_window=60.0,
        )

        start = time.time()
        client.get_team_roster("EDM")
        elapsed = time.time() - start

        # First request should be fast (< 0.5s), not delayed by rate limiting
        assert elapsed < 0.5

        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_failed_request_doesnt_affect_rate_limiting(
        self,
        mock_get: Mock,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test that failed requests don't affect rate limiting."""
        # First request succeeds
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = sample_roster_data

        # Second request fails
        mock_get.side_effect = [
            success_response,
            requests.exceptions.ConnectionError("Network error"),
        ]

        client = NHLApiClient(
            cache_enabled=False,
            rate_limit_max_requests=10,
            rate_limit_window=1.0,
            retries=1,
        )

        start = time.time()
        client.get_team_roster("EDM")

        # Failed request should not sleep for rate limiting
        with pytest.raises(NHLApiConnectionError):
            client.get_team_roster("TOR")

        elapsed = time.time() - start

        # Should not have slept for failed request
        # Total time should be less than 0.3s (one rate limit delay + tolerance)
        assert elapsed < 0.3

        client.close()
