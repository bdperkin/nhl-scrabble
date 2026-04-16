# Implement API Response Caching

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

3-4 hours

## Description

The application currently makes 32+ API calls every time it runs (1 for standings + 31 for team rosters). NHL roster data changes infrequently (daily at most), so caching responses can dramatically improve performance and reduce load on the NHL API.

## Current State

```python
# Every run makes fresh API calls
standings = client.get_standings()  # Call 1
for team in teams:
    roster = client.get_team_roster(team.abbrev)  # Calls 2-32
```

**Performance**:

- Cold run: ~30 seconds (32 API calls with rate limiting)
- Warm run: ~30 seconds (no cache, same as cold)

**Impact on NHL API**: 32 requests per run, hundreds per day during development

## Proposed Solution

Use `requests-cache` library for automatic HTTP caching:

```python
import requests_cache
from datetime import timedelta

class NHLClient:
    def __init__(
        self,
        timeout: int = 10,
        retries: int = 3,
        rate_limit_delay: float = 0.3,
        cache_enabled: bool = True,
        cache_expiry: int = 3600,  # 1 hour default
    ) -> None:
        """Initialize NHL API client.

        Args:
            cache_enabled: Enable HTTP caching (default: True)
            cache_expiry: Cache expiration in seconds (default: 3600 = 1 hour)
        """
        if cache_enabled:
            # Create cached session
            self.session = requests_cache.CachedSession(
                cache_name='.nhl_cache',
                backend='sqlite',
                expire_after=timedelta(seconds=cache_expiry),
                allowable_codes=[200],  # Only cache successful responses
                allowable_methods=['GET'],
                cache_control=True,  # Respect Cache-Control headers
            )
        else:
            self.session = requests.Session()

        self.cache_enabled = cache_enabled
        # ... rest of init ...

    def clear_cache(self) -> None:
        """Clear the HTTP cache."""
        if self.cache_enabled and hasattr(self.session, 'cache'):
            self.session.cache.clear()
            logger.info("Cache cleared")
```

Add CLI option to control caching:

```python
@click.command()
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable API response caching (always fetch fresh data)",
)
@click.option(
    "--clear-cache",
    is_flag=True,
    help="Clear API cache before running",
)
def analyze(no_cache: bool, clear_cache: bool, ...):
    """Analyze NHL player names by Scrabble score."""
    config = Config.from_env()

    # Override cache setting from CLI
    if no_cache:
        config.cache_enabled = False

    with NHLClient(
        cache_enabled=config.cache_enabled,
        cache_expiry=config.cache_expiry
    ) as client:
        if clear_cache:
            client.clear_cache()

        # ... rest of analyze ...
```

Add configuration:

```python
@dataclass
class Config:
    """Application configuration."""
    # ... existing fields ...
    cache_enabled: bool = True
    cache_expiry: int = 3600  # 1 hour
```

Environment variables:

- `NHL_SCRABBLE_CACHE_ENABLED` (default: true)
- `NHL_SCRABBLE_CACHE_EXPIRY` (default: 3600)

## Testing Strategy

Add tests in `tests/unit/test_nhl_client.py`:

```python
import pytest
import requests_cache
from pathlib import Path
from nhl_scrabble.api import NHLClient

def test_caching_enabled_by_default():
    """Test that caching is enabled by default."""
    with NHLClient() as client:
        assert client.cache_enabled
        assert isinstance(client.session, requests_cache.CachedSession)

def test_caching_can_be_disabled():
    """Test that caching can be disabled."""
    with NHLClient(cache_enabled=False) as client:
        assert not client.cache_enabled
        assert isinstance(client.session, requests.Session)
        assert not isinstance(client.session, requests_cache.CachedSession)

def test_cache_expiry_configured():
    """Test that cache expiry is configurable."""
    with NHLClient(cache_expiry=7200) as client:
        assert client.session.settings.expire_after.total_seconds() == 7200

def test_cached_response_used():
    """Test that cached responses are used."""
    with NHLClient() as client:
        # Clear cache
        client.clear_cache()

        # First request - should hit API
        response1 = client.get_standings()

        # Second request - should use cache
        response2 = client.get_standings()

        # Should be identical
        assert response1 == response2

        # Check cache statistics
        assert client.session.cache.responses.count() > 0

def test_cache_respects_expiry(monkeypatch):
    """Test that cache expires after configured time."""
    with NHLClient(cache_expiry=1) as client:
        client.clear_cache()

        # First request
        response1 = client.get_standings()

        # Wait for cache to expire
        import time
        time.sleep(2)

        # Second request - cache expired, should hit API again
        response2 = client.get_standings()

        # Responses should still match (same data)
        assert response1 == response2

def test_clear_cache():
    """Test that clear_cache() works."""
    with NHLClient() as client:
        # Make request to populate cache
        client.get_standings()
        assert client.session.cache.responses.count() > 0

        # Clear cache
        client.clear_cache()
        assert client.session.cache.responses.count() == 0

def test_cache_file_created():
    """Test that cache file is created."""
    cache_file = Path('.nhl_cache.sqlite')

    # Remove cache file if exists
    if cache_file.exists():
        cache_file.unlink()

    with NHLClient() as client:
        client.get_standings()

    # Cache file should be created
    assert cache_file.exists()

    # Cleanup
    cache_file.unlink()
```

