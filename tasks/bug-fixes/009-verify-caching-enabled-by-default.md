# Verify and Validate Caching is Enabled by Default

**GitHub Issue**: #365 - https://github.com/bdperkin/nhl-scrabble/issues/365

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

User reports that "certain sub-commands result in always fetching fresh data" despite caching being enabled by default. Need to verify that caching is actually working across all CLI commands and identify any commands where caching is disabled or not functioning properly.

**Configuration default**: `cache_enabled = True` (line 152 in `src/nhl_scrabble/config.py`)

**Suspected issue**: Some CLI commands may not be using cached data even when caching is enabled, resulting in unnecessary API calls and slower performance.

## Current State

**Caching Configuration** (`src/nhl_scrabble/config.py`):
```python
cache_enabled: Annotated[
    bool,
    Field(
        default=True,
        description="Enable caching (true/false)",
    ),
]
cache_expiry: Annotated[
    int,
    Field(
        default=3600,
        description="Cache expiry seconds (1-86400)",
    ),
]
```

**CLI Commands with caching support**:

1. **`analyze`** command (line 513):
   - Has `--no-cache` option
   - Explicitly handles cache via `if no_cache: config.cache_enabled = False` (line 640-641)
   - ✅ Should respect cache settings

2. **`dashboard`** command (line 1300):
   - Has `--no-cache` option
   - Explicitly handles cache via `if no_cache: config.cache_enabled = False` (line 1356-1357)
   - ✅ Should respect cache settings

3. **`watch`** command (line 1481):
   - Has `--no-cache` option
   - Explicitly handles cache via `if no_cache: config.cache_enabled = False` (line 1536-1537)
   - Note: Line 1577 says `clear_cache=False  # Don't clear cache between iterations`
   - ✅ Should respect cache settings

4. **`search`** command (line 995):
   - ❌ **NO** `--no-cache` option
   - Uses `Config.from_env()` which defaults to `cache_enabled=True`
   - Creates API client via `container.create_api_client()` (line 1076)
   - **Status**: Should use cache by default, but no way to disable cache
   - **Potential issue**: Need to verify cache is actually being used

5. **`interactive`** command (line 778):
   - ❌ **NO** `--no-cache` option
   - Uses `Config.from_env()` which defaults to `cache_enabled=True`
   - Uses `InteractiveShell` which likely creates API client
   - **Status**: Should use cache by default, but no way to disable cache
   - **Potential issue**: Need to verify cache is actually being used

**API Client Cache Implementation** (`src/nhl_scrabble/api/nhl_client.py`):

```python
def __init__(
    self,
    ...,
    cache_enabled: bool = True,
    cache_expiry: int = 3600,
    ...
):
    ...
    if cache_enabled:
        # Install requests-cache for HTTP caching
        import requests_cache

        self.session = requests_cache.CachedSession(
            cache_name=".nhl_api_cache",
            backend="sqlite",
            expire_after=cache_expiry,
        )
        logger.debug(f"HTTP caching enabled (expiry: {cache_expiry}s)")
    else:
        self.session = requests.Session()
        logger.debug("HTTP caching disabled")
```

**DependencyContainer Cache Handling** (`src/nhl_scrabble/di.py`):

```python
def create_api_client(
    self,
    cache_enabled: bool | None = None,
    ...
) -> NHLApiClient:
    """Create NHLApiClient with dependency injection."""
    use_cache = cache_enabled if cache_enabled is not None else self.config.cache_enabled

    return NHLApiClient(
        ...,
        cache_enabled=use_cache,
        ...
    )
```

## Potential Issues

1. **Logging gap**: No user-visible indication that caching is being used
   - Users can't tell if cache is working without `--verbose`
   - Need cache hit/miss statistics in output

2. **Missing `--no-cache` option**: `search` and `interactive` commands lack this option
   - Users may want to force fresh data for these commands
   - Inconsistent CLI experience across commands

3. **No cache validation**: No automated tests verify caching works correctly
   - Can't be sure cache is being used without manual testing
   - No regression detection if caching breaks

4. **Cache location unclear**: Cache stored in `.nhl_api_cache` (current directory)
   - Users don't know where cache is
   - No documentation about clearing cache manually
   - Cache may be in unexpected location if run from different directories

## Proposed Solution

### 1. Add Cache Verification Testing

Create integration tests that verify caching is working:

```python
# tests/integration/test_caching.py
def test_analyze_uses_cache_by_default(tmpdir, monkeypatch):
    """Test that analyze command uses cache by default."""
    # Set up cache directory
    cache_dir = tmpdir / ".nhl_api_cache.sqlite"
    monkeypatch.chdir(tmpdir)

    # First run - should fetch from API
    result1 = runner.invoke(cli, ["analyze"])
    assert result1.exit_code == 0

    # Cache file should exist
    assert cache_dir.exists()

    # Second run - should use cache (verify by checking API call count)
    with patch("requests.Session.request") as mock_request:
        result2 = runner.invoke(cli, ["analyze"])
        assert result2.exit_code == 0
        # Should not make new API calls (cache hit)
        assert mock_request.call_count == 0

def test_search_uses_cache_by_default(tmpdir):
    """Test that search command uses cache by default."""
    # Similar to above

def test_interactive_uses_cache_by_default(tmpdir):
    """Test that interactive command uses cache by default."""
    # Similar to above
```

