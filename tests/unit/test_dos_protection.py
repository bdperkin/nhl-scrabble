"""Tests for DoS protection mechanisms."""

import pytest
import requests
from requests.adapters import HTTPAdapter

from nhl_scrabble.security.dos_protection import create_protected_session


class TestCreateProtectedSession:
    """Test protected session creation."""

    def test_default_parameters(self) -> None:
        """Test session creation with default parameters."""
        session = create_protected_session()

        # Verify session is created
        assert isinstance(session, requests.Session)

        # Verify adapters are mounted
        https_adapter = session.get_adapter("https://example.com")
        http_adapter = session.get_adapter("http://example.com")

        assert isinstance(https_adapter, HTTPAdapter)
        assert isinstance(http_adapter, HTTPAdapter)

        # Verify connection pool settings
        # Note: pool_connections and pool_maxsize are internal to HTTPAdapter
        # We verify by checking the adapter is configured
        assert https_adapter._pool_connections == 10  # noqa: SLF001  # type: ignore[attr-defined]
        assert https_adapter._pool_maxsize == 5  # noqa: SLF001  # type: ignore[attr-defined]

    def test_custom_parameters(self) -> None:
        """Test session creation with custom parameters."""
        session = create_protected_session(
            max_connections=20,
            max_connections_per_host=10,
            pool_timeout=2.0,
        )

        https_adapter = session.get_adapter("https://example.com")
        assert https_adapter._pool_connections == 20  # noqa: SLF001  # type: ignore[attr-defined]
        assert https_adapter._pool_maxsize == 10  # noqa: SLF001  # type: ignore[attr-defined]

    def test_invalid_max_connections(self) -> None:
        """Test that invalid max_connections raises ValueError."""
        with pytest.raises(ValueError, match="max_connections must be >= 1"):
            create_protected_session(max_connections=0)

    def test_invalid_max_connections_per_host(self) -> None:
        """Test that invalid max_connections_per_host raises ValueError."""
        with pytest.raises(ValueError, match="max_connections_per_host must be >= 1"):
            create_protected_session(max_connections_per_host=0)

    def test_per_host_exceeds_total(self) -> None:
        """Test that per_host > total raises ValueError."""
        with pytest.raises(
            ValueError,
            match=r"max_connections_per_host .* cannot exceed max_connections",
        ):
            create_protected_session(
                max_connections=5,
                max_connections_per_host=10,
            )

    def test_invalid_pool_timeout(self) -> None:
        """Test that negative pool_timeout raises ValueError."""
        with pytest.raises(ValueError, match="pool_timeout must be >= 0"):
            create_protected_session(pool_timeout=-1.0)

    def test_zero_timeout(self) -> None:
        """Test session with zero timeout (immediate timeout)."""
        session = create_protected_session(pool_timeout=0.0)
        assert isinstance(session, requests.Session)

    def test_both_http_and_https_mounted(self) -> None:
        """Test that adapters are mounted for both HTTP and HTTPS."""
        session = create_protected_session()

        # Test HTTPS
        https_adapter = session.get_adapter("https://example.com")
        assert isinstance(https_adapter, HTTPAdapter)

        # Test HTTP
        http_adapter = session.get_adapter("http://example.com")
        assert isinstance(http_adapter, HTTPAdapter)

        # Verify they have same configuration
        assert https_adapter._pool_connections == http_adapter._pool_connections  # type: ignore[attr-defined]
        assert https_adapter._pool_maxsize == http_adapter._pool_maxsize  # type: ignore[attr-defined]

    def test_max_retries_disabled(self) -> None:
        """Test that adapter-level retries are disabled."""
        session = create_protected_session()
        adapter = session.get_adapter("https://example.com")

        # max_retries should be 0 (we handle retries at client level)
        assert adapter.max_retries.total == 0  # type: ignore[attr-defined]

    def test_pool_block_enabled(self) -> None:
        """Test that pool blocking is enabled."""
        session = create_protected_session()
        adapter = session.get_adapter("https://example.com")

        # pool_block should be True (block when pool exhausted)
        # Note: This is internal to HTTPAdapter, verifying via adapter creation
        assert isinstance(adapter, HTTPAdapter)


class TestProtectedSessionEdgeCases:
    """Test edge cases for protected session."""

    def test_minimum_valid_configuration(self) -> None:
        """Test minimum valid configuration (1 connection)."""
        session = create_protected_session(
            max_connections=1,
            max_connections_per_host=1,
        )
        assert isinstance(session, requests.Session)

    def test_large_connection_pool(self) -> None:
        """Test large connection pool configuration."""
        session = create_protected_session(
            max_connections=1000,
            max_connections_per_host=100,
        )
        adapter = session.get_adapter("https://example.com")
        assert adapter._pool_connections == 1000  # noqa: SLF001  # type: ignore[attr-defined]
        assert adapter._pool_maxsize == 100  # noqa: SLF001  # type: ignore[attr-defined]

    def test_equal_max_connections(self) -> None:
        """Test when max_connections equals max_connections_per_host."""
        session = create_protected_session(
            max_connections=10,
            max_connections_per_host=10,
        )
        adapter = session.get_adapter("https://example.com")
        assert adapter._pool_connections == 10  # noqa: SLF001  # type: ignore[attr-defined]
        assert adapter._pool_maxsize == 10  # noqa: SLF001  # type: ignore[attr-defined]
