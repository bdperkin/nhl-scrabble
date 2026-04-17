# Add DoS Prevention Mechanisms

**GitHub Issue**: #134 - https://github.com/bdperkin/nhl-scrabble/issues/134

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

2-3 hours

## Description

Add comprehensive DoS (Denial of Service) prevention mechanisms to the NHL API client to protect against resource exhaustion and service degradation.

Currently, the API client has no DoS protection:

- Unlimited concurrent requests (can exhaust system resources)
- No circuit breaker (continues hitting failing endpoints)
- No queue depth limits (memory exhaustion risk)
- No hard request timeouts (hanging requests)

This creates risks of:

- Resource exhaustion from too many concurrent requests
- Cascading failures from unresponsive endpoints
- Memory issues from unbounded request queues
- Service degradation under load

## Current State

```python
# src/nhl_scrabble/api/nhl_client.py
class NHLApiClient:
    def __init__(self):
        self.session = requests.Session()
        # No connection limits
        # No circuit breaker
        # No queue management

    def get_team_roster(self, team_abbrev: str) -> TeamRoster:
        # No hard timeout beyond requests default
        # No concurrent request limiting
        # Retries indefinitely on failure
        response = self.session.get(url, timeout=self.timeout)
```

**Problems**:

- Can create unlimited concurrent connections
- No protection against hanging endpoints
- No fast-fail mechanism for degraded services
- No queue depth control

## Proposed Solution

Implement multi-layer DoS protection:

### 1. Connection Pool Limits

```python
from requests.adapters import HTTPAdapter

class NHLApiClient:
    def __init__(
        self,
        max_connections: int = 10,
        max_connections_per_host: int = 5,
    ):
        self.session = requests.Session()

        # Limit connection pool size
        adapter = HTTPAdapter(
            pool_connections=max_connections,
            pool_maxsize=max_connections_per_host,
            max_retries=0,  # Handle retries ourselves
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
```

### 2. Circuit Breaker

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = requests.RequestException,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### 3. Request Queue with Depth Limits

```python
from queue import Queue, Full
from threading import Semaphore

class RequestQueue:
    def __init__(self, max_size: int = 100):
        self.queue = Queue(maxsize=max_size)
        self.semaphore = Semaphore(max_size)

    def enqueue(self, request, timeout: float = 1.0) -> bool:
        """Enqueue request, reject if queue full."""
        try:
            self.queue.put(request, timeout=timeout)
            return True
        except Full:
            raise QueueFullError("Request queue is full, system overloaded")
```

### 4. Hard Request Timeouts

```python
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Request exceeded hard timeout")

class NHLApiClient:
    def __init__(self, hard_timeout: float = 30.0):
        self.hard_timeout = hard_timeout

    def get_with_hard_timeout(self, url: str):
        # Set hard timeout using signal (Unix only)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.hard_timeout))

        try:
            response = self.session.get(url)
            signal.alarm(0)  # Cancel alarm
            return response
        except TimeoutError:
            signal.alarm(0)
            raise
```

### 5. Integration

```python
class NHLApiClient:
    def __init__(
        self,
        max_concurrent: int = 10,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
        queue_max_size: int = 100,
        hard_timeout: float = 30.0,
    ):
        # Connection pool limits
        adapter = HTTPAdapter(
            pool_connections=max_concurrent,
            pool_maxsize=max_concurrent,
        )
        self.session = requests.Session()
        self.session.mount("https://", adapter)

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            timeout=circuit_breaker_timeout,
        )

        # Request queue
        self.request_queue = RequestQueue(max_size=queue_max_size)

        # Timeouts
        self.hard_timeout = hard_timeout

    def get_team_roster(self, team_abbrev: str) -> TeamRoster:
        # Check circuit breaker
        if self.circuit_breaker.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit breaker open, NHL API unavailable"
            )

        # Enqueue request
        self.request_queue.enqueue({"team": team_abbrev})

        # Make request with circuit breaker
        try:
            return self.circuit_breaker.call(
                self._fetch_roster, team_abbrev
            )
        except CircuitBreakerOpenError:
            logger.warning(f"Circuit breaker opened for {team_abbrev}")
            raise
```

## Implementation Steps

1. Create `src/nhl_scrabble/protection/circuit_breaker.py`
1. Create `src/nhl_scrabble/protection/request_queue.py`
1. Update `NHLApiClient` with connection pool limits
1. Integrate circuit breaker into API calls
1. Add request queue with depth limits
1. Implement hard timeouts
1. Add configuration options
1. Add tests for DoS scenarios
1. Update documentation

## Testing Strategy

**Unit Tests**:

```python
def test_circuit_breaker_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3)

    for _ in range(3):
        with pytest.raises(Exception):
            cb.call(failing_function)

    assert cb.state == CircuitState.OPEN

def test_queue_rejects_when_full():
    queue = RequestQueue(max_size=5)

    for i in range(5):
        queue.enqueue(f"request-{i}")

    with pytest.raises(QueueFullError):
        queue.enqueue("overflow")
```

**Load Tests**:

```bash
# Simulate high load
pytest tests/load/test_dos_protection.py
```

## Acceptance Criteria

- [ ] Connection pool limits implemented
- [ ] Circuit breaker pattern working
- [ ] Request queue with max depth
- [ ] Hard timeouts enforced
- [ ] Circuit breaker opens after threshold failures
- [ ] Circuit breaker recovers after timeout
- [ ] Queue rejects when full
- [ ] Configuration options added
- [ ] Tests pass
- [ ] Documentation updated

## Related Files

- `src/nhl_scrabble/api/nhl_client.py` - Add DoS protection
- `src/nhl_scrabble/protection/circuit_breaker.py` - New module
- `src/nhl_scrabble/protection/request_queue.py` - New module
- `src/nhl_scrabble/config.py` - Add DoS config options
- `tests/unit/test_circuit_breaker.py` - New tests
- `tests/load/test_dos_protection.py` - Load tests

## Dependencies

- No new dependencies required (uses requests, threading, queue, signal)
- Should be implemented after tasks/security/004 (rate limiting)

## Additional Notes

**Benefits**:

- Prevents resource exhaustion
- Graceful degradation under load
- Fast-fail for degraded services
- Protects both client and server

**Trade-offs**:

- Adds complexity to API client
- May reject legitimate requests under extreme load
- Circuit breaker may be too aggressive
- Hard timeouts platform-dependent (Unix signals)

**Configuration Recommendations**:

- `max_concurrent`: 10 (conservative)
- `circuit_breaker_threshold`: 5 failures
- `circuit_breaker_timeout`: 60 seconds
- `queue_max_size`: 100 requests
- `hard_timeout`: 30 seconds

## Implementation Notes

*To be filled during implementation*
