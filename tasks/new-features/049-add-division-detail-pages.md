# Add Division Detail Pages with Team Standings and Top Players

**GitHub Issue**: #542 - https://github.com/bdperkin/nhl-scrabble/issues/542

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Add dynamic division detail pages accessible via `/divisions/{DIVISION_NAME}` URL paths. Each page will display a team standings table for that specific division (mimicking the main Teams page layout) followed by the Top 20 Players by Scrabble Score from that division. Update the Divisions page to link to these detail pages.

## Current State

**Divisions Page** (`/divisions`):
- Shows division standings grouped by division
- Uses card-based layout with division-grid
- Each division displayed in a separate card
- No links to division detail pages

**Data Available**:
- `division_standings` dict: `{division_name: [teams]}`
- `team_standings` list: All teams with division property
- `top_players` list: All players with division property
- NHL has 4 divisions: Atlantic, Metropolitan, Central, Pacific

**Existing Detail Pages**:
- Task #048 created conference detail pages (`/conferences/{conference_name}`)
- Same pattern can be applied to divisions
- Teams page shows all teams in table format
- Divisions page shows grouped cards

## Proposed Solution

### Step 1: Add Dynamic Division Route

Add a new `/divisions/{division_name}` route in `app.py`:

```python
@app.get("/divisions/{division_name}", response_class=HTMLResponse)
async def division_detail_page(
    request: Request,
    division_name: str,
) -> HTMLResponse:
    """Serve a division detail page with teams and top players.

    Args:
        request: FastAPI request object
        division_name: Division name (Atlantic, Metropolitan, Central, Pacific)

    Returns:
        Rendered division_detail.html template with filtered data

    Raises:
        HTTPException: If division not found or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        # Increase top_players to ensure we get 20+ per division
        analysis_request = AnalysisRequest(top_players=100, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize division name for comparison
        division_normalized = division_name.strip().title()

        # Validate division exists
        if division_normalized not in data["division_standings"]:
            raise HTTPException(
                status_code=404,
                detail=f"Division '{division_name}' not found",
            )

        # Filter teams for this division
        division_teams = [
            team for team in data["team_standings"]
            if team["division"] == division_normalized
        ]

        # Filter top players for this division
        division_team_abbrevs = {team["abbrev"] for team in division_teams}
        division_players = [
            player for player in data["top_players"]
            if player["team"] in division_team_abbrevs
        ][:20]  # Top 20 players from this division

        # Calculate division-specific stats
        division_stats = {
            "total_teams": len(division_teams),
            "total_players": sum(t["player_count"] for t in division_teams),
            "highest_team_score": division_teams[0]["total_score"] if division_teams else 0,
            "highest_team": division_teams[0]["abbrev"] if division_teams else None,
            "highest_team_name": division_teams[0]["name"] if division_teams else None,
            "highest_player_score": division_players[0]["score"] if division_players else 0,
            "highest_player_name": division_players[0]["full_name"] if division_players else None,
            "conference": division_teams[0]["conference"] if division_teams else None,
        }

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "division_name": division_normalized,
                "division_teams": division_teams,
                "division_players": division_players,
                "division_stats": division_stats,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="division_detail.html",
            context=context,
        )

    except NHLApiError as e:
        logger.error("Failed to fetch division detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
```

**Location**: Insert after `divisions_page()` function (around line 812) or after conference_detail_page if implemented

### Step 2: Create division_detail.html Template

Create `src/nhl_scrabble/web/templates/division_detail.html`:

