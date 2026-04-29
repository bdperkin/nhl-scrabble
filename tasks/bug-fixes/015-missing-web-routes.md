# Add Missing Web Application Routes

**GitHub Issue**: #456 - https://github.com/bdperkin/nhl-scrabble/issues/456

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

2-3 hours

## Description

The web application is missing routes for multiple pages that are referenced by the visual regression tests and likely expected by users. When navigating to these paths, users receive JSON `{"detail": "Not Found"}` responses instead of functional web pages.

**Affected Pages:**
- `/teams` - Team standings page
- `/divisions` - Division standings page
- `/conferences` - Conference standings page
- `/playoffs` - Playoff bracket page
- `/stats` - Statistics page

This breaks 5 core web pages and causes visual regression test failures because the tests expect these routes to exist and render HTML pages.

## Current State

### FastAPI Application Routes

**Existing Routes** (`src/nhl_scrabble/web/app.py`):
```python
@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """Serve the main web interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )

# Other routes:
# /health - Health check
# /favicon.svg - Favicon
# /robots.txt - Robots file
# /api/analyze - Analysis API
# /api/players/{player_id} - Player API
# /api/teams/{team_abbrev} - Team API
# /api/cache/* - Cache management
```

**Missing Routes:**
- `/teams` → 404 Not Found
- `/divisions` → 404 Not Found
- `/conferences` → 404 Not Found
- `/playoffs` → 404 Not Found
- `/stats` → 404 Not Found

### Page Object Models

Tests expect these routes to exist (`qa/web/pages/*.py`):

```python
# qa/web/pages/teams_page.py
class TeamsPage(BasePage):
    def __init__(self, page: Page, base_url: str = "http://localhost:5000") -> None:
        super().__init__(page, base_url)
        self.url = "/teams"  # ← Expects this route to exist

# qa/web/pages/divisions_page.py
class DivisionsPage(BasePage):
    self.url = "/divisions"  # ← 404

# qa/web/pages/conferences_page.py
class ConferencesPage(BasePage):
    self.url = "/conferences"  # ← 404

# qa/web/pages/playoffs_page.py
class PlayoffsPage(BasePage):
    self.url = "/playoffs"  # ← 404

# qa/web/pages/stats_page.py
class StatsPage(BasePage):
    self.url = "/stats"  # ← 404
```

### Current Error Response

When navigating to missing routes:
```bash
$ curl http://localhost:5000/teams
{"detail":"Not Found"}
```

Visual regression tests receive this JSON instead of HTML, causing snapshot comparison failures.

## Proposed Solution

Add route handlers for each missing page to `src/nhl_scrabble/web/app.py`.

### Option 1: Single Template with Route Parameter (Recommended)

Create separate routes that all render the same `index.html` template but with a route context variable:

```python
@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request) -> HTMLResponse:
    """Serve the teams standings page.

    Args:
        request: FastAPI request object

    Returns:
        Rendered index.html template with teams view

    Raises:
        HTTPException: If templates not configured
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view": "teams"},
    )


@app.get("/divisions", response_class=HTMLResponse)
async def divisions_page(request: Request) -> HTMLResponse:
    """Serve the divisions standings page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view": "divisions"},
    )


@app.get("/conferences", response_class=HTMLResponse)
async def conferences_page(request: Request) -> HTMLResponse:
    """Serve the conferences standings page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view": "conferences"},
    )


@app.get("/playoffs", response_class=HTMLResponse)
async def playoffs_page(request: Request) -> HTMLResponse:
    """Serve the playoff bracket page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view": "playoffs"},
    )


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request) -> HTMLResponse:
    """Serve the statistics page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view": "stats"},
    )
```

### Option 2: Separate Templates Per Page

Create individual templates for each page:

```python
@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request) -> HTMLResponse:
    """Serve the teams standings page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="teams.html",
    )

# Similar for divisions.html, conferences.html, playoffs.html, stats.html
```

**Recommendation:** Use Option 1 (single template) because:
- The current design appears to be a single-page application
- JavaScript/HTMX likely handles view switching
- Less template duplication
- Easier maintenance

### Template Updates (if using Option 1)

Update `src/nhl_scrabble/web/templates/index.html` to recognize the view context:

```html
<!-- Optional: Set active nav based on view -->
{% set current_view = view|default("home") %}

<nav>
    <a href="/" {% if current_view == "home" %}class="active"{% endif %}>Home</a>
    <a href="/teams" {% if current_view == "teams" %}class="active"{% endif %}>Teams</a>
    <a href="/divisions" {% if current_view == "divisions" %}class="active"{% endif %}>Divisions</a>
    <a href="/conferences" {% if current_view == "conferences" %}class="active"{% endif %}>Conferences</a>
    <a href="/playoffs" {% if current_view == "playoffs" %}class="active"{% endif %}>Playoffs</a>
    <a href="/stats" {% if current_view == "stats" %}class="active"{% endif %}>Stats</a>
</nav>

<!-- JavaScript can use view to show appropriate section -->
<script>
    const currentView = "{{ current_view }}";
    // Show/hide sections based on currentView
</script>
```

