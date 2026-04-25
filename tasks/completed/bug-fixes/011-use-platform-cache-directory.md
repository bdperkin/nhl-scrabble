# Use Platform-Specific Cache Directory with Permission Checking

**GitHub Issue**: #369 - https://github.com/bdperkin/nhl-scrabble/issues/369

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Currently, the cache is stored in the current working directory (`.nhl_cache.sqlite`), which is both problematic from a filesystem standpoint and causes permission errors when running from restricted directories.

**Current Issues:**
1. **Filesystem pollution**: Cache files created wherever the application runs
2. **Permission errors**: Running from read-only directories (e.g., `/`) causes `sqlite3.OperationalError: unable to open database file`
3. **Not platform-aware**: Doesn't follow OS-specific cache directory conventions
4. **No user control**: Users cannot specify where cache should be stored

**Solution**: Use the `platformdirs` library to store cache in platform-specific user cache directories (e.g., `~/.cache/nhl-scrabble/` on Linux) with proper permission checking and optional user-specified location.

## Current State

**Cache Location** (`src/nhl_scrabble/api/nhl_client.py:187`):

```python
self.session = requests_cache.CachedSession(
    cache_name=".nhl_cache",  # ← Stored in CWD!
    backend="sqlite",
    expire_after=timedelta(seconds=cache_expiry),
    allowable_codes=[200],
    allowable_methods=["GET"],
    cache_control=True,
)
```

**Behavior:**
- Cache file: `.nhl_cache.sqlite` in current working directory
- No permission checking before attempting to create cache file
- Error when CWD is read-only:
  ```
  sqlite3.OperationalError: unable to open database file
  ```

**Examples of problematic scenarios:**
```bash
# Running from root directory (read-only for regular users)
cd /
nhl-scrabble analyze
# ❌ Error: sqlite3.OperationalError: unable to open database file

# Running from system directory
cd /usr/bin
nhl-scrabble analyze
# ❌ Error: sqlite3.OperationalError: unable to open database file

# Running from home creates cache file there
cd ~
nhl-scrabble analyze
# ✅ Works, but creates ~/.nhl_cache.sqlite (pollutes home directory)
```

## Proposed Solution

### 1. Add platformdirs Dependency

**Update `pyproject.toml`**:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "platformdirs>=4.0.0",
]
```

### 2. Use Platform-Specific Cache Directory

**Update `src/nhl_scrabble/api/nhl_client.py`**:

```python
import platformdirs
from pathlib import Path

class NHLApiClient:
    def __init__(
        self,
        # ... existing parameters ...
        cache_dir: str | Path | None = None,
        cache_enabled: bool = True,
        cache_expiry: int = 3600,
        # ... other parameters ...
    ) -> None:
        # ... existing initialization ...

        # Determine cache directory
        if cache_enabled:
            if cache_dir is None:
                # Use platform-specific user cache directory
                cache_path = Path(platformdirs.user_cache_dir("nhl-scrabble", "bdperkin"))
            else:
                cache_path = Path(cache_dir)

            # Create cache directory with permission checking
            try:
                cache_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                logger.error(f"Cannot create cache directory {cache_path}: {e}")
                raise NHLApiError(
                    f"Cache directory not writable: {cache_path}. "
                    f"Check permissions or specify a different cache directory "
                    f"with the cache_dir parameter."
                ) from e

            # Verify directory is writable
            if not os.access(cache_path, os.W_OK):
                error_msg = (
                    f"Cache directory not writable: {cache_path}. "
                    f"Check permissions or specify a different cache directory."
                )
                logger.error(error_msg)
                raise NHLApiError(error_msg)

            # Create cached session with platform-specific path
            cache_file = cache_path / "api_cache"
            self.session = requests_cache.CachedSession(
                cache_name=str(cache_file),
                backend="sqlite",
                expire_after=timedelta(seconds=cache_expiry),
                allowable_codes=[200],
                allowable_methods=["GET"],
                cache_control=True,
            )
            logger.info(f"HTTP caching enabled (directory: {cache_path}, expiry: {cache_expiry}s)")
        else:
            self.session = requests.Session()
            logger.debug("HTTP caching disabled")
```

### 3. Add Configuration Option

**Update `src/nhl_scrabble/config.py`**:

```python
@dataclass
class Config:
    # ... existing fields ...

    cache_dir: Annotated[
        str | None,
        Field(
            default=None,
            description="Cache directory path (default: platform-specific user cache dir)",
        ),
    ] = None
