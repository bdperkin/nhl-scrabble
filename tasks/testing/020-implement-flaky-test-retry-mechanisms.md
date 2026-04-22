# Implement Flaky Test Retry Mechanisms

**GitHub Issue**: #322 - https://github.com/bdperkin/nhl-scrabble/issues/322

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

6-10 hours

## Description

Analyze CI/CD runs and test history to identify tests with high failure or flake rates, then implement automatic retry mechanisms using pytest plugins to improve test reliability and reduce false-negative CI failures. Flaky tests that occasionally fail due to timing issues, network conditions, or race conditions should automatically retry before being marked as failed.

## Current State

**Test Infrastructure**:

The project currently has:

- 1,220+ tests across unit, integration, and benchmarks
- pytest-xdist for parallel execution
- No automatic retry mechanisms for flaky tests
- Occasional test failures in CI that pass on retry

**Known Flaky Tests**:

From recent CI/CD analysis:

- `tests/integration/test_web_interactivity.py::test_analyze_with_different_parameters` - SQLite cache table issues
- `tests/integration/test_web_api.py::test_get_player_found` - SQLite cache table issues
- Tests involving external API calls may have network-related flakiness
- Tests with timing dependencies may fail under load

**Current Test Configuration**:

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--strict-markers",
    "--strict-config",
    "--cov=src/nhl_scrabble",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]
```

**Limitations**:

1. **No retry mechanism**: Tests fail immediately, no automatic retries
1. **No flakiness tracking**: No visibility into which tests fail intermittently
1. **CI noise**: Flaky tests cause false-negative CI failures requiring manual re-runs
1. **Developer friction**: Developers must manually re-run CI when flaky tests fail

## Proposed Solution

### Phase 1: Analyze Test History (2-3 hours)

**1. Analyze GitHub Actions CI/CD History**

```bash
# Get recent workflow runs
gh run list --limit 100 --json conclusion,createdAt,name,status > ci_runs.json

# Analyze test failures
gh run list --status failure --limit 50 --json conclusion,databaseId

# For each failed run, get test details
for run_id in $(gh run list --status failure --limit 20 --json databaseId --jq '.[].databaseId'); do
    gh run view $run_id --log-failed | grep -E "FAILED|ERROR" >> failed_tests.log
done

# Aggregate failures by test name
cat failed_tests.log | grep "FAILED" | sed 's/.*FAILED //' | sed 's/ - .*//' | sort | uniq -c | sort -rn > flaky_tests_ranked.txt
```

**2. Analyze Codecov Test Coverage Data**

Visit https://app.codecov.io/gh/bdperkin/nhl-scrabble/tests and:

- Review test execution history
- Identify tests with inconsistent coverage (may indicate flakiness)
- Check for tests that sometimes skip or fail

**3. Identify Top Flaky Tests**

Create a report showing:

- Test name
- Failure count over last 100 runs
- Failure rate (%)
- Most common error messages
- Affected CI workflows

Example output:

```
Top 10 Flaky Tests:
1. test_web_interactivity.py::test_analyze_with_different_parameters (15 failures, 15% rate)
   - sqlite3.OperationalError: no such table: responses
2. test_web_api.py::test_get_player_found (12 failures, 12% rate)
   - sqlite3.OperationalError: no such table: responses
3. test_api_integration.py::test_fetch_team_roster_timeout (5 failures, 5% rate)
   - requests.exceptions.Timeout
