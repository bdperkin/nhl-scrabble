# Expand Test Coverage of Web Modules

**GitHub Issue**: #592 - https://github.com/bdperkin/nhl-scrabble/issues/592

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

20-28 hours

## Description

**Web modules have zero test coverage despite having extensive test files**, leaving the entire web application backend untested. Current coverage is **0.00%**, with **~841 untested statements**:

- **web/app.py**: 0.00% (783 statements untested - main FastAPI application)
- **web/utils/auto_link.py**: 0.00% (53 statements untested)
- **web/__init__.py**: 0.00% (3 statements untested)
- **web/utils/__init__.py**: 0.00% (2 statements untested)

**Total missing coverage**: ~841 statements across 4 files

**Similar to Tasks 036 & 038**: Test files **already exist** (~2,032 lines of tests) but have **0% coverage**, indicating tests may be integration-only (HTTP-level) without directly importing/executing the Python modules, or coverage collection isn't configured properly for the web module.

This represents critical gaps in quality assurance for:
- FastAPI application initialization and configuration
- API endpoints (standings, teams, players, conferences, divisions)
- Template rendering and Jinja2 integration
- Security middleware (CSP, XSS protection, frame options)
- I18n/localization in web interface
- Error handling and HTTP status codes
- Static file serving
- CORS configuration
- NHL API integration in web context
- Playoff bracket generation for web
- Player/team detail pages
- Search functionality
- Data caching and performance
- Auto-linking utility for text

## Current State

### Existing Tests (But 0% Coverage):

**Total: ~2,032 lines of web tests across 7 files**

**tests/integration/test_web.py** - EXISTS (~500 lines) but 0% coverage
- Tests API endpoints via TestClient
- May test HTTP responses without importing modules directly
- Integration-level tests, not unit tests

**tests/integration/test_web_routes.py** - EXISTS (~400 lines) but 0% coverage
- Tests route functionality via HTTP
- Similar integration-only pattern

**tests/integration/test_web_api.py** - EXISTS (~350 lines) but 0% coverage
- Tests API endpoints
- Likely HTTP-level testing

**tests/integration/test_web_i18n.py** - EXISTS (~300 lines) but 0% coverage
- Tests internationalization in web context
- HTTP-level i18n testing

**tests/integration/test_web_infrastructure.py** - EXISTS (~250 lines) but 0% coverage
- Tests infrastructure components
- May need unit test complement

**tests/integration/test_web_interactivity.py** - EXISTS (~150 lines) but 0% coverage
- Tests interactive features
- Integration-only pattern

**tests/integration/test_api_server.py** - EXISTS (~82 lines) but 0% coverage
- Tests API server startup/shutdown
- May need process-level testing

### Coverage Breakdown:

**web/app.py (783 statements, 0% coverage):**
```
Lines missing: 7-2431 (entire file except imports)
Features untested:
- FastAPI app initialization and configuration
- SecurityHeadersMiddleware implementation
- Locale detection and i18n setup
- All API endpoints:
  * GET / (homepage)
  * GET /standings (league standings)
  * GET /teams (team list)
  * GET /teams/{team_abbrev} (team detail)
  * GET /players (player list)
  * GET /players/{player_id} (player detail)
  * GET /conferences/{conference} (conference standings)
  * GET /divisions/{division} (division standings)
  * GET /playoffs (playoff bracket)
  * GET /search (search functionality)
  * GET /api/standings (API JSON endpoint)
  * GET /api/teams/{team_abbrev}/roster (roster API)
  * GET /health (health check)
- Template rendering with Jinja2
- Error handlers (404, 500)
- Static file configuration
- CORS middleware setup
- Cache control headers
- Request/response lifecycle
- NHL API error handling in web context
- Data transformation for templates
- Filter functions for Jinja2
- Team/player statistics calculation
- Playoff bracket generation
- Search query processing
- Locale switching logic
```

