# Performance Benchmark Testing Workflow

**GitHub Issue**: #306 - https://github.com/bdperkin/nhl-scrabble/issues/306

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

3-4 hours

## Description

Implement automated performance benchmark testing workflow that runs pytest-benchmark tests, compares results against the main branch, and comments on PRs with performance impacts. Catches performance regressions before they reach production.

## Current State

**No Automated Benchmarking:**

Currently, performance is tested manually if at all:

- No automated performance testing
- Regressions discovered after merge
- No baseline for comparison
- No performance tracking over time
- Manual testing is inconsistent

**Existing:**

- ✅ pytest-benchmark installed (dependency)
- ✅ Some benchmark tests exist
- ❌ No automated execution
- ❌ No regression detection
- ❌ No performance tracking

## Proposed Solution

Create `.github/workflows/benchmark.yml`:

```yaml
name: Performance Benchmarks

on:
  push:
    branches:
      - main
    paths:
      - src/**/*.py
      - tests/benchmark/**
      - pyproject.toml
  pull_request:
    paths:
      - src/**/*.py
      - tests/benchmark/**
      - pyproject.toml
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write

jobs:
  benchmark:
    name: Run Performance Benchmarks
    runs-on: ubuntu-latest

    steps:
      - name: Checkout PR branch
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'

      - name: Install UV
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true

      - name: Install dependencies
        run: |
          uv pip install -e ".[dev]" --system
          uv pip install pytest-benchmark --system

      - name: Run benchmarks on PR branch
        run: |
          pytest tests/benchmark/ --benchmark-only \
            --benchmark-json=pr-benchmark.json \
            --benchmark-min-rounds=5 \
            --benchmark-warmup=on

      - name: Save PR benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: pr-benchmark
          path: pr-benchmark.json
          retention-days: 7

      - name: Checkout main branch
        if: github.event_name == 'pull_request'
        run: |
          git fetch origin main
          git checkout origin/main

      - name: Run benchmarks on main branch
        if: github.event_name == 'pull_request'
        run: |
          # Reinstall in case dependencies changed
          uv pip install -e ".[dev]" --system
          pytest tests/benchmark/ --benchmark-only \
            --benchmark-json=main-benchmark.json \
            --benchmark-min-rounds=5 \
            --benchmark-warmup=on

      - name: Save main benchmark results
        if: github.event_name == 'pull_request'
        uses: actions/upload-artifact@v4
        with:
          name: main-benchmark
          path: main-benchmark.json
          retention-days: 7

      - name: Compare benchmarks
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');

            // Load benchmark results
            const prBench = JSON.parse(fs.readFileSync('pr-benchmark.json'));
            const mainBench = JSON.parse(fs.readFileSync('main-benchmark.json'));

            // Compare benchmarks
            const comparisons = [];
            const regressions = [];
            const improvements = [];

            for (const prTest of prBench.benchmarks) {
              const mainTest = mainBench.benchmarks.find(t => t.name === prTest.name);
              if (!mainTest) continue;

              const prTime = prTest.stats.mean;
              const mainTime = mainTest.stats.mean;
              const change = ((prTime - mainTime) / mainTime) * 100;

              const comparison = {
                name: prTest.name,
                prTime: prTime.toFixed(6),
                mainTime: mainTime.toFixed(6),
                change: change.toFixed(2),
                changePercent: Math.abs(change).toFixed(2)
              };

              comparisons.push(comparison);

              if (change > 10) {  // >10% slower = regression
                regressions.push(comparison);
              } else if (change < -10) {  // >10% faster = improvement
                improvements.push(comparison);
              }
            }

            // Generate comment
            let comment = `## 📊 Performance Benchmark Results\n\n`;

            if (regressions.length > 0) {
              comment += `### ⚠️ Performance Regressions Detected\n\n`;
              comment += `| Test | Main Branch | This PR | Change |\n`;
              comment += `| ---- | ----------- | ------- | ------ |\n`;
              for (const reg of regressions) {
                comment += `| \`${reg.name}\` | ${reg.mainTime}s | ${reg.prTime}s | 🔴 +${reg.changePercent}% slower |\n`;
              }
              comment += `\n`;
            }

            if (improvements.length > 0) {
              comment += `### ✅ Performance Improvements\n\n`;
              comment += `| Test | Main Branch | This PR | Change |\n`;
              comment += `| ---- | ----------- | ------- | ------ |\n`;
              for (const imp of improvements) {
                comment += `| \`${imp.name}\` | ${imp.mainTime}s | ${imp.prTime}s | 🟢 ${imp.changePercent}% faster |\n`;
              }
              comment += `\n`;
            }

            comment += `### 📈 All Benchmark Comparisons\n\n`;
            comment += `| Test | Main Branch | This PR | Change |\n`;
            comment += `| ---- | ----------- | ------- | ------ |\n`;
            for (const comp of comparisons) {
              const emoji = comp.change > 10 ? '🔴' : comp.change < -10 ? '🟢' : '⚪';
              const sign = comp.change > 0 ? '+' : '';
              comment += `| \`${comp.name}\` | ${comp.mainTime}s | ${comp.prTime}s | ${emoji} ${sign}${comp.change}% |\n`;
            }

            comment += `\n---\n`;
            comment += `*Benchmarks run with pytest-benchmark. Each test runs 5+ rounds with warmup.*\n`;

            // Check for existing comment
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.payload.pull_request.number
            });

            const existingComment = comments.find(c =>
              c.user.type === 'Bot' && c.body.includes('Performance Benchmark Results')
            );

            if (existingComment) {
              await github.rest.issues.updateComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: existingComment.id,
                body: comment
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                body: comment
              });
            }

            // Fail if significant regressions (>20%)
            const significantRegressions = regressions.filter(r => parseFloat(r.changePercent) > 20);
            if (significantRegressions.length > 0) {
              core.setFailed(`⚠️ Significant performance regressions detected (>20% slower)`);
            }

      - name: Store baseline on main
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          # Store benchmark results as baseline
          cp pr-benchmark.json benchmark-baseline.json

      - name: Upload baseline
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-baseline
          path: benchmark-baseline.json
          retention-days: 90
