"""CLI commands for NHL Scrabble.

This package contains individual command modules for the NHL Scrabble CLI. Each command is defined
in its own module for better organization and maintainability.
"""

from __future__ import annotations

from nhl_scrabble.cli.commands.analytics import test_analytics
from nhl_scrabble.cli.commands.analyze import analyze
from nhl_scrabble.cli.commands.dashboard import dashboard
from nhl_scrabble.cli.commands.interactive_cmd import interactive
from nhl_scrabble.cli.commands.search import search
from nhl_scrabble.cli.commands.serve import serve
from nhl_scrabble.cli.commands.watch import watch

__all__ = [
    "analyze",
    "dashboard",
    "interactive",
    "search",
    "serve",
    "test_analytics",
    "watch",
]