**web/utils/auto_link.py (53 statements, 0% coverage):**
```
Lines missing: 3-181 (entire file)
Features untested:
- Auto-linking player names to detail pages
- Auto-linking team abbreviations to team pages
- URL pattern detection and replacement
- HTML escaping in links
- Edge case handling (partial matches, overlapping)
```

## Proposed Solution

### Phase 0: Investigation (2-3 hours)
**Critical First Step** - Understand why existing tests have 0% coverage:
1. Review all 7 test_web*.py files
2. Identify test patterns (HTTP-only vs module imports)
3. Check coverage configuration for web module
4. Determine if tests execute source code or bypass it
5. Check if FastAPI TestClient affects coverage collection
6. Document findings and root cause

### 1. Unit Tests for Web Application Core

**web/app.py** (783 statements):

```python
# tests/unit/test_web_app.py (NEW)
"""Unit tests for FastAPI web application core functionality."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock

from nhl_scrabble.web.app import app, SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    def test_middleware_adds_security_headers(self, client):
        """Test that security headers are added to responses."""
        response = client.get("/")

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_middleware_applies_csp_to_regular_pages(self, client):
        """Test CSP header on regular pages."""
        response = client.get("/")

        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    def test_middleware_skips_strict_csp_for_api_docs(self, client):
        """Test CSP is relaxed for API documentation."""
        # Swagger UI needs external resources
        response = client.get("/docs")

        # CSP should still exist but be less strict
        # (actual behavior depends on implementation)


class TestFastAPIConfiguration:
    """Test FastAPI app configuration."""

    def test_app_initialization(self):
        """Test FastAPI app is properly initialized."""
        assert app.title == "NHL Scrabble"
        assert app.description is not None
        assert app.version is not None

    def test_cors_middleware_configured(self):
        """Test CORS middleware is set up."""
        # Check middleware stack includes CORS
        middleware_types = [type(m.cls) for m in app.user_middleware]
        # Verify CORS is present

    def test_static_files_mounted(self):
        """Test static files are properly mounted."""
        # Verify /static route is configured
        routes = [r.path for r in app.routes]
        assert any("/static" in r for r in routes)

    def test_templates_directory_configured(self):
        """Test templates directory exists and is configured."""
        from nhl_scrabble.web.app import TEMPLATES_DIR
        assert TEMPLATES_DIR.exists()
        assert (TEMPLATES_DIR / "base.html").exists()


class TestLocaleDetection:
    """Test locale detection and i18n setup."""

    def test_locale_from_accept_language_header(self, client):
        """Test locale detection from Accept-Language header."""
        response = client.get("/", headers={"Accept-Language": "fr-CA"})
        # Verify French Canadian locale is used in response

    def test_locale_from_query_parameter(self, client):
        """Test locale override via ?lang= parameter."""
        response = client.get("/?lang=sv_SE")
        # Verify Swedish locale is used

    def test_locale_fallback_to_default(self, client):
        """Test fallback to default locale for unsupported languages."""
        response = client.get("/", headers={"Accept-Language": "xx-XX"})
        # Should fall back to en_US

    def test_supported_locales_list(self):
        """Test all supported locales are configured."""
        from nhl_scrabble.web.app import SUPPORTED_LOCALES
        assert "en_US" in SUPPORTED_LOCALES
        assert "fr_CA" in SUPPORTED_LOCALES
        assert "sv_SE" in SUPPORTED_LOCALES


class TestAPIEndpoints:
    """Test API endpoint implementations."""

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_homepage_endpoint(self, mock_client, client):
        """Test GET / returns homepage."""
        mock_client.return_value.__enter__.return_value.fetch_standings.return_value = []

        response = client.get("/")
        assert response.status_code == 200
        assert "NHL Scrabble" in response.text

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_standings_endpoint(self, mock_client, client):
        """Test GET /standings returns standings page."""
        # Mock standings data
        mock_standings = [...]
        mock_client.return_value.__enter__.return_value.fetch_standings.return_value = mock_standings

        response = client.get("/standings")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_team_detail_endpoint(self, mock_client, client):
        """Test GET /teams/{team_abbrev} returns team page."""
        # Mock team and roster data
        response = client.get("/teams/WSH")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_team_not_found(self, mock_client, client):
        """Test 404 for non-existent team."""
        mock_client.return_value.__enter__.return_value.fetch_roster.side_effect = Exception("Not found")

        response = client.get("/teams/XXX")
        assert response.status_code == 404

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_players_list_endpoint(self, mock_client, client):
        """Test GET /players returns player list."""
        response = client.get("/players")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_player_detail_endpoint(self, mock_client, client):
        """Test GET /players/{player_id} returns player page."""
        response = client.get("/players/8478402")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_conference_standings_endpoint(self, mock_client, client):
        """Test GET /conferences/{conference} returns standings."""
        response = client.get("/conferences/Eastern")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_division_standings_endpoint(self, mock_client, client):
        """Test GET /divisions/{division} returns standings."""
        response = client.get("/divisions/Metropolitan")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_playoffs_bracket_endpoint(self, mock_client, client):
        """Test GET /playoffs returns playoff bracket."""
        response = client.get("/playoffs")
        assert response.status_code == 200

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_search_endpoint(self, mock_client, client):
        """Test GET /search with query parameter."""
        response = client.get("/search?q=Ovechkin")
        assert response.status_code == 200
        # Verify search results in response

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_search_empty_query(self, mock_client, client):
        """Test search with empty query."""
        response = client.get("/search?q=")
        # Should handle gracefully


class TestAPIJsonEndpoints:
    """Test JSON API endpoints."""

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_api_standings_json(self, mock_client, client):
        """Test GET /api/standings returns JSON."""
        mock_client.return_value.__enter__.return_value.fetch_standings.return_value = []

        response = client.get("/api/standings")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, list)

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_api_roster_json(self, mock_client, client):
        """Test GET /api/teams/{team}/roster returns JSON."""
        mock_client.return_value.__enter__.return_value.fetch_roster.return_value = []

        response = client.get("/api/teams/WSH/roster")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"


class TestErrorHandlers:
    """Test error handling."""

    def test_404_error_handler(self, client):
        """Test custom 404 error page."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        # Should return custom 404 page

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_500_error_handler(self, mock_client, client):
        """Test 500 error handling."""
        # Mock an internal server error
        mock_client.return_value.__enter__.return_value.fetch_standings.side_effect = Exception("Internal error")

        response = client.get("/standings")
        # Should handle gracefully with 500 page


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_endpoint(self, client):
        """Test GET /health returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestTemplateRendering:
    """Test Jinja2 template rendering."""

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_template_context_data(self, mock_client, client):
        """Test templates receive correct context data."""
        response = client.get("/")
        # Verify template variables are present

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_template_filters_registered(self, mock_client, client):
        """Test Jinja2 filters are registered."""
        from nhl_scrabble.web.app import app
        # Check template environment has custom filters


class TestNHLAPIIntegration:
    """Test NHL API integration in web context."""

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_api_error_handling(self, mock_client, client):
        """Test handling of NHL API errors."""
        from nhl_scrabble.api import NHLApiError
        mock_client.return_value.__enter__.return_value.fetch_standings.side_effect = NHLApiError("API down")

        response = client.get("/standings")
        # Should show error page, not crash

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_api_timeout_handling(self, mock_client, client):
        """Test handling of API timeouts."""
        import asyncio
        mock_client.return_value.__enter__.return_value.fetch_standings.side_effect = asyncio.TimeoutError()

        response = client.get("/standings")
        # Should handle timeout gracefully


class TestCaching:
    """Test data caching in web application."""

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_cache_control_headers(self, mock_client, client):
        """Test Cache-Control headers are set."""
        response = client.get("/standings")
        # Check for appropriate cache headers

    @patch("nhl_scrabble.web.app.NHLApiClient")
    def test_data_caching_reduces_api_calls(self, mock_client, client):
        """Test repeated requests use cached data."""
        mock_client.return_value.__enter__.return_value.fetch_standings.return_value = []

        # First request
        client.get("/standings")
        # Second request
        client.get("/standings")

        # Should only call API once if caching works


class TestDataTransformation:
    """Test data transformation for templates."""

    def test_team_score_to_template_dict(self):
        """Test TeamScore converts to template-friendly dict."""
        # Test data transformation logic

    def test_player_score_to_template_dict(self):
        """Test PlayerScore converts to template-friendly dict."""
        # Test data transformation logic

    def test_playoff_bracket_structure(self):
        """Test playoff bracket data structure for template."""
        # Test bracket generation
```

