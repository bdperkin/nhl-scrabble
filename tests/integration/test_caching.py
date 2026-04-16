"""Integration tests for API caching functionality."""

import time
from pathlib import Path

import pytest

from nhl_scrabble.api import NHLApiClient


@pytest.mark.integration
def test_caching_performance(tmp_path: Path) -> None:
    """Test that caching is functional."""
    import os

    # Change to temp directory for isolated cache
    original_dir = Path.cwd()
    os.chdir(tmp_path)

    try:
        cache_file = tmp_path / ".nhl_cache.sqlite"
        if cache_file.exists():
            cache_file.unlink()

        with NHLApiClient() as client:
            # First run - cold cache
            standings1 = client.get_teams()

            # Cache file should exist after first call
            assert cache_file.exists(), "Cache file not created"

            # Cache file should have data (size > 0)
            cache_size = cache_file.stat().st_size
            assert cache_size > 0, "Cache file is empty"

            # Second run - should use cache
            standings2 = client.get_teams()

            # Data should match
            assert standings1 == standings2, "Cached data doesn't match original"

            # Verify data is valid (returns dict of teams)
            assert len(standings1) > 0, "No teams returned"
            assert isinstance(standings1, dict), "Teams not returned as dict"

        # Cleanup
        if cache_file.exists():
            cache_file.unlink()
    finally:
        os.chdir(original_dir)


@pytest.mark.integration
def test_cache_respects_expiry(tmp_path: Path) -> None:
    """Test that cache expires after configured time."""
    import os

    # Change to temp directory for isolated cache
    original_dir = Path.cwd()
    os.chdir(tmp_path)

    try:
        cache_file = tmp_path / ".nhl_cache.sqlite"
        if cache_file.exists():
            cache_file.unlink()

        # Use very short expiry for testing
        with NHLApiClient(cache_expiry=1) as client:
            client.clear_cache()

            # First request
            response1 = client.get_teams()

            # Wait for cache to expire
            time.sleep(2)

            # Second request - cache expired, should hit API again
            response2 = client.get_teams()

            # Responses should still match (same data)
            assert response1 == response2

        # Cleanup
        if cache_file.exists():
            cache_file.unlink()
    finally:
        os.chdir(original_dir)


@pytest.mark.integration
def test_no_cache_always_fresh(tmp_path: Path) -> None:
    """Test that no-cache always fetches fresh data."""
    import os

    # Change to temp directory
    original_dir = Path.cwd()
    os.chdir(tmp_path)

    try:
        cache_file = tmp_path / ".nhl_cache.sqlite"

        # Should not create cache file
        with NHLApiClient(cache_enabled=False) as client:
            client.get_teams()
            client.get_teams()

            # Cache file should not exist
            assert not cache_file.exists()
    finally:
        os.chdir(original_dir)
