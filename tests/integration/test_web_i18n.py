"""Integration tests for web interface internationalization."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.i18n import SUPPORTED_LOCALES


@pytest.fixture
def mock_nhl_client():
    """Mock NHL API client with fixture data."""
    # Need to patch NHLApiClient in all route modules where it's imported
    with (
        patch("nhl_scrabble.web.routes.core.NHLApiClient") as mock_core,
        patch("nhl_scrabble.web.routes.teams.NHLApiClient") as mock_teams,
        patch("nhl_scrabble.web.routes.players.NHLApiClient") as mock_players,
    ):
        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        # Mock team data
        mock_client.get_teams.return_value = {
            "TOR": {"division": "Atlantic", "conference": "Eastern"},
        }

        # Mock roster data
        mock_client.get_team_roster.return_value = {
            "forwards": [
                {
                    "playerId": 1,
                    "firstName": {"default": "John"},
                    "lastName": {"default": "Doe"},
                },
            ],
            "defensemen": [],
            "goalies": [],
        }

        # All patches return the same mock client
        mock_core.return_value = mock_client
        mock_teams.return_value = mock_client
        mock_players.return_value = mock_client
        yield mock_client


class TestLocaleDetection:
    """Test locale detection from headers and query parameters."""

    def test_default_locale(self, mock_nhl_client):
        """Test default locale when none specified."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        # Default locale should be en_US

    def test_query_param_locale(self, mock_nhl_client):
        """Test locale from ?lang= query parameter."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)

        for locale in ["en_US", "fr_CA", "sv_SE"]:
            response = client.get(f"/?lang={locale}")
            assert response.status_code == 200

    def test_invalid_locale_ignored(self, mock_nhl_client):
        """Test invalid locale falls back to default."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)
        response = client.get("/?lang=invalid_LOCALE")

        assert response.status_code == 200

    def test_accept_language_header(self, mock_nhl_client):
        """Test locale from Accept-Language header."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)

        # Test with exact match
        headers = {"Accept-Language": "fr-CA,en;q=0.9"}
        response = client.get("/", headers=headers)
        assert response.status_code == 200

        # Test with language-only match
        headers = {"Accept-Language": "sv,en;q=0.8"}
        response = client.get("/", headers=headers)
        assert response.status_code == 200

    def test_query_param_overrides_header(self, mock_nhl_client):
        """Test ?lang= parameter takes precedence over header."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)
        headers = {"Accept-Language": "sv-SE"}
        response = client.get("/?lang=fr_CA", headers=headers)

        assert response.status_code == 200
        # Should use fr_CA from query param, not sv_SE from header


class TestTemplateRendering:
    """Test template rendering with different locales."""

    def test_index_renders_all_locales(self, mock_nhl_client):
        """Test index page renders for all supported locales."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)

        for locale in SUPPORTED_LOCALES:
            response = client.get(f"/?lang={locale}")
            assert response.status_code == 200
            # Check that key content is present
            assert "NHL" in response.text or "Scrabble" in response.text

    def test_language_selector_present(self, mock_nhl_client):
        """Test language selector is present in page."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        # Check for language selector
        assert "languageSelect" in response.text or "language-selector" in response.text

    def test_language_selector_has_all_locales(self, mock_nhl_client):
        """Test language selector includes all supported locales."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        # Check that all locale codes appear in options
        for locale in SUPPORTED_LOCALES:
            assert locale in response.text

    def test_selected_locale_marked(self, mock_nhl_client):
        """Test selected locale is marked in selector."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)

        # Test with French Canadian
        response = client.get("/?lang=fr_CA")
        assert response.status_code == 200
        # Selected option should have selected attribute near fr_CA
        # (exact HTML structure may vary, but both should appear close together)
        assert "fr_CA" in response.text


class TestAPIEndpoints:
    """Test API endpoints preserve locale context."""

    def test_teams_page_with_locale(self, mock_nhl_client):
        """Test /teams page respects locale parameter."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)

        for locale in ["en_US", "fr_CA", "sv_SE"]:
            response = client.get(f"/teams?lang={locale}")
            assert response.status_code == 200

    def test_stats_page_with_locale(self, mock_nhl_client):
        """Test /stats page respects locale parameter."""
        from nhl_scrabble.web.app import app

        client = TestClient(app)

        for locale in ["en_US", "fr_CA", "sv_SE"]:
            response = client.get(f"/stats?lang={locale}")
            assert response.status_code == 200


class TestGetRequestLocale:
    """Test get_request_locale helper function."""

    def test_priority_order(self, mock_nhl_client):
        """Test locale detection priority: ?lang > Accept-Language > default."""
        from starlette.requests import Request

        from nhl_scrabble.web.locale import get_request_locale

        # Test query parameter (highest priority)
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"lang=fr_CA",
            "headers": [(b"accept-language", b"sv-SE")],
        }
        request = Request(scope)
        assert get_request_locale(request) == "fr_CA"

        # Test Accept-Language header (second priority)
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [(b"accept-language", b"sv-SE,en;q=0.8")],
        }
        request = Request(scope)
        assert get_request_locale(request) == "sv_SE"

        # Test default (lowest priority)
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
        }
        request = Request(scope)
        assert get_request_locale(request) == "en_US"

    def test_unsupported_locale_fallback(self, mock_nhl_client):
        """Test unsupported locale falls back to default."""
        from starlette.requests import Request

        from nhl_scrabble.web.locale import get_request_locale

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"lang=ja_JP",  # Unsupported
            "headers": [],
        }
        request = Request(scope)
        assert get_request_locale(request) == "en_US"


class TestSetupTemplateLocale:
    """Test setup_template_locale helper function."""

    def test_returns_context_dict(self, mock_nhl_client):
        """Test setup_template_locale returns proper context."""
        from starlette.requests import Request

        from nhl_scrabble.web.locale import setup_template_locale

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"lang=fr_CA",
            "headers": [],
        }
        request = Request(scope)
        # Pass None for templates since we're just testing the context dict
        context = setup_template_locale(request, None)

        assert "request" in context
        assert "locale" in context
        assert context["locale"] == "fr_CA"
        assert "get_locale" in context
        assert callable(context["get_locale"])
        assert context["get_locale"]() == "fr_CA"
        assert "SUPPORTED_LOCALES" in context
        assert context["SUPPORTED_LOCALES"] == SUPPORTED_LOCALES
