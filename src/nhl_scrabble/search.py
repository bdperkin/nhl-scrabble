"""Player search functionality for NHL Scrabble."""

from __future__ import annotations

import fnmatch
import logging
from difflib import get_close_matches
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nhl_scrabble.models.player import PlayerScore

logger = logging.getLogger(__name__)


class PlayerSearch:
    """Search functionality for finding players by name and score.

    Provides exact, fuzzy, and wildcard search capabilities, as well as
    filtering by Scrabble score thresholds.

    Attributes:
        players: List of PlayerScore objects to search through
    """

    def __init__(self, players: list[PlayerScore]) -> None:
        """Initialize search with player list.

        Args:
            players: List of PlayerScore objects to search

        Examples:
            Initialize with player list:

            >>> from nhl_scrabble.models.player import PlayerScore
            >>> players = [
            ...     PlayerScore(
            ...         first_name="Connor",
            ...         last_name="McDavid",
            ...         full_name="Connor McDavid",
            ...         team="EDM",
            ...         division="Pacific",
            ...         conference="Western",
            ...         first_score=20,
            ...         last_score=15,
            ...         full_score=35
            ...     )
            ... ]
            >>> searcher = PlayerSearch(players)
            >>> len(searcher.players)
            1
        """
        self.players = players

    def _exact_search(self, query: str, players: list[PlayerScore]) -> list[PlayerScore]:
        """Perform exact substring search (case-insensitive).

        Args:
            query: Search query
            players: List of players to search

        Returns:
            List of matching players
        """
        query_lower = query.lower()
        return [p for p in players if query_lower in p.full_name.lower()]

    def _fuzzy_search(
        self,
        query: str,
        players: list[PlayerScore],
        cutoff: float = 0.6,
    ) -> list[PlayerScore]:
        """Perform fuzzy search using difflib.

        Args:
            query: Search query
            players: List of players to search
            cutoff: Similarity threshold (0.0-1.0, default: 0.6)

        Returns:
            List of matching players
        """
        names = [p.full_name for p in players]
        matches = get_close_matches(query, names, n=len(names), cutoff=cutoff)
        return [p for p in players if p.full_name in matches]

    def _wildcard_search(self, pattern: str, players: list[PlayerScore]) -> list[PlayerScore]:
        """Perform wildcard search using fnmatch.

        Supports * (any characters) and ? (single character) wildcards.

        Args:
            pattern: Search pattern with wildcards
            players: List of players to search

        Returns:
            List of matching players
        """
        pattern_lower = pattern.lower()
        return [p for p in players if fnmatch.fnmatch(p.full_name.lower(), pattern_lower)]

    def search(
        self,
        query: str,
        *,
        fuzzy: bool = False,
        min_score: int | None = None,
        max_score: int | None = None,
        team: str | None = None,
        division: str | None = None,
        conference: str | None = None,
    ) -> list[PlayerScore]:
        """Search for players by name with optional filters.

        Args:
            query: Search query (supports wildcards like 'Connor*')
            fuzzy: Enable fuzzy matching using difflib (default: False)
            min_score: Minimum Scrabble score filter
            max_score: Maximum Scrabble score filter
            team: Filter by team abbreviation (e.g., 'TOR')
            division: Filter by division name
            conference: Filter by conference name

        Returns:
            List of matching PlayerScore objects sorted by score (descending)

        Examples:
            >>> searcher = PlayerSearch(players)
            >>> # Exact search
            >>> results = searcher.search("Connor McDavid")
            >>> # Fuzzy search
            >>> results = searcher.search("McDavid", fuzzy=True)
            >>> # Wildcard search
            >>> results = searcher.search("Connor*")
            >>> # Score filtering
            >>> results = searcher.search("", min_score=50)
        """
        # Start with all players
        results = self.players

        # Apply team filter first
        if team:
            results = [p for p in results if p.team.upper() == team.upper()]

        # Apply division filter
        if division:
            results = [p for p in results if p.division.lower() == division.lower()]

        # Apply conference filter
        if conference:
            results = [p for p in results if p.conference.lower() == conference.lower()]

        # Apply score filters
        if min_score is not None:
            results = [p for p in results if p.full_score >= min_score]
        if max_score is not None:
            results = [p for p in results if p.full_score <= max_score]

        # Apply name search if query provided
        if query:
            if fuzzy:
                results = self._fuzzy_search(query, results)
            elif "*" in query or "?" in query:
                results = self._wildcard_search(query, results)
            else:
                results = self._exact_search(query, results)

        # Sort by score (descending), then by name
        results.sort(key=lambda p: (-p.full_score, p.full_name))

        logger.debug(f"Search query='{query}' fuzzy={fuzzy} returned {len(results)} results")

        return results

    def get_top_players(self, n: int = 20) -> list[PlayerScore]:
        """Get top N players by Scrabble score.

        Args:
            n: Number of players to return (default: 20)

        Returns:
            List of top N players sorted by score (descending)

        Examples:
            Get top 3 players:

            >>> from nhl_scrabble.models.player import PlayerScore
            >>> players = [
            ...     PlayerScore(
            ...         first_name="Connor",
            ...         last_name="McDavid",
            ...         full_name="Connor McDavid",
            ...         team="EDM",
            ...         division="Pacific",
            ...         conference="Western",
            ...         first_score=20,
            ...         last_score=15,
            ...         full_score=35
            ...     ),
            ...     PlayerScore(
            ...         first_name="Auston",
            ...         last_name="Matthews",
            ...         full_name="Auston Matthews",
            ...         team="TOR",
            ...         division="Atlantic",
            ...         conference="Eastern",
            ...         first_score=18,
            ...         last_score=20,
            ...         full_score=38
            ...     )
            ... ]
            >>> searcher = PlayerSearch(players)
            >>> top = searcher.get_top_players(n=1)
            >>> len(top)
            1
            >>> top[0].last_name
            'Matthews'
        """
        return sorted(self.players, key=lambda p: p.full_score, reverse=True)[:n]

    def get_stats(self) -> dict[str, int | float]:
        """Get statistics about the player database.

        Returns:
            Dictionary with statistics:
                - total_players: Total number of players
                - avg_score: Average Scrabble score
                - min_score: Minimum Scrabble score
                - max_score: Maximum Scrabble score
                - total_teams: Number of unique teams

        Examples:
            Get player statistics:

            >>> from nhl_scrabble.models.player import PlayerScore
            >>> players = [
            ...     PlayerScore(
            ...         first_name="Connor",
            ...         last_name="McDavid",
            ...         full_name="Connor McDavid",
            ...         team="EDM",
            ...         division="Pacific",
            ...         conference="Western",
            ...         first_score=20,
            ...         last_score=15,
            ...         full_score=35
            ...     ),
            ...     PlayerScore(
            ...         first_name="Auston",
            ...         last_name="Matthews",
            ...         full_name="Auston Matthews",
            ...         team="TOR",
            ...         division="Atlantic",
            ...         conference="Eastern",
            ...         first_score=18,
            ...         last_score=20,
            ...         full_score=38
            ...     )
            ... ]
            >>> searcher = PlayerSearch(players)
            >>> stats = searcher.get_stats()
            >>> stats['total_players']
            2
            >>> stats['total_teams']
            2
            >>> stats['min_score']
            35
            >>> stats['max_score']
            38
        """
        if not self.players:
            return {
                "total_players": 0,
                "avg_score": 0.0,
                "min_score": 0,
                "max_score": 0,
                "total_teams": 0,
            }

        scores = [p.full_score for p in self.players]
        teams = {p.team for p in self.players}

        return {
            "total_players": len(self.players),
            "avg_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "total_teams": len(teams),
        }
