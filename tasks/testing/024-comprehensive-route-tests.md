# Add Comprehensive Web Application Route Tests

**GitHub Issue**: #457 - https://github.com/bdperkin/nhl-scrabble/issues/457

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Add comprehensive test coverage for all web application routes to ensure correct responses, status codes, content types, and security headers. Currently, many routes lack dedicated tests, which risks regressions and makes it difficult to verify correct behavior.

**Routes Requiring Test Coverage:**
- `/` - Home page (HTML)
- `/api/*` - API endpoints (JSON)
- `/conferences` - Conferences page (HTML)
- `/divisions` - Divisions page (HTML)
- `/docs` - FastAPI Swagger documentation (HTML)
- `/favicon.svg` - Favicon (SVG)
- `/health` - Health check endpoint (JSON)
- `/playoffs` - Playoffs page (HTML)
- `/redoc` - ReDoc documentation (HTML)
- `/robots.txt` - Robots file (text)
- `/stats` - Statistics page (HTML)
- `/teams` - Teams page (HTML)

## Current State

### Existing Tests

**Integration Tests** (`tests/integration/`):
- Some web endpoint tests may exist but coverage is incomplete
- No systematic testing of all routes
- Missing tests for security headers
- Missing tests for content type validation

**QA Tests** (`qa/web/tests/`):
- Functional tests for user workflows
- Visual regression tests for page rendering
- Accessibility tests for WCAG compliance
- **Missing**: Route existence and basic HTTP response tests

### Current Gaps

1. **No systematic route testing** - Routes may break without detection
2. **No security header validation** - CSP, X-Frame-Options, etc. not tested
3. **No content-type validation** - HTML vs JSON vs SVG vs text not verified
4. **No status code testing** - 200, 404, 500 responses not systematically checked
5. **API endpoint coverage incomplete** - `/api/analyze`, `/api/cache/*`, etc.

## Proposed Solution

Create two test suites:

### Suite 1: Integration Tests (`tests/integration/test_web_routes.py`)

**Purpose:** Fast unit/integration tests for route existence, responses, and basic behavior

