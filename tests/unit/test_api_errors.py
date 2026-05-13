"""Tests for NHL API error handling utilities."""

import logging
from unittest.mock import Mock

import pytest
import requests

from nhl_scrabble.api.errors import handle_connection_error, handle_http_error
from nhl_scrabble.exceptions import (
    NHLApiConnectionError,
    NHLApiError,
    NHLApiNotFoundError,
    NHLApiSSLError,
)


class TestHandleHttpError:
    """Tests for handle_http_error function."""

    def test_404_error_with_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling 404 HTTP error with context string."""
        # Arrange
        response = Mock()
        response.status_code = 404
        error = requests.exceptions.HTTPError(response=response)
        context = "team TOR"

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiNotFoundError) as exc_info:
            handle_http_error(error, context)

        assert str(exc_info.value) == "Not found: team TOR"
        assert "Not found: team TOR" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_404_error_without_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling 404 HTTP error without context string."""
        # Arrange
        response = Mock()
        response.status_code = 404
        error = requests.exceptions.HTTPError(response=response)

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiNotFoundError) as exc_info:
            handle_http_error(error)

        assert str(exc_info.value) == "Not found"
        assert "Not found" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_500_error_with_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling 500 HTTP error with context string."""
        # Arrange
        response = Mock()
        response.status_code = 500
        error = requests.exceptions.HTTPError(response=response)
        context = "fetching standings"

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiError) as exc_info:
            handle_http_error(error, context)

        expected_msg = f"HTTP error: fetching standings: {error}"
        assert str(exc_info.value) == expected_msg
        assert "HTTP error: fetching standings" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_500_error_without_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling 500 HTTP error without context string."""
        # Arrange
        response = Mock()
        response.status_code = 500
        error = requests.exceptions.HTTPError(response=response)

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiError) as exc_info:
            handle_http_error(error)

        expected_msg = f"HTTP error: {error}"
        assert str(exc_info.value) == expected_msg
        assert "HTTP error:" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_http_error_with_none_response(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling HTTP error when response is None."""
        # Arrange
        error = requests.exceptions.HTTPError()
        error.response = None
        context = "network issue"

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiError) as exc_info:
            handle_http_error(error, context)

        expected_msg = f"HTTP error: network issue: {error}"
        assert str(exc_info.value) == expected_msg
        assert "HTTP error: network issue" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_403_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling 403 Forbidden HTTP error."""
        # Arrange
        response = Mock()
        response.status_code = 403
        error = requests.exceptions.HTTPError(response=response)

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiError) as exc_info:
            handle_http_error(error)

        assert "HTTP error:" in str(exc_info.value)
        assert exc_info.value.__cause__ is error


class TestHandleConnectionError:
    """Tests for handle_connection_error function."""

    def test_ssl_error_with_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling SSL error with context string."""
        # Arrange
        error = requests.exceptions.SSLError("Certificate verification failed")
        context = "fetching roster"
        retries = 3

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiSSLError) as exc_info:
            handle_connection_error(error, context, retries)

        expected_msg = f"SSL certificate verification failed fetching roster: {error}"
        assert str(exc_info.value) == expected_msg
        assert "SSL certificate verification failed fetching roster" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_ssl_error_without_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling SSL error without context string."""
        # Arrange
        error = requests.exceptions.SSLError("Certificate verification failed")
        retries = 5

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiSSLError) as exc_info:
            handle_connection_error(error, retries=retries)

        expected_msg = f"SSL certificate verification failed: {error}"
        assert str(exc_info.value) == expected_msg
        assert "SSL certificate verification failed:" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_timeout_error_with_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling Timeout error with context string."""
        # Arrange
        error = requests.exceptions.Timeout("Connection timeout")
        context = "fetching teams"
        retries = 3

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiConnectionError) as exc_info:
            handle_connection_error(error, context, retries)

        expected_msg = f"Connection error after 3 retries fetching teams: {error}"
        assert str(exc_info.value) == expected_msg
        assert "Connection error after 3 retries fetching teams" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_timeout_error_without_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling Timeout error without context string."""
        # Arrange
        error = requests.exceptions.Timeout("Connection timeout")
        retries = 5

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiConnectionError) as exc_info:
            handle_connection_error(error, retries=retries)

        expected_msg = f"Connection error after 5 retries: {error}"
        assert str(exc_info.value) == expected_msg
        assert "Connection error after 5 retries:" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_connection_error_with_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling generic ConnectionError with context string."""
        # Arrange
        error = requests.exceptions.ConnectionError("Failed to establish connection")
        context = "fetching standings"
        retries = 2

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiConnectionError) as exc_info:
            handle_connection_error(error, context, retries)

        expected_msg = f"Connection error after 2 retries fetching standings: {error}"
        assert str(exc_info.value) == expected_msg
        assert "Connection error after 2 retries fetching standings" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_connection_error_without_context(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling generic ConnectionError without context string."""
        # Arrange
        error = requests.exceptions.ConnectionError("Failed to establish connection")
        retries = 1

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiConnectionError) as exc_info:
            handle_connection_error(error, retries=retries)

        expected_msg = f"Connection error after 1 retries: {error}"
        assert str(exc_info.value) == expected_msg
        assert "Connection error after 1 retries:" in caplog.text
        assert exc_info.value.__cause__ is error

    def test_connection_error_default_retries(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test handling connection error with default retries parameter."""
        # Arrange
        error = requests.exceptions.Timeout("Request timeout")

        # Act & Assert
        with caplog.at_level(logging.ERROR), pytest.raises(NHLApiConnectionError) as exc_info:
            handle_connection_error(error)

        assert "Connection error after 3 retries:" in str(exc_info.value)
        assert exc_info.value.__cause__ is error
