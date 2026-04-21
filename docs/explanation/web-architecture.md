# Web Interface Architecture

This document explains the architecture, design decisions, and technical implementation of the NHL Scrabble web interface.

## Overview

The web interface is a modern, single-page application (SPA) built with:

- **Backend**: FastAPI (async Python web framework)
- **Frontend**: HTMX (hypermedia-driven interactions)
- **Styling**: Custom CSS with responsive design
- **Charts**: Chart.js for data visualization
- **Templates**: Jinja2 for server-side rendering

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  HTML/CSS  │  │  HTMX.js │  │ Chart.js │  │  app.js   │ │
│  └────────────┘  └──────────┘  └──────────┘  └───────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Reverse Proxy (nginx)                   │
│                   SSL/TLS, Compression, Caching              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application (Gunicorn + Uvicorn)        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Security Middleware                         │   │
│  │     (Headers, CORS, CSP, Rate Limiting)               │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 ▼                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Route Handlers                          │   │
│  │  • / (index)    • /api/analyze   • /health           │   │
│  │  • /favicon     • /api/teams     • /api/cache        │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 ▼                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Business Logic Layer                       │   │
│  │  • TeamProcessor   • PlayoffCalculator                │   │
│  │  • ScrabbleScorer  • Cache Manager                    │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 ▼                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Data Layer                               │   │
│  │  • Pydantic Models  • In-Memory Cache                 │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 ▼                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             NHL API Client                            │   │
│  │  • HTTP Client  • Retry Logic  • Rate Limiting        │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼─────────────────────────────────────────┘
                  │ HTTPS
                  ▼
          ┌───────────────┐
          │   NHL API     │
          │ api-web.nhle  │
          └───────────────┘
```

## Component Details

### FastAPI Application

**File**: `src/nhl_scrabble/web/app.py`

FastAPI provides:

- **Async/Await**: Non-blocking I/O for concurrent requests
- **Auto Documentation**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Type Validation**: Pydantic models for request/response validation
- **Dependency Injection**: Clean separation of concerns
- **OpenAPI Schema**: Machine-readable API specification

**Why FastAPI?**

- Fastest Python web framework (benchmarks comparable to Node.js/Go)
- Built-in async support (crucial for I/O-bound NHL API calls)
- Automatic API documentation
- Type safety with Pydantic
- Modern Python 3.10+ features (type hints, async/await)

### Middleware Stack

#### 1. SecurityHeadersMiddleware

**Purpose**: Add security headers to all responses

**Headers Added**:

```python
X-Content-Type-Options: nosniff          # Prevent MIME sniffing
X-Frame-Options: DENY                    # Prevent clickjacking
X-XSS-Protection: 1; mode=block          # XSS protection
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: ...             # Restrict resource loading
```

**Why?** Defense-in-depth security following OWASP recommendations.

#### 2. CORSMiddleware

**Purpose**: Control cross-origin requests

**Configuration**:

```python
allow_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]  # Dev only
allow_methods = ["GET", "POST"]
allow_credentials = True
```

**Production**: Configured via environment variable `NHL_SCRABBLE_CORS_ORIGINS`.

### API Endpoints

#### GET / (Root)

**Purpose**: Serve main web interface

**Returns**: Rendered HTML from `templates/index.html`

**Caching**: Browser caches static assets, HTML is always fresh

#### GET /health

**Purpose**: Health check for monitoring

**Returns**: JSON with status, version, timestamp

**Use Cases**:

- Uptime monitoring (UptimeRobot, Pingdom)
- Load balancer health checks
- Container orchestration (Kubernetes probes)

#### POST /api/analyze

**Purpose**: Run NHL Scrabble analysis

**Request Body**:

```json
{
  "top_players": 20,        // 1-100
  "top_team_players": 5,    // 1-30
  "use_cache": true         // boolean
}
```

**Response**: Complete analysis results (players, teams, standings, playoffs, stats)

**Caching**: Results cached for 1 hour

**Flow**:

1. Check cache (if `use_cache: true`)
1. If cache miss or expired:
   - Fetch team standings from NHL API
   - For each team, fetch current roster
   - Calculate Scrabble scores for all players
   - Aggregate team scores
   - Calculate playoff standings
   - Build response
   - Cache result
1. Return JSON

#### GET /api/analyze

**Purpose**: HTMX-compatible GET endpoint

**Query Params**: `top_players`, `top_team_players`, `use_cache`

**Returns**:

- **HTMX request** (`HX-Request: true` header): HTML fragment from `results.html`
- **Regular request**: JSON (same as POST)

**Why?** HTMX uses GET for dynamic updates, needs HTML fragments.

#### GET /api/teams/{abbrev}

**Purpose**: Get specific team details

**Example**: `/api/teams/TOR` → Toronto Maple Leafs

**Returns**: Team object with roster and scores

**Caching**: Searches analysis cache

#### DELETE /api/cache/clear

**Purpose**: Clear analysis cache

**Use Case**: Force fresh data fetch

#### GET /api/cache/stats

**Purpose**: View cache statistics

**Returns**: Cache size, entries, age, expiration

### Templates (Jinja2)

#### base.html

**Purpose**: Base template with common structure

**Includes**:

- HTML5 doctype and semantic markup
- SEO meta tags (description, keywords, Open Graph, Twitter Card)
- Security headers
- Responsive viewport settings
- Navigation header
- Footer
- Script loading order

**Blocks**:

```jinja2
{% block title %}        <!-- Page title -->
{% block og_title %}     <!-- Open Graph title -->
{% block extra_css %}    <!-- Additional CSS -->
{% block content %}      <!-- Main content -->
{% block extra_js %}     <!-- Additional JS -->
```

#### index.html

**Purpose**: Main landing page

**Features**:

- Analysis form (top players, top team players, cache option)
- "Run Analysis" button with HTMX
- Loading indicator
- Error handling
- Results container (populated by HTMX)

**HTMX Usage**:

```html
<button hx-get="/api/analyze" hx-target="#results" hx-indicator="#loading">
  Run Analysis
