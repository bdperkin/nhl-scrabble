# Build Frontend Templates and CSS for Web Interface

**GitHub Issue**: #105 - https://github.com/bdperkin/nhl-scrabble/issues/105

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

4-6 hours

## Description

Build the frontend user interface for the NHL Scrabble web application including HTML templates, CSS styling, and responsive design. This task creates a professional, accessible, and mobile-friendly interface that displays analysis results in an attractive, easy-to-navigate format.

This is part 3 of 5 subtasks for building the complete web interface (broken down from #50).

## Current State

After completing tasks 002 (FastAPI Infrastructure) and 003 (API Endpoints), we have:

- FastAPI application with API endpoints
- `/api/analyze` returns JSON data
- `/health`, `/`, player/team endpoints
- No frontend templates
- No CSS styling
- No user interface

**Current template directory**:

```
src/nhl_scrabble/web/templates/
└── .gitkeep  # Empty directory
```

**Current static directory**:

```
src/nhl_scrabble/web/static/
├── css/.gitkeep
├── js/.gitkeep
└── img/.gitkeep
```

## Proposed Solution

Create professional HTML templates with responsive CSS styling and NHL-themed design.

### 1. Base Template

Create `src/nhl_scrabble/web/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="NHL Scrabble Analyzer - Analyze NHL player names by Scrabble score">
    <title>{% block title %}NHL Scrabble Analyzer{% endblock %}</title>

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/static/img/favicon.png">

    <!-- Stylesheets -->
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Header -->
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <h1 class="site-title">
                    <a href="/">🏒 NHL Scrabble Analyzer</a>
                </h1>
                <nav class="main-nav" aria-label="Main navigation">
                    <ul>
                        <li><a href="/">Home</a></li>
                        <li><a href="/docs">API Docs</a></li>
                        <li><a href="https://github.com/bdperkin/nhl-scrabble" target="_blank">GitHub</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="site-main" role="main">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2026 NHL Scrabble Analyzer |
               <a href="https://github.com/bdperkin/nhl-scrabble">Open Source</a> |
               <a href="/health">Status</a>
            </p>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="/static/js/app.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. Home Page Template

Create `src/nhl_scrabble/web/templates/index.html`:

```html
{% extends "base.html" %}

{% block title %}NHL Scrabble Analyzer - Home{% endblock %}

{% block content %}
<div class="hero">
    <h2>Analyze NHL Player Names by Scrabble Score</h2>
    <p class="hero-subtitle">
        Calculate Scrabble scores for NHL player names and see team standings,
        playoff brackets, and statistics based on letter values.
    </p>
</div>

<section class="analysis-form-section">
    <h3>Run Analysis</h3>

    <form id="analysisForm" class="analysis-form">
        <div class="form-row">
            <div class="form-group">
                <label for="topPlayers">
                    Top Players to Display
                    <span class="help-text">Number of top-scoring players (1-100)</span>
                </label>
                <input
                    type="number"
                    id="topPlayers"
                    name="top_players"
                    min="1"
                    max="100"
                    value="20"
                    aria-describedby="topPlayersHelp"
                    required
                >
            </div>

            <div class="form-group">
                <label for="topTeamPlayers">
                    Top Players per Team
                    <span class="help-text">Players per team in results (1-30)</span>
                </label>
                <input
                    type="number"
                    id="topTeamPlayers"
                    name="top_team_players"
                    min="1"
                    max="30"
                    value="5"
                    aria-describedby="topTeamPlayersHelp"
                    required
                >
            </div>

            <div class="form-group">
                <label for="useCache">
                    <input
                        type="checkbox"
                        id="useCache"
                        name="use_cache"
                        checked
                    >
                    Use Cached Results (faster)
                </label>
            </div>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary" id="analyzeBtn">
                <span class="btn-text">Analyze</span>
                <span class="btn-loading" hidden>
                    <span class="spinner"></span>
                    Fetching NHL data...
                </span>
            </button>
        </div>
    </form>
</section>

<!-- Results container (populated by JavaScript) -->
<div id="results" class="results-container" hidden>
    <!-- Results will be inserted here -->
</div>

<!-- Error message container -->
<div id="error" class="error-container" hidden role="alert">
    <!-- Error messages will be inserted here -->
</div>

<section class="info-section">
    <h3>About</h3>
    <p>
        NHL Scrabble Analyzer calculates Scrabble scores for all NHL players
        using standard Scrabble letter point values. Teams are ranked by their
        total roster score, creating an alternative playoff bracket based on
        alphabetical prowess rather than on-ice performance.
    </p>

    <h4>Scrabble Letter Values</h4>
    <div class="scrabble-values">
        <div class="value-group">
            <strong>1 point:</strong> A, E, I, O, U, L, N, S, T, R
        </div>
        <div class="value-group">
            <strong>2 points:</strong> D, G
        </div>
        <div class="value-group">
            <strong>3 points:</strong> B, C, M, P
        </div>
        <div class="value-group">
            <strong>4 points:</strong> F, H, V, W, Y
        </div>
        <div class="value-group">
            <strong>5 points:</strong> K
        </div>
        <div class="value-group">
            <strong>8 points:</strong> J, X
        </div>
        <div class="value-group">
            <strong>10 points:</strong> Q, Z
        </div>
    </div>
</section>
{% endblock %}
```

### 3. Results Template (Partial)

Create `src/nhl_scrabble/web/templates/results.html`:

```html
<!-- Top Statistics -->
<div class="stats-summary">
    <div class="stat-card">
        <h4>Total Players</h4>
        <p class="stat-value">{{ stats.total_players }}</p>
    </div>
    <div class="stat-card">
        <h4>Highest Score</h4>
        <p class="stat-value">{{ stats.highest_score }}</p>
    </div>
    <div class="stat-card">
        <h4>Average Score</h4>
        <p class="stat-value">{{ stats.avg_score|round(1) }}</p>
    </div>
    <div class="stat-card">
        <h4>Top Team</h4>
        <p class="stat-value">{{ stats.highest_team }}</p>
    </div>
</div>

<!-- Top Players Table -->
<section class="results-section">
    <h3>Top {{ top_players|length }} Players by Scrabble Score</h3>
    <div class="table-container">
        <table class="results-table" role="table" aria-label="Top players by Scrabble score">
            <thead>
                <tr>
                    <th scope="col">Rank</th>
                    <th scope="col">Player Name</th>
                    <th scope="col">Team</th>
                    <th scope="col">Score</th>
                </tr>
            </thead>
            <tbody>
                {% for player in top_players %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td class="player-name">{{ player.first_name }} {{ player.last_name }}</td>
                    <td class="team-abbrev">{{ player.team }}</td>
                    <td class="score">{{ player.score }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>

<!-- Team Standings Table -->
<section class="results-section">
    <h3>Team Standings by Total Scrabble Score</h3>
    <div class="table-container">
        <table class="results-table standings-table" role="table" aria-label="Team standings">
            <thead>
                <tr>
                    <th scope="col">Rank</th>
                    <th scope="col">Team</th>
                    <th scope="col">Division</th>
                    <th scope="col">Conference</th>
                    <th scope="col">Total Score</th>
                    <th scope="col">Avg Score</th>
                    <th scope="col">Players</th>
                </tr>
            </thead>
            <tbody>
                {% for team in team_standings %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td class="team-name">{{ team.name }}</td>
                    <td>{{ team.division }}</td>
                    <td>{{ team.conference }}</td>
                    <td class="score">{{ team.total_score }}</td>
                    <td>{{ team.avg_score|round(1) }}</td>
                    <td>{{ team.player_count }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>

<!-- Division Standings (simplified for space) -->
<section class="results-section">
    <h3>Division Standings</h3>
    <div class="division-grid">
        {% for division, teams in division_standings.items() %}
        <div class="division-card">
            <h4>{{ division }}</h4>
            <ol>
                {% for team in teams[:5] %}
                <li>{{ team.name }} ({{ team.total_score }})</li>
                {% endfor %}
            </ol>
        </div>
        {% endfor %}
    </div>
</section>
```

### 4. Main CSS Stylesheet

Create `src/nhl_scrabble/web/static/css/style.css`:

```css
/* ===== CSS Variables ===== */
:root {
    /* NHL-inspired color palette */
    --color-primary: #003087;      /* NHL blue */
    --color-secondary: #C8102E;    /* NHL red */
    --color-accent: #FFB81C;       /* NHL gold */
    --color-dark: #1a1a1a;
    --color-light: #f5f5f5;
    --color-white: #ffffff;
    --color-gray: #666666;
    --color-gray-light: #e0e0e0;

    /* Typography */
    --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-family-heading: "Arial Black", "Arial Bold", Gadget, sans-serif;

    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 1.5rem;
    --spacing-lg: 2rem;
    --spacing-xl: 3rem;

    /* Layout */
    --container-max-width: 1200px;
    --border-radius: 8px;
    --box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* ===== Reset & Base Styles ===== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-family-base);
    line-height: 1.6;
    color: var(--color-dark);
    background-color: var(--color-light);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* ===== Typography ===== */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family-heading);
    line-height: 1.2;
    margin-bottom: var(--spacing-sm);
    color: var(--color-primary);
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; }

/* ===== Layout ===== */
.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}

.site-main {
    flex: 1;
    padding: var(--spacing-lg) 0;
}

/* ===== Header ===== */
.site-header {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    color: var(--color-white);
    padding: var(--spacing-md) 0;
    box-shadow: var(--box-shadow);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.site-title a {
    color: var(--color-white);
    text-decoration: none;
    font-size: 1.75rem;
}

.main-nav ul {
    display: flex;
    list-style: none;
    gap: var(--spacing-md);
}

.main-nav a {
    color: var(--color-white);
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.2s;
}

.main-nav a:hover {
    opacity: 0.8;
}

/* ===== Hero Section ===== */
.hero {
    text-align: center;
    padding: var(--spacing-xl) 0;
    background: var(--color-white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    margin-bottom: var(--spacing-lg);
}

.hero-subtitle {
    font-size: 1.125rem;
    color: var(--color-gray);
    max-width: 600px;
    margin: 0 auto;
}

/* ===== Forms ===== */
.analysis-form-section {
    background: var(--color-white);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    margin-bottom: var(--spacing-lg);
}

.analysis-form {
    max-width: 600px;
    margin: 0 auto;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
    color: var(--color-dark);
}

.help-text {
    display: block;
    font-size: 0.875rem;
    color: var(--color-gray);
    font-weight: normal;
}

input[type="number"] {
    padding: var(--spacing-xs) var(--spacing-sm);
    border: 2px solid var(--color-gray-light);
    border-radius: var(--border-radius);
    font-size: 1rem;
    transition: border-color 0.2s;
}

input[type="number"]:focus {
    outline: none;
    border-color: var(--color-primary);
}

input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
}

/* ===== Buttons ===== */
.btn {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: none;
    border-radius: var(--border-radius);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
}

.btn-primary {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    color: var(--color-white);
    box-shadow: 0 4px 12px rgba(0, 48, 135, 0.3);
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 48, 135, 0.4);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.form-actions {
    text-align: center;
    margin-top: var(--spacing-lg);
}

/* ===== Loading Spinner ===== */
.spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: var(--color-white);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===== Tables ===== */
.table-container {
    overflow-x: auto;
    margin: var(--spacing-md) 0;
}

.results-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--color-white);
    box-shadow: var(--box-shadow);
    border-radius: var(--border-radius);
    overflow: hidden;
}

.results-table th {
    background: var(--color-primary);
    color: var(--color-white);
    padding: var(--spacing-sm);
    text-align: left;
    font-weight: 600;
}

.results-table td {
    padding: var(--spacing-sm);
    border-bottom: 1px solid var(--color-gray-light);
}

.results-table tbody tr:hover {
    background-color: rgba(0, 48, 135, 0.05);
}

.score {
    font-weight: 700;
    color: var(--color-secondary);
}

/* ===== Stats Cards ===== */
.stats-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.stat-card {
    background: var(--color-white);
    padding: var(--spacing-md);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-primary);
}

