# Fix Web Interface Routes Showing Same Page

**GitHub Issue**: #474 - https://github.com/bdperkin/nhl-scrabble/issues/474

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

2-3 hours

## Description

The web interface shows the same homepage content instead of the expected data when navigating to different routes or clicking navigation links. All routes (/, /teams, /divisions, /conferences, /playoffs, /stats) display the same homepage with the analysis form instead of showing the specific data view for each route.

**Impact**: Web interface is essentially unusable for viewing different data views - users cannot access teams, divisions, conferences, playoffs, or stats pages directly.

## Current State

All route handlers in `src/nhl_scrabble/web/app.py` render the `index.html` template with a `view` context parameter:

```python
@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request) -> HTMLResponse:
    """Serve the teams standings page."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"view": "teams"},  # ← Context parameter is passed
    )
```

However, `src/nhl_scrabble/web/templates/index.html` does NOT use the `view` parameter:

```jinja2
{% extends "base.html" %}

{% block title %}NHL Scrabble Analyzer - Home{% endblock %}

{% block content %}
    <div class="hero">
        <h2>Analyze NHL Player Names by Scrabble Score</h2>
        <!-- ... always shows homepage content ... -->
    </div>

    <section class="analysis-form-section">
        <!-- ... always shows form ... -->
    </section>

    <!-- No conditional logic based on 'view' parameter -->
{% endblock %}
```

**Result**: All routes show the same homepage content (hero section, form, about section) regardless of URL.

## Proposed Solution

Modify the routes to automatically fetch and display data for specific views instead of just showing the form. This matches user expectations when navigating directly to `/teams`, `/divisions`, etc.

**Option A: Auto-load data in routes (RECOMMENDED)**

Modify routes to fetch analysis data and render it automatically:

```python
@app.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request) -> HTMLResponse:
    """Serve the teams standings page with data."""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    # Fetch analysis data
    analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
    data = await analyze_post(analysis_request)

    # Render results template with teams view
    return templates.TemplateResponse(
        request=request,
        name="teams.html",  # New template or modified results.html
        context={
            "view": "teams",
            "team_standings": data["team_standings"],
            "stats": data["stats"],
        },
    )
```

**Option B: Use JavaScript/HTMX to auto-trigger (ALTERNATIVE)**

Modify `index.html` to check the `view` parameter and auto-trigger data fetch:

```jinja2
{% extends "base.html" %}

{% block title %}
    {% if view == "teams" %}NHL Scrabble Analyzer - Teams
    {% elif view == "divisions" %}NHL Scrabble Analyzer - Divisions
    <!-- ... etc ... -->
    {% else %}NHL Scrabble Analyzer - Home{% endif %}
{% endblock %}

{% block content %}
    {% if view %}
        <!-- Auto-load data for specific view -->
        <div id="results" class="results-container"
             hx-get="/api/analyze"
             hx-trigger="load"
             hx-swap="innerHTML">
            <div class="loading">Loading {{ view }} data...</div>
        </div>
    {% else %}
        <!-- Show homepage with form -->
        <div class="hero">...</div>
        <section class="analysis-form-section">...</section>
    {% endif %}
{% endblock %}
```

**Recommendation**: Use Option A (auto-load in routes) for better initial page load performance and SEO.

## Implementation Steps

1. **Create view-specific template fragments** (or modify results.html):
   - `templates/teams.html` - Teams standings table
   - `templates/divisions.html` - Division standings
   - `templates/conferences.html` - Conference standings
   - `templates/playoffs.html` - Playoff bracket
   - `templates/stats.html` - Statistics dashboard

1. **Modify route handlers** to fetch and render data:
   - Update `teams_page()` to fetch data and render teams view
   - Update `divisions_page()` to fetch data and render divisions view
   - Update `conferences_page()` to fetch data and render conferences view
   - Update `playoffs_page()` to fetch data and render playoffs view
   - Update `stats_page()` to fetch data and render stats view

1. **Handle errors gracefully**:
   - If NHL API fails, show error message instead of crash
   - Provide link back to homepage to retry
   - Log errors for debugging

1. **Optimize caching**:
   - All views should use cached data (1-hour TTL)
   - Avoid re-fetching on every page navigation
   - Share cache across all views

1. **Update navigation** (already exists in base.html):
   - Verify nav links work correctly
   - Add active state indicators
   - Test all navigation paths

1. **Add page titles and metadata**:
   - Update `<title>` based on view
   - Add appropriate meta descriptions
   - Ensure accessibility (ARIA labels, semantic HTML)

## Testing Strategy

### Manual Testing

