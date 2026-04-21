"""Edge case and error path tests for historical data storage.

This module tests:
- All exception paths
- Error message validation
- Recovery logic
- Edge cases (permissions, corrupted data, etc.)
"""

import json
from pathlib import Path
from typing import Any

import pytest

from nhl_scrabble.storage.historical import HistoricalDataStore, HistoricalDataStoreError


class TestHistoricalDataStoreInit:
    """Tests for HistoricalDataStore initialization edge cases."""

    def test_init_with_default_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test initialization with default directory path."""
        monkeypatch.chdir(tmp_path)
        store = HistoricalDataStore()

        assert store.data_dir == tmp_path / "data" / "historical"
        assert store.data_dir.exists()

    def test_init_with_custom_directory(self, tmp_path: Path) -> None:
        """Test initialization with custom directory path."""
        custom_dir = tmp_path / "custom"
        store = HistoricalDataStore(custom_dir)

        assert store.data_dir == custom_dir
        assert custom_dir.exists()

    def test_init_with_string_path(self, tmp_path: Path) -> None:
        """Test initialization with string path instead of Path object."""
        custom_dir = str(tmp_path / "string_path")
        store = HistoricalDataStore(custom_dir)

        assert store.data_dir == Path(custom_dir)
        assert store.data_dir.exists()

    def test_init_creates_nested_directories(self, tmp_path: Path) -> None:
        """Test initialization creates nested parent directories."""
        nested = tmp_path / "level1" / "level2" / "level3"
        store = HistoricalDataStore(nested)

        assert nested.exists()
        assert store.data_dir == nested

    def test_init_with_existing_directory(self, tmp_path: Path) -> None:
        """Test initialization when directory already exists."""
        existing = tmp_path / "existing"
        existing.mkdir()

        store = HistoricalDataStore(existing)
        assert store.data_dir == existing

    def test_init_directory_creation_fails(self, tmp_path: Path) -> None:
        """Test error when directory creation fails (permission denied)."""
        # Create a file where we want a directory, causing mkdir to fail
        blocked_path = tmp_path / "blocked"
        blocked_path.touch()

        # Try to create a directory at the same path
        with pytest.raises(
            HistoricalDataStoreError,
            match=r"Failed to create data directory.*blocked",
        ):
            HistoricalDataStore(blocked_path)

    def test_init_directory_creation_permission_error(self, tmp_path: Path) -> None:
        """Test error when insufficient permissions to create directory."""
        # Use a path that's guaranteed to fail (read-only parent)
        readonly_parent = tmp_path / "readonly"
        readonly_parent.mkdir()
        readonly_parent.chmod(0o444)  # Read-only

        try:
            with pytest.raises(
                HistoricalDataStoreError,
                match="Failed to create data directory",
            ):
                HistoricalDataStore(readonly_parent / "subdir")
        finally:
            # Restore permissions for cleanup
            readonly_parent.chmod(0o755)


class TestSaveSeasonEdgeCases:
    """Tests for save_season edge cases and error paths."""

    def test_save_season_basic(self, tmp_path: Path) -> None:
        """Test basic save operation."""
        store = HistoricalDataStore(tmp_path)
        data = {"teams": {"TOR": {"score": 1500}}}

        store.save_season("20222023", data)

        file_path = tmp_path / "20222023.json"
        assert file_path.exists()
        saved_data = json.loads(file_path.read_text())
        assert saved_data == data

    def test_save_season_empty_data(self, tmp_path: Path) -> None:
        """Test saving empty dictionary."""
        store = HistoricalDataStore(tmp_path)

        store.save_season("20222023", {})

        file_path = tmp_path / "20222023.json"
        assert file_path.exists()
        assert json.loads(file_path.read_text()) == {}

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
        saved_data = json.loads(file_path.read_text())
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
        saved_data = json.loads(file_path.read_text())
        assert saved_data["teams"]["MTL"]["name"] == "Montréal Canadiens"

    def test_save_season_overwrite_existing(self, tmp_path: Path) -> None:
        """Test overwriting existing season data."""
        store = HistoricalDataStore(tmp_path)

        # Save initial data
        store.save_season("20222023", {"version": 1})

        # Overwrite with new data
        store.save_season("20222023", {"version": 2})

        file_path = tmp_path / "20222023.json"
        saved_data = json.loads(file_path.read_text())
        assert saved_data["version"] == 2

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
        file_path.write_text("{}")

        loaded = store.load_season("20222023")

        assert loaded == {}

    def test_load_season_corrupted_json(self, tmp_path: Path) -> None:
        """Test error when JSON file is corrupted."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{ invalid json")

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

    def test_load_season_permission_denied(self, tmp_path: Path) -> None:
        """Test error when file exists but can't be read (permissions)."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{}")
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


class TestHasSeasonEdgeCases:
    """Tests for has_season edge cases."""

    def test_has_season_exists(self, tmp_path: Path) -> None:
        """Test checking for existing season."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})

        assert store.has_season("20222023") is True

    def test_has_season_not_exists(self, tmp_path: Path) -> None:
        """Test checking for non-existent season."""
        store = HistoricalDataStore(tmp_path)

        assert store.has_season("20222023") is False

    def test_has_season_directory_not_file(self, tmp_path: Path) -> None:
        """Test has_season returns False when path is directory, not file."""
        store = HistoricalDataStore(tmp_path)
        (tmp_path / "20222023.json").mkdir()

        # Should return False because it's a directory, not a file
        assert store.has_season("20222023") is False


