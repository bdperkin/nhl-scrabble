"""Tests for JSON formatter."""

from __future__ import annotations

import json
from typing import Any

import pytest

from nhl_scrabble.formatters.json_formatter import JSONFormatter


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


def test_json_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test JSON formatter produces valid JSON."""
    formatter = JSONFormatter()
    output = formatter.format(sample_data)

    # Should be valid JSON
    parsed = json.loads(output)
    assert isinstance(parsed, dict)


def test_json_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test JSON formatter includes all data."""
    formatter = JSONFormatter()
    output = formatter.format(sample_data)
    parsed = json.loads(output)

    assert "teams" in parsed
    assert "TOR" in parsed["teams"]
    assert parsed["teams"]["TOR"]["total"] == 1234


def test_json_formatter_pretty_printed(sample_data: dict[str, Any]) -> None:
    """Test JSON formatter uses pretty-printing."""
    formatter = JSONFormatter()
    output = formatter.format(sample_data)

    # Pretty-printed JSON should have newlines
    assert "\n" in output


def test_json_formatter_empty_data() -> None:
    """Test JSON formatter handles empty data."""
    formatter = JSONFormatter()
    output = formatter.format({})

    parsed = json.loads(output)
    assert parsed == {}
