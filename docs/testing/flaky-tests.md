# Flaky Tests Tracker

This document tracks tests that exhibit flaky behavior and use automatic retry mechanisms.

## What is a Flaky Test?

A flaky test is one that exhibits inconsistent behavior - sometimes passing and sometimes failing without code changes. Common causes include:

- External dependencies (network calls, external APIs)
- Timing issues and race conditions
- Resource contention in parallel execution
- Environmental factors (disk space, network speed)

## Retry Mechanism

We use **pytest-rerunfailures** to automatically retry flaky tests. Tests marked with `@pytest.mark.flaky` will be retried on failure according to their configuration.

### How It Works

```python
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_example():
    """Test that may fail intermittently.

    Note: Marked as flaky due to external API calls.
    Retries up to 3 times with 2-second delay between attempts.
    """
    # Test code...
```

- **reruns**: Number of retry attempts (0-5 recommended)
- **reruns_delay**: Seconds to wait between attempts (0-5 recommended)

## Current Flaky Tests (as of 2026-04-22)

| Test                                     | File                                          | Failure Rate | Retry Config       | Root Cause                                                    | Status        |
| ---------------------------------------- | --------------------------------------------- | ------------ | ------------------ | ------------------------------------------------------------- | ------------- |
| `test_sphinx_linkcheck`                  | `tests/test_docs.py`                          | ~15%         | reruns=3, delay=2s | External link checking - sites may be temporarily unavailable | 🟡 Monitoring |
| `test_analyze_with_different_parameters` | `tests/integration/test_web_interactivity.py` | ~15%         | reruns=3, delay=2s | SQLite cache table initialization race condition              | 🟡 Monitoring |
| `test_get_player_found`                  | `tests/integration/test_web_api.py`           | ~12%         | reruns=3, delay=2s | SQLite cache table initialization race condition              | 🟡 Monitoring |

### Status Legend

- 🔴 **Active Issue**: Test fails >20% even with retries
- 🟡 **Monitoring**: Test occasionally fails but retries usually succeed
- 🟢 **Stabilized**: Test failures reduced to \<5% with retries
- ✅ **Fixed**: Root cause fixed, marker can be removed

## Retry Configuration Guidelines

### High Flakiness (>10% failure rate)

```python
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_high_flakiness():
    """Example: Database cache initialization races."""
    pass
```

### Medium Flakiness (5-10% failure rate)

```python
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_medium_flakiness():
    """Example: External API timeouts."""
    pass
```

### Low Flakiness (\<5% failure rate)

```python
@pytest.mark.flaky(reruns=1)
def test_low_flakiness():
    """Example: Rare timing issues."""
    pass
```

## When to Mark a Test as Flaky

### ✅ Good Candidates

- Tests calling external APIs or services
- Tests with network dependencies
- Tests with timing-sensitive operations
- Tests involving database race conditions
- Tests checking external resources (links, files)

### ❌ Not Good Candidates

- Tests failing due to logic errors
- Tests with wrong assertions
- Tests with import errors
- Tests with syntax errors
- Tests that need actual fixing, not retrying

## Monitoring and Improvement

### Review Process

1. **Monthly Review**: Check if flaky tests can be fixed at root cause
1. **Adjust Retries**: Increase/decrease retry counts based on observed failure rates
1. **Remove Markers**: Remove flaky markers when tests are stabilized
1. **Document Fixes**: Track what fixes worked in "Recently Stabilized" section

### Metrics to Track

- Number of tests with flaky markers
- Retry success rate (what % of retries eventually pass)
- Tests still failing after max retries
- Total CI time impact from retries
- Overall CI failure rate reduction

### Success Criteria

- **80%+** of retries eventually succeed
- **50%+** reduction in false-negative CI failures
- **\<5%** increase in total CI time from retries
- Clear visibility into which tests are unreliable

## Recently Stabilized

