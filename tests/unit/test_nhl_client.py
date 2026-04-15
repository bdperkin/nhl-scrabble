"""Unit tests for NHL API client."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiConnectionError


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

        client = NHLApiClient()
        with pytest.raises(NHLApiConnectionError, match="timed out"):
            client.get_teams()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_teams_connection_error(self, mock_get: Mock) -> None:
        """Test connection error handling when fetching teams."""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()

        client = NHLApiClient()
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

        client = NHLApiClient(rate_limit_delay=0.0)  # Disable delay for testing
        roster = client.get_team_roster("EDM")

        assert roster is not None
        assert "forwards" in roster
        assert "defensemen" in roster
        assert "goalies" in roster
        assert len(roster["forwards"]) == 2

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    def test_get_team_roster_not_found(self, mock_get: Mock) -> None:
        """Test handling of 404 response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        client = NHLApiClient()
        roster = client.get_team_roster("XXX")

        assert roster is None

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

        client = NHLApiClient(retries=3, rate_limit_delay=0.0)
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
