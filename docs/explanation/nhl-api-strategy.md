# NHL API Strategy

Understanding our approach to NHL API integration.

## The NHL API

NHL provides a public JSON API at `api-web.nhle.com` with endpoints for:

- Current standings
- Team rosters
- Player statistics
- Game schedules
- And more

## Why This API?

### Alternatives Considered

**Official NHL Stats API (stats.nhl.com)**:

- More comprehensive data
- Better documented
- ❌ More complex
- ❌ Requires API key (authentication)

**Third-party APIs (ESPN, The Sports DB)**:

- Easier to use
- ❌ Less reliable
- ❌ May have usage limits
- ❌ Not official source

**Web Scraping**:

- Could get any data
- ❌ Fragile (breaks when HTML changes)
- ❌ Violates terms of service
- ❌ Unethical

**Chose api-web.nhle.com**:

- ✅ Official NHL source
- ✅ No authentication required
- ✅ Simple JSON responses
- ✅ Reliable uptime
- ✅ Current roster data

## Integration Approach

### 1. Retry Logic

Network requests can fail. We retry automatically:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RequestException, Timeout))
)
def _fetch_with_retry(self, url: str) -> dict:
    response = self.session.get(url, timeout=self.timeout)
    response.raise_for_status()
    return response.json()
```

**Why?**:

- Temporary network blips
- Server momentary overload
- Connection resets

**Strategy**: Exponential backoff (wait longer each retry)

### 2. Rate Limiting

We delay between requests to be polite:

```python
def fetch_roster(self, team_abbrev: str) -> list[Player]:
    time.sleep(self.rate_limit_delay)  # Default 0.3s
    return self._fetch_with_retry(url)
```

**Why?**:

- Respect API provider
- Avoid being blocked
- Distribute load over time

**Trade-off**: Slower (but polite and reliable)

### 3. Caching

We cache API responses in memory:

```python
@lru_cache(maxsize=128)
def fetch_standings(self) -> list[Team]:
    return self._fetch_standings_uncached()
```

**Why?**:

- Reduce redundant requests
- Faster subsequent runs
- Less load on NHL servers

**Trade-off**: May show slightly stale data

### 4. Error Handling

We handle errors gracefully:

```python
try:
    roster = api_client.fetch_roster(team_abbrev)
except NHLApiError as e:
    logger.error(f"Failed to fetch {team_abbrev}: {e}")
    failed_teams.append(team_abbrev)
    continue  # Process other teams
```

**Why?**:

- One team failure shouldn't break entire analysis
- User gets partial results
- Failures are logged for debugging

## Data Validation

We validate API responses using Pydantic:

```python
class Player(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    sweaterNumber: int | None = None
    positionCode: str
```

**Why?**:

- Catch API changes early
- Type-safe data
- Self-documenting code
- Clear error messages

## Trade-offs

### Synchronous vs Async

**Chose synchronous**:

- ✅ Simpler code
- ✅ Easier to understand
- ✅ Sufficient performance
- ❌ Could be faster with async

**Could optimize**: Fetch all rosters in parallel with asyncio (~3-5s instead of ~10-15s)

### Caching Strategy

**Chose in-memory LRU cache**:

- ✅ Simple implementation
- ✅ Works for CLI use
- ❌ Cache lost between runs
- ❌ Not shared across instances

**Could optimize**: Redis cache for persistent, shared caching

### Error Handling Philosophy

**Chose graceful degradation**:

- ✅ Partial results better than none
- ✅ User can see what succeeded
- ❌ May be unexpected for users

**Alternative**: Fail fast on any error (more predictable but less useful)

## Future Improvements

### 1. Async/Parallel Fetching

```python
async def fetch_all_rosters(self, teams):
    tasks = [self.fetch_roster(t) for t in teams]
    return await asyncio.gather(*tasks)
```

Could reduce runtime from ~15s to ~3-5s.

### 2. Persistent Caching

```python
import redis

cache = redis.Redis()

@cache_with_redis(expiry=3600)
def fetch_standings():
    ...
```

Share cache across runs and users.

### 3. Webhook/Streaming

Subscribe to roster changes instead of polling:

```python
@on_roster_change
def handle_roster_update(team, changes):
    # Update scores automatically
    ...
```

Real-time updates without constant polling.

### 4. GraphQL Alternative

If NHL provides GraphQL:

```graphql
query {
  teams {
    abbreviation
    roster {
      firstName
      lastName
    }
  }
}
```

More efficient - fetch exactly what we need.

## Related

- [Architecture Overview](architecture.md) - Overall system design
- [API Client Reference](../reference/nhl-api.md) - API endpoints
- [Debug API Issues](../how-to/debug-api-issues.md) - Troubleshooting
- [Configure API Settings](../how-to/configure-api-settings.md) - Configuration
