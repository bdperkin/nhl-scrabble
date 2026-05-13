"""Formatting utilities for interactive shell output."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

from nhl_scrabble.i18n import get_translator

if TYPE_CHECKING:
    from rich.console import Console

    from nhl_scrabble.models.player import PlayerScore
    from nhl_scrabble.models.team import TeamScore

# Get translator for interactive shell
_ = get_translator()


def display_team(team: TeamScore, console: Console) -> None:
    """Display team details.

    Args:
        team: Team score to display
        console: Rich console for output
    """
    table = Table(title=f"{team.abbrev} ({team.abbrev})")
    table.add_column(_("Attribute"), style="cyan")
    table.add_column(_("Value"), style="green")

    table.add_row(_("Conference"), team.conference)
    table.add_row(_("Division"), team.division)
    table.add_row(_("Total Score"), str(team.total))
    table.add_row(_("Players"), str(len(team.players)))
    table.add_row(_("Average Score"), f"{team.avg_per_player:.2f}")

    console.print(table)
    console.print()

    # Show top players
    top_players = sorted(team.players, key=lambda p: p.full_score, reverse=True)[:10]

    player_table = Table(title=_("Top 10 Players"))
    player_table.add_column(_("Rank"), style="cyan", width=6)
    player_table.add_column(_("Player"), style="green", width=25)
    player_table.add_column(_("Score"), style="magenta", width=8)

    for i, player in enumerate(top_players, 1):
        player_table.add_row(str(i), player.full_name, str(player.full_score))

    console.print(player_table)


def display_player(player: PlayerScore, console: Console) -> None:
    """Display player details.

    Args:
        player: Player score to display
        console: Rich console for output
    """
    table = Table(title=player.full_name)
    table.add_column(_("Attribute"), style="cyan")
    table.add_column(_("Value"), style="green")

    table.add_row(_("Team"), player.team)
    table.add_row(_("First Name"), player.first_name)
    table.add_row(_("Last Name"), player.last_name)
    table.add_row(_("Scrabble Score"), str(player.full_score))

    console.print(table)


def display_team_list(teams: list[TeamScore], title: str, console: Console) -> None:
    """Display list of teams.

    Args:
        teams: List of team scores to display
        title: Table title
        console: Rich console for output
    """
    table = Table(title=title)
    table.add_column(_("Rank"), style="cyan", width=6)
    table.add_column(_("Team"), style="green", width=25)
    table.add_column(_("Score"), style="magenta", width=8)

    for i, team in enumerate(teams, 1):
        table.add_row(str(i), team.abbrev, str(team.total))

    console.print(table)