### 2. Unit Tests for Auto-Link Utility

**web/utils/auto_link.py** (53 statements):

```python
# tests/unit/test_web_utils_auto_link.py (NEW)
"""Unit tests for auto-linking utility."""

import pytest
from nhl_scrabble.web.utils.auto_link import auto_link


class TestAutoLinkPlayerNames:
    """Test auto-linking player names."""

    def test_link_single_player_name(self):
        """Test linking a single player name."""
        text = "Connor McDavid is great"
        result = auto_link(text)
        assert '<a href="/players/' in result
        assert 'Connor McDavid</a>' in result

    def test_link_multiple_player_names(self):
        """Test linking multiple player names."""
        text = "Connor McDavid and Alex Ovechkin"
        result = auto_link(text)
        assert result.count('<a href="/players/') == 2

    def test_partial_name_no_link(self):
        """Test partial matches don't create links."""
        text = "McDav"  # Partial name
        result = auto_link(text)
        assert '<a href=' not in result

    def test_html_escaping_in_names(self):
        """Test HTML special characters are escaped."""
        text = "Player<script>alert('xss')</script>"
        result = auto_link(text)
        assert '<script>' not in result
        assert '&lt;script&gt;' in result


class TestAutoLinkTeamAbbreviations:
    """Test auto-linking team abbreviations."""

    def test_link_team_abbreviation(self):
        """Test linking team abbreviation."""
        text = "WSH is winning"
        result = auto_link(text)
        assert '<a href="/teams/WSH"' in result

    def test_link_multiple_teams(self):
        """Test linking multiple teams."""
        text = "WSH vs EDM tonight"
        result = auto_link(text)
        assert result.count('<a href="/teams/') == 2

    def test_no_link_for_invalid_abbreviation(self):
        """Test invalid abbreviations don't link."""
        text = "XXX YYY ZZZ"
        result = auto_link(text)
        assert '<a href="/teams/' not in result


class TestAutoLinkEdgeCases:
    """Test edge cases in auto-linking."""

    def test_empty_text(self):
        """Test empty text doesn't crash."""
        result = auto_link("")
        assert result == ""

    def test_none_input(self):
        """Test None input handling."""
        result = auto_link(None)
        assert result == "" or result is None

    def test_overlapping_matches(self):
        """Test overlapping player/team mentions."""
        # E.g., team abbreviation within player name
        text = "CAR player Carolina Smith"
        result = auto_link(text)
        # Should handle without double-linking

    def test_already_linked_text(self):
        """Test text with existing HTML links."""
        text = '<a href="/other">Link</a> Connor McDavid'
        result = auto_link(text)
        # Should not break existing links

    def test_special_characters(self):
        """Test text with special characters."""
        text = "Connor McDavid's goal!"
        result = auto_link(text)
        assert '<a href="/players/' in result
```

