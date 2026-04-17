# Add pytest-xdist for Parallel Test Execution

**GitHub Issue**: #120 - https://github.com/bdperkin/nhl-scrabble/issues/120

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

30-60 minutes

## Description

Add pytest-xdist plugin to run tests in parallel across multiple CPU cores, significantly speeding up test suite execution and CI/CD pipelines.

Currently, tests run sequentially taking ~30s+ for the full suite. With pytest-xdist running tests in parallel, we can achieve 3-4x speedup, reducing execution time to ~8-10s. This is particularly valuable in CI where faster feedback improves developer productivity and GitHub Actions time = money.

**Impact**: 3-4x faster test execution, faster CI feedback, better CPU utilization, improved developer experience

**ROI**: Very High - minimal setup effort, immediate and ongoing time savings

## Current State

Tests run sequentially with no parallelization:

**pyproject.toml (lines 450-467)**:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=nhl_scrabble",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]
# No parallelization configured
```

**Current performance**:

```bash
$ pytest
============================= test session starts ==============================
...
============================== 36 passed in 30.15s ==============================
```

**Missing**:

- No pytest-xdist in dependencies
- No parallel execution configured
- Tests run on single core only
- Underutilized CPU resources (typically 1 of 4-8 cores used)

**GitHub Actions runners**:

- Standard runners: 2 cores
- Large runners: 4 cores
- Running tests on 1 core wastes 50-75% of available CPU

## Proposed Solution

Add pytest-xdist with auto-detection of CPU cores for optimal parallelization:

**Step 1: Add pytest-xdist to dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-timeout>=2.2.0",
    "pytest-xdist>=3.5.0",  # Add parallel execution
    "beautifulsoup4>=4.12.0",
]
```

**Step 2: Configure parallel execution in pytest**:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Enable parallel execution by default
addopts = [
    "--strict-markers",
    "--strict-config",
    "-n", "auto",  # Auto-detect CPU cores and parallelize
    "--cov=nhl_scrabble",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]

markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
    "no_parallel: Tests that must run sequentially (e.g., @pytest.mark.no_parallel)",
]
```

**Step 3: Update tox environments** (already configured properly):

```ini
# tox.ini - no changes needed, inherits from pyproject.toml
[testenv]
description = Run unit and integration tests with pytest
extras =
    test  # pytest-xdist now included
commands_pre =
    pytest --version
commands =
    pytest {posargs:tests/}  # Parallel execution automatic
```

**Step 4: Update CI workflow** (optimize for 2-core runners):

```yaml
# .github/workflows/ci.yml
- name: Run tests with coverage
  run: pytest --cov --cov-report=xml --cov-report=term -n 2
  # Explicitly use 2 workers for GitHub Actions 2-core runners
```

**Step 5: Add marker for sequential tests** (if needed):

```python
# For tests that must run sequentially (rare)
import pytest

@pytest.mark.no_parallel
def test_that_must_run_alone():
    # This test modifies global state or requires exclusive access
    pass
```

## Implementation Steps

1. **Add pytest-xdist to dependencies**:

   - Update `pyproject.toml` `[project.optional-dependencies.test]`
   - Add `pytest-xdist>=3.5.0`

1. **Configure parallel execution**:

   - Add `-n auto` to `addopts` in `[tool.pytest.ini_options]`
   - Add `no_parallel` marker documentation

1. **Update lock file**:

   - Run `uv lock` to update dependencies

1. **Test locally**:

   - Run `pytest -n auto` to verify parallel execution works
   - Verify coverage still works correctly
   - Check for any test isolation issues

1. **Optimize CI configuration**:

   - Update CI workflow to use `-n 2` explicitly
   - Test in CI to verify speedup

1. **Identify and mark sequential tests** (if needed):

   - Review tests for shared state
   - Add `@pytest.mark.no_parallel` where necessary
   - Re-run to verify no flaky tests

1. **Document the change**:

   - Update CONTRIBUTING.md with parallel testing info
   - Document how to disable parallelization if needed
   - Document the `no_parallel` marker

## Testing Strategy

**Performance Benchmark**:

```bash
# Before pytest-xdist
$ time pytest
============================== 36 passed in 30.15s ==============================
real    0m32.456s

# After pytest-xdist (4 cores)
$ time pytest -n auto
============================== 36 passed in 8.23s ===============================
real    0m10.127s

# Speedup: 30.15s / 8.23s = 3.66x faster
```

**Verify Parallel Execution**:

```bash
# Check that tests run in parallel
pytest -n auto -v

# Output should show:
# [gw0] [25%] PASSED tests/unit/test_1.py::test_a
# [gw1] [50%] PASSED tests/unit/test_2.py::test_b
# [gw2] [75%] PASSED tests/unit/test_3.py::test_c
# [gw3] [100%] PASSED tests/unit/test_4.py::test_d
# Workers: gw0, gw1, gw2, gw3 = 4 parallel workers
```

**Verify Coverage Still Works**:

```bash
# Coverage with parallel execution
pytest -n auto --cov=nhl_scrabble --cov-report=term

