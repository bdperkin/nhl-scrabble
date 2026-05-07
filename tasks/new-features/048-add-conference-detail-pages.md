# Add Conference Detail Pages with Team Standings and Top Players

**GitHub Issue**: #541 - https://github.com/bdperkin/nhl-scrabble/issues/541

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Add dynamic conference detail pages accessible via `/conferences/{CONFERENCE_NAME}` URL paths. Each page will display a team standings table for that specific conference (mimicking the main Teams page layout) followed by the Top 20 Players by Scrabble Score from that conference. Update the Conferences page to link to these detail pages.

## Current State

**Conferences Page** (`/conferences`):
- Shows conference standings grouped by conference
- Uses card-based layout with division-grid
- Each conference displayed in a separate card
- No links to conference detail pages

**Data Available**:
- `conference_standings` dict: `{conference_name: [teams]}`
- `team_standings` list: All teams with conference property
- `top_players` list: All players with conference property
- NHL has 2 conferences: "Eastern" and "Western"

**Existing Detail Pages**:
- None currently - this will be the first detail page pattern
- Teams page shows all teams in table format
- Divisions/Conferences pages show grouped cards

## Proposed Solution

### Step 1: Add Dynamic Conference Route

Add a new `/conferences/{conference_name}` route in `app.py`:

```python
@app.get("/conferences/{conference_name}", response_class=HTMLResponse)
async def conference_detail_page(
    request: Request,
    conference_name: str,
) -> HTMLResponse:
    """Serve a conference detail page with teams and top players.

    Args:
        request: FastAPI request object
        conference_name: Conference name (Eastern, Western)

    Returns:
        Rendered conference_detail.html template with filtered data

    Raises:
        HTTPException: If conference not found or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        # Increase top_players to ensure we get 20+ per conference
        analysis_request = AnalysisRequest(top_players=100, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Normalize conference name for comparison
        conference_normalized = conference_name.strip().title()

        # Validate conference exists
        if conference_normalized not in data["conference_standings"]:
            raise HTTPException(
                status_code=404,
                detail=f"Conference '{conference_name}' not found",
            )

        # Filter teams for this conference
        conference_teams = [
            team for team in data["team_standings"]
            if team["conference"] == conference_normalized
        ]

        # Filter top players for this conference
        conference_players = [
            player for player in data["top_players"]
            if player.get("conference") == conference_normalized
               or any(t["conference"] == conference_normalized
                      for t in data["team_standings"]
                      if t["abbrev"] == player["team"])
        ][:20]  # Top 20 players from this conference

        # Calculate conference-specific stats
        conference_stats = {
            "total_teams": len(conference_teams),
            "total_players": sum(t["player_count"] for t in conference_teams),
            "highest_team_score": conference_teams[0]["total_score"] if conference_teams else 0,
            "highest_team": conference_teams[0]["abbrev"] if conference_teams else None,
            "highest_team_name": conference_teams[0]["name"] if conference_teams else None,
            "highest_player_score": conference_players[0]["score"] if conference_players else 0,
            "highest_player_name": conference_players[0]["full_name"] if conference_players else None,
        }

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "conference_name": conference_normalized,
                "conference_teams": conference_teams,
                "conference_players": conference_players,
                "conference_stats": conference_stats,
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="conference_detail.html",
            context=context,
        )

    except NHLApiError as e:
        logger.error("Failed to fetch conference detail data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
```

**Location**: Insert after `conferences_page()` function (around line 862)

### Step 2: Create conference_detail.html Template

Create `src/nhl_scrabble/web/templates/conference_detail.html`:

