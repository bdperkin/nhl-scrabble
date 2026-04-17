# Skip Rate Limiting on Cache Hits

**GitHub Issue**: #141 - https://github.com/bdperkin/nhl-scrabble/issues/141

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Skip rate limit delays when serving data from cache to improve performance. Currently, rate limiting applies even for cache hits, unnecessarily slowing down cached responses.

## Current State

```python
# src/nhl_scrabble/api/nhl_client.py
def get_team_roster(self, team_abbrev: str):
    # Check cache
    if team_abbrev in self.cache:
        time.sleep(self.rate_limit_delay)  # Unnecessary!
        return self.cache[team_abbrev]

    # Fetch from API
    time.sleep(self.rate_limit_delay)
    response = self.session.get(url)
```

## Proposed Solution

```python
def get_team_roster(self, team_abbrev: str):
    # Check cache first
    if team_abbrev in self.cache:
        return self.cache[team_abbrev]  # No delay!

    # Only rate limit for actual API calls
    time.sleep(self.rate_limit_delay)
    response = self.session.get(url)
    self.cache[team_abbrev] = result
    return result
```

## Implementation Steps

1. Move rate limiting after cache check
1. Add tests for cache hit behavior
1. Benchmark performance improvement
1. Update documentation

## Testing Strategy

```python
def test_no_rate_limit_on_cache_hit():
    client = NHLApiClient(rate_limit_delay=1.0)

    # First call (cache miss) - rate limited
    start = time.time()
    client.get_team_roster("TOR")
    first_duration = time.time() - start
    assert first_duration >= 1.0

    # Second call (cache hit) - no rate limit
    start = time.time()
    client.get_team_roster("TOR")
    second_duration = time.time() - start
    assert second_duration < 0.1  # Much faster!
```

## Acceptance Criteria

- [ ] Rate limiting skipped on cache hits
- [ ] Tests verify behavior
- [ ] Performance improvement measured
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/api/nhl_client.py` - Update rate limiting

## Dependencies

None

## Additional Notes

**Expected Improvement**: 5-10x faster for cached requests

## Implementation Notes

*To be filled during implementation*
