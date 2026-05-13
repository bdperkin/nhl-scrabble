"""Tests for HistoricalDataStore save and load operations."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from nhl_scrabble.storage.historical import HistoricalDataStore, HistoricalDataStoreError


class TestSaveSeasonEdgeCases:
    """Tests for save_season edge cases and error paths."""

    def test_save_season_basic(self, tmp_path: Path) -> None:
        """Test basic save operation."""
        store = HistoricalDataStore(tmp_path)
        data = {"teams": {"TOR": {"score": 1500}}}

        store.save_season("20222023", data)

        file_path = tmp_path / "20222023.json"
        assert file_path.exists()
        saved_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert saved_data == data

    def test_save_season_empty_data(self, tmp_path: Path) -> None:
        """Test saving empty dictionary."""
        store = HistoricalDataStore(tmp_path)

        store.save_season("20222023", {})

        file_path = tmp_path / "20222023.json"
        assert file_path.exists()
        assert json.loads(file_path.read_text(encoding="utf-8")) == {}

    def test_save_season_complex_nested_data(self, tmp_path: Path) -> None:
        """Test saving deeply nested data structures."""
        store = HistoricalDataStore(tmp_path)
        data = {
            "teams": {
                "TOR": {
                    "players": [
                        {"name": "Player1", "score": 100},
                        {"name": "Player2", "score": 200},
                    ],
                    "metadata": {"city": "Toronto", "founded": 1917},
                },
            },
            "timestamp": "2024-04-18T12:00:00",
        }

        store.save_season("20222023", data)

        file_path = tmp_path / "20222023.json"
        saved_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert saved_data == data

    def test_save_season_unicode_data(self, tmp_path: Path) -> None:
        """Test saving data with unicode characters."""
        store = HistoricalDataStore(tmp_path)
        data = {
            "teams": {
                "MTL": {"name": "Montréal Canadiens", "city": "Montréal"},
            },
        }

        store.save_season("20222023", data)

        file_path = tmp_path / "20222023.json"
        saved_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert saved_data["teams"]["MTL"]["name"] == "Montréal Canadiens"

    def test_save_season_overwrite_existing(self, tmp_path: Path) -> None:
        """Test overwriting existing season data."""
        store = HistoricalDataStore(tmp_path)

        # Save initial data
        store.save_season("20222023", {"version": 1})

        # Overwrite with new data
        store.save_season("20222023", {"version": 2})

        file_path = tmp_path / "20222023.json"
        saved_data = json.loads(file_path.read_text(encoding="utf-8"))
        assert saved_data["version"] == 2

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="chmod doesn't restrict permissions on Windows",
    )
    def test_save_season_write_fails_permission_denied(self, tmp_path: Path) -> None:
        """Test error when write fails due to permissions."""
        store = HistoricalDataStore(tmp_path)

        # Make directory read-only
        tmp_path.chmod(0o444)

        try:
            with pytest.raises(
                HistoricalDataStoreError,
                match="Failed to save season 20222023 data",
            ):
                store.save_season("20222023", {"teams": {}})
        finally:
            # Restore permissions for cleanup
            tmp_path.chmod(0o755)

    def test_save_season_non_serializable_data(self, tmp_path: Path) -> None:
        """Test error when data contains non-JSON-serializable objects."""
        store = HistoricalDataStore(tmp_path)

        # Create data with non-serializable object
        data = {"callback": lambda x: x}  # Functions can't be serialized

        with pytest.raises(
            HistoricalDataStoreError,
            match="Failed to save season 20222023 data",
        ):
            store.save_season("20222023", data)

    def test_save_season_circular_reference(self, tmp_path: Path) -> None:
        """Test error when data contains circular references."""
        store = HistoricalDataStore(tmp_path)

        # Create circular reference
        data: dict[str, Any] = {}
        data["self"] = data

        with pytest.raises(
            HistoricalDataStoreError,
            match="Failed to save season 20222023 data",
        ):
            store.save_season("20222023", data)


class TestLoadSeasonEdgeCases:
    """Tests for load_season edge cases and error paths."""

    def test_load_season_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading season data when file doesn't exist."""
        store = HistoricalDataStore(tmp_path)

        result = store.load_season("20222023")

        assert result is None

    def test_load_season_existing_file(self, tmp_path: Path) -> None:
        """Test loading existing season data."""
        store = HistoricalDataStore(tmp_path)
        data = {"teams": {"TOR": {"score": 1500}}}
        store.save_season("20222023", data)

        loaded = store.load_season("20222023")

        assert loaded == data

    def test_load_season_empty_file(self, tmp_path: Path) -> None:
        """Test loading empty JSON object."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{}", encoding="utf-8")

        loaded = store.load_season("20222023")

        assert loaded == {}

    def test_load_season_corrupted_json(self, tmp_path: Path) -> None:
        """Test error when JSON file is corrupted."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{ invalid json", encoding="utf-8")

        with pytest.raises(
            HistoricalDataStoreError,
            match="Failed to load season 20222023 data",
        ):
            store.load_season("20222023")

    def test_load_season_invalid_encoding(self, tmp_path: Path) -> None:
        """Test error when file has invalid UTF-8 encoding."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"

        # Write invalid UTF-8 bytes
        file_path.write_bytes(b"\x80\x81\x82")

        with pytest.raises(
            HistoricalDataStoreError,
            match="Failed to load season 20222023 data",
        ):
            store.load_season("20222023")

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="chmod doesn't restrict permissions on Windows",
    )
    def test_load_season_permission_denied(self, tmp_path: Path) -> None:
        """Test error when file exists but can't be read (permissions)."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{}", encoding="utf-8")
        file_path.chmod(0o000)  # No permissions

        try:
            with pytest.raises(
                HistoricalDataStoreError,
                match="Failed to load season 20222023 data",
            ):
                store.load_season("20222023")
        finally:
            # Restore permissions for cleanup
            file_path.chmod(0o644)

    def test_load_season_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test error when season path is a directory instead of file."""
        store = HistoricalDataStore(tmp_path)
        # Create a directory with the season name
        (tmp_path / "20222023.json").mkdir()

        with pytest.raises(
            HistoricalDataStoreError,
            match="Failed to load season 20222023 data",
        ):
            store.load_season("20222023")
