"""Tests for CSV formatter."""

from __future__ import annotations

import csv
from io import StringIO
from typing import Any

import pytest

from nhl_scrabble.formatters.csv_formatter import CSVFormatter


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


def test_csv_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test CSV formatter produces valid CSV."""
    formatter = CSVFormatter()
    output = formatter.format(sample_data)

    # Should be parseable as CSV
    reader = csv.reader(StringIO(output))
    rows = list(reader)
    assert len(rows) > 0


def test_csv_formatter_has_header(sample_data: dict[str, Any]) -> None:
    """Test CSV formatter includes header row."""
    formatter = CSVFormatter()
    output = formatter.format(sample_data)

    reader = csv.reader(StringIO(output))
    rows = list(reader)

    # First row should be header
    assert "Rank" in rows[0]
    assert "Team" in rows[0]


def test_csv_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test CSV formatter includes data."""
    formatter = CSVFormatter()
    output = formatter.format(sample_data)

    # Should contain team abbreviations
    assert "TOR" in output
    assert "BOS" in output


def test_csv_formatter_proper_format(sample_data: dict[str, Any]) -> None:
    """Test CSV formatter uses proper CSV format."""
    formatter = CSVFormatter()
    output = formatter.format(sample_data)

    # Should have commas as separators
    assert "," in output


def test_csv_formatter_empty_data() -> None:
    """Test CSV formatter handles empty data."""
    formatter = CSVFormatter()
    output = formatter.format({})

    reader = csv.reader(StringIO(output))
    rows = list(reader)

    # Should still have header
    assert len(rows) >= 1
