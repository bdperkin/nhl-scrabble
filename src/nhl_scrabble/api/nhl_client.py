"""NHL API client for fetching team and roster data."""

import logging
import time
from datetime import timedelta
from typing import Any

import requests
import requests_cache

logger = logging.getLogger(__name__)


class NHLApiError(Exception):
    """Base exception for NHL API errors."""


class NHLApiConnectionError(NHLApiError):
    """Raised when unable to connect to the NHL API."""


class NHLApiNotFoundError(NHLApiError):
    """Raised when the requested resource is not found."""


class NHLApiClient:
    """Client for interacting with the NHL API.

    This client provides methods to fetch team standings and roster data
    from the official NHL API with built-in retry logic and rate limiting.

    Attributes:
        base_url: Base URL for the NHL API
        timeout: Request timeout in seconds
        retries: Number of retry attempts for failed requests
        rate_limit_delay: Delay in seconds between requests to avoid rate limiting
    """

    BASE_URL = "https://api-web.nhle.com/v1"

    def __init__(
        self,
        timeout: int = 10,
        retries: int = 3,
        rate_limit_delay: float = 0.3,
        cache_enabled: bool = True,
        cache_expiry: int = 3600,
    ) -> None:
        """Initialize the NHL API client.

        Args:
            timeout: Request timeout in seconds (default: 10)
            retries: Number of retry attempts for failed requests (default: 3)
            rate_limit_delay: Delay in seconds between requests (default: 0.3)
            cache_enabled: Enable HTTP caching (default: True)
            cache_expiry: Cache expiration in seconds (default: 3600 = 1 hour)
        """
        self.timeout = timeout
        self.retries = retries
        self.rate_limit_delay = rate_limit_delay
        self.cache_enabled = cache_enabled
        self.cache_expiry = cache_expiry

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

    def get_teams(self) -> dict[str, dict[str, str]]:
        """Fetch all NHL teams with division and conference information.

        Returns:
            Dictionary mapping team abbreviations to their metadata:
            {
                'TOR': {'division': 'Atlantic', 'conference': 'Eastern'},
                'MTL': {'division': 'Atlantic', 'conference': 'Eastern'},
                ...
            }

        Raises:
            NHLApiConnectionError: If unable to connect to the API
            NHLApiError: For other API errors

        Examples:
            >>> client = NHLApiClient()
            >>> teams = client.get_teams()
            >>> "TOR" in teams
            True
        """
        url = f"{self.BASE_URL}/standings/now"
        logger.info("Fetching NHL teams from standings endpoint")

        try:
            response = self.session.get(url, timeout=self.timeout)
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
            return teams_info

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout while fetching teams: {e}")
            raise NHLApiConnectionError(f"Request timed out after {self.timeout}s") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while fetching teams: {e}")
            raise NHLApiConnectionError("Unable to connect to NHL API") from e
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error while fetching teams: {e}")
            raise NHLApiError(f"HTTP error: {e}") from e
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing teams response: {e}")
            raise NHLApiError(f"Invalid API response format: {e}") from e

    def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:
        """Fetch the current roster for a specific team.

        Args:
            team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL')

        Returns:
            Dictionary containing roster data with 'forwards', 'defensemen', and 'goalies' keys

        Raises:
            NHLApiNotFoundError: If the roster is not found (404 response)
            NHLApiConnectionError: If unable to connect to the API after all retries
            NHLApiError: For other API errors

        Examples:
            >>> client = NHLApiClient()
            >>> roster = client.get_team_roster("TOR")
            >>> "forwards" in roster
            True
        """
        url = f"{self.BASE_URL}/roster/{team_abbrev}/current"
        logger.debug(f"Fetching roster for {team_abbrev}")

        for attempt in range(self.retries):
            try:
                response = self.session.get(url, timeout=self.timeout)

                if response.status_code == 404:
                    logger.warning(f"No roster data available for {team_abbrev}")
                    raise NHLApiNotFoundError(f"Roster not found for team: {team_abbrev}")

                response.raise_for_status()
                data = response.json()
                logger.debug(f"Successfully fetched roster for {team_abbrev}")

                # Apply rate limiting
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)

                return data  # type: ignore[no-any-return]

            except requests.exceptions.Timeout:
                if attempt < self.retries - 1:
                    logger.warning(
                        f"Timeout fetching {team_abbrev} (attempt {attempt + 1}/{self.retries}), retrying..."
                    )
                    time.sleep(1)
                else:
                    logger.error(f"Failed to fetch {team_abbrev} after {self.retries} attempts")
                    raise NHLApiConnectionError(
                        f"Request timed out after {self.retries} attempts"
                    ) from None

            except requests.exceptions.ConnectionError:
                if attempt < self.retries - 1:
                    logger.warning(
                        f"Connection error for {team_abbrev} (attempt {attempt + 1}/{self.retries}), retrying..."
                    )
                    time.sleep(1)
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
        self.session.close()
        logger.debug("NHL API client session closed")

    def __enter__(self) -> "NHLApiClient":
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close session when exiting context manager."""
        self.close()
