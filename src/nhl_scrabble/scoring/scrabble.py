"""Scrabble scoring logic for player names."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, ClassVar

from nhl_scrabble.models.player import PlayerScore

logger = logging.getLogger(__name__)


class ScrabbleScorer:
    """Calculate Scrabble scores for player names using standard letter values.

    This class provides methods to calculate Scrabble scores based on the
    standard English Scrabble letter point values.

    Letter values:
        - 1 point: A, E, I, O, U, L, N, S, T, R
        - 2 points: D, G
        - 3 points: B, C, M, P
        - 4 points: F, H, V, W, Y
        - 5 points: K
        - 8 points: J, X
        - 10 points: Q, Z
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

    @staticmethod
    @lru_cache(maxsize=2048)
    def calculate_score(name: str) -> int:
        """Calculate the Scrabble score for a given name.

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
            22
        """
        return sum(ScrabbleScorer.LETTER_VALUES.get(char.upper(), 0) for char in name)

    def score_player(
        self, player_data: dict[str, Any], team: str, division: str, conference: str
    ) -> PlayerScore:
        """Score a player and return a PlayerScore object.

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
            32
        """
        first_name = player_data["firstName"]["default"]
        last_name = player_data["lastName"]["default"]
        full_name = f"{first_name} {last_name}"

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
        cache_info = ScrabbleScorer.calculate_score.cache_info()
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

            logger.info(
                "Scrabble scoring cache stats: "
                f"hits={stats['hits']}, "
                f"misses={stats['misses']}, "
                f"hit_rate={hit_rate:.1f}%, "
                f"size={stats['currsize']}/{stats['maxsize']} "
                f"({utilization:.1f}% full)"
            )
        else:
            logger.info("Scrabble scoring cache: No calls yet")

    @staticmethod
    def clear_cache() -> None:
        """Clear the score calculation cache.

        Useful for testing or when memory needs to be freed.
        """
        ScrabbleScorer.calculate_score.cache_clear()
        logger.debug("Scrabble scoring cache cleared")
