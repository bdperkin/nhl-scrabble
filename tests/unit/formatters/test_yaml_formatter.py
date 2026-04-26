"""Tests for YAML formatter."""

from __future__ import annotations

from typing import Any

import pytest

from nhl_scrabble.formatters.yaml_formatter import YAMLFormatter


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


def test_yaml_formatter_basic(sample_data: dict[str, Any]) -> None:
    """Test YAML formatter produces valid YAML."""
    yaml = pytest.importorskip("yaml")  # Skip test if PyYAML not installed

    formatter = YAMLFormatter()
    output = formatter.format(sample_data)

    # Should be valid YAML
    parsed = yaml.safe_load(output)
    assert isinstance(parsed, dict)


def test_yaml_formatter_contains_data(sample_data: dict[str, Any]) -> None:
    """Test YAML formatter includes all data."""
    yaml = pytest.importorskip("yaml")

    formatter = YAMLFormatter()
    output = formatter.format(sample_data)
    parsed = yaml.safe_load(output)

    assert "teams" in parsed
    assert "TOR" in parsed["teams"]
    assert parsed["teams"]["TOR"]["total"] == 1234


def test_yaml_formatter_readable(sample_data: dict[str, Any]) -> None:
    """Test YAML formatter produces human-readable output."""
    pytest.importorskip("yaml")

    formatter = YAMLFormatter()
    output = formatter.format(sample_data)

    # Should contain key names
    assert "teams:" in output
    assert "TOR:" in output


def test_yaml_formatter_import_error_without_pyyaml(
    sample_data: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test YAML formatter raises ImportError when PyYAML not installed."""
    # Mock import to fail
    import builtins

    original_import = builtins.__import__

    def mock_import(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "yaml":
            raise ImportError("No module named 'yaml'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    formatter = YAMLFormatter()
    with pytest.raises(ImportError, match="PyYAML is required"):
        formatter.format(sample_data)
