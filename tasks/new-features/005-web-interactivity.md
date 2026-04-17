# Add JavaScript Interactivity and Data Visualizations

**GitHub Issue**: #106 - https://github.com/bdperkin/nhl-scrabble/issues/106

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

8-12 hours

## Description

Add JavaScript interactivity and data visualizations to the NHL Scrabble web interface. Implement HTMX for seamless form submission and dynamic content loading without page refreshes. Add Chart.js for visualizing score distributions with bar charts showing team scores and player score distributions. Implement client-side table sorting for players and teams tables. Add data export functionality (CSV, JSON download). Implement responsive navigation menu for mobile devices. Add smooth scrolling and UI animations. Handle loading states and error messages gracefully.

This is part 4 of 5 subtasks for building the complete web interface (broken down from #50).

## Current State

After completing tasks 002 (FastAPI Infrastructure), 003 (API Endpoints), and 004 (Frontend Templates), we have:

- FastAPI application with full API endpoints
- HTML templates with static content
- Basic CSS styling with NHL theme
- Responsive layout foundation
- No JavaScript interactivity
- No dynamic content loading
- No data visualizations
- No export functionality
- Static navigation menu
- No table sorting

**Current template structure** (from task 004):

```
src/nhl_scrabble/web/templates/
├── base.html           # Base template with navigation
├── index.html          # Analysis page with static tables
├── player_detail.html  # Player detail page
└── team_detail.html    # Team detail page
```

**Current static structure**:

```
src/nhl_scrabble/web/static/
├── css/
│   └── style.css       # NHL-themed CSS
├── js/
│   └── .gitkeep        # Empty - needs JavaScript
└── img/
    └── .gitkeep
```

**Current index.html tables** (static):

```html
<!-- Teams table - no sorting, no interactivity -->
<table class="teams-table">
  <thead>
    <tr>
      <th>Rank</th>
      <th>Team</th>
      <th>Total Score</th>
      <th>Players</th>
      <th>Avg Score</th>
    </tr>
  </thead>
  <tbody>
    {% for team in standings.teams %}
    <tr>
      <td>{{ loop.index }}</td>
      <td>{{ team.name }}</td>
      <td>{{ team.total_score }}</td>
      <td>{{ team.player_count }}</td>
      <td>{{ team.average_score }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<!-- Players table - no sorting, no interactivity -->
<table class="players-table">
  <!-- Similar static structure -->
</table>
```

**Available API endpoints** (from task 003):

- `GET /api/analyze` - Full analysis with caching
- `GET /api/players/{player_id}` - Player details
- `GET /api/teams/{team_abbrev}` - Team details
- `GET /api/cache/clear` - Clear cache

## Proposed Solution

Add comprehensive JavaScript interactivity using modern libraries and progressive enhancement.

### 1. HTMX Integration

Add HTMX for seamless dynamic content loading without full page refreshes.

**Install HTMX** (CDN approach):

```html
<!-- base.html - add to head -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

**Dynamic form submission** (index.html):

```html
<form hx-post="/api/analyze" hx-target="#results" hx-indicator="#loading">
  <button type="submit">Refresh Analysis</button>
  <div id="loading" class="htmx-indicator">
    <span class="spinner"></span> Loading...
  </div>
</form>

<div id="results">
  <!-- Existing tables here, will be replaced on HTMX response -->
</div>
```

**Backend HTMX support** (app.py):

```python
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.post("/api/analyze")
async def analyze_htmx(request: Request):
    """Handle HTMX analysis request."""
    # Run analysis
    standings = await run_analysis()

    # Return partial HTML fragment for HTMX
    return templates.TemplateResponse(
        "partials/results_table.html",
        {"request": request, "standings": standings}
    )
```

**Create partial template** (templates/partials/results_table.html):

```html
<!-- Table fragment for HTMX updates -->
<div id="results">
  <table class="teams-table">
    <!-- Table content -->
  </table>
</div>
```

### 2. Chart.js Visualizations

Add Chart.js for interactive score visualizations.

**Install Chart.js** (CDN):

```html
<!-- base.html -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
```

**Team Scores Bar Chart** (static/js/charts.js):

```javascript
// Create team scores visualization
function createTeamScoresChart(teams) {
  const ctx = document.getElementById('teamScoresChart').getContext('2d');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: teams.map(t => t.abbreviation),
      datasets: [{
        label: 'Team Total Score',
        data: teams.map(t => t.total_score),
        backgroundColor: teams.map(t => getTeamColor(t.abbreviation)),
        borderColor: teams.map(t => getTeamBorderColor(t.abbreviation)),
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'NHL Teams by Scrabble Score'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `Score: ${context.parsed.y}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Total Score'
          }
        }
      }
    }
  });
}

// Team color mapping (NHL team colors)
function getTeamColor(abbrev) {
  const colors = {
    'TOR': 'rgba(0, 32, 91, 0.8)',      // Maple Leafs blue
    'MTL': 'rgba(175, 30, 45, 0.8)',    // Canadiens red
    'BOS': 'rgba(252, 181, 20, 0.8)',   // Bruins gold
    // ... all 32 teams
  };
  return colors[abbrev] || 'rgba(100, 100, 100, 0.8)';
}
```

**Player Score Distribution Chart** (static/js/charts.js):

```javascript
// Create player score distribution histogram
function createPlayerDistributionChart(players) {
  const ctx = document.getElementById('playerDistributionChart').getContext('2d');

  // Create score buckets (0-10, 11-20, 21-30, etc.)
  const buckets = createScoreBuckets(players);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: buckets.labels,
      datasets: [{
        label: 'Number of Players',
        data: buckets.counts,
        backgroundColor: 'rgba(75, 192, 192, 0.8)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Player Score Distribution'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `Players: ${context.parsed.y}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Players'
          },
          ticks: {
            stepSize: 10
          }
        }
      }
    }
  });
}

