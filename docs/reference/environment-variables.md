# Environment Variables Reference

Complete list of all environment variables supported by NHL Scrabble.

## Quick Reference

| Variable                        | Type   | Default                   | Description              |
| ------------------------------- | ------ | ------------------------- | ------------------------ |
| `NHL_SCRABBLE_API_TIMEOUT`      | int    | 10                        | API timeout (seconds)    |
| `NHL_SCRABBLE_API_RETRIES`      | int    | 3                         | Retry attempts           |
| `NHL_SCRABBLE_RATE_LIMIT_DELAY` | float  | 0.3                       | Request delay (seconds)  |
| `NHL_SCRABBLE_MAX_CONCURRENT`   | int    | 5                         | Concurrent API requests  |
| `NHL_SCRABBLE_CACHE_ENABLED`    | bool   | true                      | Enable caching           |
| `NHL_SCRABBLE_CACHE_EXPIRY`     | int    | 3600                      | Cache duration (seconds) |
| `NHL_SCRABBLE_OUTPUT_FORMAT`    | string | text                      | Output format            |
| `NHL_SCRABBLE_TOP_PLAYERS`      | int    | 20                        | Top players count        |
| `NHL_SCRABBLE_TOP_TEAM_PLAYERS` | int    | 5                         | Per-team players         |
| `NHL_SCRABBLE_VERBOSE`          | bool   | false                     | Verbose logging          |
| `NHL_SCRABBLE_SANITIZE_LOGS`    | bool   | true                      | Sanitize secrets         |
| `NHL_SCRABBLE_WEB_HOST`         | string | 127.0.0.1                 | Web server host          |
| `NHL_SCRABBLE_WEB_PORT`         | int    | 8000                      | Web server port          |
| `NHL_SCRABBLE_WEB_WORKERS`      | int    | 4                         | Gunicorn workers         |
| `NHL_SCRABBLE_CORS_ORIGINS`     | string | http://localhost:8000,... | Allowed CORS origins     |
| `NHL_SCRABBLE_CACHE_TTL`        | int    | 3600                      | Web cache TTL (seconds)  |
| `NHL_SCRABBLE_LOG_LEVEL`        | string | INFO                      | Logging level            |
| `NHL_SCRABBLE_LOG_FORMAT`       | string | text                      | Log format (text/json)   |

## API Configuration

### NHL_SCRABBLE_API_TIMEOUT

**Type**: Integer
**Default**: 10
**Description**: Maximum time in seconds to wait for API response.

**Example**:

```bash
export NHL_SCRABBLE_API_TIMEOUT=30
```

### NHL_SCRABBLE_API_RETRIES

**Type**: Integer
**Default**: 3
**Description**: Number of retry attempts on API failure.

**Example**:

```bash
export NHL_SCRABBLE_API_RETRIES=5
```

### NHL_SCRABBLE_RATE_LIMIT_DELAY

**Type**: Float
**Default**: 0.3
**Description**: Delay in seconds between API requests to respect rate limits.

**Example**:

```bash
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
```

### NHL_SCRABBLE_MAX_CONCURRENT

**Type**: Integer
**Default**: 5
**Description**: Maximum number of concurrent API requests for fetching team rosters.

Controls parallelism when fetching NHL team data. Higher values provide better performance
but may trigger rate limiting. Recommended range: 5-10.

**Performance Impact**:

- `1` (sequential): ~10 seconds for 32 teams
- `5` (default): ~2 seconds for 32 teams (5x speedup)
- `10` (high): ~1.5 seconds for 32 teams (7x speedup)

**Example**:

```bash
# Conservative (safe, reliable)
export NHL_SCRABBLE_MAX_CONCURRENT=3

# Default (balanced performance)
export NHL_SCRABBLE_MAX_CONCURRENT=5

# Aggressive (maximum performance)
export NHL_SCRABBLE_MAX_CONCURRENT=10

# Sequential (debugging, no parallelism)
export NHL_SCRABBLE_MAX_CONCURRENT=1
```

## Caching

### NHL_SCRABBLE_CACHE_ENABLED

**Type**: Boolean
**Default**: true
**Description**: Enable/disable API response caching.

**Example**:

```bash
export NHL_SCRABBLE_CACHE_ENABLED=false
```

### NHL_SCRABBLE_CACHE_EXPIRY

**Type**: Integer
**Default**: 3600
**Description**: Cache expiration time in seconds.

**Example**:

```bash
export NHL_SCRABBLE_CACHE_EXPIRY=7200  # 2 hours
```

## Output

### NHL_SCRABBLE_OUTPUT_FORMAT

**Type**: String (text|json)
**Default**: text
**Description**: Default output format.

**Example**:

```bash
export NHL_SCRABBLE_OUTPUT_FORMAT=json
```

### NHL_SCRABBLE_TOP_PLAYERS

