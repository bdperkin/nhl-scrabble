# Audit and Adjust Logging Levels

**GitHub Issue**: #364 - https://github.com/bdperkin/nhl-scrabble/issues/364

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

The codebase currently has many diagnostic messages logged at INFO level that should be at DEBUG level. When users run `nhl-scrabble analyze` without the `--verbose` flag, they see too many internal diagnostic messages that clutter the output and reduce signal-to-noise ratio.

**Current behavior** (without `--verbose`):
```
2026-04-24 10:00:00 - nhl_scrabble.di - INFO - Created all core dependencies
2026-04-24 10:00:01 - nhl_scrabble.api.nhl_client - INFO - Connection pool configured: max_connections=10, max_per_host=5
2026-04-24 10:00:02 - nhl_scrabble.api.nhl_client - INFO - Successfully fetched 32 teams
2026-04-24 10:00:03 - nhl_scrabble.api.nhl_client - INFO - API cache cleared
...many more diagnostic messages...
```

These messages are useful for debugging (with `--verbose`), but shouldn't appear in standard output.

**Desired behavior** (without `--verbose`):
```
2026-04-24 10:00:00 - nhl_scrabble.cli - INFO - Starting NHL Scrabble analysis v2.0.0
2026-04-24 10:00:05 - nhl_scrabble.cli - INFO - Processing complete: 32 teams, 700 players
```

Only user-facing, actionable information should be at INFO level.

## Current State

**Logging Setup** (`src/nhl_scrabble/logging_config.py`):
```python
def setup_logging(verbose: bool = False, ...):
    log_level = logging.DEBUG if verbose else logging.INFO
    # ...
```

**Current log levels** (analysis of codebase):
- **18 files** with logging statements
- **38 INFO** level log statements
- **38 DEBUG** level log statements
- **~50% of INFO messages** are diagnostic (should be DEBUG)

**Examples of INFO messages that should be DEBUG**:

```python
# src/nhl_scrabble/di.py:266
logger.info("Created all core dependencies")  # Diagnostic

# src/nhl_scrabble/api/nhl_client.py:160
logger.info(
    f"Rate limiter configured: {rate_limit_max_requests} requests per "
    f"{rate_limit_window}s"
)  # Diagnostic

# src/nhl_scrabble/api/nhl_client.py:208
logger.info(
    f"Connection pool configured: max_connections={dos_max_connections}, "
    f"max_per_host={dos_max_per_host}"
)  # Diagnostic

# src/nhl_scrabble/api/nhl_client.py:429
logger.info(f"Successfully fetched {len(teams_info)} teams")  # Diagnostic

# src/nhl_scrabble/api/nhl_client.py:726
logger.info("API cache cleared")  # Diagnostic
```

**Examples of INFO messages that should stay INFO** (user-facing):

```python
# src/nhl_scrabble/cli.py:646
logger.info(f"Starting NHL Scrabble analysis v{__version__}")  # User-facing

# src/nhl_scrabble/cli.py:661
logger.info(f"Using custom scoring config from: {scoring_config}")  # User config

# src/nhl_scrabble/cli.py:707
logger.info(f"Active filters: {filters}")  # User feature

# src/nhl_scrabble/cli.py:218
logger.info(f"Excel report written to {output}")  # User result
```

## Proposed Solution

Establish clear guidelines for log levels and audit all logging statements to conform to best practices.

### Log Level Guidelines

**DEBUG** - Diagnostic information for developers:
- Internal state changes ("Created dependencies", "Cache initialized")
- Configuration details ("Pool size: 10", "Timeout: 30s")
- Successful completion of internal operations ("Fetched 32 teams")
- Performance metrics ("Processed in 2.3s")
- Cache hits/misses
- Detailed API request/response info

**INFO** - User-facing, actionable information:
- Application lifecycle ("Starting analysis", "Processing complete")
- User configuration choices ("Using custom config", "Active filters")
- Output locations ("Report written to file.xlsx")
- Feature activation ("Interactive mode enabled")
- Progress indicators (for long operations)
- Important user decisions