```

### Phase 2: Select and Implement Retry Plugin (1-2 hours)

**Recommended Plugin: pytest-rerunfailures**

Rationale:

- Most popular pytest retry plugin (widely adopted)
- Simple marker-based API (`@pytest.mark.flaky(reruns=3)`)
- Supports both global and selective reruns
- Good pytest-xdist compatibility
- Active maintenance and well-documented

**Alternative Plugins Considered**:

| Plugin                      | Pros                                  | Cons                       | Best For                       |
| --------------------------- | ------------------------------------- | -------------------------- | ------------------------------ |
| **pytest-rerunfailures** ✅ | Most popular, simple API, good docs   | Basic features only        | General use, selective retries |
| **pytest-retry**            | Advanced features (timing, filtering) | More complex configuration | Advanced retry logic           |
| **flaky**                   | Minimum pass threshold support        | Less pytest-native         | Probabilistic tests            |

**Implementation**:

1. **Add Dependency**

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    # ... existing dependencies ...
    "pytest-rerunfailures>=14.0",  # Automatic test retries for flaky tests
]
```

2. **Update Lock File**

```bash
uv lock
pip install -e ".[test]"
```

3. **Configure pytest**

```toml
# pyproject.toml
[tool.pytest.ini_options]
# ... existing options ...
markers = [
    "flaky: mark test as flaky (will be retried on failure)",
]
```

### Phase 3: Apply Selective Markers (2-3 hours)

**Apply markers to identified flaky tests**:

```python
# tests/integration/test_web_interactivity.py
import pytest

@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_analyze_with_different_parameters(client, top_players, top_team_players):
    """Test analysis with different parameter combinations.

    Note: Marked as flaky due to intermittent SQLite cache table issues.
    Retries up to 3 times with 1-second delay between attempts.
    """
    response = client.get(
        "/api/analyze",
        params={"top_players": top_players, "top_team_players": top_team_players},
    )
    assert response.status_code == 200
```

**Categorize Retries by Flakiness Level**:

- **High flakiness** (>10% failure rate): `reruns=3, reruns_delay=2`
- **Medium flakiness** (5-10% failure rate): `reruns=2, reruns_delay=1`
- **Low flakiness** (\<5% failure rate): `reruns=1, reruns_delay=0`

**Example Markers**:

```python
# High flakiness - SQLite cache issues
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_with_sqlite_cache():
    ...

# Medium flakiness - Network timeouts
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_api_call_with_timeout():
    ...

# Low flakiness - Rare race conditions
@pytest.mark.flaky(reruns=1)
def test_with_potential_race_condition():
    ...
```

### Phase 4: Update CI Configuration (1 hour)

**GitHub Actions Workflow**:

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    # Flaky tests will automatically retry via @pytest.mark.flaky markers
    # No global --reruns flag needed (selective is better)
    pytest --verbose --cov --cov-report=xml
```

**Tox Configuration**:

```ini
# tox.ini
[testenv]
commands =
    # pytest-rerunfailures installed via test dependencies
    pytest {posargs}
    # Flaky markers work automatically, no extra config needed
```

**Document Retry Behavior**:

Add to test output configuration to show retry information:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    # ... existing options ...
    "-v",  # Verbose mode shows retry attempts
]
```

### Phase 5: Monitor and Refine (2 hours)

**1. Add Reporting**

Track retry statistics to monitor effectiveness:

```bash
# After CI run, analyze pytest output
grep -E "RERUN|FLAKY" pytest_output.log | wc -l  # Count retries

# Identify tests that still fail after retries
grep "FAILED.*flaky" pytest_output.log  # Tests that exhausted retries
```

**2. Create Flaky Test Dashboard**

Add to documentation:

```markdown
# Flaky Tests Tracker

## Current Flaky Tests (as of 2026-04-22)

| Test | Failure Rate | Retry Config | Status | Notes |
|------|-------------|--------------|---------|--------|
| test_web_interactivity.py::test_analyze_with_different_parameters | 15% | reruns=3, delay=2s | 🟡 Monitoring | SQLite cache issues |
| test_web_api.py::test_get_player_found | 12% | reruns=3, delay=2s | 🟡 Monitoring | SQLite cache issues |

## Recently Stabilized

| Test | Original Rate | Fix Date | Solution |
|------|--------------|----------|----------|
| (none yet) | - | - | - |

## Retry Success Rate

- Tests with reruns: 15
- Successful retries: 12 (80%)
- Still failing after retries: 3 (20%)
```

