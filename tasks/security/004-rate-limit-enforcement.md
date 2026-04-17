# Implement API Rate Limit Enforcement

**GitHub Issue**: #131 - https://github.com/bdperkin/nhl-scrabble/issues/131

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Implement comprehensive API rate limiting to prevent abuse of the NHL API, protect against denial-of-service, and ensure reliable operation within NHL API quota limits.

Currently the application only has a basic fixed delay (0.3s) between requests with no tracking of actual request rates, no enforcement of quotas, and no handling of rate limit responses (HTTP 429). This makes the application vulnerable to API bans and doesn't respect the NHL API's rate limits.

**Impact**: Prevent API abuse, avoid IP bans, ensure reliable operation, protect against accidental DoS

**Problems Addressed**:

- Accidental API abuse from rapid successive runs
- No protection against hitting NHL API rate limits
- No graceful handling of 429 (Too Many Requests) responses
- No visibility into API quota usage
- Could cause IP ban if rate limits violated

## Current State

**Basic delay only, no rate limiting**:

```python
# src/nhl_scrabble/api/nhl_client.py
class NHLApiClient:
    def __init__(
        self,
        base_url: str = "https://api-web.nhle.com",
        timeout: int = 10,
        max_retries: int = 3,
        rate_limit_delay: float = 0.3,  # Fixed delay only
    ):
        self.rate_limit_delay = rate_limit_delay
        # No rate limiter, no quota tracking

    def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:
        """Fetch roster - just waits fixed delay."""
        # Simple delay, no actual rate limiting
        time.sleep(self.rate_limit_delay)

        url = f"{self.base_url}/v1/roster/{team_abbrev}/current"
        response = self._make_request("GET", url)
        # No handling of 429 responses
        return response
```

**Missing functionality**:

1. **No rate limit tracking**:

   - Doesn't count requests per time window
   - Doesn't track quota usage
   - Can't detect when approaching limits

1. **No 429 handling**:

   ```python
   # Current: No special handling for rate limits
   response = self.session.get(url, timeout=self.timeout)
   response.raise_for_status()  # Raises HTTPError on 429
   # Doesn't retry with backoff
   # Doesn't respect Retry-After header
   ```

1. **No quota warnings**:

   - No visibility into how many requests made
   - Can't warn user when approaching limits
   - No metrics for monitoring

1. **Fixed delay inefficient**:

   - Always waits 0.3s even if safe to go faster
   - Wastes time when under limit
   - Doesn't adapt to actual quota

**Vulnerability examples**:

```bash
# Scenario 1: Rapid successive runs
nhl-scrabble analyze  # Run 1: 30 teams × 0.3s = 9s
nhl-scrabble analyze  # Run 2: 30 teams × 0.3s = 9s
nhl-scrabble analyze  # Run 3: 30 teams × 0.3s = 9s
# Total: 90 requests in ~27 seconds
# Could hit rate limit if NHL API allows <90/30s

# Scenario 2: Multiple instances
# User runs multiple terminals simultaneously
# Each makes 30 requests, no coordination
# Could violate rate limits

# Scenario 3: CI/CD
# Automated testing runs analyzer repeatedly
# No rate limit protection
# Could get IP banned
```

## Proposed Solution

Implement token bucket rate limiter with 429 handling and quota tracking:

**Token Bucket Algorithm**:

- Bucket holds N tokens (max requests)
- Tokens refill at rate R per second
- Each request consumes 1 token
- Block when bucket empty

**Step 1: Create rate limiter module**:

