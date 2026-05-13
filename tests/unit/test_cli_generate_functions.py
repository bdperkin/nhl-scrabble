"""Comprehensive CLI tests to achieve 90%+ coverage.

This test module provides extensive coverage for the NHL Scrabble CLI, testing command-line argument
parsing, option combinations, error handling, output formats, and environment variable integration.

Target: Improve CLI coverage from ~50% to 90%+
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from nhl_scrabble.cli import cli, validate_cli_arguments, validate_output_path


class TestGenerateFunctions:
    """Tests for report generation functions."""

    def test_generate_json_report(self) -> None:
        """Test JSON report generation using formatter factory."""
        from dataclasses import asdict, dataclass

        from nhl_scrabble.formatters import get_formatter
        from nhl_scrabble.models.player import PlayerScore

        # Create sample data
        @dataclass
        class MockTeam:
            total: int
            players: list[Any]
            division: str
            conference: str
            avg_per_player: float

        team = MockTeam(
            total=100,
            players=[
                PlayerScore(
                    first_name="John",
                    last_name="Doe",
                    full_name="John Doe",
                    team="TOR",
                    division="Atlantic",
                    conference="Eastern",
                    first_score=10,
                    last_score=20,
                    full_score=30,
                ),
            ],
            division="Atlantic",
            conference="Eastern",
            avg_per_player=30.0,
        )

        # Prepare data for formatter
        data = {
            "teams": {
                "TOR": {
                    "total": team.total,
                    "players": [asdict(p) for p in team.players],
                    "division": team.division,
                    "conference": team.conference,
                    "avg_per_player": team.avg_per_player,
                },
            },
            "divisions": {},
            "conferences": {},
            "playoffs": {},
            "summary": {"total_teams": 1, "total_players": 1},
        }

        # Use formatter factory
        formatter = get_formatter("json")
        result = formatter.format(data)

        assert '"teams"' in result
        assert '"TOR"' in result

    def test_generate_search_text(self) -> None:
        """Test search text generation."""
        from nhl_scrabble.cli.commands.search import generate_search_text
        from nhl_scrabble.models.player import PlayerScore

        players = [
            PlayerScore(
                first_name="John",
                last_name="Doe",
                full_name="John Doe",
                team="TOR",
                division="Atlantic",
                conference="Eastern",
                first_score=10,
                last_score=20,
                full_score=30,
            ),
        ]

        result = generate_search_text(
            players,
            query="Doe",
            fuzzy=False,
            min_score=None,
            max_score=None,
            teams=None,
            divisions=None,
            conferences=None,
            limit=20,
        )
        assert "John Doe" in result
        assert "30" in result  # Score value appears in output

    def test_generate_search_text_fuzzy(self) -> None:
        """Test search text generation with fuzzy matching."""
        from nhl_scrabble.cli.commands.search import generate_search_text

        result = generate_search_text(
            results=[],
            query="test",
            fuzzy=True,
            min_score=50,
            max_score=100,
            teams="TOR",
            divisions="Atlantic",
            conferences="Eastern",
            limit=10,
        )
        assert "Fuzzy" in result
        assert "Minimum Score: 50" in result
        assert "Maximum Score: 100" in result

    def test_generate_search_json(self) -> None:
        """Test search JSON generation."""
        from nhl_scrabble.cli.commands.search import generate_search_json
        from nhl_scrabble.models.player import PlayerScore

        players = [
            PlayerScore(
                first_name="John",
                last_name="Doe",
                full_name="John Doe",
                team="TOR",
                division="Atlantic",
                conference="Eastern",
                first_score=10,
                last_score=20,
                full_score=30,
            ),
        ]

        stats = {"total_players": 100}
        result = generate_search_json(players, "Doe", stats)
        assert '"query"' in result
        assert '"result_count"' in result
