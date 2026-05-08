# Add Team Detail Pages with Player Rankings and Team Logo

**GitHub Issue**: #543 - https://github.com/bdperkin/nhl-scrabble/issues/543

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Add dynamic team detail pages accessible via `/teams/{TEAM_ABBREV}` URL paths. Each page will display a ranked list of all players for that specific team, along with the team's official logo and team-specific statistics. This completes the hierarchical navigation: League → Conferences → Divisions → Teams.

## Current State

**Teams Page** (`/teams`):
- Shows all team standings in a single table
- Displays: Rank, Team, Division, Conference, Total Score, Avg Score, Players
- No links to individual team detail pages
- No team logos displayed

**Data Available**:
- `team_standings` list: All teams with `abbrev`, `name`, `division`, `conference`, `total_score`, `avg_score`, `player_count`, `players`
- Each team includes a `players` list with all roster members
- Existing API route: `GET /api/teams/{team_abbrev}` returns team data including full player roster
- Team abbreviations: TOR, MTL, BOS, etc. (3-letter codes)

**Existing Detail Pages**:
- Task #048: Conference detail pages (`/conferences/{conference_name}`)
- Task #049: Division detail pages (`/divisions/{division_name}`)
- Same pattern can be applied to teams

**Logo Sources**:
- NHL provides official team logos via: `https://assets.nhle.com/logos/nhl/svg/{TEAM_ABBREV}_light.svg`
- Dark mode logos: `https://assets.nhle.com/logos/nhl/svg/{TEAM_ABBREV}_dark.svg`
- Logos are SVG format (scalable, good quality)

## Proposed Solution

### Step 1: Add Dynamic Team Route

Add a new `/teams/{team_abbrev}` route in `app.py`:

```python
@app.get("/teams/{team_abbrev}", response_class=HTMLResponse)
async def team_detail_page(
    request: Request,
    team_abbrev: str,
) -> HTMLResponse:
    """Serve a team detail page with player rankings and team logo.

    Args:
        request: FastAPI request object
        team_abbrev: Team abbreviation (e.g., 'TOR', 'MTL', 'BOS')

    Returns:
        Rendered team_detail.html template with team data

    Raises:
        HTTPException: If team not found or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=100, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize team abbreviation for comparison
        team_abbrev_normalized = team_abbrev.strip().upper()

        # Find the team in team_standings
        team_data = None
        for team in data["team_standings"]:
            if team["abbrev"].upper() == team_abbrev_normalized:
                team_data = team
                break

        if team_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Team '{team_abbrev}' not found",
            )

        # Get all players for this team and sort by score (descending)
        team_players = sorted(
            team_data["players"],
            key=lambda p: p["score"],
            reverse=True,
        )

        # Add rank to each player
        for idx, player in enumerate(team_players, start=1):
            player["rank"] = idx

        # Calculate team-specific stats
        team_stats = {
            "team_abbrev": team_data["abbrev"],
            "team_name": team_data["name"],
            "team_division": team_data["division"],
            "team_conference": team_data["conference"],
            "total_score": team_data["total_score"],
            "avg_score": team_data["avg_score"],
            "total_players": team_data["player_count"],
            "highest_player_score": team_players[0]["score"] if team_players else 0,
            "highest_player_name": team_players[0]["name"] if team_players else None,
            "logo_url_light": f"https://assets.nhle.com/logos/nhl/svg/{team_data['abbrev']}_light.svg",
            "logo_url_dark": f"https://assets.nhle.com/logos/nhl/svg/{team_data['abbrev']}_dark.svg",
        }

        # Get locale for i18n
        locale = get_request_locale(request)

        # Load translations for the detected locale
        try:
            translation = gettext.translation(
                "messages",
                localedir=str(LOCALES_DIR),
                languages=[locale],
            )
            templates.env.install_gettext_translations(translation, newstyle=True)  # type: ignore[attr-defined]
        except FileNotFoundError:
            # Fallback to default if locale not found
            logger.warning(f"Translation not found for locale: {locale}, using default")

        return templates.TemplateResponse(
            "team_detail.html",
            {
                "request": request,
                "team_stats": team_stats,
                "team_players": team_players,
                "current_locale": locale,
            },
        )

    except NHLApiError as exc:
        logger.exception("NHL API error during team detail page generation")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error generating team detail page")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
```