```python
"""Integration tests for web application routes.

Tests verify that all routes exist, return correct status codes, content types,
and security headers.
"""

import pytest
from fastapi.testclient import TestClient

from nhl_scrabble.web.app import app


@pytest.fixture
def client():
    """Create test client for FastAPI app.

    Returns:
        TestClient for making requests to the app
    """
    return TestClient(app)


class TestHTMLRoutes:
    """Tests for HTML page routes."""

    def test_home_page_exists(self, client):
        """Test root route returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text

    def test_teams_page_exists(self, client):
        """Test teams page returns HTML."""
        response = client.get("/teams")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_divisions_page_exists(self, client):
        """Test divisions page returns HTML."""
        response = client.get("/divisions")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_conferences_page_exists(self, client):
        """Test conferences page returns HTML."""
        response = client.get("/conferences")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_playoffs_page_exists(self, client):
        """Test playoffs page returns HTML."""
        response = client.get("/playoffs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_stats_page_exists(self, client):
        """Test stats page returns HTML."""
        response = client.get("/stats")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_all_html_routes_exist(self, client):
        """Test all HTML routes return 200 OK."""
        html_routes = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

        for route in html_routes:
            response = client.get(route)
            assert response.status_code == 200, f"Route {route} returned {response.status_code}"
            assert "text/html" in response.headers["content-type"]


class TestAPIRoutes:
    """Tests for API endpoints."""

    def test_health_endpoint(self, client):
        """Test health check returns JSON."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_api_analyze_get(self, client):
        """Test GET /api/analyze endpoint."""
        response = client.get("/api/analyze")
        # This might return 500 if NHL API is unavailable, but route should exist
        assert response.status_code in [200, 500]

    def test_api_analyze_post(self, client):
        """Test POST /api/analyze endpoint."""
        response = client.post("/api/analyze", json={
            "top_players": 20,
            "top_team_players": 5,
            "use_cache": False
        })
        # This might return 500 if NHL API is unavailable, but route should exist
        assert response.status_code in [200, 500]

    def test_api_cache_stats(self, client):
        """Test cache stats endpoint."""
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert "size" in data
        assert "entries" in data

    def test_api_player_not_found(self, client):
        """Test player endpoint returns 404 for unknown player."""
        response = client.get("/api/players/999999")
        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]


class TestStaticRoutes:
    """Tests for static files and resources."""

    def test_favicon_svg(self, client):
        """Test favicon returns SVG."""
        response = client.get("/favicon.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert "<svg" in response.text

    def test_robots_txt(self, client):
        """Test robots.txt returns text."""
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestDocumentationRoutes:
    """Tests for API documentation routes."""

    def test_docs_route_exists(self, client):
        """Test Swagger UI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_route_exists(self, client):
        """Test ReDoc docs are accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json(self, client):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestSecurityHeaders:
    """Tests for security headers on responses."""

    def test_html_routes_have_security_headers(self, client):
        """Test HTML routes include security headers."""
        response = client.get("/")

        # Check for security headers
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"

        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

        assert "x-xss-protection" in response.headers
        assert response.headers["x-xss-protection"] == "1; mode=block"

        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"

        # CSP should be present on non-docs pages
        assert "content-security-policy" in response.headers

    def test_api_routes_have_security_headers(self, client):
        """Test API routes include security headers."""
        response = client.get("/health")

        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers
        assert "referrer-policy" in response.headers

    def test_docs_routes_skip_csp(self, client):
        """Test docs routes don't have strict CSP (needs external resources)."""
        docs_routes = ["/docs", "/redoc"]

        for route in docs_routes:
            response = client.get(route)
            # Docs routes may have relaxed or no CSP to allow Swagger/ReDoc
            # But should still have other security headers
            assert "x-content-type-options" in response.headers
            assert "x-frame-options" in response.headers


class TestErrorHandling:
    """Tests for error responses."""

    def test_404_on_nonexistent_route(self, client):
        """Test 404 for routes that don't exist."""
        response = client.get("/this-route-does-not-exist")
        assert response.status_code == 404

    def test_404_returns_json(self, client):
        """Test 404 errors return JSON."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        assert "application/json" in response.headers["content-type"]

        data = response.json()
        assert "detail" in data

    def test_method_not_allowed(self, client):
        """Test 405 for unsupported HTTP methods."""
        # Try DELETE on a GET-only route
        response = client.delete("/health")
        assert response.status_code == 405


class TestCORSHeaders:
    """Tests for CORS configuration."""

    def test_cors_headers_on_api_routes(self, client):
        """Test CORS headers are present on API routes."""
        response = client.options("/api/analyze", headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST"
        })

        # CORS should allow localhost
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] in [
                "http://localhost:8000",
                "http://127.0.0.1:8000"
            ]
```

### Suite 2: QA Functional Tests (`qa/web/tests/functional/test_route_navigation.py`)

**Purpose:** Browser-based E2E tests for navigation and user experience

```python
"""Functional tests for route navigation.

Tests verify that users can navigate to all pages via browser and that
pages render correctly.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.functional
def test_home_page_accessible(page: Page, base_url: str) -> None:
    """Test home page is accessible via browser.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    page.goto(base_url)

    # Should see HTML page, not JSON error
    expect(page.locator("html")).to_be_visible()

    # Should not see JSON error
    content = page.content()
    assert '{"detail"' not in content


@pytest.mark.functional
def test_all_page_routes_accessible(page: Page, base_url: str) -> None:
    """Test all page routes are accessible via browser.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    routes = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

    for route in routes:
        page.goto(f"{base_url}{route}")

        # Should render HTML page
        expect(page.locator("html")).to_be_visible()

        # Should not see JSON error
        content = page.content()
        assert '{"detail"' not in content, f"Route {route} returned JSON error"

        # Should have proper page structure
        expect(page.locator("body")).to_be_visible()


@pytest.mark.functional
def test_navigation_between_pages(page: Page, base_url: str) -> None:
    """Test user can navigate between pages.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    page.goto(base_url)

    # Navigate to teams page
    page.goto(f"{base_url}/teams")
    expect(page.locator("html")).to_be_visible()

    # Navigate to divisions page
    page.goto(f"{base_url}/divisions")
    expect(page.locator("html")).to_be_visible()

    # Navigate back to home
    page.goto(base_url)
    expect(page.locator("html")).to_be_visible()


@pytest.mark.functional
def test_favicon_loads(page: Page, base_url: str) -> None:
    """Test favicon is accessible.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    response = page.request.get(f"{base_url}/favicon.svg")
    assert response.ok
    assert "image/svg" in response.headers["content-type"]


@pytest.mark.functional
def test_robots_txt_accessible(page: Page, base_url: str) -> None:
    """Test robots.txt is accessible.

    Args:
        page: Playwright page fixture
        base_url: Base URL of application
    """
    response = page.request.get(f"{base_url}/robots.txt")
    assert response.ok
    assert "text/plain" in response.headers["content-type"]
```