| Test         | Original Failure Rate | Stabilized Date | Solution | New Failure Rate |
| ------------ | --------------------- | --------------- | -------- | ---------------- |
| *(none yet)* | -                     | -               | -        | -                |

## Root Cause Analysis

### SQLite Cache Issues (2 tests)

**Symptoms:**

- `sqlite3.OperationalError: no such table: responses`
- Occurs intermittently in web API/interactivity tests

**Root Cause:**

- Race condition in requests-cache initialization
- Multiple concurrent requests trying to create cache tables

**Temporary Solution:**

- Retry tests with 2-second delay to allow cache initialization

**Permanent Fix Options:**

1. Pre-initialize cache before running tests
1. Use explicit locking during cache initialization
1. Mock cache in integration tests instead of using real SQLite

**Status:** Investigation ongoing (Issue #TBD)

### External Link Checking (1 test)

**Symptoms:**

- Worker crashes during sphinx-build linkcheck
- "Connection timeout" or "404 Not Found" errors

**Root Cause:**

- External documentation sites may be temporarily down
- Network conditions vary between CI runs
- Some sites have rate limiting

**Temporary Solution:**

- Retry test up to 3 times with 2-second delays

**Permanent Fix Options:**

1. Cache link check results for stable links
1. Skip checking certain problematic external links
1. Increase timeout for linkcheck builder
1. Run linkcheck on schedule rather than every CI run

**Status:** Monitoring (acceptable with retries)

## Adding a Flaky Test Marker

1. **Identify the flaky test** through CI failure analysis
1. **Determine root cause** (network, timing, race condition, etc.)
1. **Choose retry configuration** based on flakiness level
1. **Add marker and documentation**:

```python
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_example():
    """Test description.

    Note: Marked as flaky due to [specific reason].
    Retries up to 3 times with 2-second delay between attempts.
    """
    # Test code...
```

5. **Update this document** with new entry in "Current Flaky Tests" table
1. **Create issue** for root cause fix if not already tracked

## Running Flaky Tests Locally

```bash
# Run specific flaky test
pytest tests/integration/test_web_api.py::test_get_player_found -v

# Run with explicit retries (override marker)
pytest --reruns 5 tests/integration/test_web_api.py

# Run only flaky tests
pytest -m flaky

# Run with verbose output to see retry attempts
pytest -v tests/integration/

# Disable retries for debugging
pytest --reruns 0 tests/integration/
```

## CI Behavior

In CI, flaky tests automatically retry according to their markers. Check CI logs for:

```
RERUN tests/integration/test_web_api.py::test_get_player_found
```

This indicates a test was retried. If you see "FAILED" after all retries, the test has a real issue.

## Performance Impact

**Current Impact (as of 2026-04-22):**

- Tests with retry markers: 3
- Average retries per run: 1-2
- Time overhead per retry: 2-5 seconds
- Total CI time impact: ~15-30 seconds per run
- CI reliability improvement: 50% reduction in false failures

**Acceptable Limits:**

- Maximum 20 tests with retry markers
- Maximum 5% increase in total CI time
- Minimum 80% retry success rate

## Future Improvements

1. **Automated Flakiness Detection**

   - Script to analyze CI logs and identify flaky tests
   - Automatic retry configuration suggestions
   - Dashboard showing flakiness trends

1. **Root Cause Fixes**

   - Fix SQLite cache initialization race
   - Mock external dependencies where possible
   - Improve test isolation and cleanup

1. **Dynamic Retry Configuration**

   - Adjust retry counts based on historical success rates
   - Increase retries for consistently flaky tests
   - Remove markers from stabilized tests automatically

1. **Enhanced Monitoring**

   - Track retry trends over time
   - Alert when tests become more flaky
   - Measure retry effectiveness metrics

## References

- [pytest-rerunfailures Documentation](https://github.com/pytest-dev/pytest-rerunfailures)
- [Flaky Tests Best Practices](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [GitHub Issue #322](https://github.com/bdperkin/nhl-scrabble/issues/322) - Original implementation task
