"""Tests for historical data storage module."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003  # Path used at runtime in fixtures

import pytest

from nhl_scrabble.storage.historical import HistoricalDataStore, HistoricalDataStoreError


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory for testing.

    Args:
        tmp_path: pytest temporary path fixture

    Returns:
        Path to temporary data directory
    """
    data_dir = tmp_path / "historical_data"
    return data_dir


@pytest.fixture
def store(temp_data_dir: Path) -> HistoricalDataStore:
    """Create HistoricalDataStore instance for testing.

    Args:
        temp_data_dir: Temporary data directory

    Returns:
        HistoricalDataStore instance
    """
    return HistoricalDataStore(data_dir=temp_data_dir)


class TestHistoricalDataStoreInit:
    """Tests for HistoricalDataStore initialization."""

    def test_init_creates_directory(self, temp_data_dir: Path) -> None:
        """Test that initialization creates the data directory."""
        assert not temp_data_dir.exists()
        store = HistoricalDataStore(data_dir=temp_data_dir)
        assert temp_data_dir.exists()
        assert temp_data_dir.is_dir()
        assert store.data_dir == temp_data_dir

    def test_init_with_existing_directory(self, temp_data_dir: Path) -> None:
        """Test initialization with pre-existing directory."""
        temp_data_dir.mkdir(parents=True)
        store = HistoricalDataStore(data_dir=temp_data_dir)
        assert store.data_dir == temp_data_dir

    def test_init_default_directory(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test initialization with default directory."""
        monkeypatch.chdir(tmp_path)
        store = HistoricalDataStore()
        expected_dir = tmp_path / "data" / "historical"
        assert store.data_dir == expected_dir
        assert expected_dir.exists()


class TestHistoricalDataStoreSave:
    """Tests for saving season data."""

    def test_save_season(self, store: HistoricalDataStore) -> None:
        """Test saving season data to file."""
        season = "20222023"
        data = {"teams": {"TOR": {"score": 1500}}, "total": 1500}

        store.save_season(season, data)

        # Verify file was created
        file_path = store.data_dir / f"{season}.json"
        assert file_path.exists()

        # Verify file contains correct data
        with file_path.open("r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        assert loaded_data == data

    def test_save_season_overwrites_existing(self, store: HistoricalDataStore) -> None:
        """Test that saving overwrites existing season data."""
        season = "20222023"
        data1 = {"teams": {"TOR": {"score": 1500}}}
        data2 = {"teams": {"TOR": {"score": 2000}}}

        store.save_season(season, data1)
        store.save_season(season, data2)

        loaded_data = store.load_season(season)
        assert loaded_data == data2

    def test_save_season_with_unicode(self, store: HistoricalDataStore) -> None:
        """Test saving data with Unicode characters."""
        season = "20222023"
        data = {"player": "Žlutý kůň"}

        store.save_season(season, data)

        loaded_data = store.load_season(season)
        assert loaded_data == data


class TestHistoricalDataStoreLoad:
    """Tests for loading season data."""

    def test_load_season_existing(self, store: HistoricalDataStore) -> None:
        """Test loading existing season data."""
        season = "20222023"
        data = {"teams": {"TOR": {"score": 1500}}}

        store.save_season(season, data)
        loaded_data = store.load_season(season)

        assert loaded_data == data

    def test_load_season_nonexistent(self, store: HistoricalDataStore) -> None:
        """Test loading non-existent season returns None."""
        season = "20222023"
        loaded_data = store.load_season(season)
        assert loaded_data is None

    def test_load_season_corrupted_json(self, store: HistoricalDataStore) -> None:
        """Test loading corrupted JSON file raises error."""
        season = "20222023"
        file_path = store.data_dir / f"{season}.json"

        # Create corrupted JSON file
        file_path.write_text("{ invalid json")

        with pytest.raises(HistoricalDataStoreError, match="Failed to load season"):
            store.load_season(season)


class TestHistoricalDataStoreHas:
    """Tests for checking season existence."""

    def test_has_season_existing(self, store: HistoricalDataStore) -> None:
        """Test has_season returns True for existing season."""
        season = "20222023"
        store.save_season(season, {"teams": {}})

        assert store.has_season(season) is True

    def test_has_season_nonexistent(self, store: HistoricalDataStore) -> None:
        """Test has_season returns False for non-existent season."""
        season = "20222023"
        assert store.has_season(season) is False


class TestHistoricalDataStoreList:
    """Tests for listing seasons."""

    def test_list_seasons_empty(self, store: HistoricalDataStore) -> None:
        """Test listing seasons returns empty list when no data."""
        seasons = store.list_seasons()
        assert seasons == []

    def test_list_seasons_multiple(self, store: HistoricalDataStore) -> None:
        """Test listing multiple seasons returns sorted list."""
        seasons_data = ["20222023", "20202021", "20232024"]
        for season in seasons_data:
            store.save_season(season, {"teams": {}})

        seasons = store.list_seasons()
        assert seasons == sorted(seasons_data)

    def test_list_seasons_ignores_non_json(self, store: HistoricalDataStore) -> None:
        """Test listing seasons ignores non-JSON files."""
        store.save_season("20222023", {"teams": {}})

        # Create non-JSON file
        (store.data_dir / "readme.txt").write_text("test")

        seasons = store.list_seasons()
        assert seasons == ["20222023"]


class TestHistoricalDataStoreDelete:
    """Tests for deleting season data."""

    def test_delete_season_existing(self, store: HistoricalDataStore) -> None:
        """Test deleting existing season returns True."""
        season = "20222023"
        store.save_season(season, {"teams": {}})

        result = store.delete_season(season)

        assert result is True
        assert not store.has_season(season)

    def test_delete_season_nonexistent(self, store: HistoricalDataStore) -> None:
        """Test deleting non-existent season returns False."""
        season = "20222023"
        result = store.delete_season(season)
        assert result is False


class TestHistoricalDataStoreClear:
    """Tests for clearing all season data."""

    def test_clear_all_empty(self, store: HistoricalDataStore) -> None:
        """Test clearing empty store returns 0."""
        count = store.clear_all()
        assert count == 0

    def test_clear_all_multiple(self, store: HistoricalDataStore) -> None:
        """Test clearing multiple seasons."""
        seasons = ["20222023", "20232024", "20242025"]
        for season in seasons:
            store.save_season(season, {"teams": {}})

        count = store.clear_all()

        assert count == 3
        assert store.list_seasons() == []

    def test_clear_all_preserves_directory(self, store: HistoricalDataStore) -> None:
        """Test clear_all preserves the data directory."""
        store.save_season("20222023", {"teams": {}})
        store.clear_all()

        assert store.data_dir.exists()
        assert store.data_dir.is_dir()
