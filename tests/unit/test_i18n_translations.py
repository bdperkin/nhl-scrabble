"""Tests for priority language translations (fr_CA, sv_SE)."""

import pytest

from nhl_scrabble.i18n import get_translator


class TestFrenchCanadianTranslations:
    """Test French Canadian (fr_CA) translations."""

    def test_fr_ca_translator_loads(self):
        """Test that fr_CA translator loads without error."""
        translator = get_translator("fr_CA")
        assert callable(translator)

    def test_fr_ca_common_hockey_terms(self):
        """Test translation of common hockey terminology."""
        translator = get_translator("fr_CA")

        # Test common terms
        assert translator("Team") == "Équipe"
        assert translator("Player") == "Joueur"
        assert translator("Score") == "Score"

    def test_fr_ca_output_format_option(self):
        """Test translation of CLI output format option."""
        translator = get_translator("fr_CA")

        result = translator("Output format (default: text)")
        assert "Format de sortie" in result
        assert "texte" in result

    def test_fr_ca_verbose_option(self):
        """Test translation of verbose logging option."""
        translator = get_translator("fr_CA")

        result = translator("Enable verbose logging")
        assert "journalisation" in result or "détaillée" in result

    def test_fr_ca_preserves_placeholders(self):
        """Test that placeholders are preserved in translations."""
        translator = get_translator("fr_CA")

        # Test string with placeholder that exists in .po file
        result = translator("  • Teams: {teams}")
        assert "{teams}" in result
        assert "équipe" in result.lower()

    def test_fr_ca_preserves_rich_markup(self):
        """Test that Rich markup is preserved in translations."""
        translator = get_translator("fr_CA")

        # Test string with Rich markup
        result = translator("[yellow]⚠[/yellow]  Failed teams: {teams}")
        assert "[yellow]" in result
        assert "[/yellow]" in result
        assert "{teams}" in result

    def test_fr_ca_fallback_for_untranslated(self):
        """Test that untranslated strings fall back to English."""
        translator = get_translator("fr_CA")

        # Test with a string that definitely doesn't exist
        fake_string = "This is a totally fake string that will never be translated xyz123"
        result = translator(fake_string)
        assert result == fake_string


class TestSwedishTranslations:
    """Test Swedish (sv_SE) translations."""

    def test_sv_se_translator_loads(self):
        """Test that sv_SE translator loads without error."""
        translator = get_translator("sv_SE")
        assert callable(translator)

    def test_sv_se_common_hockey_terms(self):
        """Test translation of common hockey terminology."""
        translator = get_translator("sv_SE")

        # Test common terms
        assert translator("Team") == "Lag"
        assert translator("Player") == "Spelare"
        assert translator("Score") == "Poäng"

    def test_sv_se_output_format_option(self):
        """Test translation of CLI output format option."""
        translator = get_translator("sv_SE")

        result = translator("Output format (default: text)")
        assert "Utdataformat" in result or "format" in result.lower()
        assert "text" in result.lower()

    def test_sv_se_verbose_option(self):
        """Test translation of verbose logging option."""
        translator = get_translator("sv_SE")

        result = translator("Enable verbose logging")
        assert "loggning" in result.lower() or "utförlig" in result.lower()

    def test_sv_se_preserves_placeholders(self):
        """Test that placeholders are preserved in translations."""
        translator = get_translator("sv_SE")

        # Test string with placeholder that exists in .po file
        result = translator("  • Teams: {teams}")
        assert "{teams}" in result
        assert "lag" in result.lower()

    def test_sv_se_preserves_rich_markup(self):
        """Test that Rich markup is preserved in translations."""
        translator = get_translator("sv_SE")

        # Test string with Rich markup
        result = translator("[yellow]⚠[/yellow]  Failed teams: {teams}")
        assert "[yellow]" in result
        assert "[/yellow]" in result
        assert "{teams}" in result

    def test_sv_se_fallback_for_untranslated(self):
        """Test that untranslated strings fall back to English."""
        translator = get_translator("sv_SE")

        # Test with a string that definitely doesn't exist
        fake_string = "This is a totally fake string that will never be translated xyz123"
        result = translator(fake_string)
        assert result == fake_string