**3. Continuous Improvement**

```python
# tests/conftest.py
def pytest_configure(config):
    """Log retry configuration for CI analysis."""
    config.addinivalue_line(
        "markers",
        "flaky: mark test as flaky (will be retried on failure)",
    )

def pytest_runtest_makereport(item, call):
    """Track retry attempts for reporting."""
    if hasattr(item, "execution_count"):
        # Log retry statistics
        pass
```

## Implementation Steps

1. **Analyze CI/CD History** (2-3 hours)

   - Export GitHub Actions workflow run data
   - Parse failed test logs
   - Aggregate failures by test name
   - Calculate failure rates
   - Identify top 10-20 flaky tests

1. **Research and Select Plugin** (30 minutes)

   - Compare pytest-rerunfailures, pytest-retry, flaky
   - Review compatibility with existing setup (pytest-xdist, tox)
   - Choose pytest-rerunfailures (recommended)

1. **Add pytest-rerunfailures Dependency** (15 minutes)

   - Update pyproject.toml with pytest-rerunfailures>=14.0
   - Run uv lock
   - Install in development environment
   - Verify plugin loads: pytest --markers | grep flaky

1. **Apply Selective Markers** (2-3 hours)

   - Start with top 5 flakiest tests
   - Add @pytest.mark.flaky(reruns=N, reruns_delay=M) markers
   - Document retry rationale in docstrings
   - Categorize by flakiness level (high/medium/low)
   - Test locally: pytest -v tests/integration/test_web_interactivity.py

1. **Update Documentation** (30 minutes)

   - Add flaky test tracker to docs/
   - Document retry strategy in CONTRIBUTING.md
   - Update test README with retry guidelines
   - Add CI configuration notes

1. **Test in CI** (1 hour)

   - Create PR with changes
   - Monitor CI runs for retry behavior
   - Verify retries work: check "RERUN" in CI logs
   - Confirm flaky tests pass after retries

1. **Monitor and Adjust** (ongoing)

   - Track retry success rate
   - Adjust retry counts based on effectiveness
   - Identify tests that still fail after max retries
   - Fix root causes when possible

## Testing Strategy

### Unit Tests

Test retry behavior in isolation:

```python
# tests/unit/test_retry_markers.py
import pytest

def test_flaky_marker_exists():
    """Verify flaky marker is registered."""
    assert "flaky" in pytest.mark._markers

@pytest.mark.flaky(reruns=2)
def test_retry_eventually_succeeds():
    """Test that fails first time but succeeds on retry."""
    import random
    if random.random() < 0.5:  # Fail ~50% of the time
        pytest.fail("Simulated flake")
    assert True
```

### Integration Tests

Test retry behavior with real flaky tests:

```bash
# Run specific flaky test multiple times to verify retry works
for i in {1..10}; do
    echo "Run $i:"
    pytest tests/integration/test_web_interactivity.py::test_analyze_with_different_parameters -v
done

# Check success rate improved with retries
```

### CI/CD Testing

1. Create PR with retry markers
1. Monitor GitHub Actions workflow runs
1. Verify in logs:
   - "RERUN" messages for retried tests
   - Reduced failure rate overall
   - Clear retry attempt counts
1. Check final test results show retries worked

### Manual Testing

```bash
# Test retry behavior locally
pytest -v --reruns 2 tests/integration/

# Test specific flaky test
pytest -v tests/integration/test_web_interactivity.py::test_analyze_with_different_parameters

# Verify marker works
pytest --markers | grep flaky
```

## Acceptance Criteria