```html
{% extends "base.html" %}

{% block title %}{% trans %}NHL Scrabble Analyzer - {{ conference_name }} Conference{% endtrans %}{% endblock %}

{% block og_title %}{{ conference_name }} {% trans %}Conference Standings{% endtrans %}{% endblock %}
{% block twitter_title %}{{ conference_name }} {% trans %}Conference Standings{% endtrans %}{% endblock %}

{% block content %}
    <div class="page-header fade-on-scroll">
        <h2>{{ conference_name }} {% trans %}Conference{% endtrans %}</h2>
        <p class="page-description">
            {% trans %}Team standings and top players from the {{ conference_name }} Conference ranked by Scrabble score.{% endtrans %}
        </p>
        <p class="timestamp">
            {% trans %}Data as of{% endtrans %}: {{ timestamp_date }} {{ timestamp_time }}
        </p>
    </div>

    <!-- Conference Summary Statistics -->
    <div class="stats-summary fade-on-scroll">
        <div class="stat-card">
            <h4>{% trans %}Total Teams{% endtrans %}</h4>
            <p class="stat-value">{{ conference_stats.total_teams }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Top Team{% endtrans %}</h4>
            <p class="stat-value">{{ conference_stats.highest_team_score }}</p>
            <p class="stat-detail">{{ conference_stats.highest_team }} ({{ conference_stats.highest_team_name }})</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Total Players{% endtrans %}</h4>
            <p class="stat-value">{{ conference_stats.total_players }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Highest Player{% endtrans %}</h4>
            <p class="stat-value">{{ conference_stats.highest_player_score }}</p>
            <p class="stat-detail">{{ conference_stats.highest_player_name }}</p>
        </div>
    </div>

    <!-- Team Standings Table -->
    <section class="results-section fade-on-scroll">
        <h3>{% trans %}Team Standings by Total Scrabble Score{% endtrans %}</h3>

        <!-- Export buttons -->
        <div class="export-buttons">
            <button id="export-conferenceTeamsTable-csv"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export team standings table to CSV format{% endtrans %}">
                <span class="icon" aria-hidden="true">📊</span> {% trans %}Export CSV{% endtrans %}
            </button>
            <button id="export-conferenceTeamsTable-json"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export team standings table to JSON format{% endtrans %}">
                <span class="icon" aria-hidden="true">📄</span> {% trans %}Export JSON{% endtrans %}
            </button>
        </div>

        <div class="table-container">
            <table id="conferenceTeamsTable"
                   class="results-table standings-table sortable"
                   role="table"
                   aria-label="{% trans %}Team standings for {{ conference_name }} Conference{% endtrans %}">
                <thead>
                    <tr>
                        <th scope="col" data-sort="rank" data-sort-type="number">{% trans %}Rank{% endtrans %}</th>
                        <th scope="col" data-sort="team" data-sort-type="string">{% trans %}Team{% endtrans %}</th>
                        <th scope="col" data-sort="division" data-sort-type="string">{% trans %}Division{% endtrans %}</th>
                        <th scope="col" data-sort="total" data-sort-type="number">{% trans %}Total Score{% endtrans %}</th>
                        <th scope="col" data-sort="avg" data-sort-type="number">{% trans %}Avg Score{% endtrans %}</th>
                        <th scope="col" data-sort="players" data-sort-type="number">{% trans %}Players{% endtrans %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for team in conference_teams %}
                        <tr data-original-index="{{ loop.index }}">
                            <td data-value="{{ loop.index }}">{{ loop.index }}</td>
                            <td class="team-name" data-value="{{ team.name }}">{{ team.name }}</td>
                            <td data-value="{{ team.division }}">{{ team.division }}</td>
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
            <button id="export-conferencePlayersTable-csv"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export players table to CSV format{% endtrans %}">
                <span class="icon" aria-hidden="true">📊</span> {% trans %}Export CSV{% endtrans %}
            </button>
            <button id="export-conferencePlayersTable-json"
                    class="btn btn-secondary btn-sm"
                    aria-label="{% trans %}Export players table to JSON format{% endtrans %}">
                <span class="icon" aria-hidden="true">📄</span> {% trans %}Export JSON{% endtrans %}
            </button>
        </div>

        <div class="table-container">
            <table id="conferencePlayersTable"
                   class="results-table sortable"
                   role="table"
                   aria-label="{% trans %}Top players for {{ conference_name }} Conference{% endtrans %}">
                <thead>
                    <tr>
                        <th scope="col" data-sort="rank" data-sort-type="number">{% trans %}Rank{% endtrans %}</th>
                        <th scope="col" data-sort="name" data-sort-type="string">{% trans %}Player Name{% endtrans %}</th>
                        <th scope="col" data-sort="team" data-sort-type="string">{% trans %}Team{% endtrans %}</th>
                        <th scope="col" data-sort="score" data-sort-type="number">{% trans %}Score{% endtrans %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for player in conference_players %}
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
            <a href="/conferences?lang={{ locale }}">{% trans %}← Back to All Conferences{% endtrans %}</a>
        </p>
    </section>
{% endblock %}
```

