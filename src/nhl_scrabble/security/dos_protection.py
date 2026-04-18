"""DoS protection mechanisms for API clients.

This module provides DoS prevention through:
- Connection pool size limits (prevents resource exhaustion)
- Request timeout enforcement (prevents hanging requests)
"""

import logging

import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger(__name__)


def create_protected_session(
    max_connections: int = 10,
    max_connections_per_host: int = 5,
    pool_timeout: float = 1.0,
) -> requests.Session:
    """Create a requests Session with DoS protection via connection pool limits.

    Connection pool limits prevent resource exhaustion by:
    - Limiting total concurrent connections across all hosts
    - Limiting concurrent connections per individual host
    - Setting connection pool timeouts to fail fast when exhausted

    Args:
        max_connections: Maximum total connections in pool (default: 10)
        max_connections_per_host: Maximum connections per host (default: 5)
        pool_timeout: Seconds to wait for connection from pool (default: 1.0)

    Returns:
        Configured requests Session with connection limits

    Raises:
        ValueError: If parameters are invalid

    Examples:
        >>> session = create_protected_session(max_connections=10)
        >>> # Session automatically limits concurrent connections
        >>> response = session.get("https://api.example.com/data")
    """
    if max_connections < 1:
        msg = f"max_connections must be >= 1, got {max_connections}"
        raise ValueError(msg)
    if max_connections_per_host < 1:
        msg = f"max_connections_per_host must be >= 1, got {max_connections_per_host}"
        raise ValueError(msg)
    if max_connections_per_host > max_connections:
        msg = (
            f"max_connections_per_host ({max_connections_per_host}) cannot exceed "
            f"max_connections ({max_connections})"
        )
        raise ValueError(msg)
    if pool_timeout < 0:
        msg = f"pool_timeout must be >= 0, got {pool_timeout}"
        raise ValueError(msg)

    session = requests.Session()

    # Create adapter with connection pool limits
    adapter = HTTPAdapter(
        pool_connections=max_connections,  # Total connections to keep alive
        pool_maxsize=max_connections_per_host,  # Max connections per host
        max_retries=0,  # Don't retry at adapter level (handled by client)
        pool_block=True,  # Block when pool exhausted (rather than creating new connections)
    )

    # Mount adapter for both HTTP and HTTPS
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    logger.debug(
        f"Created protected session with max_connections={max_connections}, "
        f"max_per_host={max_connections_per_host}, pool_timeout={pool_timeout}s"
    )

    return session
