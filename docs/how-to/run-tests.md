# How to Run Tests

Execute different test configurations for development and CI verification.

## Problem

You need to run tests to verify your changes before submitting a pull request.

## Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/unit/test_scrabble.py

# Run specific test function
pytest tests/unit/test_scrabble.py::test_calculate_score
```

## Solutions

### Method 1: Run all tests (fastest)

**When to use**: Quick verification during development.

**Command**:

```bash
pytest
```

**Output**:

```
================================ test session starts =================================
platform linux -- Python 3.12.19, pytest-9.0.3, pluggy-1.6.0
collected 131 items

tests/unit/test_scrabble.py ............                                      [  9%]
tests/unit/test_team_processor.py ..........                                  [ 17%]
tests/integration/test_cli.py ....................                            [ 32%]
...

======================== 131 passed in 23.45s ===========================
```

### Method 2: Run with coverage

**When to use**: Verify your changes have test coverage.

**Command**:

```bash
pytest --cov
```

**Output**:

```
======================== tests coverage ================================
Name                                    Stmts   Miss  Branch  BrPart  Cover
---------------------------------------------------------------------------
src/nhl_scrabble/cli.py                  114     16      20       4  85.07%
src/nhl_scrabble/scoring/scrabble.py      25      0       4       0 100.00%
...
---------------------------------------------------------------------------
TOTAL                                    705     92     164      24  83.89%

======================== 131 passed in 25.34s ===========================
```

**Target**: Aim for >80% coverage on code you modify.

### Method 3: Run specific test file

**When to use**: Testing a specific module.

**Command**:

```bash
pytest tests/unit/test_scrabble.py -v
```

**Output**:

```
tests/unit/test_scrabble.py::test_scrabble_values PASSED                 [ 14%]
tests/unit/test_scrabble.py::test_calculate_score PASSED                 [ 28%]
tests/unit/test_scrabble.py::test_score_player PASSED                    [ 42%]
...
```

### Method 4: Run specific test function

**When to use**: Debugging a single test.

**Command**:

```bash
pytest tests/unit/test_scrabble.py::test_calculate_score -v
```

**Add extra verbosity**:

```bash
pytest tests/unit/test_scrabble.py::test_calculate_score -vv
```

### Method 5: Run tests by marker

**When to use**: Running groups of tests (unit, integration, slow).

**Commands**:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

**Available markers**:

- `unit` - Fast, isolated unit tests
- `integration` - Tests that hit external APIs
- `slow` - Tests that take >5 seconds

### Method 6: Run with tox (multiple Python versions)

**When to use**: Verify compatibility before submitting PR.

**Command**:

```bash
# Run all tox environments
tox

# Run specific Python version
tox -e py312

# Run in parallel (10x faster with tox-uv)
tox -p auto
```

**Available environments**:

- `py312`, `py313`, `py314`, `py315` - Different Python versions
- `ruff-check` - Linting
- `mypy` - Type checking
- `coverage` - Coverage report

See [Tox Reference](../../docs/TOX.md) for details.

### Method 7: Run tests on file change (watch mode)

**When to use**: Continuous testing during development.

**Install pytest-watch**:

```bash
pip install pytest-watch
```

**Run**:

```bash
# Watch all files
ptw

# Watch specific directory
ptw -- tests/unit/

# With coverage
ptw -- --cov
```

Now tests run automatically when you save files!

### Method 8: Run with verbose output

**When to use**: Debugging test failures.

**Commands**:

```bash
# Verbose output
pytest -v

# Very verbose output
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Combine options
pytest -vvs -l
```

### Method 9: Run failed tests only

**When to use**: Re-running after fixing failures.

**Commands**:

```bash
# Run tests that failed last time
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Method 10: Run with coverage report

**When to use**: Generating coverage reports for analysis.

**HTML report**:

```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

**Terminal report**:

```bash
pytest --cov --cov-report=term-missing
```

Shows which lines aren't covered:

```
Name                                    Stmts   Miss  Branch  BrPart  Cover   Missing
--------------------------------------------------------------------------------------
src/nhl_scrabble/cli.py                  114     16      20       4  85.07%  168, 199-201
```

**XML report (for CI)**:

```bash
pytest --cov --cov-report=xml
```

## Using the Makefile

Convenient shortcuts:

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run tox
make tox

# Run tox in parallel
make tox-parallel

# Run all quality checks + tests
make check
```

## Continuous Integration

Our CI runs:

```bash
# Pre-commit hooks
pre-commit run --all-files

# Tests on multiple Python versions
tox -e py312,py313,py314,py315

# Coverage check
pytest --cov --cov-fail-under=80

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

Simulate CI locally:

```bash
make ci
```

## Test Structure

```
tests/
├── unit/                      # Fast, isolated unit tests
│   ├── test_scrabble.py       # Scoring logic
│   ├── test_team_processor.py # Business logic
│   └── test_models.py         # Data models
├── integration/               # Integration tests
│   ├── test_cli.py            # CLI integration
│   └── test_api_client.py     # NHL API integration
└── conftest.py                # Shared fixtures
```

## Writing Tests

**Test naming convention**:

```python
def test_<function>_<scenario>_<expected>():
    """Test that function does expected thing in scenario."""
    # Arrange
    scorer = ScrabbleScorer()

    # Act
    result = scorer.calculate_score("test")

    # Assert
    assert result == 4
```

**Use fixtures**:

```python
@pytest.fixture
def scorer():
    """Reusable scorer instance."""
    return ScrabbleScorer()


def test_with_fixture(scorer):
    """Test using fixture."""
    assert scorer.calculate_score("test") == 4
```

**Parametrize tests**:

```python
@pytest.mark.parametrize(
    "name,expected",
    [
        ("A", 1),
        ("Z", 10),
        ("TEST", 4),
    ],
)
def test_scores(name, expected):
    """Test multiple inputs."""
    scorer = ScrabbleScorer()
    assert scorer.calculate_score(name) == expected
```

## Troubleshooting

### Issue: "No module named 'nhl_scrabble'"

**Solution**: Install in editable mode:

```bash
pip install -e .
```

### Issue: "Fixture not found"

**Solution**: Check `conftest.py` or import statement.

### Issue: Tests pass locally but fail in CI

**Solution**: Run tox to test multiple Python versions:

```bash
tox -e py312,py313,py314,py315
```

### Issue: Slow tests

**Solution**: Run unit tests only:

```bash
pytest tests/unit/ -v
```

Or use pytest-xdist for parallel execution:

```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

### Issue: Import errors

**Solution**: Ensure you're in the virtual environment:

```bash
source .venv/bin/activate
which python  # Should point to .venv/bin/python
```

## Performance Tips

1. **Run specific tests** during development instead of full suite
1. **Use pytest-xdist** for parallel execution (`pytest -n auto`)
1. **Skip slow tests** during iteration (`pytest -m "not slow"`)
1. **Use tox-uv** for 10x faster tox runs (automatic in this project)
1. **Watch mode** for continuous testing (`ptw`)

## Related

- [First Contribution Tutorial](../tutorials/03-first-contribution.md) - Testing workflow
- [Tox Reference](../../docs/TOX.md) - Tox configuration details
- [Coverage Requirements](../reference/coverage.md) - Coverage standards
- [Contributing Guide](../../CONTRIBUTING.md) - Testing guidelines
