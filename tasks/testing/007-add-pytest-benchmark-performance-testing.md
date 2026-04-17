# Add pytest-benchmark for Performance Regression Testing

**GitHub Issue**: #125 - https://github.com/bdperkin/nhl-scrabble/issues/125

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Add pytest-benchmark plugin to track performance and prevent performance regressions in critical code paths through automated benchmark tests.

Currently, there's no automated way to detect if code changes make the application slower. We have performance-sensitive code (API fetching, scoring calculations, report generation) but no tests to ensure these don't regress.

pytest-benchmark provides:

- Automated performance testing integrated with pytest
- Historical baseline tracking (saves results for comparison)
- Statistical analysis of performance (mean, stddev, min, max)
- Regression detection (fails tests if performance degrades)
- Comparison reports (before vs after changes)
- Integration with CI for continuous performance monitoring

**Impact**: Prevent performance regressions, track performance improvements over time, identify bottlenecks, establish performance baselines

**ROI**: High - moderate setup effort (1-2h), ongoing value from regression prevention

## Current State

No automated performance testing exists:

**Performance-sensitive code** (identified):

1. **Scrabble scoring** (`src/nhl_scrabble/scoring/scrabble.py`):

   ```python
   class ScrabbleScorer:
       def calculate_score(self, text: str) -> int:
           # Called for every player on every team (~700 times per analysis)
           return sum(self.SCRABBLE_VALUES.get(char.upper(), 0) for char in text)
   ```

1. **NHL API fetching** (`src/nhl_scrabble/api/nhl_client.py`):

   ```python
   async def fetch_all_rosters(self) -> list[Team]:
       # Makes 32+ API calls (one per team)
       # Currently has timing code for rate limiting
       elapsed = time.time() - self._last_request_time
   ```

1. **Report generation** (`src/nhl_scrabble/reports/*.py`):

   ```python
   def generate(self) -> str:
       # Builds large text reports
       # String concatenation, sorting, formatting
   ```

**Existing timing code** (manual, not tested):

```python
# src/nhl_scrabble/api/nhl_client.py
start = time.time()
# ... operation ...
elapsed = time.time() - start
```

**Problems**:

- No baseline to compare against
- No alerts if performance degrades
- Manual inspection required
- No historical tracking
- Can't detect gradual slowdowns

**Missing**:

- No pytest-benchmark in dependencies
- No benchmark tests
- No performance baselines
- No regression detection in CI

## Proposed Solution

Add pytest-benchmark with benchmark tests for critical code paths:

**Step 1: Add pytest-benchmark to dependencies**:

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-timeout>=2.2.0",
    "pytest-xdist>=3.5.0",
    "pytest-randomly>=3.15.0",
    "pytest-sugar>=1.0.0",
    "pytest-clarity>=1.0.1",
    "diff-cover>=8.0.0",
    "pytest-benchmark>=4.0.0",  # Add performance benchmarking
    "beautifulsoup4>=4.12.0",
]
```

**Step 2: Create benchmark tests**:

```python
# tests/benchmarks/test_benchmark_scoring.py
"""Benchmark tests for Scrabble scoring performance."""

import pytest
from nhl_scrabble.scoring import ScrabbleScorer
from nhl_scrabble.models.player import Player


@pytest.fixture
def scorer():
    """ScrabbleScorer instance."""
    return ScrabbleScorer()


def test_benchmark_calculate_score_short(benchmark, scorer):
    """Benchmark scoring short names (worst case: common operation)."""
    # Typical player name length
    result = benchmark(scorer.calculate_score, "MATTHEWS")
    assert result > 0


def test_benchmark_calculate_score_long(benchmark, scorer):
    """Benchmark scoring long names."""
    # Longest player names are ~20 characters
    result = benchmark(scorer.calculate_score, "KONSTANTINOV")
    assert result > 0


def test_benchmark_score_full_roster(benchmark, scorer):
    """Benchmark scoring full team roster (23 players)."""
    players = [
        Player(firstName="Auston", lastName="Matthews"),
        Player(firstName="Mitch", lastName="Marner"),
        # ... 21 more players (realistic roster)
    ]

    def score_roster():
        return [scorer.score_player(p) for p in players]

    result = benchmark(score_roster)
    assert len(result) == 23


