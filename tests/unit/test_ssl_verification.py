"""Tests for SSL/TLS certificate verification enforcement."""

from unittest.mock import Mock, patch

import certifi
import pytest
import requests

from nhl_scrabble.api import NHLApiClient, NHLApiSSLError


class TestSSLVerificationEnforcement:
    """Test that SSL verification is enforced and cannot be disabled."""

    def test_ssl_verification_cannot_be_disabled(self) -> None:
        """Test that SSL verification cannot be disabled via constructor."""
        with pytest.raises(ValueError, match="SSL verification cannot be disabled"):
            NHLApiClient(verify_ssl=False)

    def test_ssl_verification_enabled_by_default(self) -> None:
        """Test that SSL verification is enabled by default."""
        client = NHLApiClient()
        # Should not raise an exception
        assert client is not None

    def test_uses_certifi_ca_bundle(self) -> None:
        """Test that client uses certifi CA bundle for SSL verification."""
        client = NHLApiClient()
        assert client.ca_bundle == certifi.where()
        assert client.ca_bundle.endswith("cacert.pem")


class TestSSLVerificationInRequests:
    """Test that SSL verification is used in actual requests."""

    def test_get_teams_uses_ssl_verification(self) -> None:
        """Test that get_teams() uses explicit SSL verification."""
        client = NHLApiClient()

        with patch.object(client.session, "get") as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "standings": [
                    {
                        "teamAbbrev": {"default": "TOR"},
                        "divisionName": "Atlantic",
                        "conferenceName": "Eastern",
                    },
                ],
            }
            mock_get.return_value = mock_response

            client.get_teams()

            # Verify verify parameter was passed with certifi CA bundle
            call_args = mock_get.call_args
            assert call_args is not None
            assert call_args.kwargs["verify"] == certifi.where()

    def test_get_team_roster_uses_ssl_verification(self) -> None:
        """Test that get_team_roster() uses explicit SSL verification."""
        client = NHLApiClient()

        with patch.object(client.session, "get") as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "forwards": [],
                "defensemen": [],
                "goalies": [],
            }
            mock_get.return_value = mock_response

            client.get_team_roster("TOR")

            # Verify verify parameter was passed with certifi CA bundle
            call_args = mock_get.call_args
            assert call_args is not None
            assert call_args.kwargs["verify"] == certifi.where()


class TestSSLErrorHandling:
    """Test that SSL errors are properly caught and logged."""

    def test_get_teams_raises_ssl_error_on_verification_failure(self) -> None:
        """Test that get_teams() raises NHLApiSSLError on SSL verification failure."""
        client = NHLApiClient()

        with patch.object(client.session, "get") as mock_get:
            # Simulate SSL verification failure
            mock_get.side_effect = requests.exceptions.SSLError(
                "certificate verify failed: self signed certificate",
            )

            with pytest.raises(NHLApiSSLError, match="SSL certificate verification failed"):
                client.get_teams()

    def test_get_team_roster_raises_ssl_error_on_verification_failure(self) -> None:
        """Test that get_team_roster() raises NHLApiSSLError on SSL verification failure."""
        client = NHLApiClient()

        with patch.object(client.session, "get") as mock_get:
            # Simulate SSL verification failure
            mock_get.side_effect = requests.exceptions.SSLError(
                "certificate verify failed: certificate has expired",
            )

            with pytest.raises(NHLApiSSLError, match="SSL certificate verification failed"):
                client.get_team_roster("TOR")

    def test_ssl_error_does_not_retry(self) -> None:
        """Test that SSL errors are not retried (permanent failure)."""
        client = NHLApiClient(retries=3)

        with patch.object(client.session, "get") as mock_get:
            # Simulate SSL verification failure
            mock_get.side_effect = requests.exceptions.SSLError("certificate verify failed")

            with pytest.raises(NHLApiSSLError):
                client.get_team_roster("TOR")

            # SSL error should not be retried - only called once
            assert mock_get.call_count == 1

    def test_ssl_error_logging(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that SSL errors are properly logged."""
        client = NHLApiClient()

        with patch.object(client.session, "get") as mock_get:
            # Simulate SSL verification failure
            mock_get.side_effect = requests.exceptions.SSLError("certificate verify failed")

            with pytest.raises(NHLApiSSLError):
                client.get_team_roster("TOR")

            # Check that error was logged
            assert any(
                "SSL certificate verification failed" in record.message for record in caplog.records
            )


class TestSSLConfigurationLogging:
    """Test that SSL configuration is logged."""

    def test_ca_bundle_path_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that CA bundle path is logged during initialization."""
        with caplog.at_level("DEBUG"):
            NHLApiClient()

        # Check that CA bundle path was logged
        assert any(
            "Using CA bundle for SSL verification" in record.message for record in caplog.records
        )
        assert any(certifi.where() in record.message for record in caplog.records)