```python
# src/nhl_scrabble/rate_limiter.py
"""Rate limiting for API requests."""

import time
import threading
from typing import Optional

class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Limits requests to a maximum rate while allowing bursts.
    Thread-safe for concurrent use.
    """

    def __init__(
        self,
        max_requests: int = 30,
        time_window: float = 60.0,
        burst_size: Optional[int] = None,
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per time window
            time_window: Time window in seconds (default: 60s = 1 minute)
            burst_size: Max burst size (default: max_requests)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.burst_size = burst_size or max_requests

        # Token bucket
        self.tokens = float(self.burst_size)
        self.last_update = time.monotonic()

        # Thread safety
        self.lock = threading.Lock()

        # Metrics
        self.total_requests = 0
        self.total_waits = 0
        self.total_wait_time = 0.0

    @property
    def refill_rate(self) -> float:
        """Calculate token refill rate (tokens per second)."""
        return self.max_requests / self.time_window

    def _refill_tokens(self) -> None:
        """Refill tokens based on time elapsed."""
        now = time.monotonic()
        elapsed = now - self.last_update

        # Add tokens based on elapsed time
        self.tokens = min(
            self.burst_size,
            self.tokens + (elapsed * self.refill_rate)
        )

        self.last_update = now

    def acquire(self, tokens: int = 1, block: bool = True) -> bool:
        """
        Acquire tokens from bucket.

        Args:
            tokens: Number of tokens to acquire (default: 1)
            block: Whether to block until tokens available (default: True)

        Returns:
            True if tokens acquired, False if not available (non-blocking only)
        """
        with self.lock:
            self._refill_tokens()

            # Check if tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.total_requests += 1
                return True

            # Non-blocking mode
            if not block:
                return False

            # Calculate wait time
            deficit = tokens - self.tokens
            wait_time = deficit / self.refill_rate

            # Metrics
            self.total_waits += 1
            self.total_wait_time += wait_time

        # Wait outside lock
        time.sleep(wait_time)

        # Try again after waiting
        with self.lock:
            self._refill_tokens()
            self.tokens -= tokens
            self.total_requests += 1
            return True

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        with self.lock:
            return {
                "total_requests": self.total_requests,
                "total_waits": self.total_waits,
                "total_wait_time": self.total_wait_time,
                "average_wait": (
                    self.total_wait_time / self.total_waits
                    if self.total_waits > 0
                    else 0.0
                ),
                "current_tokens": self.tokens,
                "max_tokens": self.burst_size,
            }

    def reset(self) -> None:
        """Reset rate limiter (for testing)."""
        with self.lock:
            self.tokens = float(self.burst_size)
            self.last_update = time.monotonic()
            self.total_requests = 0
            self.total_waits = 0
            self.total_wait_time = 0.0
```

**Step 2: Integrate into API client**:

```python
# src/nhl_scrabble/api/nhl_client.py
from nhl_scrabble.rate_limiter import RateLimiter
import requests

class NHLApiClient:
    def __init__(
        self,
        base_url: str = "https://api-web.nhle.com",
        timeout: int = 10,
        max_retries: int = 3,
        rate_limit_max_requests: int = 30,
        rate_limit_window: float = 60.0,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=rate_limit_max_requests,
            time_window=rate_limit_window,
        )

        logger.info(
            f"Rate limiter initialized: {rate_limit_max_requests} "
            f"requests per {rate_limit_window}s"
        )

    def _make_request(self, method: str, url: str) -> dict[str, Any]:
        """
        Make HTTP request with rate limiting and 429 handling.

        Args:
            method: HTTP method
            url: Full URL

        Returns:
            Response JSON

        Raises:
            NHLApiError: If request fails
        """
        # Acquire rate limit token (blocks if necessary)
        self.rate_limiter.acquire()

        # Make request with retry logic for 429
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = self._get_retry_after(response)

                    logger.warning(
                        f"Rate limited (429) on attempt {attempt}. "
                        f"Waiting {retry_after}s before retry."
                    )

                    # Wait as requested by API
                    time.sleep(retry_after)

                    # Continue to next retry attempt
                    continue

                # Raise for other errors
                response.raise_for_status()

                # Success
                return response.json()

            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    raise NHLApiError(f"Request timeout after {attempt} attempts")
                time.sleep(2 ** attempt)  # Exponential backoff

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    raise NHLApiError(f"Request failed: {e}")
                time.sleep(2 ** attempt)

        raise NHLApiError(f"Request failed after {self.max_retries} attempts")

    def _get_retry_after(self, response: requests.Response) -> float:
        """
        Extract Retry-After header value.

        Args:
            response: HTTP response with 429 status

        Returns:
            Seconds to wait before retry
        """
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                # Try as integer (seconds)
                return float(retry_after)
            except ValueError:
                # Could be HTTP date format, but uncommon for 429
                # Default to exponential backoff
                pass

        # No Retry-After header, use exponential backoff
        # Start with 1 second, double on each 429
        return 1.0

    def get_rate_limit_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics."""
        return self.rate_limiter.get_stats()
```