### 2. Add `--no-cache` Option to All Commands

Add consistency by giving all commands the `--no-cache` option:

```python
# src/nhl_scrabble/cli.py

@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable API response caching (fetch fresh data)",
)
def search(..., no_cache: bool) -> None:
    """Search for players..."""
    config = Config.from_env()

    # Override cache setting
    if no_cache:
        config.cache_enabled = False

    # ... rest of implementation

@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable API response caching (fetch fresh data)",
)
def interactive(no_fetch: bool, verbose: bool, no_cache: bool) -> None:
    """Start interactive mode..."""
    config = Config.from_env()

    # Override cache setting
    if no_cache:
        config.cache_enabled = False

    # ... rest of implementation
```

### 3. Add Cache Statistics to Output

Show cache usage in verbose mode or with a `--show-cache-stats` flag:

```python
# After API operations complete
if config.verbose and api_client.cache_enabled:
    cache_info = api_client.get_cache_info()
    logger.info(
        f"Cache statistics: {cache_info['hits']} hits, "
        f"{cache_info['misses']} misses, "
        f"{cache_info['size']} cached responses"
    )
```

### 4. Document Cache Behavior

Add to CLI help text and documentation:

```python
\b
Caching:
  API responses are cached by default (1 hour) to improve performance.
  Cache location: .nhl_api_cache.sqlite (in current directory)
  Use --no-cache to fetch fresh data
  Use --clear-cache to clear the cache before running
```

## Implementation Steps

1. **Add cache verification tests**:
   - Create `tests/integration/test_caching.py`
   - Test `analyze`, `search`, `interactive`, `dashboard`, `watch` commands
   - Verify cache is created and used
   - Test `--no-cache` flag disables caching

2. **Add `--no-cache` to missing commands**:
   - Add option to `search` command
   - Add option to `interactive` command
   - Update help text for consistency

3. **Add cache statistics logging**:
   - Create `NHLApiClient.get_cache_info()` method
   - Log cache stats in verbose mode after API operations
   - Show hits/misses/size

4. **Update documentation**:
   - Add caching section to CLI help
   - Document cache location and behavior
   - Add troubleshooting for cache issues
   - Update CHANGELOG.md

5. **Manual testing**:
   ```bash
   # Test 1: Verify cache is created and used
   rm -f .nhl_api_cache.sqlite
   time nhl-scrabble analyze  # Should be slow (API calls)
   time nhl-scrabble analyze  # Should be fast (cached)

   # Test 2: Verify --no-cache works
   time nhl-scrabble analyze --no-cache  # Should be slow (fresh)

   # Test 3: Verify search uses cache
   nhl-scrabble analyze  # Populate cache
   time nhl-scrabble search McDavid  # Should be fast (cached)

   # Test 4: Verify interactive uses cache
   nhl-scrabble analyze  # Populate cache
   nhl-scrabble interactive  # Should be fast (cached)
   ```

## Testing Strategy

**Unit Tests**:
```python
def test_config_cache_enabled_default():
    """Test cache is enabled by default in config."""
    config = Config()
    assert config.cache_enabled is True
    assert config.cache_expiry == 3600

def test_dependency_container_respects_cache_setting():
    """Test DependencyContainer uses config cache setting."""
    config = Config()
    config.cache_enabled = False

    container = DependencyContainer(config)
    client = container.create_api_client()

    assert client.cache_enabled is False
```

**Integration Tests**:
```python
def test_analyze_creates_cache_file(tmpdir, monkeypatch):
    """Test analyze command creates cache file."""
    monkeypatch.chdir(tmpdir)
    result = runner.invoke(cli, ["analyze"])
    assert result.exit_code == 0
    assert (tmpdir / ".nhl_api_cache.sqlite").exists()

def test_analyze_uses_cache_on_second_run(tmpdir, monkeypatch):
    """Test second run uses cached data."""
    monkeypatch.chdir(tmpdir)

    # First run
    result1 = runner.invoke(cli, ["analyze"])
    time1 = result1.elapsed

    # Second run (should be faster due to cache)
    result2 = runner.invoke(cli, ["analyze"])
    time2 = result2.elapsed

    # Second run should be significantly faster
    assert time2 < time1 * 0.5  # At least 50% faster

def test_no_cache_flag_bypasses_cache(tmpdir, monkeypatch):
    """Test --no-cache flag forces fresh data."""
    monkeypatch.chdir(tmpdir)

    # Populate cache
    runner.invoke(cli, ["analyze"])

    # Run with --no-cache (should make API calls)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = Mock(status_code=200, json=lambda: {...})
        result = runner.invoke(cli, ["analyze", "--no-cache"])
        # Should make API calls
        assert mock_request.call_count > 0
```