### Step 3: Update conferences.html with Links

Modify `src/nhl_scrabble/web/templates/conferences.html` to link to detail pages:

```html
<!-- Conference Standings -->
<section class="results-section">
    <h3>{% trans %}Conference Standings by Total Scrabble Score{% endtrans %}</h3>
    <div class="division-grid">
        {% for conference, teams in conference_standings.items() %}
            <div class="division-card">
                <h4>
                    <a href="/conferences/{{ conference }}?lang={{ locale }}" class="conference-link">
                        {{ conference }}
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

### Step 4: Add CSS for Conference Links

Add styling to `src/nhl_scrabble/web/static/css/style.css`:

```css
/* Conference Detail Page */
.conference-link {
    color: var(--heading-color);
    text-decoration: none;
    transition: color 0.3s ease;
}

.conference-link:hover {
    color: var(--primary-color);
    text-decoration: underline;
}

/* Dual table layout on conference detail pages */
.results-section + .results-section {
    margin-top: 3rem;
}
```

### Step 5: Handle Player Conference Data

Ensure players have conference data. Modify filtering logic if needed:

```python
# In conference_detail_page route, alternative player filtering:
conference_team_abbrevs = {team["abbrev"] for team in conference_teams}
conference_players = [
    player for player in data["top_players"]
    if player["team"] in conference_team_abbrevs
][:20]
```

### Step 6: Add i18n Translations

Extract and update translations:

```bash
make i18n-extract
make i18n-update
make i18n-compile
```

**New translatable strings**:
- "{conference_name} Conference"
- "Team standings and top players from the {conference_name} Conference..."
- "Top 20 Players by Scrabble Score"
- "← Back to All Conferences"

## Implementation Steps

1. **Add dynamic route to app.py**:
   - Open `src/nhl_scrabble/web/app.py`
   - Insert `conference_detail_page()` after `conferences_page()` (line 862)
   - Handle conference name normalization and validation
   - Filter teams and players by conference

2. **Create conference_detail.html template**:
   - Create new file `src/nhl_scrabble/web/templates/conference_detail.html`
   - Use teams.html table structure as reference
   - Add two tables: teams and players
   - Include summary statistics

3. **Update conferences.html**:
   - Add links to conference detail pages
   - Wrap conference name in `<a>` tag
   - Maintain existing card layout

4. **Add CSS styling**:
   - Style conference links (hover effect)
   - Ensure dual table layout spacing

5. **Handle edge cases**:
   - Invalid conference names (404 error)
   - Empty conferences (should not happen but handle gracefully)
   - URL encoding (spaces in conference names if any)

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
   # http://localhost:8000/conferences/Eastern
   # http://localhost:8000/conferences/Western
   # http://localhost:8000/conferences/Invalid (should 404)

   # Test:
   # - Conference detail pages load
   # - Teams filtered correctly by conference
   # - Players filtered correctly by conference
   # - Links from conferences page work
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

# Test Eastern Conference
curl http://localhost:8000/conferences/Eastern | grep -o "<title>.*</title>"
# Should show: NHL Scrabble Analyzer - Eastern Conference

# Test Western Conference
curl http://localhost:8000/conferences/Western | grep -o "<title>.*</title>"
# Should show: NHL Scrabble Analyzer - Western Conference

# Test invalid conference (should 404)
curl -I http://localhost:8000/conferences/Invalid
# Should return: HTTP/1.1 404 Not Found

# Test case insensitivity
curl http://localhost:8000/conferences/eastern
curl http://localhost:8000/conferences/WESTERN

# Functional tests:
1. Visit /conferences
2. Click "Eastern" conference link
3. Verify team table shows only Eastern teams
4. Verify players table shows only Eastern players
5. Verify stats are conference-specific
6. Click "Back to All Conferences" link
7. Repeat for Western conference
8. Test table sorting on both tables
9. Test export buttons
10. Test language switching
11. Test mobile view
```

### Automated Testing

**Playwright Tests** (tests/functional/test_conference_detail.py):