- [ ] CI/CD history analyzed, flaky tests identified (top 10-20 tests documented)
- [ ] Codecov test history reviewed for additional flaky test indicators
- [ ] pytest-rerunfailures plugin added to pyproject.toml test dependencies
- [ ] uv.lock updated with new dependency
- [ ] Flaky test markers applied to top 10 flakiest tests
- [ ] Retry counts categorized by flakiness level (high/medium/low)
- [ ] Docstrings updated with retry rationale for each marked test
- [ ] pytest configuration includes flaky marker registration
- [ ] CI workflow runs without errors with new retry plugin
- [ ] Retry behavior verified in CI logs (RERUN messages visible)
- [ ] Documentation updated:
  - [ ] Flaky test tracker created
  - [ ] CONTRIBUTING.md updated with retry guidelines
  - [ ] Test README updated
- [ ] All tests pass with retry mechanisms in place
- [ ] Retry success rate monitored (target: >80% of retries succeed)
- [ ] False-negative CI failures reduced (target: 50% reduction)

## Related Files

**Modified Files**:

- `pyproject.toml` - Add pytest-rerunfailures dependency, update pytest markers
- `uv.lock` - Update with new dependency
- `tests/integration/test_web_interactivity.py` - Apply @pytest.mark.flaky markers
- `tests/integration/test_web_api.py` - Apply @pytest.mark.flaky markers
- `tests/integration/test_api_integration.py` - Apply @pytest.mark.flaky markers (if flaky)
- `tests/conftest.py` - Add retry tracking hooks (optional)
- `CONTRIBUTING.md` - Document retry strategy
- `docs/testing/flaky-tests.md` - Create flaky test tracker (new file)

**Files to Analyze**:

- GitHub Actions workflow logs (via gh CLI)
- Codecov test history (https://app.codecov.io/gh/bdperkin/nhl-scrabble/tests)
- pytest output from recent CI runs

**New Files**:

- `docs/testing/flaky-tests.md` - Flaky test tracker and documentation
- `scripts/analyze_flaky_tests.py` - Script to analyze CI history (optional)

## Dependencies

**Python Dependencies**:

- `pytest-rerunfailures>=14.0` - Main retry plugin
- `pytest>=8.0.0` - Already installed
- `pytest-xdist>=3.5.0` - Already installed (compatibility verified)

**External Dependencies**:

- GitHub CLI (`gh`) - For analyzing CI/CD history
- Access to GitHub Actions logs
- Access to Codecov dashboard

**Task Dependencies**:

- No blocking dependencies (can implement independently)

**Related Tasks**:

- None directly blocking, but this improves reliability of all other testing tasks

## Additional Notes

### Plugin Comparison Details

**pytest-rerunfailures** (Recommended):

- **Pros**: Simplest to use, most adopted, good pytest integration
- **Cons**: Basic retry logic only, no advanced timing features
- **Best for**: Selective marker-based retries (our use case)
- **Installation**: `pip install pytest-rerunfailures`
- **Usage**: `@pytest.mark.flaky(reruns=3, reruns_delay=1)`

**pytest-retry**:

- **Pros**: Cumulative timing, global exception filtering, advanced features
- **Cons**: More complex configuration, less widely adopted
- **Best for**: Complex retry scenarios with timing constraints
- **Installation**: `pip install pytest-retry`
- **Usage**: `@pytest.mark.flaky(retries=3, delay=1)`

**flaky**:

- **Pros**: Minimum pass threshold (`min_passes`), flexible
- **Cons**: Less pytest-native, different API
- **Best for**: Probabilistic tests needing multiple passes
- **Installation**: `pip install flaky`
- **Usage**: `@flaky(max_runs=3, min_passes=2)`

### Flakiness Root Causes

Understanding why tests are flaky helps fix them permanently:

1. **SQLite Cache Issues** (most common in our codebase):

   - Symptom: `sqlite3.OperationalError: no such table`
   - Cause: Race condition in requests-cache initialization
   - Solution: Retry + investigate cache initialization timing

1. **Network Timeouts**:

   - Symptom: `requests.exceptions.Timeout`
   - Cause: External API slow or temporarily unavailable
   - Solution: Retry + increase timeout + mock in tests

1. **Race Conditions**:

   - Symptom: Intermittent assertion failures
   - Cause: Async operations not properly synchronized
   - Solution: Retry + add proper async/await

1. **Resource Contention**:

   - Symptom: Tests fail under parallel execution
   - Cause: Shared resources (files, ports, databases)
   - Solution: Retry + isolate resources

### Best Practices

**When to Use Retries**:

- ✅ External API calls with network dependencies
- ✅ Database operations with potential race conditions
- ✅ File system operations that may have timing issues
- ✅ Async operations with timing sensitivity

**When NOT to Use Retries**:

- ❌ Logic errors (fix the test instead)
- ❌ Assertion failures due to wrong expected values (fix expectations)
- ❌ Import errors (fix dependencies)
- ❌ Syntax errors (fix code)

**Retry Configuration Guidelines**:

```python
# High-flakiness tests (>10% failure rate)
# Example: Database cache initialization races
@pytest.mark.flaky(reruns=3, reruns_delay=2)

# Medium-flakiness tests (5-10% failure rate)
# Example: External API timeouts
@pytest.mark.flaky(reruns=2, reruns_delay=1)

# Low-flakiness tests (<5% failure rate)
# Example: Rare timing issues
@pytest.mark.flaky(reruns=1)
```

### Performance Considerations

**Retry Impact on CI Time**:

- Each retry adds test execution time
- Minimize retries to most flaky tests only
- Use selective markers, not global `--reruns` flag
- Example: 15 flaky tests × 2 retries × 10s = ~5 minutes max overhead

**Parallel Execution Compatibility**:

- pytest-rerunfailures works with pytest-xdist
- Retries happen within same worker
- No impact on parallel speedup

### Monitoring Strategy

**Track Metrics**:

1. Number of tests with retry markers
1. Retry success rate (retries that eventually pass)
1. Tests still failing after max retries
1. Total CI time impact from retries
1. Overall CI failure rate reduction

**Success Criteria**:

- 80%+ of retries eventually succeed
- 50%+ reduction in false-negative CI failures
- \<5% increase in total CI time
- Clear visibility into which tests are flaky

### Future Enhancements

After initial implementation:

1. **Automated Flakiness Detection**:

   - Script to analyze CI logs automatically
   - Flag tests with high failure rates
   - Suggest retry configuration

1. **Root Cause Analysis**:

   - Fix SQLite cache initialization race
   - Mock external API calls in integration tests
   - Improve async test synchronization

1. **Retry Analytics Dashboard**:

   - Track retry trends over time
   - Identify tests becoming more/less flaky
   - Measure retry effectiveness

1. **Dynamic Retry Configuration**:

   - Adjust retry counts based on historical success rate
   - Increase retries for consistently flaky tests
   - Remove markers from stabilized tests

### Security Considerations

**No Security Implications**:

- pytest-rerunfailures is a testing tool only
- No runtime impact on production code
- No new dependencies at runtime
- Test-time only dependency

### Breaking Changes

**None** - This is purely additive:

- Existing tests work unchanged
- Only marked tests get retry behavior
- No changes to test assertions or logic
- Backwards compatible with existing pytest configuration

### Migration Notes

**For Developers**:

```bash
# After merging, update dependencies
pip install -e ".[test]"  # or uv pip install -e ".[test]"

# Run tests normally - retries happen automatically
pytest

# Run specific flaky test to see retry behavior
pytest -v tests/integration/test_web_interactivity.py::test_analyze_with_different_parameters
```

**For CI/CD**:

- No changes needed to GitHub Actions workflows
- Retries happen automatically via markers
- Check logs for "RERUN" messages to see retries in action

## Implementation Notes

*To be filled during implementation:*

- Actual flaky tests identified from CI analysis
- Final retry counts chosen for each test
- Retry success rates observed
- CI failure rate reduction achieved
- Challenges encountered
- Deviations from plan
- Actual effort vs estimated
