# How to Debug API Issues

Diagnose and fix NHL API connection problems.

## Problem

You're experiencing errors or timeouts when fetching NHL data.

## Common Issues

### Connection timeout

**Symptoms**: "Connection timeout" error after 10-15 seconds.

**Solutions**:

```bash
# Increase timeout
export NHL_SCRABBLE_API_TIMEOUT=60
nhl-scrabble analyze --verbose

# Check network connection
ping api-web.nhle.com

# Try with retries
export NHL_SCRABBLE_API_RETRIES=10
```

### 404 errors

**Symptoms**: "Team not found" or "404 Not Found" errors.

**Solutions**:

- NHL API may have changed endpoints
- Team abbreviation may be wrong
- Check NHL API status: https://www.nhl.com/info/api-status

### Rate limiting

**Symptoms**: Requests failing intermittently, "429 Too Many Requests".

**Solutions**:

```bash
# Increase delay between requests
export NHL_SCRABBLE_RATE_LIMIT_DELAY=1.0  # 1 second delay
nhl-scrabble analyze
```

### Invalid JSON

**Symptoms**: "JSON decode error" messages.

**Solutions**:

```bash
# Enable verbose logging to see response
nhl-scrabble analyze --verbose --no-cache

# Clear cache in case of corrupted data
nhl-scrabble analyze --clear-cache
```

## Debugging workflow

1. **Enable verbose logging**:

```bash
nhl-scrabble analyze --verbose
```

2. **Check API directly**:

```bash
curl -v https://api-web.nhle.com/v1/standings/now
```

3. **Test with retries**:

```bash
export NHL_SCRABBLE_API_RETRIES=10
export NHL_SCRABBLE_API_TIMEOUT=60
nhl-scrabble analyze --verbose --no-cache
```

4. **Check logs** for specific error messages

## Related

- [Configure API Settings](configure-api-settings.md) - API configuration
- [NHL API Reference](../reference/nhl-api.md) - API endpoints
- [NHL API Strategy](../explanation/nhl-api-strategy.md) - How we use the API