## Implementation Steps

1. **Add route handlers to FastAPI app**
   - Open `src/nhl_scrabble/web/app.py`
   - Add 5 new route handlers after the `root()` function
   - Follow the pattern of existing route (template check, proper responses)
   - Add docstrings with descriptions

2. **Test routes locally**
   ```bash
   # Start web server
   nhl-scrabble serve --host 0.0.0.0 --port 5000

   # Test each route
   curl -I http://localhost:5000/teams
   curl -I http://localhost:5000/divisions
   curl -I http://localhost:5000/conferences
   curl -I http://localhost:5000/playoffs
   curl -I http://localhost:5000/stats

   # Should all return 200 OK with text/html content-type
   ```

3. **Verify in browser**
   - Navigate to http://localhost:5000/teams
   - Navigate to http://localhost:5000/divisions
   - Navigate to http://localhost:5000/conferences
   - Navigate to http://localhost:5000/playoffs
   - Navigate to http://localhost:5000/stats
   - Verify all render HTML pages (not JSON errors)

4. **Run visual regression tests**
   ```bash
   # Test with all browsers
   ./scripts/pytest-playwright qa/web/tests/visual/ --browser=chromium
   ./scripts/pytest-playwright qa/web/tests/visual/ --browser=firefox
   ./scripts/pytest-playwright qa/web/tests/visual/ --browser=webkit

   # Verify visual tests now pass
   ```

5. **Run functional tests**
   ```bash
   ./scripts/pytest-playwright qa/web/tests/functional/ --browser=chromium
   ```

6. **Update templates (if needed)**
   - If Option 1: Update `index.html` to accept view context
   - If Option 2: Create separate templates for each page
   - Ensure navigation links point to correct routes

7. **Add unit tests for routes**
   ```python
   # tests/integration/test_web_routes.py

   import pytest
   from fastapi.testclient import TestClient
   from nhl_scrabble.web.app import app


   @pytest.fixture
   def client():
       """Create test client."""
       return TestClient(app)


   def test_teams_route_exists(client):
       """Test /teams route returns HTML."""
       response = client.get("/teams")
       assert response.status_code == 200
       assert "text/html" in response.headers["content-type"]


   def test_divisions_route_exists(client):
       """Test /divisions route returns HTML."""
       response = client.get("/divisions")
       assert response.status_code == 200
       assert "text/html" in response.headers["content-type"]


   # Similar for conferences, playoffs, stats
   ```

8. **Commit changes**
   ```bash
   git add src/nhl_scrabble/web/app.py
   git add src/nhl_scrabble/web/templates/  # If templates updated
   git add tests/integration/test_web_routes.py  # If tests added

   git commit -m "feat(web): Add missing page routes

   Add route handlers for teams, divisions, conferences, playoffs, and
   stats pages. These routes were referenced by visual regression tests
   and page objects but were missing from the FastAPI app, causing 404
   errors.

   Routes added:
   - /teams - Team standings page
   - /divisions - Division standings page
   - /conferences - Conference standings page
   - /playoffs - Playoff bracket page
   - /stats - Statistics page

   All routes render index.html template (single-page app design).

   Fixes visual regression test failures for:
   - teams-page-full
   - divisions-page-full
   - conferences-page-full
   - playoffs-page-full
   - stats-page-full
   - teams-page-viewport
   - teams-page-tablet
   - teams-page-chromium

   Task: tasks/bug-fixes/002-missing-web-routes.md
   Issue: #TBD"
   ```

9. **Push and create PR**
   ```bash
   git push -u origin bug-fixes/002-missing-web-routes
   gh pr create
   ```

10. **Verify CI passes**
    - Monitor GitHub Actions workflows
    - Confirm QA Automation Tests pass
    - Verify Visual Regression Tests pass
    - Check test coverage

## Testing Strategy

### Local Testing

**Manual Browser Testing:**
```bash
# Start server
nhl-scrabble serve --host 0.0.0.0 --port 5000

# Test each route in browser:
# 1. http://localhost:5000/teams
# 2. http://localhost:5000/divisions
# 3. http://localhost:5000/conferences
# 4. http://localhost:5000/playoffs
# 5. http://localhost:5000/stats

# Expected: All render HTML pages (not JSON errors)
```

**cURL Testing:**
```bash
# Test routes return HTML
for route in teams divisions conferences playoffs stats; do
  echo "Testing /$route..."
  curl -I http://localhost:5000/$route | grep -E "HTTP|content-type"
done

# Expected output for each:
# HTTP/1.1 200 OK
# content-type: text/html; charset=utf-8
```

**Visual Regression Testing:**
```bash
# Full visual test suite
./scripts/pytest-playwright qa/web/tests/visual/ --browser=chromium
./scripts/pytest-playwright qa/web/tests/visual/ --browser=firefox
./scripts/pytest-playwright qa/web/tests/visual/ --browser=webkit

# Should see all snapshot tests pass
```

