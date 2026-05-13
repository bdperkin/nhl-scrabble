"""Data conversion utilities for web responses.

This module provides functions to convert internal data models to dictionaries suitable for
JSON/HTML responses.
"""

from __future__ import annotations

import operator
from typing import Any

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore


def _convert_players_to_dict(
    players: list[PlayerScore],
) -> list[dict[str, str | int | float]]:
    """Convert PlayerScore objects to dict format for response.

    Args:
        players: List of PlayerScore objects

    Returns:
        List of player dictionaries
    """
    return [
        {
            "first_name": player.first_name,
            "last_name": player.last_name,
            "full_name": player.full_name,
            "team": player.team,
            "division": player.division,
            "conference": player.conference,
            "score": player.full_score,
            "first_score": player.first_score,
            "last_score": player.last_score,
            "player_id": player.player_id,
            "birthplace": player.birthplace,
            "birth_country": player.birth_country,
            "nationality": player.nationality,
            "position_code": player.position_code,
            "position": player.position,
            "position_type": player.position_type,
        }
        for player in players
    ]


def _convert_teams_to_dict(
    team_scores_dict: dict[str, TeamScore],
    top_team_players: int,
) -> list[dict[str, Any]]:
    """Convert TeamScore objects to dict format for response.

    Args:
        team_scores_dict: Dictionary of TeamScore objects
        top_team_players: Number of top players to include per team

    Returns:
        List of team dictionaries
    """
    teams_data = [
        {
            "abbrev": team_score.abbrev,
            "name": team_score.name,
            "total_score": team_score.total,
            "avg_score": team_score.avg_per_player,
            "player_count": team_score.player_count,
            "division": team_score.division,
            "conference": team_score.conference,
            "top_players": [
                {
                    "first_name": player.first_name,
                    "last_name": player.last_name,
                    "full_name": player.full_name,
                    "score": player.full_score,
                }
                for player in sorted(
                    team_score.players,
                    key=lambda x: x.full_score,
                    reverse=True,
                )[:top_team_players]
            ],
        }
        for team_score in team_scores_dict.values()
    ]
    teams_data.sort(key=operator.itemgetter("total_score"), reverse=True)
    return teams_data


def _group_teams_by_grouping(
    teams_data: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Group teams by division and conference.

    Args:
        teams_data: List of team dictionaries

    Returns:
        Tuple of (divisions dict, conferences dict)
    """
    divisions: dict[str, list[dict[str, Any]]] = {}
    conferences: dict[str, list[dict[str, Any]]] = {}

    for team in teams_data:
        div = team["division"]
        conf = team["conference"]

        if div not in divisions:
            divisions[div] = []
        divisions[div].append(team)

        if conf not in conferences:
            conferences[conf] = []
        conferences[conf].append(team)

    return divisions, conferences


def _build_entity_data(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Build entity data for auto-linking from analysis results.

    Args:
        data: Analysis results dictionary containing team_standings and top_players

    Returns:
        Dictionary with entity lists for auto-linking:
        {
            'teams': [{'name': str, 'abbrev': str}, ...],
            'divisions': [{'name': str}, ...],
            'conferences': [{'name': str}, ...],
            'players': [{'name': str, 'id': int}, ...]
        }
    """
    # Extract unique teams
    teams = [
        {"name": team["name"], "abbrev": team["abbrev"]} for team in data.get("team_standings", [])
    ]

    # Extract unique divisions from teams
    divisions_set = {team["division"] for team in data.get("team_standings", [])}
    divisions = [{"name": div} for div in sorted(divisions_set)]

    # Extract unique conferences from teams
    conferences_set = {team["conference"] for team in data.get("team_standings", [])}
    conferences = [{"name": conf} for conf in sorted(conferences_set)]

    # Extract players with IDs (for player detail pages)
    # Note: Player IDs come from the NHL API and are used for linking
    players = [
        {
            "name": f"{player['first_name']} {player['last_name']}",
            "id": player.get("player_id"),
        }
        for player in data.get("top_players", [])
        if player.get("player_id") and player.get("player_id") > 0
    ]

    # Ensure highest and lowest players are in entity data for stat card linking
    stats = data.get("stats", {})
    if stats:
        # Add highest player if not already in list
        if stats.get("highest_player_id") and stats.get("highest_player_name"):
            highest_exists = any(
                p["id"] == stats["highest_player_id"] for p in players if p.get("id")
            )
            if not highest_exists:
                players.append(
                    {"name": stats["highest_player_name"], "id": stats["highest_player_id"]},
                )

        # Add lowest player if not already in list
        if stats.get("lowest_player_id") and stats.get("lowest_player_name"):
            lowest_exists = any(
                p["id"] == stats["lowest_player_id"] for p in players if p.get("id")
            )
            if not lowest_exists:
                players.append(
                    {"name": stats["lowest_player_name"], "id": stats["lowest_player_id"]},
                )

    return {
        "teams": teams,
        "divisions": divisions,
        "conferences": conferences,
        "players": players,
    }
