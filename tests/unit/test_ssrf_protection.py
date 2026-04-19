"""Unit tests for SSRF protection module."""

import socket
from unittest.mock import patch

import pytest

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


class TestIsIpBlocked:
    """Tests for is_ip_blocked() function."""

    def test_public_ipv4_not_blocked(self) -> None:
        """Test that public IPv4 addresses are not blocked."""
        # Major public DNS servers
        assert not is_ip_blocked("8.8.8.8")  # Google DNS
        assert not is_ip_blocked("1.1.1.1")  # Cloudflare DNS
        assert not is_ip_blocked("9.9.9.9")  # Quad9 DNS

        # Public web servers
        assert not is_ip_blocked("185.199.108.153")  # GitHub
        assert not is_ip_blocked("151.101.1.69")  # Reddit

    def test_private_ipv4_blocked(self) -> None:
        """Test that private IPv4 ranges (RFC 1918) are blocked."""
        # 10.0.0.0/8 - Private network
        assert is_ip_blocked("10.0.0.1")
        assert is_ip_blocked("10.255.255.255")

        # 192.168.0.0/16 - Private network
        assert is_ip_blocked("192.168.1.1")
        assert is_ip_blocked("192.168.255.255")

        # 172.16.0.0/12 - Private network
        assert is_ip_blocked("172.16.0.1")
        assert is_ip_blocked("172.31.255.255")

    def test_localhost_blocked(self) -> None:
        """Test that localhost addresses are blocked."""
        assert is_ip_blocked("127.0.0.1")
        assert is_ip_blocked("127.0.0.2")
        assert is_ip_blocked("127.255.255.255")

    def test_metadata_endpoint_blocked(self) -> None:
        """Test that cloud metadata endpoints are blocked."""
        # AWS, Azure, GCP, Oracle Cloud all use 169.254.169.254
        assert is_ip_blocked("169.254.169.254")
        # Link-local range (169.254.0.0/16)
        assert is_ip_blocked("169.254.0.1")
        assert is_ip_blocked("169.254.255.255")

    def test_special_ipv4_ranges_blocked(self) -> None:
        """Test that special use IPv4 ranges are blocked."""
        # 0.0.0.0/8 - "This" network
        # Safe: Testing SSRF protection blocks this IP, not binding to it
        assert is_ip_blocked("0.0.0.0")  # noqa: S104
        assert is_ip_blocked("0.255.255.255")

        # 100.64.0.0/10 - Shared address space
        assert is_ip_blocked("100.64.0.1")

        # 192.0.0.0/24 - IETF protocol assignments
        assert is_ip_blocked("192.0.0.1")

        # 192.0.2.0/24 - TEST-NET-1
        assert is_ip_blocked("192.0.2.1")

        # 198.51.100.0/24 - TEST-NET-2
        assert is_ip_blocked("198.51.100.1")

        # 203.0.113.0/24 - TEST-NET-3
        assert is_ip_blocked("203.0.113.1")

        # 224.0.0.0/4 - Multicast
        assert is_ip_blocked("224.0.0.1")
        assert is_ip_blocked("239.255.255.255")

        # 240.0.0.0/4 - Reserved
        assert is_ip_blocked("240.0.0.1")

        # 255.255.255.255 - Broadcast
        assert is_ip_blocked("255.255.255.255")

    def test_ipv6_localhost_blocked(self) -> None:
        """Test that IPv6 localhost is blocked."""
        assert is_ip_blocked("::1")  # IPv6 loopback

    def test_ipv6_special_ranges_blocked(self) -> None:
        """Test that special IPv6 ranges are blocked."""
        # Unspecified address
        assert is_ip_blocked("::")

        # IPv4-mapped IPv6
        assert is_ip_blocked("::ffff:127.0.0.1")

        # Link-local
        assert is_ip_blocked("fe80::1")
        assert is_ip_blocked("febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff")

        # Unique local addresses (fc00::/7)
        assert is_ip_blocked("fc00::1")
        assert is_ip_blocked("fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")

        # Multicast (ff00::/8)
        assert is_ip_blocked("ff00::1")
        assert is_ip_blocked("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")

    def test_invalid_ip_blocked(self) -> None:
        """Test that invalid IP addresses are blocked."""
        assert is_ip_blocked("not an ip")
        assert is_ip_blocked("999.999.999.999")
        assert is_ip_blocked("192.168.1.999")
        assert is_ip_blocked("192.168")
        assert is_ip_blocked("")
        assert is_ip_blocked("gggg::1")  # Invalid IPv6