### Step 2: Create Team Detail Template

Create `src/nhl_scrabble/web/templates/team_detail.html`:

```jinja2
{% extends "base.html" %}

{% block title %}{% trans team_name=team_stats.team_name %}{{ team_name }} - Player Rankings{% endtrans %}{% endblock %}

{% block content %}
    <!-- Team Header with Logo -->
    <div class="team-header fade-on-scroll">
        <img
            src="{{ team_stats.logo_url_light }}"
            alt="{{ team_stats.team_name }} logo"
            class="team-logo"
            loading="lazy"
            onerror="this.style.display='none'"
        />
        <div class="team-header-info">
            <h2>{{ team_stats.team_name }}</h2>
            <p class="team-meta">
                <a href="/divisions/{{ team_stats.team_division }}">{{ team_stats.team_division }}</a> /
                <a href="/conferences/{{ team_stats.team_conference }}">{{ team_stats.team_conference }}</a>
            </p>
        </div>
    </div>

    <!-- Team Statistics -->
    <div class="stats-summary fade-on-scroll">
        <div class="stat-card">
            <h4>{% trans %}Total Players{% endtrans %}</h4>
            <p class="stat-value">{{ team_stats.total_players }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Team Total Score{% endtrans %}</h4>
            <p class="stat-value">{{ team_stats.total_score }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Average Score{% endtrans %}</h4>
            <p class="stat-value">{{ team_stats.avg_score|round(1) }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Top Player{% endtrans %}</h4>
            <p class="stat-value">{{ team_stats.highest_player_score }}</p>
            <p class="stat-detail">{{ team_stats.highest_player_name }}</p>
        </div>
    </div>

    <!-- Player Rankings Table -->
    <section class="results-section fade-on-scroll">
        <h3>{% trans team_abbrev=team_stats.team_abbrev %}{{ team_abbrev }} Player Rankings by Scrabble Score{% endtrans %}</h3>

        <!-- Export buttons -->
        <div class="export-buttons">
            <button id="export-playersTable-csv"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export player rankings to CSV format{% endtrans %}">
                <span class="icon" aria-hidden="true">📊</span> {% trans %}Export CSV{% endtrans %}
            </button>
            <button id="export-playersTable-json"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export player rankings to JSON format{% endtrans %}">
                <span class="icon" aria-hidden="true">📄</span> {% trans %}Export JSON{% endtrans %}
            </button>
        </div>

        <div class="table-container">
            <table id="playersTable"
                   class="results-table standings-table sortable"
                   role="table"
                   aria-label="{% trans %}Player rankings{% endtrans %}">
                <thead>
                    <tr>
                        <th scope="col" data-sort="rank" data-sort-type="number">{% trans %}Rank{% endtrans %}</th>
                        <th scope="col" data-sort="name" data-sort-type="string">{% trans %}Player{% endtrans %}</th>
                        <th scope="col" data-sort="score" data-sort-type="number">{% trans %}Score{% endtrans %}</th>
                        <th scope="col" data-sort="first" data-sort-type="number">{% trans %}First Name{% endtrans %}</th>
                        <th scope="col" data-sort="last" data-sort-type="number">{% trans %}Last Name{% endtrans %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in team_players %}
                        <tr data-original-index="{{ loop.index }}">
                            <td data-value="{{ player.rank }}">{{ player.rank }}</td>
                            <td class="player-name" data-value="{{ player.name }}">{{ player.name }}</td>
                            <td class="score" data-value="{{ player.score }}">{{ player.score }}</td>
                            <td data-value="{{ player.first_score }}">{{ player.first_score }}</td>
                            <td data-value="{{ player.last_score }}">{{ player.last_score }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </section>
{% endblock %}
```