### 3. Integration Tests Enhancement

Enhance existing integration tests to ensure coverage:

```python
# tests/integration/test_web.py (ENHANCE)
# Already exists with ~500 lines
# Add imports to ensure modules are loaded for coverage

from nhl_scrabble.web import app  # Direct import
from nhl_scrabble.web.app import SecurityHeadersMiddleware  # Import classes
from nhl_scrabble.web.utils.auto_link import auto_link  # Import functions

# Existing tests should then count toward coverage
```

### 4. Test Organization

```
tests/
├── unit/
│   ├── test_web_app.py                    ✓ NEW (783 statements)
│   └── test_web_utils_auto_link.py        ✓ NEW (53 statements)
└── integration/
    ├── test_web.py                        ✓ ENHANCE (import modules)
    ├── test_web_routes.py                 ✓ ENHANCE (import modules)
    ├── test_web_api.py                    ✓ ENHANCE (import modules)
    ├── test_web_i18n.py                   ✓ ENHANCE (import modules)
    ├── test_web_infrastructure.py         ✓ ENHANCE (import modules)
    ├── test_web_interactivity.py          ✓ ENHANCE (import modules)
    └── test_api_server.py                 ✓ ENHANCE (import modules)
```

## Implementation Steps

1. **Phase 0: Investigation** (2-3 hours)
   - Review all 7 existing test files (~2,032 lines)
   - Understand why coverage is 0% despite extensive tests
   - Check FastAPI TestClient coverage collection
   - Check pytest-cov configuration for web module
   - Document findings and root cause