```

## Implementation Steps

1. **Create Benchmark Tests** (1-1.5h)

   - Create `tests/benchmark/` directory
   - Write benchmarks for critical paths
   - Test scoring performance
   - Test API client performance
   - Test report generation
   - Verify benchmarks run locally

1. **Create Workflow File** (1h)

   - Create `.github/workflows/benchmark.yml`
   - Configure triggers
   - Set up PR/main comparison
   - Add result comparison logic
   - Add PR commenting

1. **Configure Thresholds** (30min)

   - Set regression threshold (10%)
   - Set significant regression threshold (20%)
   - Define acceptable variance
   - Configure warmup/rounds

1. **Test Workflow** (1-1.5h)

   - Create PR with no performance change
   - Create PR with improvement
   - Create PR with regression
   - Verify comments accurate
   - Verify failure on significant regression

1. **Add Documentation** (30min)

   - Document benchmark tests
   - Add to CONTRIBUTING.md
   - Explain how to run locally
   - Document thresholds

## Testing Strategy

### Local Benchmark Testing

```bash
# Run all benchmarks
pytest tests/benchmark/ --benchmark-only

# Run with more detail
pytest tests/benchmark/ --benchmark-only --benchmark-verbose

# Save results
pytest tests/benchmark/ --benchmark-only --benchmark-json=results.json

# Compare with saved baseline
pytest tests/benchmark/ --benchmark-only --benchmark-compare=results.json

# Run specific benchmark
pytest tests/benchmark/test_scoring_bench.py::test_score_player_benchmark
```

### Workflow Testing

```bash
# Test 1: Baseline (no changes)
git checkout -b test/benchmark-baseline
# No changes to code
gh pr create --title "test: Benchmark baseline"
# Expected: No regressions, no improvements

# Test 2: Performance improvement
git checkout -b test/benchmark-improvement
# Optimize a function
gh pr create --title "perf: Optimize scoring"
# Expected: Green improvements shown