1. **Direct URL Navigation**:
   ```bash
   # Start server
   nhl-scrabble serve

   # Test each URL directly in browser
   curl http://localhost:5000/
   curl http://localhost:5000/teams
   curl http://localhost:5000/divisions
   curl http://localhost:5000/conferences
   curl http://localhost:5000/playoffs
   curl http://localhost:5000/stats
   ```

   **Expected**: Each URL shows different content specific to that view

1. **Navigation Links**:
   - Click "Home" → Shows homepage with form
   - Click "Teams" → Shows teams standings table
   - Click "Divisions" → Shows division standings
   - Click "Conferences" → Shows conference standings
   - Click "Playoffs" → Shows playoff bracket
   - Click "Stats" → Shows statistics dashboard

1. **Error Handling**:
   - Stop NHL API mock or use invalid data
   - Navigate to /teams → Should show error message, not crash
   - Error message should have link back to home

### Automated Tests

Update QA functional tests in `qa/web/tests/functional/test_navigation.py`:

```python
def test_teams_page_shows_teams_data(page: Page):
    """Test /teams route shows teams standings."""
    page.goto("http://localhost:5000/teams")

    # Should NOT show homepage hero
    assert page.locator(".hero").count() == 0

    # Should show teams table
    assert page.locator("#teamsTable").is_visible()
    assert "Team Standings" in page.content()

def test_divisions_page_shows_divisions_data(page: Page):
    """Test /divisions route shows division standings."""
    page.goto("http://localhost:5000/divisions")

    # Should NOT show homepage form
    assert page.locator("#analysisForm").count() == 0

    # Should show division cards
    assert page.locator(".division-card").count() > 0
    assert "Division Standings" in page.content()

# Similar tests for /conferences, /playoffs, /stats
```

Update visual regression tests in `qa/web/tests/visual/test_page_screenshots.py`:

```python
def test_teams_page_visual(page: Page):
    """Visual regression test for teams page."""
    page.goto("http://localhost:5000/teams")
    page.wait_for_selector("#teamsTable", state="visible")
    assert page.screenshot() == "teams-page-with-data.png"
```

## Acceptance Criteria

- [ ] `/` shows homepage with analysis form
- [ ] `/teams` shows teams standings table (not homepage)
- [ ] `/divisions` shows division standings (not homepage)
- [ ] `/conferences` shows conference standings (not homepage)
- [ ] `/playoffs` shows playoff bracket (not homepage)
- [ ] `/stats` shows statistics dashboard (not homepage)
- [ ] Navigation links work correctly between all views
- [ ] Direct URL access works for all routes
- [ ] Data loads automatically when navigating to view-specific routes
- [ ] Cached data is shared across all views (no duplicate API calls)
- [ ] Error handling shows appropriate message if API fails
- [ ] Page titles update based on current view
- [ ] All QA functional tests pass
- [ ] Visual regression tests updated for new page views
- [ ] Documentation updated (if needed)

## Related Files

- `src/nhl_scrabble/web/app.py` - Route handlers (lines 153-287)
- `src/nhl_scrabble/web/templates/index.html` - Homepage template
- `src/nhl_scrabble/web/templates/results.html` - Results display template
- `src/nhl_scrabble/web/templates/base.html` - Base template with navigation
- `qa/web/tests/functional/test_navigation.py` - Navigation tests
- `qa/web/tests/visual/test_page_screenshots.py` - Visual regression tests

## Dependencies

None - standalone bug fix

## Additional Notes

### Performance Considerations

- Use cached data (1-hour TTL) to avoid re-fetching on every page load
- Cache is already implemented in `/api/analyze` endpoint
- All views should share the same cache key

### Security Considerations

- No security implications - read-only data display
- Existing security headers middleware remains unchanged

### Breaking Changes

None - only fixing existing broken functionality

### Alternative Approaches Considered

1. **Single-page app with client-side routing**:
   - Pros: No page reloads, smooth navigation
   - Cons: More complex, requires JavaScript framework
   - Rejected: Overkill for simple multi-page app

1. **Conditional template in index.html**:
   - Pros: Single template file, simple
   - Cons: Large template file, harder to maintain
   - Rejected: Violates separation of concerns

1. **Redirect to homepage with view parameter**:
   - Pros: Minimal code changes
   - Cons: Extra redirect, poor UX, doesn't fix direct URL access
   - Rejected: Doesn't solve the root problem

### User Experience Impact

**Before**: All routes show homepage → Confusing, unusable
**After**: Each route shows expected data → Clear, intuitive navigation

### Future Enhancements

Consider adding in future tasks:
- Breadcrumb navigation
- Back/forward button support (browser history)
- Loading states for data fetch
- Pagination for large datasets
- Filter/search capabilities per view

## Implementation Notes

*To be filled during implementation:*
- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Related PRs
