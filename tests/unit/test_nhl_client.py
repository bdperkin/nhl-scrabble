"""Unit tests for NHL API client."""

import time
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests_cache

from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiConnectionError, NHLApiNotFoundError


class TestNHLApiClient:
    """Tests for NHLApiClient class."""

    def test_client_initialization(self) -> None:
        """Test client initialization with custom parameters."""
        client = NHLApiClient(
            timeout=15, retries=5, rate_limit_max_requests=120, rate_limit_window=60.0
        )

        assert client.timeout == 15
        assert client.retries == 5
        assert client.rate_limiter.max_requests >= 1

    def test_client_default_initialization(self) -> None:
        """Test client initialization with default parameters."""
        client = NHLApiClient()

        assert client.timeout == 10
        assert client.retries == 3
        assert client.rate_limiter.max_requests >= 1

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_teams_success(self, mock_get: Mock, sample_standings_data: dict[str, Any]) -> None:
        """Test successful team fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_standings_data
        mock_get.return_value = mock_response

        client = NHLApiClient()
        teams = client.get_teams()

        assert "TOR" in teams
        assert "MTL" in teams
        assert "EDM" in teams
        assert teams["TOR"]["division"] == "Atlantic"
        assert teams["TOR"]["conference"] == "Eastern"
        assert teams["EDM"]["division"] == "Pacific"
        assert teams["EDM"]["conference"] == "Western"

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_teams_timeout(self, mock_get: Mock) -> None:
        """Test timeout handling when fetching teams."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiConnectionError, match="after retries"):
            client.get_teams()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_teams_connection_error(self, mock_get: Mock) -> None:
        """Test connection error handling when fetching teams."""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()

        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiConnectionError, match="Unable to connect"):
            client.get_teams()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_team_roster_success(
        self, mock_get: Mock, sample_roster_data: dict[str, Any]
    ) -> None:
        """Test successful roster fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data
        mock_get.return_value = mock_response

        client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        roster = client.get_team_roster("EDM")

        assert roster is not None
        assert "forwards" in roster
        assert "defensemen" in roster
        assert "goalies" in roster
        assert len(roster["forwards"]) == 2

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_team_roster_not_found(self, mock_get: Mock) -> None:
        """Test handling of 404 response raises NHLApiNotFoundError."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiNotFoundError, match=r"Roster not found for team: XXX"):
            client.get_team_roster("XXX")

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_team_roster_retry(
        self, mock_get: Mock, sample_roster_data: dict[str, Any]
    ) -> None:
        """Test retry logic on failure."""
        import requests

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
            cache_enabled=False, retries=3, rate_limit_max_requests=1000, rate_limit_window=1.0
        )
        roster = client.get_team_roster("EDM")

        assert roster is not None
        assert mock_get.call_count == 3

    def test_context_manager(self) -> None:
        """Test that client works as a context manager."""
        with NHLApiClient() as client:
            assert client is not None
            assert hasattr(client, "session")

        # Session should be closed after exiting context
        # (This is hard to test directly, but we can verify no exceptions)

    def test_close(self) -> None:
        """Test explicit client closing."""
        client = NHLApiClient()
        client.close()
        # Verify no exceptions are raised

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_not_found_error_has_team_name(self, mock_get: Mock) -> None:
        """Test that NHLApiNotFoundError includes the team name in message."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiNotFoundError) as exc_info:
            client.get_team_roster("TOR")

        assert "TOR" in str(exc_info.value)

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_not_found_error_is_nhl_api_error(self, mock_get: Mock) -> None:
        """Test that NHLApiNotFoundError is a subclass of NHLApiError."""
        from nhl_scrabble.api.nhl_client import NHLApiError

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = NHLApiClient(cache_enabled=False)
        # Should be catchable as NHLApiError
        with pytest.raises(NHLApiError):
            client.get_team_roster("TOR")

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_not_found_error_logs_warning(self, mock_get: Mock, caplog: Any) -> None:
        """Test that 404 response logs a warning before raising."""
        import logging

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = NHLApiClient(cache_enabled=False)
        with caplog.at_level(logging.WARNING), pytest.raises(NHLApiNotFoundError):
            client.get_team_roster("TOR")

        assert "No roster data available for TOR" in caplog.text

    def test_caching_enabled_by_default(self) -> None:
        """Test that caching is enabled by default."""
        client = NHLApiClient()
        assert client.cache_enabled
        assert isinstance(client.session, requests_cache.CachedSession)
        client.close()

    def test_caching_can_be_disabled(self) -> None:
        """Test that caching can be disabled."""
        import requests

        client = NHLApiClient(cache_enabled=False)
        assert not client.cache_enabled
        assert isinstance(client.session, requests.Session)
        assert not isinstance(client.session, requests_cache.CachedSession)
        client.close()

    def test_cache_expiry_configured(self) -> None:
        """Test that cache expiry is configurable."""
        client = NHLApiClient(cache_expiry=7200)
        assert client.session.settings.expire_after.total_seconds() == 7200  # type: ignore[union-attr]
        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_clear_cache(self, mock_get: Mock, sample_standings_data: dict[str, Any]) -> None:
        """Test that clear_cache() works."""
        # Mock successful API response at the HTTP layer (allows cache to function)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_standings_data
        mock_get.return_value = mock_response

        client = NHLApiClient()

        # Make request to populate cache
        client.get_teams()

        # Check cache has entries (cache layer should have intercepted the request)
        assert client.session.cache.responses.count() > 0  # type: ignore[union-attr]

        # Clear cache
        client.clear_cache()

        # Cache should be empty
        assert client.session.cache.responses.count() == 0  # type: ignore[union-attr]

        client.close()

    def test_clear_cache_when_disabled(self, caplog: Any) -> None:
        """Test that clear_cache() handles disabled caching gracefully."""
        import logging

        client = NHLApiClient(cache_enabled=False)

        with caplog.at_level(logging.DEBUG):
            client.clear_cache()

        assert "Cache not available or caching disabled" in caplog.text
        client.close()

    def test_cache_file_created(self, tmp_path: Path) -> None:
        """Test that cache file is created."""
        import os

        # Change to temp directory
        original_dir = Path.cwd()
        os.chdir(tmp_path)

        try:
            cache_file = tmp_path / ".nhl_cache.sqlite"

            # Remove cache file if exists
            if cache_file.exists():
                cache_file.unlink()

            # Create client which should create cache
            client = NHLApiClient()

            # Cache file should be created
            assert cache_file.exists()

            client.close()
        finally:
            os.chdir(original_dir)

    def test_context_manager_closes_session(self) -> None:
        """Test that context manager closes session properly."""
        client = NHLApiClient(cache_enabled=False)

        with client:
            assert not client._closed

        # Session should be closed after exiting context
        assert client._closed

    def test_destructor_closes_session(self, caplog: Any) -> None:
        """Test that destructor closes session if not explicitly closed."""
        import logging

        with caplog.at_level(logging.WARNING):
            client = NHLApiClient(cache_enabled=False)
            # Don't close explicitly - let destructor do it
            del client

        # Should have logged warning about cleanup
        assert "not explicitly closed" in caplog.text

    def test_explicit_close_works(self) -> None:
        """Test that explicit close works correctly."""
        client = NHLApiClient(cache_enabled=False)

        assert not client._closed
        client.close()
        assert client._closed

    def test_double_close_safe(self, caplog: Any) -> None:
        """Test that double close is safe (doesn't raise errors)."""
        import logging

        client = NHLApiClient(cache_enabled=False)

        with caplog.at_level(logging.DEBUG):
            client.close()
            # Verify first close worked
            assert client._closed

            # Second close should be safe
            client.close()

        # Should only see one close message
        close_messages = [r for r in caplog.records if "session closed" in r.message.lower()]
        assert len(close_messages) == 1

    def test_atexit_cleanup_registered(self) -> None:
        """Test that atexit cleanup is registered."""
        # Create client
        client = NHLApiClient(cache_enabled=False)

        # Check that _cleanup_all is registered with atexit
        # We can't easily verify this directly, but we can check the method exists
        assert hasattr(NHLApiClient, "_cleanup_all")
        assert callable(NHLApiClient._cleanup_all)

        client.close()

    def test_weakref_tracking(self) -> None:
        """Test that instances are tracked with weak references.

        Note: In parallel test execution with pytest-xdist, counting instances
        is unreliable because other tests may create/destroy clients concurrently.
        Instead, we verify that our specific instances are tracked.
        """
        # Create clients
        client1 = NHLApiClient(cache_enabled=False)
        client2 = NHLApiClient(cache_enabled=False)

        # Verify both clients are tracked (weakrefs point to our instances)
        # Get all alive instances from weakrefs
        tracked_instances = [ref() for ref in NHLApiClient._instances if ref() is not None]

        assert client1 in tracked_instances, "client1 should be tracked in _instances"
        assert client2 in tracked_instances, "client2 should be tracked in _instances"

        # Clean up
        client1.close()
        client2.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_rate_limiting_between_successful_requests(
        self, mock_get: Mock, sample_roster_data: dict[str, Any]
    ) -> None:
        """Test that rate limiting applies between successful requests."""
        import time

        # Mock successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data
        mock_get.return_value = mock_response

        client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=10, rate_limit_window=1.0
        )

        # First request
        start = time.time()
        client.get_team_roster("EDM")

        # Second request should be delayed by rate limiting
        client.get_team_roster("TOR")
        elapsed = time.time() - start

        # Should take at least rate limiting (0.1s)
        # Add small tolerance for timing variations
        assert elapsed >= 0.09

        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_no_rate_limiting_on_first_request(
        self, mock_get: Mock, sample_roster_data: dict[str, Any]
    ) -> None:
        """Test that first request has no delay."""
        import time

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data
        mock_get.return_value = mock_response

        client = NHLApiClient(
            cache_enabled=False, rate_limit_max_requests=60, rate_limit_window=60.0
        )

        start = time.time()
        client.get_team_roster("EDM")
        elapsed = time.time() - start

        # First request should be fast (< 0.5s), not delayed by rate limiting
        assert elapsed < 0.5

        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_failed_request_doesnt_affect_rate_limiting(
        self, mock_get: Mock, sample_roster_data: dict[str, Any]
    ) -> None:
        """Test that failed requests don't affect rate limiting."""
        import time

        import requests

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
            cache_enabled=False, rate_limit_max_requests=10, rate_limit_window=1.0, retries=1
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

    def test_calculate_backoff_delay_exponential(self):
        """Test that backoff delay increases exponentially."""
        client = NHLApiClient(
            cache_enabled=False,
            backoff_factor=2.0,
            max_backoff=30.0,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )

        # Test exponential growth (with jitter tolerance)
        delay_0 = client._calculate_backoff_delay(0)
        delay_1 = client._calculate_backoff_delay(1)
        delay_2 = client._calculate_backoff_delay(2)
        delay_3 = client._calculate_backoff_delay(3)

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

        client.close()

    def test_calculate_backoff_delay_respects_max(self):
        """Test that backoff delay respects max_backoff limit."""
        client = NHLApiClient(
            cache_enabled=False,
            backoff_factor=2.0,
            max_backoff=5.0,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )

        # High attempt number would normally give huge delay
        # 1.0 * (2.0 ** 10) = 1024.0, but max_backoff = 5.0
        delay = client._calculate_backoff_delay(10)

        # Should be capped at max_backoff ± jitter (25% of 5.0 = 1.25)
        assert 0.0 <= delay <= 6.25  # max_backoff + jitter

        client.close()

    def test_calculate_backoff_delay_respects_retry_after(self):
        """Test that backoff delay respects Retry-After header."""
        client = NHLApiClient(
            cache_enabled=False,
            backoff_factor=2.0,
            max_backoff=30.0,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )

        # Retry-After value should override exponential backoff
        delay = client._calculate_backoff_delay(0, retry_after=10)
        assert delay == 10.0

        # Retry-After should still respect max_backoff
        delay_capped = client._calculate_backoff_delay(0, retry_after=50)
        assert delay_capped == 30.0  # Capped at max_backoff

        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_retry_with_exponential_backoff(self, mock_get, sample_roster_data):
        """Test that retries use exponential backoff instead of fixed delay."""
        import requests

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

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")



    def test_is_url_cached_returns_false_when_caching_disabled(self) -> None:
        """Test that _is_url_cached returns False when caching is disabled."""
        client = NHLApiClient(cache_enabled=False)
        result = client._is_url_cached("https://api-web.nhle.com/v1/roster/TOR/current")
        assert result is False
        client.close()

    def test_is_url_cached_returns_false_for_no_cache_attribute(self) -> None:
        """Test that _is_url_cached returns False when session has no cache attribute."""
        client = NHLApiClient(cache_enabled=False)
        # Regular session doesn't have 'cache' attribute
        assert not hasattr(client.session, "cache")
        result = client._is_url_cached("https://api-web.nhle.com/v1/roster/TOR/current")
        assert result is False
        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")