## Implementation Steps

1. **Create integration test file**
   - Create `tests/integration/test_web_routes.py`
   - Add test classes for different route categories
   - Implement tests for all 12 route base paths
   - Add security header validation tests
   - Add error handling tests

2. **Create QA functional test file**
   - Create `qa/web/tests/functional/test_route_navigation.py`
   - Add browser-based navigation tests
   - Verify routes accessible via Playwright
   - Test navigation between pages

3. **Run integration tests locally**
   ```bash
   # Run new route tests
   pytest tests/integration/test_web_routes.py -v

   # Run all integration tests
   pytest tests/integration/ -v
   ```

4. **Run QA functional tests locally**
   ```bash
   # Start web server
   nhl-scrabble serve --host 0.0.0.0 --port 5000

   # Run new navigation tests
   ./scripts/pytest-playwright qa/web/tests/functional/test_route_navigation.py --browser=chromium

   # Run all functional tests
   ./scripts/pytest-playwright qa/web/tests/functional/ --browser=chromium
   ```

5. **Add parameterized tests** (if helpful)
   ```python
   @pytest.mark.parametrize("route,content_type", [
       ("/", "text/html"),
       ("/teams", "text/html"),
       ("/divisions", "text/html"),
       ("/conferences", "text/html"),
       ("/playoffs", "text/html"),
       ("/stats", "text/html"),
       ("/health", "application/json"),
       ("/favicon.svg", "image/svg+xml"),
       ("/robots.txt", "text/plain"),
   ])
   def test_route_returns_correct_content_type(client, route, content_type):
       """Test routes return expected content types."""
       response = client.get(route)
       assert response.status_code == 200
       assert content_type in response.headers["content-type"]
   ```

6. **Update test documentation**
   - Add tests to `tests/README.md` (if exists)
   - Document test coverage for routes
   - Add examples of running route tests

7. **Run full test suite**
   ```bash
   # All unit/integration tests
   pytest tests/

   # All QA tests
   ./scripts/pytest-playwright qa/web/tests/ --browser=chromium

   # Generate coverage report
   pytest tests/integration/test_web_routes.py --cov=src/nhl_scrabble/web --cov-report=html
   ```

8. **Verify CI passes**
   - Ensure GitHub Actions workflows pass
   - Check test coverage doesn't decrease
   - Verify no flaky tests

9. **Commit changes**
   ```bash
   git add tests/integration/test_web_routes.py
   git add qa/web/tests/functional/test_route_navigation.py

   git commit -m "test(web): Add comprehensive route test coverage

   Add integration and functional tests for all web application routes:
   - HTML routes (/, /teams, /divisions, /conferences, /playoffs, /stats)
   - API routes (/health, /api/*)
   - Static routes (/favicon.svg, /robots.txt)
   - Documentation routes (/docs, /redoc, /openapi.json)

   Tests verify:
   - Route existence and correct status codes
   - Content-type headers (HTML, JSON, SVG, text)
   - Security headers (CSP, X-Frame-Options, etc.)
   - Error handling (404, 405)
   - CORS configuration
   - Browser navigation and rendering

   Increases test coverage and prevents route regressions.

   Task: tasks/testing/024-comprehensive-route-tests.md
   Issue: #TBD"
   ```

10. **Push and create PR**
    ```bash
    git push -u origin testing/024-comprehensive-route-tests
    gh pr create
    ```

## Testing Strategy

### Integration Testing (Fast)