**WARNING** - Recoverable issues requiring user attention:
- Validation failures (with fallback)
- API errors (with retry)
- Missing optional features
- Deprecation notices

**ERROR** - Unrecoverable issues:
- Fatal errors preventing operation
- Configuration errors
- Permission errors
- Missing required resources

**CRITICAL** - System-level failures:
- Application crash scenarios
- Security violations
- Data corruption

### Implementation Approach

1. **Create log level audit document**:
   - List all logging statements by file
   - Categorize current level vs recommended level
   - Identify changes needed

2. **Update logging statements**:
   - Change diagnostic INFO → DEBUG
   - Keep user-facing INFO
   - Adjust any misleveled WARNING/ERROR

3. **Add guidelines to CONTRIBUTING.md**:
   - Document log level criteria
   - Provide examples of each level
   - Include in code review checklist

4. **Add pre-commit hook check** (optional future enhancement):
   - Flag potential INFO overuse
   - Suggest DEBUG for common diagnostic patterns

## Implementation Steps

1. **Audit all logging statements** across codebase:
   ```bash
   # Generate audit report
   grep -rn "logger\.\(debug\|info\|warning\|error\|critical\)" src/ \
     --include="*.py" > docs/logging-audit.txt
   ```

2. **Categorize each statement**:
   - Diagnostic (internal operations) → DEBUG
   - User-facing (configuration, results) → INFO
   - Issues requiring attention → WARNING
   - Fatal errors → ERROR

3. **Update logging statements** following guidelines:
   ```python
   # BEFORE: Diagnostic at INFO
   logger.info("Created all core dependencies")
   logger.info(f"Successfully fetched {len(teams)} teams")
   logger.info("API cache cleared")

   # AFTER: Diagnostic at DEBUG
   logger.debug("Created all core dependencies")
   logger.debug(f"Successfully fetched {len(teams)} teams")
   logger.debug("API cache cleared")

   # KEEP: User-facing at INFO
   logger.info(f"Starting NHL Scrabble analysis v{__version__}")
   logger.info(f"Using custom scoring config from: {config_path}")
   logger.info(f"Report written to {output}")
   ```

4. **Update documentation**:
   - Add "Logging Guidelines" section to CONTRIBUTING.md
   - Document log level criteria
   - Provide code examples

5. **Test logging output**:
   - Run without `--verbose`: Should see minimal, user-focused INFO
   - Run with `--verbose`: Should see detailed DEBUG diagnostics
   - Verify no regressions in log clarity

6. **Update tests if needed**:
   - Tests checking log output may need level adjustments
   - Verify caplog fixtures use appropriate levels

## Testing Strategy

**Manual Testing**:

```bash
# Test default (INFO) output - should be clean and user-focused
nhl-scrabble analyze 2>&1 | tee /tmp/info-logs.txt
# Expect: ~5-10 lines, all user-facing

# Test verbose (DEBUG) output - should be detailed
nhl-scrabble analyze --verbose 2>&1 | tee /tmp/debug-logs.txt
# Expect: 50-100 lines, diagnostic details included

# Compare log counts
echo "INFO logs: $(grep -c INFO /tmp/info-logs.txt)"
echo "DEBUG logs: $(grep -c DEBUG /tmp/debug-logs.txt)"
```

**Expected results**:
- **Non-verbose**: 5-10 INFO messages (user-facing only)
- **Verbose**: 50-100 messages (INFO + DEBUG diagnostics)

**Unit Tests** (if log output is tested):

```python
def test_analyze_logs_user_facing_info(caplog):
    """Test that non-verbose mode shows only user-facing INFO."""
    with caplog.at_level(logging.INFO):
        run_analysis(verbose=False)

    # Should see startup and completion messages
    assert "Starting NHL Scrabble analysis" in caplog.text
    # Should NOT see diagnostic messages
    assert "Created all core dependencies" not in caplog.text
    assert "Connection pool configured" not in caplog.text

def test_analyze_logs_diagnostic_debug(caplog):
    """Test that verbose mode shows diagnostic DEBUG."""
    with caplog.at_level(logging.DEBUG):
        run_analysis(verbose=True)

    # Should see diagnostic messages
    assert "Created all core dependencies" in caplog.text
    assert "Connection pool configured" in caplog.text
```

