"""Integration tests for API caching functionality."""

import time
from pathlib import Path

import pytest

from nhl_scrabble.api import NHLApiClient


@pytest.mark.integration
def test_caching_performance(tmp_path: Path) -> None:
    """Test that caching improves performance."""
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
            start = time.time()
            standings1 = client.get_teams()
            duration_cold = time.time() - start

            # Second run - warm cache
            start = time.time()
            standings2 = client.get_teams()
            duration_warm = time.time() - start

            # Warm should be much faster (at least 10x)
            assert duration_warm < duration_cold / 10, (
                f"Warm cache not faster enough: cold={duration_cold:.3f}s, "
                f"warm={duration_warm:.3f}s"
            )

            # Data should match
            assert standings1 == standings2

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
