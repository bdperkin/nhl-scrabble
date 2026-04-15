"""Team data processing module."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from nhl_scrabble.api.nhl_client import NHLApiClient
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

logger = logging.getLogger(__name__)


class TeamProcessor:
    """Process team roster data and calculate aggregate scores.

    This class orchestrates fetching roster data for all NHL teams, calculating Scrabble scores for
    all players, and aggregating statistics at team, division, and conference levels.
    """

    def __init__(self, api_client: NHLApiClient, scorer: ScrabbleScorer) -> None:
        """Initialize the team processor.

        Args:
            api_client: NHL API client for fetching data
            scorer: Scrabble scorer for calculating player scores
        """
        self.api_client = api_client
        self.scorer = scorer

    def process_all_teams(
        self,
    ) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
        """Process all NHL teams and calculate scores.

        Returns:
            Tuple containing:
                - Dictionary mapping team abbreviations to TeamScore objects
                - List of all PlayerScore objects across all teams
                - List of team abbreviations that failed to fetch

        Examples:
            >>> client = NHLApiClient()
            >>> scorer = ScrabbleScorer()
            >>> processor = TeamProcessor(client, scorer)
            >>> teams, players, failed = processor.process_all_teams()
            >>> len(teams) > 0
            True
        """
        logger.info("Starting team processing")

        # Fetch all teams
        teams_info = self.api_client.get_teams()
        total_teams = len(teams_info)
        logger.info(f"Fetched {total_teams} teams from NHL API")

        team_scores: dict[str, TeamScore] = {}
        all_players: list[PlayerScore] = []
        failed_teams: list[str] = []

        # Process each team
        for i, (team_abbrev, team_meta) in enumerate(teams_info.items(), 1):
            logger.info(f"Processing {team_abbrev} ({i}/{total_teams})")

            roster = self.api_client.get_team_roster(team_abbrev)

            if not roster:
                logger.warning(f"No roster data for {team_abbrev}")
                failed_teams.append(team_abbrev)
                continue

            team_players = self._process_team_roster(
                roster, team_abbrev, team_meta["division"], team_meta["conference"]
            )

            team_total = sum(player.full_score for player in team_players)

            team_scores[team_abbrev] = TeamScore(
                abbrev=team_abbrev,
                total=team_total,
                players=team_players,
                division=team_meta["division"],
                conference=team_meta["conference"],
            )

            all_players.extend(team_players)

        logger.info(
            f"Processing complete: {len(team_scores)} teams processed, {len(failed_teams)} failed"
        )
        return team_scores, all_players, failed_teams

    def _process_team_roster(
        self, roster: dict[str, Any], team_abbrev: str, division: str, conference: str
    ) -> list[PlayerScore]:
        """Process a single team's roster and score all players.

        Args:
            roster: Roster data from NHL API
            team_abbrev: Team abbreviation
            division: Division name
            conference: Conference name

        Returns:
            List of PlayerScore objects for all players on the team
        """
        team_players: list[PlayerScore] = []

        # Process all position groups
        for position in ["forwards", "defensemen", "goalies"]:
            if position not in roster:
                continue

            for player_data in roster[position]:
                player_score = self.scorer.score_player(
                    player_data, team_abbrev, division, conference
                )
                team_players.append(player_score)

        logger.debug(
            f"Scored {len(team_players)} players for {team_abbrev} "
            f"(total: {sum(p.full_score for p in team_players)})"
        )

        return team_players

    def calculate_division_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, DivisionStandings]:
        """Calculate division-level standings from team scores.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary mapping division names to DivisionStandings objects

        Examples:
            >>> standings = processor.calculate_division_standings(teams)
            >>> "Atlantic" in standings
            True
        """
        division_data: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"total": 0, "teams": [], "player_count": 0}
        )

        for team_abbrev, team_score in team_scores.items():
            division = team_score.division
            division_data[division]["total"] += team_score.total
            division_data[division]["teams"].append(team_abbrev)
            division_data[division]["player_count"] += team_score.player_count

        # Convert to DivisionStandings objects
        standings: dict[str, DivisionStandings] = {}
        for division, data in division_data.items():
            avg_per_team = data["total"] / len(data["teams"]) if data["teams"] else 0.0
            standings[division] = DivisionStandings(
                name=division,
                total=data["total"],
                teams=sorted(data["teams"]),
                player_count=data["player_count"],
                avg_per_team=avg_per_team,
            )

        logger.debug(f"Calculated standings for {len(standings)} divisions")
        return standings

    def calculate_conference_standings(
        self, team_scores: dict[str, TeamScore]
    ) -> dict[str, ConferenceStandings]:
        """Calculate conference-level standings from team scores.

        Args:
            team_scores: Dictionary of TeamScore objects by team abbreviation

        Returns:
            Dictionary mapping conference names to ConferenceStandings objects

        Examples:
            >>> standings = processor.calculate_conference_standings(teams)
            >>> "Eastern" in standings
            True
        """
        conference_data: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"total": 0, "teams": [], "player_count": 0}
        )

        for team_abbrev, team_score in team_scores.items():
            conference = team_score.conference
            conference_data[conference]["total"] += team_score.total
            conference_data[conference]["teams"].append(team_abbrev)
            conference_data[conference]["player_count"] += team_score.player_count

        # Convert to ConferenceStandings objects
        standings: dict[str, ConferenceStandings] = {}
        for conference, data in conference_data.items():
            avg_per_team = data["total"] / len(data["teams"]) if data["teams"] else 0.0
            standings[conference] = ConferenceStandings(
                name=conference,
                total=data["total"],
                teams=sorted(data["teams"]),
                player_count=data["player_count"],
                avg_per_team=avg_per_team,
            )

        logger.debug(f"Calculated standings for {len(standings)} conferences")
        return standings
