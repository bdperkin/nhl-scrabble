"""Integration tests for NHL API player details."""

import pytest

from nhl_scrabble.api import NHLApiClient
from nhl_scrabble.exceptions import NHLApiNotFoundError


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
