"""Unit tests for NHL API client."""

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
        client = NHLApiClient(timeout=15, retries=5, rate_limit_delay=0.5)

        assert client.timeout == 15
        assert client.retries == 5
        assert client.rate_limit_delay == 0.5

    def test_client_default_initialization(self) -> None:
        """Test client initialization with default parameters."""
        client = NHLApiClient()

        assert client.timeout == 10
        assert client.retries == 3
        assert client.rate_limit_delay == 0.3

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
        with pytest.raises(NHLApiConnectionError, match="timed out"):
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

        client = NHLApiClient(cache_enabled=False, rate_limit_delay=0.0)
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

        client = NHLApiClient(cache_enabled=False, retries=3, rate_limit_delay=0.0)
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

    @patch("nhl_scrabble.api.nhl_client.requests_cache.CachedSession.get")
    def test_clear_cache(self, mock_get: Mock, sample_standings_data: dict[str, Any]) -> None:
        """Test that clear_cache() works."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_standings_data
        mock_get.return_value = mock_response

        client = NHLApiClient()

        # Make request to populate cache
        client.get_teams()

        # Check cache has entries
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