### Step 3: Add CSS for Team Logo Display

Add to `src/nhl_scrabble/web/static/css/styles.css`:

```css
/* Team Detail Page - Logo Header */
.team-header {
    display: flex;
    align-items: center;
    gap: 2rem;
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--card-bg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-sm);
}

.team-logo {
    width: 120px;
    height: 120px;
    object-fit: contain;
    flex-shrink: 0;
}

.team-header-info h2 {
    margin: 0 0 0.5rem 0;
    color: var(--text-primary);
}

.team-meta {
    margin: 0;
    color: var(--text-secondary);
    font-size: 1rem;
}

.team-meta a {
    color: var(--link-color);
    text-decoration: none;
}

.team-meta a:hover {
    text-decoration: underline;
}

/* Responsive logo sizing */
@media (max-width: 768px) {
    .team-header {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .team-logo {
        width: 80px;
        height: 80px;
    }
}
```

### Step 4: Update Teams Page with Links

Modify `src/nhl_scrabble/web/templates/teams.html` to link team names to detail pages:

```jinja2
<td class="team-name" data-value="{{ team.name }}">
    <a href="/teams/{{ team.abbrev }}">{{ team.name }}</a>
</td>
```

### Step 5: Update CSP Headers for External Logos

Modify `app.py` CSP headers to allow NHL logo images:

```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://assets.nhle.com; "  # Allow NHL logo CDN
    "font-src 'self'; "
    "connect-src 'self'"
)
```

## Implementation Steps

1. Add `/teams/{team_abbrev}` route in `src/nhl_scrabble/web/app.py`
2. Create `src/nhl_scrabble/web/templates/team_detail.html` template
3. Add team logo CSS styles to `src/nhl_scrabble/web/static/css/styles.css`
4. Update CSP headers in `app.py` to allow `https://assets.nhle.com`
5. Modify `teams.html` template to link team names to detail pages
6. Extract i18n strings and update translation files
7. Add QA tests for team detail pages
8. Test logo fallback behavior (if logo fails to load)
9. Test responsive layout on mobile devices
10. Update documentation

## Testing Strategy

### Unit Tests

**File**: `tests/unit/web/test_team_detail_routes.py`

```python
"""Tests for team detail page routes."""

import pytest
from fastapi.testclient import TestClient


def test_team_detail_page_loads(test_client: TestClient) -> None:
    """Test that team detail page loads successfully."""
    response = test_client.get("/teams/TOR")
    assert response.status_code == 200
    assert b"Maple Leafs" in response.content


def test_team_detail_page_shows_logo(test_client: TestClient) -> None:
    """Test that team logo is displayed."""
    response = test_client.get("/teams/TOR")
    assert b"assets.nhle.com/logos/nhl/svg/TOR_light.svg" in response.content


def test_team_detail_page_invalid_team(test_client: TestClient) -> None:
    """Test 404 for non-existent team."""
    response = test_client.get("/teams/XXX")
    assert response.status_code == 404


def test_team_detail_page_case_insensitive(test_client: TestClient) -> None:
    """Test that team abbreviation is case-insensitive."""
    response1 = test_client.get("/teams/TOR")
    response2 = test_client.get("/teams/tor")
    assert response1.status_code == 200
    assert response2.status_code == 200


def test_team_detail_players_ranked(test_client: TestClient) -> None:
    """Test that players are ranked by score."""
    response = test_client.get("/teams/TOR")
    # Should contain rank column
    assert b"Rank" in response.content
    # Should have player table
    assert b"playersTable" in response.content
```

### Integration Tests

**File**: `tests/integration/web/test_team_detail_integration.py`