**Location:** `tests/integration/test_web_routes.py`

**Purpose:** Fast, isolated tests using TestClient (no browser)

**Coverage:**
- All 12 route base paths
- Status codes (200, 404, 405, 500)
- Content types (HTML, JSON, SVG, text)
- Security headers (CSP, X-Frame-Options, X-XSS-Protection, etc.)
- Error responses
- CORS headers
- API endpoint responses

**Execution:**
```bash
pytest tests/integration/test_web_routes.py -v

# Expected output:
# test_web_routes.py::TestHTMLRoutes::test_home_page_exists PASSED
# test_web_routes.py::TestHTMLRoutes::test_teams_page_exists PASSED
# test_web_routes.py::TestHTMLRoutes::test_all_html_routes_exist PASSED
# test_web_routes.py::TestAPIRoutes::test_health_endpoint PASSED
# test_web_routes.py::TestStaticRoutes::test_favicon_svg PASSED
# test_web_routes.py::TestSecurityHeaders::test_html_routes_have_security_headers PASSED
# ... etc.
```

### QA Functional Testing (Browser-based)

**Location:** `qa/web/tests/functional/test_route_navigation.py`

**Purpose:** Real browser tests for navigation and rendering

**Coverage:**
- Browser accessibility of all pages
- Navigation between pages
- HTML rendering (no JSON errors)
- Favicon and robots.txt loading
- Page structure integrity

**Execution:**
```bash
# Start server
nhl-scrabble serve --host 0.0.0.0 --port 5000

# Run tests
./scripts/pytest-playwright qa/web/tests/functional/test_route_navigation.py --browser=chromium
./scripts/pytest-playwright qa/web/tests/functional/test_route_navigation.py --browser=firefox
./scripts/pytest-playwright qa/web/tests/functional/test_route_navigation.py --browser=webkit
```

### Manual Testing

**Verify routes return correct responses:**
```bash
# HTML routes
curl -I http://localhost:5000/
curl -I http://localhost:5000/teams
curl -I http://localhost:5000/divisions
curl -I http://localhost:5000/conferences
curl -I http://localhost:5000/playoffs
curl -I http://localhost:5000/stats

# API routes
curl http://localhost:5000/health
curl http://localhost:5000/api/cache/stats

# Static routes
curl -I http://localhost:5000/favicon.svg
curl -I http://localhost:5000/robots.txt

# Documentation routes
curl -I http://localhost:5000/docs
curl -I http://localhost:5000/redoc
curl -I http://localhost:5000/openapi.json
```

### CI Testing

- Integration tests run in GitHub Actions test workflow
- QA tests run in QA Automation workflow
- Coverage reports generated and uploaded to Codecov

## Acceptance Criteria

- [ ] Integration test file created: `tests/integration/test_web_routes.py`
- [ ] QA functional test file created: `qa/web/tests/functional/test_route_navigation.py`
- [ ] All 12 route base paths have test coverage
- [ ] HTML routes tested for correct content-type
- [ ] API routes tested for correct responses
- [ ] Static routes tested (favicon.svg, robots.txt)
- [ ] Documentation routes tested (/docs, /redoc, /openapi.json)
- [ ] Security headers validated on all routes
- [ ] Error handling tested (404, 405)
- [ ] CORS configuration tested
- [ ] Browser navigation tests pass on all three browsers
- [ ] All tests pass locally
- [ ] CI workflows pass
- [ ] Test coverage increases (not decreases)
- [ ] No flaky tests introduced

## Related Files

- `tests/integration/test_web_routes.py` - New integration test file
- `qa/web/tests/functional/test_route_navigation.py` - New QA functional test file
- `src/nhl_scrabble/web/app.py` - FastAPI application being tested
- `.github/workflows/test.yml` - CI workflow for integration tests
- `.github/workflows/qa-automation.yml` - CI workflow for QA tests
- `tests/README.md` - Test documentation (update)

## Dependencies

**Prerequisite Tasks:**
- Task #002 (Add Missing Web Application Routes) - Some routes must exist before testing

**None blocking:** Tests can be written before routes exist (tests will fail, which is expected)

## Additional Notes

### Test Organization