## Acceptance Criteria

- [x] All logging statements audited and categorized
- [x] Diagnostic messages changed from INFO → DEBUG
- [x] User-facing messages remain at INFO
- [x] Logging guidelines added to CONTRIBUTING.md
- [x] Non-verbose output is clean (5-10 INFO messages max)
- [x] Verbose output includes full diagnostics (DEBUG level)
- [x] No regression in log clarity or usefulness
- [x] Tests updated if log output checked
- [x] Documentation updated

## Related Files

- `src/nhl_scrabble/**/*.py` - All files with logging (18 files)
- `src/nhl_scrabble/logging_config.py` - Logging configuration
- `src/nhl_scrabble/cli.py` - Primary user-facing logs
- `src/nhl_scrabble/api/nhl_client.py` - Many diagnostic logs
- `src/nhl_scrabble/di.py` - Dependency creation logs
- `CONTRIBUTING.md` - Add logging guidelines section

## Dependencies

None - standalone refactoring task.

## Additional Notes

### Why This Matters

**User Experience**:
- **Cleaner output**: Users see only relevant information
- **Reduced noise**: Easier to spot important messages
- **Professional**: Standard tools don't spam diagnostics at INFO

**Developer Experience**:
- **Better debugging**: `--verbose` provides detailed diagnostics
- **Consistent standards**: Clear guidelines for new code
- **Log analysis**: Easier to filter/search when levels are semantic

### Log Level Decision Tree

When adding a log statement, ask:

1. **Is this about the user's action or result?**
   - YES → INFO (e.g., "Report written to file.xlsx")
   - NO → Continue to #2

2. **Is this about internal operation details?**
   - YES → DEBUG (e.g., "Fetched 32 teams from API")
   - NO → Continue to #3

3. **Is this a recoverable problem?**
   - YES → WARNING (e.g., "Invalid player name, using fallback")
   - NO → Continue to #4

4. **Is this a fatal error?**
   - YES → ERROR (e.g., "Cannot write output file")
   - NO → DEBUG (default for uncertain cases)

### Examples of Each Level

**DEBUG** (diagnostic, verbose only):
```python
logger.debug("Created ScrabbleScorer with 26 letter values")
logger.debug(f"API request to {url} completed in {elapsed:.2f}s")
logger.debug(f"Cache hit for key {cache_key}")
logger.debug("Connection pool initialized with 10 connections")
```

**INFO** (user-facing, always visible):
```python
logger.info(f"Starting NHL Scrabble analysis v{version}")
logger.info(f"Using custom scoring: {scoring_system}")
logger.info(f"Active filters: {filter_list}")
logger.info(f"Report written to {output_path}")
logger.info("Analysis complete: 32 teams, 700 players processed")
```

**WARNING** (issues with fallback):
```python
logger.warning(f"Invalid player name '{name}', using 'Unknown'")
logger.warning("API rate limit exceeded, retrying in 60s")
logger.warning("Cache expired, fetching fresh data")
```

**ERROR** (fatal issues):
```python
logger.error(f"Cannot write to {path}: Permission denied")
logger.error("API authentication failed: Invalid credentials")
logger.error("Required dependency 'requests' not installed")
```

### Breaking Changes

None - this is purely internal logging changes. External behavior unchanged.

### Performance Implications

**Positive**:
- Slightly faster non-verbose execution (fewer log writes)
- Reduced log file sizes in production

**Neutral**:
- No performance impact on verbose execution
- Negligible difference overall (~0.1% faster)

### Future Enhancements

After this task:
- Add structured logging fields (user_id, request_id, etc.)
- Implement log level override per module (`--log-level nhl_scrabble.api=DEBUG`)
- Add log aggregation integration (Sentry, Datadog, etc.)
- Create pre-commit hook to suggest DEBUG for common diagnostic patterns

## Implementation Notes

*To be filled during implementation:*

- Actual count of logging statements changed
- List of files modified
- Any surprising findings during audit
- User feedback on improved log clarity
- Actual effort vs estimated