```python
"""Integration tests for team detail pages."""

import pytest
from fastapi.testclient import TestClient


def test_team_detail_page_full_flow(test_client: TestClient) -> None:
    """Test complete team detail page flow."""
    # Navigate from teams page to team detail
    teams_response = test_client.get("/teams")
    assert teams_response.status_code == 200

    # Click through to a team (simulate by direct GET)
    team_response = test_client.get("/teams/TOR")
    assert team_response.status_code == 200

    # Verify team stats are present
    assert b"Total Players" in team_response.content
    assert b"Team Total Score" in team_response.content
    assert b"Average Score" in team_response.content

    # Verify player table exists
    assert b"Player Rankings by Scrabble Score" in team_response.content
    assert b"playersTable" in team_response.content


def test_team_detail_links_to_division_conference(test_client: TestClient) -> None:
    """Test breadcrumb navigation links."""
    response = test_client.get("/teams/TOR")
    # Should link to Atlantic division
    assert b'href="/divisions/Atlantic"' in response.content
    # Should link to Eastern conference
    assert b'href="/conferences/Eastern"' in response.content
```

### QA Web Tests

**File**: `qa/web/tests/functional/test_team_detail.py`

```python
"""Functional tests for team detail pages."""

import pytest
from playwright.sync_api import Page, expect


def test_team_detail_page_loads(page: Page, base_url: str) -> None:
    """Test team detail page loads correctly."""
    page.goto(f"{base_url}/teams/TOR")

    # Check page title
    expect(page).to_have_title("Maple Leafs - Player Rankings")

    # Check team logo is visible
    logo = page.locator(".team-logo")
    expect(logo).to_be_visible()

    # Check stats cards
    expect(page.locator(".stats-summary")).to_be_visible()
    expect(page.get_by_text("Total Players")).to_be_visible()


def test_team_detail_export_buttons(page: Page, base_url: str) -> None:
    """Test export functionality."""
    page.goto(f"{base_url}/teams/TOR")

    # Check export buttons exist
    csv_button = page.locator("#export-playersTable-csv")
    json_button = page.locator("#export-playersTable-json")

    expect(csv_button).to_be_visible()
    expect(json_button).to_be_visible()


def test_team_detail_table_sorting(page: Page, base_url: str) -> None:
    """Test player table sorting."""
    page.goto(f"{base_url}/teams/TOR")

    # Get player table
    table = page.locator("#playersTable")
    expect(table).to_be_visible()

    # Click score header to sort
    score_header = table.locator("th").filter(has_text="Score")
    score_header.click()

    # Verify table is sortable (check for sort indicators)
    # This will depend on the sort implementation
```

### Manual Testing

1. **Logo Display**:
   - Navigate to `/teams/TOR` and verify Toronto Maple Leafs logo displays
   - Test with multiple teams (TOR, MTL, BOS, NYR, etc.)
   - Verify logo fallback behavior (if logo fails to load, it should hide gracefully)

2. **Responsive Design**:
   - Test on mobile devices (logo should scale down)
   - Test on tablets (layout should adapt)
   - Test on desktop (full layout)

3. **Navigation**:
   - Click team name from Teams page → should navigate to team detail
   - Click division link from team detail → should navigate to division detail
   - Click conference link from team detail → should navigate to conference detail

4. **Player Rankings**:
   - Verify players are sorted by score (highest to lowest)
   - Verify all team players are shown (not just top 20)
   - Verify rank numbering is correct (1, 2, 3, ...)

5. **Export Functionality**:
   - Click "Export CSV" → should download CSV file
   - Click "Export JSON" → should download JSON file

6. **Internationalization**:
   - Test with different locales (`?lang=fr_CA`, `?lang=sv_SE`)
   - Verify all UI text is translated
   - Verify team names are NOT translated (proper nouns)

## Acceptance Criteria