# Should show same coverage as sequential execution
# Coverage: 49.93% (should be identical)
```

**Test Different Worker Counts**:

```bash
# Auto-detect (recommended)
pytest -n auto  # Uses all available cores

# Explicit worker count
pytest -n 2     # Use 2 workers (good for CI)
pytest -n 4     # Use 4 workers (good for local dev)

# Disable parallel (fallback)
pytest -n 0     # Sequential execution
pytest          # Also sequential if -n not in addopts
```

**Check for Test Isolation Issues**:

```bash
# Run multiple times to catch flaky tests
for i in {1..10}; do
  pytest -n auto --lf || break  # Stop on first failure
done

# All runs should pass consistently
```

**Integration Testing**:

```bash
# Run through tox
tox -e py310

# Expected: Same results as local pytest, but faster
```

## Acceptance Criteria

- [ ] pytest-xdist added to `[project.optional-dependencies.test]`
- [ ] `-n auto` added to pytest addopts for default parallelization
- [ ] `no_parallel` marker documented in pytest markers
- [ ] Lock file updated with pytest-xdist
- [ ] Tests run in parallel locally (verified with -v output)
- [ ] Coverage collection works with parallel execution
- [ ] All existing tests pass with parallelization
- [ ] 3-4x speedup measured locally
- [ ] CI workflow updated to use `-n 2` explicitly
- [ ] CI shows speedup compared to sequential execution
- [ ] No flaky tests introduced by parallelization
- [ ] Documentation updated (CONTRIBUTING.md)
- [ ] Tox environments work with pytest-xdist

## Related Files

- `pyproject.toml` - Add pytest-xdist dependency and configuration
- `.github/workflows/ci.yml` - Optimize for 2-core runners
- `CONTRIBUTING.md` - Document parallel testing
- `uv.lock` - Updated with pytest-xdist
- `tests/**/*.py` - Review for test isolation (mark sequential tests if needed)

## Dependencies

**Recommended implementation order**:

- Implement after pytest-timeout (task 001)
- These work together: timeout prevents hanging even in parallel execution

**No blocking dependencies** - Can be implemented independently

## Additional Notes

**Why pytest-xdist?**

- **Faster feedback**: 3-4x speedup means faster development cycles
- **Better resource usage**: Utilize all available CPU cores
- **Cost savings**: Reduced GitHub Actions minutes
- **Scalability**: Test suite can grow without proportional time increase

**How pytest-xdist Works**:

```
Sequential Execution (current):
┌─────────────────────────────────────────┐
│ [Main Process]                          │
│   Test 1 → Test 2 → Test 3 → Test 4    │
│   (30 seconds total)                    │
└─────────────────────────────────────────┘

Parallel Execution (with -n 4):
┌─────────────────────────────────────────┐
│ [Controller Process]                    │
│   ├─ [Worker 0] Test 1, Test 5, ...    │
│   ├─ [Worker 1] Test 2, Test 6, ...    │
│   ├─ [Worker 2] Test 3, Test 7, ...    │
│   └─ [Worker 3] Test 4, Test 8, ...    │
│   (8 seconds total)                     │
└─────────────────────────────────────────┘
```

**Worker Count Options**:

```bash
# Auto-detect (recommended for local development)
-n auto  # Uses logical_cpus() from multiprocessing

# Explicit count (recommended for CI)
-n 2     # Good for GitHub Actions standard runners (2 cores)
-n 4     # Good for GitHub Actions large runners (4 cores)

# Disable parallelization (for debugging)
-n 0     # Run sequentially
```

**Coverage with pytest-xdist**:

pytest-cov has built-in support for pytest-xdist:

```bash
pytest -n auto --cov=nhl_scrabble --cov-report=html

# Coverage is collected from all workers and combined
# No configuration changes needed!
```

**Test Isolation Best Practices**:

```python
# ✅ Good: Isolated test (works in parallel)
def test_isolated():
    scorer = ScrabbleScorer()  # Fresh instance per test
    assert scorer.calculate_score("TEST") == 4

# ✅ Good: Using fixtures (pytest handles isolation)
def test_with_fixture(tmp_path):
    # tmp_path is unique per test even in parallel
    file = tmp_path / "test.txt"
    file.write_text("data")
    assert file.read_text() == "data"

# ❌ Bad: Shared global state (will fail in parallel)
GLOBAL_CACHE = {}

def test_that_modifies_global():
    GLOBAL_CACHE["key"] = "value"  # Race condition!
    assert GLOBAL_CACHE["key"] == "value"

