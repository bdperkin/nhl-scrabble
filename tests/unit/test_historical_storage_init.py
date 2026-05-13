"""Tests for HistoricalDataStore initialization and setup."""

import sys
from pathlib import Path

import pytest

from nhl_scrabble.storage.historical import HistoricalDataStore, HistoricalDataStoreError


class TestHistoricalDataStoreInit:
    """Tests for HistoricalDataStore initialization edge cases."""

    def test_init_with_default_directory(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
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

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="chmod doesn't restrict permissions on Windows",
    )
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