class TestTranslationCompleteness:
    """Test translation completeness and consistency."""

    @pytest.mark.parametrize("locale", ["fr_CA", "sv_SE"])
    def test_locale_has_compiled_mo_file(self, locale):
        """Test that .mo binary file exists for locale."""
        from pathlib import Path

        mo_file = (
            Path("src/nhl_scrabble/locales")
            / locale
            / "LC_MESSAGES"
            / "messages.mo"
        )
        assert mo_file.exists(), f"Missing .mo file for {locale}"

    @pytest.mark.parametrize("locale", ["fr_CA", "sv_SE"])
    def test_locale_translation_file_exists(self, locale):
        """Test that .po translation file exists for locale."""
        from pathlib import Path

        po_file = (
            Path("src/nhl_scrabble/locales")
            / locale
            / "LC_MESSAGES"
            / "messages.po"
        )
        assert po_file.exists(), f"Missing .po file for {locale}"

    @pytest.mark.parametrize("locale", ["fr_CA", "sv_SE"])
    def test_locale_has_translations(self, locale):
        """Test that locale has actual translations (not all empty)."""
        from pathlib import Path

        po_file = (
            Path("src/nhl_scrabble/locales")
            / locale
            / "LC_MESSAGES"
            / "messages.po"
        )

        content = po_file.read_text(encoding="utf-8")

        # Count non-empty msgstr lines
        import re

        msgstr_pattern = re.compile(r'^msgstr "(.+)"', re.MULTILINE)
        non_empty_translations = len(
            [m for m in msgstr_pattern.findall(content) if m]
        )

        assert (
            non_empty_translations > 0
        ), f"No translations found in {locale}/messages.po"

    def test_fr_ca_vs_sv_se_consistency(self):
        """Test that fr_CA and sv_SE have similar translation coverage."""
        translator_fr = get_translator("fr_CA")
        translator_sv = get_translator("sv_SE")

        # Test same strings translate to different values using actual .po entries
        test_strings = [
            "Output format (default: text)",
            "Enable verbose logging",
            "Clear API cache before running",
        ]

        for string in test_strings:
            fr_result = translator_fr(string)
            sv_result = translator_sv(string)

            # Both should be translated (different from English)
            assert fr_result != string, (
                f"French did not translate '{string}'"
            )
            assert sv_result != string, (
                f"Swedish did not translate '{string}'"
            )
            # And they should be different from each other
            assert fr_result != sv_result, (
                f"French and Swedish produced same translation for '{string}'"
            )


class TestTranslationQuality:
    """Test translation quality and format preservation."""

    def test_fr_ca_no_placeholder_corruption(self):
        """Test that placeholders are not corrupted in French."""
        translator = get_translator("fr_CA")

        # Test various placeholder formats using actual translated strings
        test_cases = [
            ("  • Teams: {teams}", "{teams}"),
            ("[yellow]⚠[/yellow]  Failed teams: {teams}", "{teams}"),
            ("[yellow]⚠[/yellow]  Failed teams: {teams}", "[yellow]"),
            ("[yellow]⚠[/yellow]  Failed teams: {teams}", "[/yellow]"),
        ]

        for original, expected_preserved in test_cases:
            result = translator(original)
            assert expected_preserved in result, (
                f"Placeholder '{expected_preserved}' missing in translation of '{original}'"
            )

    def test_sv_se_no_placeholder_corruption(self):
        """Test that placeholders are not corrupted in Swedish."""
        translator = get_translator("sv_SE")

        # Test various placeholder formats using actual translated strings
        test_cases = [
            ("  • Teams: {teams}", "{teams}"),
            ("[yellow]⚠[/yellow]  Failed teams: {teams}", "{teams}"),
            ("[yellow]⚠[/yellow]  Failed teams: {teams}", "[yellow]"),
            ("[yellow]⚠[/yellow]  Failed teams: {teams}", "[/yellow]"),
        ]

        for original, expected_preserved in test_cases:
            result = translator(original)
            assert expected_preserved in result, (
                f"Placeholder '{expected_preserved}' missing in translation of '{original}'"
            )

    @pytest.mark.parametrize("locale", ["fr_CA", "sv_SE"])
    def test_translation_encoding_utf8(self, locale):
        """Test that translation files use UTF-8 encoding."""
        from pathlib import Path

        po_file = (
            Path("src/nhl_scrabble/locales")
            / locale
            / "LC_MESSAGES"
            / "messages.po"
        )

        content = po_file.read_text(encoding="utf-8")
        assert 'charset=utf-8' in content.lower() or 'charset=UTF-8' in content