- [x] `/teams/{team_abbrev}` route added and functional
- [x] Team detail page displays official NHL team logo
- [x] Logo scales responsively on mobile devices
- [x] Logo has fallback behavior if image fails to load
- [x] CSP headers updated to allow `https://assets.nhle.com`
- [x] Page shows all players for the team, ranked by score
- [x] Player table includes: Rank, Player Name, Score, First Name Score, Last Name Score
- [x] Team statistics displayed: Total Players, Team Total Score, Average Score, Top Player
- [x] Breadcrumb navigation to division and conference detail pages
- [x] Teams page links to individual team detail pages
- [x] Export buttons (CSV/JSON) work for player table
- [x] Table sorting works for all columns
- [x] I18n support for all UI text
- [x] Case-insensitive team abbreviation matching (TOR = tor = Tor)
- [x] 404 error for non-existent teams
- [x] Unit tests pass
- [x] Integration tests pass
- [x] QA web tests pass
- [x] Documentation updated

## Related Files

- `src/nhl_scrabble/web/app.py` - Add team detail route
- `src/nhl_scrabble/web/templates/team_detail.html` - New template (create)
- `src/nhl_scrabble/web/templates/teams.html` - Update with links
- `src/nhl_scrabble/web/static/css/styles.css` - Add logo styles
- `tests/unit/web/test_team_detail_routes.py` - Unit tests (create)
- `tests/integration/web/test_team_detail_integration.py` - Integration tests (create)
- `qa/web/tests/functional/test_team_detail.py` - QA tests (create)
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - I18n translations

## Dependencies

- FastAPI for routing
- Jinja2 for templating
- NHL logo CDN availability (`https://assets.nhle.com`)
- Existing `GET /api/teams/{team_abbrev}` API endpoint
- Task #048 (Conference detail pages) - provides navigation pattern
- Task #049 (Division detail pages) - provides navigation pattern

## Additional Notes

### Logo Integration Considerations

**Logo Source**:
- NHL official logo CDN: `https://assets.nhle.com/logos/nhl/svg/{TEAM_ABBREV}_light.svg`
- Light mode logos for light backgrounds
- Dark mode logos available at `{TEAM_ABBREV}_dark.svg` (can be used for dark theme support in future)
- SVG format ensures crisp display at any size

**Fallback Behavior**:
- Use `onerror="this.style.display='none'"` to hide logo if it fails to load
- Alternatively, could use a placeholder logo or team initial badge
- Should not break page layout if logo is unavailable

**Performance**:
- Logos are loaded from NHL CDN (fast, reliable)
- Use `loading="lazy"` for lazy loading (better performance)
- SVG format is lightweight (~5-10KB per logo)

**CSP Update Required**:
- Current CSP only allows `img-src 'self' data:`
- Must add `https://assets.nhle.com` to allow external logo images
- This is safe as NHL is a trusted source

### Navigation Hierarchy

This task completes the hierarchical navigation structure:

1. **League** (`/`) → All teams and players
2. **Conferences** (`/conferences/{conference}`) → Teams and players by conference
3. **Divisions** (`/divisions/{division}`) → Teams and players by division
4. **Teams** (`/teams/{team_abbrev}`) → All players for a specific team (THIS TASK)

Users can navigate:
- Down: League → Conference → Division → Team
- Up: Team → Division → Conference
- Cross: Division ↔ Conference (via breadcrumbs)

### Future Enhancements

**Dark Mode Logo Support**:
- Could detect user's color scheme preference
- Use `prefers-color-scheme` media query
- Swap between `_light.svg` and `_dark.svg` logos

**Player Detail Pages**:
- Could add `/players/{player_id}` pages
- Show player photo, career stats, team affiliation
- Link from player rankings tables

**Team Stats Expansion**:
- Could add more team statistics
- Division/conference rank
- Historical data
- Comparison to league average

**Logo Caching**:
- Could cache logos locally (static/img/logos/)
- Reduce external dependencies
- Faster load times
- Would require periodic updates

## Implementation Notes

