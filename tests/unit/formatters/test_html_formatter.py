"""Tests for HTML formatter."""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.formatters.html_formatter import HTMLFormatter


@pytest.fixture
def sample_data() -> dict[str, Any]:
    """Sample analysis data for testing."""
    return {
        "teams": {
            "TOR": {
                "total": 1234,
                "avg_per_player": 45.67,
                "division": "Atlantic",
                "conference": "Eastern",
            },
            "BOS": {
                "total": 1198,
                "avg_per_player": 44.33,
                "division": "Atlantic",
                "conference": "Eastern",
            },
        },
        "summary": {
            "total_teams": 2,
            "total_players": 50,
        },
    }


def test_html_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test HTML formatter produces valid HTML."""
    formatter = HTMLFormatter()
    output = formatter.format(sample_data)

    # Should be complete HTML document
    assert "<!DOCTYPE html>" in output
    assert "<html>" in output
    assert "</html>" in output


def test_html_formatter_contains_table(sample_data: dict[str, Any]) -> None:
    """Test HTML formatter creates table."""
    formatter = HTMLFormatter()
    output = formatter.format(sample_data)

    # Should contain table with data
    assert "<table>" in output
    assert "<th>" in output
    assert "TOR" in output


def test_html_formatter_has_styling(sample_data: dict[str, Any]) -> None:
    """Test HTML formatter includes CSS styling."""
    formatter = HTMLFormatter()
    output = formatter.format(sample_data)

    # Should have style tag
    assert "<style>" in output
    assert "table {" in output


def test_html_formatter_empty_data() -> None:
    """Test HTML formatter handles empty data."""
    formatter = HTMLFormatter()
    output = formatter.format({"summary": {}})

    # Should still produce valid HTML
    assert "<!DOCTYPE html>" in output
