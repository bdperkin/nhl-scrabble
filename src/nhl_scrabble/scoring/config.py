"""Scoring configuration management for custom letter values."""

from __future__ import annotations

import json
import logging
import string
from pathlib import Path
from typing import ClassVar

logger = logging.getLogger(__name__)


class ScoringConfig:
    """Manages scoring configurations for different letter value systems.

    Provides built-in scoring systems and supports loading custom letter values
    from JSON configuration files.

    Built-in scoring systems:
        - scrabble: Standard Scrabble letter values (default)
        - wordle: Wordle-inspired uniform scoring (common=1, uncommon=2, rare=3)
        - uniform: All letters worth 1 point

    Custom configs:
        Load from JSON file with letter-to-point mappings:
        {"A": 5, "B": 2, "C": 2, ...}
    """

    # Standard Scrabble letter values (default)
    SCRABBLE_VALUES: ClassVar[dict[str, int]] = {
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

    # Wordle-inspired scoring (common letters = 1, uncommon = 2, rare = 3)
    WORDLE_VALUES: ClassVar[dict[str, int]] = {
        # Very common (1 point)
        "E": 1,
        "A": 1,
        "R": 1,
        "I": 1,
        "O": 1,
        "T": 1,
        "N": 1,
        "S": 1,
        "L": 1,
        # Common (2 points)
        "C": 2,
        "U": 2,
        "D": 2,
        "P": 2,
        "M": 2,
        "H": 2,
        "G": 2,
        "B": 2,
        "F": 2,
        "Y": 2,
        "W": 2,
        "K": 2,
        "V": 2,
        # Rare (3 points)
        "X": 3,
        "Z": 3,
        "J": 3,
        "Q": 3,
    }

    # Uniform scoring (all letters worth 1 point)
    UNIFORM_VALUES: ClassVar[dict[str, int]] = dict.fromkeys(string.ascii_uppercase, 1)

    # Mapping of system names to value dictionaries
    BUILT_IN_SYSTEMS: ClassVar[dict[str, dict[str, int]]] = {
        "scrabble": SCRABBLE_VALUES,
        "wordle": WORDLE_VALUES,
        "uniform": UNIFORM_VALUES,
    }

    @classmethod
    def get_scoring_system(cls, system: str) -> dict[str, int]:
        """Get letter values for a built-in scoring system.

        Args:
            system: Name of the scoring system (scrabble, wordle, uniform)

        Returns:
            Dictionary mapping uppercase letters to point values

        Raises:
            ValueError: If the scoring system is not recognized

        Examples:
            >>> values = ScoringConfig.get_scoring_system("scrabble")
            >>> values["Q"]
            10
            >>> values = ScoringConfig.get_scoring_system("uniform")
            >>> values["Q"]
            1
        """
        system_lower = system.lower()
        if system_lower not in cls.BUILT_IN_SYSTEMS:
            available = ", ".join(cls.BUILT_IN_SYSTEMS.keys())
            raise ValueError(f"Unknown scoring system: {system}. Available systems: {available}")

        logger.debug(f"Using built-in scoring system: {system_lower}")
        return cls.BUILT_IN_SYSTEMS[system_lower].copy()

    @classmethod
    def _validate_config(cls, config_data: dict[str, int], source: Path | str) -> dict[str, int]:
        """Validate and normalize a scoring configuration.

        Args:
            config_data: Dictionary from JSON file
            source: Source file path (for error messages)

        Returns:
            Normalized dictionary with uppercase letters and validated values

        Raises:
            ValueError: If the config is invalid
        """
        if not isinstance(config_data, dict):
            raise TypeError(
                f"Scoring config must be a dictionary, got {type(config_data).__name__}",
            )

        # Normalize to uppercase and validate
        normalized: dict[str, int] = {}
        expected_letters = set(string.ascii_uppercase)
        provided_letters = set()

        for letter, value in config_data.items():
            if not isinstance(letter, str) or len(letter) != 1:
                raise ValueError(f"Invalid letter in scoring config: {letter!r}")

            letter_upper = letter.upper()
            if not letter_upper.isalpha():
                raise ValueError(f"Invalid letter in scoring config: {letter!r}")

            if not isinstance(value, int):
                raise TypeError(f"Letter {letter_upper} has non-integer value: {value!r}")

            if value < 0:
                raise ValueError(f"Letter {letter_upper} has negative value: {value}")

            if letter_upper in normalized and normalized[letter_upper] != value:
                logger.warning(
                    f"Duplicate letter {letter_upper} in config (using first value: {normalized[letter_upper]})",
                )
            else:
                normalized[letter_upper] = value
                provided_letters.add(letter_upper)

        # Check for missing letters
        missing_letters = expected_letters - provided_letters
        if missing_letters:
            missing_str = ", ".join(sorted(missing_letters))
            raise ValueError(f"Scoring config from {source} is missing letters: {missing_str}")

        logger.debug(f"Successfully loaded custom scoring config with {len(normalized)} letters")
        return normalized

    @classmethod
    def load_from_file(cls, config_path: Path | str) -> dict[str, int]:
        """Load custom letter values from a JSON configuration file.

        The JSON file should contain a dictionary mapping letters (A-Z) to
        integer point values. Letters can be uppercase or lowercase in the file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            Dictionary mapping uppercase letters to point values

        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
            ValueError: If the config is invalid (missing letters, invalid values)

        Examples:
            >>> # Given custom_values.json: {"A": 5, "B": 2, ...}
            >>> values = ScoringConfig.load_from_file("custom_values.json")
            >>> values["A"]
            5
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Scoring config file not found: {path}")

        logger.debug(f"Loading custom scoring config from: {path}")

        try:
            with path.open() as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in scoring config file: {path}",
                e.doc,
                e.pos,
            ) from e

        # Validate and normalize the config
        return cls._validate_config(config_data, path)

    @classmethod
    def list_available_systems(cls) -> list[str]:
        """List all available built-in scoring systems.

        Returns:
            List of system names

        Examples:
            >>> systems = ScoringConfig.list_available_systems()
            >>> "scrabble" in systems
            True
            >>> "wordle" in systems
            True
        """
        return sorted(cls.BUILT_IN_SYSTEMS.keys())