def test_benchmark_score_all_teams(benchmark, scorer):
    """Benchmark scoring all NHL teams (~700 players)."""
    # Simulates full NHL analysis
    fake_players = [
        Player(firstName=f"Player{i}", lastName=f"Name{i}")
        for i in range(700)
    ]

    def score_all():
        return [scorer.score_player(p) for p in fake_players]

    result = benchmark(score_all)
    assert len(result) == 700
```

```python
# tests/benchmarks/test_benchmark_reports.py
"""Benchmark tests for report generation performance."""

import pytest
from nhl_scrabble.reports.team_report import TeamReport
from nhl_scrabble.models.team import TeamScore


@pytest.fixture
def sample_teams():
    """Generate sample team data for benchmarking."""
    return [
        TeamScore(team_abbrev=f"T{i}", total_score=1000+i, players=[])
        for i in range(32)
    ]


def test_benchmark_team_report_generation(benchmark, sample_teams):
    """Benchmark team report generation."""
    report = TeamReport(sample_teams)

    result = benchmark(report.generate)

    assert len(result) > 0
    assert "NHL Scrabble" in result
```

**Step 3: Configure pytest-benchmark**:

```toml
# pyproject.toml
[tool.pytest.ini_options]
# ... existing config ...

# Benchmark configuration
[tool.pytest_benchmark]
# Save results for comparison
save = true
save_data = true

# Automatically compare against previous runs
compare = "0001"  # Compare against run 0001 (baseline)

# Fail if performance degrades beyond threshold
fail_on_regression = true
regression_threshold = 0.2  # 20% slower = fail

# Storage location
storage = ".benchmarks"

# Columns to display
columns = ["min", "max", "mean", "stddev", "median", "iqr", "outliers", "rounds", "iterations"]

# Histogram display
histogram = "normal"

# Warmup rounds (iterations before measurement)
warmup = true
warmup_iterations = 5

# Minimum time to run each benchmark
min_time = 0.000005  # 5 microseconds
```

**Step 4: Add tox environment for benchmarks**:

```ini
# tox.ini
[testenv:benchmark]
description = Run performance benchmark tests
deps =
    pytest>=8.0.0
    pytest-benchmark>=4.0.0
commands_pre =
    pytest-benchmark --version
commands =
    # Run benchmarks and save results
    pytest tests/benchmarks/ --benchmark-only --benchmark-save=latest

    # Compare against baseline (if exists)
    pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001 || true
allowlist_externals =
    pytest-benchmark
labels = quality, performance

[testenv:benchmark-compare]
description = Compare benchmark results against baseline
deps =
    pytest>=8.0.0
    pytest-benchmark>=4.0.0
commands =
    # Compare current code against baseline
    pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001
labels = quality, performance
```

**Step 5: CLI usage examples**:

```bash
# Run benchmarks and save as baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline

# Run benchmarks and compare against baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

# Run benchmarks with histogram
pytest tests/benchmarks/ --benchmark-only --benchmark-histogram

# Run specific benchmark
pytest tests/benchmarks/test_benchmark_scoring.py::test_benchmark_calculate_score_short

# Via tox
tox -e benchmark

# Compare against specific run
tox -e benchmark-compare
```

**Step 6: Example output**:

```
---------------------- benchmark: 4 tests ----------------------
Name (time in ns)                          Min        Max       Mean
--------------------------------------------------------------------
test_benchmark_calculate_score_short      45.0      125.0      52.3
test_benchmark_calculate_score_long       78.0      234.0      89.1
test_benchmark_score_full_roster       1_234.0    2_567.0   1_456.2
test_benchmark_score_all_teams        38_901.0   52_345.0  41_234.5
--------------------------------------------------------------------

Saved benchmark data in: .benchmarks/0001_baseline.json
```

**Step 7: Comparison output**:

```bash
$ pytest tests/benchmarks/ --benchmark-compare=0001

-------------------------- benchmark: 4 tests --------------------------
Name (time in ns)                          Min                      Change
----------------------------------------------------------------------------
test_benchmark_calculate_score_short      45.0 (baseline)          +2.3% ✅
test_benchmark_calculate_score_long       78.0 (baseline)          +1.1% ✅
test_benchmark_score_full_roster       1_234.0 (baseline)         -5.2% ⚡
test_benchmark_score_all_teams        38_901.0 (baseline)         +23.4% ❌