# Test 3: Performance regression
git checkout -b test/benchmark-regression
# Add inefficient code
gh pr create --title "test: Regression test"
# Expected: Red regressions shown, may fail if >20%
```

## Acceptance Criteria

- [x] Benchmark tests created in `tests/benchmark/` (exist in `tests/benchmarks/`)
- [x] Workflow file created: `.github/workflows/benchmark.yml`
- [x] Runs on pushes to main
- [x] Runs on PRs affecting performance-critical code
- [x] Compares PR vs main branch
- [x] Posts comparison comment on PRs
- [x] Highlights regressions (>10% slower)
- [x] Highlights improvements (>10% faster)
- [x] Fails CI on significant regressions (>20%)
- [x] Stores baseline from main branch
- [x] Benchmark results uploaded as artifacts
- [x] Documentation added for running locally
- [x] Thresholds documented
- [ ] Test PRs verified (will verify post-merge)

## Related Files

**New Files:**

- `.github/workflows/benchmark.yml` - Benchmark workflow
- `tests/benchmark/__init__.py` - Benchmark test package
- `tests/benchmark/test_scoring_bench.py` - Scoring benchmarks
- `tests/benchmark/test_api_bench.py` - API benchmarks
- `tests/benchmark/test_reports_bench.py` - Report benchmarks

**Modified Files:**

- `CONTRIBUTING.md` - Add benchmarking guidelines
- `CLAUDE.md` - Document benchmark workflow
- `pyproject.toml` - Ensure pytest-benchmark listed

## Dependencies

**Task Dependencies:**

- None - can be implemented independently

**Tool Dependencies:**

- `pytest-benchmark` - Already installed
- `actions/github-script@v7` - For comparison logic

## Additional Notes

### Benchmark Test Examples

```python
# tests/benchmark/test_scoring_bench.py
import pytest
from nhl_scrabble.scoring import ScrabbleScorer
from nhl_scrabble.models import Player


@pytest.fixture
def scorer():
    return ScrabbleScorer()


@pytest.fixture
def sample_player():
    return Player(
        firstName="Alexander", lastName="Ovechkin", sweaterNumber=8, positionCode="L"
    )


def test_score_calculation_benchmark(benchmark, scorer):
    """Benchmark basic score calculation."""
    result = benchmark(scorer.calculate_score, "Ovechkin")
    assert result > 0


def test_score_player_benchmark(benchmark, scorer, sample_player):
    """Benchmark player scoring."""
    result = benchmark(scorer.score_player, sample_player)
    assert result.total_score > 0


def test_large_name_benchmark(benchmark, scorer):
    """Benchmark scoring of very long names."""
    long_name = "A" * 1000
    result = benchmark(scorer.calculate_score, long_name)
    assert result > 0