/* ===== Footer ===== */
.site-footer {
    background: var(--color-dark);
    color: var(--color-white);
    padding: var(--spacing-md) 0;
    text-align: center;
    margin-top: auto;
}

.site-footer a {
    color: var(--color-accent);
    text-decoration: none;
}

/* ===== Responsive Design ===== */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
    }

    .main-nav ul {
        flex-direction: column;
        gap: var(--spacing-sm);
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }
}

/* ===== Accessibility ===== */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

:focus {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
}

/* ===== Error/Success Messages ===== */
.error-container {
    background: #fee;
    border-left: 4px solid var(--color-secondary);
    padding: var(--spacing-md);
    margin: var(--spacing-md) 0;
    border-radius: var(--border-radius);
}

.success-container {
    background: #efe;
    border-left: 4px solid #4caf50;
    padding: var(--spacing-md);
    margin: var(--spacing-md) 0;
    border-radius: var(--border-radius);
}
```

## Implementation Steps

1. **Create Base Template**

   - Create `base.html` with header, footer, navigation
   - Add semantic HTML structure
   - Include meta tags for SEO and viewport
   - Add favicon placeholder

1. **Create Home Page**

   - Create `index.html` extending base template
   - Add hero section with description
   - Add analysis form with proper labels
   - Add results container
   - Add informational sections

1. **Create Results Template**

   - Create `results.html` partial template
   - Add stats summary cards
   - Add top players table
   - Add team standings table
   - Add division/conference sections
   - Add playoff bracket display

1. **Implement CSS**

   - Create `style.css` with NHL-themed design
   - Define CSS variables for consistency
   - Implement responsive grid layout
   - Style forms, buttons, tables
   - Add loading spinner animation
   - Ensure mobile-first approach

1. **Add Accessibility Features**

   - Use semantic HTML5 elements
   - Add ARIA labels and roles
   - Ensure keyboard navigation
   - Add focus states
   - Add screen-reader-only text where needed

1. **Test Responsive Design**

   - Test on mobile (320px+)
   - Test on tablet (768px+)
   - Test on desktop (1200px+)
   - Verify flexbox/grid layouts
   - Check touch targets on mobile

1. **Update FastAPI Integration**

   - Update `app.py` to serve templates
   - Add template rendering for index page
   - Ensure static files are served correctly

## Testing Strategy

### Manual Testing

```bash
# Start server
nhl-scrabble serve --reload