❌ FAILED: test_benchmark_score_all_teams regression threshold exceeded
   Baseline: 38,901 ns
   Current:  48,012 ns
   Change:   +23.4% (threshold: 20%)
```

## Implementation Steps

1. **Add pytest-benchmark to dependencies**:

   - Update `pyproject.toml` `[project.optional-dependencies.test]`
   - Add `pytest-benchmark>=4.0.0`

1. **Create benchmarks directory**:

   - Create `tests/benchmarks/` directory
   - Create `__init__.py`
   - Create benchmark test files

1. **Write benchmark tests**:

   - `test_benchmark_scoring.py` - Scrabble scoring benchmarks
   - `test_benchmark_reports.py` - Report generation benchmarks
   - (Optional) `test_benchmark_api.py` - API client benchmarks

1. **Configure pytest-benchmark**:

   - Add `[tool.pytest_benchmark]` to `pyproject.toml`
   - Set regression threshold, storage location, etc.

1. **Add tox environments**:

   - `[testenv:benchmark]` - Run benchmarks
   - `[testenv:benchmark-compare]` - Compare against baseline

1. **Establish baselines**:

   - Run `pytest tests/benchmarks/ --benchmark-save=baseline`
   - Commit `.benchmarks/` directory (or exclude from git)
   - Document baseline values

1. **Update lock file**:

   - Run `uv lock` to update dependencies

1. **Test locally**:

   - Run benchmarks
   - Verify output shows timing statistics
   - Make a code change and verify comparison works

1. **(Optional) Add to CI**:

   - Add benchmark environment to CI matrix
   - Configure to compare against main branch baseline
   - Decide whether to fail CI on regression

1. **Document usage**:

   - Add to CONTRIBUTING.md
   - Explain how to run benchmarks
   - Document how to compare results
   - Explain regression threshold

## Testing Strategy

**Baseline Establishment**:

```bash
# Step 1: Run benchmarks to establish baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline

# Output:
# Saved benchmark data in: .benchmarks/0001_baseline.json

# Step 2: Verify baseline saved
ls .benchmarks/
# 0001_baseline.json

# Step 3: Run again to verify consistency
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

# Should show minimal differences (<5%)
```

**Regression Detection**:

```bash
# Step 1: Make code change that slows down scoring
# (e.g., add unnecessary computation)

# Step 2: Run benchmarks with comparison
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

# Expected: FAIL if >20% slower
# ❌ FAILED: Regression threshold exceeded
```

**Improvement Verification**:

```bash
# Step 1: Make optimization (e.g., cache SCRABBLE_VALUES lookup)

# Step 2: Run benchmarks
pytest tests/benchmarks/ --benchmark-compare=baseline

# Expected: Shows percentage improvement
# ⚡ -15.3% faster
```

**Histogram Visualization**:

```bash
# Generate histogram
pytest tests/benchmarks/ --benchmark-only --benchmark-histogram

# Creates: .benchmarks/histogram.svg
# Shows: Distribution of execution times
```

## Acceptance Criteria

- [ ] pytest-benchmark added to `[project.optional-dependencies.test]`
- [ ] Lock file updated with pytest-benchmark
- [ ] `tests/benchmarks/` directory created
- [ ] Benchmark tests written for scoring, reports (minimum 4 benchmarks)
- [ ] `[tool.pytest_benchmark]` configuration added to `pyproject.toml`
- [ ] Regression threshold set (e.g., 20%)
- [ ] `[testenv:benchmark]` added to `tox.ini`
- [ ] Baseline established and saved
- [ ] Running `pytest tests/benchmarks/` shows timing statistics
- [ ] `--benchmark-compare` shows comparison against baseline
- [ ] Regression detection works (fails if too slow)
- [ ] Histogram generation works with `--benchmark-histogram`
- [ ] Works with existing pytest configuration
- [ ] Documentation updated (CONTRIBUTING.md)
- [ ] Baseline values documented

## Related Files

- `pyproject.toml` - Add pytest-benchmark dependency and configuration
- `tox.ini` - Add benchmark tox environments
- `tests/benchmarks/` - New directory for benchmark tests
- `tests/benchmarks/test_benchmark_scoring.py` - Scoring benchmarks
- `tests/benchmarks/test_benchmark_reports.py` - Report benchmarks
- `.benchmarks/` - Storage for benchmark results (git: optional)
- `CONTRIBUTING.md` - Document benchmark usage
- `uv.lock` - Updated with pytest-benchmark

## Dependencies

**Recommended implementation order**:

- Implement after basic pytest setup
- Independent of other testing tasks (001-006)
- Can be implemented standalone

**No blocking dependencies** - Can be implemented independently

**Works with**:

- pytest (required)
- All existing pytest plugins
- Tox environments
- CI workflows

## Additional Notes

**Why pytest-benchmark?**

- **Prevent regressions**: Catch performance degradation early
- **Track improvements**: Measure optimization effectiveness
- **Identify bottlenecks**: Know what's slow
- **Historical tracking**: See performance trends over time
- **Integrated**: Works with existing pytest setup
- **Statistical**: Proper statistical analysis, not just single runs

**How pytest-benchmark Works**:

```
Standard test:
  def test_function():
      result = my_function()
      assert result == expected

