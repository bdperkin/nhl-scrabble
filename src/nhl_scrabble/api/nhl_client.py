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

from nhl_scrabble.security.ssrf_protection import SSRFProtectionError, validate_url_for_ssrf
from nhl_scrabble.utils.retry import retry

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
    SSRF protection, and enforced SSL/TLS certificate verification.

    SSL/TLS Security:
        - Certificate verification is always enabled and cannot be disabled
        - Uses certifi CA bundle for up-to-date certificate authorities
        - SSL errors are caught and logged for security monitoring

    Attributes:
        base_url: Base URL for the NHL API (SSRF-validated)
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed requests
        rate_limit_delay: Delay in seconds between requests to avoid rate limiting
        ca_bundle: Path to CA bundle for SSL verification (uses certifi)
    """

    BASE_URL = "https://api-web.nhle.com/v1"  # Default base URL
    _instances: ClassVar[set[weakref.ref[Any]]] = set()  # Track all instances for cleanup

    def __init__(  # noqa: PLR0913
        self,
        base_url: str | None = None,
        timeout: int = 10,
        retries: int = 3,
        rate_limit_delay: float = 0.3,
        backoff_factor: float = 2.0,
        max_backoff: float = 30.0,
        cache_enabled: bool = True,
        cache_expiry: int = 3600,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the NHL API client.

        Args:
            base_url: Base URL for NHL API (default: https://api-web.nhle.com/v1).
                Will be validated for SSRF protection on first request.
            timeout: Request timeout in seconds (default: 10)
            retries: Number of retry attempts for failed requests (default: 3)
            rate_limit_delay: Delay in seconds between requests (default: 0.3)
            backoff_factor: Exponential backoff multiplier (default: 2.0)
            max_backoff: Maximum backoff delay in seconds (default: 30.0)
            cache_enabled: Enable HTTP caching (default: True)
            cache_expiry: Cache expiration in seconds (default: 3600 = 1 hour)
            verify_ssl: SSL verification (must be True, cannot be disabled for security)

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
        self.rate_limit_delay = rate_limit_delay
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry
        self._last_request_time: float | None = (
            None  # Track last successful request for rate limiting
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
            logger.debug(f"HTTP caching enabled (expiry: {cache_expiry}s)")
        else:
            self.session = requests.Session()
            logger.debug("HTTP caching disabled")

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

    def get_teams(self) -> dict[str, dict[str, str]]:
        """Fetch all NHL teams with division and conference information.

        This method uses the retry decorator to automatically retry on network errors.
        The URL is validated with SSRF protection before making the request.

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
        """
        url = f"{self.base_url}/standings/now"
        logger.info("Fetching NHL teams from standings endpoint")

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
            if not is_cached and self._last_request_time is not None and self.rate_limit_delay > 0:
                elapsed = time.time() - self._last_request_time
                if elapsed < self.rate_limit_delay:
                    sleep_time = self.rate_limit_delay - elapsed
                    logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
                    time.sleep(sleep_time)

            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    verify=self.ca_bundle,  # Explicit SSL verification with certifi CA bundle
                )
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

                # Only record request time if this was a real API call (not cached)
                # Check from_cache attribute safely (handles Mock objects that don't have it set)
                from_cache = (
                    hasattr(response, "from_cache")
                    and isinstance(response.from_cache, bool)
                    and response.from_cache
                )
                if not from_cache:
                    self._last_request_time = time.time()
                    logger.debug("Real API request - updated rate limit timer")
                else:
                    logger.debug("Cache hit - skipped rate limiting")

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
            return _fetch_teams()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # Convert to NHLApiConnectionError after retries exhausted
            logger.error(f"Connection error after retries: {e}")
            raise NHLApiConnectionError("Unable to connect to NHL API after retries") from e

    def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:  # noqa: PLR0915
        """Fetch the current roster for a specific team.

        The URL is validated with SSRF protection before making the request.

        Args:
            team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL')

        Returns:
            Dictionary containing roster data with 'forwards', 'defensemen', and 'goalies' keys

        Raises:
            NHLApiNotFoundError: If the roster is not found (404 response)
            NHLApiConnectionError: If unable to connect to the API after all retries
            NHLApiError: For other API errors, including SSRF protection blocks

        Examples:
            >>> client = NHLApiClient()
            >>> roster = client.get_team_roster("TOR")
            >>> "forwards" in roster
            True
        """
        url = f"{self.base_url}/roster/{team_abbrev}/current"
        logger.debug(f"Fetching roster for {team_abbrev}")

        # Validate URL with SSRF protection
        self._validate_request_url(url)

        for attempt in range(self.retries):
            try:
                # Check if URL is cached
                is_cached = self._is_url_cached(url)

                # Only rate limit for actual API calls (not cached responses)
                if (
                    not is_cached
                    and self._last_request_time is not None
                    and self.rate_limit_delay > 0
                ):
                    elapsed = time.time() - self._last_request_time
                    if elapsed < self.rate_limit_delay:
                        sleep_time = self.rate_limit_delay - elapsed
                        logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
                        time.sleep(sleep_time)

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
                        # Extract Retry-After header (seconds)
                        retry_after = response.headers.get("Retry-After")
                        retry_after_int = int(retry_after) if retry_after else None
                        backoff_delay = self._calculate_backoff_delay(attempt, retry_after_int)
                        logger.warning(
                            f"Rate limited (429) for {team_abbrev} "
                            f"(attempt {attempt + 1}/{self.retries}), "
                            f"retrying in {backoff_delay:.2f}s..."
                        )
                        time.sleep(backoff_delay)
                        continue
                    logger.error(
                        f"Rate limited (429) for {team_abbrev} after {self.retries} attempts"
                    )
                    raise NHLApiConnectionError(
                        f"Rate limited after {self.retries} attempts"
                    ) from None

                response.raise_for_status()
                data = response.json()
                logger.debug(f"Successfully fetched roster for {team_abbrev}")

                # Only record request time if this was a real API call (not cached)
                # Check from_cache attribute safely (handles Mock objects that don't have it set)
                from_cache = (
                    hasattr(response, "from_cache")
                    and isinstance(response.from_cache, bool)
                    and response.from_cache
                )
                if not from_cache:
                    self._last_request_time = time.time()
                    logger.debug("Real API request - updated rate limit timer")
                else:
                    logger.debug("Cache hit - skipped rate limiting")

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
                raise NHLApiSSLError(f"SSL certificate verification failed for {url}: {e}") from e

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
