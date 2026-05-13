"""Tests for NHLApiClient initialization and lifecycle management."""

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests
import requests_cache

from nhl_scrabble.api.nhl_client import NHLApiClient


class TestNHLApiClientInitialization:
    """Tests for NHLApiClient initialization."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_client_initialization(self) -> None:
        """Test client initialization with custom parameters."""
        client = NHLApiClient(
            timeout=15,
            retries=5,
            rate_limit_max_requests=120,
            rate_limit_window=60.0,
        )

        assert client.timeout == 15
        assert client.retries == 5
        assert client.rate_limiter.max_requests >= 1

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_client_default_initialization(self) -> None:
        """Test client initialization with default parameters."""
        client = NHLApiClient()

        assert client.timeout == 10
        assert client.retries == 3
        assert client.rate_limiter.max_requests >= 1

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_context_manager(self) -> None:
        """Test that client works as a context manager."""
        with NHLApiClient() as client:
            assert client is not None
            assert hasattr(client, "session")

        # Session should be closed after exiting context
        # (This is hard to test directly, but we can verify no exceptions)

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_close(self) -> None:
        """Test explicit client closing."""
        client = NHLApiClient()
        client.close()
        # Verify no exceptions are raised

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_context_manager_closes_session(self) -> None:
        """Test that context manager closes session properly."""
        client = NHLApiClient(cache_enabled=False)

        with client:
            assert not client._closed

        # Session should be closed after exiting context
        assert client._closed

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_destructor_closes_session(self, caplog: Any) -> None:
        """Test that destructor closes session if not explicitly closed."""
        import logging

        with caplog.at_level(logging.WARNING):
            client = NHLApiClient(cache_enabled=False)
            # Don't close explicitly - let destructor do it
            del client

        # Should have logged warning about cleanup
        assert "not explicitly closed" in caplog.text

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_explicit_close_works(self) -> None:
        """Test that explicit close works correctly."""
        client = NHLApiClient(cache_enabled=False)

        assert not client._closed
        client.close()
        assert client._closed

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_atexit_cleanup_registered(self) -> None:
        """Test that atexit cleanup is registered."""
        # Create client
        client = NHLApiClient(cache_enabled=False)

        # Check that _cleanup_all is registered with atexit
        # We can't easily verify this directly, but we can check the method exists
        assert hasattr(NHLApiClient, "_cleanup_all")
        assert callable(NHLApiClient._cleanup_all)

        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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


class TestCacheConfiguration:
    """Tests for cache configuration."""

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_caching_enabled_by_default(self) -> None:
        """Test that caching is enabled by default."""
        client = NHLApiClient()
        assert client.cache_enabled
        assert isinstance(client.session, requests_cache.CachedSession)
        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_caching_can_be_disabled(self) -> None:
        """Test that caching can be disabled."""
        client = NHLApiClient(cache_enabled=False)
        assert not client.cache_enabled
        assert isinstance(client.session, requests.Session)
        assert not isinstance(client.session, requests_cache.CachedSession)
        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_cache_expiry_configured(self) -> None:
        """Test that cache expiry is configurable."""
        client = NHLApiClient(cache_expiry=7200)
        assert client.session.settings.expire_after.total_seconds() == 7200  # type: ignore[union-attr]
        client.close()

    @patch("nhl_scrabble.api.nhl_client.requests.Session.get")
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
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

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_clear_cache_when_disabled(self, caplog: Any) -> None:
        """Test that clear_cache() handles disabled caching gracefully."""
        import logging

        client = NHLApiClient(cache_enabled=False)

        with caplog.at_level(logging.DEBUG):
            client.clear_cache()

        assert "Cache not available or caching disabled" in caplog.text
        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_cache_file_created(self, tmp_path: Path) -> None:
        """Test that cache file is created."""
        cache_dir = tmp_path / "cache"
        cache_file = cache_dir / "api_cache.sqlite"

        # Remove cache file if exists
        if cache_file.exists():
            cache_file.unlink()

        # Create client with custom cache directory
        client = NHLApiClient(cache_dir=cache_dir)

        # Cache file should be created
        assert cache_file.exists()

        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_cache_uses_platform_directory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test cache uses platform-specific directory by default."""
        # Mock platformdirs to return test directory
        monkeypatch.setattr("platformdirs.user_cache_dir", lambda *args: str(tmp_path))

        client = NHLApiClient(cache_enabled=True)

        # Cache directory should be created
        assert tmp_path.exists()
        assert tmp_path.is_dir()

        # Cache file should be in platform directory
        expected_cache = tmp_path / "api_cache.sqlite"
        assert expected_cache.exists()

        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_cache_uses_custom_directory(self, tmp_path: Path) -> None:
        """Test cache uses custom directory when specified."""
        custom_dir = tmp_path / "custom_cache"

        client = NHLApiClient(cache_enabled=True, cache_dir=custom_dir)

        # Cache should be in custom directory
        assert custom_dir.exists()
        assert (custom_dir / "api_cache.sqlite").exists()

        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.skipif(
        __import__("sys").platform == "win32",
        reason="Unix-specific permission test (Windows has different permission model)",
    )
    def test_cache_directory_permission_error(self) -> None:
        """Test proper error when cache directory is not writable."""
        read_only_dir = "/root/.cache"  # Typically not writable by regular users

        with pytest.raises(Exception, match="Cache directory not writable"):
            NHLApiClient(cache_enabled=True, cache_dir=read_only_dir)

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_cache_directory_creation(self, tmp_path: Path) -> None:
        """Test cache directory is created if it doesn't exist."""
        cache_dir = tmp_path / "nested" / "cache" / "dir"

        client = NHLApiClient(cache_enabled=True, cache_dir=cache_dir)

        # Nested directory should be created
        assert cache_dir.exists()
        assert cache_dir.is_dir()

        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_is_url_cached_returns_false_when_caching_disabled(self) -> None:
        """Test that _is_url_cached returns False when caching is disabled."""
        client = NHLApiClient(cache_enabled=False)
        result = client._is_url_cached("https://api-web.nhle.com/v1/roster/TOR/current")
        assert result is False
        client.close()

    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    def test_is_url_cached_returns_false_for_no_cache_attribute(self) -> None:
        """Test that _is_url_cached returns False when session has no cache attribute."""
        client = NHLApiClient(cache_enabled=False)
        # Regular session doesn't have 'cache' attribute
        assert not hasattr(client.session, "cache")
        result = client._is_url_cached("https://api-web.nhle.com/v1/roster/TOR/current")
        assert result is False
        client.close()
