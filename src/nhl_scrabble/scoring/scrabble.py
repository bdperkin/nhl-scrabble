"""Scrabble scoring logic for player names."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, ClassVar

from nhl_scrabble.models.player import PlayerScore

logger = logging.getLogger(__name__)


class ScrabbleScorer:
    """Calculate Scrabble scores for player names using configurable letter values.

    This class provides methods to calculate scores based on letter point values.
    By default, uses standard English Scrabble values, but supports custom
    scoring systems via the letter_values parameter.

    Default letter values (standard Scrabble):
        - 1 point: A, E, I, O, U, L, N, S, T, R
        - 2 points: D, G
        - 3 points: B, C, M, P
        - 4 points: F, H, V, W, Y
        - 5 points: K
        - 8 points: J, X
        - 10 points: Q, Z

    Custom scoring systems can be provided via the letter_values parameter,
    enabling alternative scoring methods (e.g., Wordle scoring, uniform values).
    """

    LETTER_VALUES: ClassVar[dict[str, int]] = {
        "A": 1,
        "E": 1,
        "I": 1,
        "O": 1,
        "U": 1,
        "L": 1,
        "N": 1,
        "S": 1,
        "T": 1,
        "R": 1,
        "D": 2,
        "G": 2,
        "B": 3,
        "C": 3,
        "M": 3,
        "P": 3,
        "F": 4,
        "H": 4,
        "V": 4,
        "W": 4,
        "Y": 4,
        "K": 5,
        "J": 8,
        "X": 8,
        "Q": 10,
        "Z": 10,
    }

    def __init__(self, letter_values: dict[str, int] | None = None) -> None:
        """Initialize the scorer with custom or default letter values.

        Args:
            letter_values: Optional custom letter-to-points mapping.
                If None, uses standard Scrabble values.

        Examples:
            >>> # Standard Scrabble scoring
            >>> scorer = ScrabbleScorer()
            >>> scorer.calculate_score("ALEX")
            11

            >>> # Custom scoring (all letters worth 1 point)
            >>> uniform_values = {chr(i): 1 for i in range(65, 91)}
            >>> scorer = ScrabbleScorer(letter_values=uniform_values)
            >>> scorer.calculate_score_custom("ALEX")
            4
        """
        self._letter_values = letter_values if letter_values is not None else self.LETTER_VALUES
        logger.debug(f"ScrabbleScorer initialized with {len(self._letter_values)} letter values")

    @staticmethod
    @lru_cache(maxsize=2048)
    def _calculate_with_values(name: str, values_tuple: tuple[tuple[str, int], ...]) -> int:
        """Calculate score with provided letter values (cached).

        This static method enables LRU caching while supporting custom letter values.
        The letter values are passed as a hashable tuple for cache key uniqueness.

        Args:
            name: Name to score
            values_tuple: Letter values as tuple of (letter, value) pairs

        Returns:
            Total score for the name
        """
        values_dict = dict(values_tuple)
        return sum(values_dict.get(char.upper(), 0) for char in name)

    @staticmethod
    def calculate_score(name: str) -> int:
        """Calculate the Scrabble score for a given name using standard values.

        This static method provides convenient scoring with default Scrabble letter values.
        For custom scoring values, create a ScrabbleScorer instance and use
        the calculate_score_custom() method.

        This method uses LRU caching to avoid recomputing scores for duplicate
        names, which significantly improves performance when processing ~700 NHL
        players with many duplicate first/last names.

        Cache size: 2048 entries (sufficient for all unique name components)

        Args:
            name: The name to score (can include spaces and special characters)

        Returns:
            The total Scrabble score (non-letter characters are worth 0 points)

        Examples:
            >>> ScrabbleScorer.calculate_score("ALEX")
            11
            >>> ScrabbleScorer.calculate_score("Ovechkin")
            20
        """
        # Use default Scrabble values
        values_tuple = tuple(sorted(ScrabbleScorer.LETTER_VALUES.items()))
        return ScrabbleScorer._calculate_with_values(name, values_tuple)

    def calculate_score_custom(self, name: str) -> int:
        """Calculate score using custom letter values configured in this instance.

        Use this method when you've created a ScrabbleScorer with custom letter
        values. For default Scrabble scoring, use the static calculate_score() method.

        Args:
            name: The name to score (can include spaces and special characters)

        Returns:
            The total score using custom letter values

        Examples:
            >>> uniform_values = {chr(i): 1 for i in range(65, 91)}
            >>> scorer = ScrabbleScorer(letter_values=uniform_values)
            >>> scorer.calculate_score_custom("ALEX")
            4
        """
        # Convert dict to hashable tuple for caching
        values_tuple = tuple(sorted(self._letter_values.items()))
        return self._calculate_with_values(name, values_tuple)

    def score_player(
        self,
        player_data: dict[str, Any],
        team: str,
        division: str,
        conference: str,
    ) -> PlayerScore:
        """Score a player and return a PlayerScore object.

        Uses custom letter values if configured, otherwise uses default Scrabble values.

        Args:
            player_data: Dictionary with 'firstName' and 'lastName' keys containing 'default' values
            team: Team abbreviation
            division: Division name
            conference: Conference name

        Returns:
            PlayerScore object with all scoring information

        Examples:
            >>> scorer = ScrabbleScorer()
            >>> player = {"firstName": {"default": "Connor"}, "lastName": {"default": "McDavid"}}
            >>> result = scorer.score_player(player, "EDM", "Pacific", "Western")
            >>> result.full_score
            24
        """
        first_name = player_data["firstName"]["default"]
        last_name = player_data["lastName"]["default"]
        full_name = f"{first_name} {last_name}"

        # Use custom scoring if custom values are set
        if self._letter_values is not self.LETTER_VALUES:
            first_score = self.calculate_score_custom(first_name)
            last_score = self.calculate_score_custom(last_name)
        else:
            first_score = self.calculate_score(first_name)
            last_score = self.calculate_score(last_name)

        full_score = first_score + last_score

        return PlayerScore(
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            first_score=first_score,
            last_score=last_score,
            full_score=full_score,
            team=team,
            division=division,
            conference=conference,
        )

    @staticmethod
    def get_cache_info() -> dict[str, int]:
        """Get cache statistics for the score calculation cache.

        Returns:
            Dictionary with cache statistics:
                - hits: Number of cache hits
                - misses: Number of cache misses
                - maxsize: Maximum cache size
                - currsize: Current cache size

        Examples:
            >>> info = ScrabbleScorer.get_cache_info()
            >>> info['maxsize']
            2048
        """
        cache_info = ScrabbleScorer._calculate_with_values.cache_info()
        return {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "maxsize": cache_info.maxsize or 0,
            "currsize": cache_info.currsize,
        }

    @staticmethod
    def log_cache_stats() -> None:
        """Log cache statistics for monitoring and performance analysis.

        Logs hit rate, total calls, and cache utilization at INFO level.
        """
        stats = ScrabbleScorer.get_cache_info()
        total_calls = stats["hits"] + stats["misses"]

        if total_calls > 0:
            hit_rate = (stats["hits"] / total_calls) * 100
            utilization = (
                (stats["currsize"] / stats["maxsize"]) * 100 if stats["maxsize"] > 0 else 0
            )

            logger.debug(
                "Scrabble scoring cache stats: "
                f"hits={stats['hits']}, "
                f"misses={stats['misses']}, "
                f"hit_rate={hit_rate:.1f}%, "
                f"size={stats['currsize']}/{stats['maxsize']} "
                f"({utilization:.1f}% full)",
            )
        else:
            logger.debug("Scrabble scoring cache: No calls yet")

    @staticmethod
    def clear_cache() -> None:
        """Clear the score calculation cache.

        Useful for testing or when memory needs to be freed.
        """
        ScrabbleScorer._calculate_with_values.cache_clear()
        logger.debug("Scrabble scoring cache cleared")
