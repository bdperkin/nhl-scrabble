# Add Session Cleanup Safety Net

**GitHub Issue**: #44 - https://github.com/bdperkin/nhl-scrabble/issues/44

## Priority

**MEDIUM** - Must Do (Next Sprint)

## Estimated Effort

1-2 hours

## Description

The `NHLClient` relies on proper use of the context manager (`with NHLClient() as client`) to ensure the requests session is closed. If the context manager is not used correctly, the session may leak. Add a safety net to ensure cleanup happens even if the context manager is bypassed.

## Current State

```python
class NHLClient:
    """Client for interacting with NHL API."""

    def __init__(self, timeout: int = 10, retries: int = 3, rate_limit_delay: float = 0.3) -> None:
        """Initialize NHL API client."""
        self.session = requests.Session()
        # ...

    def __enter__(self) -> "NHLClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and close session."""
        self.close()

    def close(self) -> None:
        """Close the requests session."""
        if self.session:
            self.session.close()
```

**Risk**: If someone uses `client = NHLClient()` without `with`, the session never closes.

## Proposed Solution

Add `__del__()` method and use `atexit` for guaranteed cleanup:

```python
import atexit
import weakref

class NHLClient:
    """Client for interacting with NHL API."""

    _instances: set[weakref.ref] = set()  # Track all instances

    def __init__(self, timeout: int = 10, retries: int = 3, rate_limit_delay: float = 0.3) -> None:
        """Initialize NHL API client."""
        self.session = requests.Session()
        self._closed = False
        # ...

        # Register cleanup
        self._instances.add(weakref.ref(self, self._cleanup_callback))
        atexit.register(self._cleanup_all)

    def __enter__(self) -> "NHLClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and close session."""
        self.close()

    def __del__(self) -> None:
        """Destructor - close session if not already closed."""
        if not self._closed:
            logger.warning("NHLClient session was not explicitly closed - cleaning up")
            self.close()

    def close(self) -> None:
        """Close the requests session."""
        if not self._closed and self.session:
            self.session.close()
            self._closed = True

    @classmethod
    def _cleanup_callback(cls, ref: weakref.ref) -> None:
        """Callback when instance is garbage collected."""
        cls._instances.discard(ref)

    @classmethod
    def _cleanup_all(cls) -> None:
        """Cleanup all instances at program exit."""
        for ref in list(cls._instances):
            instance = ref()
            if instance and not instance._closed:
                logger.warning("Cleaning up unclosed NHLClient at program exit")
                instance.close()
```

## Testing Strategy

Add tests in `tests/unit/test_nhl_client.py`:

```python
import gc
import pytest
from nhl_scrabble.api import NHLClient

def test_context_manager_closes_session():
    """Test that context manager properly closes session."""
    with NHLClient() as client:
        assert not client._closed
        session = client.session

    assert client._closed
    # Verify session is actually closed
    with pytest.raises(Exception):
        session.get("https://httpbin.org/get")

def test_destructor_closes_session(caplog):
    """Test that __del__ closes session if context manager not used."""
    client = NHLClient()
    assert not client._closed

    # Delete reference and force garbage collection
    del client
    gc.collect()

    # Should see warning in logs
    assert "not explicitly closed" in caplog.text

def test_explicit_close_works():
    """Test that calling close() directly works."""
    client = NHLClient()
    assert not client._closed

    client.close()
    assert client._closed

    # Calling close() again should be safe
    client.close()
    assert client._closed

def test_atexit_cleanup(monkeypatch):
    """Test that atexit handler cleans up unclosed instances."""
    # This is harder to test - may need subprocess
    pass  # TODO: Implement subprocess test
```

## Acceptance Criteria

- [ ] `__del__()` method closes session if not already closed
- [ ] `atexit` handler cleans up all unclosed instances
- [ ] `_closed` flag prevents double-close
- [ ] Warning logged when session not explicitly closed
- [ ] Context manager usage remains the preferred/documented method
- [ ] All tests pass including edge cases
- [ ] No memory leaks (verified with manual testing)

## Related Files

- `src/nhl_scrabble/api/nhl_client.py`
- `tests/unit/test_nhl_client.py`
- `docs/DEVELOPMENT.md` (add warning about context manager usage)

## Dependencies

- Python `atexit` module (stdlib)
- Python `weakref` module (stdlib)

## Additional Notes

While this adds safety, the documentation should still emphasize using the context manager. The safety net is for error conditions and improper usage, not normal operation.

**Best Practice** (document in README):

```python
# ✅ Preferred: Context manager
with NHLClient() as client:
    standings = client.get_standings()

# ⚠️ Also works but requires explicit close
client = NHLClient()
try:
    standings = client.get_standings()
finally:
    client.close()
```
