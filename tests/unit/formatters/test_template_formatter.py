"""Tests for Template formatter."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003  # Used at runtime for fixture
from typing import Any

import pytest

from nhl_scrabble.formatters.template_formatter import TemplateFormatter


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
        },
    }


@pytest.fixture
def temp_template(tmp_path: Path) -> Path:
    """Create temporary template file."""
    template_file = tmp_path / "test.j2"
    template_file.write_text(
        "NHL Scores\n{% for abbrev, team in teams.items() %}{{ abbrev }}: {{ team.total }}\n{% endfor %}",
    )
    return template_file


def test_template_formatter_basic(sample_data: dict[str, Any], temp_template: Path) -> None:
    """Test Template formatter renders template."""
    formatter = TemplateFormatter(template_file=str(temp_template))
    output = formatter.format(sample_data)

    # Should render template
    assert "NHL Scores" in output
    assert "TOR" in output


def test_template_formatter_includes_data(sample_data: dict[str, Any], temp_template: Path) -> None:
    """Test Template formatter includes data in output."""
    formatter = TemplateFormatter(template_file=str(temp_template))
    output = formatter.format(sample_data)

    # Should include team score
    assert "1234" in output


def test_template_formatter_requires_file() -> None:
    """Test Template formatter requires template_file."""
    with pytest.raises(ValueError, match="template_file is required"):
        TemplateFormatter(template_file=None)


def test_template_formatter_file_not_found() -> None:
    """Test Template formatter raises error for missing file."""
    with pytest.raises(FileNotFoundError, match="Template file not found"):
        TemplateFormatter(template_file="/nonexistent/template.j2")


def test_template_formatter_adds_timestamp(
    sample_data: dict[str, Any],
    temp_template: Path,
) -> None:
    """Test Template formatter adds timestamp to data."""
    # Create template that uses timestamp
    timestamp_template = temp_template.parent / "timestamp.j2"
    timestamp_template.write_text("Generated: {{ timestamp }}")

    formatter = TemplateFormatter(template_file=str(timestamp_template))
    output = formatter.format(sample_data)

    # Should include timestamp
    assert "Generated:" in output