class TestResolveHostname:
    """Tests for resolve_hostname() function."""

    def test_resolve_public_domain(self) -> None:
        """Test resolving a well-known public domain."""
        ips = resolve_hostname("google.com")
        assert len(ips) > 0
        # Should return valid IP addresses (IPv4 or IPv6)
        assert all("." in ip or ":" in ip for ip in ips)

    def test_resolve_localhost(self) -> None:
        """Test resolving localhost."""
        ips = resolve_hostname("localhost")
        # Should resolve to 127.0.0.1 or ::1
        assert any(ip in ["127.0.0.1", "::1"] for ip in ips)

    def test_resolve_nonexistent_domain(self) -> None:
        """Test that nonexistent domains raise SSRFProtectionError."""
        # Mock socket.getaddrinfo to raise gaierror (DNS resolution failure)
        with patch("socket.getaddrinfo") as mock_getaddrinfo:
            mock_getaddrinfo.side_effect = socket.gaierror(-2, "Name or service not known")
            with pytest.raises(SSRFProtectionError, match="Failed to resolve hostname"):
                resolve_hostname("this-domain-definitely-does-not-exist-12345.com")


class TestValidateUrlForSsrf:
    """Tests for validate_url_for_ssrf() function."""

    def test_valid_nhl_api_url(self) -> None:
        """Test that valid NHL API URLs pass validation."""
        url = "https://api-web.nhle.com/v1/standings/now"
        result = validate_url_for_ssrf(url)
        assert result == url

    def test_alternative_nhl_api_url(self) -> None:
        """Test that alternative NHL API domain passes validation."""
        url = "https://api.nhle.com/v1/teams"
        result = validate_url_for_ssrf(url)
        assert result == url

    def test_non_allowed_domain_blocked(self) -> None:
        """Test that non-allowed domains are blocked."""
        with pytest.raises(SSRFProtectionError, match="not in allowed domains"):
            validate_url_for_ssrf("https://evil.com/api")

    def test_allowed_domains_constant(self) -> None:
        """Test that ALLOWED_DOMAINS constant is correctly configured."""
        # Check expected domains are in the allowed list (membership test, not substring match)
        expected_domains = {"api-web.nhle.com", "api.nhle.com"}
        for domain in expected_domains:
            assert domain in ALLOWED_DOMAINS, f"{domain} should be in ALLOWED_DOMAINS"
        assert len(ALLOWED_DOMAINS) >= 2

    def test_blocked_ip_ranges_constant(self) -> None:
        """Test that BLOCKED_IP_RANGES constant includes expected ranges."""
        # Should include at least the major private networks
        assert len(BLOCKED_IP_RANGES) >= 20  # Both IPv4 and IPv6 ranges

    def test_blocked_ports_constant(self) -> None:
        """Test that BLOCKED_PORTS constant includes common service ports."""
        expected_ports = {22, 23, 25, 3306, 5432, 6379, 8080, 8443, 9200, 27017}
        assert expected_ports.issubset(BLOCKED_PORTS)

    def test_private_ip_url_blocked(self) -> None:
        """Test that URLs with private IPs are blocked (even as hostname)."""
        # Note: Direct IP addresses won't be in ALLOWED_DOMAINS
        with pytest.raises(SSRFProtectionError, match="not in allowed domains"):
            validate_url_for_ssrf("http://192.168.1.1/api")

    def test_localhost_url_blocked(self) -> None:
        """Test that localhost URLs are blocked."""
        with pytest.raises(SSRFProtectionError, match="not in allowed domains"):
            validate_url_for_ssrf("http://localhost/api")

    def test_metadata_endpoint_blocked(self) -> None:
        """Test that cloud metadata endpoints are blocked."""
        with pytest.raises(SSRFProtectionError, match="not in allowed domains"):
            validate_url_for_ssrf("http://169.254.169.254/latest/meta-data")

    def test_non_http_scheme_blocked(self) -> None:
        """Test that non-HTTP/HTTPS schemes are blocked."""
        # Even for allowed domains, only HTTP/HTTPS should work
        with pytest.raises(SSRFProtectionError, match="Only HTTP/HTTPS"):
            validate_url_for_ssrf("ftp://api-web.nhle.com/file")

        with pytest.raises(SSRFProtectionError, match="Only HTTP/HTTPS"):
            validate_url_for_ssrf("file:///etc/passwd")

        with pytest.raises(SSRFProtectionError, match="Only HTTP/HTTPS"):
            validate_url_for_ssrf("gopher://api-web.nhle.com/")

    def test_url_without_hostname_blocked(self) -> None:
        """Test that URLs without hostname are blocked."""
        with pytest.raises(SSRFProtectionError, match="must include hostname"):
            validate_url_for_ssrf("http://")

    def test_url_with_standard_https_port(self) -> None:
        """Test that standard HTTPS port (443) is allowed."""
        # Explicit port 443 should work for HTTPS
        url = "https://api-web.nhle.com:443/v1/standings"
        result = validate_url_for_ssrf(url)
        assert result == url

    def test_url_with_standard_http_port(self) -> None:
        """Test that standard HTTP port (80) is allowed."""
        # Port 80 is not in BLOCKED_PORTS
        url = "http://api-web.nhle.com:80/v1/standings"
        result = validate_url_for_ssrf(url)
        assert result == url


