"""Team data processing module."""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from nhl_scrabble.api.nhl_client import NHLApiClient, NHLApiNotFoundError
from nhl_scrabble.models.player import PlayerScore
from nhl_scrabble.models.standings import ConferenceStandings, DivisionStandings
from nhl_scrabble.models.team import TeamScore
from nhl_scrabble.scoring.scrabble import ScrabbleScorer

logger = logging.getLogger(__name__)


class TeamProcessor:
    """Process team roster data and calculate aggregate scores.

    This class orchestrates fetching roster data for all NHL teams, calculating Scrabble scores for
    all players, and aggregating statistics at team, division, and conference levels.

    Supports concurrent fetching of team rosters to improve performance for I/O-bound operations.
    """

    def __init__(
        self, api_client: NHLApiClient, scorer: ScrabbleScorer, max_workers: int = 5
    ) -> None:
        """Initialize the team processor.

        Args:
            api_client: NHL API client for fetching data
            scorer: Scrabble scorer for calculating player scores
            max_workers: Maximum number of concurrent API requests (default: 5)
        """
        self.api_client = api_client
        self.scorer = scorer
        self.max_workers = max_workers

    def process_all_teams(
        self,
        progress_callback: Callable[[str], None] | None = None,
        season: str | None = None,
    ) -> tuple[dict[str, TeamScore], list[PlayerScore], list[str]]:
        """Process all NHL teams and calculate scores with concurrent fetching.

        Uses ThreadPoolExecutor to fetch team rosters concurrently, improving performance
        for I/O-bound operations. The number of concurrent workers is controlled by max_workers.

        Args:
            progress_callback: Optional callback to report progress after each team.
                Called with team abbreviation after successfully processing each team.
            season: Optional season to analyze (format: YYYYYYYY, e.g., 20222023).
                If None, fetches current season data.

        Returns:
            Tuple containing:
                - Dictionary mapping team abbreviations to TeamScore objects
                - List of all PlayerScore objects across all teams
                - List of team abbreviations that failed to fetch

        Examples:
            >>> client = NHLApiClient()
            >>> scorer = ScrabbleScorer()
            >>> processor = TeamProcessor(client, scorer, max_workers=5)
            >>> teams, players, failed = processor.process_all_teams()
            >>> len(teams) > 0
            True
            >>> teams_2022, players_2022, failed = processor.process_all_teams(season="20222023")
            >>> len(teams_2022) > 0
            True
        """
        season_desc = f"for season {season}" if season else "for current season"
        logger.info(
            f"Starting team processing {season_desc} "
            f"(concurrent mode, max_workers={self.max_workers})"
        )

        # Fetch all teams metadata
        teams_info = self.api_client.get_teams(season=season)
        total_teams = len(teams_info)
        logger.info(f"Fetched {total_teams} teams from NHL API")

        team_scores: dict[str, TeamScore] = {}
        all_players: list[PlayerScore] = []
        failed_teams: list[str] = []

        # Concurrent fetching with controlled parallelism
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all roster fetch jobs
            future_to_team = {
                executor.submit(
                    self._fetch_and_process_team, team_abbrev, team_meta, season
                ): team_abbrev
                for team_abbrev, team_meta in teams_info.items()
            }

            # Process results as they complete
            for completed, future in enumerate(as_completed(future_to_team), start=1):
                team_abbrev = future_to_team[future]

                try:
                    result = future.result()

                    if result is None:
                        # Team failed to fetch
                        failed_teams.append(team_abbrev)
                        logger.warning(
                            f"No roster data for {team_abbrev} ({completed}/{total_teams})"
                        )
                    else:
                        # Success
                        team_score, team_players = result
                        team_scores[team_abbrev] = team_score
                        all_players.extend(team_players)
                        logger.info(f"Processed {team_abbrev} ({completed}/{total_teams})")

                        # Call progress callback if provided
                        if progress_callback:
                            progress_callback(team_abbrev)

                except (OSError, ValueError) as e:
                    # OSError covers network/connection errors, ValueError for data parsing
                    logger.error(f"Error processing {team_abbrev}: {e}")
                    failed_teams.append(team_abbrev)

        logger.info(
            f"Processing complete: {len(team_scores)} teams processed, "
            f"{len(failed_teams)} failed (concurrent mode)"
        )
        return team_scores, all_players, failed_teams

    def _fetch_and_process_team(
        self, team_abbrev: str, team_meta: dict[str, str], season: str | None = None
    ) -> tuple[TeamScore, list[PlayerScore]] | None:
        """Fetch and process a single team (thread-safe).

        This method is called concurrently from multiple threads. It fetches the roster
        for a single team, calculates scores for all players, and aggregates team statistics.

        Args:
            team_abbrev: Team abbreviation (e.g., "TOR", "BOS")
            team_meta: Team metadata containing division and conference
            season: Optional season to analyze (format: YYYYYYYY, e.g., 20222023)

        Returns:
            Tuple of (TeamScore, player list) if successful, None if team fetch failed

        Note:
            This method is thread-safe as it operates only on local variables and
            thread-safe API client methods. No shared mutable state is accessed.
        """
        try:
            # Fetch roster (with built-in retry and rate limiting)
            roster = self.api_client.get_team_roster(team_abbrev, season=season)

            # Process roster
            team_players = self._process_team_roster(
                roster, team_abbrev, team_meta["division"], team_meta["conference"]
            )

            # Calculate team score
            team_total = sum(player.full_score for player in team_players)

            team_score = TeamScore(
                abbrev=team_abbrev,
                total=team_total,
                players=team_players,
                division=team_meta["division"],
                conference=team_meta["conference"],
            )

            return (team_score, team_players)

        except NHLApiNotFoundError:
            # Team has no roster data
            return None

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

        # Use level guard to avoid expensive sum() call when DEBUG disabled
        if logger.isEnabledFor(logging.DEBUG):
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

        if logger.isEnabledFor(logging.DEBUG):
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

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calculated standings for {len(standings)} conferences")
        return standings