```html
{% extends "base.html" %}

{% block title %}{% trans %}NHL Scrabble Analyzer - {{ division_name }} Division{% endtrans %}{% endblock %}

{% block og_title %}{{ division_name }} {% trans %}Division Standings{% endtrans %}{% endblock %}
{% block twitter_title %}{{ division_name }} {% trans %}Division Standings{% endtrans %}{% endblock %}

{% block content %}
    <div class="page-header fade-on-scroll">
        <h2>{{ division_name }} {% trans %}Division{% endtrans %}</h2>
        <p class="page-description">
            {% trans %}Team standings and top players from the {{ division_name }} Division ranked by Scrabble score.{% endtrans %}
        </p>
        <p class="timestamp">
            {% trans %}Data as of{% endtrans %}: {{ timestamp_date }} {{ timestamp_time }}
        </p>
    </div>

    <!-- Division Summary Statistics -->
    <div class="stats-summary fade-on-scroll">
        <div class="stat-card">
            <h4>{% trans %}Conference{% endtrans %}</h4>
            <p class="stat-value" style="font-size: 1.2rem;">{{ division_stats.conference }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Total Teams{% endtrans %}</h4>
            <p class="stat-value">{{ division_stats.total_teams }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Top Team{% endtrans %}</h4>
            <p class="stat-value">{{ division_stats.highest_team_score }}</p>
            <p class="stat-detail">{{ division_stats.highest_team }} ({{ division_stats.highest_team_name }})</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Total Players{% endtrans %}</h4>
            <p class="stat-value">{{ division_stats.total_players }}</p>
        </div>
    </div>

    <!-- Team Standings Table -->
    <section class="results-section fade-on-scroll">
        <h3>{% trans %}Team Standings by Total Scrabble Score{% endtrans %}</h3>

        <!-- Export buttons -->
        <div class="export-buttons">
            <button id="export-divisionTeamsTable-csv"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export team standings table to CSV format{% endtrans %}">
                <span class="icon" aria-hidden="true">📊</span> {% trans %}Export CSV{% endtrans %}
            </button>
            <button id="export-divisionTeamsTable-json"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export team standings table to JSON format{% endtrans %}">
                <span class="icon" aria-hidden="true">📄</span> {% trans %}Export JSON{% endtrans %}
            </button>
        </div>

        <div class="table-container">
            <table id="divisionTeamsTable"
                   class="results-table standings-table sortable"
                   role="table"
                   aria-label="{% trans %}Team standings for {{ division_name }} Division{% endtrans %}">
                <thead>
                    <tr>
                        <th scope="col" data-sort="rank" data-sort-type="number">{% trans %}Rank{% endtrans %}</th>
                        <th scope="col" data-sort="team" data-sort-type="string">{% trans %}Team{% endtrans %}</th>
                        <th scope="col" data-sort="total" data-sort-type="number">{% trans %}Total Score{% endtrans %}</th>
                        <th scope="col" data-sort="avg" data-sort-type="number">{% trans %}Avg Score{% endtrans %}</th>
                        <th scope="col" data-sort="players" data-sort-type="number">{% trans %}Players{% endtrans %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for team in division_teams %}
                        <tr data-original-index="{{ loop.index }}">
                            <td data-value="{{ loop.index }}">{{ loop.index }}</td>
                            <td class="team-name" data-value="{{ team.name }}">{{ team.name }}</td>
                            <td class="score" data-value="{{ team.total_score }}">{{ team.total_score }}</td>
                            <td data-value="{{ team.avg_score|round(1) }}">{{ team.avg_score|round(1) }}</td>
                            <td data-value="{{ team.player_count }}">{{ team.player_count }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </section>

    <!-- Top Players Section -->
    <section class="results-section fade-on-scroll">
        <h3>{% trans %}Top 20 Players by Scrabble Score{% endtrans %}</h3>

        <!-- Export buttons -->
        <div class="export-buttons">
            <button id="export-divisionPlayersTable-csv"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export players table to CSV format{% endtrans %}">
                <span class="icon" aria-hidden="true">📊</span> {% trans %}Export CSV{% endtrans %}
            </button>
            <button id="export-divisionPlayersTable-json"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export players table to JSON format{% endtrans %}">
                <span class="icon" aria-hidden="true">📄</span> {% trans %}Export JSON{% endtrans %}
            </button>
        </div>

        <div class="table-container">
            <table id="divisionPlayersTable"
                   class="results-table sortable"
                   role="table"
                   aria-label="{% trans %}Top players for {{ division_name }} Division{% endtrans %}">
                <thead>
                    <tr>
                        <th scope="col" data-sort="rank" data-sort-type="number">{% trans %}Rank{% endtrans %}</th>
                        <th scope="col" data-sort="name" data-sort-type="string">{% trans %}Player Name{% endtrans %}</th>
                        <th scope="col" data-sort="team" data-sort-type="string">{% trans %}Team{% endtrans %}</th>
                        <th scope="col" data-sort="score" data-sort-type="number">{% trans %}Score{% endtrans %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in division_players %}
                        <tr data-original-index="{{ loop.index }}">
                            <td data-value="{{ loop.index }}">{{ loop.index }}</td>
                            <td class="player-name" data-value="{{ player.first_name }} {{ player.last_name }}">
                                {{ player.first_name }} {{ player.last_name }}
                            </td>
                            <td class="team-abbrev" data-value="{{ player.team }}">{{ player.team }}</td>
                            <td class="score" data-value="{{ player.score }}">{{ player.score }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </section>

    <!-- Navigation Links -->
    <section class="info-section fade-on-scroll">
        <p>
            <a href="/divisions?lang={{ locale }}">{% trans %}← Back to All Divisions{% endtrans %}</a>
            {% if division_stats.conference %}
                |
                <a href="/conferences/{{ division_stats.conference }}?lang={{ locale }}">
                    {% trans %}View {{ division_stats.conference }} Conference{% endtrans %}
                </a>
            {% endif %}
        </p>
    </section>
{% endblock %}
```

