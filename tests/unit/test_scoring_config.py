"""Tests for scoring configuration management."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003

import pytest

from nhl_scrabble.scoring.config import ScoringConfig


class TestScoringConfig:
    """Tests for ScoringConfig class."""

    def test_scrabble_values_exist(self) -> None:
        """Test that standard Scrabble values are defined."""
        assert len(ScoringConfig.SCRABBLE_VALUES) == 26
        assert ScoringConfig.SCRABBLE_VALUES["Q"] == 10
        assert ScoringConfig.SCRABBLE_VALUES["Z"] == 10
        assert ScoringConfig.SCRABBLE_VALUES["A"] == 1
        assert ScoringConfig.SCRABBLE_VALUES["E"] == 1

    def test_wordle_values_exist(self) -> None:
        """Test that Wordle-inspired values are defined."""
        assert len(ScoringConfig.WORDLE_VALUES) == 26
        # Common letters should be worth less
        assert ScoringConfig.WORDLE_VALUES["E"] == 1
        assert ScoringConfig.WORDLE_VALUES["A"] == 1
        # Rare letters should be worth more
        assert ScoringConfig.WORDLE_VALUES["Q"] == 3
        assert ScoringConfig.WORDLE_VALUES["Z"] == 3

    def test_uniform_values_exist(self) -> None:
        """Test that uniform values are defined."""
        assert len(ScoringConfig.UNIFORM_VALUES) == 26
        # All letters should be worth 1
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert ScoringConfig.UNIFORM_VALUES[letter] == 1

    def test_get_scrabble_system(self) -> None:
        """Test getting standard Scrabble scoring system."""
        values = ScoringConfig.get_scoring_system("scrabble")
        assert values == ScoringConfig.SCRABBLE_VALUES
        # Should return a copy, not the original
        values["A"] = 999
        assert ScoringConfig.SCRABBLE_VALUES["A"] == 1

    def test_get_wordle_system(self) -> None:
        """Test getting Wordle scoring system."""
        values = ScoringConfig.get_scoring_system("wordle")
        assert values == ScoringConfig.WORDLE_VALUES

    def test_get_uniform_system(self) -> None:
        """Test getting uniform scoring system."""
        values = ScoringConfig.get_scoring_system("uniform")
        assert values == ScoringConfig.UNIFORM_VALUES

    def test_get_system_case_insensitive(self) -> None:
        """Test that system names are case-insensitive."""
        assert ScoringConfig.get_scoring_system("SCRABBLE") == ScoringConfig.SCRABBLE_VALUES
        assert ScoringConfig.get_scoring_system("Wordle") == ScoringConfig.WORDLE_VALUES
        assert ScoringConfig.get_scoring_system("UnIfOrM") == ScoringConfig.UNIFORM_VALUES

    def test_get_unknown_system_raises(self) -> None:
        """Test that unknown system names raise ValueError."""
        with pytest.raises(ValueError, match="Unknown scoring system: unknown"):
            ScoringConfig.get_scoring_system("unknown")

    def test_list_available_systems(self) -> None:
        """Test listing available scoring systems."""
        systems = ScoringConfig.list_available_systems()
        assert "scrabble" in systems
        assert "wordle" in systems
        assert "uniform" in systems
        assert len(systems) == 3

    def test_load_from_file_valid(self, tmp_path: Path) -> None:
        """Test loading a valid custom configuration file."""
        config_file = tmp_path / "custom.json"
        custom_values = {chr(i): i - 64 for i in range(65, 91)}  # A=1, B=2, ..., Z=26
        config_file.write_text(json.dumps(custom_values))

        values = ScoringConfig.load_from_file(config_file)
        assert values["A"] == 1
        assert values["Z"] == 26
        assert len(values) == 26

    def test_load_from_file_lowercase_letters(self, tmp_path: Path) -> None:
        """Test loading config with lowercase letters (should normalize)."""
        config_file = tmp_path / "custom.json"
        custom_values = {chr(i): i - 96 for i in range(97, 123)}  # a=1, b=2, ..., z=26
        config_file.write_text(json.dumps(custom_values))

        values = ScoringConfig.load_from_file(config_file)
        assert values["A"] == 1  # Normalized to uppercase
        assert values["Z"] == 26
        assert "a" not in values  # No lowercase keys

    def test_load_from_file_mixed_case(self, tmp_path: Path) -> None:
        """Test loading config with mixed case letters."""
        config_file = tmp_path / "custom.json"
        custom_values = {
            "A": 5,
            "b": 3,
            "C": 2,
            **{chr(i): 1 for i in range(68, 91)},  # D-Z all worth 1
        }
        config_file.write_text(json.dumps(custom_values))

        values = ScoringConfig.load_from_file(config_file)
        assert values["A"] == 5
        assert values["B"] == 3  # Normalized
        assert values["C"] == 2

    def test_load_from_file_missing_letters_raises(self, tmp_path: Path) -> None:
        """Test that missing letters raise ValueError."""
        config_file = tmp_path / "incomplete.json"
        incomplete_values = {"A": 1, "B": 2}  # Only 2 letters
        config_file.write_text(json.dumps(incomplete_values))

        with pytest.raises(ValueError, match="missing letters"):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_invalid_letter_raises(self, tmp_path: Path) -> None:
        """Test that invalid letters raise ValueError."""
        config_file = tmp_path / "invalid.json"
        invalid_values = {
            **{chr(i): 1 for i in range(65, 91)},
            "1": 5,  # Invalid: not a letter
        }
        config_file.write_text(json.dumps(invalid_values))

        with pytest.raises(ValueError, match="Invalid letter"):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_non_integer_value_raises(self, tmp_path: Path) -> None:
        """Test that non-integer values raise TypeError."""
        config_file = tmp_path / "non_int.json"
        invalid_values = {
            **{chr(i): 1 for i in range(65, 90)},
            "Z": "five",  # Invalid: string instead of int
        }
        config_file.write_text(json.dumps(invalid_values))

        with pytest.raises(TypeError, match="non-integer value"):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_negative_value_raises(self, tmp_path: Path) -> None:
        """Test that negative values raise ValueError."""
        config_file = tmp_path / "negative.json"
        invalid_values = {
            **{chr(i): 1 for i in range(65, 90)},
            "Z": -5,  # Invalid: negative value
        }
        config_file.write_text(json.dumps(invalid_values))

        with pytest.raises(ValueError, match="negative value"):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_not_dict_raises(self, tmp_path: Path) -> None:
        """Test that non-dict JSON raises TypeError."""
        config_file = tmp_path / "not_dict.json"
        config_file.write_text(json.dumps([1, 2, 3]))  # List instead of dict

        with pytest.raises(TypeError, match="must be a dictionary"):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_not_found_raises(self, tmp_path: Path) -> None:
        """Test that non-existent file raises FileNotFoundError."""
        config_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_invalid_json_raises(self, tmp_path: Path) -> None:
        """Test that invalid JSON raises JSONDecodeError."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            ScoringConfig.load_from_file(config_file)

    def test_load_from_file_duplicate_letters_warns(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that duplicate letters log a warning (uses first value)."""
        config_file = tmp_path / "duplicate.json"
        # Create config with duplicate 'A' (both uppercase and lowercase)
        config_data = {chr(i): 1 for i in range(65, 91)}
        config_data["a"] = 10  # Duplicate, different value

        config_file.write_text(json.dumps(config_data))

        values = ScoringConfig.load_from_file(config_file)
        # Should use the first value (uppercase A)
        assert values["A"] == 1
        # Should log a warning
        assert "Duplicate letter A" in caplog.text

    def test_validate_config_zero_value_allowed(self, tmp_path: Path) -> None:
        """Test that zero values are allowed."""
        config_file = tmp_path / "zeros.json"
        values_with_zeros = {chr(i): 0 for i in range(65, 91)}  # All zeros
        config_file.write_text(json.dumps(values_with_zeros))

        values = ScoringConfig.load_from_file(config_file)
        assert all(v == 0 for v in values.values())

    def test_load_from_file_string_path(self, tmp_path: Path) -> None:
        """Test loading from string path (not Path object)."""
        config_file = tmp_path / "custom.json"
        custom_values = {chr(i): 1 for i in range(65, 91)}
        config_file.write_text(json.dumps(custom_values))

        # Pass as string, not Path
        values = ScoringConfig.load_from_file(str(config_file))
        assert len(values) == 26