2. **Phase 1: Core Web Application** (8-10 hours)
   - Test FastAPI initialization and configuration
   - Test SecurityHeadersMiddleware
   - Test locale detection and i18n setup
   - Test CORS and static file configuration
   - Test all API endpoints (unit level with mocks)

3. **Phase 2: Template and Error Handling** (4-6 hours)
   - Test Jinja2 template rendering
   - Test error handlers (404, 500)
   - Test health check endpoint
   - Test data transformation for templates

4. **Phase 3: Auto-Link Utility** (2-3 hours)
   - Test player name linking
   - Test team abbreviation linking
   - Test edge cases and HTML escaping

5. **Phase 4: NHL API Integration** (2-3 hours)
   - Test API error handling in web context
   - Test timeout handling
   - Test caching behavior

6. **Phase 5: Integration Test Enhancement** (2-3 hours)
   - Add module imports to existing tests
   - Verify coverage collection works
   - Run full test suite and check coverage

7. **Phase 6: Documentation** (1 hour)
   - Update test documentation
   - Document investigation findings
   - CI configuration updates

## Testing Strategy

### Unit Tests
- Test web components in isolation
- Mock NHLApiClient with @patch
- Test middleware and security headers
- Test endpoint logic without HTTP
- Test utility functions directly

### Integration Tests (Existing + Enhanced)
- Test full HTTP request/response cycle
- Test with TestClient
- Verify end-to-end workflows
- Add imports to ensure coverage

### Special Considerations
- **FastAPI TestClient**: May affect coverage collection - investigate
- **Async code**: Ensure async handlers are tested
- **Template rendering**: Mock or use real templates?
- **Static files**: Test configuration, not file serving itself

## Acceptance Criteria

- [ ] Investigation complete - understand why tests had 0% coverage
- [ ] **web/app.py** coverage: 0% → 95% (783 statements)
- [ ] **web/utils/auto_link.py** coverage: 0% → 95% (53 statements)
- [ ] **web/__init__.py** coverage: 0% → 100% (3 statements)
- [ ] **web/utils/__init__.py** coverage: 0% → 100% (2 statements)
- [ ] All API endpoints tested (unit and integration)
- [ ] Security middleware tested
- [ ] Error handling tested (404, 500, API errors)
- [ ] Template rendering tested
- [ ] I18n/locale detection tested
- [ ] Auto-link utility tested (all edge cases)
- [ ] All tests pass on all platforms
- [ ] All tests pass with Python 3.12-3.15-dev
- [ ] No test flakiness
- [ ] diff-cover shows 100% coverage
- [ ] Documentation updated with investigation findings