### Step 3: Update divisions.html with Links

Modify `src/nhl_scrabble/web/templates/divisions.html` to link to detail pages:

```html
<!-- Division Standings -->
<section class="results-section">
    <h3>{% trans %}Division Standings by Total Scrabble Score{% endtrans %}</h3>
    <div class="division-grid">
        {% for division, teams in division_standings.items() %}
            <div class="division-card">
                <h4>
                    <a href="/divisions/{{ division }}?lang={{ locale }}" class="division-link">
                        {{ division }}
                    </a>
                </h4>
                <ol>
                    {% for team in teams %}
                        <li>{{ team.name }} ({{ team.total_score }})</li>
                    {% endfor %}
                </ol>
            </div>
        {% endfor %}
    </div>
</section>
```

### Step 4: Add CSS for Division Links

Add styling to `src/nhl_scrabble/web/static/css/style.css`:

```css
/* Division Detail Page (similar to conference) */
.division-link {
    color: var(--heading-color);
    text-decoration: none;
    transition: color 0.3s ease;
}

.division-link:hover {
    color: var(--primary-color);
    text-decoration: underline;
}

/* Division stats card adjustments */
.stat-value[style*="font-size: 1.2rem"] {
    line-height: 1.4;
}
```

### Step 5: Add i18n Translations

Extract and update translations:

```bash
make i18n-extract
make i18n-update
make i18n-compile
```

**New translatable strings**:
- "{division_name} Division"
- "Team standings and top players from the {division_name} Division..."
- "Conference" (stat card label)
- "View {conference} Conference"
- "← Back to All Divisions"

## Implementation Steps

1. **Add dynamic route to app.py**:
   - Open `src/nhl_scrabble/web/app.py`
   - Insert `division_detail_page()` after `divisions_page()` (line 812)
   - Handle division name normalization and validation
   - Filter teams and players by division

