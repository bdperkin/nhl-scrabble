# Testing Philosophy

Understanding our approach to testing NHL Scrabble.

## Testing Goals

Our tests aim to:

1. **Verify correctness** - Does the code work as intended?
1. **Prevent regressions** - Does old code still work?
1. **Document behavior** - What is the expected behavior?
1. **Enable refactoring** - Can we change code safely?

## Test Pyramid

```
           /\
          /  \         Integration (20%)
         /____\           - Full workflows
        /      \          - Component interactions
       /  Unit  \         - Mocked external APIs
      /__________\
     Unit (80%)
     - Individual functions
     - Isolated components
     - Fast execution
```

### Why this distribution?

**Unit tests (80%)**:

- Fast to run (\<1s for all)
- Easy to write
- Pinpoint failures
- Test one thing at a time

**Integration tests (20%)**:

- Verify components work together
- Test real user workflows
- Catch integration bugs
- Slower but comprehensive

**No E2E tests**:

- CLI tool, not web app
- Integration tests cover full workflow
- Would be slow and fragile

## What We Test

### Core Logic (100% coverage goal)

- `ScrabbleScorer` - Letter value calculations
- `TeamProcessor` - Score aggregation
- `PlayoffCalculator` - Playoff seeding logic

**Why?**: This is our unique value - must be correct.

### API Client (Integration tests)

- Mock NHL API responses
- Test retry logic
- Test rate limiting
- Test error handling

**Why?**: External dependency - can't rely on real API.

### CLI (Integration tests)

- Test command invocation
- Test option parsing
- Test output formatting
- Test error messages

**Why?**: User-facing - must work correctly.

### Reports (Unit tests)

- Test formatting logic
- Test data transformations
- Test edge cases

**Why?**: Complex formatting - easy to break.

## What We Don't Test

### External APIs

**Don't test**:

- NHL API responses
- Network behavior
- Third-party libraries

**Why?**:

- Out of our control
- Would be slow and flaky
- Mock instead

### Framework Code

**Don't test**:

- Click argument parsing
- Pydantic validation
- Python standard library

**Why?**:

- Already tested by authors
- Trust mature libraries
- Focus on our code

## Mocking Strategy

### When to Mock

**Mock external dependencies**:

- NHL API calls
- Network requests
- File system operations
- Time/dates

**Don't mock**:

- Our own code
- Data structures
- Pure functions

### How We Mock

Using `pytest-mock` and `unittest.mock`:

```python
def test_fetch_roster(mocker):
    # Mock external API
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {...}

    # Test our code
    client = NHLApiClient()
    roster = client.fetch_roster("TOR")

    # Verify
    assert len(roster) == 25
    mock_get.assert_called_once()
```

## Test Organization

```
tests/
├── unit/                   # Fast, isolated unit tests
│   ├── test_scrabble.py    # Scoring logic
│   ├── test_processor.py   # Business logic
│   └── test_models.py      # Data models
├── integration/            # Slower integration tests
│   ├── test_cli.py         # CLI workflows
│   └── test_api_client.py  # API integration
└── conftest.py             # Shared fixtures
```

## Naming Conventions

```python
def test_<function>_<scenario>_<expected>():
    """Test that <function> <expected> when <scenario>."""
    # Arrange
    # Act
    # Assert
```

**Examples**:

```python
def test_calculate_score_simple_name_returns_correct_value():
    """Test that calculate_score returns correct value for simple name."""


def test_fetch_roster_api_failure_raises_exception():
    """Test that fetch_roster raises exception on API failure."""
```

## Coverage Targets

- **Core logic**: 100% coverage required
- **Reports**: >90% coverage
- **Utilities**: >80% coverage
- **Overall**: >80% coverage

**Check coverage**:

```bash
pytest --cov
pytest --cov --cov-report=html
```

## Test Fixtures

Reusable test data in `conftest.py`:

```python
@pytest.fixture
def sample_player():
    """Sample player for testing."""
    return Player(
        firstName="Alexander", lastName="Ovechkin", sweaterNumber=8, positionCode="L"
    )


@pytest.fixture
def mock_nhl_api(mocker):
    """Mock NHL API responses."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {...}
    return mock_get
```

## Parametrized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize(
    "name,expected",
    [
        ("A", 1),
        ("Z", 10),
        ("TEST", 4),
        ("HELLO", 8),
    ],
)
def test_scores(name, expected):
    scorer = ScrabbleScorer()
    assert scorer.calculate_score(name) == expected
```

## Continuous Integration

Tests run automatically on:

- Every commit (pre-commit hooks)
- Every push (GitHub Actions)
- Every PR (required to pass)
- Multiple Python versions (3.12, 3.13, 3.14, 3.15)

**CI workflow**:

```yaml
  - Run pre-commit hooks
  - Run pytest on py3.12, 3.13, 3.14, 3.15
  - Check coverage >80%
  - Run type checking (mypy)
  - Run linting (ruff)
```

## Trade-offs

### High Coverage vs Speed

**Chose high coverage**:

- ✅ Catch more bugs
- ✅ Safe refactoring
- ❌ Slower test suite

**Currently**: 131 tests in ~25s (acceptable)

### Mocking vs Real APIs

**Chose mocking**:

- ✅ Fast and reliable
- ✅ Test edge cases
- ❌ May miss real API changes

**Mitigation**: Occasional manual testing with real API

### Unit vs Integration

**Chose more unit tests**:

- ✅ Faster feedback
- ✅ Easier debugging
- ❌ May miss integration bugs

**Mitigation**: Comprehensive integration tests for critical paths

## Future Improvements

### Property-Based Testing

Use Hypothesis for generative testing:

```python
from hypothesis import given
from hypothesis.strategies import text


@given(text(alphabet=string.ascii_letters))
def test_score_any_text(s):
    scorer = ScrabbleScorer()
    assert scorer.calculate_score(s) >= 0
```

### Mutation Testing

Verify tests actually catch bugs:

```bash
mutmut run  # Introduce mutations
mutmut results  # See if tests caught them
```

### Performance Testing

Benchmark critical paths:

```python
def test_performance_benchmark(benchmark):
    result = benchmark(scorer.calculate_score, "LONGNAME" * 100)
    assert result > 0
```

## Related

- [How to Run Tests](../how-to/run-tests.md) - Running tests
- [Architecture Overview](architecture.md) - System design
- [First Contribution](../tutorials/03-first-contribution.md) - Writing tests