```python
import pytest
from playwright.sync_api import Page, expect

def test_eastern_conference_page_loads(page: Page, base_url: str):
    """Test that Eastern conference detail page loads."""
    page.goto(f"{base_url}/conferences/Eastern")
    expect(page).to_have_title(re.compile("Eastern Conference"))

def test_western_conference_page_loads(page: Page, base_url: str):
    """Test that Western conference detail page loads."""
    page.goto(f"{base_url}/conferences/Western")
    expect(page).to_have_title(re.compile("Western Conference"))

def test_invalid_conference_returns_404(page: Page, base_url: str):
    """Test that invalid conference name returns 404."""
    response = page.goto(f"{base_url}/conferences/Invalid")
    assert response.status == 404

def test_conference_teams_filtered(page: Page, base_url: str):
    """Test that teams are filtered by conference."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Check teams table exists
    teams_table = page.locator('#conferenceTeamsTable')
    expect(teams_table).to_be_visible()

    # Count rows (should be 16 teams in Eastern)
    team_rows = page.locator('#conferenceTeamsTable tbody tr')
    count = team_rows.count()
    assert count == 16, f"Expected 16 Eastern teams, got {count}"

def test_conference_players_filtered(page: Page, base_url: str):
    """Test that players are filtered by conference."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Check players table exists
    players_table = page.locator('#conferencePlayersTable')
    expect(players_table).to_be_visible()

    # Should have 20 players
    player_rows = page.locator('#conferencePlayersTable tbody tr')
    expect(player_rows).to_have_count(20)

def test_conference_links_from_main_page(page: Page, base_url: str):
    """Test that links from conferences page work."""
    page.goto(f"{base_url}/conferences")

    # Click Eastern conference link
    page.click('a.conference-link:has-text("Eastern")')

    # Should navigate to detail page
    expect(page).to_have_url(re.compile("/conferences/Eastern"))
    expect(page).to_have_title(re.compile("Eastern Conference"))

def test_back_link_works(page: Page, base_url: str):
    """Test that back link returns to conferences page."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Click back link
    page.click('a:has-text("Back to All Conferences")')

    # Should return to main conferences page
    expect(page).to_have_url(re.compile("/conferences$"))

def test_both_tables_sortable(page: Page, base_url: str):
    """Test that both tables support sorting."""
    page.goto(f"{base_url}/conferences/Eastern")

    # Sort teams table by total score
    page.click('#conferenceTeamsTable th[data-sort="total"]')

    # Sort players table by score
    page.click('#conferencePlayersTable th[data-sort="score"]')

    # Tables should still be visible
    expect(page.locator('#conferenceTeamsTable')).to_be_visible()
    expect(page.locator('#conferencePlayersTable')).to_be_visible()

def test_export_buttons_present(page: Page, base_url: str):
    """Test that export buttons are present for both tables."""
    page.goto(f"{base_url}/conferences/Western")

    # Teams export buttons
    expect(page.locator('#export-conferenceTeamsTable-csv')).to_be_visible()
    expect(page.locator('#export-conferenceTeamsTable-json')).to_be_visible()

    # Players export buttons
    expect(page.locator('#export-conferencePlayersTable-csv')).to_be_visible()
    expect(page.locator('#export-conferencePlayersTable-json')).to_be_visible()
```

### i18n Testing

```bash
# Test in French
curl "http://localhost:8000/conferences/Eastern?lang=fr_CA" | grep -o "<h2>.*</h2>"

# Test in Swedish
curl "http://localhost:8000/conferences/Western?lang=sv_SE" | grep -o "<h2>.*</h2>"
```

## Acceptance Criteria

- [ ] `/conferences/{conference_name}` routes exist and return HTTP 200
- [ ] Both "Eastern" and "Western" conference pages work
- [ ] Invalid conference names return HTTP 404
- [ ] Conference names are case-insensitive (eastern, Eastern, EASTERN all work)
- [ ] Team table displays only teams from specified conference
- [ ] Teams table matches layout of main Teams page (sortable columns)
- [ ] Player table displays top 20 players from specified conference
- [ ] Players are correctly filtered by conference
- [ ] Summary statistics are conference-specific
- [ ] Export buttons work for both tables (CSV and JSON)
- [ ] Table sorting works on both tables
- [ ] Conferences page includes clickable links to detail pages
- [ ] "Back to All Conferences" link works
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
- `src/nhl_scrabble/web/templates/conferences.html` - Add links to detail pages
- `src/nhl_scrabble/web/templates/conference_detail.html` - New template (create)
- `src/nhl_scrabble/web/templates/teams.html` - Reference for table layout
- `src/nhl_scrabble/web/static/css/style.css` - Add conference link styling
- `src/nhl_scrabble/web/static/js/table-sort.js` - Table sorting (already exists)
- `src/nhl_scrabble/web/static/js/export.js` - Export functionality (already exists)
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - Translation files
- `qa/web/tests/functional/` - Add test_conference_detail.py
- `qa/web/tests/visual/` - Add visual regression tests