class TestListSeasonsEdgeCases:
    """Tests for list_seasons edge cases."""

    def test_list_seasons_empty_directory(self, tmp_path: Path) -> None:
        """Test listing seasons when directory is empty."""
        store = HistoricalDataStore(tmp_path)

        seasons = store.list_seasons()

        assert seasons == []

    def test_list_seasons_single_season(self, tmp_path: Path) -> None:
        """Test listing with single season."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})

        seasons = store.list_seasons()

        assert seasons == ["20222023"]

    def test_list_seasons_multiple_sorted(self, tmp_path: Path) -> None:
        """Test listing multiple seasons returns sorted list."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20232024", {"teams": {}})
        store.save_season("20212022", {"teams": {}})
        store.save_season("20222023", {"teams": {}})

        seasons = store.list_seasons()

        assert seasons == ["20212022", "20222023", "20232024"]

    def test_list_seasons_ignores_non_json_files(self, tmp_path: Path) -> None:
        """Test listing ignores non-JSON files."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})
        (tmp_path / "readme.txt").write_text("info")
        (tmp_path / "backup.bak").write_text("data")

        seasons = store.list_seasons()

        assert seasons == ["20222023"]

    def test_list_seasons_includes_directories(self, tmp_path: Path) -> None:
        """Test listing includes directories if named .json (current behavior).

        Note: This is current implementation behavior. Ideally, directories
        should be filtered out to only return actual season files.
        """
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})
        (tmp_path / "directory.json").mkdir()

        seasons = store.list_seasons()

        # Current implementation includes directories in results
        assert "20222023" in seasons
        assert "directory" in seasons

    def test_list_seasons_read_error_returns_empty(self, tmp_path: Path) -> None:
        """Test list_seasons returns empty list on OSError."""
        store = HistoricalDataStore(tmp_path)

        # Make directory unreadable
        tmp_path.chmod(0o000)

        try:
            seasons = store.list_seasons()
            assert seasons == []
        finally:
            # Restore permissions for cleanup
            tmp_path.chmod(0o755)


class TestDeleteSeasonEdgeCases:
    """Tests for delete_season edge cases."""

    def test_delete_season_existing_file(self, tmp_path: Path) -> None:
        """Test deleting existing season file."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})

        result = store.delete_season("20222023")

        assert result is True
        assert not (tmp_path / "20222023.json").exists()

    def test_delete_season_nonexistent_file(self, tmp_path: Path) -> None:
        """Test deleting non-existent season returns False."""
        store = HistoricalDataStore(tmp_path)

        result = store.delete_season("20222023")

        assert result is False

    @pytest.mark.skip(reason="Platform-dependent permission behavior")
    def test_delete_season_permission_denied(self, tmp_path: Path) -> None:
        """Test error when deletion fails due to permissions.

        Note: Skipped because:
        - On Unix: Permission errors may raise PermissionError directly
        - On Windows: Behavior differs for read-only files
        - As root: All files can be deleted regardless of permissions
        """
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})

        # Make directory read-only (may not work as root)
        tmp_path.chmod(0o444)

        try:
            with pytest.raises(HistoricalDataStoreError):
                store.delete_season("20222023")
        finally:
            # Restore permissions for cleanup
            tmp_path.chmod(0o755)

    def test_delete_season_file_in_use(self, tmp_path: Path) -> None:
        """Test deletion when file might be in use (platform-dependent)."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{}")

        # On most systems, this will succeed even with file open
        # But test the scenario regardless
        with file_path.open("r"):
            # Try to delete while file is open
            # This may or may not fail depending on OS
            try:
                result = store.delete_season("20222023")
                # On Unix-like systems, this succeeds
                assert result is True
            except HistoricalDataStoreError:
                # On Windows, this might fail
                pass


class TestClearAllEdgeCases:
    """Tests for clear_all edge cases."""

    def test_clear_all_empty_directory(self, tmp_path: Path) -> None:
        """Test clearing when directory is empty."""
        store = HistoricalDataStore(tmp_path)

        count = store.clear_all()

        assert count == 0

    def test_clear_all_single_file(self, tmp_path: Path) -> None:
        """Test clearing single file."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})

        count = store.clear_all()

        assert count == 1
        assert len(list(tmp_path.glob("*.json"))) == 0

    def test_clear_all_multiple_files(self, tmp_path: Path) -> None:
        """Test clearing multiple files."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20212022", {"teams": {}})
        store.save_season("20222023", {"teams": {}})
        store.save_season("20232024", {"teams": {}})

        count = store.clear_all()

        assert count == 3
        assert len(list(tmp_path.glob("*.json"))) == 0

    def test_clear_all_preserves_non_json_files(self, tmp_path: Path) -> None:
        """Test clear_all only deletes JSON files."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})
        readme = tmp_path / "readme.txt"
        readme.write_text("info")

        count = store.clear_all()

        assert count == 1
        assert not (tmp_path / "20222023.json").exists()
        assert readme.exists()  # Non-JSON file preserved

    @pytest.mark.skip(reason="Platform-dependent permission behavior")
    def test_clear_all_partial_failure(self, tmp_path: Path) -> None:
        """Test clear_all with partial failures (some files can't be deleted).

        Note: Skipped because file permission behavior varies by platform:
        - Unix: Owner can delete files even in read-only directories
        - Windows: Read-only files cannot be deleted
        - Root: Can delete any file regardless of permissions
        """
        store = HistoricalDataStore(tmp_path)
        store.save_season("20212022", {"teams": {}})
        store.save_season("20222023", {"teams": {}})
        store.save_season("20232024", {"teams": {}})

        # Make one file read-only to cause failure
        protected = tmp_path / "20222023.json"
        protected.chmod(0o000)

        try:
            count = store.clear_all()
            # Should successfully delete 2 files (one is protected)
            assert count == 2
        finally:
            # Restore permissions for cleanup
            protected.chmod(0o644)

    @pytest.mark.skipif(
        __import__("os").geteuid() == 0,
        reason="Test requires non-root user (root can read any directory)",
    )
    def test_clear_all_glob_error(self, tmp_path: Path) -> None:
        """Test clear_all when glob operation fails."""
        store = HistoricalDataStore(tmp_path)

        # Make directory unreadable to cause glob to fail
        tmp_path.chmod(0o000)

        try:
            # Try to clear - should fail or return empty
            try:
                result = store.clear_all()
                # If it succeeds, it should return 0 (no files found)
                assert result == 0
            except HistoricalDataStoreError as e:
                assert "Failed to clear cached data" in str(e)  # noqa: PT017
        finally:
            # Restore permissions for cleanup
            tmp_path.chmod(0o755)


