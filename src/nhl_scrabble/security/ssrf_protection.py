"""SSRF protection utilities for NHL Scrabble.

This module provides Server-Side Request Forgery (SSRF) protection
to prevent unauthorized requests to internal/private networks,
cloud metadata endpoints, and other protected resources.

SSRF attacks occur when an attacker tricks an application into making
HTTP requests to arbitrary URLs, potentially accessing internal services,
cloud metadata, or scanning internal networks.

Example:
    >>> from nhl_scrabble.security.ssrf_protection import validate_api_base_url
    >>> url = validate_api_base_url("https://api-web.nhle.com")
    >>> # Returns validated URL if safe, raises SSRFProtectionError if blocked
"""

import ipaddress
import logging
import socket
from urllib.parse import urlparse

from nhl_scrabble.exceptions import SSRFProtectionError

logger = logging.getLogger(__name__)

__all__ = [
    "SSRFProtectionError",
    "is_ip_blocked",
    "resolve_hostname",
    "validate_api_base_url",
    "validate_url_for_ssrf",
]


# Blocked IP ranges (RFC 1918 private networks + special use)
# These ranges are commonly used for internal networks and should not
# be accessible via external API calls to prevent SSRF attacks.
BLOCKED_IP_RANGES = [
    # IPv4 ranges
    ipaddress.ip_network("0.0.0.0/8"),  # "This" network (RFC 1122)
    ipaddress.ip_network("10.0.0.0/8"),  # Private network (RFC 1918)
    ipaddress.ip_network("100.64.0.0/10"),  # Shared address space (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback (RFC 1122)
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local (RFC 3927) - AWS/Azure metadata!
    ipaddress.ip_network("172.16.0.0/12"),  # Private network (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),  # IETF protocol assignments (RFC 6890)
    ipaddress.ip_network("192.0.2.0/24"),  # Documentation (TEST-NET-1) (RFC 5737)
    ipaddress.ip_network("192.168.0.0/16"),  # Private network (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmarking (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),  # Documentation (TEST-NET-2) (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),  # Documentation (TEST-NET-3) (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    # IPv6 ranges
    ipaddress.ip_network("::1/128"),  # Loopback
    ipaddress.ip_network("::/128"),  # Unspecified address
    ipaddress.ip_network("::ffff:0:0/96"),  # IPv4-mapped IPv6
    ipaddress.ip_network("fe80::/10"),  # Link-local
    ipaddress.ip_network("fc00::/7"),  # Unique local addresses
    ipaddress.ip_network("ff00::/8"),  # Multicast
]

# Allowed domains (allowlist approach for maximum security)
# Only these domains are permitted for API requests.
# To add a new domain, it must be explicitly added to this list.
ALLOWED_DOMAINS = [
    "api-web.nhle.com",  # Primary NHL API
    "api.nhle.com",  # Alternative NHL API endpoint
]

# Blocked ports (commonly used for internal services)
# Blocking these ports prevents attackers from scanning internal
# infrastructure or accessing common internal service ports.
BLOCKED_PORTS = {
    22,  # SSH
    23,  # Telnet
    25,  # SMTP
    3306,  # MySQL
    5432,  # PostgreSQL
    6379,  # Redis
    8080,  # Common proxy/admin
    8443,  # HTTPS alternative
    9200,  # Elasticsearch
    27017,  # MongoDB
}


def is_ip_blocked(ip_address: str) -> bool:
    """Check if IP address is in blocked range.

    Validates whether an IP address (IPv4 or IPv6) falls within
    any of the blocked IP ranges, which include private networks,
    loopback addresses, and cloud metadata endpoints.

    Args:
        ip_address: IP address string to check (e.g., "192.168.1.1" or "::1").

    Returns:
        True if IP is blocked, False if IP is allowed.
        Invalid IP addresses are considered blocked (returns True).

    Example:
        >>> is_ip_blocked("8.8.8.8")  # Google DNS - public IP
        False
        >>> is_ip_blocked("192.168.1.1")  # Private network
        True
        >>> is_ip_blocked("169.254.169.254")  # AWS metadata endpoint
        True
        >>> is_ip_blocked("invalid-ip")  # Invalid IP
        True
    """
    try:
        ip = ipaddress.ip_address(ip_address)

        # Check against all blocked ranges
        return any(ip in blocked_range for blocked_range in BLOCKED_IP_RANGES)
    except ValueError:
        # Invalid IP address - block it for safety
        return True


def resolve_hostname(hostname: str) -> list[str]:
    """Resolve hostname to IP addresses.

    Performs DNS resolution to get all IP addresses associated with
    a hostname. This is used to prevent DNS rebinding attacks by
    validating the resolved IPs before making requests.

    Args:
        hostname: Hostname to resolve (e.g., "api-web.nhle.com").

    Returns:
        List of IP address strings (IPv4 and/or IPv6).

    Raises:
        SSRFProtectionError: If DNS resolution fails or hostname
            cannot be resolved.

    Example:
        >>> ips = resolve_hostname("google.com")
        >>> len(ips) > 0
        True
        >>> resolve_hostname("nonexistent-domain-12345.com")
        Traceback (most recent call last):
            ...
        SSRFProtectionError: Failed to resolve hostname 'nonexistent-domain-12345.com'
    """
    try:
        # Get all IP addresses for hostname (both IPv4 and IPv6)
        addr_info = socket.getaddrinfo(
            hostname, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )

        # Extract unique IPs (info[4][0] is always the IP address string)
        # For IPv4: (address, port)
        # For IPv6: (address, port, flow, scopeid)
        ips = list({str(info[4][0]) for info in addr_info})

        return ips
    except socket.gaierror as e:
        raise SSRFProtectionError(f"Failed to resolve hostname '{hostname}': {e}") from e


