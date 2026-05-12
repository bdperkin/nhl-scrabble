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

    def test_init_permission_error(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test initialization raises error when directory creation fails."""
        from pathlib import Path

        def mock_mkdir(*args, **kwargs):  # noqa: ANN002, ANN003, ARG001
            raise OSError("Permission denied")

        monkeypatch.setattr(Path, "mkdir", mock_mkdir)

        with pytest.raises(HistoricalDataStoreError, match="Failed to create data directory"):
            HistoricalDataStore(data_dir=tmp_path / "test")


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

    def test_save_season_write_error(
        self,
        store: HistoricalDataStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test save_season raises error when file write fails."""
        from pathlib import Path

        original_open = Path.open

        def mock_open(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
            # Fail on write mode
            mode = kwargs.get("mode", args[0] if args else "r")
            if "w" in mode:
                raise OSError("Disk full")
            return original_open(self, *args, **kwargs)

        monkeypatch.setattr(Path, "open", mock_open)

        season = "20222023"
        data = {"teams": {}}

        with pytest.raises(HistoricalDataStoreError, match="Failed to save season"):
            store.save_season(season, data)


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

    def test_list_seasons_permission_error(
        self,
        store: HistoricalDataStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test list_seasons handles permission errors gracefully."""
        from pathlib import Path

        def mock_glob(*args, **kwargs):  # noqa: ANN002, ANN003, ARG001
            raise OSError("Permission denied")

        # Mock the glob method to raise OSError
        monkeypatch.setattr(Path, "glob", mock_glob)

        # Should return empty list instead of raising
        seasons = store.list_seasons()
        assert seasons == []


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

    def test_delete_season_permission_error(
        self,
        store: HistoricalDataStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test delete_season raises error on permission issues."""
        from pathlib import Path

        season = "20222023"
        store.save_season(season, {"teams": {}})

        def mock_unlink(*args, **kwargs):  # noqa: ANN002, ANN003, ARG001
            raise OSError("Permission denied")

        # Mock the unlink method to raise OSError
        monkeypatch.setattr(Path, "unlink", mock_unlink)

        with pytest.raises(HistoricalDataStoreError, match="Failed to delete season"):
            store.delete_season(season)


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

    def test_clear_all_partial_failure(
        self,
        store: HistoricalDataStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test clear_all continues on individual file deletion errors."""
        from pathlib import Path

        seasons = ["20222023", "20232024", "20242025"]
        for season in seasons:
            store.save_season(season, {"teams": {}})

        # Save original unlink method
        original_unlink = Path.unlink
        call_count = 0

        def mock_unlink(self):  # noqa: ANN001, ANN202
            nonlocal call_count
            call_count += 1
            # Fail on first file, succeed on others
            if call_count == 1:
                raise OSError("Permission denied")
            # Call the original unlink for other files
            return original_unlink(self)

        monkeypatch.setattr(Path, "unlink", mock_unlink)

        # Should delete 2 out of 3 files
        count = store.clear_all()
        assert count == 2

    def test_clear_all_glob_error(
        self,
        store: HistoricalDataStore,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test clear_all raises error when glob fails."""
        from pathlib import Path

        def mock_glob(*args, **kwargs):  # noqa: ANN002, ANN003, ARG001
            raise OSError("Permission denied")

        monkeypatch.setattr(Path, "glob", mock_glob)

        with pytest.raises(HistoricalDataStoreError, match="Failed to clear cached data"):
            store.clear_all()
