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
    sample_data: dict[str, Any], monkeypatch: pytest.MonkeyPatch
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