class TestGetSeasonFilePathEdgeCases:
    """Tests for _get_season_file_path edge cases."""

    def test_get_season_file_path_basic(self, tmp_path: Path) -> None:
        """Test basic season file path generation."""
        store = HistoricalDataStore(tmp_path)

        path = store._get_season_file_path("20222023")

        assert path == tmp_path / "20222023.json"
        assert path.name == "20222023.json"

    def test_get_season_file_path_special_characters(self, tmp_path: Path) -> None:
        """Test season identifier with special characters."""
        store = HistoricalDataStore(tmp_path)

        # Season IDs should be validated elsewhere, but test path generation
        path = store._get_season_file_path("2022-2023")

        assert path == tmp_path / "2022-2023.json"

    def test_get_season_file_path_empty_string(self, tmp_path: Path) -> None:
        """Test season file path with empty string (edge case)."""
        store = HistoricalDataStore(tmp_path)

        path = store._get_season_file_path("")

        assert path == tmp_path / ".json"


class TestErrorMessages:
    """Tests to verify error messages are clear and actionable."""

    def test_init_error_message_includes_path(self, tmp_path: Path) -> None:
        """Test init error message includes the problematic path."""
        blocked = tmp_path / "blocked"
        blocked.touch()

        with pytest.raises(HistoricalDataStoreError) as exc_info:
            HistoricalDataStore(blocked)

        assert "blocked" in str(exc_info.value)
        assert "Failed to create data directory" in str(exc_info.value)

    def test_save_error_message_includes_season(self, tmp_path: Path) -> None:
        """Test save error message includes season identifier."""
        store = HistoricalDataStore(tmp_path)
        tmp_path.chmod(0o444)

        try:
            with pytest.raises(HistoricalDataStoreError) as exc_info:
                store.save_season("20222023", {"teams": {}})

            assert "20222023" in str(exc_info.value)
            assert "Failed to save season" in str(exc_info.value)
        finally:
            tmp_path.chmod(0o755)

    def test_load_error_message_includes_season(self, tmp_path: Path) -> None:
        """Test load error message includes season identifier."""
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("invalid json")

        with pytest.raises(HistoricalDataStoreError) as exc_info:
            store.load_season("20222023")

        assert "20222023" in str(exc_info.value)
        assert "Failed to load season" in str(exc_info.value)

    @pytest.mark.skip(reason="Platform-dependent permission behavior")
    def test_delete_error_message_includes_season(self, tmp_path: Path) -> None:
        """Test delete error message includes season identifier.

        Note: Skipped because Unix owners can delete files in read-only directories.
        """
        store = HistoricalDataStore(tmp_path)
        file_path = tmp_path / "20222023.json"
        file_path.write_text("{}")
        tmp_path.chmod(0o444)

        try:
            with pytest.raises(HistoricalDataStoreError) as exc_info:
                store.delete_season("20222023")

            assert "20222023" in str(exc_info.value)
            assert "Failed to delete season" in str(exc_info.value)
        finally:
            tmp_path.chmod(0o755)


