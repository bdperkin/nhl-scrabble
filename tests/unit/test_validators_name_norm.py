"""Unit tests for input validation utilities."""

from pathlib import Path

import pytest

from nhl_scrabble.validators import (
    ValidationError,
    normalize_player_name,
    validate_api_response_structure,
    validate_file_path,
    validate_float_range,
    validate_output_format,
    validate_player_name,
    validate_team_abbreviation,
    validate_url,
)


class TestNormalizePlayerName:
    """Tests for normalize_player_name()."""

    def test_normalize_removes_czech_diacritics(self) -> None:
        """Test diacritic removal from Czech names."""
        assert normalize_player_name("Ondřej") == "Ondrej"
        assert normalize_player_name("Tomáš") == "Tomas"
        assert normalize_player_name("Lukáš") == "Lukas"
        assert normalize_player_name("Voráček") == "Voracek"

    def test_normalize_removes_french_accents(self) -> None:
        """Test accent removal from French names."""
        assert normalize_player_name("José") == "Jose"
        assert normalize_player_name("René") == "Rene"
        assert normalize_player_name("Théodore") == "Theodore"
        assert normalize_player_name("Québec") == "Quebec"

    def test_normalize_removes_scandinavian_characters(self) -> None:
        """Test Scandinavian character normalization."""
        assert normalize_player_name("Bjørn") == "Bjorn"
        assert normalize_player_name("Øvergård") == "Overgard"
        assert normalize_player_name("Sörensen") == "Sorensen"

    def test_normalize_preserves_ascii_names(self) -> None:
        """Test ASCII names are unchanged."""
        assert normalize_player_name("Connor McDavid") == "Connor McDavid"
        assert normalize_player_name("P.K. Subban") == "P.K. Subban"
        assert normalize_player_name("Jean-Gabriel Pageau") == "Jean-Gabriel Pageau"
        assert normalize_player_name("Ryan O'Reilly") == "Ryan O'Reilly"

    def test_normalize_full_names_with_accents(self) -> None:
        """Test normalization of full names with accented characters."""
        assert normalize_player_name("Ondřej Pavelec") == "Ondrej Pavelec"
        assert normalize_player_name("José Théodore") == "Jose Theodore"
        assert normalize_player_name("Tomáš Hertl") == "Tomas Hertl"

    def test_normalize_handles_special_ligatures(self) -> None:
        """Test handling of special ligatures."""
        # unidecode converts ligatures: œ → oe, æ → ae
        assert normalize_player_name("Fœrster") == "Foerster"
        assert normalize_player_name("Jæger") == "Jaeger"

    def test_normalize_handles_german_characters(self) -> None:
        """Test German character normalization."""
        # ü → u (via NFD), ß → ss (via unidecode)
        assert normalize_player_name("Müller") == "Muller"
        assert normalize_player_name("Straße") == "Strasse"

    def test_normalize_handles_empty_string(self) -> None:
        """Test normalization of empty string."""
        assert normalize_player_name("") == ""

    def test_normalize_handles_whitespace(self) -> None:
        """Test normalization preserves whitespace."""
        assert normalize_player_name("  John Doe  ") == "  John Doe  "
        assert normalize_player_name("Multiple   Spaces") == "Multiple   Spaces"

    def test_normalize_handles_mixed_scripts(self) -> None:
        """Test normalization of mixed Latin and non-Latin scripts."""
        # Cyrillic transliteration
        assert "Connor" in normalize_player_name("Connor Смирнов")
        # Result should be ASCII-only after normalization
        result = normalize_player_name("Connor Смирнов")
        assert result.isascii()

    def test_normalize_handles_emoji_conversion(self) -> None:
        """Test emoji normalization (converted to text representation)."""
        # unidecode converts emoji to text representation: 😀 → :grinning_face:
        result = normalize_player_name("Connor 😀")
        # Should contain "Connor" and be ASCII-only
        assert "Connor" in result
        assert result.isascii()

    def test_normalize_result_is_ascii(self) -> None:
        """Test all normalization results are ASCII-only."""
        test_cases = [
            "Ondřej Pavelec",
            "José Théodore",
            "Bjørn Sørensen",
            "Müller",
            "Straße",
            "Fœrster",
        ]
        for name in test_cases:
            result = normalize_player_name(name)
            assert result.isascii(), f"Result '{result}' is not ASCII for input '{name}'"

    def test_normalize_deterministic(self) -> None:
        """Test normalization is deterministic (same input → same output)."""
        name = "Ondřej Pavelec"
        result1 = normalize_player_name(name)
        result2 = normalize_player_name(name)
        assert result1 == result2


