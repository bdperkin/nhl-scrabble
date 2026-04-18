# Using the Web Interface

This guide shows you how to use the NHL Scrabble web interface to analyze player names in your browser.

## Quick Start

1. **Start the web server**:

   ```bash
   # Using uvicorn directly
   uvicorn nhl_scrabble.web.app:app --reload

   # Or specify host and port
   uvicorn nhl_scrabble.web.app:app --host 0.0.0.0 --port 8000
   ```

1. **Open your browser**: Navigate to `http://localhost:8000`

1. **Run an analysis**: Fill in the form and click "Analyze"

## Features

### Home Page

The home page (`/`) provides:

- **Analysis Form**: Configure and run NHL Scrabble analysis
- **Scrabble Values**: Reference table of letter point values
- **About Section**: Explanation of the scoring system

### API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Form Options

**Top Players to Display** (1-100)

- Number of highest-scoring players to show in results
- Default: 20 players
- Higher values take longer to load

**Top Players per Team** (1-30)

- Number of players to show per team in team results
- Default: 5 players per team
- Affects result detail level

**Use Cached Results**

- ✅ Enabled (default): Use cached API responses for faster results
- ❌ Disabled: Fetch fresh data from NHL API (slower but current)

### Results

Analysis results include:

- **Top Players**: Highest-scoring player names across the league
- **Team Standings**: Teams ranked by total roster score
- **Division Standings**: Teams within each division
- **Conference Standings**: Eastern and Western Conference standings
- **Playoff Bracket**: Mock playoff bracket based on scores

Results are currently displayed as formatted JSON. Enhanced visualization will be available in a future update.

## Usage Examples

### Quick Analysis (Fastest)

1. Keep default settings (20 players, 5 per team, cache enabled)
1. Click "Analyze"
1. Wait 2-5 seconds for cached results

### Detailed Analysis (Most Complete)

1. Set "Top Players" to 50
1. Set "Top Team Players" to 10
1. Enable cache
1. Click "Analyze"
1. Wait for results (may take longer on first run)

### Fresh Data Analysis

1. Disable "Use Cached Results"
1. Set your preferred player counts
1. Click "Analyze"
1. Wait for fresh data from NHL API (30-60 seconds)

## Navigation

- **Home**: Click the 🏒 logo or "Home" link
- **API Docs**: Click "API Docs" in navigation
- **GitHub**: Click "GitHub" for source code
- **Status**: Footer link to `/health` endpoint

## Mobile Usage

The web interface is fully responsive and works on mobile devices:

- **iOS Safari**: Tested and compatible
- **Chrome Android**: Tested and compatible
- **Other browsers**: Should work but not explicitly tested

On mobile:

- Form adapts to smaller screens
- Navigation collapses for easier access
- Results scroll smoothly
- Touch-friendly buttons and inputs

## Accessibility

The web interface follows accessibility best practices:

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **ARIA labels**: Navigation and form elements labeled
- **Keyboard navigation**: All features accessible via keyboard
- **Screen readers**: Compatible with NVDA, JAWS, VoiceOver

## Performance

**Caching**

- First run: 30-60 seconds (fetches from NHL API)
- Subsequent runs: 2-5 seconds (uses cached data)
- Cache expiry: Configurable via environment variables

**Optimization Tips**

- Use cache for faster results
- Lower player counts for quicker response
- Run during off-peak hours for NHL API reliability

## Troubleshooting

See [Troubleshooting Guide](troubleshooting-web.md) for common issues and solutions.

## Next Steps

- Read the [Deployment Guide](deploy-web-interface.md) to run in production
- Check [API Reference](../reference/api.md) for programmatic access
- See [Environment Variables](../reference/environment-variables.md) for configuration options
