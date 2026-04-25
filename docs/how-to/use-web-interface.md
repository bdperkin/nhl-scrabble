# How to Use the Web Interface

This guide explains how to use the NHL Scrabble web interface to analyze player names and view statistics.

## Starting the Server

### Development Mode

Start the development server with auto-reload:

```bash
# Using uvicorn directly
uvicorn nhl_scrabble.web.app:app --reload --port 8000

# Or using make (if configured)
make run-web

# Or using python -m
python -m uvicorn nhl_scrabble.web.app:app --reload --port 8000
```

The server will be available at: **http://localhost:8000**

### Production Mode

For production deployment, use a production server like Gunicorn:

```bash
# Install gunicorn
pip install gunicorn[setproctitle]

# Run with multiple workers
gunicorn nhl_scrabble.web.app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

See [Deploy Web Interface](deploy-web-interface.md) for full deployment guide.

## Using the Web Interface

### Main Page

1. **Open browser** to http://localhost:8000
1. You'll see the NHL Scrabble Analyzer homepage
1. Click **"Run Analysis"** button to start analysis

### Running Analysis

The analysis fetches current NHL roster data and calculates Scrabble scores:

**Options**:

- **Top Players**: Number of top players to display (1-100)
- **Top Team Players**: Number of top players per team (1-30)
- **Use Cache**: Use cached results if available (faster)

**Results Display**:

1. **Top Players** - Highest-scoring players across all teams
1. **Team Standings** - Teams ranked by total Scrabble score
1. **Division Standings** - Teams grouped by division
1. **Conference Standings** - Eastern vs Western conference
1. **Playoff Bracket** - Mock playoff bracket based on scores
1. **Statistics** - Overall statistics and insights

### Interactive Features

#### Table Sorting

Click column headers to sort tables:

- **Name** - Alphabetical sorting
- **Score** - Numerical sorting
- **Team** - Group by team

Click again to reverse sort order.

#### Data Export

Export results in multiple formats:

- **JSON** - Machine-readable format
- **CSV** - Spreadsheet-compatible
- **PDF** - Printable report (requires jsPDF)

Click the **Export** button and select your format.

#### Charts and Visualizations

View interactive charts:

- **Score Distribution** - Histogram of player scores
- **Team Comparison** - Bar chart comparing teams
- **Conference Breakdown** - Pie chart of conference totals

Charts are powered by Chart.js and are interactive (hover for details).

### Mobile Usage

The web interface is fully responsive and works on mobile devices:

- **Hamburger Menu** - Tap ☰ icon to open navigation
- **Touch Sorting** - Tap column headers to sort
- **Swipe Charts** - Swipe charts for interaction
- **Portrait Mode** - Optimized for phone screens

### Accessibility

The interface is designed for accessibility:

- **Keyboard Navigation** - Full keyboard support
- **Screen Readers** - ARIA labels and semantic HTML
- **High Contrast** - Good color contrast ratios
- **Focus Indicators** - Clear focus states for navigation

## API Endpoints

The web interface also exposes REST API endpoints.

### GET /health

Health check endpoint:

```bash
curl http://localhost:8000/health
```

**Response**:

```json
{
  "status": "healthy",
  "version": "0.0.1",
  "timestamp": "2026-04-21T12:00:00Z"
}
```

### POST /api/analyze

Run analysis via API:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"top_players": 20, "top_team_players": 5, "use_cache": true}'
```

**Response**: Complete analysis results in JSON format

### GET /api/analyze

Run analysis via GET (simpler):

```bash
curl "http://localhost:8000/api/analyze?top_players=20&top_team_players=5"
```

### GET /api/teams/{abbrev}

Get specific team details:

```bash
curl http://localhost:8000/api/teams/TOR
```

**Response**: Team details including roster and scores

### DELETE /api/cache/clear

Clear the analysis cache:

```bash
curl -X DELETE http://localhost:8000/api/cache/clear
```

### GET /api/cache/stats

View cache statistics:

```bash
curl http://localhost:8000/api/cache/stats
```

## Caching

The web interface caches analysis results for **1 hour** to improve performance.

**Cache Behavior**:

- First request: Fetches fresh data from NHL API (~30 seconds)
- Subsequent requests: Returns cached data instantly
- Cache expires: After 1 hour, next request fetches fresh data
- Manual clear: Use `/api/cache/clear` endpoint

**Disable Cache**:

To always fetch fresh data, set `use_cache: false`:

```json
{
  "top_players": 20,
  "top_team_players": 5,
  "use_cache": false
}
```

## Troubleshooting

### Server Won't Start

**Error**: `Address already in use`

**Solution**: Port 8000 is already in use. Try a different port:

```bash
uvicorn nhl_scrabble.web.app:app --reload --port 8001
```

### Templates Not Found

**Error**: `Templates not configured`

**Solution**: Ensure templates directory exists:

```bash
ls src/nhl_scrabble/web/templates/
```

If missing, the web package may not be installed correctly.

### Static Files Not Loading

**Error**: CSS/JS files return 404

**Solution**: Verify static files exist:

```bash
ls src/nhl_scrabble/web/static/
```

If missing, reinstall package:

```bash
pip install -e .
```

### Analysis Takes Too Long

**Issue**: First analysis is slow (~30 seconds)

**Explanation**: This is normal - the API must fetch all 32 team rosters from NHL API.

**Solutions**:

1. **Use cache**: Subsequent requests are instant with `use_cache: true`
1. **Reduce players**: Request fewer top players (doesn't affect speed much)
1. **Pre-warm cache**: Run analysis once to populate cache

### NHL API Unavailable

**Error**: `Analysis failed: NHL API unavailable`

**Explanation**: NHL API is down or rate-limiting

**Solutions**:

1. **Wait and retry**: NHL API may be temporarily unavailable
1. **Check status**: Visit https://api-web.nhle.com/v1/standings/now in browser
1. **Use cache**: If cache exists, use cached data

### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Explanation**: You're accessing the API from a different origin

**Solution**: The server allows localhost:8000 and 127.0.0.1:8000 by default. For other origins, see [Deploy Web Interface](deploy-web-interface.md) for CORS configuration.

## Performance Tips

1. **Use cache**: Enable caching for instant results
1. **Limit data**: Request only the players/teams you need
1. **Browser cache**: Browser caches static assets (CSS/JS)
1. **Compression**: Enable gzip compression in production
1. **CDN**: Use CDN for Chart.js and HTMX libraries

## Security Considerations

The web interface includes security features:

- **Security Headers**: X-Content-Type-Options, X-Frame-Options, CSP
- **CORS**: Limited to localhost in development
- **Input Validation**: All inputs validated via Pydantic
- **No Authentication**: Data is public, no auth required
- **Rate Limiting**: Consider adding for production (see deployment guide)

## Browser Support

**Supported Browsers**:

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Opera 76+

**Mobile Browsers**:

- iOS Safari 14+
- Chrome Android 90+
- Samsung Internet 14+

**JavaScript Required**: The interface requires JavaScript for full functionality.

## API Documentation

FastAPI provides automatic API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces let you:

- Explore all endpoints
- View request/response schemas
- Try API calls interactively
- Download OpenAPI specification

## Next Steps

- [Deploy to Production](deploy-web-interface.md)
- [Configure Environment Variables](../reference/environment-variables.md)
- [Understand Web Architecture](../explanation/web-architecture.md)
- [Contribute to Web Interface](../../CONTRIBUTING.md)

## Related Documentation

- [Installation](installation.md)
- [Run Tests](run-tests.md)
- [CLI Reference](../reference/cli.md)
- [Configuration Reference](../reference/configuration.md)
