# Add League Menu Item and League Standings Page

**GitHub Issue**: #540 - https://github.com/bdperkin/nhl-scrabble/issues/540

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-5 hours

## Description

Add a new "League" navigation menu item between "Conferences" and "Playoffs" in the web interface. The new page should display all NHL teams in a single league-wide standings list, mimicking the visual design of the Division/Conference pages (card-based layout with ordered list) but without grouping teams into sub-sections.

## Current State

**Navigation Structure** (base.html lines 64-97):
- Home (/)
- Players (/players) - Added in task #046
- Teams (/teams)
- Divisions (/divisions)
- Conferences (/conferences)
- Playoffs (/playoffs)
- Stats (/stats)
- API Docs, Documentation, GitHub

**Team Standings Display**:
- **Teams page** (`/teams`) - Shows all teams in sortable table format with columns: Rank, Team, Division, Conference, Total Score, Avg Score, Players
- **Divisions page** (`/divisions`) - Shows teams grouped by division in card format (division-grid with division-card elements containing ordered lists)
- **Conferences page** (`/conferences`) - Shows teams grouped by conference in card format (same visual style as divisions)

**FastAPI Route Structure** (app.py):
- `GET /` - Home page (index.html)
- `GET /players` - Players ranking page
- `GET /teams` - Teams standings page (table format)
- `GET /divisions` - Divisions standings page (grouped cards)
- `GET /conferences` - Conferences standings page (grouped cards)
- `GET /playoffs` - Playoff bracket page
- `GET /stats` - Statistics page with charts
- `POST /api/analyze` - API endpoint (returns team_standings data)

**Data Available**:
- `/api/analyze` endpoint already fetches team standings data
- Returns team objects sorted by total_score
- Data includes: abbrev, name, total_score, avg_score, player_count, division, conference

## Proposed Solution

### Step 1: Create New Route in app.py

Add a new `/league` route similar to existing standings pages:

```python
@app.get("/league", response_class=HTMLResponse)
async def league_page(request: Request) -> HTMLResponse:
    """Serve the league standings page with data.

    Args:
        request: FastAPI request object

    Returns:
        Rendered league.html template with league-wide standings

    Raises:
        HTTPException: If templates not configured or analysis fails
    """
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not configured")

    try:
        # Fetch analysis data with caching enabled
        analysis_request = AnalysisRequest(top_players=20, top_team_players=5, use_cache=True)
        data = await analyze_post(analysis_request)

        # Format timestamp for display
        timestamp_str = data["timestamp"]
        timestamp_dt = datetime.fromisoformat(timestamp_str)
        timestamp_date = timestamp_dt.strftime("%B %d, %Y")
        timestamp_time = timestamp_dt.strftime("%I:%M %p UTC")

        context = setup_template_locale(request)
        context.update(
            {
                "team_standings": data["team_standings"],
                "stats": data["stats"],
                "timestamp_date": timestamp_date,
                "timestamp_time": timestamp_time,
            },
        )
        return templates.TemplateResponse(
            request=request,
            name="league.html",
            context=context,
        )
    except NHLApiError as e:
        logger.error("Failed to fetch league data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch NHL data: {e!s}",
        ) from e
```

**Location**: Insert after `conferences_page()` function (around line 862) and before `/playoffs` route

### Step 2: Create league.html Template

Create `src/nhl_scrabble/web/templates/league.html`:

```html
{% extends "base.html" %}

{% block title %}{% trans %}NHL Scrabble Analyzer - League Standings{% endtrans %}{% endblock %}

{% block og_title %}{% trans %}NHL League Standings by Scrabble Score{% endtrans %}{% endblock %}
{% block twitter_title %}{% trans %}NHL League Standings by Scrabble Score{% endtrans %}{% endblock %}

{% block content %}
    <div class="page-header fade-on-scroll">
        <h2>{% trans %}League Standings by Total Scrabble Score{% endtrans %}</h2>
        <p class="page-description">
            {% trans %}Complete NHL standings ranked by total Scrabble score across all teams in the league.{% endtrans %}
        </p>
        <p class="timestamp">
            {% trans %}Data as of{% endtrans %}: {{ timestamp_date }} {{ timestamp_time }}
        </p>
    </div>

    <!-- Summary Statistics -->
    <div class="stats-summary fade-on-scroll">
        <div class="stat-card">
            <h4>{% trans %}Total Teams{% endtrans %}</h4>
            <p class="stat-value">{{ stats.total_teams }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Top Team{% endtrans %}</h4>
            <p class="stat-value">{{ stats.highest_team_score }}</p>
            <p class="stat-detail">{{ stats.highest_team }} ({{ stats.highest_team_name }})</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Lowest Team{% endtrans %}</h4>
            <p class="stat-value">{{ stats.lowest_team }}</p>
            <p class="stat-detail">{{ stats.lowest_team_name }}</p>
        </div>
        <div class="stat-card">
            <h4>{% trans %}Total Players{% endtrans %}</h4>
            <p class="stat-value">{{ stats.total_players }}</p>
        </div>
    </div>

    <!-- League Standings -->
    <section class="results-section fade-on-scroll">
        <h3>{% trans %}League Standings{% endtrans %}</h3>
        <div class="division-grid">
            <div class="division-card league-card">
                <h4>{% trans %}National Hockey League{% endtrans %}</h4>
                <ol class="league-standings-list">
                    {% for team in team_standings %}
                        <li class="league-team-item">
                            <span class="team-rank">{{ loop.index }}.</span>
                            <span class="team-name">{{ team.name }}</span>
                            <span class="team-details">
                                ({{ team.abbrev }} - {{ team.division }})
                            </span>
                            <span class="team-score">{{ team.total_score }}</span>
                        </li>
                    {% endfor %}
                </ol>
            </div>
        </div>
    </section>

    <!-- Additional Info Section -->
    <section class="info-section fade-on-scroll">
        <h3>{% trans %}About League Standings{% endtrans %}</h3>
        <p>
            {% trans %}Teams are ranked by their total Scrabble score, calculated by summing the Scrabble letter values of all players' names on each roster. This league-wide view shows the complete standings without division or conference groupings.{% endtrans %}
        </p>
        <p>
            {% trans %}For grouped standings, see:{% endtrans %}
            <a href="/divisions?lang={{ locale }}">{% trans %}Division Standings{% endtrans %}</a> |
            <a href="/conferences?lang={{ locale }}">{% trans %}Conference Standings{% endtrans %}</a>
        </p>
    </section>
{% endblock %}
```

### Step 3: Update Navigation in base.html

Modify navigation menu to insert "League" between "Conferences" and "Playoffs":

```html
<!-- Navigation menu -->
<nav id="navMenu" class="main-nav" aria-label="{% trans %}Main navigation{% endtrans %}">
    <ul>
        <li>
            <a href="/?lang={{ locale }}">{% trans %}Home{% endtrans %}</a>
        </li>
        <li>
            <a href="/players?lang={{ locale }}">{% trans %}Players{% endtrans %}</a>
        </li>
        <li>
            <a href="/teams?lang={{ locale }}">{% trans %}Teams{% endtrans %}</a>
        </li>
        <li>
            <a href="/divisions?lang={{ locale }}">{% trans %}Divisions{% endtrans %}</a>
        </li>
        <li>
            <a href="/conferences?lang={{ locale }}">{% trans %}Conferences{% endtrans %}</a>
        </li>
        <li>
            <a href="/league?lang={{ locale }}">{% trans %}League{% endtrans %}</a>
        </li>
        <li>
            <a href="/playoffs?lang={{ locale }}">{% trans %}Playoffs{% endtrans %}</a>
        </li>
        <!-- Rest of navigation unchanged -->
    </ul>
</nav>
```

**Location**: base.html lines 64-97

### Step 4: Add Custom CSS (Optional)

Add league-specific styling to `src/nhl_scrabble/web/static/css/style.css`:

```css
/* League Standings Specific Styles */
.league-card {
    min-width: 100%;
    max-width: 100%;
}

.league-standings-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.league-team-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    gap: 1rem;
}

.league-team-item:last-child {
    border-bottom: none;
}

.league-team-item:hover {
    background-color: var(--hover-bg);
}

.team-rank {
    font-weight: bold;
    color: var(--primary-color);
    min-width: 2rem;
}

.team-name {
    font-weight: 600;
    flex-grow: 1;
}

.team-details {
    color: var(--muted-text);
    font-size: 0.9rem;
}

.team-score {
    font-weight: bold;
    color: var(--accent-color);
    min-width: 4rem;
    text-align: right;
}

.info-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background-color: var(--card-bg);
    border-radius: var(--border-radius);
}

.info-section h3 {
    margin-top: 0;
}

.info-section a {
    color: var(--link-color);
    text-decoration: none;
}

.info-section a:hover {
    text-decoration: underline;
}
```

### Step 5: Add i18n Translations

Extract new translatable strings and update all locale files:

```bash
# Extract new strings
make i18n-extract

# Update existing translations
make i18n-update

# Compile translations
make i18n-compile
```

**New translatable strings**:
- "League" (navigation)
- "NHL League Standings by Scrabble Score" (page title)
- "League Standings by Total Scrabble Score" (heading)
- "Complete NHL standings ranked by total Scrabble score..." (description)
- "League Standings" (section header)
- "National Hockey League" (card title)
- "About League Standings" (info section)
- Related explanatory text

## Implementation Steps

1. **Create league.html template**:
   ```bash
   # Create new template file
   touch src/nhl_scrabble/web/templates/league.html
   # Add content from proposed solution above
   ```

2. **Add route to app.py**:
   - Open `src/nhl_scrabble/web/app.py`
   - Insert `league_page()` function after `conferences_page()` (around line 862)
   - Use same data structure as other standings pages

3. **Update navigation in base.html**:
   - Open `src/nhl_scrabble/web/templates/base.html`
   - Insert League menu item at line 79 (between Conferences and Playoffs)
   - Add `{% trans %}League{% endtrans %}` for i18n

4. **Add optional CSS styling**:
   - Open `src/nhl_scrabble/web/static/css/style.css`
   - Add league-specific styles for better presentation
   - Style the league-team-item elements for readability

5. **Extract and update translations**:
   ```bash
   make i18n-extract    # Extract new strings to messages.pot
   make i18n-update     # Update all .po files
   ```

6. **Translate new strings** in all locale files:
   - `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po`
   - Add translations for "League" and other new strings
   - Minimum: en_US, en_CA, fr_CA, sv_SE (primary locales)

7. **Compile translations**:
   ```bash
   make i18n-compile    # Generate .mo files
   ```

8. **Test locally**:
   ```bash
   # Start web server
   nhl-scrabble web

   # Visit in browser
   # http://localhost:8000/league

   # Test:
   # - Navigation menu shows League item
   # - League page loads with data
   # - All teams shown in single list
   # - Stats cards display correctly
   # - i18n works (change language selector)
   # - Mobile navigation works
   # - Responsive design works
   ```

9. **Run automated tests**:
   ```bash
   # Unit tests (if any route tests exist)
   pytest tests/unit/test_web.py -v

   # QA web tests
   cd qa/web
   pytest tests/functional/ -v
   pytest tests/visual/ -v
   ```

10. **Update documentation** (if needed):
    - Update web interface screenshots
    - Update navigation documentation

## Testing Strategy

### Manual Testing

**Functional Tests**:
```bash
# Start server
nhl-scrabble web

# Test cases:
1. Navigate to http://localhost:8000/
2. Click "League" in navigation menu
3. Verify league page loads with single standings card
4. Verify all teams displayed in ordered list
5. Verify team details shown (name, abbrev, division, score)
6. Verify stats cards display correctly
7. Verify links to Divisions/Conferences pages work
8. Change language selector - verify translations
9. Test mobile view (responsive design)
10. Test with different browsers (Chrome, Firefox, Safari)
```

**i18n Testing**:
```bash
# Test each locale
for locale in en_US en_CA fr_CA sv_SE fi_FI cs_CZ de_DE de_CH it_CH sk_SK ru_RU lv_LV; do
    echo "Testing locale: $locale"
    curl "http://localhost:8000/league?lang=$locale" | grep -o "<title>.*</title>"
done
```

### Automated Testing