**Step 3: Add configuration**:

```python
# src/nhl_scrabble/config.py
class NHLScrabbleConfig(BaseModel):
    """Configuration for NHL Scrabble application."""

    # Existing fields...

    # Rate limiting
    rate_limit_max_requests: int = 30
    rate_limit_window: float = 60.0  # seconds

    @field_validator("rate_limit_max_requests")
    @classmethod
    def validate_max_requests(cls, v: int) -> int:
        """Validate max requests is reasonable."""
        if v < 1:
            raise ValueError("rate_limit_max_requests must be at least 1")
        if v > 1000:
            raise ValueError("rate_limit_max_requests cannot exceed 1000")
        return v

    @field_validator("rate_limit_window")
    @classmethod
    def validate_time_window(cls, v: float) -> float:
        """Validate time window is reasonable."""
        if v < 1.0:
            raise ValueError("rate_limit_window must be at least 1 second")
        if v > 3600.0:
            raise ValueError("rate_limit_window cannot exceed 1 hour")
        return v
```

**Step 4: Add quota warnings**:

```python
# src/nhl_scrabble/cli.py
def analyze(...):
    """Run NHL Scrabble analysis."""
    # ... fetch data ...

    # Show rate limit stats if verbose
    if config.verbose:
        stats = client.get_rate_limit_stats()
        click.echo(f"\nAPI Rate Limit Stats:")
        click.echo(f"  Total requests: {stats['total_requests']}")
        click.echo(f"  Total waits: {stats['total_waits']}")
        click.echo(f"  Average wait: {stats['average_wait']:.2f}s")
```

## Implementation Steps

1. **Create rate limiter module**:

   - Create `src/nhl_scrabble/rate_limiter.py`
   - Implement `RateLimiter` class with token bucket algorithm
   - Make thread-safe with threading.Lock
   - Add metrics tracking

1. **Integrate into API client**:

   - Add rate limiter to `NHLApiClient.__init__()`
   - Call `acquire()` before each request
   - Implement 429 response handling
   - Parse and respect `Retry-After` headers

1. **Add configuration**:

   - Add rate limit config to `NHLScrabbleConfig`
   - Add environment variable support
   - Add validation for limits

1. **Add stats/monitoring**:

   - Implement `get_stats()` method
   - Log rate limit events
   - Display stats in verbose mode

1. **Add tests**:

   - Unit tests for RateLimiter
   - Test token bucket algorithm
   - Test 429 handling
   - Test thread safety

1. **Update documentation**:

   - Document rate limits in README
   - Add environment variable docs
   - Document 429 handling behavior

## Testing Strategy

**Unit tests** (`tests/unit/test_rate_limiter.py`):