def validate_url_for_ssrf(url: str, allow_private: bool = False) -> str:
    """Validate URL for SSRF protection.

    Performs comprehensive SSRF validation including:
    - URL scheme validation (HTTP/HTTPS only)
    - Domain allowlist checking
    - Port blocklist checking
    - DNS resolution and IP blocklist checking

    This prevents attacks targeting internal networks, cloud metadata
    endpoints, or other protected resources.

    Args:
        url: URL to validate (e.g., "https://api-web.nhle.com/v1/standings").
        allow_private: Whether to allow private IP ranges (default: False).
            Should only be True for testing/development.

    Returns:
        The original URL if validation passes.

    Raises:
        SSRFProtectionError: If URL fails any validation check:
            - Invalid URL format
            - Non-HTTP/HTTPS scheme (ftp://, file://, etc.)
            - Missing hostname
            - Hostname not in allowlist
            - Port in blocklist
            - Resolves to blocked IP address

    Example:
        >>> validate_url_for_ssrf("https://api-web.nhle.com/v1/standings")
        'https://api-web.nhle.com/v1/standings'
        >>> validate_url_for_ssrf("http://localhost/api")
        Traceback (most recent call last):
            ...
        SSRFProtectionError: Hostname 'localhost' not in allowed domains list
        >>> validate_url_for_ssrf("ftp://api-web.nhle.com/file")
        Traceback (most recent call last):
            ...
        SSRFProtectionError: Only HTTP/HTTPS URLs allowed, got scheme 'ftp'
    """
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise SSRFProtectionError(f"Invalid URL format: {e}") from e

    # Check scheme (only http/https)
    if parsed.scheme not in ("http", "https"):
        raise SSRFProtectionError(f"Only HTTP/HTTPS URLs allowed, got scheme '{parsed.scheme}'")

    # Extract hostname and port
    hostname = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    if not hostname:
        raise SSRFProtectionError("URL must include hostname")

    # Check if hostname is in allowlist (preferred approach for security)
    if hostname not in ALLOWED_DOMAINS:
        logger.warning(
            f"SSRF protection blocked request to non-allowed domain: {hostname}. "
            f"Allowed domains: {', '.join(ALLOWED_DOMAINS)}"
        )
        raise SSRFProtectionError(
            f"Hostname '{hostname}' not in allowed domains list. "
            f"Allowed domains: {', '.join(ALLOWED_DOMAINS)}"
        )

    # Check for blocked ports
    if port in BLOCKED_PORTS:
        logger.warning(f"SSRF protection blocked request to blocked port: {port}")
        raise SSRFProtectionError(f"Port {port} is blocked (commonly used for internal services)")

    # Resolve hostname to IPs (prevents DNS rebinding attacks)
    ip_addresses = resolve_hostname(hostname)

    # Check all resolved IPs (important for DNS rebinding protection)
    # Even if hostname is in allowlist, verify it doesn't resolve to blocked IPs
    if not allow_private:
        for ip in ip_addresses:
            if is_ip_blocked(ip):
                logger.warning(
                    f"SSRF protection blocked request: hostname '{hostname}' "
                    f"resolves to blocked IP address: {ip}"
                )
                raise SSRFProtectionError(
                    f"Hostname '{hostname}' resolves to blocked IP address: {ip}. "
                    f"Private/internal IPs are not allowed."
                )

    return url


def validate_api_base_url(url: str) -> str:
    """Validate NHL API base URL with SSRF protection.

    This is a strict validation specifically for API base URLs.
    It enforces HTTPS (not HTTP) for security and applies all
    SSRF protections.

    Args:
        url: Base URL to validate (e.g., "https://api-web.nhle.com").

    Returns:
        Validated URL if all checks pass.

    Raises:
        SSRFProtectionError: If URL fails validation:
            - Not using HTTPS
            - Any SSRF protection check failure

    Example:
        >>> validate_api_base_url("https://api-web.nhle.com")
        'https://api-web.nhle.com'
        >>> validate_api_base_url("http://api-web.nhle.com")
        Traceback (most recent call last):
            ...
        SSRFProtectionError: API base URL must use HTTPS for security
        >>> validate_api_base_url("https://192.168.1.1")
        Traceback (most recent call last):
            ...
        SSRFProtectionError: Hostname '192.168.1.1' not in allowed domains list
    """
    # Must be HTTPS for API security
    parsed = urlparse(url)
    if parsed.scheme != "https":
        logger.warning(f"SSRF protection rejected non-HTTPS API URL: {url}")
        raise SSRFProtectionError("API base URL must use HTTPS for security")

    # Validate with SSRF protection (no private IPs allowed)
    return validate_url_for_ssrf(url, allow_private=False)
