"""NHL API-specific error handling and utilities.

This module provides NHL API-specific error handling utilities,
complementing the base exceptions defined in nhl_scrabble.exceptions.
"""

import logging

import requests

from nhl_scrabble.exceptions import (
    NHLApiConnectionError,
    NHLApiError,
    NHLApiNotFoundError,
    NHLApiSSLError,
)

logger = logging.getLogger(__name__)

__all__ = [
    "NHLApiError",
    "NHLApiConnectionError",
    "NHLApiNotFoundError",
    "NHLApiSSLError",
    "handle_http_error",
    "handle_connection_error",
]


def handle_http_error(
    error: requests.exceptions.HTTPError,
    context: str = "",
) -> None:
    """Handle HTTP errors and convert to appropriate NHL API exceptions.

    Args:
        error: The HTTP error to handle
        context: Optional context string (e.g., "team TOR")

    Raises:
        NHLApiNotFoundError: If 404 status code
        NHLApiError: For other HTTP errors

    Examples:
        >>> import requests
        >>> from unittest.mock import Mock
        >>> response = Mock()
        >>> response.status_code = 404
        >>> error = requests.exceptions.HTTPError(response=response)
        >>> try:
        ...     handle_http_error(error, "team TOR")
        ... except NHLApiNotFoundError as e:
        ...     print(str(e))
        Not found: team TOR
    """
    context_str = f": {context}" if context else ""

    if error.response is not None and error.response.status_code == 404:
        msg = f"Not found{context_str}"
        logger.error(msg)
        raise NHLApiNotFoundError(msg) from error

    msg = f"HTTP error{context_str}: {error}"
    logger.error(msg)
    raise NHLApiError(msg) from error


def handle_connection_error(
    error: requests.exceptions.RequestException,
    context: str = "",
    retries: int = 3,
) -> None:
    """Handle connection errors after retries exhausted.

    Args:
        error: The connection error
        context: Optional context string
        retries: Number of retries that were attempted

    Raises:
        NHLApiSSLError: If SSL certificate verification failed
        NHLApiConnectionError: For other connection errors

    Examples:
        >>> import requests
        >>> error = requests.exceptions.Timeout("Connection timeout")
        >>> try:
        ...     handle_connection_error(error, "fetching teams", retries=3)
        ... except NHLApiConnectionError as e:
        ...     print("timeout" in str(e).lower())
        True
    """
    context_str = f" {context}" if context else ""

    if isinstance(error, requests.exceptions.SSLError):
        msg = f"SSL certificate verification failed{context_str}: {error}"
        logger.error(msg)
        raise NHLApiSSLError(msg) from error

    msg = f"Connection error after {retries} retries{context_str}: {error}"
    logger.error(msg)
    raise NHLApiConnectionError(msg) from error
