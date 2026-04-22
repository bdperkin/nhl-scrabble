"""Tests for Text formatter."""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.formatters.text_formatter import TextFormatter


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


def test_text_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test Text formatter produces output."""
    formatter = TextFormatter()
    output = formatter.format(sample_data)

    # Should have content
    assert len(output) > 0


def test_text_formatter_has_title(sample_data: dict[str, Any]) -> None:
    """Test Text formatter includes title."""
    formatter = TextFormatter()
    output = formatter.format(sample_data)

    # Should have title
    assert "NHL SCRABBLE SCORES" in output


def test_text_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test Text formatter includes data."""
    formatter = TextFormatter()
    output = formatter.format(sample_data)

    # Should contain team data
    assert "TOR" in output
    assert "BOS" in output
    assert "1234" in output


def test_text_formatter_has_separators(sample_data: dict[str, Any]) -> None:
    """Test Text formatter uses separators."""
    formatter = TextFormatter()
    output = formatter.format(sample_data)

    # Should have separator lines
    assert "=" * 80 in output
    assert "-" * 80 in output


def test_text_formatter_empty_data() -> None:
    """Test Text formatter handles empty data."""
    formatter = TextFormatter()
    output = formatter.format({"summary": {}})

    # Should still have title
    assert "NHL SCRABBLE SCORES" in output