## Dependencies

**No blocking dependencies**, but related to:
- Web interface infrastructure (already implemented)
- Conference data (already available)
- Player conference association
- i18n system (already implemented)
- Table sorting/export functionality (already implemented)

**Data requirements**:
- Players need conference association (either direct or via team lookup)
- Conference names must be consistent ("Eastern", "Western")

## Additional Notes

### Conference Names

**NHL Conferences**:
- Eastern Conference (16 teams)
- Western Conference (16 teams)

**URL Encoding**:
- No spaces in conference names, so no encoding issues
- Handle case-insensitivity: "Eastern", "eastern", "EASTERN" all valid

### Data Filtering

**Two approaches for player filtering**:

1. **Direct conference property** (if available):
   ```python
   players = [p for p in all_players if p.get("conference") == conference_name]
   ```

2. **Lookup via team** (more reliable):
   ```python
   conference_teams = {t["abbrev"] for t in teams if t["conference"] == conference_name}
   players = [p for p in all_players if p["team"] in conference_teams]
   ```

Recommend approach #2 for accuracy.

### Performance Considerations

**Caching**:
- Use existing cache (1 hour TTL)
- Increase `top_players` to 100+ to ensure 20+ per conference
- Filtering happens in Python (fast, no API calls)

**Data Volume**:
- 16 teams per conference
- 20 players per conference
- Minimal HTML (~15-20 KB per page)
- Two tables with sorting: moderate client-side processing

### URL Routing

**FastAPI path parameters**:
- `{conference_name}` captures any string
- Normalize in route: `.strip().title()`
- Validate against available conferences
- Return 404 if not found

**Example URLs**:
- `/conferences/Eastern`
- `/conferences/Western`
- `/conferences/eastern` (normalized to "Eastern")

### Design Consistency

**Follow teams.html layout**:
- Same table columns (Rank, Team, Division, Total, Avg, Players)
- Same export buttons
- Same sortable table classes
- Same responsive design

**Additional elements**:
- Conference-specific heading
- Conference-specific stats
- Top 20 players section below teams
- Back navigation link

### Future Enhancements

**Phase 2 Ideas** (not in this task):
- Add division detail pages (`/divisions/{DIVISION_NAME}`)
- Add team detail pages (`/teams/{TEAM_ABBREV}`)
- Add breadcrumb navigation
- Add comparison between conferences
- Add historical conference standings
- Add playoff seeding visualization

### Testing in TEST_MODE

**Visual tests**:
- Set `NHL_SCRABBLE_TEST_MODE=1`
- Use fixture data
- Eastern conference should have consistent teams
- Western conference should have consistent teams
- Deterministic for visual regression tests

### Accessibility

**WCAG 2.1 Compliance**:
- Two separate tables with proper ARIA labels
- Distinct table IDs for export buttons
- Navigation links have descriptive text
- Conference name in heading for context
- Keyboard navigation between tables

### Error Handling

**404 Scenarios**:
- Conference name not found
- Typos in URL
- Non-existent conference

**Empty Data Scenarios**:
- Conference with no teams (shouldn't happen)
- Conference with no players (handle gracefully)

### Mobile Responsiveness

**Two tables stacked**:
- Teams table first
- Players table below
- Both tables responsive (horizontal scroll if needed)
- Export buttons wrap on small screens

### SEO Considerations

**Dynamic meta tags**:
- Page title: "{Conference} Conference Standings"
- Meta description: Conference-specific
- Open Graph tags with conference name
- Canonical URL for each conference

## Implementation Notes

*To be filled during implementation:*
- Player conference association method used
- Actual conference names from API
- Number of teams per conference
- Any data structure adjustments needed
- Translation completion status
- QA test results
- Performance metrics
- Date of implementation completion
