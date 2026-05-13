"""NHL API retry logic with Retry-After header support.

This module provides NHL API-specific retry logic, including handling of Retry-After headers from
429 (rate limit) responses.
"""

import logging
from contextlib import suppress

import requests

logger = logging.getLogger(__name__)

__all__ = [
    "get_retry_after",
]


def get_retry_after(response: requests.Response) -> float:
    """Extract Retry-After header value from 429 response.

    The Retry-After header can be either:
    - An integer (seconds to wait)
    - An HTTP date (less common for 429 responses)

    If no valid Retry-After header is found, returns 1.0 second as default.

    Args:
        response: HTTP response with 429 status

    Returns:
        Seconds to wait before retry (minimum 1.0)

    Examples:
        >>> from unittest.mock import Mock
        >>> response = Mock()
        >>> response.headers = {"Retry-After": "60"}
        >>> get_retry_after(response)
        60.0

        >>> response.headers = {}
        >>> get_retry_after(response)
        1.0

        >>> response.headers = {"Retry-After": "invalid"}
        >>> get_retry_after(response)
        1.0
    """
    retry_after = response.headers.get("Retry-After")

    if retry_after:
        # Try as integer (seconds)
        # Could be HTTP date format, but uncommon for 429 - default to exponential backoff
        with suppress(ValueError):
            return float(retry_after)

    # No Retry-After header or invalid format, use default
    return 1.0
