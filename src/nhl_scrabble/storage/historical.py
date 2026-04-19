"""Historical data storage for caching NHL season data locally."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HistoricalDataStoreError(Exception):
    """Base exception for historical data storage errors."""


class HistoricalDataStore:
    """Storage manager for historical NHL Scrabble data.

    This class manages local caching of historical season data to reduce
    API calls and improve performance. Data is stored as JSON files in a
    configurable directory.

    Attributes:
        data_dir: Directory path where historical data files are stored.
            Each season is stored as a separate JSON file named '{season}.json'.

    Examples:
        >>> store = HistoricalDataStore()
        >>> data = {"teams": {"TOR": {"score": 1500}}}
        >>> store.save_season("20222023", data)
        >>> loaded = store.load_season("20222023")
        >>> loaded["teams"]["TOR"]["score"]
        1500
    """

    def __init__(self, data_dir: Path | str | None = None) -> None:
        """Initialize the historical data store.

        Args:
            data_dir: Directory for storing historical data files.
                Defaults to 'data/historical' in the current working directory.
                Will be created if it doesn't exist.

        Raises:
            HistoricalDataStoreError: If unable to create the data directory.

        Examples:
            >>> store = HistoricalDataStore()  # Uses default data/historical
            >>> store = HistoricalDataStore(Path("/tmp/nhl-data"))  # Custom location
        """
        # Use default directory if none provided
        data_dir = Path.cwd() / "data" / "historical" if data_dir is None else Path(data_dir)

        self.data_dir = data_dir

        # Create directory if it doesn't exist
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Historical data directory: {self.data_dir}")
        except OSError as e:
            error_msg = f"Failed to create data directory {self.data_dir}: {e}"
            logger.error(error_msg)
            raise HistoricalDataStoreError(error_msg) from e

    def _get_season_file_path(self, season: str) -> Path:
        """Get the file path for a season's data file.

        Args:
            season: Season identifier (e.g., '20222023')

        Returns:
            Path to the season's JSON file

        Examples:
            >>> store = HistoricalDataStore()
            >>> path = store._get_season_file_path("20222023")
            >>> path.name
            '20222023.json'
        """
        return self.data_dir / f"{season}.json"

    def save_season(self, season: str, data: dict[str, Any]) -> None:
        """Save season data to a JSON file.

        Args:
            season: Season identifier (e.g., '20222023' for 2022-23)
            data: Dictionary containing season data to save

        Raises:
            HistoricalDataStoreError: If unable to write the data file

        Examples:
            >>> store = HistoricalDataStore()
            >>> data = {
            ...     "teams": {"TOR": {"score": 1500}},
            ...     "timestamp": "2024-04-18T12:00:00"
            ... }
            >>> store.save_season("20222023", data)
        """
        file_path = self._get_season_file_path(season)

        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved season {season} data to {file_path}")
        except (OSError, TypeError, ValueError) as e:
            error_msg = f"Failed to save season {season} data: {e}"
            logger.error(error_msg)
            raise HistoricalDataStoreError(error_msg) from e

    def load_season(self, season: str) -> dict[str, Any] | None:
        """Load season data from a JSON file.

        Args:
            season: Season identifier (e.g., '20222023' for 2022-23)

        Returns:
            Dictionary containing season data if the file exists,
            None if the file doesn't exist

        Raises:
            HistoricalDataStoreError: If unable to read or parse the data file

        Examples:
            >>> store = HistoricalDataStore()
            >>> data = store.load_season("20222023")
            >>> data is None  # Returns None if file doesn't exist
            True
            >>> store.save_season("20222023", {"teams": {}})
            >>> data = store.load_season("20222023")
            >>> "teams" in data
            True
        """
        file_path = self._get_season_file_path(season)

        # Return None if file doesn't exist
        if not file_path.exists():
            logger.debug(f"No cached data found for season {season}")
            return None

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded season {season} data from {file_path}")
            return data  # type: ignore[no-any-return]
        except (OSError, json.JSONDecodeError, ValueError) as e:
            error_msg = f"Failed to load season {season} data: {e}"
            logger.error(error_msg)
            raise HistoricalDataStoreError(error_msg) from e

    def has_season(self, season: str) -> bool:
        """Check if data exists for a specific season.

        Args:
            season: Season identifier (e.g., '20222023' for 2022-23)

        Returns:
            True if cached data exists for the season, False otherwise

        Examples:
            >>> store = HistoricalDataStore()
            >>> store.has_season("20222023")
            False
            >>> store.save_season("20222023", {"teams": {}})
            >>> store.has_season("20222023")
            True
        """
        file_path = self._get_season_file_path(season)
        exists = file_path.exists() and file_path.is_file()
        logger.debug(f"Season {season} cached: {exists}")
        return exists

    def list_seasons(self) -> list[str]:
        """List all seasons with cached data.

        Returns:
            List of season identifiers (e.g., ['20222023', '20232024'])
            sorted in ascending order

        Examples:
            >>> store = HistoricalDataStore()
            >>> store.save_season("20222023", {"teams": {}})
            >>> store.save_season("20232024", {"teams": {}})
            >>> store.list_seasons()
            ['20222023', '20232024']
        """
        try:
            # Find all JSON files in the data directory
            season_files = sorted(self.data_dir.glob("*.json"))
            # Extract season names (remove .json extension)
            seasons = [f.stem for f in season_files]
            logger.debug(f"Found {len(seasons)} cached seasons")
            return seasons
        except OSError as e:
            logger.error(f"Failed to list seasons: {e}")
            return []

    def delete_season(self, season: str) -> bool:
        """Delete cached data for a specific season.

        Args:
            season: Season identifier (e.g., '20222023' for 2022-23)

        Returns:
            True if the file was deleted, False if it didn't exist

        Raises:
            HistoricalDataStoreError: If unable to delete the file

        Examples:
            >>> store = HistoricalDataStore()
            >>> store.save_season("20222023", {"teams": {}})
            >>> store.delete_season("20222023")
            True
            >>> store.delete_season("20222023")  # Already deleted
            False
        """
        file_path = self._get_season_file_path(season)

        if not file_path.exists():
            logger.debug(f"No cached data to delete for season {season}")
            return False

        try:
            file_path.unlink()
            logger.info(f"Deleted season {season} data from {file_path}")
            return True
        except OSError as e:
            error_msg = f"Failed to delete season {season} data: {e}"
            logger.error(error_msg)
            raise HistoricalDataStoreError(error_msg) from e

    def clear_all(self) -> int:
        """Delete all cached season data.

        Returns:
            Number of season files deleted

        Raises:
            HistoricalDataStoreError: If unable to delete files

        Examples:
            >>> store = HistoricalDataStore()
            >>> store.save_season("20222023", {"teams": {}})
            >>> store.save_season("20232024", {"teams": {}})
            >>> count = store.clear_all()
            >>> count
            2
        """
        try:
            season_files = list(self.data_dir.glob("*.json"))
            count = 0

            for file_path in season_files:
                try:
                    file_path.unlink()
                    count += 1
                except OSError as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")

            logger.info(f"Cleared {count} cached season files")
            return count
        except OSError as e:
            error_msg = f"Failed to clear cached data: {e}"
            logger.error(error_msg)
            raise HistoricalDataStoreError(error_msg) from e
