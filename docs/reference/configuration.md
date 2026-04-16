# Configuration Reference

Complete reference for all NHL Scrabble configuration options.

## Overview

NHL Scrabble can be configured via:

1. **Environment variables** (recommended for deployment)
2. **Command-line options** (for ad-hoc usage)
3. **.env file** (for development)

**Priority**: Command-line > Environment variables > Defaults

## All Configuration Options

### API Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `NHL_SCRABBLE_API_TIMEOUT` | int | 10 | API request timeout in seconds |
| `NHL_SCRABBLE_API_RETRIES` | int | 3 | Number of retry attempts on failure |
| `NHL_SCRABBLE_RATE_LIMIT_DELAY` | float | 0.3 | Delay between requests in seconds |

**Example**:

```bash
export NHL_SCRABBLE_API_TIMEOUT=30
export NHL_SCRABBLE_API_RETRIES=5
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
```

### Caching Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `NHL_SCRABBLE_CACHE_ENABLED` | bool | true | Enable API response caching |
| `NHL_SCRABBLE_CACHE_EXPIRY` | int | 3600 | Cache expiry time in seconds |

**Example**:

```bash
export NHL_SCRABBLE_CACHE_ENABLED=true
export NHL_SCRABBLE_CACHE_EXPIRY=7200  # 2 hours
```

### Output Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `NHL_SCRABBLE_OUTPUT_FORMAT` | string | text | Output format: `text` or `json` |
| `NHL_SCRABBLE_TOP_PLAYERS` | int | 20 | Number of top players to show |
| `NHL_SCRABBLE_TOP_TEAM_PLAYERS` | int | 5 | Top players per team to show |

**Example**:

```bash
export NHL_SCRABBLE_OUTPUT_FORMAT=json
export NHL_SCRABBLE_TOP_PLAYERS=50
export NHL_SCRABBLE_TOP_TEAM_PLAYERS=10
```

### Logging Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `NHL_SCRABBLE_VERBOSE` | bool | false | Enable verbose (DEBUG) logging |
| `NHL_SCRABBLE_SANITIZE_LOGS` | bool | true | Sanitize secrets from logs |

**Example**:

```bash
export NHL_SCRABBLE_VERBOSE=true
export NHL_SCRABBLE_SANITIZE_LOGS=true
```

## Configuration File (.env)

Create `.env` in project root:

```env
# API Settings
NHL_SCRABBLE_API_TIMEOUT=30
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5

# Caching
NHL_SCRABBLE_CACHE_ENABLED=true
NHL_SCRABBLE_CACHE_EXPIRY=7200

# Output
NHL_SCRABBLE_OUTPUT_FORMAT=json
NHL_SCRABBLE_TOP_PLAYERS=50
NHL_SCRABBLE_TOP_TEAM_PLAYERS=10

# Logging
NHL_SCRABBLE_VERBOSE=false
NHL_SCRABBLE_SANITIZE_LOGS=true
```

## Command-Line Options

Override configuration via CLI:

```bash
nhl-scrabble analyze \
  --format json \
  --output report.json \
  --verbose \
  --top-players 100 \
  --top-team-players 15 \
  --no-cache
```

See [CLI Reference](cli.md) for all options.

## Configuration Scenarios

### Development

```env
NHL_SCRABBLE_VERBOSE=true
NHL_SCRABBLE_CACHE_ENABLED=false
NHL_SCRABBLE_RATE_LIMIT_DELAY=0
NHL_SCRABBLE_SANITIZE_LOGS=false
```

### Production

```env
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=3
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.3
NHL_SCRABBLE_CACHE_ENABLED=true
NHL_SCRABBLE_CACHE_EXPIRY=7200
NHL_SCRABBLE_SANITIZE_LOGS=true
```

### Slow Network

```env
NHL_SCRABBLE_API_TIMEOUT=60
NHL_SCRABBLE_API_RETRIES=10
NHL_SCRABBLE_RATE_LIMIT_DELAY=1.0
```

## Validation

Configuration values are validated at startup:

- **Timeouts**: Must be positive integers
- **Delays**: Must be non-negative floats
- **Counts**: Must be positive integers
- **Formats**: Must be `text` or `json`
- **Booleans**: `true`/`false`, `1`/`0`, `yes`/`no`

## Related

- [Environment Variables Reference](environment-variables.md) - Complete list
- [CLI Reference](cli.md) - Command-line options
- [How to Configure API Settings](../how-to/configure-api-settings.md) - Configuration guide
