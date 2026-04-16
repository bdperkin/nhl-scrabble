# Implement NHLApiNotFoundError Properly

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

1-2 hours

## Description

The `NHLApiNotFoundError` exception is defined in `src/nhl_scrabble/api/__init__.py` but is never raised anywhere in the codebase. Instead, the API client returns `None` for 404 responses, which prevents proper error handling and makes debugging difficult.

## Current State

**Exception Definition** (`src/nhl_scrabble/api/__init__.py`):

```python
class NHLApiNotFoundError(NHLApiError):
    """Raised when NHL API returns 404 Not Found."""
```

**Current Implementation** (`src/nhl_scrabble/api/nhl_client.py`):

```python
def _make_request(self, endpoint: str) -> dict[str, Any] | None:
    """Make request to NHL API with retry logic."""
    # ... retry logic ...
    if response.status_code == 404:
        logger.warning(f"NHL API endpoint not found: {url}")
        return None  # <-- Should raise NHLApiNotFoundError instead
    # ...
```

**Impact**:

- Vulture correctly identifies this as unused code
- Callers must check for `None` instead of catching specific exception
- Lost context about why request failed

## Proposed Solution

Raise `NHLApiNotFoundError` instead of returning `None`:

```python
def _make_request(self, endpoint: str) -> dict[str, Any]:
    """Make request to NHL API with retry logic.

    Raises:
        NHLApiNotFoundError: If endpoint returns 404
        NHLApiError: For other API errors
        requests.RequestException: For network errors
    """
    # ... retry logic ...
    if response.status_code == 404:
        logger.warning(f"NHL API endpoint not found: {url}")
        raise NHLApiNotFoundError(f"Endpoint not found: {endpoint}")
    # ...
    return response.json()  # Never returns None
```

Update callers to handle the exception:

```python
def get_standings(self) -> dict[str, Any]:
    """Fetch current NHL standings."""
    try:
        return self._make_request("standings/now")
    except NHLApiNotFoundError:
        logger.error("Standings endpoint not found - NHL API may have changed")
        raise

def get_team_roster(self, team_abbrev: str) -> dict[str, Any]:
    """Fetch current roster for a team."""
    try:
        return self._make_request(f"roster/{team_abbrev}/current")
    except NHLApiNotFoundError:
        logger.error(f"Roster not found for team {team_abbrev}")
        raise
```

## Testing Strategy

Add tests in `tests/unit/test_nhl_client.py`:

```python
import pytest
from unittest.mock import Mock, patch
from nhl_scrabble.api import NHLClient, NHLApiNotFoundError

def test_make_request_404_raises_not_found_error():
    """Test that 404 response raises NHLApiNotFoundError."""
    with NHLClient() as client:
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            with pytest.raises(NHLApiNotFoundError, match="Endpoint not found"):
                client._make_request("invalid/endpoint")

def test_get_standings_propagates_not_found_error():
    """Test that get_standings() propagates NHLApiNotFoundError."""
    with NHLClient() as client:
        with patch.object(client, '_make_request', side_effect=NHLApiNotFoundError("Not found")):
            with pytest.raises(NHLApiNotFoundError):
                client.get_standings()

def test_get_team_roster_propagates_not_found_error():
    """Test that get_team_roster() propagates NHLApiNotFoundError."""
    with NHLClient() as client:
        with patch.object(client, '_make_request', side_effect=NHLApiNotFoundError("Not found")):
            with pytest.raises(NHLApiNotFoundError):
                client.get_team_roster("TOR")
```

Add integration test to verify error handling in CLI:

```python
def test_cli_handles_not_found_error(monkeypatch):
    """Test that CLI handles NHLApiNotFoundError gracefully."""
    with patch('nhl_scrabble.api.NHLClient.get_standings',
               side_effect=NHLApiNotFoundError("Not found")):
        result = runner.invoke(cli, ["analyze"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
```

## Acceptance Criteria

- [ ] `NHLApiNotFoundError` is raised for 404 responses
- [ ] `_make_request()` return type is `dict[str, Any]` (not `| None`)
- [ ] All callers properly handle the exception
- [ ] Vulture no longer flags `NHLApiNotFoundError` as unused
- [ ] Unit tests verify exception is raised and propagated
- [ ] Integration tests verify CLI handles the error gracefully
- [ ] Type checking passes with strict mypy settings

## Related Files

- `src/nhl_scrabble/api/__init__.py`
- `src/nhl_scrabble/api/nhl_client.py`
- `tests/unit/test_nhl_client.py`
- `tests/integration/test_cli.py`

## Dependencies

None - standalone fix

## Additional Notes

This change makes the API more Pythonic ("ask forgiveness not permission" vs "look before you leap"). Exceptions provide better error context and stack traces than `None` returns.
