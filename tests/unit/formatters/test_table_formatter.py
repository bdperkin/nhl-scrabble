"""Tests for Table formatter."""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.formatters.table_formatter import TableFormatter


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
    }


def test_table_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test Table formatter produces output."""
    formatter = TableFormatter()
    output = formatter.format(sample_data)

    # Should have content
    assert len(output) > 0


def test_table_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test Table formatter includes data."""
    formatter = TableFormatter()
    output = formatter.format(sample_data)

    # Should contain team abbreviations
    assert "TOR" in output
    assert "BOS" in output


def test_table_formatter_has_box_drawing(sample_data: dict[str, Any]) -> None:
    """Test Table formatter uses box-drawing characters."""
    formatter = TableFormatter()
    output = formatter.format(sample_data)

    # Rich tables use box-drawing characters
    # Check for any common box-drawing character
    has_box_drawing = any(
        char in output
        for char in ["┃", "│", "─", "━", "┏", "┓", "┗", "┛", "┌", "┐", "└", "┘", "├", "┤"]
    )
    assert has_box_drawing


def test_table_formatter_empty_data() -> None:
    """Test Table formatter handles empty data."""
    formatter = TableFormatter()
    output = formatter.format({})

    # Should still produce some output
    assert len(output) > 0