function createScoreBuckets(players) {
  const bucketSize = 10;
  const maxScore = Math.max(...players.map(p => p.score));
  const numBuckets = Math.ceil(maxScore / bucketSize);

  const buckets = Array(numBuckets).fill(0);
  players.forEach(p => {
    const bucketIndex = Math.floor(p.score / bucketSize);
    buckets[bucketIndex]++;
  });

  return {
    labels: buckets.map((_, i) => `${i * bucketSize}-${(i + 1) * bucketSize - 1}`),
    counts: buckets
  };
}
```

**Add chart canvases to template** (index.html):

```html
<!-- Add visualization section -->
<section class="visualizations">
  <h2>Score Visualizations</h2>

  <div class="chart-container">
    <h3>Team Scores</h3>
    <canvas id="teamScoresChart" width="800" height="400"></canvas>
  </div>

  <div class="chart-container">
    <h3>Player Score Distribution</h3>
    <canvas id="playerDistributionChart" width="800" height="400"></canvas>
  </div>
</section>

<script src="{{ url_for('static', path='/js/charts.js') }}"></script>
<script>
  // Initialize charts with data from backend
  document.addEventListener('DOMContentLoaded', function() {
    const teamsData = {{ teams_json | safe }};
    const playersData = {{ players_json | safe }};

    createTeamScoresChart(teamsData);
    createPlayerDistributionChart(playersData);
  });
</script>
```

### 3. Table Sorting

Add client-side table sorting for players and teams.

**Create sorting library** (static/js/table-sort.js):

```javascript
class TableSort {
  constructor(tableId) {
    this.table = document.getElementById(tableId);
    this.tbody = this.table.querySelector('tbody');
    this.headers = this.table.querySelectorAll('th[data-sort]');
    this.currentSort = { column: null, direction: 'asc' };

    this.init();
  }

  init() {
    this.headers.forEach(header => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => this.handleHeaderClick(header));

      // Add sort indicator
      const indicator = document.createElement('span');
      indicator.className = 'sort-indicator';
      indicator.innerHTML = '↕️';
      header.appendChild(indicator);
    });
  }

  handleHeaderClick(header) {
    const column = header.dataset.sort;
    const type = header.dataset.sortType || 'string';

    // Toggle direction if same column
    if (this.currentSort.column === column) {
      this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
      this.currentSort.column = column;
      this.currentSort.direction = 'asc';
    }

    this.sortTable(column, type, this.currentSort.direction);
    this.updateSortIndicators();
  }

  sortTable(column, type, direction) {
    const rows = Array.from(this.tbody.querySelectorAll('tr'));
    const columnIndex = this.getColumnIndex(column);

    rows.sort((a, b) => {
      const aValue = a.cells[columnIndex].textContent.trim();
      const bValue = b.cells[columnIndex].textContent.trim();

      let comparison = 0;
      if (type === 'number') {
        comparison = parseFloat(aValue) - parseFloat(bValue);
      } else {
        comparison = aValue.localeCompare(bValue);
      }

      return direction === 'asc' ? comparison : -comparison;
    });

    // Re-append rows in sorted order
    rows.forEach(row => this.tbody.appendChild(row));
  }

  getColumnIndex(column) {
    return Array.from(this.headers).findIndex(h => h.dataset.sort === column);
  }

  updateSortIndicators() {
    this.headers.forEach(header => {
      const indicator = header.querySelector('.sort-indicator');
      if (header.dataset.sort === this.currentSort.column) {
        indicator.innerHTML = this.currentSort.direction === 'asc' ? '↑' : '↓';
        indicator.style.opacity = '1';
      } else {
        indicator.innerHTML = '↕️';
        indicator.style.opacity = '0.3';
      }
    });
  }
}

