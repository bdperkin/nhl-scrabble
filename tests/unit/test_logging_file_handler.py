"""Tests for file-based logging functionality."""

import logging
import shutil
from pathlib import Path

import pytest

from nhl_scrabble.logging_config import setup_logging


def test_setup_logging_with_file(tmp_path: Path) -> None:
    """Test file-based logging creates log file and writes messages."""
    log_file = tmp_path / "test.log"

    setup_logging(log_file=log_file)

    # Verify file created
    assert log_file.exists()

    # Verify logging works
    test_logger = logging.getLogger("test_file_logging")
    test_logger.info("Test message")

    # Verify message in file
    log_content = log_file.read_text()
    assert "Test message" in log_content
    assert "test_file_logging" in log_content


def test_setup_logging_rotation(tmp_path: Path) -> None:
    """Test log rotation creates backup files when size limit exceeded."""
    log_file = tmp_path / "test.log"

    # Small max_bytes to force rotation
    setup_logging(log_file=log_file, max_bytes=100, backup_count=2)

    test_logger = logging.getLogger("test_rotation")
    # Write enough messages to force rotation
    for i in range(50):
        test_logger.info(f"Message {i} " * 10)  # Make messages longer to hit size limit faster

    # Verify rotation occurred (at least one backup file should exist)
    backup_file = tmp_path / "test.log.1"
    assert backup_file.exists(), "Log rotation should have created backup file"


def test_setup_logging_creates_directory(tmp_path: Path) -> None:
    """Test that parent directories are created automatically."""
    log_file = tmp_path / "logs" / "app" / "test.log"

    # Verify directory doesn't exist yet
    assert not log_file.parent.exists()

    setup_logging(log_file=log_file)

    # Verify directory and file created
    assert log_file.parent.exists()
    assert log_file.exists()


def test_setup_logging_file_and_console(tmp_path: Path) -> None:
    """Test that logging goes to both file and console when file logging enabled."""
    log_file = tmp_path / "test.log"

    setup_logging(log_file=log_file)

    test_logger = logging.getLogger("test_dual_output")
    test_logger.info("Dual output message")

    # Verify message in file
    log_content = log_file.read_text()
    assert "Dual output message" in log_content

    # Verify console handler exists
    root_logger = logging.getLogger()
    handlers = root_logger.handlers
    assert len(handlers) >= 2  # Should have both console and file handlers

    # Verify we have a file handler
    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) >= 1, "Should have at least one file handler"


def test_setup_logging_without_file() -> None:
    """Test that logging works without file when log_file not specified."""
    setup_logging(log_file=None)

    test_logger = logging.getLogger("test_console_only")
    test_logger.info("Console only message")

    # Verify only console handler exists (no file handlers)
    root_logger = logging.getLogger()
    handlers = root_logger.handlers
    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 0, "Should have no file handlers"

    # Should have at least console handler
    assert len(handlers) >= 1, "Should have at least console handler"


def test_setup_logging_verbose_mode(tmp_path: Path) -> None:
    """Test that verbose mode enables DEBUG level in both console and file."""
    log_file = tmp_path / "debug.log"

    setup_logging(verbose=True, log_file=log_file)

    test_logger = logging.getLogger("test_verbose")
    test_logger.debug("Debug message")

    # Verify DEBUG message in file
    log_content = log_file.read_text()
    assert "Debug message" in log_content


def test_setup_logging_backup_count(tmp_path: Path) -> None:
    """Test that backup_count limits number of backup files."""
    log_file = tmp_path / "test.log"

    # Only keep 2 backups
    setup_logging(log_file=log_file, max_bytes=50, backup_count=2)

    test_logger = logging.getLogger("test_backup_limit")
    # Write many messages to force multiple rotations
    for i in range(200):
        test_logger.info(f"Message {i} with some padding text to make it longer")

    # Count backup files
    backup_files = list(tmp_path.glob("test.log.*"))

    # Should have at most 2 backups (.1 and .2)
    assert len(backup_files) <= 2, f"Expected at most 2 backup files, got {len(backup_files)}"


def test_setup_logging_json_output(tmp_path: Path) -> None:
    """Test that JSON output format works with file logging."""
    log_file = tmp_path / "test.json"

    setup_logging(json_output=True, log_file=log_file)

    test_logger = logging.getLogger("test_json")
    test_logger.info("JSON test message")

    # Verify JSON format in file
    log_content = log_file.read_text()
    assert (
        '"message": "JSON test message"' in log_content
        or '"message":"JSON test message"' in log_content
    )


def test_setup_logging_sanitize_logs(tmp_path: Path) -> None:
    """Test that sensitive data is sanitized in file logs."""
    log_file = tmp_path / "test.log"

    setup_logging(sanitize_logs=True, log_file=log_file)

    test_logger = logging.getLogger("test_sanitize")
    test_logger.info("API key is api_key=abc123")

    # Verify sensitive data is sanitized
    log_content = log_file.read_text()
    assert "api_key=***" in log_content or "api_key=[REDACTED]" in log_content
    assert "abc123" not in log_content


def test_setup_logging_file_encoding(tmp_path: Path) -> None:
    """Test that log files use UTF-8 encoding for non-ASCII characters."""
    log_file = tmp_path / "test.log"

    setup_logging(log_file=log_file)

    test_logger = logging.getLogger("test_encoding")
    # Test various Unicode characters
    test_logger.info("Unicode test: Ñícolás 日本語 🏒")

    # Verify Unicode characters in file
    log_content = log_file.read_text(encoding="utf-8")
    assert "Ñícolás" in log_content
    assert "日本語" in log_content
    assert "🏒" in log_content


def test_setup_logging_multiple_calls(tmp_path: Path) -> None:
    """Test that calling setup_logging multiple times replaces handlers correctly."""
    log_file1 = tmp_path / "test1.log"
    log_file2 = tmp_path / "test2.log"

    # First setup
    setup_logging(log_file=log_file1)
    test_logger = logging.getLogger("test_multiple")
    test_logger.info("Message 1")

    # Second setup (should replace handlers)
    setup_logging(log_file=log_file2)
    test_logger.info("Message 2")

    # Verify Message 1 in first file
    assert "Message 1" in log_file1.read_text()

    # Verify Message 2 in second file
    assert "Message 2" in log_file2.read_text()

    # Verify Message 2 NOT in first file (handlers were replaced)
    assert "Message 2" not in log_file1.read_text()


@pytest.mark.skipif(
    shutil.which("sphinx-build") is None,
    reason="sphinx-build not found (optional dependencies not installed)",
)
def test_setup_logging_info_level_by_default(tmp_path: Path) -> None:
    """Test that INFO level is used by default (not DEBUG)."""
    log_file = tmp_path / "test.log"

    setup_logging(verbose=False, log_file=log_file)

    test_logger = logging.getLogger("test_info_level")
    test_logger.debug("Debug message (should not appear)")
    test_logger.info("Info message (should appear)")

    log_content = log_file.read_text()

    # INFO should appear
    assert "Info message" in log_content

    # DEBUG should NOT appear
    assert "Debug message" not in log_content