**Integration Tests** (`tests/integration/`):
- Fast execution (no browser)
- Use FastAPI TestClient
- Test HTTP responses, headers, status codes
- Run on every commit
- Should be comprehensive and cover all routes

**QA Functional Tests** (`qa/web/tests/functional/`):
- Browser-based (Playwright)
- Test user experience and navigation
- Verify rendering and page structure
- Run on PR and nightly
- Focus on critical user paths

### Test Coverage Goals

**Routes to Test:**
1. ✅ `/` - Home page
2. ✅ `/teams` - Teams standings
3. ✅ `/divisions` - Division standings
4. ✅ `/conferences` - Conference standings
5. ✅ `/playoffs` - Playoff bracket
6. ✅ `/stats` - Statistics page
7. ✅ `/health` - Health check
8. ✅ `/api/analyze` - Analysis API
9. ✅ `/api/cache/stats` - Cache stats
10. ✅ `/favicon.svg` - Favicon
11. ✅ `/robots.txt` - Robots file
12. ✅ `/docs` - Swagger UI
13. ✅ `/redoc` - ReDoc docs
14. ✅ `/openapi.json` - OpenAPI schema

### Security Testing

**Headers to Validate:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: ...` (on non-docs routes)

### Performance Considerations

- Integration tests are fast (<1s per test)
- QA tests slower (~5-10s per test due to browser)
- Parameterized tests reduce code duplication
- Group related tests in classes for clarity

### Maintenance

**When adding new routes:**
1. Add integration test to `test_web_routes.py`
2. Add functional test to `test_route_navigation.py` (if user-facing)
3. Update parameterized test lists
4. Verify security headers on new routes

**When changing existing routes:**
1. Update tests to match new behavior
2. Ensure backward compatibility tested
3. Update assertions for new content

### Future Enhancements

Once basic route tests exist, consider:
- Response time assertions (performance)
- Response body validation (JSON schema)
- Authentication/authorization tests (if added)
- Rate limiting tests (if implemented)
- Caching header tests
- Compression header tests

### Example Test Output

```
tests/integration/test_web_routes.py::TestHTMLRoutes::test_home_page_exists PASSED
tests/integration/test_web_routes.py::TestHTMLRoutes::test_teams_page_exists PASSED
tests/integration/test_web_routes.py::TestHTMLRoutes::test_divisions_page_exists PASSED
tests/integration/test_web_routes.py::TestHTMLRoutes::test_conferences_page_exists PASSED
tests/integration/test_web_routes.py::TestHTMLRoutes::test_playoffs_page_exists PASSED
tests/integration/test_web_routes.py::TestHTMLRoutes::test_stats_page_exists PASSED
tests/integration/test_web_routes.py::TestHTMLRoutes::test_all_html_routes_exist PASSED
tests/integration/test_web_routes.py::TestAPIRoutes::test_health_endpoint PASSED
tests/integration/test_web_routes.py::TestAPIRoutes::test_api_cache_stats PASSED
tests/integration/test_web_routes.py::TestStaticRoutes::test_favicon_svg PASSED
tests/integration/test_web_routes.py::TestStaticRoutes::test_robots_txt PASSED
tests/integration/test_web_routes.py::TestDocumentationRoutes::test_docs_route_exists PASSED
tests/integration/test_web_routes.py::TestDocumentationRoutes::test_redoc_route_exists PASSED
tests/integration/test_web_routes.py::TestDocumentationRoutes::test_openapi_json PASSED
tests/integration/test_web_routes.py::TestSecurityHeaders::test_html_routes_have_security_headers PASSED
tests/integration/test_web_routes.py::TestSecurityHeaders::test_api_routes_have_security_headers PASSED
tests/integration/test_web_routes.py::TestErrorHandling::test_404_on_nonexistent_route PASSED
tests/integration/test_web_routes.py::TestErrorHandling::test_method_not_allowed PASSED

========================== 18 passed in 0.85s ==========================
```

## Implementation Notes

*To be filled during implementation:*
- Actual routes that existed vs needed to be added
- Any routes that behaved differently than expected
- Security headers actually present
- Test execution time
- Coverage percentage increase
- Challenges encountered
- Actual effort vs estimated (4-6h)
- Any flaky tests and resolutions
