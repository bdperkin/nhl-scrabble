# Logging Guidelines

Proper logging levels help maintain clean user output while providing detailed diagnostics for debugging.

## Log Level Criteria

### DEBUG

Diagnostic information for developers (only shown with `--verbose`):

- Internal state changes ("Created dependencies", "Cache initialized")
- Configuration details ("Pool size: 10", "Timeout: 30s")
- Successful completion of internal operations ("Fetched 32 teams", "Processed team XYZ")
- Performance metrics ("Processed in 2.3s", "Cache hit rate: 95%")
- Cache hits/misses
- Detailed API request/response info
- Progress indicators for internal operations

### INFO

User-facing, actionable information (always visible):

- Application lifecycle ("Starting analysis", "Processing complete")
- User configuration choices ("Using custom config", "Active filters")
- Output locations ("Report written to file.xlsx")
- Feature activation ("Interactive mode enabled")
- Important user decisions
- Confirmation of user-initiated actions

### WARNING

Recoverable issues requiring user attention:

- Validation failures (with fallback behavior)
- API errors (with retry logic)
- Missing optional features
- Deprecation notices
- Data quality issues

### ERROR

Unrecoverable issues preventing operation:

- Fatal errors preventing operation
- Configuration errors
- Permission errors
- Missing required resources
- API failures after retries

### CRITICAL

System-level failures:

- Application crash scenarios
- Security violations
- Data corruption
- Unrecoverable system errors

## Decision Tree

When adding a log statement, ask:

1. **Is this about the user's action or result?**

   - YES → `INFO` (e.g., "Report written to file.xlsx")
   - NO → Continue to #2

1. **Is this about internal operation details?**

   - YES → `DEBUG` (e.g., "Fetched 32 teams from API")
   - NO → Continue to #3

1. **Is this a recoverable problem?**

   - YES → `WARNING` (e.g., "Invalid player name, using fallback")
   - NO → Continue to #4

1. **Is this a fatal error?**

   - YES → `ERROR` (e.g., "Cannot write output file")
   - NO → `DEBUG` (default for uncertain cases)

## Examples

### DEBUG (diagnostic, verbose only)

```python
logger.debug("Created ScrabbleScorer with 26 letter values")
logger.debug(f"API request to {url} completed in {elapsed:.2f}s")
logger.debug(f"Cache hit for key {cache_key}")
logger.debug("Connection pool initialized with 10 connections")
logger.debug(f"Processed team {team_abbrev} (15/32)")
```

### INFO (user-facing, always visible)

```python
logger.info(f"Starting NHL Scrabble analysis v{version}")
logger.info(f"Using custom scoring config from: {config_path}")
logger.info(f"Active filters: divisions=[Atlantic, Metropolitan]")
logger.info(f"Report written to {output_path}")
logger.info("Analysis complete: 32 teams, 700 players processed")
```

### WARNING (issues with fallback)

```python
logger.warning(f"Invalid player name '{name}', using 'Unknown'")
logger.warning("API rate limit exceeded, retrying in 60s")
logger.warning("Cache expired, fetching fresh data")
logger.warning(f"Team {abbrev} roster unavailable, skipping")
```

### ERROR (fatal issues)

```python
logger.error(f"Cannot write to {path}: Permission denied")
logger.error("API authentication failed: Invalid credentials")
logger.error("Required dependency 'requests' not installed")
logger.error(f"Failed to fetch team {abbrev} after {retries} attempts")
```

## Testing Your Logs

Before committing, test that log levels are appropriate:

```bash
# Non-verbose output should be clean (5-10 INFO messages)
nhl-scrabble analyze 2>&1 | tee /tmp/info-logs.txt
grep -c INFO /tmp/info-logs.txt  # Expect: 5-10 lines

# Verbose output should include diagnostics (50-100 messages)
nhl-scrabble analyze --verbose 2>&1 | tee /tmp/debug-logs.txt
grep -c DEBUG /tmp/debug-logs.txt  # Expect: 50-100 lines

# INFO messages should be user-facing
grep INFO /tmp/info-logs.txt  # Review: Are these all actionable for users?

# DEBUG messages should be diagnostic
grep DEBUG /tmp/debug-logs.txt  # Review: Are these internal details?
```

## Code Review Checklist

When reviewing logging statements:

- [ ] User-facing information uses `INFO`
- [ ] Internal diagnostics use `DEBUG`
- [ ] Recoverable issues use `WARNING`
- [ ] Fatal errors use `ERROR`
- [ ] Non-verbose output is clean (\<10 INFO messages for typical runs)
- [ ] Verbose output provides useful debugging details
- [ ] Log messages are clear and actionable
- [ ] Sensitive information is not logged (API keys, passwords, etc.)