**Functional Testing:**
```bash
# Full functional test suite
./scripts/pytest-playwright qa/web/tests/functional/ --browser=chromium
./scripts/pytest-playwright qa/web/tests/functional/ --browser=firefox
./scripts/pytest-playwright qa/web/tests/functional/ --browser=webkit
```

### Unit/Integration Testing

Add tests to verify routes exist and return correct responses:

```python
def test_all_page_routes_exist(client):
    """Test all page routes return HTML."""
    routes = ["/", "/teams", "/divisions", "/conferences", "/playoffs", "/stats"]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<!DOCTYPE html>" in response.text  # Verify HTML response
```

### CI Testing

- Visual Regression Tests workflow will validate snapshots
- QA Automation Tests workflow will verify functional behavior
- All browsers (chromium, firefox, webkit) will be tested

## Acceptance Criteria

- [ ] `/teams` route exists and returns HTML (200 OK)
- [ ] `/divisions` route exists and returns HTML (200 OK)
- [ ] `/conferences` route exists and returns HTML (200 OK)
- [ ] `/playoffs` route exists and returns HTML (200 OK)
- [ ] `/stats` route exists and returns HTML (200 OK)
- [ ] All routes render `index.html` template successfully
- [ ] No JSON `{"detail": "Not Found"}` errors on these routes
- [ ] Visual regression tests pass for all affected pages
- [ ] Browser navigation works for all pages
- [ ] FastAPI docs show new routes in API documentation
- [ ] Templates configured properly (if using view context)
- [ ] Unit/integration tests added for new routes
- [ ] CI QA Automation workflow passes
- [ ] No breaking changes to existing routes

## Related Files

- `src/nhl_scrabble/web/app.py` - FastAPI application with routes
- `src/nhl_scrabble/web/templates/index.html` - Main template
- `qa/web/pages/teams_page.py` - TeamsPage page object
- `qa/web/pages/divisions_page.py` - DivisionsPage page object
- `qa/web/pages/conferences_page.py` - ConferencesPage page object
- `qa/web/pages/playoffs_page.py` - PlayoffsPage page object
- `qa/web/pages/stats_page.py` - StatsPage page object
- `qa/web/tests/visual/test_page_screenshots.py` - Visual regression tests
- `tests/integration/test_web_routes.py` - New route tests (to be created)

## Dependencies

None - This task can be implemented independently.

## Additional Notes

### Design Decision: Single Template vs Multiple Templates

**Recommended Approach:** Single template (`index.html`) with view context

**Reasoning:**
1. Current web interface appears to be a single-page application (SPA)
2. JavaScript/HTMX likely handles view switching dynamically
3. Less template duplication and easier maintenance
4. Consistent header/footer across all pages
5. Follows modern web app patterns

**Alternative:** If the application grows and pages become significantly different, separate templates may be warranted in a future refactoring task.

### Navigation and User Experience

Once routes exist, users can:
- Bookmark specific pages (e.g., `/teams`, `/playoffs`)
- Navigate directly to different views via URL
- Use browser back/forward buttons
- Share direct links to specific pages

### SEO and Accessibility

Having proper routes improves:
- **SEO**: Search engines can index individual pages
- **Accessibility**: Screen readers can announce page changes
- **User Experience**: Direct linking and bookmarking

### Template Context

The `view` context variable allows the template to:
- Highlight the active navigation item
- Set appropriate page title
- Show relevant content section on initial load
- Initialize JavaScript for the appropriate view

Example template usage:
```html
<title>
  {% if view == "teams" %}Teams - {% endif %}
  {% if view == "divisions" %}Divisions - {% endif %}
  {% if view == "conferences" %}Conferences - {% endif %}
  {% if view == "playoffs" %}Playoffs - {% endif %}
  {% if view == "stats" %}Stats - {% endif %}
  NHL Scrabble
</title>
```

### Testing Implications

Adding these routes will:
- ✅ Fix 8 visual regression test snapshot failures
- ✅ Enable functional tests that navigate to these pages
- ✅ Allow page objects to work correctly
- ✅ Improve test coverage and reliability

### Performance Considerations

Rendering the same template for multiple routes has minimal performance impact:
- Templates are cached by Jinja2
- No additional database queries or API calls
- Same static assets loaded regardless of route
- Client-side JavaScript handles most interactions

### Security Considerations

New routes follow the same security patterns as existing routes:
- Security headers middleware applies to all routes
- CSP policy enforced (except for `/docs`, `/redoc`)
- Template injection protection via Jinja2
- No additional attack surface introduced

### Future Enhancements

Once routes exist, future tasks could:
- Add server-side rendering for initial content
- Pre-fetch data for specific views
- Implement per-page caching strategies
- Add route-specific analytics tracking
- Create dedicated templates if views diverge significantly

## Implementation Notes

*To be filled during implementation:*
- Actual template approach chosen (single vs multiple)
- Any template modifications made
- JavaScript changes (if any)
- Challenges encountered
- Actual effort vs estimated (2-3h)
- Test results and coverage
- Browser-specific quirks discovered