**Manual Testing**:
```bash
# Test cache is working
rm -f .nhl_api_cache.sqlite
nhl-scrabble analyze --verbose 2>&1 | grep -i cache
# Expected: "HTTP caching enabled (expiry: 3600s)"

# Test second run uses cache
time nhl-scrabble analyze > /dev/null
time nhl-scrabble analyze > /dev/null
# Second run should be much faster

# Test --no-cache disables caching
time nhl-scrabble analyze --no-cache > /dev/null
# Should be slow (no cache)

# Test search command uses cache
nhl-scrabble analyze > /dev/null  # Populate cache
time nhl-scrabble search McDavid > /dev/null
# Should be fast (using cache)

# Test search --no-cache
time nhl-scrabble search McDavid --no-cache > /dev/null
# Should be slow (fresh data)
```

## Acceptance Criteria

- [x] Integration tests verify caching works for all commands
- [x] `search` command has `--no-cache` option
- [x] `interactive` command has `--no-cache` option
- [x] All commands respect `cache_enabled` config setting
- [x] Cache statistics logged in verbose mode
- [x] Documentation explains caching behavior
- [x] Cache location documented
- [x] Manual testing confirms cache is used by default
- [x] Manual testing confirms `--no-cache` forces fresh data
- [x] All tests pass (unit + integration)
- [x] Type checking passes (mypy)
- [x] Linting passes (ruff)

## Related Files

- `src/nhl_scrabble/config.py` - Cache configuration defaults
- `src/nhl_scrabble/cli.py` - CLI commands (analyze, search, interactive, dashboard, watch)
- `src/nhl_scrabble/api/nhl_client.py` - HTTP caching implementation
- `src/nhl_scrabble/di.py` - Dependency injection (cache config passing)
- `tests/integration/test_caching.py` - New cache verification tests
- `tests/unit/test_config.py` - Config cache setting tests
- `docs/reference/cli.md` - CLI documentation (add caching section)
- `CHANGELOG.md` - Document cache improvements

## Dependencies

None - standalone bug investigation and fix.

## Additional Notes

### Why This Matters

**Performance**:
- Caching reduces API latency from 3-5s to <100ms per request
- Batch operations (700 players) benefit significantly
- Reduces load on NHL API servers (good citizenship)

**User Experience**:
- Faster command execution (especially repeat runs)
- Less waiting for data to load
- Clear feedback about cache usage
- Consistent CLI behavior across commands

**Reliability**:
- Reduces risk of API rate limiting
- Works offline if cache is populated
- Automated tests prevent regressions

### Cache Behavior Details

**Cache Storage**:
- Format: SQLite database
- Location: `.nhl_api_cache.sqlite` in current directory
- Expiry: 3600 seconds (1 hour) by default
- Size: ~1-2 MB for full NHL data

**Cache Key**:
- Based on URL and request parameters
- GET requests only (POST/PUT/DELETE not cached)
- Separate cache entries for different URLs

**Cache Expiry**:
- Responses expire after `cache_expiry` seconds
- Expired entries automatically refreshed on next access
- Manual clearing via `--clear-cache` flag

**Cache Invalidation**:
- Time-based expiry (configurable)
- Manual clearing with `--clear-cache`
- Delete `.nhl_api_cache.sqlite` file
- No automatic invalidation on data changes (trade-off for simplicity)

### Performance Impact

**Without cache** (typical `analyze` run):
- 32 teams × ~0.5s API call = 16 seconds API time
- Plus processing time = ~20 seconds total

**With cache** (subsequent runs):
- 32 teams × ~0.01s cache read = 0.3 seconds API time
- Plus processing time = ~4 seconds total
- **80% faster!**

### Edge Cases

1. **Cache in wrong directory**: User runs command from different directory
   - Solution: Cache in CWD (current behavior) or use XDG cache dir
   - Document cache location clearly

2. **Stale cache**: Data in cache older than expiry but not refreshed
   - Current: Automatic expiry handles this
   - Alternative: Add `--refresh-cache` option

3. **Corrupted cache**: SQLite file corrupted
   - Current: requests-cache handles gracefully (rebuilds)
   - Fallback: Delete cache file

4. **Disk space**: Cache grows over time
   - Current: Small size (~1-2 MB), not an issue
   - Future: Add cache size limit or auto-cleanup

### Future Enhancements

After this task:
- Add `--cache-dir` option to specify cache location
- Add `--cache-stats` command to show cache statistics
- Add cache warming (pre-populate cache)
- Add cache export/import for sharing
- Use XDG_CACHE_HOME for cache location (Linux standard)
- Add cache compression for space savings

## Implementation Notes

*To be filled during implementation:*

- Actual caching behavior found during testing
- Which commands had caching issues
- Performance measurements (before/after)
- Cache hit rate statistics
- User feedback on cache improvements
- Actual effort vs estimated
