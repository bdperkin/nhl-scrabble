"""NHL API client module.

This package provides the NHL API client and related utilities for fetching
team and roster data from the official NHL API.

Public API:
    - NHLApiClient: Main API client class
    - Error classes: NHLApiError, NHLApiConnectionError, NHLApiNotFoundError, NHLApiSSLError
    - Retry utilities: get_retry_after (from api.retry)
    - Error handlers: handle_http_error, handle_connection_error (from api.errors)
"""

from nhl_scrabble.api.errors import (
    handle_connection_error,
    handle_http_error,
)
from nhl_scrabble.api.nhl_client import (
    NHLApiClient,
    NHLApiConnectionError,
    NHLApiError,
    NHLApiNotFoundError,
    NHLApiSSLError,
)
from nhl_scrabble.api.retry import get_retry_after

__all__ = [
    "NHLApiClient",
    "NHLApiConnectionError",
    "NHLApiError",
    "NHLApiNotFoundError",
    "NHLApiSSLError",
    "get_retry_after",
    "handle_connection_error",
    "handle_http_error",
]