# Test pages in browser
open http://localhost:8000/
open http://localhost:8000/docs

# Test responsive design (Chrome DevTools)
# - Toggle device toolbar
# - Test various screen sizes
# - Verify layout adapts

# Test accessibility
# - Tab through all interactive elements
# - Verify focus indicators visible
# - Test with screen reader
# - Check color contrast

# Test forms
# - Enter valid values (submit form)
# - Enter invalid values (check validation)
# - Test checkbox
# - Verify loading spinner appears

# Test tables
# - Scroll horizontally on mobile
# - Verify hover states
# - Check readability
```

### Browser Testing

Test in multiple browsers:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Android)

### Accessibility Testing

Tools to use:

- [WAVE](https://wave.webaim.org/) browser extension
- Lighthouse in Chrome DevTools
- Keyboard-only navigation
- Screen reader testing (NVDA on Windows, VoiceOver on Mac)

## Acceptance Criteria

- [ ] `base.html` template created with header, footer, navigation
- [ ] `index.html` home page created with analysis form
- [ ] `results.html` partial template created for displaying results
- [ ] `style.css` created with comprehensive styling
- [ ] Responsive design works on mobile, tablet, desktop
- [ ] Forms have proper labels and validation
- [ ] Tables are scrollable on mobile
- [ ] Loading spinner implemented and functional
- [ ] Color scheme uses NHL-inspired palette
- [ ] All interactive elements have hover/focus states
- [ ] Semantic HTML5 elements used throughout
- [ ] ARIA labels added where needed
- [ ] Keyboard navigation works properly
- [ ] Focus indicators visible
- [ ] Text has sufficient color contrast (WCAG AA)
- [ ] Templates integrate with FastAPI app
- [ ] Static files served correctly
- [ ] Manual testing confirms UI functionality
- [ ] Cross-browser testing passes
- [ ] Accessibility audit passes

## Related Files

- `src/nhl_scrabble/web/templates/base.html` - New base template
- `src/nhl_scrabble/web/templates/index.html` - New home page
- `src/nhl_scrabble/web/templates/results.html` - New results partial
- `src/nhl_scrabble/web/static/css/style.css` - New stylesheet
- `src/nhl_scrabble/web/static/img/favicon.png` - Favicon (optional)
- `src/nhl_scrabble/web/app.py` - Update to serve templates
- `README.md` - Add web interface screenshots/usage
- `CHANGELOG.md` - Document new UI

## Dependencies

**Required**:

- Task new-features/002 (FastAPI Infrastructure) - Provides web server
- Task new-features/003 (API Endpoints) - Provides data for templates

Both tasks must be completed before this one.

## Additional Notes

### Design Philosophy

**NHL-Themed**:

- Primary colors: NHL blue (#003087) and red (#C8102E)
- Accent: NHL gold (#FFB81C)
- Professional, sports-inspired aesthetic
- Bold headings, clean tables

**Mobile-First**:

- Design for smallest screens first
- Progressive enhancement for larger screens
- Touch-friendly targets (minimum 44x44px)
- Readable text sizes (minimum 16px)

**Accessibility-First**:

- WCAG 2.1 Level AA compliance
- Semantic HTML structure
- Keyboard navigable
- Screen reader friendly

### Template Rendering

Update `app.py` to serve the index page:

```python
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve home page."""
    return templates.TemplateResponse("index.html", {"request": request})
```

### CSS Architecture

**Organization**:

1. CSS Variables (colors, spacing, fonts)
1. Reset & base styles
1. Typography
1. Layout
1. Components (header, forms, tables, buttons)
1. Utilities
1. Responsive breakpoints
1. Accessibility

**Naming Convention**:

- BEM-inspired: `.component-element--modifier`
- Descriptive class names
- Avoid generic names like `.container-1`

### Performance

**CSS**:

- Single stylesheet (style.css)
- No external CSS dependencies
- Minimal CSS (~500 lines)
- Use CSS variables for consistency

**Images**:

- Favicon only (small, optimized PNG)
- No hero images or backgrounds
- Keep page weight low

### Browser Support

**Target browsers**:

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari 14+
- Chrome Android 90+

**Features used**:

- CSS Grid (widely supported)
- CSS Flexbox (widely supported)
- CSS Variables (widely supported)
- No bleeding-edge features

### Future Enhancements

Not included in this task:

- Dark mode toggle
- Print stylesheet
- Advanced animations
- Chart visualizations (next task)
- Table sorting (next task)
- Filtering/search

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
- Browser compatibility issues found
- Accessibility improvements made
