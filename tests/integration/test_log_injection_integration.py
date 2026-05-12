"""Integration tests for log injection prevention."""

import logging

import pytest

from nhl_scrabble.exceptions import SSRFProtectionError
from nhl_scrabble.security.ssrf_protection import validate_url_for_ssrf


class TestLogInjectionPrevention:
    """Integration tests ensuring log injection is prevented in error paths."""

    def test_ssrf_blocked_port_logs_sanitized(self, caplog):
        """Test that SSRF protection logs sanitized port numbers."""
        with caplog.at_level(logging.WARNING):
            # Try to access allowed domain with blocked port
            # Port 3306 (MySQL) is in BLOCKED_PORTS
            malicious_url = "https://api-web.nhle.com:3306/test"
            with pytest.raises(SSRFProtectionError, match="Port 3306 is blocked"):
                validate_url_for_ssrf(malicious_url)

        # Check that logs were created
        log_messages = [record.message for record in caplog.records]
        assert len(log_messages) > 0, "Should have logged a warning"
        assert any("3306" in msg for msg in log_messages), "Should log port number"
