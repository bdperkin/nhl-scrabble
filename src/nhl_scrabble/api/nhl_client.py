"""NHL API client for fetching team and roster data."""

import atexit
import logging
import random
import time
import weakref
from datetime import timedelta
from typing import Any, ClassVar

import certifi
import requests
import requests_cache
from requests.adapters import HTTPAdapter

from nhl_scrabble.rate_limiter import RateLimiter
from nhl_scrabble.security.circuit_breaker import CircuitBreaker
from nhl_scrabble.security.ssrf_protection import SSRFProtectionError, validate_url_for_ssrf
from nhl_scrabble.utils.retry import retry
from nhl_scrabble.validators import (
    ValidationError,
    validate_api_response_structure,
    validate_player_name,
    validate_team_abbreviation,
)

logger = logging.getLogger(__name__)


class NHLApiError(Exception):
    """Base exception for NHL API errors."""


class NHLApiConnectionError(NHLApiError):
    """Raised when unable to connect to the NHL API."""


class NHLApiNotFoundError(NHLApiError):
    """Raised when the requested resource is not found."""


class NHLApiSSLError(NHLApiError):
    """Raised when SSL/TLS certificate verification fails."""


class NHLApiClient:
    """Client for interacting with the NHL API.

    This client provides methods to fetch team standings and roster data
    from the official NHL API with built-in retry logic, rate limiting,
    SSRF protection, DoS prevention, and enforced SSL/TLS certificate verification.

    SSL/TLS Security:
        - Certificate verification is always enabled and cannot be disabled
        - Uses certifi CA bundle for up-to-date certificate authorities
        - SSL errors are caught and logged for security monitoring

    DoS Prevention:
        - Circuit breaker pattern to prevent cascading failures
        - Connection pool limits to prevent resource exhaustion
        - Configurable failure thresholds and timeouts

    Attributes:
        base_url: Base URL for the NHL API (SSRF-validated)
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed requests
        rate_limiter: Token bucket rate limiter for API requests
        circuit_breaker: Circuit breaker for DoS prevention
        ca_bundle: Path to CA bundle for SSL verification (uses certifi)
    """

    BASE_URL = "https://api-web.nhle.com/v1"  # Default base URL
    _instances: ClassVar[set[weakref.ref[Any]]] = set()  # Track all instances for cleanup

    def __init__(  # noqa: PLR0913
        self,
        base_url: str | None = None,
        timeout: int = 10,
        retries: int = 3,
        rate_limit_max_requests: int = 30,
        rate_limit_window: float = 60.0,
        backoff_factor: float = 2.0,
        max_backoff: float = 30.0,
        cache_enabled: bool = True,
        cache_expiry: int = 3600,
        verify_ssl: bool = True,
        dos_max_connections: int = 10,
        dos_max_per_host: int = 5,
        dos_circuit_breaker_threshold: int = 5,
        dos_circuit_breaker_timeout: float = 60.0,
    ) -> None:
        """Initialize the NHL API client.

        Args:
            base_url: Base URL for NHL API (default: https://api-web.nhle.com/v1).
                Will be validated for SSRF protection on first request.
            timeout: Request timeout in seconds (default: 10)
            retries: Number of retry attempts for failed requests (default: 3)
            rate_limit_max_requests: Maximum requests per time window (default: 30)
            rate_limit_window: Time window for rate limiting in seconds (default: 60.0)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
            max_backoff: Maximum backoff delay in seconds (default: 30.0)
            cache_enabled: Enable HTTP caching (default: True)
            cache_expiry: Cache expiration in seconds (default: 3600 = 1 hour)
            verify_ssl: SSL verification (must be True, cannot be disabled for security)
            dos_max_connections: Maximum connection pool connections (default: 10)
            dos_max_per_host: Maximum connections per host (default: 5)
            dos_circuit_breaker_threshold: Circuit breaker failure threshold (default: 5)
            dos_circuit_breaker_timeout: Circuit breaker timeout in seconds (default: 60.0)

        Raises:
            NHLApiError: If base_url fails SSRF protection validation
            ValueError: If verify_ssl is False (SSL verification cannot be disabled)
        """
        # Initialize state tracking FIRST (before any potential exceptions)
        # This prevents AttributeError in __del__ if __init__ fails
        self._closed = False

        # Enforce SSL verification - cannot be disabled
        if not verify_ssl:
            error_msg = "SSL verification cannot be disabled for security reasons"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Use provided base_url or fall back to class default
        self.base_url = base_url or self.BASE_URL

        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=rate_limit_max_requests, time_window=rate_limit_window
        )
        logger.info(
            f"Rate limiter initialized: {rate_limit_max_requests} requests per {rate_limit_window}s"
        )

        # Initialize circuit breaker for DoS prevention
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=dos_circuit_breaker_threshold,
            timeout=dos_circuit_breaker_timeout,
            expected_exception=(
                requests.exceptions.RequestException,
                NHLApiError,
            ),
        )
        logger.info(
            f"Circuit breaker initialized: threshold={dos_circuit_breaker_threshold}, "
            f"timeout={dos_circuit_breaker_timeout}s"
        )

        # Use certifi CA bundle for SSL verification
        self.ca_bundle = certifi.where()
        logger.debug(f"Using CA bundle for SSL verification: {self.ca_bundle}")

        # Session can be either CachedSession or regular Session
        self.session: requests_cache.CachedSession | requests.Session
        if cache_enabled:
            # Create cached session
            self.session = requests_cache.CachedSession(
                cache_name=".nhl_cache",
                backend="sqlite",
                expire_after=timedelta(seconds=cache_expiry),
                allowable_codes=[200],  # Only cache successful responses
                allowable_methods=["GET"],
                cache_control=True,  # Respect Cache-Control headers
            )
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"HTTP caching enabled (expiry: {cache_expiry}s)")
        else:
            self.session = requests.Session()
            logger.debug("HTTP caching disabled")

        # Configure connection pool limits for DoS protection
        adapter = HTTPAdapter(
            pool_connections=dos_max_connections,
            pool_maxsize=dos_max_per_host,
            max_retries=0,  # We handle retries ourselves via @retry decorator
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        logger.info(
            f"Connection pool configured: max_connections={dos_max_connections}, "
            f"max_per_host={dos_max_per_host}"
        )

        self.session.headers.update({"User-Agent": "NHL-Scrabble/2.0"})

        # Register instance for cleanup at exit (safety net)
        self._instances.add(weakref.ref(self, self._cleanup_callback))
        atexit.register(self._cleanup_all)

    def _validate_request_url(self, url: str) -> None:
        """Validate URL with SSRF protection before making request.

        Args:
            url: Full URL to validate

        Raises:
            NHLApiError: If URL fails SSRF protection validation
        """
        try:
            validate_url_for_ssrf(url, allow_private=False)
        except SSRFProtectionError as e:
            logger.error(f"SSRF protection blocked request to {url}: {e}")
            raise NHLApiError(f"Request blocked by security protection: {e}") from e

    def _get_retry_after(self, response: requests.Response) -> float:
        """Extract Retry-After header value from 429 response.

        Args:
            response: HTTP response with 429 status

        Returns:
            Seconds to wait before retry

        Examples:
            >>> client = NHLApiClient()
            >>> from unittest.mock import Mock
            >>> response = Mock()
            >>> response.headers = {"Retry-After": "60"}
            >>> client._get_retry_after(response)
            60.0
        """
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                # Try as integer (seconds)
                return float(retry_after)
            except ValueError:
                # Could be HTTP date format, but uncommon for 429
                # Default to exponential backoff
                pass

        # No Retry-After header, use exponential backoff
        # Start with 1 second
        return 1.0

    def _calculate_backoff_delay(self, attempt: int, retry_after: int | None = None) -> float:
        """Calculate backoff delay with exponential backoff and jitter.

        Args:
            attempt: Current attempt number (0-indexed)
            retry_after: Optional Retry-After header value from 429 response

        Returns:
            Delay in seconds with jitter applied

        Examples:
            >>> client = NHLApiClient()
            >>> client._calculate_backoff_delay(0)  # First retry
            0.75  # ~1.0 * (2.0 ** 0) with ±25% jitter
            >>> client._calculate_backoff_delay(3)  # Fourth retry
            6.5   # ~8.0 * (2.0 ** 3) with ±25% jitter, capped at max_backoff
        """
        if retry_after is not None:
            # Respect Retry-After header from API (429 responses)
            return min(float(retry_after), self.max_backoff)

        # Exponential backoff: base_delay * (backoff_factor ** attempt)
        base_delay = 1.0
        delay = min(base_delay * (self.backoff_factor**attempt), self.max_backoff)

        # Add jitter: randomize ±25% to prevent thundering herd
        # Safe: Using random for jitter, not cryptography
        jitter = delay * 0.25
        delay = delay + random.uniform(-jitter, jitter)  # noqa: S311

        return max(0, delay)

    def _is_url_cached(self, url: str) -> bool:
        """Check if a URL response is cached and not expired.

        Args:
            url: The URL to check

        Returns:
            True if the URL response is cached and valid, False otherwise

        Examples:
            >>> client = NHLApiClient(cache_enabled=True)
            >>> client._is_url_cached("https://api-web.nhle.com/v1/roster/TOR/current")
            False  # Not cached initially
        """
        if not self.cache_enabled:
            return False

        if not hasattr(self.session, "cache"):
            return False

        try:
            # Check if URL is in cache using has_url() method (requests-cache 1.0+)
            if hasattr(self.session.cache, "has_url"):
                return self.session.cache.has_url(url)  # type: ignore[no-any-return]

            # Fallback: check using contains() method
            if hasattr(self.session.cache, "contains"):
                return self.session.cache.contains(url=url)  # type: ignore[no-any-return]

            # If no cache checking method available, assume not cached
            return False
        except Exception:  # noqa: BLE001
            # If anything goes wrong checking cache, assume not cached
            # This ensures we always apply rate limiting if uncertain
            return False

    def get_teams(self, season: str | None = None) -> dict[str, dict[str, str]]:
        """Fetch all NHL teams with division and conference information.

        This method uses the retry decorator to automatically retry on network errors.
        The URL is validated with SSRF protection before making the request.

        Args:
            season: Optional season in format 'YYYYYYYY' (e.g., '20222023' for 2022-23).
                If None, fetches current season data.

        Returns:
            Dictionary mapping team abbreviations to their metadata:
            {
                'TOR': {'division': 'Atlantic', 'conference': 'Eastern'},
                'MTL': {'division': 'Atlantic', 'conference': 'Eastern'},
                ...
            }

        Raises:
            NHLApiConnectionError: If unable to connect to the API
            NHLApiError: For other API errors, including SSRF protection blocks

        Examples:
            >>> client = NHLApiClient()
            >>> teams = client.get_teams()
            >>> "TOR" in teams
            True
            >>> teams_2022 = client.get_teams(season="20222023")
            >>> "TOR" in teams_2022
            True
        """
        # Use season-specific endpoint or current season endpoint
        endpoint = f"standings/{season}" if season else "standings/now"
        url = f"{self.base_url}/{endpoint}"

        season_desc = f"season {season}" if season else "current season"
        logger.info(f"Fetching NHL teams from standings endpoint for {season_desc}")

        # Validate URL with SSRF protection
        self._validate_request_url(url)

        @retry(
            max_attempts=self.retries,
            backoff_factor=self.backoff_factor,
            max_backoff=self.max_backoff,
            exceptions=(
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ),
        )
        def _fetch_teams() -> dict[str, dict[str, str]]:
            """Fetch teams with retry logic."""
            # Check if URL is cached
            is_cached = self._is_url_cached(url)

            # Only rate limit for actual API calls (not cached responses)
            if not is_cached:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Rate limiting: acquiring token for teams request")
                self.rate_limiter.acquire()

            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    verify=self.ca_bundle,  # Explicit SSL verification with certifi CA bundle
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = self._get_retry_after(response)
                    logger.warning(f"Rate limited (429). Waiting {retry_after}s before retry.")
                    time.sleep(retry_after)
                    # Raise to trigger retry
                    response.raise_for_status()

                response.raise_for_status()
                data = response.json()

                teams_info: dict[str, dict[str, str]] = {}
                for team in data["standings"]:
                    team_abbrev = team["teamAbbrev"]["default"]
                    teams_info[team_abbrev] = {
                        "division": team.get("divisionName", "Unknown"),
                        "conference": team.get("conferenceName", "Unknown"),
                    }

                logger.info(f"Successfully fetched {len(teams_info)} teams")

                # Log cache status
                from_cache = (
                    hasattr(response, "from_cache")
                    and isinstance(response.from_cache, bool)
                    and response.from_cache
                )
                if from_cache:
                    logger.debug("Cache hit - skipped rate limiting")
                else:
                    logger.debug("Real API request - rate limited")

                return teams_info

            except requests.exceptions.SSLError as e:
                logger.error(f"SSL certificate verification failed for {url}: {e}")
                raise NHLApiSSLError(f"SSL certificate verification failed for {url}: {e}") from e
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error while fetching teams: {e}")
                raise NHLApiError(f"HTTP error: {e}") from e
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing teams response: {e}")
                raise NHLApiError(f"Invalid API response format: {e}") from e

        try:
            # Wrap with circuit breaker for DoS prevention
            return self.circuit_breaker.call(_fetch_teams)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # Convert to NHLApiConnectionError after retries exhausted
            logger.error(f"Connection error after retries: {e}")
            raise NHLApiConnectionError("Unable to connect to NHL API after retries") from e

    def get_team_roster(  # noqa: PLR0915
        self, team_abbrev: str, season: str | None = None
    ) -> dict[str, Any]:
        """Fetch the roster for a specific team with input and response validation.

        Validates team abbreviation before making API call and validates response
        structure to prevent errors from malformed data.

        The URL is validated with SSRF protection before making the request.

        Args:
            team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL')
            season: Optional season in format 'YYYYYYYY' (e.g., '20222023' for 2022-23).
                If None, fetches current season roster.

        Returns:
            Dictionary containing roster data with 'forwards', 'defensemen', and 'goalies' keys

        Raises:
            ValidationError: If team abbreviation is invalid
            NHLApiNotFoundError: If the roster is not found (404 response)
            NHLApiConnectionError: If unable to connect to the API after all retries
            NHLApiError: For other API errors, including SSRF protection blocks and malformed responses

        Security:
            - Validates team abbreviation to prevent injection attacks
            - Validates response structure to prevent KeyError exceptions
            - Sanitizes player names from API responses
            - SSRF protection on all API requests

        Examples:
            >>> client = NHLApiClient()
            >>> roster = client.get_team_roster("TOR")
            >>> "forwards" in roster
            True
            >>> roster_2022 = client.get_team_roster("TOR", season="20222023")
            >>> "forwards" in roster_2022
            True
            >>> client.get_team_roster("INVALID")
            Traceback (most recent call last):
            ValidationError: Team abbreviation must be 2-3 characters...
        """
        # Validate team abbreviation BEFORE making API call
        try:
            validated_abbrev = validate_team_abbreviation(team_abbrev)
        except ValidationError:
            # Re-raise validation errors for consistency with other API errors
            logger.error(f"Invalid team abbreviation: {team_abbrev}")
            raise

        # Use season-specific endpoint or current season endpoint
        endpoint = (
            f"roster/{validated_abbrev}/{season}"
            if season
            else f"roster/{validated_abbrev}/current"
        )
        url = f"{self.base_url}/{endpoint}"

        season_desc = f"season {season}" if season else "current season"
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Fetching roster for {validated_abbrev} ({season_desc})")

        # Validate URL with SSRF protection
        self._validate_request_url(url)

        def _fetch_roster() -> dict[str, Any]:  # noqa: PLR0915
            """Fetch roster with retry logic."""
            for attempt in range(self.retries):
                try:
                    # Check if URL is cached
                    is_cached = self._is_url_cached(url)

                    # Only rate limit for actual API calls (not cached responses)
                    if not is_cached:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"Rate limiting: acquiring token for {team_abbrev} roster")
                        self.rate_limiter.acquire()

                    response = self.session.get(
                        url,
                        timeout=self.timeout,
                        verify=self.ca_bundle,  # Explicit SSL verification with certifi CA bundle
                    )

                    if response.status_code == 404:
                        logger.warning(f"No roster data available for {team_abbrev}")
                        raise NHLApiNotFoundError(f"Roster not found for team: {team_abbrev}")

                    # Handle 429 rate limiting with exponential backoff
                    if response.status_code == 429:
                        if attempt < self.retries - 1:
                            retry_after = self._get_retry_after(response)
                            logger.warning(
                                f"Rate limited (429) for {team_abbrev} "
                                f"(attempt {attempt + 1}/{self.retries}), "
                                f"retrying in {retry_after:.2f}s..."
                            )
                            time.sleep(retry_after)
                            continue
                        logger.error(
                            f"Rate limited (429) for {team_abbrev} after {self.retries} attempts"
                        )
                        raise NHLApiConnectionError(
                            f"Rate limited after {self.retries} attempts"
                        ) from None

                    response.raise_for_status()
                    data = response.json()

                    # Validate response structure
                    try:
                        validate_api_response_structure(
                            data,
                            required_keys=["forwards", "defensemen", "goalies"],
                            context=f"Team roster response for {validated_abbrev}",
                        )
                    except ValidationError as e:
                        logger.error(
                            f"Invalid roster response structure for {validated_abbrev}: {e}"
                        )
                        raise NHLApiError(f"Invalid API response: {e}") from e

                    # Sanitize player names in response
                    self._sanitize_roster_player_names(data)

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"Successfully fetched and validated roster for {validated_abbrev}"
                        )

                    # Log cache status
                    from_cache = (
                        hasattr(response, "from_cache")
                        and isinstance(response.from_cache, bool)
                        and response.from_cache
                    )
                    if from_cache:
                        logger.debug("Cache hit - skipped rate limiting")
                    else:
                        logger.debug("Real API request - rate limited")

                    return data  # type: ignore[no-any-return]

                except requests.exceptions.Timeout:
                    if attempt < self.retries - 1:
                        backoff_delay = self._calculate_backoff_delay(attempt)
                        logger.warning(
                            f"Timeout fetching {team_abbrev} "
                            f"(attempt {attempt + 1}/{self.retries}), "
                            f"retrying in {backoff_delay:.2f}s..."
                        )
                        time.sleep(backoff_delay)
                    else:
                        logger.error(f"Failed to fetch {team_abbrev} after {self.retries} attempts")
                        raise NHLApiConnectionError(
                            f"Request timed out after {self.retries} attempts"
                        ) from None

                except requests.exceptions.SSLError as e:
                    # SSL errors should not be retried - certificate validation failure is permanent
                    logger.error(f"SSL certificate verification failed for {team_abbrev}: {e}")
                    raise NHLApiSSLError(
                        f"SSL certificate verification failed for {url}: {e}"
                    ) from e

                except requests.exceptions.ConnectionError:
                    if attempt < self.retries - 1:
                        backoff_delay = self._calculate_backoff_delay(attempt)
                        logger.warning(
                            f"Connection error for {team_abbrev} "
                            f"(attempt {attempt + 1}/{self.retries}), "
                            f"retrying in {backoff_delay:.2f}s..."
                        )
                        time.sleep(backoff_delay)
                    else:
                        logger.error(f"Failed to fetch {team_abbrev} after {self.retries} attempts")
                        raise NHLApiConnectionError(
                            f"Connection failed after {self.retries} attempts"
                        ) from None

                except requests.exceptions.HTTPError as e:
                    logger.error(f"HTTP error fetching {team_abbrev}: {e}")
                    raise NHLApiError(f"HTTP error: {e}") from e

            # This should never be reached as all paths above either return or raise
            raise NHLApiError("Unexpected error: retry loop completed without returning data")

        # Wrap with circuit breaker for DoS prevention
        return self.circuit_breaker.call(_fetch_roster)

    def _sanitize_roster_player_names(self, roster_data: dict[str, Any]) -> None:
        """Sanitize player names in roster data to prevent injection attacks.

        Validates and sanitizes all player names (firstName and lastName) in the
        roster data for all positions (forwards, defensemen, goalies).

        Args:
            roster_data: Roster data dictionary with forwards, defensemen, goalies

        Raises:
            NHLApiError: If player names contain invalid characters (potential attack)

        Note:
            Modifies roster_data in-place for efficiency
        """
        for position in ["forwards", "defensemen", "goalies"]:
            if position not in roster_data:
                continue

            for player in roster_data[position]:
                # Validate and sanitize first name
                if (
                    "firstName" in player
                    and isinstance(player["firstName"], dict)
                    and "default" in player["firstName"]
                ):
                    try:
                        player["firstName"]["default"] = validate_player_name(
                            player["firstName"]["default"]
                        )
                    except ValidationError as e:
                        logger.warning(f"Invalid player first name in API response: {e}")
                        # Use sanitized version or skip
                        player["firstName"]["default"] = "Unknown"

                # Validate and sanitize last name
                if (
                    "lastName" in player
                    and isinstance(player["lastName"], dict)
                    and "default" in player["lastName"]
                ):
                    try:
                        player["lastName"]["default"] = validate_player_name(
                            player["lastName"]["default"]
                        )
                    except ValidationError as e:
                        logger.warning(f"Invalid player last name in API response: {e}")
                        # Use sanitized version or skip
                        player["lastName"]["default"] = "Unknown"

    def get_rate_limit_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Dictionary with rate limiter statistics including:
                - total_requests: Total requests made
                - total_waits: Total times waited for tokens
                - total_wait_time: Total time spent waiting
                - average_wait: Average wait time per wait
                - current_tokens: Current token count
                - max_tokens: Maximum token capacity

        Examples:
            >>> client = NHLApiClient()
            >>> stats = client.get_rate_limit_stats()
            >>> "total_requests" in stats
            True
        """
        return self.rate_limiter.get_stats()

    def clear_cache(self) -> None:
        """Clear the HTTP cache."""
        if self.cache_enabled and hasattr(self.session, "cache"):
            self.session.cache.clear()
            logger.info("API cache cleared")
        else:
            logger.debug("Cache not available or caching disabled")

    def close(self) -> None:
        """Close the session and release resources."""
        if not self._closed and hasattr(self, "session"):
            self.session.close()
            self._closed = True
            logger.debug("NHL API client session closed")

    def __enter__(self) -> "NHLApiClient":
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close session when exiting context manager."""
        self.close()

    def __del__(self) -> None:
        """Destructor - close session if not already closed (safety net)."""
        if not self._closed:
            logger.warning(
                "NHLApiClient session was not explicitly closed - cleaning up in destructor"
            )
            self.close()

    @classmethod
    def _cleanup_callback(cls, ref: weakref.ref[Any]) -> None:
        """Remove dead instance from tracking set.

        Args:
            ref: Weak reference to the instance being garbage collected.
        """
        cls._instances.discard(ref)

    @classmethod
    def _cleanup_all(cls) -> None:
        """Close all remaining open sessions at program exit (safety net)."""
        alive_instances = [ref() for ref in cls._instances if ref() is not None]
        if alive_instances:
            logger.warning(
                f"Cleaning up {len(alive_instances)} unclosed NHLApiClient session(s) at exit"
            )
            for instance in alive_instances:
                if instance and not instance._closed:  # noqa: SLF001
                    instance.close()
