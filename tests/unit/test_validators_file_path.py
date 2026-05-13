"""Unit tests for input validation utilities."""

from pathlib import Path

import pytest

from nhl_scrabble.validators import ValidationError, validate_file_path


class TestValidateFilePath:
    """Tests for validate_file_path()."""

    def test_valid_path(self, tmp_path: Path) -> None:
        """Test valid file path."""
        file_path = tmp_path / "output.txt"
        result = validate_file_path(str(file_path))
        assert isinstance(result, Path)
        assert result.name == "output.txt"

    def test_path_traversal_blocked(self) -> None:
        """Test path traversal attack is blocked."""
        with pytest.raises(ValidationError, match="suspicious pattern"):
            validate_file_path("../../../etc/passwd")

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test error when parent directory doesn't exist."""
        # Make tmp_path the current directory for this test
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(ValidationError, match="does not exist"):
                validate_file_path("nonexistent/dir/file.txt")
        finally:
            os.chdir(original_cwd)

    def test_invalid_filename_characters(self, tmp_path: Path) -> None:
        """Test filename with invalid characters is rejected."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_file_path(str(tmp_path / "file<>.txt"))

    def test_existing_file_no_overwrite(self, tmp_path: Path) -> None:
        """Test error when file exists and overwrite not allowed."""
        existing = tmp_path / "existing.txt"
        existing.write_text("data")

        with pytest.raises(ValidationError, match="already exists"):
            validate_file_path(str(existing), allow_overwrite=False)

    def test_existing_file_with_overwrite(self, tmp_path: Path) -> None:
        """Test success when file exists but overwrite allowed."""
        existing = tmp_path / "existing.txt"
        existing.write_text("data")

        result = validate_file_path(str(existing), allow_overwrite=True)
        assert result == existing

    def test_path_with_dangerous_characters(self, tmp_path: Path) -> None:
        """Test filename with dangerous special chars is rejected."""
        # Note: Spaces would be rejected by our \w pattern which only allows alphanumeric
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_file_path(str(tmp_path / "dangerous!file.txt"))

    def test_hidden_file(self) -> None:
        """Test hidden file (starting with dot) is allowed."""
        # Use current directory to avoid path traversal check
        result = validate_file_path(".hidden")
        assert result.name == ".hidden"

    def test_path_not_directory(self, tmp_path: Path) -> None:
        """Test error when parent exists but is not a directory."""
        # Create a regular file
        not_a_dir = tmp_path / "notdir"
        not_a_dir.write_text("content")

        # Try to create file with non-directory parent
        with pytest.raises(ValidationError, match="not a directory"):
            validate_file_path(str(not_a_dir / "file.txt"))

    def test_readonly_parent_directory(self, tmp_path: Path) -> None:
        """Test error when parent directory is read-only."""
        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        try:
            with pytest.raises(ValidationError, match="not writable"):
                validate_file_path(str(readonly_dir / "file.txt"))
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)

    def test_readonly_file_overwrite(self, tmp_path: Path) -> None:
        """Test error when trying to overwrite read-only file."""
        # Create read-only file
        readonly_file = tmp_path / "readonly.txt"
        readonly_file.write_text("content")
        readonly_file.chmod(0o444)  # Read-only

        try:
            with pytest.raises(ValidationError, match="not writable"):
                validate_file_path(str(readonly_file), allow_overwrite=True)
        finally:
            # Restore permissions for cleanup
            readonly_file.chmod(0o644)

    def test_complex_path_traversal_patterns(self) -> None:
        """Test various path traversal attack patterns."""
        patterns = [
            "../etc/passwd",
            "../../etc/passwd",
            "../../../etc/passwd",
            "/..",
            "/../../etc/passwd",
            "file/../../../etc/passwd",
        ]
        for pattern in patterns:
            with pytest.raises(ValidationError, match="suspicious pattern"):
                validate_file_path(pattern)

    def test_invalid_path_value_error(self, tmp_path: Path) -> None:
        """Test invalid path conversion raises ValidationError."""
        # Null bytes in path cause ValueError in Path()
        with pytest.raises(ValidationError, match="Invalid path"):
            validate_file_path(str(tmp_path / "file\x00.txt"))

    def test_path_resolution(self, tmp_path: Path) -> None:
        """Test path is resolved to absolute path."""
        # Use relative path within tmp_path
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = validate_file_path("test.txt")
            # Result should be absolute
            assert result.is_absolute()
            assert str(result).startswith(str(tmp_path))
        finally:
            os.chdir(original_cwd)