Benchmark test:
  def test_function(benchmark):
      result = benchmark(my_function)  ← Measured automatically
      assert result == expected

Benchmark execution:
  1. Warmup rounds (5 iterations)
  2. Calibration (determine iterations needed)
  3. Measurement rounds (multiple iterations)
  4. Statistical analysis (mean, stddev, min, max)
  5. Save results to .benchmarks/
  6. Compare against baseline (if configured)
```

**Benchmark Test Patterns**:

```python
# Pattern 1: Simple function benchmark
def test_benchmark_simple(benchmark):
    result = benchmark(my_function, arg1, arg2)
    assert result == expected

# Pattern 2: Setup/teardown
def test_benchmark_with_setup(benchmark):
    # Setup not measured
    data = prepare_data()

    # Only this is measured
    result = benchmark(process_data, data)

    # Teardown not measured
    cleanup(result)

# Pattern 3: Callable object
def test_benchmark_callable(benchmark):
    @benchmark
    def operation():
        return complex_operation()

    assert operation > 0

# Pattern 4: Custom rounds
def test_benchmark_custom_rounds(benchmark):
    benchmark.pedantic(my_function, rounds=100, iterations=10)
```

**Performance Targets** (examples for this project):

| Operation                          | Target (mean) | Threshold |
| ---------------------------------- | ------------- | --------- |
| **Scrabble score short name**      | \<100 ns      | +20%      |
| **Scrabble score long name**       | \<200 ns      | +20%      |
| **Score full roster (23 players)** | \<5 μs        | +20%      |
| **Score all teams (~700 players)** | \<100 μs      | +20%      |
| **Generate team report**           | \<10 ms       | +30%      |

**Storage Options**:

```bash
# Option 1: Commit baselines to git (recommended)
# - Baselines versioned with code
# - Easy comparison across branches
# - Add .benchmarks/ to git

# Option 2: Exclude from git (alternative)
# - Baselines local to developer
# - Smaller repository
# - Add .benchmarks/ to .gitignore
```

**CI Integration** (optional):

```yaml
# .github/workflows/ci.yml
- name: Run benchmarks
  run: |
    # Run benchmarks
    pytest tests/benchmarks/ --benchmark-only --benchmark-save=ci_${GITHUB_SHA}

    # Compare against main branch baseline
    git fetch origin main
    git checkout origin/main -- .benchmarks/0001_baseline.json
    pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001 || true
```

**Comparison Modes**:

```bash
# Compare against specific baseline
pytest --benchmark-compare=0001

# Compare against latest
pytest --benchmark-compare=latest

# Compare against name
pytest --benchmark-compare=baseline

# Compare against previous run
pytest --benchmark-compare

# Show histogram
pytest --benchmark-histogram

