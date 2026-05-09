"""Integration tests for NHL API player details."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from nhl_scrabble.api import NHLApiClient
from nhl_scrabble.exceptions import (
    NHLApiConnectionError,
    NHLApiError,
    NHLApiNotFoundError,
    NHLApiSSLError,
)


@pytest.mark.slow
def test_get_player_details_success() -> None:
    """Test fetching player details from NHL API.

    This test makes a real API call to the NHL API. It's marked as slow to allow skipping during
    quick test runs.
    """
    client = NHLApiClient()
    try:
        # Use Connor McDavid's player ID (known to exist)
        data = client.get_player_details(8478402)

        # Verify required fields are present
        assert "playerId" in data
        assert "firstName" in data
        assert "lastName" in data
        assert data["playerId"] == 8478402

        # Verify some expected data
        assert data["firstName"]["default"] == "Connor"
        assert data["lastName"]["default"] == "McDavid"

    finally:
        client.close()


@pytest.mark.slow
def test_get_player_details_not_found() -> None:
    """Test 404 for non-existent player.

    This test makes a real API call to verify error handling. It's marked as slow to allow skipping
    during quick test runs.
    """
    client = NHLApiClient()
    try:
        # Use an invalid player ID that should not exist
        with pytest.raises(NHLApiNotFoundError):
            client.get_player_details(9999999)
    finally:
        client.close()


def test_get_player_details_cached() -> None:
    """Test that player details are cached properly."""
    client = NHLApiClient(cache_enabled=True)
    try:
        # First call should make an API request
        data1 = client.get_player_details(8478402)

        # Second call should use cache
        data2 = client.get_player_details(8478402)

        # Data should be identical
        assert data1 == data2

        # Verify cache is being used
        cache_info = client.get_cache_info()
        assert cache_info["enabled"] is True

    finally:
        client.close()


def test_get_player_details_http_error() -> None:
    """Test handling of HTTP errors (non-404)."""
    client = NHLApiClient()

    # Mock session to return 500 error
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    with (
        patch.object(client.session, "get", return_value=mock_response),
        pytest.raises(
            NHLApiError,
            match="HTTP error",
        ),
    ):
        client.get_player_details(8478402)

    client.close()


def test_get_player_details_connection_error() -> None:
    """Test handling of connection errors."""
    client = NHLApiClient()

    # Mock session to raise connection error
    with (
        patch.object(
            client.session,
            "get",
            side_effect=requests.exceptions.ConnectionError("Connection failed"),
        ),
        pytest.raises(NHLApiConnectionError, match="Unable to connect"),
    ):
        client.get_player_details(8478402)

    client.close()


def test_get_player_details_timeout_error() -> None:
    """Test handling of timeout errors."""
    client = NHLApiClient()

    # Mock session to raise timeout error
    with (
        patch.object(
            client.session,
            "get",
            side_effect=requests.exceptions.Timeout("Request timed out"),
        ),
        pytest.raises(NHLApiConnectionError, match="Unable to connect"),
    ):
        client.get_player_details(8478402)

    client.close()


def test_get_player_details_ssl_error() -> None:
    """Test handling of SSL certificate verification errors."""
    client = NHLApiClient()

    # Mock session to raise SSL error
    with (
        patch.object(
            client.session,
            "get",
            side_effect=requests.exceptions.SSLError("Certificate verification failed"),
        ),
        pytest.raises(NHLApiSSLError, match="SSL certificate verification failed"),
    ):
        client.get_player_details(8478402)

    client.close()


def test_get_player_details_invalid_response() -> None:
    """Test handling of invalid API response (missing required fields)."""
    client = NHLApiClient()

    # Mock session to return invalid response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid": "data"}  # Missing required fields

    with (
        patch.object(client.session, "get", return_value=mock_response),
        pytest.raises(
            NHLApiError,
            match="Invalid API response",
        ),
    ):
        client.get_player_details(8478402)

    client.close()