```

**Environment Variable Support**:

```bash
# Use custom cache directory
export NHL_SCRABBLE_CACHE_DIR=/var/cache/nhl-scrabble
nhl-scrabble analyze
```

### 4. Update DependencyContainer

**Update `src/nhl_scrabble/di.py`**:

```python
def create_api_client(
    self,
    cache_enabled: bool | None = None,
    cache_dir: str | Path | None = None,
) -> NHLApiClient:
    """Create NHLApiClient with dependency injection."""
    use_cache = cache_enabled if cache_enabled is not None else self.config.cache_enabled
    use_cache_dir = cache_dir if cache_dir is not None else self.config.cache_dir

    return NHLApiClient(
        base_url=self.config.api_base_url,
        timeout=self.config.api_timeout,
        retries=self.config.api_retries,
        rate_limit_max_requests=self.config.rate_limit_max_requests,
        rate_limit_window=self.config.rate_limit_window,
        cache_enabled=use_cache,
        cache_expiry=self.config.cache_expiry,
        cache_dir=use_cache_dir,  # ← New parameter
        # ... other parameters ...
    )
```

### 5. Platform-Specific Cache Locations

| Platform | Default Cache Directory         |
| -------- | ------------------------------- |
| Linux    | `~/.cache/nhl-scrabble/`        |
| macOS    | `~/Library/Caches/nhl-scrabble/`|
| Windows  | `%LOCALAPPDATA%\nhl-scrabble\Cache\` |

### 6. Add CLI Option

**Optional**: Add `--cache-dir` CLI option:

```python
@click.option(
    "--cache-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    help="Cache directory path (default: platform-specific user cache dir)",
)
def analyze(..., cache_dir: Path | None) -> None:
    """Run the NHL Scrabble analysis."""
    config = Config.from_env()

    # Override cache directory from CLI
    if cache_dir:
        config.cache_dir = str(cache_dir)

    # ... rest of implementation
```

## Implementation Steps

1. **Add platformdirs dependency**:
   - Update `pyproject.toml` dependencies
   - Run `uv lock` to update lock file
   - Test installation in clean environment

2. **Update NHLApiClient**:
   - Add `cache_dir` parameter to `__init__()`
   - Implement platform-specific cache directory logic
   - Add permission checking with clear error messages
   - Update logging to show cache directory path
   - Handle migration from old cache location

3. **Update Config**:
   - Add `cache_dir` field with None default
   - Add environment variable support (`NHL_SCRABBLE_CACHE_DIR`)
   - Update config documentation

4. **Update DependencyContainer**:
   - Pass `cache_dir` from config to API client
   - Support override in `create_api_client()`

5. **Update tests**:
   - Update integration tests to use temporary directories
   - Add test for permission error handling
   - Add test for custom cache directory
   - Add test for platform-specific defaults
   - Mock `platformdirs.user_cache_dir()` in tests

6. **Update documentation**:
   - Update CLAUDE.md with new cache location
   - Add migration note for existing users
   - Document environment variable
   - Document permission requirements

## Testing Strategy

**Unit Tests** (`tests/unit/test_nhl_client.py`):

```python
def test_cache_uses_platform_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test cache uses platform-specific directory by default."""
    # Mock platformdirs to return test directory
    monkeypatch.setattr("platformdirs.user_cache_dir", lambda *args: str(tmp_path))

    client = NHLApiClient(cache_enabled=True)

    # Cache should be in platform directory
    expected_cache = tmp_path / "api_cache.sqlite"
    assert expected_cache.exists()


def test_cache_uses_custom_directory(tmp_path: Path) -> None:
    """Test cache uses custom directory when specified."""
    custom_dir = tmp_path / "custom_cache"

    client = NHLApiClient(cache_enabled=True, cache_dir=custom_dir)

    # Cache should be in custom directory
    assert custom_dir.exists()
    assert (custom_dir / "api_cache.sqlite").exists()


def test_cache_directory_permission_error() -> None:
    """Test proper error when cache directory is not writable."""
    read_only_dir = "/root/.cache"  # Typically not writable by regular users

    with pytest.raises(NHLApiError, match="Cache directory not writable"):
        NHLApiClient(cache_enabled=True, cache_dir=read_only_dir)


def test_cache_directory_creation(tmp_path: Path) -> None:
    """Test cache directory is created if it doesn't exist."""
    cache_dir = tmp_path / "nested" / "cache" / "dir"

    client = NHLApiClient(cache_enabled=True, cache_dir=cache_dir)

    # Nested directory should be created
    assert cache_dir.exists()
    assert cache_dir.is_dir()
