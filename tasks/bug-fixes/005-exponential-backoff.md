# Implement Exponential Backoff for Retries

**GitHub Issue**: #48 - https://github.com/bdperkin/nhl-scrabble/issues/48

## Priority

**LOW** - Should Do (Next Month)

## Estimated Effort

2-3 hours

## Description

The current retry logic uses a fixed delay between retries, which is not optimal for handling transient failures. Implementing exponential backoff will reduce load on the NHL API during outages and improve retry success rates.

## Current State

```python
def _make_request(self, endpoint: str) -> dict[str, Any]:
    """Make request to NHL API with retry logic."""
    url = f"{self.base_url}/{endpoint}"

    for attempt in range(self.retries + 1):
        try:
            response = self.session.get(url, timeout=self.timeout)
            # ... handle response ...
        except requests.RequestException as e:
            if attempt < self.retries:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.retries + 1}): {e}")
                time.sleep(1)  # <-- Fixed 1 second delay
                continue
            raise
```

**Issues**:

- Fixed 1s delay is not optimal
- Doesn't account for rate limiting (429 responses)
- Doesn't use jitter to prevent thundering herd
- Hard to configure

## Proposed Solution

Implement exponential backoff with jitter:

```python
import random


class NHLClient:
    def __init__(
        self,
        timeout: int = 10,
        retries: int = 3,
        rate_limit_delay: float = 0.3,
        backoff_factor: float = 2.0,
        max_backoff: float = 30.0,
    ) -> None:
        """Initialize NHL API client.

        Args:
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            rate_limit_delay: Delay between successful requests
            backoff_factor: Multiplier for exponential backoff (default: 2.0)
            max_backoff: Maximum backoff delay in seconds (default: 30.0)
        """
        self.timeout = timeout
        self.retries = retries
        self.rate_limit_delay = rate_limit_delay
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        # ...

    def _calculate_backoff_delay(self, attempt: int, retry_after: int | None = None) -> float:
        """Calculate backoff delay with exponential backoff and jitter.

        Args:
            attempt: Current attempt number (0-indexed)
            retry_after: Optional Retry-After header value from 429 response

        Returns:
            Delay in seconds
        """
        if retry_after is not None:
            # Respect Retry-After header from API
            return min(retry_after, self.max_backoff)

        # Exponential backoff: base_delay * (backoff_factor ** attempt)
        base_delay = 1.0
        delay = min(base_delay * (self.backoff_factor**attempt), self.max_backoff)

        # Add jitter: randomize ±25% to prevent thundering herd
        jitter = delay * 0.25
        delay = delay + random.uniform(-jitter, jitter)

        return max(0, delay)

    def _make_request(self, endpoint: str) -> dict[str, Any]:
        """Make request to NHL API with retry logic and exponential backoff."""
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_after_int = int(retry_after) if retry_after else None

                    if attempt < self.retries:
                        delay = self._calculate_backoff_delay(attempt, retry_after_int)
                        logger.warning(
                            f"Rate limited (429) on attempt {attempt + 1}/{self.retries + 1}, "
                            f"retrying after {delay:.2f}s"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        raise NHLApiError(f"Rate limited after {self.retries + 1} attempts")

                # ... handle other response codes ...

            except requests.RequestException as e:
                if attempt < self.retries:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.retries + 1}): {e}, "
                        f"retrying after {delay:.2f}s"
                    )
                    time.sleep(delay)
                    continue
                raise NHLApiError(f"Request failed after {self.retries + 1} attempts") from e
```

## Configuration

Add to `Config` dataclass and environment variables:

```python
@dataclass
class Config:
    """Application configuration."""

    # ... existing fields ...
    backoff_factor: float = 2.0
    max_backoff: float = 30.0
```

Environment variables:

- `NHL_SCRABBLE_BACKOFF_FACTOR` (default: 2.0)
- `NHL_SCRABBLE_MAX_BACKOFF` (default: 30.0)

## Testing Strategy

Add tests in `tests/unit/test_nhl_client.py`:

```python
import pytest
from unittest.mock import Mock, patch
from nhl_scrabble.api import NHLClient


def test_calculate_backoff_delay_exponential():
    """Test exponential backoff calculation."""
    client = NHLClient(backoff_factor=2.0)

    # First retry: ~1 second
    delay0 = client._calculate_backoff_delay(0)
    assert 0.75 <= delay0 <= 1.25  # 1.0 ± 25%

    # Second retry: ~2 seconds
    delay1 = client._calculate_backoff_delay(1)
    assert 1.5 <= delay1 <= 2.5  # 2.0 ± 25%

    # Third retry: ~4 seconds
    delay2 = client._calculate_backoff_delay(2)
    assert 3.0 <= delay2 <= 5.0  # 4.0 ± 25%


def test_calculate_backoff_delay_respects_max():
    """Test that backoff delay respects max_backoff."""
    client = NHLClient(backoff_factor=2.0, max_backoff=5.0)

    # Large attempt number should be capped at max_backoff
    delay = client._calculate_backoff_delay(10)
    assert delay <= 5.0


def test_calculate_backoff_delay_respects_retry_after():
    """Test that Retry-After header is respected."""
    client = NHLClient()

    # Retry-After should be used directly
    delay = client._calculate_backoff_delay(0, retry_after=10)
    assert delay == 10.0


def test_retry_with_exponential_backoff():
    """Test that retries use exponential backoff."""
    with NHLClient(retries=3) as client:
        with patch("requests.Session.get") as mock_get, patch("time.sleep") as mock_sleep:

            # First 3 attempts fail, 4th succeeds
            mock_get.side_effect = [
                requests.RequestException("Error 1"),
                requests.RequestException("Error 2"),
                requests.RequestException("Error 3"),
                Mock(status_code=200, json=lambda: {"data": "success"}),
            ]

            result = client._make_request("endpoint")

            # Should have slept 3 times with increasing delays
            assert mock_sleep.call_count == 3
            delays = [call[0][0] for call in mock_sleep.call_args_list]

            # Each delay should be larger than the previous (roughly)
            assert delays[1] > delays[0]
            assert delays[2] > delays[1]


def test_429_rate_limit_with_retry_after():
    """Test that 429 responses with Retry-After are handled."""
    with NHLClient(retries=2) as client:
        with patch("requests.Session.get") as mock_get, patch("time.sleep") as mock_sleep:

            # First attempt: 429 with Retry-After, second: success
            rate_limit_response = Mock()
            rate_limit_response.status_code = 429
            rate_limit_response.headers = {"Retry-After": "5"}

            success_response = Mock()
            success_response.status_code = 200
            success_response.json.return_value = {"data": "success"}

            mock_get.side_effect = [rate_limit_response, success_response]

            result = client._make_request("endpoint")

            # Should have slept for Retry-After duration
            mock_sleep.assert_called_once()
            assert mock_sleep.call_args[0][0] == 5.0
```

## Acceptance Criteria

- [ ] Exponential backoff implemented with configurable factor
- [ ] Maximum backoff delay is enforced
- [ ] Jitter is added to prevent thundering herd
- [ ] 429 responses with Retry-After header are respected
- [ ] Configuration is exposed via environment variables
- [ ] Unit tests verify backoff calculation
- [ ] Integration tests verify retry behavior
- [ ] Documentation updated with retry strategy

## Related Files

- `src/nhl_scrabble/api/nhl_client.py`
- `src/nhl_scrabble/config.py`
- `tests/unit/test_nhl_client.py`
- `README.md` (environment variables)

## Dependencies

None - uses Python stdlib `random` module

## Performance Impact

- **Better**: Faster recovery from transient failures
- **Polite**: Reduces load on NHL API during outages
- **Reliable**: Higher success rate for retries

## Additional Notes

Consider using a library like `tenacity` or `backoff` for more advanced retry logic, but the custom implementation is simple and doesn't add dependencies.

**Example Backoff Timeline**:

- Attempt 1: Immediate
- Attempt 2: Wait ~1s (1 * 2^0 ± jitter)
- Attempt 3: Wait ~2s (1 * 2^1 ± jitter)
- Attempt 4: Wait ~4s (1 * 2^2 ± jitter)
- Total: ~7s for 4 attempts (vs. 3s with fixed delay)