// Initialize sortable tables
document.addEventListener('DOMContentLoaded', function() {
  new TableSort('teamsTable');
  new TableSort('playersTable');
});
```

**Update table headers** (index.html):

```html
<table id="teamsTable" class="teams-table">
  <thead>
    <tr>
      <th data-sort="rank" data-sort-type="number">Rank</th>
      <th data-sort="team" data-sort-type="string">Team</th>
      <th data-sort="score" data-sort-type="number">Total Score</th>
      <th data-sort="players" data-sort-type="number">Players</th>
      <th data-sort="avg" data-sort-type="number">Avg Score</th>
    </tr>
  </thead>
  <tbody>
    <!-- Table rows -->
  </tbody>
</table>
```

### 4. Data Export Functionality

Add CSV and JSON export with client-side download.

**Create export library** (static/js/export.js):

```javascript
class DataExporter {
  static exportToCSV(data, filename) {
    const csv = this.convertToCSV(data);
    this.downloadFile(csv, filename, 'text/csv');
  }

  static exportToJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    this.downloadFile(json, filename, 'application/json');
  }

  static convertToCSV(data) {
    if (data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const csvRows = [];

    // Add header row
    csvRows.push(headers.join(','));

    // Add data rows
    data.forEach(row => {
      const values = headers.map(header => {
        const value = row[header];
        // Escape quotes and wrap in quotes if contains comma
        return typeof value === 'string' && value.includes(',')
          ? `"${value.replace(/"/g, '""')}"`
          : value;
      });
      csvRows.push(values.join(','));
    });

    return csvRows.join('\n');
  }

  static downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

// Export button handlers
document.getElementById('exportTeamsCSV').addEventListener('click', function() {
  const teamsData = getTeamsTableData();
  DataExporter.exportToCSV(teamsData, 'nhl-scrabble-teams.csv');
});

document.getElementById('exportTeamsJSON').addEventListener('click', function() {
  const teamsData = getTeamsTableData();
  DataExporter.exportToJSON(teamsData, 'nhl-scrabble-teams.json');
});

// Extract data from table
function getTeamsTableData() {
  const table = document.getElementById('teamsTable');
  const rows = table.querySelectorAll('tbody tr');

  return Array.from(rows).map(row => ({
    rank: row.cells[0].textContent.trim(),
    team: row.cells[1].textContent.trim(),
    total_score: parseInt(row.cells[2].textContent.trim()),
    players: parseInt(row.cells[3].textContent.trim()),
    avg_score: parseFloat(row.cells[4].textContent.trim())
  }));
}
```

**Add export buttons** (index.html):

```html
<div class="export-buttons">
  <h3>Export Data</h3>
  <button id="exportTeamsCSV" class="btn btn-secondary">
    <span class="icon">📊</span> Export Teams (CSV)
  </button>
  <button id="exportTeamsJSON" class="btn btn-secondary">
    <span class="icon">📄</span> Export Teams (JSON)
  </button>
  <button id="exportPlayersCSV" class="btn btn-secondary">
    <span class="icon">📊</span> Export Players (CSV)
  </button>
  <button id="exportPlayersJSON" class="btn btn-secondary">
    <span class="icon">📄</span> Export Players (JSON)
  </button>
</div>
```

### 5. Responsive Mobile Navigation

Add hamburger menu for mobile devices.

**Mobile navigation** (static/js/nav.js):

```javascript
class MobileNav {
  constructor() {
    this.navToggle = document.getElementById('navToggle');
    this.navMenu = document.getElementById('navMenu');
    this.body = document.body;

    this.init();
  }

  init() {
    this.navToggle.addEventListener('click', () => this.toggle());

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.navToggle.contains(e.target) && !this.navMenu.contains(e.target)) {
        this.close();
      }
    });

    // Close menu when clicking a link
    this.navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => this.close());
    });
  }

  toggle() {
    this.navMenu.classList.toggle('open');
    this.navToggle.classList.toggle('open');
    this.body.classList.toggle('nav-open');
  }

  close() {
    this.navMenu.classList.remove('open');
    this.navToggle.classList.remove('open');
    this.body.classList.remove('nav-open');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  new MobileNav();
});
```

**Update navigation HTML** (base.html):

```html
<nav class="navbar">
  <div class="container">
    <a href="/" class="logo">NHL Scrabble</a>

    <!-- Hamburger button (mobile) -->
    <button id="navToggle" class="nav-toggle" aria-label="Toggle navigation">
      <span class="hamburger"></span>
    </button>

    <!-- Navigation menu -->
    <ul id="navMenu" class="nav-menu">
      <li><a href="/">Home</a></li>
      <li><a href="/teams">Teams</a></li>
      <li><a href="/players">Players</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </div>
