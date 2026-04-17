"""Performance benchmark tests for nhl-scrabble.

This package contains pytest-benchmark tests for measuring and tracking
performance of critical code paths.

Benchmarks track:
- Scrabble scoring performance
- Report generation performance
- Bulk operations performance

Use:
    # Run all benchmarks
    pytest tests/benchmarks/ --benchmark-only

    # Save baseline
    pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline

    # Compare against baseline
    pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

    # Generate histogram
    pytest tests/benchmarks/ --benchmark-only --benchmark-histogram

    # Via tox
    tox -e benchmark
"""
