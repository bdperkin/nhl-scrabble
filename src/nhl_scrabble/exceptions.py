"""Custom exception hierarchy for NHL Scrabble Score Analyzer.

This module defines a consistent exception hierarchy for all NHL Scrabble errors,
providing clear error messages and proper categorization for different error types.

The exception hierarchy follows the pattern:
    NHLScrabbleError (base)
    ├── ValidationError (input validation)
    ├── APIError (API communication)
    │   ├── NHLApiError (NHL API specific)
    │   │   ├── NHLApiConnectionError
    │   │   ├── NHLApiNotFoundError
    │   │   └── NHLApiSSLError
    ├── SecurityError (security violations)
    │   ├── SSRFProtectionError
    │   └── CircuitBreakerOpenError
    ├── StorageError (data storage)
    │   └── HistoricalDataStoreError
    └── DataError (data processing)
        └── DataValidationError

All exceptions include:
    - Clear, user-friendly error messages
    - Proper exception chaining (from/raise)
    - Context information when available
"""

class NHLScrabbleError(Exception):
    """Base exception for all NHL Scrabble errors.

    All custom exceptions in the NHL Scrabble package inherit from this base class,
    making it easy to catch all package-specific errors.

    Examples:
        >>> raise NHLScrabbleError("Something went wrong")
        Traceback (most recent call last):
        NHLScrabbleError: Something went wrong
    """


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Validation Errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ValidationError(NHLScrabbleError, ValueError):
    """Raised when input validation fails.

    This exception is raised when user input or configuration values fail
    validation checks. It provides clear, actionable error messages to help
    users correct their input.

    Inherits from both NHLScrabbleError and ValueError for backward compatibility
    with code that catches ValueError.

    Examples:
        >>> raise ValidationError("top_players must be between 1 and 100, got 999")
        Traceback (most recent call last):
        ValidationError: top_players must be between 1 and 100, got 999
    """


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API Errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class APIError(NHLScrabbleError):
    """Base exception for API communication errors.

    Raised when there are issues communicating with external APIs,
    including network errors, timeouts, and invalid responses.

    Examples:
        >>> raise APIError("Failed to connect to API")
        Traceback (most recent call last):
        APIError: Failed to connect to API
    """


class NHLApiError(APIError):
    """Base exception for NHL API errors.

    Raised for NHL API-specific errors including HTTP errors,
    invalid responses, and API-level failures.

    Examples:
        >>> raise NHLApiError("NHL API returned invalid data")
        Traceback (most recent call last):
        NHLApiError: NHL API returned invalid data
    """


class NHLApiConnectionError(NHLApiError):
    """Raised when unable to connect to the NHL API.

    This includes network timeouts, connection refused, DNS failures,
    and other connection-related issues.

    Examples:
        >>> raise NHLApiConnectionError("Unable to connect to NHL API after 3 retries")
        Traceback (most recent call last):
        NHLApiConnectionError: Unable to connect to NHL API after 3 retries
    """


class NHLApiNotFoundError(NHLApiError):
    """Raised when the requested resource is not found (404).

    Indicates that the NHL API returned a 404 status code,
    meaning the requested resource (team, roster, etc.) does not exist.

    Examples:
        >>> raise NHLApiNotFoundError("Roster not found for team: XYZ")
        Traceback (most recent call last):
        NHLApiNotFoundError: Roster not found for team: XYZ
    """


class NHLApiSSLError(NHLApiError):
    """Raised when SSL/TLS certificate verification fails.

    Indicates a problem with SSL/TLS certificate validation,
    which could be a security issue or a configuration problem.

    Examples:
        >>> raise NHLApiSSLError("SSL certificate verification failed for api.nhle.com")
        Traceback (most recent call last):
        NHLApiSSLError: SSL certificate verification failed for api.nhle.com
    """


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Security Errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class SecurityError(NHLScrabbleError):
    """Base exception for security-related errors.

    Raised when security policies are violated or security checks fail.

    Examples:
        >>> raise SecurityError("Security policy violation detected")
        Traceback (most recent call last):
        SecurityError: Security policy violation detected
    """


class SSRFProtectionError(SecurityError, ValueError):
    """Raised when SSRF (Server-Side Request Forgery) protection blocks a request.

    Indicates that a URL failed SSRF validation checks, preventing potential
    security vulnerabilities from accessing internal or malicious resources.

    Inherits from ValueError for backward compatibility.

    Examples:
        >>> raise SSRFProtectionError("Request blocked: URL targets private IP address")
        Traceback (most recent call last):
        SSRFProtectionError: Request blocked: URL targets private IP address
    """


class CircuitBreakerOpenError(SecurityError):
    """Raised when circuit breaker is open, preventing requests.

    The circuit breaker pattern is used for DoS prevention. When too many
    failures occur, the circuit "opens" and blocks requests temporarily.

    Examples:
        >>> raise CircuitBreakerOpenError("Circuit breaker open after 5 failures")
        Traceback (most recent call last):
        CircuitBreakerOpenError: Circuit breaker open after 5 failures
    """


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Storage Errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class StorageError(NHLScrabbleError):
    """Base exception for storage and persistence errors.

    Raised when there are issues with data storage operations,
    including database errors, file I/O errors, and serialization failures.

    Examples:
        >>> raise StorageError("Failed to save data to database")
        Traceback (most recent call last):
        StorageError: Failed to save data to database
    """


class HistoricalDataStoreError(StorageError):
    """Raised when historical data storage operations fail.

    Indicates failures in storing or retrieving historical analysis data,
    including database connection issues and query failures.

    Examples:
        >>> raise HistoricalDataStoreError("Failed to store analysis results")
        Traceback (most recent call last):
        HistoricalDataStoreError: Failed to store analysis results
    """


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Data Processing Errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class DataError(NHLScrabbleError):
    """Base exception for data processing errors.

    Raised when there are issues processing or transforming data,
    including parsing errors and invalid data structures.

    Examples:
        >>> raise DataError("Failed to parse player data")
        Traceback (most recent call last):
        DataError: Failed to parse player data
    """


class DataValidationError(DataError):
    """Raised when data validation fails during processing.

    This is different from ValidationError (input validation).
    DataValidationError is raised when processing data from external sources
    (APIs, files) that doesn't match expected formats.

    Examples:
        >>> raise DataValidationError("Player data missing required field: 'lastName'")
        Traceback (most recent call last):
        DataValidationError: Player data missing required field: 'lastName'
    """


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Exception Utility Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def format_exception_message(error: Exception, context: str | None = None) -> str:
    """Format exception message with context for user-friendly display.

    Args:
        error: The exception to format
        context: Optional context information

    Returns:
        Formatted error message with context

    Examples:
        >>> err = ValidationError("Invalid input")
        >>> format_exception_message(err, "Processing team TOR")
        'Processing team TOR: Invalid input'
        >>> format_exception_message(err)
        'Invalid input'
    """
    message = str(error)
    if context:
        return f"{context}: {message}"
    return message


__all__ = [
    "APIError",
    "CircuitBreakerOpenError",
    "DataError",
    "DataValidationError",
    "HistoricalDataStoreError",
    "NHLApiConnectionError",
    "NHLApiError",
    "NHLApiNotFoundError",
    "NHLApiSSLError",
    "NHLScrabbleError",
    "SSRFProtectionError",
    "SecurityError",
    "StorageError",
    "ValidationError",
    "format_exception_message",
]