Add integration tests in `tests/integration/test_caching.py`:

```python
import pytest
import time
from pathlib import Path
from nhl_scrabble.api import NHLClient

def test_caching_performance():
    """Test that caching improves performance."""
    cache_file = Path('.nhl_cache.sqlite')
    if cache_file.exists():
        cache_file.unlink()

    with NHLClient() as client:
        # First run - cold cache
        start = time.time()
        standings1 = client.get_standings()
        duration_cold = time.time() - start

        # Second run - warm cache
        start = time.time()
        standings2 = client.get_standings()
        duration_warm = time.time() - start

        # Warm should be much faster
        assert duration_warm < duration_cold / 10

        # Data should match
        assert standings1 == standings2

    # Cleanup
    if cache_file.exists():
        cache_file.unlink()
```

## Acceptance Criteria

- [ ] `requests-cache` dependency added to `pyproject.toml`
- [ ] Caching enabled by default with 1-hour expiry
- [ ] `--no-cache` CLI flag to disable caching
- [ ] `--clear-cache` CLI flag to clear cache before run
- [ ] Environment variables to configure caching
- [ ] Cache file is `.gitignore`d
- [ ] Unit tests verify caching behavior
- [ ] Integration tests measure performance improvement
- [ ] Documentation updated with caching information

## Related Files

- `src/nhl_scrabble/api/nhl_client.py`
- `src/nhl_scrabble/config.py`
- `src/nhl_scrabble/cli.py`
- `pyproject.toml` (add requests-cache dependency)
- `.gitignore` (add .nhl_cache.sqlite)
- `tests/unit/test_nhl_client.py`
- `tests/integration/test_caching.py` (new)
- `README.md` (document caching)

## Dependencies

- `requests-cache` (new dependency)

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing ...
    "requests-cache>=1.2.0",
]
```

## Performance Impact

**Before** (no cache):

- First run: 30 seconds (32 API calls)
- Second run: 30 seconds (32 API calls)
- Development workflow: Slow iterations

**After** (with cache):

- First run: 30 seconds (32 API calls, populates cache)
- Second run: \<1 second (0 API calls, uses cache)
- Development workflow: Fast iterations

**Improvement**: 30x faster for cached runs

## Configuration Examples

```bash
# Default: 1-hour cache
nhl-scrabble analyze

# Disable cache (always fresh data)
nhl-scrabble analyze --no-cache

# Clear cache before running
nhl-scrabble analyze --clear-cache

# Custom cache expiry via environment
export NHL_SCRABBLE_CACHE_EXPIRY=7200  # 2 hours
nhl-scrabble analyze

# Disable cache via environment
export NHL_SCRABBLE_CACHE_ENABLED=false
nhl-scrabble analyze
```

## Additional Notes

**Cache invalidation**: The cache automatically expires after the configured time. For immediate updates:

```bash
# Manual cache clear
rm .nhl_cache.sqlite

# Or use CLI flag
nhl-scrabble analyze --clear-cache
```

**Cache location**: `.nhl_cache.sqlite` in current directory. Consider moving to user cache directory:

```python
import appdirs
cache_dir = appdirs.user_cache_dir("nhl-scrabble", "bdperkin")
cache_file = Path(cache_dir) / "api_cache.sqlite"
```

**Cache size**: With 32 API responses, cache file is ~100KB. Not a concern.

**Production use**: In production, consider:

- Longer cache expiry (6-24 hours)
- Shared cache for multiple runs
- Cache warm-up before first use

## Future Enhancements

- [ ] Add cache statistics to output (X cached, Y fresh)
- [ ] Add `--cache-status` command to show cache contents
- [ ] Support per-endpoint expiry (standings: 1h, rosters: 24h)
- [ ] Add cache warm-up command
- [ ] Support redis backend for shared cache