class TestValidateApiBaseUrl:
    """Tests for validate_api_base_url() function."""

    def test_valid_https_api_url(self) -> None:
        """Test that valid HTTPS API base URL passes."""
        url = "https://api-web.nhle.com/v1"
        result = validate_api_base_url(url)
        assert result == url

    def test_valid_https_api_url_without_path(self) -> None:
        """Test that HTTPS API URL without path passes."""
        url = "https://api-web.nhle.com"
        result = validate_api_base_url(url)
        assert result == url

    def test_http_api_url_rejected(self) -> None:
        """Test that HTTP (not HTTPS) is rejected for API base URL."""
        with pytest.raises(SSRFProtectionError, match="must use HTTPS"):
            validate_api_base_url("http://api-web.nhle.com")

    def test_private_ip_api_url_blocked(self) -> None:
        """Test that private IP API base URL is blocked."""
        with pytest.raises(SSRFProtectionError):
            validate_api_base_url("https://192.168.1.1")

    def test_localhost_api_url_blocked(self) -> None:
        """Test that localhost API base URL is blocked."""
        with pytest.raises(SSRFProtectionError):
            validate_api_base_url("https://localhost")

    def test_metadata_endpoint_api_url_blocked(self) -> None:
        """Test that metadata endpoint API base URL is blocked."""
        with pytest.raises(SSRFProtectionError):
            validate_api_base_url("http://169.254.169.254")

    def test_non_allowed_domain_api_url_blocked(self) -> None:
        """Test that non-allowed domain is blocked for API base URL."""
        with pytest.raises(SSRFProtectionError, match="not in allowed domains"):
            validate_api_base_url("https://evil.com")


class TestSSRFProtectionError:
    """Tests for SSRFProtectionError exception."""

    def test_exception_is_value_error(self) -> None:
        """Test that SSRFProtectionError is a ValueError."""
        assert issubclass(SSRFProtectionError, ValueError)

    def test_exception_message(self) -> None:
        """Test that exception message is preserved."""
        message = "Test error message"
        error = SSRFProtectionError(message)
        assert str(error) == message

    def test_exception_can_be_raised(self) -> None:
        """Test that exception can be raised and caught."""
        with pytest.raises(SSRFProtectionError, match="test"):
            raise SSRFProtectionError("test")
