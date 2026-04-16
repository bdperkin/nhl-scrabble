# How to Configure API Settings

Customize NHL API behavior for your needs.

## Problem

You need to adjust API timeout, retries, rate limiting, or caching behavior.

## Solutions

### Via Environment Variables

```bash
# API timeout (seconds)
export NHL_SCRABBLE_API_TIMEOUT=30

# Number of retries on failure
export NHL_SCRABBLE_API_RETRIES=5

# Delay between requests (seconds)
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5

# Enable/disable caching
export NHL_SCRABBLE_CACHE_ENABLED=true

# Cache expiry (seconds)
export NHL_SCRABBLE_CACHE_EXPIRY=3600
```

### Via .env File

Create `.env` in project root:

```env
NHL_SCRABBLE_API_TIMEOUT=30
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
NHL_SCRABBLE_CACHE_ENABLED=true
NHL_SCRABBLE_CACHE_EXPIRY=3600
```

### Via Command-Line Options

```bash
# Disable cache for fresh data
nhl-scrabble analyze --no-cache

# Clear cache before running
nhl-scrabble analyze --clear-cache
```

## Common Scenarios

### Slow network connection

```bash
export NHL_SCRABBLE_API_TIMEOUT=60
export NHL_SCRABBLE_API_RETRIES=10
```

### Development/testing

```bash
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0  # No delays
export NHL_SCRABBLE_CACHE_ENABLED=false  # Fresh data always
```

### Production use

```bash
export NHL_SCRABBLE_API_TIMEOUT=15
export NHL_SCRABBLE_API_RETRIES=3
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.3
export NHL_SCRABBLE_CACHE_ENABLED=true
export NHL_SCRABBLE_CACHE_EXPIRY=7200  # 2 hours
```

## Related

- [Configuration Reference](../reference/configuration.md) - All configuration options
- [Environment Variables Reference](../reference/environment-variables.md) - Complete list
- [Debug API Issues](debug-api-issues.md) - Troubleshooting API problems
