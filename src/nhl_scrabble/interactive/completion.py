"""Tab completion support for interactive shell."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from prompt_toolkit.completion import WordCompleter

if TYPE_CHECKING:
    from nhl_scrabble.models.team import TeamScore


def get_completer(commands: list[str], data: dict[str, Any] | None) -> WordCompleter:
    """Get command completer with team/player names.

    Args:
        commands: List of available commands
        data: Shell data dictionary (optional)

    Returns:
        WordCompleter configured with commands and data
    """
    if not data:
        return WordCompleter(commands, ignore_case=True)

    # Add team abbreviations
    teams: list[TeamScore] = data["teams"]
    team_abbrevs = [team.abbrev for team in teams]

    # Add player names (first 100 for performance)
    players: list[str] = []
    for team in teams:
        players.extend([p.full_name for p in team.players[:10]])

    words = commands + team_abbrevs + players[:100]
    return WordCompleter(words, ignore_case=True)
