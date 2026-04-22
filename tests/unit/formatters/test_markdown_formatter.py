"""Tests for Markdown formatter."""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.formatters.markdown_formatter import MarkdownFormatter


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


def test_markdown_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test Markdown formatter produces Markdown."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_data)

    # Should have Markdown title
    assert "# NHL Scrabble Scores" in output


def test_markdown_formatter_has_table(sample_data: dict[str, Any]) -> None:
    """Test Markdown formatter creates table."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_data)

    # Should have table with header separator
    assert "| Rank |" in output
    assert "|------|" in output


def test_markdown_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test Markdown formatter includes data."""
    formatter = MarkdownFormatter()
    output = formatter.format(sample_data)

    # Should contain team data
    assert "TOR" in output
    assert "1234" in output


def test_markdown_formatter_empty_data() -> None:
    """Test Markdown formatter handles empty data."""
    formatter = MarkdownFormatter()
    output = formatter.format({"summary": {}})

    # Should still have title
    assert "# NHL Scrabble Scores" in output