```

### Performance Thresholds

**Regression Threshold: 10%**

- Warn on PRs
- Show in comparison table
- Don't fail CI

**Significant Regression: 20%**

- Fail CI
- Require review
- Must be justified

**Improvement Threshold: 10%**

- Celebrate!
- Show in comparison table
- Highlight in PR

### Benchmark Best Practices

**Good benchmarks:**

- Test one thing
- Representative workload
- Sufficient iterations
- Include warmup
- Deterministic

**Avoid:**

- Network calls (use mocks)
- Random data (use fixtures)
- File I/O (use in-memory)
- Non-deterministic operations

### Expected Performance Baseline

Based on current implementation:

```
test_score_calculation: ~0.000010s (10μs)
test_score_player: ~0.000015s (15μs)
test_team_aggregation: ~0.001000s (1ms)
test_report_generation: ~0.010000s (10ms)
```

### Future Enhancements

- Performance tracking dashboard
- Historical trend analysis
- Memory profiling
- CPU profiling
- Automated optimization suggestions
- Performance budget enforcement

## Implementation Notes

**Implemented**: 2026-04-28
**Branch**: new-features/039-benchmark-workflow
**PR**: #421 - https://github.com/bdperkin/nhl-scrabble/pull/421
**Commits**: 1 commit (044fb5c)

### Actual Implementation

Leveraged existing comprehensive benchmark suite rather than creating new tests:

**Workflow Implementation:**

- Created `.github/workflows/benchmark.yml` with complete PR comparison logic
- Runs on PRs affecting `src/**/*.py`, `tests/benchmarks/**`, `pyproject.toml`
- Runs on pushes to main to store baseline
- Uses Python 3.12 with UV for fast dependency installation
- Runs benchmarks with pytest-benchmark (5+ rounds, warmup enabled)
- Compares PR branch vs main branch using JavaScript in GitHub Actions
- Posts detailed comparison comment with regression/improvement highlights
- Updates existing comments to avoid spam
- Fails CI on significant regressions (>20%)
- Uploads artifacts (7-day for PRs, 90-day for baselines)

**Documentation:**

- Added Performance Benchmarking section to CONTRIBUTING.md
- Updated CLAUDE.md CI/CD section with benchmark workflow details
- Documented thresholds, best practices, and local execution

**Existing Benchmarks Used:**

- `tests/benchmarks/test_benchmark_scoring.py` (6 benchmarks)
- `tests/benchmarks/test_benchmark_reports.py` (8 benchmarks)
- `tests/benchmarks/test_logging_optimization.py` (2 benchmarks)
- Total: 16 comprehensive benchmarks covering critical paths

### Challenges Encountered

**yamllint Line Length:**

- Initial workflow had lines >100 characters in JavaScript template literals
- Fixed by splitting long template strings across multiple lines
- Maintained readability while satisfying linter

**pytest-xdist Conflict:**

- xdist parallel execution interferes with benchmark timing
- Resolved by adding `-n 0 --no-cov` flags to pytest command
- Ensures accurate, deterministic benchmark measurements

**mdformat Auto-Fixes:**

- Pre-commit hook auto-formatted markdown files
- Required restaging and recommitting
- No issues, just process overhead

### Deviations from Plan

**No New Benchmark Tests:**

- Plan suggested creating `test_api_bench.py`
- API benchmarks would require mocking or network calls (non-deterministic)
- Existing 16 benchmarks already cover critical performance paths
- Decision: Use existing benchmarks, skip API benchmarks

**Simplified Comparison Logic:**

- Used JavaScript in GitHub Actions instead of Python script
- More maintainable, fewer dependencies
- Direct access to GitHub API for PR comments

### Actual vs Estimated Effort

- **Estimated**: 3-4h
- **Actual**: ~2.5h
- **Variance**: -0.5 to -1.5h faster
- **Reason**: Benchmark tests already existed, main work was workflow creation and documentation

### Related PRs

- #421 - Main implementation

### Lessons Learned

**Leverage Existing Assets:**

- Don't create tests that already exist
- Review existing test coverage before implementing

**YAML Linting Matters:**

- Test workflows with yamllint before committing
- Long lines in JavaScript/YAML can fail linting
- Break up long strings proactively

**Benchmark Determinism:**

- Avoid network calls in benchmarks
- Avoid file I/O when possible
- Use fixed fixtures, not random data
- Disable parallel execution for timing accuracy

**Pre-commit Integration:**

- Auto-formatters can modify files during commit
- Expect to restage and recommit
- Not a bug, just part of the process

### Performance Metrics

**Benchmark Coverage:**

- 16 benchmarks total
- Performance ranges: 500ns (logging guards) to 10ms (full league scoring)
- All critical paths covered (scoring, aggregation, formatting)

**CI Impact:**

- Adds ~2-3 minutes to PR CI time
- Runs only on performance-critical file changes
- Benefits far outweigh cost (prevents production regressions)

**Baseline Storage:**

- 7-day retention for PR artifacts
- 90-day retention for main baselines
- Allows historical comparison

### Test Coverage

Local execution verified:

```bash
pytest tests/benchmarks/ --benchmark-only -n 0 --no-cov
# Results: 16 passed, 1 skipped
```

Pre-commit hooks: All 68 hooks passed
YAML validation: Passed
Workflow syntax: Valid
