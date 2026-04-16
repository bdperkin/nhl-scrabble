# Fix Rate Limiting to Only Apply After Successful Requests

**GitHub Issue**: #47 - https://github.com/bdperkin/nhl-scrabble/issues/47

## Priority

**LOW** - Should Do (Next Month)

## Estimated Effort

1 hour

## Description

The current rate limiting implementation sleeps after every roster fetch, including failed requests. This means failed requests still consume the rate limit delay, which is unnecessary and slows down error recovery.

## Current State

```python
def fetch_all_team_scores(self) -> list[TeamScore]:
    """Fetch and calculate scores for all NHL teams."""
    # ... get standings ...

    for team in teams:
        try:
            roster = self.client.get_team_roster(team.abbrev)
            team_score = self.processor.process_team(team, roster)
            team_scores.append(team_score)
        except Exception as e:
            logger.error(f"Failed to fetch roster for {team.name}: {e}")
            continue
        finally:
            # Sleep after each roster fetch to respect rate limits
            time.sleep(self.config.rate_limit_delay)  # <-- Sleeps even on failure
```

**Issue**: If 5 teams fail, we waste `5 * 0.3s = 1.5s` sleeping unnecessarily.

## Proposed Solution

Only sleep after successful requests:

```python
def fetch_all_team_scores(self) -> list[TeamScore]:
    """Fetch and calculate scores for all NHL teams."""
    # ... get standings ...

    for team in teams:
        try:
            roster = self.client.get_team_roster(team.abbrev)
            team_score = self.processor.process_team(team, roster)
            team_scores.append(team_score)

            # Sleep after successful fetch to respect rate limits
            time.sleep(self.config.rate_limit_delay)
        except Exception as e:
            logger.error(f"Failed to fetch roster for {team.name}: {e}")
            # No sleep on failure - retry immediately or move to next team
            continue
```

Alternative: Move rate limiting into `NHLClient._make_request()`:

```python
class NHLClient:
    def __init__(self, timeout: int = 10, retries: int = 3, rate_limit_delay: float = 0.3) -> None:
        """Initialize NHL API client."""
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time: float | None = None

    def _make_request(self, endpoint: str) -> dict[str, Any]:
        """Make request to NHL API with retry logic and rate limiting."""
        # Rate limit: Ensure minimum delay between requests
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)

        # ... make request ...

        # Record successful request time
        self._last_request_time = time.time()
        return response.json()
```

**Benefits of moving to client**:

- Rate limiting is centralized
- Automatically applies to all API calls
- No need for explicit sleeps in calling code
- Failed requests don't affect rate limiting

## Testing Strategy

Add tests in `tests/unit/test_nhl_client.py`:

```python
import time
import pytest
from unittest.mock import Mock, patch
from nhl_scrabble.api import NHLClient

def test_rate_limiting_between_successful_requests():
    """Test that rate limiting applies between successful requests."""
    with NHLClient(rate_limit_delay=0.1) as client:
        with patch('requests.Session.get') as mock_get:
            # Mock successful responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_get.return_value = mock_response

            # First request
            start = time.time()
            client._make_request("endpoint1")

            # Second request should be delayed
            client._make_request("endpoint2")
            elapsed = time.time() - start

            # Should take at least rate_limit_delay
            assert elapsed >= 0.1

def test_no_rate_limiting_on_first_request():
    """Test that first request has no delay."""
    with NHLClient(rate_limit_delay=1.0) as client:
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_get.return_value = mock_response

            start = time.time()
            client._make_request("endpoint1")
            elapsed = time.time() - start

            # First request should be fast (< 0.5s)
            assert elapsed < 0.5

def test_failed_request_doesnt_affect_rate_limiting():
    """Test that failed requests don't affect rate limiting."""
    with NHLClient(rate_limit_delay=0.1) as client:
        with patch('requests.Session.get') as mock_get:
            # First request succeeds
            success_response = Mock()
            success_response.status_code = 200
            success_response.json.return_value = {"data": "test"}

            # Second request fails
            mock_get.side_effect = [
                success_response,
                requests.RequestException("Network error")
            ]

            start = time.time()
            client._make_request("endpoint1")

            # Failed request should not sleep
            with pytest.raises(requests.RequestException):
                client._make_request("endpoint2")

            elapsed = time.time() - start
            # Should not have slept for failed request
            assert elapsed < 0.2  # Less than rate_limit_delay * 2
```

## Acceptance Criteria

- [ ] Rate limiting only applies after successful requests
- [ ] Failed requests do not consume rate limit delay
- [ ] First request has no delay
- [ ] Subsequent successful requests are properly delayed
- [ ] Unit tests verify rate limiting behavior
- [ ] Integration tests show improved performance with failed requests
- [ ] Documentation updated to explain rate limiting behavior

## Related Files

- `src/nhl_scrabble/api/nhl_client.py`
- `tests/unit/test_nhl_client.py`

## Dependencies

None - standalone fix

## Performance Impact

- **Current**: With 5 failed requests: ~1.5s wasted
- **After fix**: With 5 failed requests: ~0s wasted
- **Improvement**: Faster error recovery

## Additional Notes

Consider also implementing adaptive rate limiting based on response headers (if NHL API provides rate limit information).