```python
import time
import pytest
import threading
from nhl_scrabble.rate_limiter import RateLimiter

class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_basic_rate_limiting(self):
        """Test basic rate limiting behavior."""
        limiter = RateLimiter(max_requests=2, time_window=1.0)

        # First 2 requests should be instant
        start = time.monotonic()
        limiter.acquire()
        limiter.acquire()
        assert time.monotonic() - start < 0.1

        # Third request should wait
        start = time.monotonic()
        limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.4  # Should wait for token refill

    def test_burst_size(self):
        """Test burst size allows initial burst."""
        limiter = RateLimiter(max_requests=10, time_window=10.0, burst_size=5)

        # Can make 5 requests immediately (burst)
        start = time.monotonic()
        for _ in range(5):
            limiter.acquire()
        assert time.monotonic() - start < 0.1

        # 6th request waits for refill
        start = time.monotonic()
        limiter.acquire()
        assert time.monotonic() - start >= 0.5

    def test_non_blocking_mode(self):
        """Test non-blocking acquire mode."""
        limiter = RateLimiter(max_requests=1, time_window=10.0)

        # First request succeeds
        assert limiter.acquire(block=False) is True

        # Second request fails (no tokens)
        assert limiter.acquire(block=False) is False

    def test_thread_safety(self):
        """Test rate limiter is thread-safe."""
        limiter = RateLimiter(max_requests=10, time_window=1.0)
        results = []

        def make_requests():
            for _ in range(5):
                limiter.acquire()
                results.append(1)

        # Create multiple threads
        threads = [threading.Thread(target=make_requests) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # All requests should succeed
        assert len(results) == 15
        assert limiter.total_requests == 15

    def test_stats_tracking(self):
        """Test statistics tracking."""
        limiter = RateLimiter(max_requests=2, time_window=1.0)

        # Make requests
        limiter.acquire()
        limiter.acquire()
        limiter.acquire()  # This one waits

        stats = limiter.get_stats()
        assert stats["total_requests"] == 3
        assert stats["total_waits"] == 1
        assert stats["total_wait_time"] > 0
        assert stats["average_wait"] > 0

    def test_reset(self):
        """Test resetting rate limiter."""
        limiter = RateLimiter(max_requests=1, time_window=10.0)

        # Use up token
        limiter.acquire()

        # Reset
        limiter.reset()

        # Should have token again
        assert limiter.acquire(block=False) is True
```

**Integration tests** (`tests/integration/test_api_rate_limiting.py`):

```python
import pytest
from unittest.mock import Mock, patch
from nhl_scrabble.api.nhl_client import NHLApiClient

def test_api_client_rate_limiting():
    """Test API client enforces rate limiting."""
    client = NHLApiClient(rate_limit_max_requests=2, rate_limit_window=1.0)

    with patch.object(client.session, 'request') as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = {"data": "test"}

        # First 2 requests should be fast
        import time
        start = time.monotonic()
        client._make_request("GET", "http://test.com/1")
        client._make_request("GET", "http://test.com/2")
        assert time.monotonic() - start < 0.1

        # Third request should wait
        start = time.monotonic()
        client._make_request("GET", "http://test.com/3")
        assert time.monotonic() - start >= 0.4

def test_api_client_429_handling():
    """Test API client handles 429 responses."""
    client = NHLApiClient()

    with patch.object(client.session, 'request') as mock_request:
        # First call returns 429, second succeeds
        response_429 = Mock()
        response_429.status_code = 429
        response_429.headers = {"Retry-After": "1"}

        response_200 = Mock()
        response_200.status_code = 200
        response_200.json.return_value = {"data": "test"}

        mock_request.side_effect = [response_429, response_200]

        # Should retry and succeed
        result = client._make_request("GET", "http://test.com")
        assert result == {"data": "test"}
        assert mock_request.call_count == 2
```

**Manual testing**:

```bash
# Test rate limiting
export NHL_SCRABBLE_RATE_LIMIT_MAX_REQUESTS=5
export NHL_SCRABBLE_RATE_LIMIT_WINDOW=10
nhl-scrabble analyze --verbose
# Should show rate limit stats, some requests wait

# Test rapid runs (should not violate limits)
for i in {1..3}; do nhl-scrabble analyze; done
# Should complete without errors, no 429 responses

# Test low rate limit (see waiting)
export NHL_SCRABBLE_RATE_LIMIT_MAX_REQUESTS=1
export NHL_SCRABBLE_RATE_LIMIT_WINDOW=5
nhl-scrabble analyze --verbose
# Should see many waits in stats
```

## Acceptance Criteria

