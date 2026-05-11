"""Unit tests for position mapping utilities."""

import pytest

from nhl_scrabble.utils.positions import (
    POSITION_CODES,
    POSITION_TYPES,
    get_all_position_codes,
    get_all_position_names,
    get_all_position_types,
    get_position_name,
    get_position_type,
    validate_position_code,
)


class TestPositionCodeMapping:
    """Tests for position code to name mapping."""

    def test_center_mapping(self) -> None:
        """Test Center position mapping."""
        assert get_position_name("C") == "Center"

    def test_left_wing_mapping(self) -> None:
        """Test Left Wing position mapping."""
        assert get_position_name("L") == "Left Wing"

    def test_right_wing_mapping(self) -> None:
        """Test Right Wing position mapping."""
        assert get_position_name("R") == "Right Wing"

    def test_defense_mapping(self) -> None:
        """Test Defense position mapping."""
        assert get_position_name("D") == "Defense"

    def test_goalie_mapping(self) -> None:
        """Test Goalie position mapping."""
        assert get_position_name("G") == "Goalie"

    def test_case_insensitive_mapping(self) -> None:
        """Test position mapping is case-insensitive."""
        assert get_position_name("c") == "Center"
        assert get_position_name("C") == "Center"
        assert get_position_name("g") == "Goalie"
        assert get_position_name("G") == "Goalie"

    def test_unknown_position_code(self) -> None:
        """Test unknown position code returns the code itself."""
        assert get_position_name("X") == "X"
        assert get_position_name("Z") == "Z"
        assert get_position_name("") == ""


class TestPositionTypeMapping:
    """Tests for position code to type mapping."""

    def test_center_is_forward(self) -> None:
        """Test Center is Forward type."""
        assert get_position_type("C") == "Forward"

    def test_left_wing_is_forward(self) -> None:
        """Test Left Wing is Forward type."""
        assert get_position_type("L") == "Forward"

    def test_right_wing_is_forward(self) -> None:
        """Test Right Wing is Forward type."""
        assert get_position_type("R") == "Forward"

    def test_defense_type(self) -> None:
        """Test Defense position type."""
        assert get_position_type("D") == "Defense"

    def test_goalie_type(self) -> None:
        """Test Goalie position type."""
        assert get_position_type("G") == "Goalie"

    def test_case_insensitive_type(self) -> None:
        """Test position type mapping is case-insensitive."""
        assert get_position_type("c") == "Forward"
        assert get_position_type("C") == "Forward"
        assert get_position_type("d") == "Defense"
        assert get_position_type("D") == "Defense"

    def test_unknown_position_type(self) -> None:
        """Test unknown position code returns Unknown."""
        assert get_position_type("X") == "Unknown"
        assert get_position_type("Z") == "Unknown"
        assert get_position_type("") == "Unknown"


class TestPositionValidation:
    """Tests for position code validation."""

    def test_valid_position_codes(self) -> None:
        """Test validation of valid position codes."""
        assert validate_position_code("C") is True
        assert validate_position_code("L") is True
        assert validate_position_code("R") is True
        assert validate_position_code("D") is True
        assert validate_position_code("G") is True

    def test_case_insensitive_validation(self) -> None:
        """Test validation is case-insensitive."""
        assert validate_position_code("c") is True
        assert validate_position_code("d") is True
        assert validate_position_code("g") is True

    def test_invalid_position_codes(self) -> None:
        """Test validation of invalid position codes."""
        assert validate_position_code("X") is False
        assert validate_position_code("Z") is False
        assert validate_position_code("") is False
        assert validate_position_code("AA") is False


class TestPositionConstants:
    """Tests for position constant dictionaries."""

    def test_position_codes_contains_all_positions(self) -> None:
        """Test POSITION_CODES contains all NHL positions."""
        assert len(POSITION_CODES) == 5
        assert "C" in POSITION_CODES
        assert "L" in POSITION_CODES
        assert "R" in POSITION_CODES
        assert "D" in POSITION_CODES
        assert "G" in POSITION_CODES

    def test_position_types_contains_all_positions(self) -> None:
        """Test POSITION_TYPES contains all NHL positions."""
        assert len(POSITION_TYPES) == 5
        assert "C" in POSITION_TYPES
        assert "L" in POSITION_TYPES
        assert "R" in POSITION_TYPES
        assert "D" in POSITION_TYPES
        assert "G" in POSITION_TYPES

    def test_position_types_mapping(self) -> None:
        """Test position types are correctly mapped."""
        assert POSITION_TYPES["C"] == "Forward"
        assert POSITION_TYPES["L"] == "Forward"
        assert POSITION_TYPES["R"] == "Forward"
        assert POSITION_TYPES["D"] == "Defense"
        assert POSITION_TYPES["G"] == "Goalie"


class TestGetAllPositions:
    """Tests for getting all position codes/names/types."""

    def test_get_all_position_codes(self) -> None:
        """Test getting all position codes."""
        codes = get_all_position_codes()
        assert len(codes) == 5
        assert "C" in codes
        assert "L" in codes
        assert "R" in codes
        assert "D" in codes
        assert "G" in codes

    def test_get_all_position_names(self) -> None:
        """Test getting all position names."""
        names = get_all_position_names()
        assert len(names) == 5
        assert "Center" in names
        assert "Left Wing" in names
        assert "Right Wing" in names
        assert "Defense" in names
        assert "Goalie" in names

    def test_get_all_position_types(self) -> None:
        """Test getting all unique position types."""
        types = get_all_position_types()
        assert len(types) == 3
        assert "Forward" in types
        assert "Defense" in types
        assert "Goalie" in types


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_string_position_code(self) -> None:
        """Test empty string position code handling."""
        assert get_position_name("") == ""
        assert get_position_type("") == "Unknown"
        assert validate_position_code("") is False

    def test_whitespace_position_code(self) -> None:
        """Test whitespace in position code."""
        # Current implementation doesn't strip whitespace
        assert validate_position_code(" C ") is False
        assert get_position_name(" C ") == " C "

    @pytest.mark.parametrize(
        ("code", "expected_name"),
        [
            ("C", "Center"),
            ("L", "Left Wing"),
            ("R", "Right Wing"),
            ("D", "Defense"),
            ("G", "Goalie"),
        ],
    )
    def test_all_codes_parametrized(self, code: str, expected_name: str) -> None:
        """Test all position codes with parametrization."""
        assert get_position_name(code) == expected_name

    @pytest.mark.parametrize(
        ("code", "expected_type"),
        [
            ("C", "Forward"),
            ("L", "Forward"),
            ("R", "Forward"),
            ("D", "Defense"),
            ("G", "Goalie"),
        ],
    )
    def test_all_types_parametrized(self, code: str, expected_type: str) -> None:
        """Test all position types with parametrization."""
        assert get_position_type(code) == expected_type
