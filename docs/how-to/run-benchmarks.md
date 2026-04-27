# How to Run Performance Benchmarks

Track performance and prevent regressions using pytest-benchmark.

## Problem

You need to measure code performance or ensure your changes don't introduce performance regressions.

## Quick Start

```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only -n 0

# Compare against baseline
tox -e benchmark-compare
```

## Solutions

### Method 1: Run benchmarks

**When to use**: Quick performance check.

```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only -n 0
```

**Why -n 0?** Benchmarks require sequential execution (no parallel workers) for reliable timing measurements.

### Method 2: Save baseline

**When to use**: Before making performance improvements.

```bash
# Save baseline for future comparisons
pytest tests/benchmarks/ --benchmark-only -n 0 --benchmark-save=baseline
```

### Method 3: Compare against baseline

**When to use**: After optimization to verify improvements.

```bash
# Compare against baseline (detect regressions)
pytest tests/benchmarks/ --benchmark-only -n 0 --benchmark-compare=baseline
```

### Method 4: Generate visualization

**When to use**: Visual analysis of performance distribution.

```bash
# Generate performance histogram
pytest tests/benchmarks/ --benchmark-only -n 0 --benchmark-histogram
```

### Method 5: Via Tox

**When to use**: Standardized benchmark workflow.

```bash
# Run benchmarks and save latest
tox -e benchmark

# Compare against baseline
tox -e benchmark-compare
```

## Performance Targets

| Operation                          | Target (mean) | Threshold |
| ---------------------------------- | ------------- | --------- |
| **Scrabble score short name**      | \<100 ns      | +20%      |
| **Scrabble score long name**       | \<200 ns      | +20%      |
| **Score full roster (23 players)** | \<5 μs        | +20%      |
| **Score all teams (~700 players)** | \<100 μs      | +20%      |
| **Sort players by score**          | \<1 ms        | +20%      |
| **Aggregate by division**          | \<500 μs      | +20%      |

## Configuration

Benchmarks are configured in `pyproject.toml`:

- **Storage**: `.benchmarks/` directory (auto-created, git-ignored)
- **Regression threshold**: 20% (configurable)
- **Warmup**: 5 iterations before measurement
- **Statistical analysis**: min, max, mean, stddev, median, IQR, outliers

## When to Run Benchmarks

1. **Before optimizing**: Establish baseline to measure improvement
1. **After optimizing**: Verify optimization actually helped
1. **Before committing**: Ensure no performance regressions
1. **During code review**: Compare branch performance vs main

## Example Output

```
---------------------------------- benchmark: 14 tests ----------------------------------
Name (time in ns)                  Min         Max        Mean      StdDev    Median
------------------------------------------------------------------------------------
test_benchmark_short_name      735.40    2,146.35     768.52      57.22    759.14
test_benchmark_full_league   1,910,574  3,079,815  1,984,307   80,544  1,967,394
------------------------------------------------------------------------------------
```

## Regression Detection

If your changes cause performance to degrade beyond the threshold (20%), the benchmark comparison will fail:

```bash
$ pytest tests/benchmarks/ --benchmark-compare=baseline

❌ FAILED: test_benchmark_full_league regression threshold exceeded
   Baseline: 1,910,574 ns
   Current:  2,342,129 ns
   Change:   +22.6% (threshold: 20%)
```

## Best Practices

- ✅ Run benchmarks sequentially (`-n 0`)
- ✅ Commit baselines with code
- ✅ Compare before/after optimizations
- ✅ Focus on critical paths (scoring, sorting, aggregation)
- ❌ Don't benchmark I/O operations (network, disk)
- ❌ Don't run benchmarks in parallel (`pytest -n auto` will auto-disable)

## Related Documentation

- [How to Run Tests](run-tests.md) - General test execution
- [Testing Philosophy](../explanation/testing-philosophy.md) - Why we test the way we do