**Type**: Integer
**Default**: 20
**Description**: Number of top players to show in league rankings.

**Example**:

```bash
export NHL_SCRABBLE_TOP_PLAYERS=50
```

### NHL_SCRABBLE_TOP_TEAM_PLAYERS

**Type**: Integer
**Default**: 5
**Description**: Number of top players to show per team.

**Example**:

```bash
export NHL_SCRABBLE_TOP_TEAM_PLAYERS=10
```

## Logging

### NHL_SCRABBLE_VERBOSE

**Type**: Boolean
**Default**: false
**Description**: Enable verbose (DEBUG level) logging.

**Example**:

```bash
export NHL_SCRABBLE_VERBOSE=true
```

### NHL_SCRABBLE_SANITIZE_LOGS

**Type**: Boolean
**Default**: true
**Description**: Sanitize sensitive data (API keys, tokens) from logs.

**Example**:

```bash
export NHL_SCRABBLE_SANITIZE_LOGS=false  # Only for debugging
```

### NHL_SCRABBLE_LOG_LEVEL

**Type**: String (DEBUG|INFO|WARNING|ERROR|CRITICAL)
**Default**: INFO
**Description**: Logging level for application logs.

**Example**:

```bash
export NHL_SCRABBLE_LOG_LEVEL=DEBUG  # Verbose logging
export NHL_SCRABBLE_LOG_LEVEL=WARNING  # Only warnings and errors
```

### NHL_SCRABBLE_LOG_FORMAT

**Type**: String (text|json)
**Default**: text
**Description**: Log output format. Use `json` for structured logging in production.

**Example**:

```bash
export NHL_SCRABBLE_LOG_FORMAT=json  # Structured logs for parsing
```

## Web Server Configuration

### NHL_SCRABBLE_WEB_HOST

**Type**: String
**Default**: 127.0.0.1
**Description**: Host address for web server. Use `0.0.0.0` to bind to all interfaces.

**Security Note**: Only use `0.0.0.0` behind a reverse proxy (nginx, Caddy) with proper firewall rules.

**Example**:

```bash
# Development (local only)
export NHL_SCRABBLE_WEB_HOST=127.0.0.1

# Production (behind reverse proxy)
export NHL_SCRABBLE_WEB_HOST=0.0.0.0
```

### NHL_SCRABBLE_WEB_PORT

**Type**: Integer
**Default**: 8000
**Description**: Port for web server to listen on.

**Example**:

```bash
export NHL_SCRABBLE_WEB_PORT=5000
```

### NHL_SCRABBLE_WEB_WORKERS

**Type**: Integer
**Default**: 4
**Description**: Number of Gunicorn worker processes for production.

**Recommended Formula**: `(2 * CPU_COUNT) + 1`

**Example**:

```bash
# 2 CPU cores → 5 workers
export NHL_SCRABBLE_WEB_WORKERS=5

# 4 CPU cores → 9 workers
export NHL_SCRABBLE_WEB_WORKERS=9
```

### NHL_SCRABBLE_CORS_ORIGINS

**Type**: String (comma-separated URLs)
**Default**: `http://localhost:8000,http://127.0.0.1:8000`
**Description**: Allowed CORS origins for cross-origin requests.

**Security Note**: In production, only list your actual domain(s).

**Example**:

```bash
# Development
export NHL_SCRABBLE_CORS_ORIGINS="http://localhost:8000,http://localhost:3000"

# Production
export NHL_SCRABBLE_CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Multiple domains
export NHL_SCRABBLE_CORS_ORIGINS="https://app.example.com,https://api.example.com"
```

### NHL_SCRABBLE_CACHE_TTL

**Type**: Integer
**Default**: 3600
**Description**: Time-to-live for web interface analysis cache (in seconds).

**Note**: This is separate from NHL API cache (`NHL_SCRABBLE_CACHE_EXPIRY`). Web cache stores complete analysis results.

**Example**:

```bash
# 30 minutes
export NHL_SCRABBLE_CACHE_TTL=1800

# 2 hours
export NHL_SCRABBLE_CACHE_TTL=7200

# Disable web caching (always fetch fresh)
export NHL_SCRABBLE_CACHE_TTL=0
```

## Setting Variables

### Temporary (current shell)

```bash
export NHL_SCRABBLE_API_TIMEOUT=30
nhl-scrabble analyze
```

### Persistent (shell profile)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export NHL_SCRABBLE_API_TIMEOUT=30
export NHL_SCRABBLE_OUTPUT_FORMAT=json
```

### Via .env file

Create `.env` in project directory:

```env
NHL_SCRABBLE_API_TIMEOUT=30
NHL_SCRABBLE_OUTPUT_FORMAT=json
```

## Related

- [Configuration Reference](configuration.md) - All configuration options
- [CLI Reference](cli.md) - Command-line overrides
- [How to Configure](../how-to/configure-api-settings.md) - Configuration guide
