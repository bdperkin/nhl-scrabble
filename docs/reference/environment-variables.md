# Environment Variables Reference

Complete list of all environment variables supported by NHL Scrabble.

## Quick Reference

| Variable                        | Type   | Default | Description              |
| ------------------------------- | ------ | ------- | ------------------------ |
| `NHL_SCRABBLE_API_TIMEOUT`      | int    | 10      | API timeout (seconds)    |
| `NHL_SCRABBLE_API_RETRIES`      | int    | 3       | Retry attempts           |
| `NHL_SCRABBLE_RATE_LIMIT_DELAY` | float  | 0.3     | Request delay (seconds)  |
| `NHL_SCRABBLE_CACHE_ENABLED`    | bool   | true    | Enable caching           |
| `NHL_SCRABBLE_CACHE_EXPIRY`     | int    | 3600    | Cache duration (seconds) |
| `NHL_SCRABBLE_OUTPUT_FORMAT`    | string | text    | Output format            |
| `NHL_SCRABBLE_TOP_PLAYERS`      | int    | 20      | Top players count        |
| `NHL_SCRABBLE_TOP_TEAM_PLAYERS` | int    | 5       | Per-team players         |
| `NHL_SCRABBLE_VERBOSE`          | bool   | false   | Verbose logging          |
| `NHL_SCRABBLE_SANITIZE_LOGS`    | bool   | true    | Sanitize secrets         |

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
