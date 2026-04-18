"""NHL API client module."""

from nhl_scrabble.api.nhl_client import (
    NHLApiClient,
    NHLApiConnectionError,
    NHLApiError,
    NHLApiNotFoundError,
    NHLApiSSLError,
)

__all__ = [
    "NHLApiClient",
    "NHLApiConnectionError",
    "NHLApiError",
    "NHLApiNotFoundError",
    "NHLApiSSLError",
]
