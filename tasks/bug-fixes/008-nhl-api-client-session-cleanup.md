# Fix NHLApiClient Session Cleanup Warning

**GitHub Issue**: #362 - https://github.com/bdperkin/nhl-scrabble/issues/362

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

When running `nhl-scrabble analyze`, a warning is logged:

```
nhl_scrabble.api.nhl_client - WARNING - NHLApiClient session was not explicitly closed - cleaning up in destructor
```

This warning indicates that the `NHLApiClient` context manager is being created but not properly closed. While the `__del__` destructor provides a safety net for cleanup, relying on it is not best practice and can lead to resource leaks or delayed cleanup in some scenarios.

## Current State

In `src/nhl_scrabble/cli.py`, the `run_analysis()` function creates an `NHLApiClient` instance but does not explicitly close it:

```python
def run_analysis(...) -> str | None:
    """Run NHL Scrabble analysis with given configuration."""
    # Create configuration from environment
    config = Config.from_env()

    # Override config with CLI arguments
    if verbose:
        config.verbose = True
    # ... other overrides ...

    # Create dependencies
    container = DependencyContainer(config)
    api_client = container.create_api_client()  # Line 264 - created but never closed

    # ... uses api_client for fetching data ...

    # No api_client.close() call
```

The `NHLApiClient` class is designed as a context manager with `__enter__` and `__exit__` methods, but the CLI code doesn't use it as one. Instead, it relies on the `__del__` destructor to clean up, which triggers the warning.

**Relevant code in `src/nhl_scrabble/api/nhl_client.py`:**

```python
class NHLApiClient:
    """NHL API client with session management."""

    def __enter__(self) -> "NHLApiClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - close session."""
        self.close()

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None:
            self._session.close()
            logger.debug("NHLApiClient session closed")
            self._session = None

    def __del__(self) -> None:
        """Destructor to ensure session cleanup."""
        if self._session is not None:
            logger.warning(
                "NHLApiClient session was not explicitly closed - cleaning up in destructor"
            )
            self.close()
```

## Proposed Solution

Modify `run_analysis()` in `src/nhl_scrabble/cli.py` to use `NHLApiClient` as a context manager. This ensures the session is explicitly closed when done, preventing the warning and following best practices for resource management.

**Updated code:**

```python
def run_analysis(...) -> str | None:
    """Run NHL Scrabble analysis with given configuration."""
    # Create configuration from environment
    config = Config.from_env()

    # Override config with CLI arguments
    if verbose:
        config.verbose = True
    # ... other overrides ...

    # Create dependencies
    container = DependencyContainer(config)

    # Use api_client as context manager for automatic cleanup
    with container.create_api_client() as api_client:
        scorer = container.create_scorer()
        processor = container.create_team_processor(api_client=api_client, scorer=scorer)

        # Process all teams
        logger.info("Processing NHL teams...")
        teams, all_players, failed_teams = processor.process_all_teams()

        # ... rest of analysis logic ...

        return output
    # api_client.close() called automatically on context exit
```

**Benefits:**

- **Explicit cleanup**: Session closed immediately when done, not delayed until garbage collection
- **No warnings**: Eliminates the destructor warning message
- **Best practice**: Follows Python idiom for resource management (context managers)
- **Deterministic**: Cleanup happens at predictable time, not when GC runs
- **Exception safety**: Session closed even if exception occurs during processing

## Implementation Steps

1. **Modify `run_analysis()` function** in `src/nhl_scrabble/cli.py`:
   - Wrap `api_client` creation in `with` statement
   - Indent code that uses `api_client` to be inside the context
   - Ensure all code paths exit the context properly

2. **Test the change**:
   - Run `nhl-scrabble analyze` and verify no warning appears
   - Check that API calls still work correctly
   - Verify logs show "NHLApiClient session closed" debug message

3. **Add regression test** in `tests/unit/test_cli.py`:
   - Test that `run_analysis()` doesn't leak sessions
   - Mock `NHLApiClient` and verify `close()` is called
   - Verify no destructor warnings in test output

## Testing Strategy

**Manual Testing:**

```bash
# Run analyzer and check for warnings
nhl-scrabble analyze --verbose

# Verify in logs:
# ✅ "NHLApiClient session closed" appears
# ❌ "NHLApiClient session was not explicitly closed" does NOT appear
```

**Unit Testing:**

```python
# tests/unit/test_cli.py
from unittest.mock import Mock, patch
from nhl_scrabble.cli import run_analysis

def test_run_analysis_closes_api_client():
    """Test that run_analysis properly closes API client."""
    with patch("nhl_scrabble.cli.DependencyContainer") as mock_container:
        # Create mock api_client with context manager support
        mock_api_client = Mock()
        mock_api_client.__enter__ = Mock(return_value=mock_api_client)
        mock_api_client.__exit__ = Mock(return_value=None)

        mock_container.return_value.create_api_client.return_value = mock_api_client

        # Run analysis
        run_analysis(...)

        # Verify context manager was used
        mock_api_client.__enter__.assert_called_once()
        mock_api_client.__exit__.assert_called_once()
```

**Integration Testing:**

Run full test suite to ensure no regressions:

```bash
pytest tests/integration/test_full_workflow.py -v
```

## Acceptance Criteria

- [x] `run_analysis()` uses `api_client` as context manager with `with` statement
- [x] Running `nhl-scrabble analyze` produces no session cleanup warnings
- [x] API calls function correctly (no behavior change)
- [x] Debug logs show "NHLApiClient session closed" message
- [x] Unit test verifies `close()` is called on api_client
- [x] All existing tests pass
- [x] Type checking passes (mypy)
- [x] Linting passes (ruff)
- [x] Documentation updated (if applicable)

## Related Files

- `src/nhl_scrabble/cli.py` - Primary change: wrap api_client in context manager
- `src/nhl_scrabble/api/nhl_client.py` - Reference: context manager implementation
- `src/nhl_scrabble/di.py` - Reference: DependencyContainer.create_api_client()
- `tests/unit/test_cli.py` - Add regression test for session cleanup

## Dependencies

None - this is a standalone bug fix.

## Additional Notes

**Why this matters:**

- **Resource Management**: HTTP sessions hold system resources (sockets, connections)
- **Best Practices**: Python context managers are the standard way to manage resources
- **Clean Logs**: Warnings in production logs reduce signal-to-noise ratio
- **Deterministic Cleanup**: Relying on `__del__` is unpredictable (GC timing varies)

**Edge Cases:**

- **Exception during processing**: Context manager ensures cleanup even on exception
- **Early return**: Any early returns must be inside the `with` block to ensure cleanup
- **Multiple exit points**: All paths through function must exit the context properly

**Performance Implications:**

- Negligible - context manager overhead is minimal
- Cleanup happens at same time (function exit vs GC), just more explicit
- No change to API call behavior or timing

## Implementation Notes

*To be filled during implementation:*

- Actual approach taken
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