</nav>
```

**Mobile navigation CSS** (style.css):

```css
.nav-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
}

.hamburger {
  display: block;
  width: 25px;
  height: 3px;
  background-color: #fff;
  position: relative;
  transition: background-color 0.3s;
}

.hamburger::before,
.hamburger::after {
  content: '';
  position: absolute;
  width: 25px;
  height: 3px;
  background-color: #fff;
  transition: transform 0.3s;
}

.hamburger::before {
  top: -8px;
}

.hamburger::after {
  top: 8px;
}

/* Mobile styles */
@media (max-width: 768px) {
  .nav-toggle {
    display: block;
  }

  .nav-menu {
    position: fixed;
    top: 60px;
    right: -100%;
    width: 80%;
    max-width: 300px;
    height: calc(100vh - 60px);
    background-color: #003366;
    flex-direction: column;
    padding: 20px;
    transition: right 0.3s;
    box-shadow: -2px 0 10px rgba(0, 0, 0, 0.3);
  }

  .nav-menu.open {
    right: 0;
  }

  /* Hamburger animation when open */
  .nav-toggle.open .hamburger {
    background-color: transparent;
  }

  .nav-toggle.open .hamburger::before {
    transform: rotate(45deg) translate(6px, 6px);
  }

  .nav-toggle.open .hamburger::after {
    transform: rotate(-45deg) translate(6px, -6px);
  }
}
```

### 6. Smooth Scrolling and Animations

Add smooth scrolling and UI animations for better UX.

**Smooth scrolling** (static/js/ui.js):

```javascript
// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Fade-in animation for elements as they scroll into view
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const fadeInObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in');
      fadeInObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.fade-on-scroll').forEach(el => {
  fadeInObserver.observe(el);
});
```

**Animation CSS** (style.css):

```css
/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Fade-in animation */
.fade-on-scroll {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.fade-on-scroll.fade-in {
  opacity: 1;
  transform: translateY(0);
}

/* Loading spinner */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Button hover animations */
.btn {
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.btn:active {
  transform: translateY(0);
}
```

### 7. Loading States and Error Handling

Add graceful loading states and error messages.

**Loading overlay** (base.html):

```html
<!-- Global loading overlay -->
<div id="loadingOverlay" class="loading-overlay">
  <div class="loading-content">
    <div class="spinner-large"></div>
    <p>Loading NHL data...</p>
  </div>
</div>
```

**Error handling** (static/js/errors.js):

```javascript
class ErrorHandler {
  static show(message, type = 'error') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${this.getIcon(type)}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }

  static getIcon(type) {
    const icons = {
      error: '❌',
      warning: '⚠️',
      success: '✅',
      info: 'ℹ️'
    };
    return icons[type] || icons.info;
  }

  static handleApiError(error) {
    console.error('API Error:', error);

    let message = 'An error occurred. Please try again.';
    if (error.response) {
      message = `Error ${error.response.status}: ${error.response.statusText}`;
    } else if (error.message) {
      message = error.message;
    }

    this.show(message, 'error');
  }
}

// Global error handler for fetch requests
window.addEventListener('unhandledrejection', event => {
  ErrorHandler.handleApiError(event.reason);
});
```

**Error toast CSS** (style.css):

```css
.toast {
  position: fixed;
  top: 80px;
  right: 20px;
  background-color: #fff;
  border-left: 4px solid;
  padding: 15px 20px;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 10000;
  animation: slideIn 0.3s ease-out;
  max-width: 400px;
}

.toast-error { border-left-color: #dc3545; }
.toast-warning { border-left-color: #ffc107; }
.toast-success { border-left-color: #28a745; }
.toast-info { border-left-color: #17a2b8; }

.toast-icon {
  font-size: 20px;
}

.toast-message {
  flex: 1;
  font-size: 14px;
}

.toast-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  opacity: 0.5;
}

.toast-close:hover {
  opacity: 1;
}

.toast.fade-out {
  animation: slideOut 0.3s ease-in forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(400px);
    opacity: 0;
  }
}
```

## Implementation Steps

1. **Add JavaScript Dependencies** (30 min)

   - Add HTMX CDN to base.html
   - Add Chart.js CDN to base.html
   - Create static/js/ directory structure
   - Update templates to load scripts

1. **Implement HTMX Dynamic Loading** (1-2h)

   - Add HTMX attributes to forms
   - Create partial templates for HTMX responses
   - Add loading indicators
   - Update backend endpoints for HTMX
   - Test form submission without page refresh

1. **Implement Chart.js Visualizations** (2-3h)

   - Create charts.js with team scores chart
   - Add player distribution histogram
   - Implement NHL team color scheme
   - Add chart canvases to templates
   - Pass data from backend to charts
   - Style chart containers responsively

1. **Implement Table Sorting** (1-2h)

   - Create table-sort.js library
   - Add data-sort attributes to headers
   - Implement click handlers
   - Add sort indicators (arrows)
   - Test sorting on teams and players tables

1. **Implement Data Export** (1-2h)

   - Create export.js library
   - Implement CSV conversion
   - Implement JSON export
   - Add export buttons to UI
   - Test downloads in multiple browsers

1. **Implement Mobile Navigation** (1h)

   - Create nav.js for mobile menu
   - Add hamburger button to template
   - Implement toggle functionality
   - Style mobile menu with CSS
   - Add close-on-click-outside behavior

1. **Add Smooth Scrolling and Animations** (1h)

   - Create ui.js for interactions
   - Implement smooth scroll for anchors
   - Add fade-in-on-scroll observer
   - Create CSS animations
   - Add animation classes to elements

1. **Implement Loading States and Error Handling** (1h)

   - Create errors.js error handler
   - Add loading overlay component
   - Implement toast notifications
   - Add global error handlers
   - Style loading and error components

1. **Browser Testing** (1h)

   - Test in Chrome, Firefox, Safari, Edge
   - Verify mobile responsiveness
   - Check touch interactions
   - Validate accessibility
   - Fix browser-specific issues

1. **Documentation** (30 min)

   - Document JavaScript modules
   - Add code comments
   - Update user documentation
   - Document browser support

## Testing Strategy

### Manual Testing

**HTMX Functionality:**

1. Click refresh button → verify no page reload
1. Check loading indicator appears
1. Verify tables update correctly
1. Test error handling on API failure

**Chart.js Visualizations:**

1. Verify team scores chart displays
1. Check player distribution histogram
1. Verify NHL team colors are correct
1. Test chart responsiveness on mobile
1. Verify chart tooltips work
1. Check chart legends display

**Table Sorting:**

1. Click each column header
1. Verify ascending sort works
1. Verify descending sort works
1. Check sort indicators update
1. Test on mobile devices
1. Verify performance with large tables

**Data Export:**

1. Export teams as CSV → verify format
1. Export teams as JSON → verify format
1. Export players as CSV
1. Export players as JSON
1. Test downloads in different browsers
1. Verify file names are correct

**Mobile Navigation:**

1. Resize to mobile viewport
1. Click hamburger menu → verify opens
1. Click link → verify menu closes
1. Click outside → verify menu closes
1. Test on actual mobile devices

**Animations and UX:**

1. Verify smooth scrolling works
1. Check fade-in animations trigger
1. Test button hover effects
1. Verify transitions are smooth
1. Check loading spinner displays

**Error Handling:**

1. Simulate API error → verify toast
1. Test network timeout
1. Verify error messages are user-friendly
1. Check auto-dismiss after 5 seconds
1. Test manual close button

### Browser Compatibility

Test on:

- ✅ Chrome 120+
- ✅ Firefox 120+
- ✅ Safari 17+
- ✅ Edge 120+
- ✅ Mobile Safari (iOS 16+)
- ✅ Mobile Chrome (Android 12+)

### Performance Testing

- Verify charts render in \<1 second
- Check table sorting is instant (\<100ms)
- Verify HTMX updates are smooth
- Test with large datasets (500+ players)
- Check memory usage doesn't grow

## Acceptance Criteria

- [ ] HTMX integrated for form submission without page refresh
- [ ] Chart.js integrated for score visualizations
- [ ] Bar chart showing team scores implemented with NHL colors
- [ ] Bar chart showing player score distribution implemented
- [ ] Client-side table sorting functional on teams table
- [ ] Client-side table sorting functional on players table
- [ ] CSV export functionality working for teams
- [ ] CSV export functionality working for players
- [ ] JSON export functionality working for teams
- [ ] JSON export functionality working for players
- [ ] Responsive mobile navigation menu with hamburger
- [ ] Smooth scrolling implemented for anchor links
- [ ] Fade-in animations on scroll implemented
- [ ] Loading overlay displays during data fetches
- [ ] Error toast notifications display gracefully
- [ ] All features work in Chrome, Firefox, Safari, Edge
- [ ] Mobile testing passes on iOS and Android
- [ ] Performance testing passes (charts \<1s, sorting \<100ms)
- [ ] Accessibility testing passes (keyboard navigation, screen readers)
- [ ] Documentation updated with JavaScript features
- [ ] Code comments added to all JavaScript modules

## Related Files

**New Files**:

- `src/nhl_scrabble/web/static/js/charts.js` - Chart.js visualizations
- `src/nhl_scrabble/web/static/js/table-sort.js` - Table sorting
- `src/nhl_scrabble/web/static/js/export.js` - Data export
- `src/nhl_scrabble/web/static/js/nav.js` - Mobile navigation
- `src/nhl_scrabble/web/static/js/ui.js` - UI interactions and animations
- `src/nhl_scrabble/web/static/js/errors.js` - Error handling
- `src/nhl_scrabble/web/templates/partials/results_table.html` - HTMX partial

**Modified Files**:

- `src/nhl_scrabble/web/templates/base.html` - Add CDN scripts, loading overlay
- `src/nhl_scrabble/web/templates/index.html` - Add charts, export buttons, HTMX attributes
- `src/nhl_scrabble/web/static/css/style.css` - Add animation, mobile nav, toast styles
- `src/nhl_scrabble/web/app.py` - Add HTMX endpoints, partial template responses

## Dependencies

**Required**:

- Task 002 (FastAPI Infrastructure) - Must be complete
- Task 003 (API Endpoints) - Must be complete
- Task 004 (Frontend Templates) - Must be complete

**External Libraries (CDN)**:

- HTMX 1.9.10+ - Dynamic content loading
- Chart.js 4.4.0+ - Data visualizations

## Additional Notes

**Progressive Enhancement**:

- All features work without JavaScript (degraded experience)
- HTMX falls back to full page loads
- Export buttons still work via backend endpoints
- Tables still viewable without sorting

**Performance Considerations**:

- Use CDN for libraries (caching, global CDN)
- Lazy load charts (only render when visible)
- Debounce sort operations for large tables
- Use requestAnimationFrame for smooth animations

**Security Considerations**:

- Sanitize all user input (although minimal user input)
- Use CSP headers for script sources
- Validate data before export
- HTTPS only in production

**Accessibility**:

- Keyboard navigation for all interactive elements
- ARIA labels for screen readers
- Focus indicators for keyboard users
- Color contrast meets WCAG AA standards

**Browser Support**:

- Modern browsers (last 2 versions)
- ES6+ JavaScript (no IE11 support)
- CSS Grid and Flexbox required
- Intersection Observer API for scroll animations

**Future Enhancements** (not in this task):

- Real-time updates via WebSockets
- Advanced filtering and search
- Customizable chart types
- User preferences persistence
- Print-friendly stylesheets

## Implementation Notes

*To be filled during implementation*