# Sort by specific column
pytest --benchmark-sort=mean
pytest --benchmark-sort=min
```

**Statistics Explained**:

| Metric         | Meaning             | Target                       |
| -------------- | ------------------- | ---------------------------- |
| **min**        | Fastest execution   | Best case performance        |
| **max**        | Slowest execution   | Worst case performance       |
| **mean**       | Average time        | Typical performance          |
| **stddev**     | Standard deviation  | Consistency (lower = better) |
| **median**     | Middle value        | Less affected by outliers    |
| **iqr**        | Interquartile range | Consistency measure          |
| **outliers**   | Unusual values      | Should be low                |
| **rounds**     | Test repetitions    | More = better stats          |
| **iterations** | Calls per round     | Calibrated automatically     |

**Regression Threshold Guidelines**:

| Threshold | Meaning     | When to Use          |
| --------- | ----------- | -------------------- |
| **5%**    | Very strict | Critical paths       |
| **10%**   | Strict      | Important operations |
| **20%**   | Moderate    | General code         |
| **50%**   | Lenient     | Non-critical code    |

Recommended: Start with 20%, tighten to 10% for critical code.

**Example Benchmark Test Suite**:

```python
# tests/benchmarks/test_benchmark_scoring.py
import pytest
from nhl_scrabble.scoring import ScrabbleScorer


@pytest.fixture
def scorer():
    return ScrabbleScorer()


class TestScoringSingleName:
    """Benchmark individual scoring operations."""

    def test_benchmark_short_name(self, benchmark, scorer):
        """2-5 characters (common)."""
        result = benchmark(scorer.calculate_score, "OVI")
        assert result > 0

    def test_benchmark_medium_name(self, benchmark, scorer):
        """6-10 characters (typical)."""
        result = benchmark(scorer.calculate_score, "MATTHEWS")
        assert result > 0

    def test_benchmark_long_name(self, benchmark, scorer):
        """11+ characters (edge case)."""
        result = benchmark(scorer.calculate_score, "KONSTANTINOV")
        assert result > 0


class TestScoringBulkOperations:
    """Benchmark batch scoring operations."""

    def test_benchmark_team_roster(self, benchmark, scorer):
        """Full team roster (23 players)."""
        names = [f"Player{i} Name{i}" for i in range(23)]

        def score_all():
            return [scorer.calculate_score(name) for name in names]

        result = benchmark(score_all)
        assert len(result) == 23

    def test_benchmark_full_league(self, benchmark, scorer):
        """All NHL players (~700)."""
        names = [f"Player{i} Name{i}" for i in range(700)]

        def score_all():
            return [scorer.calculate_score(name) for name in names]

        result = benchmark(score_all)
        assert len(result) == 700
```

**Best Practices**:

```bash
# ✅ Good: Run benchmarks before committing optimization
pytest tests/benchmarks/ --benchmark-compare=baseline
# Shows if optimization actually helped

# ✅ Good: Separate benchmarks from regular tests
pytest tests/unit/  # Regular tests
pytest tests/benchmarks/ --benchmark-only  # Benchmarks only

# ✅ Good: Use --benchmark-only to skip assertions
# Benchmarks run faster without test logic

# ✅ Good: Commit baselines with code
# Makes comparison across branches easy

# ❌ Bad: Running benchmarks in parallel
# pytest -n auto tests/benchmarks/  # Don't do this
# Benchmark results will be unreliable

# ❌ Bad: Benchmarking I/O operations
# Network calls, disk I/O - too variable
# Mock external dependencies for benchmarks

# ❌ Bad: Too strict thresholds
# 5% threshold on non-critical code
# Results in false failures
```

**Common Questions**:

**Q: Should benchmarks run in CI?**
A: Optional. Useful for regression detection, but can be flaky on shared CI runners.

**Q: How many iterations should benchmarks run?**
A: pytest-benchmark auto-calibrates. Typically 100-1000 iterations for fast code.

**Q: What if benchmarks are slow?**
A: Use `--benchmark-disable` to skip them during normal development.

**Q: Should I benchmark API calls?**
A: No, mock external dependencies. Benchmark application logic only.

**Q: Can I benchmark async code?**
A: Yes, but requires special setup. pytest-benchmark supports async.

**Q: What about memory benchmarks?**
A: pytest-benchmark focuses on time. Use memory_profiler for memory.

## Implementation Notes

*To be filled during implementation:*

- Baseline values established for each benchmark
- Number of benchmarks created (target: 4-8)
- Regression threshold chosen (recommended: 20%)
- Whether baselines committed to git or excluded
- Whether benchmarks added to CI (optional)
- Any performance optimizations discovered
- Developer feedback on benchmark utility