</button>
```

#### results.html

**Purpose**: Analysis results template (HTMX fragment)

**Sections**:

1. **Statistics Summary** - Total players, teams, scores
1. **Top Players Table** - Sortable table
1. **Team Standings** - Sortable with expand/collapse
1. **Division Standings** - Grouped by division
1. **Conference Standings** - Eastern vs Western
1. **Playoff Bracket** - Mock playoff matchups
1. **Charts** - Score distribution, team comparison

### Static Assets

#### CSS (style.css)

**Structure**:

```css
/* 1. CSS Variables (theme colors, spacing) */
:root {
  --primary-color: #0066cc;
  --spacing-unit: 8px;
}

/* 2. Reset and Base Styles */

/* 3. Layout (flexbox, grid) */

/* 4. Components (buttons, tables, cards) */

/* 5. Utilities (text align, spacing) */

/* 6. Media Queries (responsive) */
@media (max-width: 768px) { ... }
```

**Design System**:

- **Colors**: Primary blue, secondary gray, success green, error red
- **Typography**: System font stack for performance
- **Spacing**: 8px grid system
- **Breakpoints**: 768px (tablet), 1024px (desktop)

**Accessibility**:

- WCAG 2.1 AA color contrast (4.5:1 minimum)
- Focus indicators on all interactive elements
- Reduced motion support via `prefers-reduced-motion`

#### JavaScript Modules

**Module System**: ES6 modules loaded in order

**Loading Order** (defined in `base.html`):

1. **Core modules** (load first):

   - `errors.js` - Error handling and display
   - `ui.js` - UI utilities (loading states, toasts)
   - `nav.js` - Navigation (mobile menu, smooth scroll)

1. **Feature modules**:

   - `table-sort.js` - Table sorting functionality
   - `export.js` - Data export (JSON, CSV, PDF)
   - `charts.js` - Chart.js wrapper and visualizations

1. **Main application**:

   - `app.js` - Application initialization and orchestration

**Why this order?**

- Core modules provide utilities used by feature modules
- Feature modules are independent and can load in any order
- Main app orchestrates everything after dependencies loaded

##### errors.js

**Purpose**: Centralized error handling

**Functions**:

```javascript
ErrorHandler.showError(message, type='error')  // Display error toast
ErrorHandler.handleApiError(response)          // Parse and show API errors
ErrorHandler.clearErrors()                     // Clear all error messages
```

##### ui.js

**Purpose**: UI utilities and helpers

**Functions**:

```javascript
UI.showLoading(element)         // Show loading spinner
UI.hideLoading(element)         // Hide loading spinner
UI.showToast(message, type)     // Show toast notification
UI.scrollToElement(element)     // Smooth scroll to element
UI.toggleElement(element)       // Show/hide toggle
```

##### nav.js

**Purpose**: Navigation functionality

**Features**:

- Mobile hamburger menu toggle
- Smooth scrolling for anchor links
- Active nav item highlighting
- Close menu on outside click

##### table-sort.js

**Purpose**: Client-side table sorting

**Features**:

- Click column header to sort
- Numeric and string sorting
- Sort direction indicator (▲▼)
- Maintains data types (numbers vs strings)

**Usage**:

```javascript
TableSort.init('.sortable-table')  // Initialize all sortable tables
```

##### export.js

**Purpose**: Data export functionality

**Formats**:

- **JSON**: Machine-readable, preserves data types
- **CSV**: Spreadsheet-compatible, good for Excel
- **PDF**: Printable reports (requires jsPDF library)

**Functions**:

```javascript
DataExport.exportJSON(data, filename)
DataExport.exportCSV(data, filename)
DataExport.exportPDF(data, filename)
```

##### charts.js

**Purpose**: Data visualization with Chart.js

**Charts**:

1. **Score Distribution** - Histogram of player scores
1. **Team Comparison** - Horizontal bar chart
1. **Conference Breakdown** - Pie chart

**Features**:

- Responsive sizing
- Interactive tooltips
- Color-blind friendly palette
- Accessible labels

##### app.js

**Purpose**: Main application logic

**Responsibilities**:

- Initialize all modules on page load
- Coordinate HTMX events
- Handle form submissions
- Manage application state
- Set up event listeners

### Caching Strategy

**Cache Type**: In-memory dictionary (Python)

**Key Format**: `{top_players}_{top_team_players}`

**TTL**: 1 hour (3600 seconds)

**Cache Hit**: Returns cached data with `cache_hit: true`

**Cache Miss**: Fetches from NHL API, caches result

**Limitations**:

- Cleared on application restart
- Not shared across workers (each worker has own cache)
- Limited by available memory

**Future Improvements**:

- Redis for shared cache across workers
- Configurable TTL
- Cache warming on startup
- Stale-while-revalidate strategy

### Data Flow

#### Analysis Request Flow

```
1. User clicks "Run Analysis"
2. HTMX sends GET /api/analyze?top_players=20
3. FastAPI receives request, extracts params
4. Check cache with key "20_5"
5. If cache hit (< 1 hour old):
   → Return cached data (instant)