class TestValidatePlayerName:
    """Tests for validate_player_name()."""

    def test_valid_simple_name(self) -> None:
        """Test valid simple name."""
        result = validate_player_name("Connor McDavid")
        assert result == "Connor McDavid"

    def test_valid_hyphenated_name(self) -> None:
        """Test valid hyphenated name."""
        result = validate_player_name("Jean-Gabriel Pageau")
        assert result == "Jean-Gabriel Pageau"

    def test_valid_name_with_apostrophe(self) -> None:
        """Test valid name with apostrophe."""
        result = validate_player_name("Ryan O'Reilly")
        assert result == "Ryan O'Reilly"

    def test_valid_name_with_period(self) -> None:
        """Test valid name with period."""
        result = validate_player_name("P.K. Subban")
        assert result == "P.K. Subban"

    def test_whitespace_stripped(self) -> None:
        """Test leading/trailing whitespace is stripped."""
        result = validate_player_name("  Connor McDavid  ")
        assert result == "Connor McDavid"

    def test_empty_name(self) -> None:
        """Test error when name is empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_player_name("")

    def test_whitespace_only(self) -> None:
        """Test error when name is only whitespace."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_player_name("   ")

    def test_name_too_long(self) -> None:
        """Test error when name too long."""
        with pytest.raises(ValidationError, match="too long"):
            validate_player_name("A" * 101)

    def test_invalid_characters_script_tag(self) -> None:
        """Test error when name contains script tag (XSS attempt)."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor<script>alert(1)</script>")

    def test_invalid_characters_numbers(self) -> None:
        """Test error when name contains numbers."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor123")

    def test_invalid_characters_special(self) -> None:
        """Test error when name contains special characters."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor@McDavid")

    def test_accepts_accented_names_after_normalization(self) -> None:
        """Test validation accepts accented names after normalization."""
        # Czech names with diacritics - should normalize and validate successfully
        assert validate_player_name("Ondřej Pavelec") == "Ondrej Pavelec"
        assert validate_player_name("Tomáš Hertl") == "Tomas Hertl"

        # French names with accents
        assert validate_player_name("José Théodore") == "Jose Theodore"
        assert validate_player_name("René Bourque") == "Rene Bourque"

        # Scandinavian names
        assert validate_player_name("Bjørn Sørensen") == "Bjorn Sorensen"

    def test_normalized_name_returned(self) -> None:
        """Test that normalized (ASCII) name is returned, not original Unicode."""
        # Original has diacritics, result should be ASCII
        result = validate_player_name("Ondřej Pavelec")
        assert result == "Ondrej Pavelec"
        assert result != "Ondřej Pavelec"
        assert result.isascii()

    def test_emoji_removed_by_normalization(self) -> None:
        """Test emojis are removed during normalization (name still valid if remainder is valid)."""
        # Emoji normalization removes emoji entirely, leaving just the text
        # If the remaining text is valid, validation passes
        result = validate_player_name("Connor 😀 McDavid")
        assert result == "Connor  McDavid"  # Emoji removed, leaves double space
        assert result.isascii()

    def test_special_symbols_still_rejected(self) -> None:
        """Test special symbols still fail validation."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("Connor <script> McDavid")

    def test_trademark_symbols_rejected(self) -> None:
        """Test trademark/copyright symbols fail validation after normalization."""
        # Symbols normalize to text with parentheses: ™ → (tm), ® → (r), © → (c)
        # Parentheses are invalid characters
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_player_name("™️®️©️")

    def test_only_emoji_becomes_empty(self) -> None:
        """Test names with only emoji become empty after normalization."""
        # Pure emoji normalizes to empty string
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_player_name("😀😀😀")