- [ ] `rate_limiter.py` module created with `RateLimiter` class
- [ ] Token bucket algorithm implemented correctly
- [ ] Rate limiter is thread-safe (uses threading.Lock)
- [ ] `acquire()` method blocks when out of tokens
- [ ] Non-blocking mode supported (`acquire(block=False)`)
- [ ] Tokens refill at correct rate
- [ ] Burst size parameter works correctly
- [ ] Statistics tracking implemented (requests, waits, wait time)
- [ ] `get_stats()` method returns metrics
- [ ] `reset()` method clears state
- [ ] Integrated into `NHLApiClient`
- [ ] Rate limiter called before each API request
- [ ] 429 responses handled with retry
- [ ] `Retry-After` header respected
- [ ] Exponential backoff used when no Retry-After
- [ ] Rate limit config added to `NHLScrabbleConfig`
- [ ] Environment variables support rate limit config
- [ ] Config validation for rate limits
- [ ] Stats displayed in verbose mode
- [ ] Unit tests achieve 100% coverage of rate limiter
- [ ] Integration tests verify API client rate limiting
- [ ] Integration tests verify 429 handling
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No regressions in existing functionality

## Related Files

- `src/nhl_scrabble/rate_limiter.py` - New rate limiter module
- `src/nhl_scrabble/api/nhl_client.py` - Integrate rate limiting
- `src/nhl_scrabble/config.py` - Add rate limit configuration
- `src/nhl_scrabble/cli.py` - Display stats in verbose mode
- `tests/unit/test_rate_limiter.py` - Rate limiter unit tests
- `tests/integration/test_api_rate_limiting.py` - Integration tests
- `docs/reference/configuration.md` - Document rate limit config
- `README.md` - Document rate limiting feature

## Dependencies

**Python packages** (standard library):

- `time` - Time tracking (standard library)
- `threading` - Thread safety (standard library)
- `typing` - Type hints (standard library)

**Related tasks**:

- Builds on: Existing retry logic (`bug-fixes/005-exponential-backoff.md`)
- Complements: API caching (`optimization/001-api-caching.md`)

**No blocking dependencies** - Can be implemented immediately

## Additional Notes

**Token Bucket vs Sliding Window**:

- **Token Bucket** (chosen):

  - ✅ Allows bursts (good UX)
  - ✅ Simple to implement
  - ✅ Low memory overhead
  - ✅ Thread-safe with single lock

- **Sliding Window**:

  - ❌ More complex
  - ❌ Higher memory (stores timestamps)
  - ✅ More precise rate limiting

**Token Bucket chosen** for simplicity and burst handling.

**Rate Limit Recommendations**:

```python
# Conservative (safe for any API)
max_requests=30, time_window=60.0  # 30 req/min = 0.5 req/sec

# Moderate (most APIs allow this)
max_requests=60, time_window=60.0  # 60 req/min = 1 req/sec

# Aggressive (only if API allows)
max_requests=120, time_window=60.0  # 120 req/min = 2 req/sec
```

**Default of 30 req/min** chosen as conservative safe value.

**429 Response Handling**:

HTTP 429 responses include `Retry-After` header:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

We respect this header and wait the specified time.

**Exponential Backoff Strategy**:

If no `Retry-After` header:

- 1st 429: Wait 1s
- 2nd 429: Wait 2s
- 3rd 429: Wait 4s
- etc.

**Thread Safety**:

Rate limiter must be thread-safe because:

- Future: Concurrent API fetching (`optimization/002`)
- Testing: Parallel test execution
- General: Could be used in threaded context

**Performance Impact**:

- Token bucket overhead: ~1µs per request
- Lock acquisition: ~0.1µs per request
- Negligible compared to network latency (10-100ms)

**Monitoring Integration**:

Future could add:

- Prometheus metrics
- CloudWatch metrics
- Rate limit violations log
- Request rate dashboard

**Trade-offs**:

- **Pro**: Prevents API bans, more reliable
- **Pro**: Visibility into API usage
- **Con**: Slightly slower (waits when needed)
- **Con**: Additional complexity

**Breaking Changes**: None - only adds protection, doesn't change behavior

## Implementation Notes

*To be filled during implementation:*

- Actual rate limits chosen
- NHL API rate limit discovery
- Performance impact measured
- Any issues with thread safety
- Actual 429 responses encountered
- Deviations from proposed solution
- Actual effort vs estimated
