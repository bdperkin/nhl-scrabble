"""Tests for exception hierarchy."""

import pytest

from nhl_scrabble.exceptions import (
    APIError,
    CircuitBreakerOpenError,
    DataError,
    DataValidationError,
    HistoricalDataStoreError,
    NHLApiConnectionError,
    NHLApiError,
    NHLApiNotFoundError,
    NHLApiSSLError,
    NHLScrabbleError,
    SecurityError,
    SSRFProtectionError,
    StorageError,
    ValidationError,
    format_exception_message,
)


class TestExceptionHierarchy:
    """Test exception inheritance and hierarchy."""

    def test_base_exception(self) -> None:
        """Test NHLScrabbleError is base for all exceptions."""
        error = NHLScrabbleError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_validation_error_inherits_from_base_and_value_error(self) -> None:
        """Test ValidationError inherits from both NHLScrabbleError and ValueError."""
        error = ValidationError("Invalid input")
        assert isinstance(error, NHLScrabbleError)
        assert isinstance(error, ValueError)
        assert str(error) == "Invalid input"

    def test_api_error_inherits_from_base(self) -> None:
        """Test APIError inherits from NHLScrabbleError."""
        error = APIError("API failed")
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "API failed"

    def test_nhl_api_error_inherits_from_api_error(self) -> None:
        """Test NHLApiError inherits from APIError."""
        error = NHLApiError("NHL API failed")
        assert isinstance(error, APIError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "NHL API failed"

    def test_nhl_api_connection_error_inherits_from_nhl_api_error(self) -> None:
        """Test NHLApiConnectionError inherits from NHLApiError."""
        error = NHLApiConnectionError("Connection failed")
        assert isinstance(error, NHLApiError)
        assert isinstance(error, APIError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Connection failed"

    def test_nhl_api_not_found_error_inherits_from_nhl_api_error(self) -> None:
        """Test NHLApiNotFoundError inherits from NHLApiError."""
        error = NHLApiNotFoundError("Not found")
        assert isinstance(error, NHLApiError)
        assert isinstance(error, APIError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Not found"

    def test_nhl_api_ssl_error_inherits_from_nhl_api_error(self) -> None:
        """Test NHLApiSSLError inherits from NHLApiError."""
        error = NHLApiSSLError("SSL failed")
        assert isinstance(error, NHLApiError)
        assert isinstance(error, APIError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "SSL failed"

    def test_security_error_inherits_from_base(self) -> None:
        """Test SecurityError inherits from NHLScrabbleError."""
        error = SecurityError("Security violation")
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Security violation"

    def test_ssrf_protection_error_inherits_from_security_error_and_value_error(self) -> None:
        """Test SSRFProtectionError inherits from SecurityError and ValueError."""
        error = SSRFProtectionError("SSRF blocked")
        assert isinstance(error, SecurityError)
        assert isinstance(error, ValueError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "SSRF blocked"

    def test_circuit_breaker_open_error_inherits_from_security_error(self) -> None:
        """Test CircuitBreakerOpenError inherits from SecurityError."""
        error = CircuitBreakerOpenError("Circuit open")
        assert isinstance(error, SecurityError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Circuit open"

    def test_storage_error_inherits_from_base(self) -> None:
        """Test StorageError inherits from NHLScrabbleError."""
        error = StorageError("Storage failed")
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Storage failed"

    def test_historical_data_store_error_inherits_from_storage_error(self) -> None:
        """Test HistoricalDataStoreError inherits from StorageError."""
        error = HistoricalDataStoreError("Store failed")
        assert isinstance(error, StorageError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Store failed"

    def test_data_error_inherits_from_base(self) -> None:
        """Test DataError inherits from NHLScrabbleError."""
        error = DataError("Data processing failed")
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Data processing failed"

    def test_data_validation_error_inherits_from_data_error(self) -> None:
        """Test DataValidationError inherits from DataError."""
        error = DataValidationError("Data invalid")
        assert isinstance(error, DataError)
        assert isinstance(error, NHLScrabbleError)
        assert str(error) == "Data invalid"


class TestExceptionCatching:
    """Test exception catching patterns."""

    def test_catch_all_nhl_scrabble_errors(self) -> None:
        """Test catching all package errors with base exception."""
        with pytest.raises(NHLScrabbleError):
            raise ValidationError("Test")

        with pytest.raises(NHLScrabbleError):
            raise NHLApiError("Test")

        with pytest.raises(NHLScrabbleError):
            raise SecurityError("Test")

    def test_catch_specific_api_errors(self) -> None:
        """Test catching specific API error types."""
        with pytest.raises(NHLApiConnectionError):
            raise NHLApiConnectionError("Connection failed")

        with pytest.raises(NHLApiNotFoundError):
            raise NHLApiNotFoundError("Not found")

        with pytest.raises(NHLApiSSLError):
            raise NHLApiSSLError("SSL failed")

    def test_catch_validation_error_as_value_error(self) -> None:
        """Test ValidationError can be caught as ValueError for backward compatibility."""
        with pytest.raises(ValueError):  # noqa: PT011
            raise ValidationError("Invalid")

    def test_catch_ssrf_error_as_value_error(self) -> None:
        """Test SSRFProtectionError can be caught as ValueError for backward compatibility."""
        with pytest.raises(ValueError):  # noqa: PT011
            raise SSRFProtectionError("SSRF blocked")

    def test_exception_chaining(self) -> None:
        """Test exception chaining with 'from' clause."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise NHLApiError("Wrapped error") from e
        except NHLApiError as api_error:
            # Intentionally testing exception attributes in except block
            assert str(api_error) == "Wrapped error"  # noqa: PT017
            assert api_error.__cause__ is not None  # noqa: PT017
            assert isinstance(api_error.__cause__, ValueError)  # noqa: PT017
            assert str(api_error.__cause__) == "Original error"  # noqa: PT017


class TestExceptionMessages:
    """Test exception message formatting."""

    def test_exception_messages(self) -> None:
        """Test all exceptions support custom messages."""
        exceptions = [
            (NHLScrabbleError, "Base error"),
            (ValidationError, "Validation failed"),
            (APIError, "API error"),
            (NHLApiError, "NHL API error"),
            (NHLApiConnectionError, "Connection error"),
            (NHLApiNotFoundError, "Not found"),
            (NHLApiSSLError, "SSL error"),
            (SecurityError, "Security error"),
            (SSRFProtectionError, "SSRF error"),
            (CircuitBreakerOpenError, "Circuit breaker error"),
            (StorageError, "Storage error"),
            (HistoricalDataStoreError, "Historical storage error"),
            (DataError, "Data error"),
            (DataValidationError, "Data validation error"),
        ]

        for exception_class, message in exceptions:
            error = exception_class(message)
            assert str(error) == message

    def test_format_exception_message_without_context(self) -> None:
        """Test formatting exception message without context."""
        error = ValidationError("Invalid input")
        formatted = format_exception_message(error)
        assert formatted == "Invalid input"

    def test_format_exception_message_with_context(self) -> None:
        """Test formatting exception message with context."""
        error = ValidationError("Invalid input")
        formatted = format_exception_message(error, "Processing team TOR")
        assert formatted == "Processing team TOR: Invalid input"

    def test_format_exception_message_with_different_error_types(self) -> None:
        """Test formatting different exception types with context."""
        errors = [
            (NHLApiConnectionError("Connection failed"), "Fetching roster"),
            (SSRFProtectionError("SSRF blocked"), "Validating URL"),
            (DataValidationError("Invalid data"), "Processing API response"),
        ]

        for error, context in errors:
            formatted = format_exception_message(error, context)
            assert formatted == f"{context}: {error!s}"


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    def test_raise_and_catch_validation_error(self) -> None:
        """Test raising and catching ValidationError."""

        def validate_input(value: int) -> None:
            if value < 0:
                raise ValidationError("Value must be positive")

        with pytest.raises(ValidationError, match="Value must be positive"):
            validate_input(-1)

    def test_raise_and_catch_api_error_with_chaining(self) -> None:
        """Test API error with exception chaining."""

        def fetch_data() -> None:
            try:
                # Simulate network error
                raise ConnectionError("Network unreachable")  # noqa: TRY301
            except ConnectionError as e:
                # Wrap in domain-specific exception
                raise NHLApiConnectionError("Failed to connect to NHL API") from e

        with pytest.raises(NHLApiConnectionError) as exc_info:
            fetch_data()

        assert "Failed to connect to NHL API" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, ConnectionError)

    def test_catch_specific_then_general(self) -> None:
        """Test catching specific exceptions before general ones."""

        def process_data(error_type: str) -> None:
            if error_type == "not_found":
                raise NHLApiNotFoundError("Resource not found")
            if error_type == "connection":
                raise NHLApiConnectionError("Connection failed")
            raise NHLApiError("Generic error")

        # Catch specific error
        with pytest.raises(NHLApiNotFoundError):
            process_data("not_found")

        # Catch different specific error
        with pytest.raises(NHLApiConnectionError):
            process_data("connection")

        # Catch with general handler
        with pytest.raises(NHLApiError):
            process_data("other")


class TestExceptionDocumentation:
    """Test exception docstrings and documentation."""

    def test_all_exceptions_have_docstrings(self) -> None:
        """Test all exception classes have docstrings."""
        exceptions = [
            NHLScrabbleError,
            ValidationError,
            APIError,
            NHLApiError,
            NHLApiConnectionError,
            NHLApiNotFoundError,
            NHLApiSSLError,
            SecurityError,
            SSRFProtectionError,
            CircuitBreakerOpenError,
            StorageError,
            HistoricalDataStoreError,
            DataError,
            DataValidationError,
        ]

        for exception_class in exceptions:
            assert (
                exception_class.__doc__ is not None
            ), f"{exception_class.__name__} missing docstring"
            assert (
                len(exception_class.__doc__.strip()) > 0
            ), f"{exception_class.__name__} has empty docstring"

    def test_format_exception_message_has_docstring(self) -> None:
        """Test format_exception_message function has docstring."""
        assert format_exception_message.__doc__ is not None
        assert len(format_exception_message.__doc__.strip()) > 0
