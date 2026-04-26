"""Tests for XML formatter."""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.formatters.xml_formatter import XMLFormatter


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Sample analysis data for testing."""
    return {
        "teams": {
            "TOR": {
                "total": 1234,
                "division": "Atlantic",
            },
        },
        "summary": {
            "total_teams": 2,
        },
    }


def test_xml_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test XML formatter produces valid XML."""
    pytest.importorskip("dicttoxml")

    formatter = XMLFormatter()
    output = formatter.format(sample_data)

    # Should start with XML declaration
    assert output.startswith("<?xml")


def test_xml_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test XML formatter includes data."""
    pytest.importorskip("dicttoxml")

    formatter = XMLFormatter()
    output = formatter.format(sample_data)

    # Should contain root element and data
    assert "<nhl_scrabble>" in output
    assert "<teams>" in output


def test_xml_formatter_import_error_without_dicttoxml(
    sample_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test XML formatter raises ImportError when dicttoxml not installed."""
    # Mock import to fail
    import builtins

    original_import = builtins.__import__

    def mock_import(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "dicttoxml":
            raise ImportError("No module named 'dicttoxml'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    formatter = XMLFormatter()
    with pytest.raises(ImportError, match="dicttoxml is required"):
        formatter.format(sample_data)


def test_xml_formatter_suppresses_dicttoxml_logging(
    sample_data: dict[str, Any],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test XML formatter suppresses verbose dicttoxml INFO logging.

    Related to issue #366 - dicttoxml library logs verbose INFO messages
    showing entire data dictionary during conversion, which clutters output.
    This test verifies dicttoxml logger is set to WARNING level.
    """
    pytest.importorskip("dicttoxml")

    import logging

    # Capture logs at INFO level
    caplog.set_level(logging.INFO)

    formatter = XMLFormatter()
    output = formatter.format(sample_data)

    # Should produce valid XML
    assert "<nhl_scrabble>" in output

    # Should NOT have dicttoxml INFO messages in logs
    # (dicttoxml logs things like "Inside unicode_me(). val = ...")
    dicttoxml_logs = [record for record in caplog.records if record.name == "dicttoxml"]

    # All dicttoxml logs should be WARNING or higher (no INFO/DEBUG)
    info_logs = [log for log in dicttoxml_logs if log.levelno < logging.WARNING]
    assert len(info_logs) == 0, (
        f"dicttoxml should not log at INFO level, but got {len(info_logs)} INFO messages: "
        f"{[log.message for log in info_logs]}"
    )