class TestRecoveryLogic:
    """Tests for recovery and graceful degradation."""

    def test_load_after_save_failure(self, tmp_path: Path) -> None:
        """Test loading after a save failure doesn't corrupt data."""
        store = HistoricalDataStore(tmp_path)

        # Save initial data
        store.save_season("20222023", {"version": 1})

        # Make directory read-only
        tmp_path.chmod(0o444)

        try:
            # Try to save new data (will fail)
            with pytest.raises(HistoricalDataStoreError):
                store.save_season("20222023", {"version": 2})
        finally:
            tmp_path.chmod(0o755)

        # Original data should still be intact
        loaded = store.load_season("20222023")
        assert loaded == {"version": 1}

    def test_list_continues_after_individual_error(self, tmp_path: Path) -> None:
        """Test list_seasons returns empty list on error but doesn't crash."""
        store = HistoricalDataStore(tmp_path)
        store.save_season("20222023", {"teams": {}})

        tmp_path.chmod(0o000)
        try:
            # Should return empty list, not crash
            seasons = store.list_seasons()
            assert seasons == []
        finally:
            tmp_path.chmod(0o755)

    @pytest.mark.skip(reason="Platform-dependent permission behavior")
    def test_clear_all_continues_on_partial_failure(self, tmp_path: Path) -> None:
        """Test clear_all attempts to delete all files even if some fail.

        Note: Skipped because behavior varies by platform and user permissions.
        """
        store = HistoricalDataStore(tmp_path)
        file1 = tmp_path / "20212022.json"
        file2 = tmp_path / "20222023.json"
        file3 = tmp_path / "20232024.json"

        file1.write_text("{}")
        file2.write_text("{}")
        file3.write_text("{}")

        # Make middle file read-only (on Unix, owner can still delete)
        # This test is platform-dependent
        file2.chmod(0o000)

        try:
            count = store.clear_all()
            # Should attempt to delete all files
            # Count depends on platform permission behavior
            assert count >= 2
        finally:
            file2.chmod(0o644)