6. If cache miss:
   → Call NHLApiClient to fetch standings
   → For each team (32 teams):
     → Fetch roster from /v1/roster/{abbrev}/current
     → Calculate Scrabble score for each player
     → Aggregate to team total
   → Calculate playoff standings
   → Cache result
   → Return data
7. HTMX receives HTML fragment
8. HTMX swaps content into #results div
9. JavaScript initializes charts and tables
10. User sees results
```

**Performance**:

- **Cache hit**: ~5ms response time
- **Cache miss**: ~30 seconds (32 API calls to NHL)
- **Subsequent requests**: Instant (from cache)

## Design Decisions

### Why HTMX Instead of React/Vue?

**Advantages**:

- **Simplicity**: No build step, no npm, no bundler
- **Performance**: Less JavaScript to download and parse
- **SEO**: Server-rendered HTML (better for crawlers)
- **Progressive Enhancement**: Works without JavaScript for basic functionality
- **Team Skill**: Python developers can contribute without learning React

**Trade-offs**:

- Less interactive than full SPA
- More server load (rendering HTML)
- Fewer reusable components

**Decision**: HTMX is perfect for this use case (data display with moderate interactivity).

### Why In-Memory Cache Instead of Redis?

**Advantages**:

- **Zero Dependencies**: No Redis server required
- **Simplicity**: No network calls for cache
- **Fast**: Nanosecond lookup time
- **Easy Deployment**: Works everywhere Python runs

**Trade-offs**:

- Lost on restart (acceptable for public data)
- Not shared across workers (acceptable for low traffic)
- Limited by memory (NHL data is small ~1MB)

**Decision**: In-memory cache is sufficient for current scale. Migrate to Redis if:

- Traffic exceeds 1000 requests/minute
- Multiple workers/instances needed
- Cache warming on startup required

### Why FastAPI Instead of Flask/Django?

**Advantages**:

- **Performance**: Async/await for concurrent NHL API calls
- **Type Safety**: Pydantic validates all I/O
- **Modern**: Leverages Python 3.10+ features
- **Documentation**: Auto-generated API docs
- **Future-Proof**: Built for async, microservices, modern APIs

**Trade-offs**:

- Smaller community than Flask
- Fewer plugins/extensions
- Steeper learning curve (async/await)

**Decision**: FastAPI is the best choice for modern API-driven web apps.

## Security Considerations

### Content Security Policy (CSP)

Prevents XSS attacks by restricting resource loading:

```
default-src 'self'                           # Only load from same origin
style-src 'self' 'unsafe-inline'             # Inline styles allowed (for dynamic styling)
script-src 'self' 'unsafe-inline' cdn.js...  # Inline JS + trusted CDNs
img-src 'self' data:                         # Images from self + data URIs
```

**Trade-off**: `'unsafe-inline'` allows inline scripts, but needed for HTMX and Chart.js.

### CORS Configuration

**Development**: Localhost only

**Production**: Must configure allowed origins via `NHL_SCRABBLE_CORS_ORIGINS`

**Why?** Prevents unauthorized sites from accessing the API.

### Input Validation

**Pydantic Models**: Validate all input:

```python
class AnalysisRequest(BaseModel):
    top_players: int = Field(ge=1, le=100)  # 1-100 only
    top_team_players: int = Field(ge=1, le=30)
    use_cache: bool = Field(default=True)