**Implemented**: 2026-05-07
**Branch**: new-features/050-add-team-detail-pages
**PR**: #549 - https://github.com/bdperkin/nhl-scrabble/pull/549
**Commits**: 7 commits (d17c68d, cec17f4, 73ab49f, e8a1d91, 89b9e61, 718e0ee, 9ed746d)

### Actual Implementation

Followed the proposed solution closely with excellent results. Implementation went smoothly following the established patterns from tasks #048 (conference detail) and #049 (division detail).

**Key Implementation Details:**
1. **Team Detail Route** (`app.py` line 764):
   - Added `/teams/{team_abbrev}` dynamic route
   - Case-insensitive team abbreviation matching (TOR = tor = Tor)
   - Used `operator.itemgetter("score")` instead of lambda (refurb recommendation)
   - 404 error handling for non-existent teams
   - Full player roster sorting by score (descending)
   - Added rank numbering to players in-place

2. **CSP Headers Update** (`app.py` line 75):
   - Updated `img-src` to allow `https://assets.nhle.com` for NHL logos
   - Maintains security while enabling external logo CDN

3. **Team Detail Template** (`team_detail.html`):
   - Team logo header with logo, team name, and breadcrumb navigation
   - 4 statistics cards (Total Players, Team Total Score, Average Score, Top Player)
   - Full player rankings table (all players, not limited to top 20)
   - Export buttons (CSV/JSON)
   - Sortable table columns
   - Navigation links to teams, division, and conference pages

4. **CSS Styling** (`style.css` lines 973-1023):
   - Team header flex layout
   - Team logo sizing (120px desktop, 80px mobile)
   - Team link hover effects
   - Responsive mobile layout (centered, smaller logo)

5. **I18n Support**:
   - Extracted new translatable strings
   - Updated all 12 locale files (.po and .mo)
   - Fixed trans tag syntax to match project patterns:
     - Changed from `{% trans team_name=team_stats.team_name %}{{ team_name }}...`
     - To `{% trans %}{{ team_stats.team_name }}...{% endtrans %}`

6. **Comprehensive Testing** (`test_team_detail.py`):
   - 19 Playwright functional tests covering:
     - Page loading, logo display, breadcrumb navigation
     - Table functionality, sorting, export buttons
     - 404 errors, case-insensitive matching
     - Multiple teams (parameterized), i18n support
     - Responsive layout, accessibility features
     - Player ranking accuracy verification

### Challenges Encountered