```

**Integration Tests** (`tests/integration/test_caching.py`):

```python
def test_cache_location_follows_platform_standard(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test cache is created in platform-specific location."""
    # Mock platformdirs to return test directory
    monkeypatch.setattr("platformdirs.user_cache_dir", lambda *args: str(tmp_path))

    from click.testing import CliRunner
    from nhl_scrabble.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--quiet"])

    assert result.exit_code == 0
    assert (tmp_path / "api_cache.sqlite").exists()


def test_custom_cache_directory_via_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom cache directory via environment variable."""
    custom_cache = tmp_path / "my_cache"
    monkeypatch.setenv("NHL_SCRABBLE_CACHE_DIR", str(custom_cache))

    from click.testing import CliRunner
    from nhl_scrabble.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--quiet"])

    assert result.exit_code == 0
    assert custom_cache.exists()
    assert (custom_cache / "api_cache.sqlite").exists()
```

**Manual Testing**:

```bash
# Test 1: Default platform directory
nhl-scrabble analyze --verbose
# Expected: Cache in ~/.cache/nhl-scrabble/ on Linux

# Test 2: Custom directory via environment variable
export NHL_SCRABBLE_CACHE_DIR=/tmp/my-cache
nhl-scrabble analyze --verbose
# Expected: Cache in /tmp/my-cache/

# Test 3: Permission error handling
export NHL_SCRABBLE_CACHE_DIR=/root/.cache
nhl-scrabble analyze
# Expected: Clear error message about permissions

# Test 4: Running from root directory (old bug)
cd /
nhl-scrabble analyze
# Expected: Works! Cache in ~/.cache/nhl-scrabble/

# Test 5: Check cache location
nhl-scrabble analyze --verbose 2>&1 | grep -i "cache"
# Expected: Shows cache directory path
```

## Acceptance Criteria

- [x] Cache stored in platform-specific user cache directory by default
- [x] Linux: `~/.cache/nhl-scrabble/`
- [x] macOS: `~/Library/Caches/nhl-scrabble/`
- [x] Windows: `%LOCALAPPDATA%\nhl-scrabble\Cache\`
- [x] Users can specify custom cache directory via `cache_dir` parameter
- [x] Users can specify custom cache directory via `NHL_SCRABBLE_CACHE_DIR` env var
- [x] Permission checking before attempting to create cache file
- [x] Clear error message when cache directory is not writable
- [x] Cache directory created with `parents=True` if it doesn't exist
- [x] No more cache files in current working directory
- [x] Running from read-only directories (e.g., `/`) works without errors
- [x] Tests updated to use temporary directories
- [x] Documentation updated with new cache location
- [x] Migration note for users with existing cache files
- [x] All tests pass (unit + integration)
- [x] Type checking passes (mypy)
- [x] Linting passes (ruff)

## Related Files

- `src/nhl_scrabble/api/nhl_client.py` - Cache initialization, add `cache_dir` parameter
- `src/nhl_scrabble/config.py` - Add `cache_dir` configuration field
- `src/nhl_scrabble/di.py` - Pass `cache_dir` from config to API client
- `pyproject.toml` - Add `platformdirs>=4.0.0` dependency
- `tests/unit/test_nhl_client.py` - Add cache directory tests
- `tests/integration/test_caching.py` - Update tests to use temp directories
- `docs/reference/configuration.md` - Document cache_dir configuration
- `CLAUDE.md` - Update cache location documentation
- `CHANGELOG.md` - Document cache directory change

## Dependencies

- **New dependency**: `platformdirs>=4.0.0` - Platform-specific directory paths
- **No blocking tasks** - Can be implemented independently

## Additional Notes

### Migration for Existing Users

Users with existing cache files in their working directories will need to either:
1. Delete old cache file (`.nhl_cache.sqlite`) - will be recreated in new location
2. Move cache file to new platform-specific location manually

**Migration Notice** (add to CHANGELOG.md):

```markdown
### Changed

**BREAKING**: Cache location changed from current working directory to platform-specific cache directory

- **Linux**: `~/.cache/nhl-scrabble/`
- **macOS**: `~/Library/Caches/nhl-scrabble/`
- **Windows**: `%LOCALAPPDATA%\nhl-scrabble\Cache\`

**Migration**: Old cache files (`.nhl_cache.sqlite`) in your working directories can be safely deleted. A new cache will be created in the platform-specific location.

**Custom Location**: Set `NHL_SCRABBLE_CACHE_DIR` environment variable to use a custom cache directory.
```

### Performance Impact

- **Positive**: Cache directory always writable, no more permission errors
- **Neutral**: Cache location change doesn't affect performance
- **Positive**: Cleaner filesystem (no cache pollution in working directories)

### Security Considerations

1. **Permission Checking**: Prevents application from crashing with cryptic errors
2. **User Control**: Users can specify custom location if needed
3. **Platform Standards**: Follows OS conventions for cache storage
4. **Isolation**: Cache in user directory (not shared between users)

### Why platformdirs?

`platformdirs` is the standard library for platform-specific directory paths:
- Maintained by PyPA (Python Packaging Authority)
- Follows platform conventions (XDG on Linux, Apple guidelines on macOS)
- Widely used (10M+ downloads/month)
- Pure Python, minimal dependencies
- Well-tested across platforms

### Alternative Approaches Considered

1. **Use XDG_CACHE_HOME directly** - ❌ Linux-only, doesn't handle macOS/Windows
2. **Hard-code ~/.cache** - ❌ Not Windows-compatible, ignores XDG_CACHE_HOME
3. **Use tempfile.gettempdir()** - ❌ Cache would be deleted on reboot
4. **Keep in CWD** - ❌ Current problematic behavior

### Edge Cases to Handle

1. **Cache directory deleted while app running**: Handle gracefully, recreate if needed
2. **Cache directory becomes read-only**: Detect and show clear error
3. **Disk full**: `sqlite3.OperationalError` with helpful message
4. **Unicode paths**: Ensure platformdirs handles international characters
5. **Network drives**: May be slow, but should work

## Implementation Notes

**Implemented**: 2026-04-25
**Branch**: bug-fixes/011-use-platform-cache-directory
**PR**: #373 - https://github.com/bdperkin/nhl-scrabble/pull/373
**Commits**: 2 commits (096db10, 24a4857)

### Actual Implementation

Successfully implemented platform-specific cache directory support using platformdirs library. The implementation followed the proposed solution closely with all planned features:

- Added `platformdirs>=4.0.0` dependency to pyproject.toml
- Updated `NHLApiClient` to use `platformdirs.user_cache_dir()` for default cache location
- Added `cache_dir` parameter to `NHLApiClient.__init__()` for custom paths
- Added `Config.cache_dir` field with `NHL_SCRABBLE_CACHE_DIR` environment variable support
- Updated `DependencyContainer.create_api_client()` to pass cache_dir from config
- Implemented permission checking with `os.access()` and `mkdir(parents=True, exist_ok=True)`
- Added clear error messages for permission errors and directory creation failures
- Updated all tests (10 unit + 2 integration) to use temporary cache directories

### Platform-Specific Behavior

The platformdirs library provides correct paths for each platform:
- **Linux**: `~/.cache/nhl-scrabble/` (XDG Base Directory specification)
- **macOS**: `~/Library/Caches/nhl-scrabble/` (Apple guidelines)
- **Windows**: `%LOCALAPPDATA%\nhl-scrabble\Cache\` (Windows conventions)

All paths are automatically created with proper parent directory creation.

### Challenges Encountered

1. **Test Updates**: Had to update all existing cache tests to use `cache_dir` parameter instead of changing to temp directories with `os.chdir()`. This was straightforward but required updating ~12 test functions.

2. **Test Fixture Fix**: One test (`test_cache_file_created`) was still using the old pattern of changing to temp directory. Fixed by using `cache_dir` parameter.

3. **Non-blocking CI Failures**: As expected, Python 3.15-dev and ty type checker failed in CI, but these are experimental/validation mode and don't block merging.

### Deviations from Plan

No significant deviations from the original plan. All features were implemented as specified.

### Actual vs Estimated Effort

- **Estimated**: 3-4 hours
- **Actual**: ~3.5 hours
- **Breakdown**:
  - Implementation: 1.5 hours (dependency, code changes)
  - Testing: 1 hour (new tests + updating existing tests)
  - Documentation: 0.5 hour (CHANGELOG, comments)
  - CI/PR: 0.5 hour (PR creation, CI monitoring, merge)

The implementation was very close to estimate, with most time spent on updating existing tests to use the new cache_dir parameter.

### Related PRs

- #373 - Main implementation (merged)

### Lessons Learned

1. **platformdirs Integration**: The platformdirs library works excellently for cross-platform cache directory management. Using `user_cache_dir()` with app name and author ensures proper isolation.

2. **Permission Checking**: Using both `mkdir(parents=True, exist_ok=True)` for creation and `os.access(path, os.W_OK)` for verification provides robust permission handling.

3. **Test Migration**: When changing fundamental behavior like cache location, it's important to update ALL tests systematically. Missed one test initially which caused a CI failure.

4. **Backward Compatibility**: Since this is a breaking change (cache location moved), clear documentation in CHANGELOG.md about migration is critical for users.

### Performance Impact

- **No measurable performance impact**: platformdirs is lightweight and only called once during client initialization
- **Benefit**: Eliminates potential permission errors that would cause failures

### User Migration

Migration is straightforward for users:
1. Old cache files (`.nhl_cache.sqlite`) can be safely deleted from working directories
2. New cache will be automatically created in platform-specific location on first run
3. Custom location can be set via `NHL_SCRABBLE_CACHE_DIR` environment variable if needed
