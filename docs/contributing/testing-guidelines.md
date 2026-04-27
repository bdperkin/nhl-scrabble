# Testing Guidelines

Follow these guidelines when writing and organizing tests.

## Test Structure

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Name test files `test_*.py`
- Name test classes `Test*`
- Name test functions `test_*`

## Writing Tests

```python
class TestScrabbleScorer:
    """Tests for the ScrabbleScorer class."""

    def test_calculate_score_basic(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test basic score calculation."""
        assert scrabble_scorer.calculate_score("A") == 1
        assert scrabble_scorer.calculate_score("Z") == 10
```

## Test Coverage

- Aim for >80% overall coverage
- Critical modules should have >90% coverage
- All new features must include tests
- Bug fixes should include regression tests

## Flaky Test Retry Mechanisms

The project uses **[pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures)** to automatically retry flaky tests that may fail intermittently due to external dependencies, timing issues, or resource contention.

### When to Mark a Test as Flaky

Use the `@pytest.mark.flaky` decorator for tests that:

- Call external APIs or services
- Check external resources (links, files)
- Have timing-sensitive operations
- Involve database race conditions
- Depend on network conditions

### Retry Configuration

```python
# High flakiness (>10% failure rate)
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_external_api_call():
    """Test with external dependency.

    Note: Marked as flaky due to external API calls.
    Retries up to 3 times with 2-second delay between attempts.
    """
    pass


# Medium flakiness (5-10% failure rate)
@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_timing_sensitive():
    """Test with timing dependency."""
    pass


# Low flakiness (<5% failure rate)
@pytest.mark.flaky(reruns=1)
def test_rare_race_condition():
    """Test with rare race condition."""
    pass
```

### When NOT to Use Retry

- Tests failing due to logic errors (fix the test instead)
- Tests with wrong assertions (fix expectations)
- Tests with import/syntax errors (fix the code)

### Documentation

- Always add a note in the test docstring explaining why it's marked flaky
- Add entry to `docs/testing/flaky-tests.md`
- Create issue for root cause fix if appropriate

See [Flaky Tests Tracker](../testing/flaky-tests.md) for current flaky tests and monitoring guidelines.

## Diff Coverage (PR-Specific Coverage)

The project uses **[diff-cover](https://github.com/Bachmann1234/diff_cover)** to enforce test coverage on changed lines only in pull requests. This ensures new code is well-tested without requiring 100% coverage on existing code.

### What is Diff Coverage?

- **Total Coverage**: Coverage across entire codebase (~50% currently)
- **Diff Coverage**: Coverage on lines changed in your PR (target: ≥80%)

### Why Both Matter

| Metric       | Total Coverage  | Diff Coverage      |
| ------------ | --------------- | ------------------ |
| **Scope**    | Entire codebase | Changed lines only |
| **Purpose**  | Overall health  | PR quality         |
| **Target**   | ~50% (current)  | ≥80% (enforced)    |
| **Enforced** | ⚠️ Optional     | ✅ Required in CI  |

### Local Usage

```bash
# Generate coverage report
pytest --cov=nhl_scrabble --cov-report=xml

# Check diff coverage against main branch
diff-cover coverage.xml --compare-branch=origin/main

# With enforcement (fails if < 80%)
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80

# Generate HTML report for detailed review
diff-cover coverage.xml --html-report=diff-cover.html
open diff-cover.html
```

### Via Tox

```bash
# Run diff coverage check (same as CI)
tox -e diff-cover

# This runs:
# 1. pytest --cov=nhl_scrabble --cov-report=xml
# 2. diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
```

### CI Enforcement

⚠️ **Note**: diff-cover is currently a local development tool only. It is not yet enforced in CI due to git history limitations in GitHub Actions shallow clones. However, you should still run it locally to ensure your changes are well-tested.

To check diff coverage locally:

1. Run `tox -e diff-cover` or manually generate coverage and run diff-cover
1. Review which lines are missing coverage
1. Add tests for the uncovered lines
1. Re-run to verify ≥80% diff coverage before pushing

### Example Scenario

```
Your PR adds 50 new lines:
- 45 lines covered by tests
- 5 lines not covered

Total coverage: 50.4% (unchanged) ✓
Diff coverage: 90.0% (45/50) ✓

CI passes because diff coverage ≥ 80%
```

### Best Practices

- ✅ Run `diff-cover` locally before pushing
- ✅ Use HTML reports to see exactly which lines need tests
- ✅ Add tests for all new functionality
- ✅ Aim for ≥80% diff coverage on all changes
- ❌ Don't skip coverage on new code without good reason

### Configuration

Diff-cover is configured in `pyproject.toml`:

```toml
[tool.diff_cover]
compare_branch = "origin/main"
fail_under = 80.0
include_paths = ["src/"]
exclude_paths = ["tests/", "*/__main__.py"]
```
