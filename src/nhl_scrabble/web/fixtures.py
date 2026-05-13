"""Fixture data loading for test mode.

This module provides utilities to load and process NHL API fixture data from JSON files
when the application is running in TEST_MODE.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.scoring import ScrabbleScorer

logger = logging.getLogger(__name__)


def _load_fixture_data() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load NHL API fixture data from JSON files for test mode.

    Returns:
        Tuple of (standings_data, rosters_data)

    Raises:
        FileNotFoundError: If fixture files not found
        json.JSONDecodeError: If fixture files are invalid JSON
    """
    # Get current working directory for debugging
    cwd = Path.cwd()
    logger.info("Current working directory: %s", cwd)

    # Look for fixtures in common locations
    fixture_paths = [
        Path("qa/web/tests/visual/fixtures"),  # CI and local (from project root)
        Path(__file__).parent.parent.parent.parent
        / "qa/web/tests/visual/fixtures",  # Relative to this file
        cwd / "qa/web/tests/visual/fixtures",  # Explicit from CWD
    ]

    logger.info("Searching for fixture directory in %d locations:", len(fixture_paths))
    for i, path in enumerate(fixture_paths, 1):
        resolved = path.resolve()
        exists = path.exists()
        logger.info("  %d. %s (resolved: %s, exists: %s)", i, path, resolved, exists)

    fixture_dir = None
    for path in fixture_paths:
        if path.exists():
            fixture_dir = path
            logger.info("✅ Found fixture directory: %s", fixture_dir.resolve())
            break

    if fixture_dir is None:
        error_msg = (
            f"Fixture directory not found. CWD: {cwd}. "
            f"Tried: {[str(p.resolve()) for p in fixture_paths]}"
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    standings_file = fixture_dir / "nhl_standings.json"
    rosters_file = fixture_dir / "nhl_rosters.json"

    logger.info("Looking for fixture files:")
    logger.info("  - Standings: %s (exists: %s)", standings_file, standings_file.exists())
    logger.info("  - Rosters: %s (exists: %s)", rosters_file, rosters_file.exists())

    if not standings_file.exists():
        error_msg = f"Standings fixture not found: {standings_file.resolve()}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    if not rosters_file.exists():
        error_msg = f"Rosters fixture not found: {rosters_file.resolve()}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with standings_file.open() as f:
            standings_data = json.load(f)
        logger.info("✅ Loaded standings fixture: %d bytes", standings_file.stat().st_size)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in standings fixture {standings_file}: {e}"
        logger.error(error_msg)
        raise

    try:
        with rosters_file.open() as f:
            rosters_data = json.load(f)
        logger.info("✅ Loaded rosters fixture: %d bytes", rosters_file.stat().st_size)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in rosters fixture {rosters_file}: {e}"
        logger.error(error_msg)
        raise

    num_standings = len(standings_data.get("standings", []))
    num_rosters = len(rosters_data)
    logger.info(
        "✅ Fixture data loaded successfully: %d teams in standings, %d team rosters",
        num_standings,
        num_rosters,
    )

    return standings_data, rosters_data


def _process_fixture_data(
    scorer: ScrabbleScorer,
) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
    """Process fixture data the same way as TeamProcessor would process live API data.

    Args:
        scorer: ScrabbleScorer instance

    Returns:
        Tuple of (team_scores_dict, all_players, failed_teams)
    """
    standings_data, rosters_data = _load_fixture_data()

    team_scores: dict[str, TeamScore] = {}
    all_players: list[PlayerScore] = []
    failed_teams: list[str] = []

    # Extract team metadata from standings
    teams_info: dict[str, dict[str, str]] = {}
    for team in standings_data.get("standings", []):
        team_abbrev = team["teamAbbrev"]["default"]
        teams_info[team_abbrev] = {
            "name": team.get("teamName", {}).get("default", team_abbrev),
            "division": team.get("divisionName", "Unknown"),
            "conference": team.get("conferenceName", "Unknown"),
        }

    # Process each team's roster
    for team_abbrev, team_info in teams_info.items():
        if team_abbrev not in rosters_data:
            logger.warning("No roster data for team: %s", team_abbrev)
            failed_teams.append(team_abbrev)
            continue

        roster = rosters_data[team_abbrev]
        team_players: list[PlayerScore] = []

        # Process all positions
        for position_group in ("forwards", "defensemen", "goalies"):
            for player_data in roster.get(position_group, []):
                first_name = player_data.get("firstName", {}).get("default", "")
                last_name = player_data.get("lastName", {}).get("default", "")

                if not first_name or not last_name:
                    continue

                # Calculate scores
                first_score = scorer.calculate_score(first_name)
                last_score = scorer.calculate_score(last_name)
                full_name = f"{first_name} {last_name}"
                full_score = first_score + last_score

                player = PlayerScore(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    first_score=first_score,
                    last_score=last_score,
                    full_score=full_score,
                    team=team_abbrev,
                    division=team_info["division"],
                    conference=team_info["conference"],
                )
                team_players.append(player)
                all_players.append(player)

        # Create TeamScore
        if team_players:
            total_score = sum(p.full_score for p in team_players)
            team_score = TeamScore(
                abbrev=team_abbrev,
                name=team_info["name"],
                total=total_score,
                players=team_players,
                division=team_info["division"],
                conference=team_info["conference"],
            )
            team_scores[team_abbrev] = team_score

    logger.info("Processed %d teams with %d total players", len(team_scores), len(all_players))

    return team_scores, all_players, failed_teams