```

**FastAPI**: Returns 422 Unprocessable Entity for invalid input.

### Rate Limiting

**Current**: None (public data, low traffic)

**Future**: Add rate limiting for production:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/analyze")
@limiter.limit("10/minute")
async def analyze(...):
    ...
```

## Performance Optimizations

### 1. Async I/O

FastAPI's async/await allows concurrent requests without blocking:

```python
async def analyze(...):
    # Multiple requests can process simultaneously
    with NHLApiClient() as client:
        teams = client.fetch_all_teams()  # Blocking I/O
```

**Future**: Make NHLApiClient fully async with `httpx.AsyncClient`.

### 2. Response Compression

Nginx/Caddy compresses responses (gzip/brotli):

- **HTML**: ~70% compression (4KB → 1.2KB)
- **JSON**: ~80% compression (100KB → 20KB)
- **CSS/JS**: ~60% compression

### 3. Static Asset Caching

Browser caches CSS/JS with long expiration:

```nginx
location /static {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Result**: CSS/JS only downloaded once.

### 4. HTTP/2

Nginx with HTTP/2 multiplexes requests over single connection:

- Fewer TCP connections
- Header compression
- Server push (for critical resources)

### 5. CDN for Libraries

Chart.js and HTMX loaded from CDN (jsDelivr):

- Geographic distribution (low latency)
- Likely already cached (used by other sites)
- Offloads bandwidth from app server

## Testing Strategy

### Unit Tests

**Location**: `tests/unit/test_web_*.py`

**Coverage**: Business logic, data transformations, scoring

### Integration Tests

**Location**: `tests/integration/test_web.py`

**Coverage**:

- API endpoints
- Request/response validation
- Error handling
- Caching behavior
- Security headers
- CORS

**Method**: FastAPI TestClient (doesn't require running server)

### Manual Testing

**Browsers**: Chrome, Firefox, Safari, Edge

**Mobile**: iOS Safari, Chrome Android

**Tools**:

- **Lighthouse**: Performance, accessibility, SEO scores
- **WAVE**: Accessibility checker
- **Chrome DevTools**: Network, performance profiling

### Performance Testing

**Tool**: Lighthouse CI, k6, or wrk

**Metrics**:

- **Time to First Byte (TTFB)**: < 200ms
- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Total Blocking Time (TBT)**: < 300ms

## Accessibility

**WCAG 2.1 Level AA Compliance**:

- Semantic HTML (`<header>`, `<main>`, `<nav>`, `<footer>`)
- ARIA labels for dynamic content
- Keyboard navigation support
- Focus indicators
- Color contrast ratios ≥ 4.5:1
- Responsive text sizing
- Skip navigation links

**Screen Reader Support**:

- Table headers (`<th scope="col">`)
- Form labels (`<label for="...">`)
- Status updates announced
- Error messages associated with inputs

## Future Enhancements

### Short Term

- [ ] Add rate limiting (slowapi)
- [ ] Implement Redis caching
- [ ] Add WebSocket for real-time updates
- [ ] Export to Excel (openpyxl)
- [ ] Print-friendly CSS

### Medium Term

- [ ] User accounts and saved analyses
- [ ] Historical data tracking
- [ ] Email reports
- [ ] API authentication
- [ ] GraphQL endpoint

### Long Term

- [ ] Real-time playoff bracket updates
- [ ] Social sharing
- [ ] Mobile app (React Native)
- [ ] Webhooks for integrations
- [ ] Multi-language support

## Related Documentation

- [Use Web Interface](../how-to/use-web-interface.md)
- [Deploy Web Interface](../how-to/deploy-web-interface.md)
- [Environment Variables](../reference/environment-variables.md)
- [API Reference](../reference/api.md)