## Related Files

### Source Files:
- `src/nhl_scrabble/web/app.py` - FastAPI application (783 statements)
- `src/nhl_scrabble/web/utils/auto_link.py` - Auto-linking utility (53 statements)
- `src/nhl_scrabble/web/__init__.py` - Module exports (3 statements)
- `src/nhl_scrabble/web/utils/__init__.py` - Utils exports (2 statements)

### Test Files:
- `tests/unit/test_web_app.py` - NEW unit tests (783 statements)
- `tests/unit/test_web_utils_auto_link.py` - NEW utility tests (53 statements)
- `tests/integration/test_web.py` - ENHANCE existing (~500 lines)
- `tests/integration/test_web_routes.py` - ENHANCE existing (~400 lines)
- `tests/integration/test_web_api.py` - ENHANCE existing (~350 lines)
- `tests/integration/test_web_i18n.py` - ENHANCE existing (~300 lines)
- `tests/integration/test_web_infrastructure.py` - ENHANCE existing (~250 lines)
- `tests/integration/test_web_interactivity.py` - ENHANCE existing (~150 lines)
- `tests/integration/test_api_server.py` - ENHANCE existing (~82 lines)
- `tests/conftest.py` - Add web testing fixtures

## Dependencies

- **Independent**: Can be implemented immediately
- **Complements Tasks 033-038**: Part of comprehensive test coverage initiative
- **Investigation Required**: Similar to Tasks 036 & 038 (tests exist but 0% coverage)
- **May affect**: QA automation workflow (visual/functional tests use web server)

## Additional Notes

### Why This Task

1. **User-Facing**: Web interface is primary UI for many users
2. **Large Surface Area**: 783 statements in app.py alone
3. **0% Coverage Risk**: Entire web backend is untested at module level
4. **Tests Exist**: ~2,032 lines of tests, but 0% coverage - needs investigation
5. **Security Critical**: Web endpoints are attack surface

### Investigation Hypotheses

**Why 0% coverage despite extensive tests?**

1. **Integration-only testing**: Tests use FastAPI TestClient which tests HTTP layer, not Python module imports
2. **Coverage scope**: pytest-cov may not be configured to include web module
3. **Import patterns**: Tests may not directly import web.app module
4. **Async code**: Coverage collection may fail on async endpoints
5. **Test execution**: Tests may be skipped or not running

### Testing Patterns

```python
# Pattern 1: Unit test with mocks (ADDS COVERAGE)
@patch("nhl_scrabble.web.app.NHLApiClient")
def test_endpoint_logic(mock_client):
    from nhl_scrabble.web.app import app  # Direct import
    # Test logic directly

# Pattern 2: Integration test (MAY NOT ADD COVERAGE)
def test_endpoint_http(client):
    response = client.get("/")  # Tests via HTTP
    # Doesn't import module directly
```

### Platform Compatibility

All tests must pass on:
- Linux (primary)
- macOS (different async behavior?)
- Windows (path handling in static files)

## Implementation Notes

*To be filled during implementation:*
- Investigation findings (root cause of 0% coverage)
- FastAPI TestClient coverage behavior
- Coverage configuration changes needed
- Testing patterns that work
- Actual effort vs estimated
- Coverage improvements achieved

---

## Summary

This task completes the **7-task comprehensive test coverage initiative** covering the entire NHL Scrabble application:

**Tasks 033-039 Combined**:
- ~3,746 untested statements
- 126-172 hours total effort
- Coverage target: 90.21% → 97%+
- Complete application coverage (all modules)

**Task 039 specifically addresses**:
- Web/FastAPI application backend (~841 statements)
- Investigation of unusual 0% coverage despite extensive tests
- Unit and integration test coverage for web interface
