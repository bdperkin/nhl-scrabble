"""Security module for NHL Scrabble.

This module provides security utilities including SSRF protection, log filtering, input validation,
DoS prevention (circuit breaker, connection pools), and other security-related functionality.
"""

from nhl_scrabble.security.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from nhl_scrabble.security.dos_protection import create_protected_session
from nhl_scrabble.security.log_filter import SensitiveDataFilter
from nhl_scrabble.security.ssrf_protection import (
    ALLOWED_DOMAINS,
    BLOCKED_IP_RANGES,
    BLOCKED_PORTS,
    SSRFProtectionError,
    is_ip_blocked,
    resolve_hostname,
    validate_api_base_url,
    validate_url_for_ssrf,
)

__all__ = [
    "ALLOWED_DOMAINS",
    "BLOCKED_IP_RANGES",
    "BLOCKED_PORTS",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
    "SSRFProtectionError",
    "SensitiveDataFilter",
    "create_protected_session",
    "is_ip_blocked",
    "resolve_hostname",
    "validate_api_base_url",
    "validate_url_for_ssrf",
]
