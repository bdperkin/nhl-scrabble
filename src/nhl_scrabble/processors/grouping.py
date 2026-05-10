"""Player grouping utilities for analysis and reporting.

This module provides functions to group players by various attributes such as nationality, country
code, team, division, and conference.
"""

from collections import defaultdict
from typing import Any

from nhl_scrabble.models.player import PlayerScore


def group_by_nationality(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by nationality (full country name).

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping nationality to list of players.
        Empty string key contains players with unknown nationality.

    Examples:
        >>> from nhl_scrabble.models.player import PlayerScore
        >>> players = [
        ...     PlayerScore(
        ...         first_name="Connor", last_name="McDavid",
        ...         full_name="Connor McDavid", first_score=20, last_score=15,
        ...         full_score=35, team="EDM", division="Pacific",
        ...         conference="Western", nationality="Canada"
        ...     ),
        ...     PlayerScore(
        ...         first_name="Auston", last_name="Matthews",
        ...         full_name="Auston Matthews", first_score=18, last_score=22,
        ...         full_score=40, team="TOR", division="Atlantic",
        ...         conference="Eastern", nationality="United States"
        ...     ),
        ... ]
        >>> grouped = group_by_nationality(players)
        >>> len(grouped["Canada"])
        1
        >>> grouped["Canada"][0].full_name
        'Connor McDavid'
    """
    grouped: dict[str, list[PlayerScore]] = defaultdict(list)
    for player in players:
        # Use empty string for unknown nationality
        key = player.nationality or "Unknown"
        grouped[key].append(player)
    return grouped.copy()


def group_by_birth_country(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by birth country code (ISO 3166-1 alpha-3).

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping country code to list of players.
        Empty string key contains players with unknown country.

    Examples:
        >>> from nhl_scrabble.models.player import PlayerScore
        >>> players = [
        ...     PlayerScore(
        ...         first_name="Connor", last_name="McDavid",
        ...         full_name="Connor McDavid", first_score=20, last_score=15,
        ...         full_score=35, team="EDM", division="Pacific",
        ...         conference="Western", birth_country="CAN", nationality="Canada"
        ...     ),
        ...     PlayerScore(
        ...         first_name="Leon", last_name="Draisaitl",
        ...         full_name="Leon Draisaitl", first_score=18, last_score=24,
        ...         full_score=42, team="EDM", division="Pacific",
        ...         conference="Western", birth_country="DEU", nationality="Germany"
        ...     ),
        ... ]
        >>> grouped = group_by_birth_country(players)
        >>> len(grouped["CAN"])
        1
        >>> len(grouped["DEU"])
        1
    """
    grouped: dict[str, list[PlayerScore]] = defaultdict(list)
    for player in players:
        # Use empty string for unknown country
        key = player.birth_country or "Unknown"
        grouped[key].append(player)
    return grouped.copy()


def group_by_team(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by team abbreviation.

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping team abbreviation to list of players

    Examples:
        >>> from nhl_scrabble.models.player import PlayerScore
        >>> players = [
        ...     PlayerScore(
        ...         first_name="Connor", last_name="McDavid",
        ...         full_name="Connor McDavid", first_score=20, last_score=15,
        ...         full_score=35, team="EDM", division="Pacific",
        ...         conference="Western"
        ...     ),
        ...     PlayerScore(
        ...         first_name="Auston", last_name="Matthews",
        ...         full_name="Auston Matthews", first_score=18, last_score=22,
        ...         full_score=40, team="TOR", division="Atlantic",
        ...         conference="Eastern"
        ...     ),
        ... ]
        >>> grouped = group_by_team(players)
        >>> len(grouped["EDM"])
        1
        >>> len(grouped["TOR"])
        1
    """
    grouped: dict[str, list[PlayerScore]] = defaultdict(list)
    for player in players:
        grouped[player.team].append(player)
    return grouped.copy()


def group_by_division(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by division.

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping division name to list of players

    Examples:
        >>> from nhl_scrabble.models.player import PlayerScore
        >>> players = [
        ...     PlayerScore(
        ...         first_name="Connor", last_name="McDavid",
        ...         full_name="Connor McDavid", first_score=20, last_score=15,
        ...         full_score=35, team="EDM", division="Pacific",
        ...         conference="Western"
        ...     ),
        ...     PlayerScore(
        ...         first_name="Auston", last_name="Matthews",
        ...         full_name="Auston Matthews", first_score=18, last_score=22,
        ...         full_score=40, team="TOR", division="Atlantic",
        ...         conference="Eastern"
        ...     ),
        ... ]
        >>> grouped = group_by_division(players)
        >>> len(grouped["Pacific"])
        1
        >>> len(grouped["Atlantic"])
        1
    """
    grouped: dict[str, list[PlayerScore]] = defaultdict(list)
    for player in players:
        grouped[player.division].append(player)
    return grouped.copy()


def group_by_conference(players: list[PlayerScore]) -> dict[str, list[PlayerScore]]:
    """Group players by conference.

    Args:
        players: List of player scores

    Returns:
        Dictionary mapping conference name to list of players

    Examples:
        >>> from nhl_scrabble.models.player import PlayerScore
        >>> players = [
        ...     PlayerScore(
        ...         first_name="Connor", last_name="McDavid",
        ...         full_name="Connor McDavid", first_score=20, last_score=15,
        ...         full_score=35, team="EDM", division="Pacific",
        ...         conference="Western"
        ...     ),
        ...     PlayerScore(
        ...         first_name="Auston", last_name="Matthews",
        ...         full_name="Auston Matthews", first_score=18, last_score=22,
        ...         full_score=40, team="TOR", division="Atlantic",
        ...         conference="Eastern"
        ...     ),
        ... ]
        >>> grouped = group_by_conference(players)
        >>> len(grouped["Western"])
        1
        >>> len(grouped["Eastern"])
        1
    """
    grouped: dict[str, list[PlayerScore]] = defaultdict(list)
    for player in players:
        grouped[player.conference].append(player)
    return grouped.copy()


def calculate_group_statistics(players: list[PlayerScore]) -> dict[str, Any]:
    """Calculate statistics for a group of players.

    Args:
        players: List of player scores in the group

    Returns:
        Dictionary with group statistics:
            - player_count: Number of players
            - total_score: Sum of all player scores
            - average_score: Mean score across all players
            - min_score: Lowest player score
            - max_score: Highest player score
            - top_player: Player with highest score

    Examples:
        >>> from nhl_scrabble.models.player import PlayerScore
        >>> players = [
        ...     PlayerScore(
        ...         first_name="Connor", last_name="McDavid",
        ...         full_name="Connor McDavid", first_score=20, last_score=15,
        ...         full_score=35, team="EDM", division="Pacific",
        ...         conference="Western"
        ...     ),
        ...     PlayerScore(
        ...         first_name="Leon", last_name="Draisaitl",
        ...         full_name="Leon Draisaitl", first_score=18, last_score=24,
        ...         full_score=42, team="EDM", division="Pacific",
        ...         conference="Western"
        ...     ),
        ... ]
        >>> stats = calculate_group_statistics(players)
        >>> stats["player_count"]
        2
        >>> stats["total_score"]
        77
        >>> stats["average_score"]
        38.5
        >>> stats["top_player"]["full_name"]
        'Leon Draisaitl'
    """
    if not players:
        return {
            "player_count": 0,
            "total_score": 0,
            "average_score": 0.0,
            "min_score": 0,
            "max_score": 0,
            "top_player": None,
        }

    scores = [p.full_score for p in players]
    total_score = sum(scores)
    top_player = max(players, key=lambda p: p.full_score)

    return {
        "player_count": len(players),
        "total_score": total_score,
        "average_score": total_score / len(players),
        "min_score": min(scores),
        "max_score": max(scores),
        "top_player": top_player.to_dict(),
    }