2. **Create division_detail.html template**:
   - Create new file `src/nhl_scrabble/web/templates/division_detail.html`
   - Use conference_detail.html as reference (task #048)
   - Add two tables: teams and players
   - Include summary statistics with conference reference

3. **Update divisions.html**:
   - Add links to division detail pages
   - Wrap division name in `<a>` tag
   - Maintain existing card layout

4. **Add CSS styling**:
   - Style division links (hover effect)
   - Ensure dual table layout spacing
   - Copy conference detail styles

5. **Handle edge cases**:
   - Invalid division names (404 error)
   - Empty divisions (should not happen but handle gracefully)
   - URL encoding (spaces in "Atlantic" etc.)

6. **Extract and update translations**:
   ```bash
   make i18n-extract
   make i18n-update
   make i18n-compile
   ```

7. **Test locally**:
   ```bash
   nhl-scrabble web

   # Test URLs:
   # http://localhost:8000/divisions/Atlantic
   # http://localhost:8000/divisions/Metropolitan
   # http://localhost:8000/divisions/Central
   # http://localhost:8000/divisions/Pacific
   # http://localhost:8000/divisions/Invalid (should 404)

   # Test:
   # - All division pages load
   # - Teams filtered correctly
   # - Players filtered correctly
   # - Links from divisions page work
   # - Back link works
   # - Conference link works
   # - Table sorting works
   # - Export buttons work
   # - i18n works
   # - Mobile responsive
   ```

8. **Run automated tests**:
   ```bash
   pytest tests/unit/test_web.py -v
   cd qa/web
   pytest tests/functional/ -v
   pytest tests/visual/ -v
   ```

9. **Update documentation** (if needed)

## Testing Strategy

### Manual Testing

```bash
# Start server
nhl-scrabble web

# Test all four divisions
for div in Atlantic Metropolitan Central Pacific; do
    echo "Testing $div..."
    curl "http://localhost:8000/divisions/$div" | grep -o "<title>.*</title>"
done

# Test invalid division (should 404)
curl -I http://localhost:8000/divisions/Invalid
# Should return: HTTP/1.1 404 Not Found

# Test case insensitivity
curl http://localhost:8000/divisions/atlantic
curl http://localhost:8000/divisions/METROPOLITAN

# Functional tests:
1. Visit /divisions
2. Click "Atlantic" division link
3. Verify team table shows only Atlantic teams
4. Verify players table shows only Atlantic players
5. Verify conference badge shows "Eastern"
6. Click "View Eastern Conference" link (should work)
7. Click "Back to All Divisions" link
8. Repeat for other divisions
9. Test table sorting on both tables
10. Test export buttons
11. Test language switching
12. Test mobile view
```

### Automated Testing

**Playwright Tests** (tests/functional/test_division_detail.py):

```python
import pytest
from playwright.sync_api import Page, expect
import re

@pytest.mark.parametrize("division,expected_conference,expected_teams", [
    ("Atlantic", "Eastern", 8),
    ("Metropolitan", "Eastern", 8),
    ("Central", "Western", 8),
    ("Pacific", "Western", 8),
])
def test_division_page_loads(page: Page, base_url: str, division: str, expected_conference: str, expected_teams: int):
    """Test that division detail page loads with correct data."""
    page.goto(f"{base_url}/divisions/{division}")

    # Check title
    expect(page).to_have_title(re.compile(f"{division} Division"))

    # Check conference badge
    expect(page.locator('.stat-card:has-text("Conference")')).to_contain_text(expected_conference)

    # Check team count
    team_rows = page.locator('#divisionTeamsTable tbody tr')
    expect(team_rows).to_have_count(expected_teams)

def test_invalid_division_returns_404(page: Page, base_url: str):
    """Test that invalid division name returns 404."""
    response = page.goto(f"{base_url}/divisions/Invalid")
    assert response.status == 404

def test_division_players_filtered(page: Page, base_url: str):
    """Test that players are filtered by division."""
    page.goto(f"{base_url}/divisions/Atlantic")

    # Check players table exists
    players_table = page.locator('#divisionPlayersTable')
    expect(players_table).to_be_visible()

    # Should have up to 20 players (could be less for small divisions)
    player_rows = page.locator('#divisionPlayersTable tbody tr')
    count = player_rows.count()
    assert 1 <= count <= 20, f"Expected 1-20 players, got {count}"

def test_division_links_from_main_page(page: Page, base_url: str):
    """Test that links from divisions page work."""
    page.goto(f"{base_url}/divisions")

    # Click Atlantic division link
    page.click('a.division-link:has-text("Atlantic")')

    # Should navigate to detail page
    expect(page).to_have_url(re.compile("/divisions/Atlantic"))
    expect(page).to_have_title(re.compile("Atlantic Division"))

def test_conference_link_works(page: Page, base_url: str):
    """Test that conference link navigates correctly."""
    page.goto(f"{base_url}/divisions/Metropolitan")

    # Click "View Eastern Conference" link
    page.click('a:has-text("View Eastern Conference")')

    # Should navigate to conference detail page
    expect(page).to_have_url(re.compile("/conferences/Eastern"))

def test_back_link_works(page: Page, base_url: str):
    """Test that back link returns to divisions page."""
    page.goto(f"{base_url}/divisions/Central")

    # Click back link
    page.click('a:has-text("Back to All Divisions")')

    # Should return to main divisions page
    expect(page).to_have_url(re.compile("/divisions$"))

def test_both_tables_sortable(page: Page, base_url: str):
    """Test that both tables support sorting."""
    page.goto(f"{base_url}/divisions/Pacific")

    # Sort teams table by total score
    page.click('#divisionTeamsTable th[data-sort="total"]')

    # Sort players table by score
    page.click('#divisionPlayersTable th[data-sort="score"]')

    # Tables should still be visible
    expect(page.locator('#divisionTeamsTable')).to_be_visible()
    expect(page.locator('#divisionPlayersTable')).to_be_visible()

def test_export_buttons_present(page: Page, base_url: str):
    """Test that export buttons are present for both tables."""
    page.goto(f"{base_url}/divisions/Atlantic")

    # Teams export buttons
    expect(page.locator('#export-divisionTeamsTable-csv')).to_be_visible()
    expect(page.locator('#export-divisionTeamsTable-json')).to_be_visible()

    # Players export buttons
    expect(page.locator('#export-divisionPlayersTable-csv')).to_be_visible()
    expect(page.locator('#export-divisionPlayersTable-json')).to_be_visible()
```

### i18n Testing

```bash
# Test in French
curl "http://localhost:8000/divisions/Atlantic?lang=fr_CA" | grep -o "<h2>.*</h2>"

# Test in Swedish
curl "http://localhost:8000/divisions/Central?lang=sv_SE" | grep -o "<h2>.*</h2>"
```

## Acceptance Criteria

- [ ] `/divisions/{division_name}` routes exist and return HTTP 200
- [ ] All 4 division pages work: Atlantic, Metropolitan, Central, Pacific
- [ ] Invalid division names return HTTP 404
- [ ] Division names are case-insensitive
- [ ] Team table displays only teams from specified division
- [ ] Teams table matches layout of main Teams page (sortable columns)
- [ ] Player table displays top 20 players from specified division
- [ ] Players are correctly filtered by division
- [ ] Summary statistics are division-specific
- [ ] Conference badge displays correct conference (Eastern/Western)
- [ ] Export buttons work for both tables (CSV and JSON)
- [ ] Table sorting works on both tables
- [ ] Divisions page includes clickable links to detail pages
- [ ] "Back to All Divisions" link works
- [ ] "View {Conference} Conference" link works
- [ ] i18n works for all supported locales (12 locales)
- [ ] Responsive design works on mobile devices
- [ ] Caching works (uses same cache as other endpoints)
- [ ] No performance regression
- [ ] All automated tests pass
- [ ] QA functional tests pass
- [ ] QA visual regression tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated (if needed)

## Related Files

- `src/nhl_scrabble/web/app.py` - Add new dynamic route
- `src/nhl_scrabble/web/templates/divisions.html` - Add links to detail pages
- `src/nhl_scrabble/web/templates/division_detail.html` - New template (create)
- `src/nhl_scrabble/web/templates/conference_detail.html` - Reference template (task #048)
- `src/nhl_scrabble/web/static/css/style.css` - Add division link styling
- `src/nhl_scrabble/web/static/js/table-sort.js` - Table sorting (already exists)
- `src/nhl_scrabble/web/static/js/export.js` - Export functionality (already exists)
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - Translation files
- `qa/web/tests/functional/` - Add test_division_detail.py
- `qa/web/tests/visual/` - Add visual regression tests

## Dependencies

**Directly depends on**:
- Task #048 (Conference detail pages) - Provides pattern and reference implementation

**No blocking dependencies**, but related to:
- Web interface infrastructure (already implemented)
- Division data (already available)
- Player division association
- i18n system (already implemented)
- Table sorting/export functionality (already implemented)

**Data requirements**:
- Players need division association (via team lookup)
- Division names must be consistent: "Atlantic", "Metropolitan", "Central", "Pacific"

## Additional Notes

### NHL Divisions

**Eastern Conference**:
- Atlantic Division (8 teams)
- Metropolitan Division (8 teams)

**Western Conference**:
- Central Division (8 teams)
- Pacific Division (8 teams)

**Total**: 4 divisions, 32 teams

### URL Routing

**FastAPI path parameters**:
- `{division_name}` captures any string
- Normalize in route: `.strip().title()`
- Validate against available divisions
- Return 404 if not found

**Example URLs**:
- `/divisions/Atlantic`
- `/divisions/Metropolitan`
- `/divisions/Central`
- `/divisions/Pacific`
- `/divisions/atlantic` (normalized to "Atlantic")

### Data Filtering

**Player filtering approach** (via team lookup):
```python
# Get all team abbreviations in this division
division_team_abbrevs = {team["abbrev"] for team in division_teams}

# Filter players by team membership
division_players = [
    player for player in all_players
    if player["team"] in division_team_abbrevs
][:20]
```

This ensures accurate filtering based on team membership.

### Design Consistency

**Follow conference detail pattern** (task #048):
- Same table structure
- Same export buttons
- Same sortable table classes
- Same responsive design
- Similar navigation links

**Additional elements specific to divisions**:
- Conference badge (stat card showing which conference)
- Link to parent conference detail page
- Smaller team count (8 vs 16)

### Performance Considerations

**Caching**:
- Use existing cache (1 hour TTL)
- Increase `top_players` to 100+ to ensure 20+ per division
- Filtering happens in Python (fast, no API calls)

**Data Volume**:
- 8 teams per division (vs 16 per conference)
- 20 players per division
- Minimal HTML (~12-15 KB per page)
- Four division pages total

### Cross-Navigation

**Navigation paths**:
1. Divisions page → Division detail page
2. Division detail page → Conference detail page
3. Division detail page → Back to divisions page
4. Conference detail page → Division detail pages (future enhancement)

### Future Enhancements

**Phase 2 Ideas** (not in this task):
- Add breadcrumb navigation: Home > Divisions > Atlantic
- Add division comparison view
- Add historical division standings
- Add playoff implications for divisions
- Add rivalry indicators within divisions
- Add division trophy/award information

### Testing in TEST_MODE

**Visual tests**:
- Set `NHL_SCRABBLE_TEST_MODE=1`
- Use fixture data
- Each division should have consistent teams
- Deterministic for visual regression tests

### Accessibility

**WCAG 2.1 Compliance**:
- Two separate tables with proper ARIA labels
- Distinct table IDs for export buttons
- Navigation links have descriptive text
- Division name in heading for context
- Conference badge clearly labeled
- Keyboard navigation between tables

### Error Handling

**404 Scenarios**:
- Division name not found
- Typos in URL
- Non-existent division

**Empty Data Scenarios**:
- Division with no teams (shouldn't happen)
- Division with no players (handle gracefully)

### Mobile Responsiveness

**Two tables stacked**:
- Teams table first (fewer columns than conference version)
- Players table below
- Both tables responsive (horizontal scroll if needed)
- Conference badge displays well on mobile

### SEO Considerations

**Dynamic meta tags**:
- Page title: "{Division} Division Standings"
- Meta description: Division-specific
- Open Graph tags with division name
- Canonical URL for each division

### CSS Reuse

Most CSS from conference detail pages can be reused:
- `.division-link` (new, similar to `.conference-link`)
- Dual table layout (reuse from conference)
- Export buttons (reuse)
- Navigation links (reuse)

## Implementation Notes

*To be filled during implementation:*
- Actual division names from API
- Number of teams per division
- Any data structure adjustments needed
- Translation completion status
- QA test results
- Performance metrics
- Date of implementation completion
