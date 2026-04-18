"""Integration tests for NHL API client SSRF protection."""

from unittest.mock import Mock, patch

import pytest

from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiError


class TestNHLApiClientSSRFProtection:
    """Integration tests for SSRF protection in NHL API client."""

    def test_client_accepts_valid_base_url(self) -> None:
        """Test that client accepts valid NHL API base URL."""
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")
        assert client.base_url == "https://api-web.nhle.com/v1"
        client.close()

    def test_client_uses_default_base_url_when_none(self) -> None:
        """Test that client uses default base URL when none provided."""
        client = NHLApiClient()
        assert client.base_url == "https://api-web.nhle.com/v1"
        client.close()

    def test_client_blocks_request_to_private_ip(self) -> None:
        """Test that client blocks requests to private IP addresses."""
        # Create client with allowed domain
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")

        # Modify base_url to point to private IP (simulating attack)
        client.base_url = "https://192.168.1.1"

        # Try to fetch teams - URL should be validated and blocked
        with pytest.raises(NHLApiError, match="Request blocked by security protection"):
            client.get_teams()

        client.close()

    def test_client_blocks_request_to_localhost(self) -> None:
        """Test that client blocks requests to localhost."""
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")

        # Simulate SSRF attack targeting localhost
        client.base_url = "http://localhost:6379"

        with pytest.raises(NHLApiError, match="Request blocked by security protection"):
            client.get_teams()

        client.close()

    def test_client_blocks_request_to_metadata_endpoint(self) -> None:
        """Test that client blocks requests to cloud metadata endpoints."""
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")

        # Simulate SSRF attack targeting AWS metadata
        client.base_url = "http://169.254.169.254"

        with pytest.raises(NHLApiError, match="Request blocked by security protection"):
            client.get_teams()

        client.close()

    def test_client_allows_valid_nhl_api_request(self) -> None:
        """Test that client allows valid NHL API requests with mocked response."""
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "standings": [
                {
                    "teamAbbrev": {"default": "TOR"},
                    "divisionName": "Atlantic",
                    "conferenceName": "Eastern",
                }
            ]
        }

        with patch.object(client.session, "get", return_value=mock_response):
            # This should succeed - valid domain and URL
            teams = client.get_teams()
            assert "TOR" in teams
            assert teams["TOR"]["division"] == "Atlantic"

        client.close()

    def test_client_ssrf_protection_on_team_roster(self) -> None:
        """Test that SSRF protection applies to team roster requests."""
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")

        # Simulate attack
        client.base_url = "http://127.0.0.1"

        with pytest.raises(NHLApiError, match="Request blocked by security protection"):
            client.get_team_roster("TOR")

        client.close()

    def test_client_blocks_non_allowed_domain(self) -> None:
        """Test that client blocks requests to non-allowed domains."""
        client = NHLApiClient(base_url="https://api-web.nhle.com/v1")

        # Simulate attack with non-allowed domain
        client.base_url = "https://evil.com"

        with pytest.raises(NHLApiError, match="Request blocked by security protection"):
            client.get_teams()

        client.close()

    def test_client_context_manager_with_ssrf(self) -> None:
        """Test that SSRF protection works with context manager usage."""
        # Should work with valid URL
        with NHLApiClient(base_url="https://api-web.nhle.com/v1") as client:
            assert client.base_url == "https://api-web.nhle.com/v1"
