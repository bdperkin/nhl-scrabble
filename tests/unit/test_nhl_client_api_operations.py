"""Unit tests for NHL API client operations."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiConnectionError, NHLApiNotFoundError


class TestNHLApiClientOperations:
    """Tests for NHL API client operations."""

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_get_teams_timeout(self, mock_get: Mock) -> None:
        """Test timeout handling when fetching teams."""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiConnectionError, match="after retries"):
            client.get_teams()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_get_teams_connection_error(self, mock_get: Mock) -> None:
        """Test connection error handling when fetching teams."""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()

        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiConnectionError, match="Unable to connect"):
            client.get_teams()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_get_team_roster_success(
        self,
        mock_get: Mock,
        sample_roster_data: dict[str, Any],
    ) -> None:
        """Test successful roster fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_roster_data
        mock_get.return_value = mock_response
        client = NHLApiClient(
            cache_enabled=False,
            rate_limit_max_requests=1000,
            rate_limit_window=1.0,
        )
        roster = client.get_team_roster("EDM")

        assert roster is not None
        assert "forwards" in roster
        assert "defensemen" in roster
        assert "goalies" in roster
        assert len(roster["forwards"]) == 2

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_get_team_roster_not_found(self, mock_get: Mock) -> None:
        """Test handling of 404 response raises NHLApiNotFoundError."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        client = NHLApiClient(cache_enabled=False)
        with pytest.raises(NHLApiNotFoundError, match=r"Roster not found for team: XXX"):
            client.get_team_roster("XXX")

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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
