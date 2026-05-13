"""Command-line interface for NHL Scrabble.

This package provides the CLI for the NHL Scrabble Score Analyzer.
The monolithic cli.py has been refactored into a modular structure:

- validators.py: Argument validation functions
- excel.py: Excel report generation
- orchestration.py: Main analysis orchestration (run_analysis)
- commands/: Individual CLI commands (analyze, search, serve, etc.)
"""

from __future__ import annotations

import click

from nhl_scrabble import __version__

# Import commands
from nhl_scrabble.cli.commands.analyze import analyze
from nhl_scrabble.cli.commands.dashboard import dashboard
from nhl_scrabble.cli.commands.interactive_cmd import interactive
from nhl_scrabble.cli.commands.search import search
from nhl_scrabble.cli.commands.serve import serve
from nhl_scrabble.cli.commands.test_analytics import test_analytics
from nhl_scrabble.cli.commands.watch import watch

# Import utilities for public API
from nhl_scrabble.cli.excel import generate_excel_report
from nhl_scrabble.cli.orchestration import run_analysis
from nhl_scrabble.cli.validators import validate_cli_arguments, validate_output_path


# Define the main CLI group
@click.group()
@click.version_option(__version__, "-V", "--version", prog_name="nhl-scrabble")
@click.help_option("-h", "--help")
def cli() -> None:
    """NHL Roster Scrabble Score Analyzer.

    Fetch NHL roster data and calculate Scrabble scores for player names. Generate comprehensive
    reports showing team, division, and conference standings.
    """


# Register all commands with the CLI group
cli.add_command(analyze)
cli.add_command(interactive)
cli.add_command(search)
cli.add_command(serve)
cli.add_command(dashboard)
cli.add_command(watch)
cli.add_command(test_analytics)

# Public API exports
__all__ = [
    "cli",
    "validate_output_path",
    "validate_cli_arguments",
    "generate_excel_report",
    "run_analysis",
    "analyze",
    "interactive",
    "search",
    "serve",
    "dashboard",
    "watch",
    "test_analytics",
]