**QA Web Tests**:
```bash
# Functional test for new page
cd qa/web
pytest tests/functional/test_league_page.py -v

# Visual regression test
pytest tests/visual/test_league_page.py --browser chromium -v
```

**Example Playwright Test** (tests/functional/test_league_page.py):
```python
import pytest
from playwright.sync_api import Page, expect

def test_league_page_loads(page: Page, base_url: str):
    """Test that league page loads successfully."""
    page.goto(f"{base_url}/league")
    expect(page).to_have_title("NHL Scrabble Analyzer - League Standings")

def test_league_navigation_exists(page: Page, base_url: str):
    """Test that League menu item exists in navigation."""
    page.goto(base_url)
    league_link = page.locator('nav a:has-text("League")')
    expect(league_link).to_be_visible()

def test_league_all_teams_displayed(page: Page, base_url: str):
    """Test that all teams are displayed in league standings."""
    page.goto(f"{base_url}/league")

    # Check that league card exists
    league_card = page.locator('.league-card')
    expect(league_card).to_be_visible()

    # Count team items (should be 32 NHL teams)
    team_items = page.locator('.league-team-item')
    expect(team_items).to_have_count(32)

def test_league_info_links(page: Page, base_url: str):
    """Test that info section links to divisions/conferences."""
    page.goto(f"{base_url}/league")

    divisions_link = page.locator('a:has-text("Division Standings")')
    conferences_link = page.locator('a:has-text("Conference Standings")')

    expect(divisions_link).to_be_visible()
    expect(conferences_link).to_be_visible()
```

### Performance Testing

**Load Test**:
```bash
# Test with hey or ab
hey -n 100 -c 10 http://localhost:8000/league

# Verify caching works
curl -w "@curl-format.txt" http://localhost:8000/league
# Should be fast on subsequent requests
```

## Acceptance Criteria

- [ ] New "League" menu item appears in navigation between "Conferences" and "Playoffs"
- [ ] League menu item is visible on all pages
- [ ] `/league` route exists and returns HTTP 200
- [ ] League page displays all teams in a single ordered list
- [ ] Page uses card-based layout (mimics divisions/conferences visual style)
- [ ] No grouping by division or conference (single league-wide list)
- [ ] Team details shown: rank, name, abbreviation, division, total score
- [ ] Page includes summary statistics (total teams, highest/lowest team, total players)
- [ ] Info section explains league standings with links to divisions/conferences
- [ ] Timestamp shows data freshness
- [ ] i18n works for all supported locales (12 locales)
- [ ] Responsive design works on mobile devices
- [ ] Navigation menu works on mobile (hamburger menu)
- [ ] Page follows same design patterns as other standings pages
- [ ] Caching works (uses same cache as other endpoints)
- [ ] No performance regression (page loads < 2 seconds)
- [ ] All automated tests pass
- [ ] QA functional tests pass
- [ ] QA visual regression tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated (if needed)

## Related Files

- `src/nhl_scrabble/web/app.py` - FastAPI application (add new route)
- `src/nhl_scrabble/web/templates/base.html` - Base template (update navigation)
- `src/nhl_scrabble/web/templates/league.html` - New league page template (create)
- `src/nhl_scrabble/web/templates/divisions.html` - Reference for card-based layout
- `src/nhl_scrabble/web/templates/conferences.html` - Reference for card-based layout
- `src/nhl_scrabble/web/static/css/style.css` - Styles (add league-specific classes)
- `src/nhl_scrabble/locales/*/LC_MESSAGES/messages.po` - Translation files (all 12 locales)
- `qa/web/tests/functional/` - Functional tests directory
- `qa/web/tests/visual/` - Visual regression tests directory

## Dependencies

**No blocking dependencies**, but related to:
- Web interface infrastructure (already implemented)
- i18n system (already implemented)
- Team standings data (already available from /api/analyze)
- QA test infrastructure (already implemented)
- Task #046 (Players page) - Similar navigation addition pattern

**Runtime dependencies**:
- FastAPI (already installed)
- Jinja2 templates (already configured)
- NHL API client (already implemented)
- Caching system (already implemented)

## Additional Notes

### Design Consistency