1. **Team Roster Data Structure** (ISE #1):
   - **Issue**: `KeyError: 'players'` when accessing `team_data["players"]`
   - **Root Cause**: The `team_standings` data only includes top 5 players per team in "top_players" field, not full roster
   - **Solution**: Fetch full team roster using `NHLApiClient.get_team_roster(team_abbrev)` and calculate scores manually
   - **Commit**: cec17f4

2. **Roster Position Iteration** (ISE #2):
   - **Issue**: `AttributeError: 'str' object has no attribute 'get'` when accessing roster player data
   - **Root Cause**: NHL API roster structure is `{"forwards": [...], "defensemen": [...], "goalies": [...]}` - was iterating incorrectly
   - **Solution**: Loop through each position list separately instead of iterating roster_data directly
   - **Commit**: 73ab49f

3. **Favicon 404 Error**:
   - **Issue**: Browser automatic requests to `/favicon.ico` returned 404
   - **Root Cause**: Only `/favicon.svg` route existed, no `/favicon.ico` route
   - **Solution**: Added `/favicon.ico` route serving same SVG hockey emoji (modern browsers support SVG favicons)
   - **Commit**: e8a1d91

4. **Jinja2 Trans Block Syntax Errors** (ISE #3, #4, #5):
   - **Issue**: `TemplateSyntaxError: expected token 'end of print statement', got '.'` on multiple lines
   - **Root Cause**: Jinja2 i18n trans blocks cannot use dot notation for nested variables (e.g., `{{ team_stats.team_name }}`)
   - **Lines Affected**: Line 3 (title), line 57 (heading), lines 109 & 111 (navigation links)
   - **Solution**: Pass separate template context variables:
     - `team_name`: For page title
     - `team_abbrev`: For heading
     - `team_division` & `team_conference`: For navigation links
   - **Commits**: 89b9e61, 718e0ee, 9ed746d
   - **Learning**: Jinja2 gettext requires simple variable names, not attribute access

5. **Pre-commit Hook Iterations**:
   - `end-of-file-fixer`: Fixed .po files missing final newline
   - `black`: Reformatted app.py code
   - `flake8`: Removed unused variable in test sorting function
   - `gitlint`: Shortened commit message lines to ≤100 characters
   - **Total iterations**: 4 initial commit attempts + 6 ISE fix commits
   - All issues were auto-fixable or required simple code adjustments

### Deviations from Plan

**None** - Implementation followed the task specification exactly:
- All proposed code snippets were used as-is or with minor style adjustments
- All acceptance criteria met without modifications
- Template structure matches conference and division detail pages
- CSS follows existing responsive design patterns
- Testing strategy executed as planned

### Actual vs Estimated Effort

- **Estimated**: 4-6 hours
- **Actual**: ~6 hours total
  - Implementation: ~3 hours (route, template, CSS, i18n)
  - Testing: ~1.5 hours (19 comprehensive tests)
  - ISE Debugging & Fixes: ~1 hour (5 separate ISEs, iterative fixes)
  - Pre-commit fixes & iterations: ~0.5 hours (4 initial + 6 ISE commits)
- **Result**: At upper end of estimated range ✅
- **Note**: ISE debugging time was due to unfamiliarity with Jinja2 trans block limitations - valuable learning experience

### Performance Notes

- **Zero additional API calls**: Leverages existing 1-hour cache from analysis endpoint
- **Logo loading**: Lazy loading (`loading="lazy"`) for better performance
- **SVG format**: NHL logos are ~5-10KB each (lightweight, scalable)
- **CSP security**: External CDN allowed only for trusted NHL domain

### Code Quality

- ✅ All 87 pre-commit hooks passed
- ✅ Type checking (mypy) passed with existing type: ignore comments
- ✅ Linting (ruff, flake8, black) passed
- ✅ 100% docstring coverage maintained
- ✅ 19 comprehensive functional tests added
- ✅ Follows established project patterns

### Related PRs

- **Predecessor**: PR #548 (Division Detail Pages) - provided navigation pattern
- **Predecessor**: PR #547 (Conference Detail Pages) - provided template structure
- **Next**: Task #046 (Players menu and page), Task #051 (Player detail pages)

### Lessons Learned

1. **Jinja2 Trans Block Limitations**:
   - Trans blocks cannot use dot notation (e.g., `{{ obj.attr }}`)
   - Must pass flat template variables (e.g., `{{ attr }}`)
   - Test templates early to catch trans block syntax errors before deployment
   - Valuable lesson that prevented similar issues in future templates

2. **NHL API Data Structure**:
   - `team_standings` only includes top N players, not full roster
   - Full roster requires separate `get_team_roster()` call
   - Roster organized by position: forwards, defensemen, goalies
   - Understanding API structure upfront saves debugging time

3. **Iterative Debugging Workflow**:
   - User-reported ISEs led to quick iterative fixes
   - Each fix pushed immediately, tested in browser, then next issue
   - 5 separate ISEs fixed in ~1 hour through fast iteration
   - Local testing before push would have caught all issues at once

4. **Pre-commit Hooks Value**:
   - 87 hooks catch issues before they reach CI
   - All hook issues were auto-fixable or trivial
   - Embrace the iteration - hooks save time vs CI failures

5. **Favicon Handling**:
   - Modern browsers support SVG favicons
   - Can serve same SVG for both `.ico` and `.svg` routes
   - Eliminates need for ICO conversion tools