# Fix: Use fixtures or mark as no_parallel
@pytest.mark.no_parallel
def test_that_modifies_global():
    GLOBAL_CACHE["key"] = "value"
    assert GLOBAL_CACHE["key"] == "value"
```

**Load Balancing**:

pytest-xdist uses intelligent load balancing:

```python
# Slow tests are scheduled early to maximize parallelization
# Fast tests fill in the gaps

Duration distribution:
Worker 0: [10s test] + [1s test] + [1s test] = 12s
Worker 1: [8s test] + [3s test] + [1s test] = 12s
Worker 2: [7s test] + [4s test] + [1s test] = 12s
Worker 3: [6s test] + [5s test] + [1s test] = 12s
# Total: 12s (vs 48s sequential) = 4x speedup
```

**Common Issues and Solutions**:

| Issue                           | Symptom                                  | Solution                                                       |
| ------------------------------- | ---------------------------------------- | -------------------------------------------------------------- |
| **Tests fail only in parallel** | Passes with `-n 0`, fails with `-n auto` | Test has shared state - fix or mark `@pytest.mark.no_parallel` |
| **Slower than expected**        | Less than 2x speedup on 4 cores          | Tests are I/O bound or have long setup/teardown                |
| **Flaky tests**                 | Intermittent failures in parallel        | Test has race condition - fix synchronization                  |
| **Coverage lower**              | Coverage drops with `-n auto`            | Bug in test (fixed by pytest-cov 4.1+)                         |

**Debugging Parallel Test Failures**:

```bash
# Step 1: Confirm it's a parallelization issue
pytest -n 0  # If this passes, it's a parallel issue

# Step 2: Find the problematic test
pytest --lf -n 0 -v  # Run last failed sequentially

# Step 3: Run just that test in parallel
pytest tests/test_problem.py::test_specific -n 4 -v

# Step 4: Add logging to understand the issue
pytest -n 2 -v -s  # -s shows print statements

# Step 5: Fix or mark as sequential
@pytest.mark.no_parallel  # If can't fix
```

**CI/CD Optimization**:

```yaml
# GitHub Actions: Standard runners (2 cores)
- name: Run tests
  run: pytest -n 2 --cov

# Local development: Use all available cores
$ pytest -n auto --cov

# Tox: Auto-detect (works in both environments)
[testenv]
commands = pytest -n auto {posargs}
```

**Performance Metrics to Track**:

```bash
# Before pytest-xdist
Total test time: 30.15s
CI time: ~45s (with setup)
Cost: 1 minute of Actions time

# After pytest-xdist (4 cores)
Total test time: 8.23s (3.66x faster)
CI time: ~20s (with setup) (2.25x faster overall)
Cost: 0.33 minutes of Actions time (67% savings!)

# Annual savings for 100 test runs/day
Before: 100 * 365 * 1 min = 36,500 minutes = 608 hours
After: 100 * 365 * 0.33 min = 12,045 minutes = 200 hours
Savings: 408 hours of CI time per year!
```

**When NOT to Use pytest-xdist**:

```python
# 1. Very few tests (< 5)
# Overhead > benefit

# 2. Tests are already very fast (< 1s total)
# Overhead > benefit

# 3. Tests require strict order
@pytest.mark.no_parallel  # Mark these tests

# 4. Tests modify shared external resources
# Database, files, environment variables
@pytest.mark.no_parallel  # Or use proper isolation
```

**pytest-xdist Advanced Features**:

```bash
# Load distribution strategies
pytest -n 4 --dist loadscope   # Distribute by scope (module/class)
pytest -n 4 --dist loadfile    # Distribute by file
pytest -n 4 --dist load        # Default: dynamic load balancing

# Maximum workers (useful for CI rate limits)
pytest -n auto --maxprocesses=4  # Cap at 4 workers even if more cores

# Test execution order
pytest -n 4 --dist loadgroup    # Group tests by xdist_group marker
```

**Compatibility**:

✅ **Works with**:

- pytest-cov (coverage collection)
- pytest-timeout (timeouts work per worker)
- pytest-mock (mocks are isolated per worker)
- pytest markers (all standard markers work)
- pytest fixtures (proper isolation maintained)

⚠️ **May need adjustment**:

- Tests that modify global state
- Tests that use shared databases
- Tests that create temporary files in fixed locations
- Tests that bind to specific ports

**Alternative: pytest-parallel**:

pytest-parallel is another option but pytest-xdist is more mature:

- pytest-xdist: 13k+ GitHub stars, industry standard
- pytest-parallel: 400+ GitHub stars, newer
- **Recommendation**: Use pytest-xdist (proven, well-maintained)

## Implementation Notes

*To be filled during implementation:*

- Actual speedup measured (target: 3-4x)
- Number of CPU cores available in different environments
- Any tests that needed `@pytest.mark.no_parallel`
- CI time savings observed
- Coverage percentages before/after (should be identical)
- Any flaky tests discovered and fixed