**Follow existing page patterns**:
- Use same header structure as divisions/conferences pages
- Use same stats-summary cards
- Use division-grid and division-card classes (existing CSS)
- Use same fade-on-scroll animations
- Use same responsive breakpoints

**Visual Design**:
- Single card spanning full width (vs multiple cards for divisions/conferences)
- Ordered list format (like divisions.html/conferences.html)
- Enhanced list items with team details (rank, name, abbrev, division, score)
- Similar to divisions/conferences but without the grouping loop

### Differences from Existing Pages

**vs Teams Page**:
- Teams page uses sortable table format
- League page uses card/list format (matches divisions/conferences style)
- Teams page is more data-dense with columns
- League page is more visual and scannable

**vs Divisions/Conferences Pages**:
- Divisions/conferences use grouped cards (one per division/conference)
- League page uses single card with all teams
- Same visual style, different organization

**vs Players Page (task #046)**:
- Players page uses table format with sorting and export
- League page uses simpler list format
- League page is lighter weight (no export buttons needed initially)

### Performance Considerations

**Caching Strategy**:
- League page uses same cache as other pages (1 hour TTL)
- Cache key: `{top_players}_{top_team_players}`
- Cache hit reduces load on NHL API
- First request: ~2-3 seconds (API calls)
- Cached requests: < 100ms

**Data Volume**:
- NHL has 32 teams
- Displaying 32 teams in list: ~8-10 KB HTML
- Lightweight compared to table-based pages
- No client-side sorting needed

### i18n Considerations

**Translation Coverage**:
- Minimum viable: en_US, en_CA, fr_CA (North American hockey markets)
- Recommended: Add sv_SE, fi_FI, cs_CZ (European hockey markets)
- Full coverage: All 12 supported locales

**Locale-Specific Notes**:
- Team names NOT translated (proper nouns)
- Division/Conference names typically NOT translated
- UI strings translated (navigation, headers, labels)
- "National Hockey League" may have translations (NHL is known worldwide)

### Mobile Responsiveness

**Hamburger Menu**:
- League item appears in mobile navigation
- Same behavior as existing items
- Handled by existing `nav.js` script

**Card Responsiveness**:
- Single card layout already responsive
- List items stack vertically on small screens
- May need font-size adjustments for mobile

### Future Enhancements

**Phase 2 Ideas** (not in this task):
- Add filtering options (by division, conference)
- Add search functionality
- Add team detail popups on click
- Add visual indicators (icons for divisions/conferences)
- Add playoff qualification indicators
- Add comparison with real NHL standings
- Add historical league standings tracking

### Testing in TEST_MODE

**Visual Tests**:
- Set `NHL_SCRABBLE_TEST_MODE=1`
- Uses fixture data from `qa/web/tests/visual/fixtures/`
- Deterministic team data for visual regression tests
- Ensures consistent screenshots

### Accessibility

**WCAG 2.1 Compliance**:
- List has proper semantic HTML (`<ol>`, `<li>`)
- Navigation has `aria-label` for screen readers
- Color contrast meets AA standards
- Keyboard navigation works (tab through list)
- Links have descriptive text

### Browser Compatibility

**Tested Browsers**:
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS)
- Mobile Chrome (Android)

### SEO Considerations

**Meta Tags**:
- Add Open Graph tags for social sharing
- Add Twitter Card tags
- Use semantic HTML (`<section>`, `<ol>`, `<li>`)
- Include descriptive page title
- Add meta description

### CSS Variables Used

The template assumes the following CSS variables exist (already defined in style.css):
- `--border-color` - Border colors for list items
- `--hover-bg` - Hover background color
- `--primary-color` - Primary brand color (for rank numbers)
- `--muted-text` - Muted text color (for team details)
- `--accent-color` - Accent color (for scores)
- `--card-bg` - Card background color
- `--border-radius` - Border radius for rounded corners
- `--link-color` - Link color

## Implementation Notes

*To be filled during implementation:*
- Actual CSS class names used
- Any template adjustments needed
- Translation completion status per locale
- QA test results (functional + visual)
- Performance metrics (load time, cache hit rate)
- Browser compatibility test results
- Accessibility audit results
- Date of implementation completion
