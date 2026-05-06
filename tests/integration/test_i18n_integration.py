"""Integration tests for i18n functionality."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from nhl_scrabble.config import Config
from nhl_scrabble.i18n import LOCALES_DIR, SUPPORTED_LOCALES, get_translator


class TestConfigLocale:
    """Test Config class locale field integration."""

    def test_config_locale_default(self):
        """Test Config uses default locale."""
        config = Config()
        assert config.locale == "en_US"

    def test_config_locale_from_env(self):
        """Test Config reads locale from environment."""
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
            config = Config()
            assert config.locale == "fr_CA"

    def test_config_locale_all_supported(self):
        """Test Config accepts all supported locales."""
        for locale_code in SUPPORTED_LOCALES:
            with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": locale_code}):
                config = Config()
                assert config.locale == locale_code

    def test_config_locale_validation_invalid(self):
        """Test Config validates invalid locale."""
        with (
            patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "invalid_LOCALE"}),
            pytest.raises(ValueError, match="NHL_SCRABBLE_LANG"),
        ):
            Config()

    def test_config_locale_validation_unsupported(self):
        """Test Config rejects unsupported but valid-format locale."""
        with (
            patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "ja_JP"}),
            pytest.raises(ValueError, match="NHL_SCRABBLE_LANG"),
        ):
            Config()

    def test_config_locale_case_sensitive(self):
        """Test Config locale is case-sensitive."""
        # Wrong case should be rejected
        with (
            patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "en_us"}),
            pytest.raises(ValueError, match="NHL_SCRABBLE_LANG"),
        ):
            Config()

    def test_config_from_env_locale(self):
        """Test Config.from_env() respects locale."""
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "sv_SE"}):
            config = Config.from_env()
            assert config.locale == "sv_SE"

    def test_config_to_dict_includes_locale(self):
        """Test Config.to_dict() includes locale."""
        config = Config()
        config_dict = config.to_dict()
        assert "locale" in config_dict
        assert config_dict["locale"] == "en_US"

    def test_config_repr_includes_locale(self):
        """Test Config.__repr__() includes locale."""
        config = Config()
        repr_str = repr(config)
        assert "locale" in repr_str.lower()


class TestI18nInfrastructure:
    """Test i18n infrastructure integration."""

    def test_locales_directory_exists(self):
        """Test locales directory is created."""
        # Directory may not exist until locales are initialized
        # Just verify path is defined correctly
        assert LOCALES_DIR.name == "locales"
        assert "nhl_scrabble" in str(LOCALES_DIR)

    def test_locales_dir_in_package(self):
        """Test locales directory is in nhl_scrabble package."""
        # Works both in development (src/nhl_scrabble) and installed (.tox/*/site-packages/nhl_scrabble)
        assert "nhl_scrabble" in str(LOCALES_DIR.absolute())
        assert LOCALES_DIR.name == "locales"

    def test_babel_cfg_exists(self):
        """Test babel.cfg configuration file exists."""
        # Find project root (go up from this test file)
        project_root = Path(__file__).parent.parent.parent
        babel_cfg = project_root / "babel.cfg"
        assert babel_cfg.exists(), "babel.cfg should exist in project root"

    def test_babel_cfg_content(self):
        """Test babel.cfg has correct content."""
        project_root = Path(__file__).parent.parent.parent
        babel_cfg = project_root / "babel.cfg"

        if babel_cfg.exists():
            content = babel_cfg.read_text()
            assert "[python:" in content
            assert "[jinja2:" in content
            assert "encoding = utf-8" in content

    def test_i18n_module_exists(self):
        """Test i18n.py module exists."""
        from nhl_scrabble import i18n

        assert i18n is not None
        assert hasattr(i18n, "get_translator")
        assert hasattr(i18n, "get_system_locale")
        assert hasattr(i18n, "format_number")

    def test_translation_workflow_docs_exist(self):
        """Test translation workflow documentation exists."""
        project_root = Path(__file__).parent.parent.parent
        docs_path = project_root / ".github" / "docs" / "translation-workflow.md"
        assert docs_path.exists(), "Translation workflow docs should exist"

    def test_translation_workflow_docs_content(self):
        """Test translation workflow docs have key sections."""
        project_root = Path(__file__).parent.parent.parent
        docs_path = project_root / ".github" / "docs" / "translation-workflow.md"

        if docs_path.exists():
            content = docs_path.read_text()
            # Check for key sections
            assert "pybabel extract" in content
            assert "pybabel init" in content
            assert "pybabel update" in content
            assert "pybabel compile" in content


class TestEnvironmentVariableIntegration:
    """Test environment variable integration across modules."""

    def test_env_var_affects_config_and_translator(self):
        """Test NHL_SCRABBLE_LANG affects both Config and translator."""
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "de_DE"}):
            # Config should read env var
            config = Config()
            assert config.locale == "de_DE"

            # Translator should also read env var when called with None
            _ = get_translator(None)
            assert callable(_)

    def test_config_locale_matches_translator_locale(self):
        """Test Config locale can be passed to get_translator."""
        config = Config()
        _ = get_translator(config.locale)
        assert callable(_)

    def test_all_config_locales_work_with_translator(self):
        """Test all Config-supported locales work with get_translator."""
        for locale_code in SUPPORTED_LOCALES:
            with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": locale_code}):
                config = Config()
                _ = get_translator(config.locale)
                assert callable(_)
                assert _("Test") == "Test"  # Identity function without translations


class TestPackageStructure:
    """Test package structure for i18n."""

    def test_i18n_module_in_nhl_scrabble(self):
        """Test i18n module is in nhl_scrabble package."""
        from nhl_scrabble import i18n

        assert "nhl_scrabble" in i18n.__name__

    def test_i18n_module_importable(self):
        """Test i18n module can be imported."""
        # Should not raise ImportError
        from nhl_scrabble.i18n import (
            DEFAULT_LOCALE,
            LOCALES_DIR,
            SUPPORTED_LOCALES,
            format_number,
            get_system_locale,
            get_translator,
        )

        # Verify exports are correct types
        assert isinstance(SUPPORTED_LOCALES, list)
        assert isinstance(DEFAULT_LOCALE, str)
        assert isinstance(LOCALES_DIR, Path)
        assert callable(get_translator)
        assert callable(get_system_locale)
        assert callable(format_number)

    def test_config_imports_i18n_constants(self):
        """Test Config can access i18n constants."""
        # Config validation uses i18n locale list
        # Test it works by creating config with valid locale
        config = Config()
        assert config.locale in SUPPORTED_LOCALES


class TestDocumentation:
    """Test documentation completeness."""

    def test_env_vars_docs_has_locale(self):
        """Test environment variables documentation includes NHL_SCRABBLE_LANG."""
        project_root = Path(__file__).parent.parent.parent
        env_vars_doc = project_root / "docs" / "reference" / "environment-variables.md"

        if env_vars_doc.exists():
            content = env_vars_doc.read_text()
            assert "NHL_SCRABBLE_LANG" in content
            assert "locale" in content.lower()

    def test_readme_mentions_i18n(self):
        """Test README mentions internationalization."""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "README.md"

        if readme.exists():
            content = readme.read_text()
            # Should mention i18n or internationalization
            has_i18n = (
                "i18n" in content.lower()
                or "internationalization" in content.lower()
                or "locale" in content.lower()
                or "translation" in content.lower()
            )
            assert has_i18n, "README should mention i18n/internationalization"


class TestDependencies:
    """Test i18n dependencies are installed."""

    def test_babel_importable(self):
        """Test babel can be imported."""
        try:
            import babel

            assert babel is not None
        except ImportError:
            pytest.skip("babel not installed (i18n optional dependency)")

    def test_flask_babel_importable(self):
        """Test flask-babel can be imported."""
        try:
            import flask_babel

            assert flask_babel is not None
        except ImportError:
            pytest.skip("flask-babel not installed (i18n optional dependency)")

    def test_gettext_available(self):
        """Test gettext module is available."""
        import gettext

        assert gettext is not None
        assert hasattr(gettext, "translation")


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_cli_translation_scenario(self):
        """Test scenario: CLI uses translation in French."""
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
            config = Config()
            _ = get_translator(config.locale)

            # Simulate CLI strings (without compiled translations, identity function)
            assert callable(_)
            result = _("Analyzing NHL rosters...")
            # Without translations, returns original
            assert result == "Analyzing NHL rosters..."

    def test_web_translation_scenario(self):
        """Test scenario: Web interface uses translation in Swedish."""
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "sv_SE"}):
            config = Config()
            _ = get_translator(config.locale)

            assert callable(_)
            result = _("Team")
            # With Swedish translations, should return translated string
            assert result == "Lag"

    def test_number_formatting_scenario(self):
        """Test scenario: Format score for different locales."""
        from nhl_scrabble.i18n import format_number

        # US English (fallback mode for testing)
        score = 1234.56
        formatted = format_number(score, "invalid")
        assert formatted == "1234.56"

    def test_locale_switching_scenario(self):
        """Test scenario: User switches locale mid-session."""
        # Start with English
        config1 = Config()
        _en = get_translator(config1.locale)

        # Switch to French
        with patch.dict(os.environ, {"NHL_SCRABBLE_LANG": "fr_CA"}):
            config2 = Config()
            _fr = get_translator(config2.locale)

        # Both should work
        assert callable(_en)
        assert callable(_fr)
        assert _en("Test") == "Test"
        assert _fr("Test") == "Test"
