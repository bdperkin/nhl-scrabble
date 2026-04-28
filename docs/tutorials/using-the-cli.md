# Using the NHL Scrabble CLI

Complete guide to using the NHL Scrabble command-line interface.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Output Formats](#output-formats)
- [Customization Options](#customization-options)
- [Web Interface](#web-interface)
- [Interactive Dashboard](#interactive-dashboard)
- [Configuration](#configuration)
- [Advanced Patterns](#advanced-patterns)

## Basic Usage

### Running the Analyzer

```bash
# Run analysis with default settings (shows progress bars)
nhl-scrabble analyze

# Using Python module directly
python -m nhl_scrabble analyze
```

### Help and Version

```bash
# Show version
nhl-scrabble -V               # Short option
nhl-scrabble --version        # Long option

# Show help
nhl-scrabble -h               # Short option
nhl-scrabble --help           # Long option
nhl-scrabble analyze -h       # Command help
```

### Verbose Logging

```bash
# Enable verbose logging (with colorized output in terminal)
nhl-scrabble analyze -v       # Short option
nhl-scrabble analyze --verbose # Long option

# Disable colors (for scripts/pipes)
NO_COLOR=1 nhl-scrabble analyze
```

## Output Formats

### Text Output (Default)

Human-readable format with rich formatting:

```bash
# Default text output to terminal
nhl-scrabble analyze

# Save to file
nhl-scrabble analyze -o report.txt
nhl-scrabble analyze --output report.txt
```

### JSON Output

Machine-readable format for integrations:

```bash
# JSON output to terminal
nhl-scrabble analyze --format json

# Save JSON to file
nhl-scrabble analyze --format json -o report.json

# Pretty-print JSON (with jq)
nhl-scrabble analyze --format json | jq '.'
```

### HTML Output

Browser-friendly format:

```bash
# Generate HTML report
nhl-scrabble analyze --format html -o report.html

# Open in browser (macOS)
nhl-scrabble analyze --format html -o report.html && open report.html

# Open in browser (Linux)
nhl-scrabble analyze --format html -o report.html && xdg-open report.html
```

## Customization Options

### Top Players

Control how many top players are shown:

```bash
# Show top 30 players (default: 20)
nhl-scrabble analyze --top-players 30

# Show top 50 players
nhl-scrabble analyze --top-players 50
```

### Team Players

Control how many players per team:

```bash
# Show top 10 players per team (default: 5)
nhl-scrabble analyze --top-team-players 10

# Show top 3 players per team
nhl-scrabble analyze --top-team-players 3
```

### Combining Options

```bash
# Custom top players, JSON output, save to file
nhl-scrabble analyze --top-players 30 --format json -o report.json

# Verbose mode with custom team players
nhl-scrabble analyze -v --top-team-players 10

# All options together
nhl-scrabble analyze \
  --verbose \
  --format json \
  --output report.json \
  --top-players 50 \
  --top-team-players 10
```

## Web Interface

### Starting the Server

```bash
# Start web server (default: http://localhost:8000)
nhl-scrabble serve

# Custom host and port
nhl-scrabble serve --host 0.0.0.0 --port 5000

# Enable auto-reload for development
nhl-scrabble serve --reload

# Production mode (no auto-reload)
nhl-scrabble serve --host 0.0.0.0 --port 8000 --no-reload
```

### Server Options

```bash
# Show all server options
nhl-scrabble serve --help

# Common combinations
nhl-scrabble serve --reload --verbose  # Development mode
nhl-scrabble serve --host 0.0.0.0     # Allow external connections
```

### Accessing the Web Interface

Once the server is running, access:

- **Main Dashboard**: <http://localhost:8000/>
- **API Documentation**: <http://localhost:8000/docs> (Swagger UI)
- **Alternative API Docs**: <http://localhost:8000/redoc> (ReDoc)
- **Health Check**: <http://localhost:8000/health>

## Interactive Dashboard

### Starting the Dashboard

```bash
# Launch interactive dashboard
nhl-scrabble dashboard

# Dashboard with verbose logging
nhl-scrabble dashboard --verbose
```

### Dashboard Features

The interactive dashboard provides:

- **Team Browsing**: View all teams and their scores
- **Player Search**: Find players by name
- **Division View**: Filter teams by division
- **Conference View**: Eastern vs Western breakdown
- **Standings**: Team, division, and conference standings
- **Playoff Bracket**: Mock playoff matchups
- **Statistics**: League-wide stats and fun facts

### Dashboard Commands

While in the dashboard, use these commands:

```text
help          Show all available commands
list teams    List all teams
show [team]   Show team details
top [N]       Show top N players
division [D]  Show teams in division
conference [C] Show teams in conference
standings     Show standings
playoff       Show playoff bracket
stats         Show statistics
exit          Exit dashboard
```

## Configuration

### Environment Variables

Configure behavior via environment variables:

```bash
# Set environment variables
export NHL_SCRABBLE_API_TIMEOUT=15
export NHL_SCRABBLE_API_RETRIES=5
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
export NHL_SCRABBLE_TOP_PLAYERS=30
export NHL_SCRABBLE_VERBOSE=true

# Then run
nhl-scrabble analyze
```

### Configuration File

Create a `.env` file in your project:

```bash
# .env file
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
NHL_SCRABBLE_TOP_PLAYERS=30
NHL_SCRABBLE_TOP_TEAM_PLAYERS=10
NHL_SCRABBLE_VERBOSE=true
NHL_SCRABBLE_OUTPUT_FORMAT=json
```

Then the configuration is automatically loaded:

```bash
nhl-scrabble analyze  # Uses .env settings
```

### Configuration Priority

Configuration sources in order of precedence (highest to lowest):

1. Command-line arguments
1. Environment variables
1. `.env` file
1. Default values

Example:

```bash
# .env has TOP_PLAYERS=30
# Command-line overrides it
nhl-scrabble analyze --top-players 50  # Uses 50, not 30
```

## Advanced Patterns

### Scripting and Automation

```bash
# Generate report and extract data with jq
nhl-scrabble analyze --format json | jq '.top_players[0:5]'

# Save report with timestamp
nhl-scrabble analyze -o "report-$(date +%Y%m%d).txt"

# Run and check exit code
if nhl-scrabble analyze --format json -o report.json; then
    echo "Analysis successful"
else
    echo "Analysis failed"
    exit 1
fi
```

### Pipeline Integration

```bash
# Generate JSON and process with other tools
nhl-scrabble analyze --format json | \
    jq '.team_standings | sort_by(.total) | reverse | .[0:3]' | \
    tee top-teams.json

# Convert JSON to CSV (with jq + @csv)
nhl-scrabble analyze --format json | \
    jq -r '.top_players[] | [.name, .team, .score] | @csv' > players.csv
```

### Error Handling

```bash
# Redirect verbose output to log file
nhl-scrabble analyze -v 2> analysis.log

# Suppress all output except errors
nhl-scrabble analyze 2>&1 > /dev/null

# Retry on failure
for i in {1..3}; do
    nhl-scrabble analyze && break || sleep 5
done
```

### Performance Optimization

```bash
# Reduce API calls (fewer retries, longer timeout)
export NHL_SCRABBLE_API_RETRIES=3
export NHL_SCRABBLE_API_TIMEOUT=20
nhl-scrabble analyze

# Faster analysis (fewer players displayed)
nhl-scrabble analyze --top-players 10 --top-team-players 3
```

## See Also

- [CLI Reference](../reference/cli.md) - Complete command-line reference
- [Configuration Reference](../reference/configuration.md) - All configuration options
- Understanding Output - Interpreting report data
- [Web Interface Guide](../how-to/use-web-interface.md) - Using the web UI

## Troubleshooting

### Common Issues

**"Connection timeout" errors:**

```bash
# Increase timeout
export NHL_SCRABBLE_API_TIMEOUT=30
nhl-scrabble analyze
```

**"Rate limited" errors:**

```bash
# Increase delay between requests
export NHL_SCRABBLE_RATE_LIMIT_DELAY=1.0
nhl-scrabble analyze
```

**Missing dependencies:**

```bash
# Reinstall package
pip install --force-reinstall nhl-scrabble
```

For more help, see [SUPPORT.md](../../SUPPORT.md).
