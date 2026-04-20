# Contributing to NHL Scrabble

Thank you for your interest in contributing to NHL Scrabble! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We're here to have fun analyzing hockey data with Scrabble scores!

## Getting Started

### Development Environment Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/nhl-scrabble.git
cd nhl-scrabble
```

2. **Quick Setup (Recommended)**

```bash
# Initialize development environment
make init

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Note:** UV acceleration is automatic when using tox (via tox-uv plugin).

3. **Manual Setup (Alternative)**

```bash
# Create virtual environment
python -m venv .venv

# Activate environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Branch Protection and PR Requirements

**⚠️ IMPORTANT: The main branch is protected**

- ❌ Direct commits to main are **blocked**
- ✅ All changes must go through Pull Requests
- ✅ All CI checks must pass before merge
- ✅ All conversations must be resolved
- ✅ Only squash merging is allowed

**Required CI Checks:**

- Pre-commit hooks (54 hooks)
- Python 3.10 tests
- Python 3.11 tests
- Python 3.12 tests
- Python 3.13 tests
- Python 3.14 tests
- Python 3.15-dev tests (experimental, non-blocking)
- All tox environments (31 environments)

**Before creating a PR:**

1. Ensure all tests pass locally: `pytest`
1. Run pre-commit hooks: `pre-commit run --all-files`
1. Check type hints: `mypy src`
1. Verify code quality: `make check`

**The pre-commit hook will warn you if attempting to commit directly to main**, but GitHub branch protection provides an additional safeguard.

#### Admin Commits to Main (Maintainers Only)

**IMPORTANT**: If you have admin permissions and need to bypass branch protection to commit directly to `main`:

```bash
# ✅ CORRECT: Skip only the branch protection check
SKIP=check-branch-protection git commit -m "docs: Update task tracking"

# ❌ NEVER: This bypasses ALL quality checks
git commit --no-verify -m "message"
```

**Why this matters**:

- The `check-branch-protection` hook is a workflow reminder, not a quality check
- All 56 other hooks (ruff, mypy, black, bandit, security checks, etc.) **MUST always run**
- Quality checks prevent bugs, security issues, and maintain code standards
- Even admin commits must meet the same quality standards as PR commits

**Use cases for admin bypass**:

- Post-merge documentation updates
- Task tracking file updates
- Emergency hotfixes (quality checks still required!)

**Rule**: NEVER use `--no-verify` - Always run pre-commit hooks.

### Making Changes

1. **Write your code** following the project's style guidelines
1. **Add tests** for any new functionality
1. **Update documentation** if needed
1. **Run tests** to ensure everything works

### Testing

Run the full test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov --cov-report=html

# Run specific test file
pytest tests/unit/test_scrabble.py

# Run specific test
pytest tests/unit/test_scrabble.py::TestScrabbleScorer::test_calculate_score_basic
```

**Enhanced Test Output with pytest-sugar:**

The project includes pytest-sugar for improved test output with real-time progress bars, instant failure display, and colored results:

```bash
# pytest-sugar works automatically (no configuration needed)
pytest

# Enhanced features:
# - Real-time progress bar showing percentage completion
# - Colored output (✓ green for pass, ✗ red for fail)
# - Instant failure display (shows failures as they happen, not at end)
# - Cleaner, more compact output format

# Disable pytest-sugar if needed (for debugging)
pytest -p no:sugar
```

pytest-sugar auto-detects CI environments and falls back to plain output in non-interactive terminals, ensuring CI logs remain readable.

**Enhanced Assertion Diffs with pytest-clarity:**

The project includes pytest-clarity for improved assertion error output with better diff formatting and clearer visualization:

```bash
# pytest-clarity works automatically (no configuration needed)
pytest

# Enhanced features:
# - Clearer visual diffs with only changed values highlighted
# - Smart diff algorithms for nested structures (dicts, lists)
# - Character-level precision for string differences
# - Path annotations for nested differences
# - Less noise: unchanged values shown once, not duplicated

# Example: Dict difference
# Instead of showing the entire dict twice (- expected, + actual),
# pytest-clarity shows only the changed keys:
#
# E       Dict difference:
# E         {
# E           'team': 'TOR',
# E       -   'score': 100,  ← Expected
# E       +   'score': 105,  ← Actual
# E           'players': ['Matthews', 'Marner'],
# E         }

# Disable pytest-clarity if needed (rare)
pytest -p no:clarity
```

pytest-clarity works in CI environments (with or without colors) and is compatible with all other pytest plugins.

### Test Timeout Protection

The project uses pytest-timeout to prevent tests from hanging indefinitely and wasting CI resources:

```bash
# pytest-timeout works automatically (no configuration needed)
pytest
# Output: timeout: 10.0s, timeout method: thread

# Default timeout: 10 seconds for unit tests
# Tests exceeding timeout are automatically failed

# Override timeout for specific run (e.g., debugging)
pytest --timeout=60

# Disable timeout for debugging hung tests
pytest --timeout=0
```

**Timeout Configuration:**

- **Unit tests**: 10 seconds (default, configured in `pyproject.toml`)
- **Integration tests**: 300 seconds (5 minutes, marked with `@pytest.mark.timeout(300)`)
- **Slow tests**: 60 seconds (marked with `@pytest.mark.slow` and `@pytest.mark.timeout(60)`)

**Setting Custom Timeouts:**

```python
import pytest


# Override timeout for specific test
@pytest.mark.timeout(60)  # 1 minute timeout
def test_slow_operation():
    # Test that takes longer than default 10s
    pass


# Disable timeout for specific test (use sparingly)
@pytest.mark.timeout(0)
def test_that_must_complete():
    # Test with no timeout limit
    pass


# Module-level timeout for all tests in file
pytestmark = pytest.mark.timeout(300)  # 5 minutes for all tests
```

**Why timeout protection matters:**

- **Prevents wasted time**: No more waiting for hung tests
- **Saves CI minutes**: GitHub Actions charges for execution time
- **Better debugging**: Immediately identifies problematic tests
- **Professional workflow**: Production-grade testing infrastructure

**Common timeout scenarios:**

- Infinite loops in code under test
- Deadlocks in concurrent code
- API calls without timeouts
- External services that hang

**If a test times out:**

1. Check if the test legitimately needs more time (integration test, slow operation)
1. If so, add `@pytest.mark.timeout(N)` with appropriate timeout
1. If not, investigate why the test is hanging:
   - Add debugging output to see where it hangs
   - Run with increased timeout to see if it completes: `pytest --timeout=300`
   - Check for infinite loops, missing timeouts, or deadlocks
1. Fix the underlying issue rather than just increasing timeout

### Parallel Test Execution

The project uses pytest-xdist to run tests in parallel across multiple CPU cores, significantly speeding up test execution:

```bash
# pytest-xdist runs automatically (configured in pyproject.toml)
pytest
# Output: created: 8/8 workers (auto-detects CPU cores)

# Tests run in parallel with ~2.8x speedup on 8 cores
# 170 tests: 131s sequential → 47s parallel

# Explicit worker count (useful for limiting resources)
pytest -n 4     # Use 4 workers
pytest -n 2     # Use 2 workers (GitHub Actions runners)

# Disable parallel execution (for debugging)
pytest -n 0     # Run sequentially
```

**Performance Benefits:**

- **Faster feedback**: 2.8x faster locally (131s → 47s for 170 tests)
- **Better resource usage**: Utilizes all available CPU cores
- **CI optimization**: GitHub Actions runners use 2 workers
- **Scalability**: Test suite can grow without proportional time increase

**Parallel Execution Configuration:**

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "-n", "auto",  # Auto-detect CPU cores for parallel execution
    # ... other options
]
```

**Test Isolation:**

Most tests work seamlessly in parallel, but tests that modify shared state may need the `no_parallel` marker:

```python
import pytest


# Most tests work in parallel (no changes needed)
def test_isolated():
    scorer = ScrabbleScorer()  # Fresh instance per test
    assert scorer.calculate_score("TEST") == 4


# Tests that must run sequentially (rare)
@pytest.mark.no_parallel
def test_that_modifies_global_state():
    # Test that modifies shared resources
    pass
```

**When to use `@pytest.mark.no_parallel`:**

- Test modifies global state or environment variables
- Test uses shared external resources (databases, files with fixed paths)
- Test requires exclusive access to a resource (specific ports, locks)

**Coverage with Parallel Execution:**

pytest-cov has built-in support for pytest-xdist - coverage is collected from all workers and combined automatically:

```bash
pytest -n auto --cov=nhl_scrabble --cov-report=html
# Coverage: 93.25% (identical to sequential execution)
```

**Debugging Parallel Test Failures:**

```bash
# Step 1: Confirm it's a parallelization issue
pytest -n 0 tests/path/to/test.py  # If this passes, it's a parallel issue

# Step 2: Run with verbose output to see worker distribution
pytest -n auto -v

# Step 3: Add logging to understand the issue
pytest -n 2 -v -s  # -s shows print statements

# Step 4: Fix test isolation or mark as sequential
@pytest.mark.no_parallel  # If can't fix isolation
```

**CI/CD Optimization:**

GitHub Actions standard runners have 2 cores, so the CI workflow uses `-n 2` explicitly:

```yaml
# .github/workflows/ci.yml
- name: Run tests with coverage
  run: pytest -n 2 --cov --cov-report=xml --cov-report=term
```

Local development uses `-n auto` to maximize parallelization based on available cores.

### Test Randomization

The project uses pytest-randomly to randomize test execution order and catch hidden test dependencies:

```bash
# pytest-randomly works automatically (no configuration needed)
pytest
# Output: Using --randomly-seed=1234567890

# Reproduce exact same order (for debugging failures)
pytest --randomly-seed=1234567890

# Disable randomization temporarily (for debugging)
pytest -p no:randomly

# Set seed via environment variable
PYTEST_RANDOMLY_SEED=1234567890 pytest
```

**Why randomization matters:**

- **Catches hidden bugs**: Tests that depend on each other or shared global state
- **Improves test quality**: Forces proper test isolation with fixtures
- **Production reliability**: Order-dependent bugs won't surprise you in production

**If tests fail randomly:**

1. This is good! You found a hidden dependency
1. Note the seed from the output: `Using --randomly-seed=1234567890`
1. Reproduce: `pytest --randomly-seed=1234567890`
1. Debug and fix the hidden dependency (usually missing fixture or global state)
1. Re-run all tests to verify fix

**Common patterns that pytest-randomly catches:**

- Global state modified by tests
- Database records created by one test, used by another
- File system changes not cleaned up
- Shared singletons modified
- Module import side effects

**Best practices:**

- ✅ Use fixtures for test data setup
- ✅ Clean up after each test (use yield fixtures)
- ✅ Avoid global state in tests
- ❌ Don't use `@pytest.mark.randomly_disable` (fix the dependency instead)

### Multi-Environment Testing with Tox

For testing across multiple Python versions before submitting a PR:

```bash
# Test across Python 3.10, 3.11, 3.12, 3.13, 3.14, and 3.15 in parallel
tox -p auto

# Run quality checks only (fast)
tox -e quality

# Simulate the full CI pipeline
tox -e ci

# Test specific Python version
tox -e py310
tox -e py315

# Run specific tools
tox -e ruff-check
tox -e mypy
tox -e ruff-format
```

See [docs/TOX.md](docs/TOX.md) for complete tox documentation and [docs/TOX-UV.md](docs/TOX-UV.md) for tox with UV acceleration.

### Performance Benchmarking

The project uses pytest-benchmark to track performance and prevent performance regressions in critical code paths:

```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only -n 0

# Save baseline for future comparisons
pytest tests/benchmarks/ --benchmark-only -n 0 --benchmark-save=baseline

# Compare against baseline (detect regressions)
pytest tests/benchmarks/ --benchmark-only -n 0 --benchmark-compare=baseline

# Generate performance histogram
pytest tests/benchmarks/ --benchmark-only -n 0 --benchmark-histogram

# Via tox
tox -e benchmark              # Run benchmarks and save latest
tox -e benchmark-compare      # Compare against baseline
```

**Why -n 0?** Benchmarks require sequential execution (no parallel workers) for reliable timing measurements.

**Performance Targets:**

| Operation                          | Target (mean) | Threshold |
| ---------------------------------- | ------------- | --------- |
| **Scrabble score short name**      | \<100 ns      | +20%      |
| **Scrabble score long name**       | \<200 ns      | +20%      |
| **Score full roster (23 players)** | \<5 μs        | +20%      |
| **Score all teams (~700 players)** | \<100 μs      | +20%      |
| **Sort players by score**          | \<1 ms        | +20%      |
| **Aggregate by division**          | \<500 μs      | +20%      |

**Benchmark Configuration:**

- **Storage**: `.benchmarks/` directory (auto-created, git-ignored)
- **Regression threshold**: 20% (configurable in `pyproject.toml`)
- **Warmup**: 5 iterations before measurement
- **Statistical analysis**: min, max, mean, stddev, median, IQR, outliers

**When to Run Benchmarks:**

1. **Before optimizing**: Establish baseline to measure improvement
1. **After optimizing**: Verify optimization actually helped
1. **Before committing**: Ensure no performance regressions
1. **During code review**: Compare branch performance vs main

**Example Output:**

```
---------------------------------------------------------------------------------------------------------------- benchmark: 14 tests -----------------------------------------------------------------------------------------------------------------
Name (time in ns)                                   Min                       Max                      Mean                 StdDev                    Median                    IQR            Outliers             OPS            Rounds  Iterations
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_benchmark_short_name                      735.3956 (1.0)          2,146.3493 (1.0)            768.5196 (1.0)          57.2188 (1.0)            759.1443 (1.0)           3.9116 (1.0)    1685;13894  1,301,203.0086 (1.0)       64871          20
test_benchmark_full_league               1,910,574.2685 (>1000.0)  3,079,814.8364 (>1000.0)  1,984,307.0172 (>1000.0)  80,544.2540 (>1000.0)  1,967,393.5603 (>1000.0)  50,543.5746 (>1000.0)     24;19        503.9543 (0.00)        524           1
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

**Regression Detection:**

If your changes cause performance to degrade beyond the threshold (20%), the benchmark comparison will fail:

```bash
$ pytest tests/benchmarks/ --benchmark-compare=baseline

❌ FAILED: test_benchmark_full_league regression threshold exceeded
   Baseline: 1,910,574 ns
   Current:  2,342,129 ns
   Change:   +22.6% (threshold: 20%)
```

**Best Practices:**

- ✅ Run benchmarks sequentially (`-n 0`)
- ✅ Commit baselines with code
- ✅ Compare before/after optimizations
- ✅ Focus on critical paths (scoring, sorting, aggregation)
- ❌ Don't benchmark I/O operations (network, disk)
- ❌ Don't run benchmarks in parallel (`pytest -n auto` will auto-disable)

### Fast Package Management with UV

UV acceleration is automatic when using tox (via tox-uv plugin):

```bash
# Testing with automatic UV acceleration
make tox              # Uses UV automatically
make tox-parallel     # Even faster with parallel execution

# Standard package management
make install-dev      # Install dependencies
make update           # Update dependencies
```

See [docs/TOX-UV.md](docs/TOX-UV.md) for tox with UV acceleration.

### Code Quality

Before committing, ensure your code passes all quality checks:

```bash
# Format code with ruff
make ruff-format
# or directly: ruff format .

# Check for linting issues
make ruff-check
# or directly: ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Type check with mypy
make mypy
# or directly: mypy src

# Validate JSON/YAML files against schemas
tox -e check-jsonschema
# or directly: check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" .github/workflows/*.yml

# Run pre-commit hooks manually
pre-commit run --all-files

# Security scanning with bandit
make bandit
# or via tox: tox -e bandit

# Generate security reports
make security-report
# Reports saved to reports/ directory
```

### Security Scanning

The project uses two complementary security tools:

#### Bandit - Code Security Scanning

**Bandit** scans Python source code for security vulnerabilities:

```bash
# Quick security scan (MEDIUM+ severity/confidence)
make bandit

# Comprehensive security scan with bandit + safety
tox -e security

# Generate detailed HTML/JSON/TXT reports
make security-report
```

**What Bandit Detects:**

- **SQL Injection** (B201-B299): Unparameterized SQL queries
- **Hardcoded Secrets** (B301-B399): Passwords, API keys, tokens in code
- **Weak Cryptography** (B401-B499): MD5, SHA1, weak random generators
- **Shell Injection** (B501-B599): Unsafe subprocess calls with `shell=True`
- **Unsafe YAML** (B601-B699): `yaml.load()` vs `yaml.safe_load()`
- **Dangerous Functions** (B701-B799): `eval()`, `exec()`, `pickle`

**Handling False Positives:**

If bandit reports a false positive, add a `# nosec` comment with justification:

```python
# Safe: password from environment, not hardcoded
password = os.getenv("DATABASE_PASSWORD")  # nosec B105

# Safe: subprocess call with validated, trusted input
subprocess.run(["ls", validated_path], check=True)  # nosec B603
```

#### Safety - Dependency Vulnerability Scanning

**Safety** scans installed packages against CVE databases for known vulnerabilities:

```bash
# Quick dependency vulnerability scan
make safety

# Detailed safety scan with tox
tox -e safety

# Generate safety reports (JSON + TXT)
make safety-report
```

**What Safety Detects:**

- **Known CVEs**: Common Vulnerabilities and Exposures in dependencies
- **Security Advisories**: PyUP, NVD, and OSV vulnerability databases
- **Outdated Packages**: Dependencies with known security patches
- **Critical Vulnerabilities**: HIGH and CRITICAL severity issues

**Handling Known Vulnerabilities:**

If safety reports a vulnerability that is acceptable (disputed, test-only, mitigated), add it to `.safety-policy.yml`:

```yaml
security:
  ignore-cvs:
    - id: "51457"
      package: "py"
      reason: "DISPUTED CVE - ReDoS in test-only dependency, not in production"
      expires: "2026-07-20"  # Quarterly review
```

**Vulnerability Severity Levels:**

- **CRITICAL**: Immediate action required - blocks CI builds
- **HIGH**: Fix ASAP - plan remediation within sprint
- **MEDIUM**: Review and assess - document if acceptable
- **LOW**: Informational - assess risk and document decision

**Security Integration:**

- ✅ Pre-commit hooks: Bandit (code) + Safety (dependencies)
- ✅ CI/CD: Automated scanning on all PRs
- ✅ Artifact storage: JSON/TXT reports retained for 90 days
- ✅ Weekly scans: Scheduled security audits (Sundays 12 AM UTC)
- ✅ Auto-issue creation: Critical vulnerabilities create GitHub issues

### Commit Messages

Write clear, descriptive commit messages:

```
Add feature to export reports as CSV

- Implement CSVReporter class
- Add --format csv option to CLI
- Include tests for CSV generation
- Update documentation
```

Guidelines:

- Use present tense ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Provide detailed description in the body if needed
- Reference issues with `#issue-number`

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public modules, classes, and functions

### Docstring Format

Use Google-style docstrings:

```python
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name.

    Args:
        name: The name to score (can include spaces and special characters)

    Returns:
        The total Scrabble score (non-letter characters are worth 0 points)

    Raises:
        ValueError: If name is None

    Examples:
        >>> scorer = ScrabbleScorer()
        >>> scorer.calculate_score("ALEX")
        11
    """
    pass
```

### Type Hints

Always use type hints:

```python
# Good
def process_teams(teams: dict[str, TeamScore]) -> list[PlayerScore]:
    pass


# Bad
def process_teams(teams):
    pass
```

## Testing Guidelines

### Test Structure

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Name test files `test_*.py`
- Name test classes `Test*`
- Name test functions `test_*`

### Writing Tests

```python
class TestScrabbleScorer:
    """Tests for the ScrabbleScorer class."""

    def test_calculate_score_basic(self, scrabble_scorer: ScrabbleScorer) -> None:
        """Test basic score calculation."""
        assert scrabble_scorer.calculate_score("A") == 1
        assert scrabble_scorer.calculate_score("Z") == 10
```

### Test Coverage

- Aim for >80% overall coverage
- Critical modules should have >90% coverage
- All new features must include tests
- Bug fixes should include regression tests

### Diff Coverage (PR-Specific Coverage)

The project uses **diff-cover** to enforce test coverage on changed lines only in pull requests. This ensures new code is well-tested without requiring 100% coverage on existing code.

**What is Diff Coverage?**

- **Total Coverage**: Coverage across entire codebase (~50% currently)
- **Diff Coverage**: Coverage on lines changed in your PR (target: ≥80%)

**Why Both Matter:**

| Metric       | Total Coverage  | Diff Coverage      |
| ------------ | --------------- | ------------------ |
| **Scope**    | Entire codebase | Changed lines only |
| **Purpose**  | Overall health  | PR quality         |
| **Target**   | ~50% (current)  | ≥80% (enforced)    |
| **Enforced** | ⚠️ Optional     | ✅ Required in CI  |

**Local Usage:**

```bash
# Generate coverage report
pytest --cov=nhl_scrabble --cov-report=xml

# Check diff coverage against main branch
diff-cover coverage.xml --compare-branch=origin/main

# Output shows coverage on changed lines only:
# -------------
# Diff Coverage
# Diff: origin/main...HEAD, staged and unstaged changes
# -------------
# src/nhl_scrabble/api/nhl_client.py (100.0%)
# src/nhl_scrabble/processors/team_processor.py (85.7%)
# -------------
# Total: 42 lines
# Missing: 3 lines
# Coverage: 92.9%
# -------------

# With enforcement (fails if < 80%)
diff-cover coverage.xml --compare-branch=origin/main --fail-under=80

# Generate HTML report for detailed review
diff-cover coverage.xml --html-report=diff-cover.html
open diff-cover.html
```

**Via Tox:**

```bash
# Run diff coverage check (same as CI)
tox -e diff-cover

# This runs:
# 1. pytest --cov=nhl_scrabble --cov-report=xml
# 2. diff-cover coverage.xml --compare-branch=origin/main --fail-under=80
```

**CI Enforcement:**

⚠️ **Note**: diff-cover is currently a local development tool only. It is not yet enforced in CI due to git history limitations in GitHub Actions shallow clones. However, you should still run it locally to ensure your changes are well-tested.

To check diff coverage locally:

1. Run `tox -e diff-cover` or manually generate coverage and run diff-cover
1. Review which lines are missing coverage
1. Add tests for the uncovered lines
1. Re-run to verify ≥80% diff coverage before pushing

**Example Scenario:**

```
Your PR adds 50 new lines:
- 45 lines covered by tests
- 5 lines not covered

Total coverage: 50.4% (unchanged) ✓
Diff coverage: 90.0% (45/50) ✓

CI passes because diff coverage ≥ 80%
```

**Best Practices:**

- ✅ Run `diff-cover` locally before pushing
- ✅ Use HTML reports to see exactly which lines need tests
- ✅ Add tests for all new functionality
- ✅ Aim for ≥80% diff coverage on all changes
- ❌ Don't skip coverage on new code without good reason

**Configuration:**

Diff-cover is configured in `pyproject.toml`:

```toml
[tool.diff_cover]
compare_branch = "origin/main"
fail_under = 80.0
include_paths = ["src/"]
exclude_paths = ["tests/", "*/__main__.py"]
```

## Documentation

### Documentation Structure

We follow the [Diátaxis framework](https://diataxis.fr/) with four documentation types:

- **[Tutorials](docs/tutorials/)** - Learning-oriented lessons for beginners
- **[How-to Guides](docs/how-to/)** - Problem-oriented solutions to specific tasks
- **[Reference](docs/reference/)** - Technical specifications and API documentation
- **[Explanation](docs/explanation/)** - Conceptual understanding and background

**Online Documentation:** https://bdperkin.github.io/nhl-scrabble/

### Building Documentation

Build and view Sphinx documentation locally:

```bash
# Build HTML documentation
make docs

# Serve with auto-rebuild (recommended for development)
make serve-docs
# Visit http://localhost:8000

# Check documentation spelling
tox -e docs -- -b spelling

# Check all links
sphinx-build -b linkcheck docs docs/_build/linkcheck
```

### Updating Documentation

When adding new features:

1. **Add docstrings** to all new code (100% coverage required)
1. **Regenerate API/CLI docs** after docstring or CLI changes (see below)
1. **Create how-to guide** if it solves a specific problem
1. **Update reference** docs if adding new CLI options or configuration
1. **Write explanation** if introducing new concepts or design decisions
1. **Update `CHANGELOG.md`** with user-facing changes
1. **Update `CLAUDE.md`** if architecture changes
1. **Update `README.md`** if changing core functionality

### Regenerating Auto-Generated Documentation

The project automatically generates API and CLI reference documentation:

**After updating docstrings:**

```bash
make docs-api  # Regenerate API reference
```

**After changing CLI commands or options:**

```bash
make docs-cli  # Regenerate CLI reference
```

**Regenerate everything:**

```bash
make docs-gen  # Regenerate both API and CLI docs
```

**Check if docs are up-to-date:**

```bash
make docs-check  # Fails if you forgot to regenerate
```

**Important:**

- ✅ Always regenerate docs after changing docstrings or CLI
- ✅ Commit the generated documentation files
- ✅ CI will fail if generated docs are out of date
- ⚠️ Never manually edit `docs/reference/cli-generated.md` or files in `docs/reference/api/`

### Where to Add Documentation

**New feature**: Create a how-to guide in `docs/how-to/`

**New CLI option**: Auto-generated in `docs/reference/cli-generated.md` (run `make docs-cli`)

- Optionally update `docs/reference/cli.md` for usage patterns and examples

**New Python API**: Auto-generated in `docs/reference/api/` (run `make docs-api`)

- Ensure docstrings are complete (100% coverage enforced by interrogate)

**New configuration**: Update `docs/reference/configuration.md`

**Architecture change**: Update `docs/explanation/architecture.md`

**Beginner content**: Add to tutorials in `docs/tutorials/`

### Writing Documentation

- Use clear, concise language
- Include code examples that work
- Keep examples up-to-date
- Add links to related documentation
- Follow the Diátaxis framework (don't mix documentation types)
- Use consistent formatting and tone

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
1. ✅ Code coverage is maintained or improved
1. ✅ Code is formatted with ruff
1. ✅ No linting errors
1. ✅ Type checking passes
1. ✅ Documentation is updated
1. ✅ Commit messages are clear
1. ✅ Branch is up-to-date with main

### Submitting a Pull Request

1. **Push your branch**

```bash
git push origin feature/your-feature-name
```

2. **Create pull request** on GitHub

1. **Fill out the PR template** with:

   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

1. **Address review feedback**

   - Make requested changes
   - Push updates to your branch
   - Respond to comments

### PR Review Criteria

Pull requests will be reviewed for:

- **Functionality**: Does it work as intended?
- **Tests**: Are there adequate tests?
- **Code Quality**: Is the code clean and maintainable?
- **Documentation**: Is it properly documented?
- **Style**: Does it follow project conventions?
- **Performance**: Are there any performance concerns?

### Reviewing Dependabot Pull Requests

This project uses GitHub Dependabot to automatically create PRs for dependency updates. When reviewing Dependabot PRs:

#### For Security Updates (Immediate Action Required)

1. **Review the vulnerability**: Check the security advisory linked in the PR
1. **Verify the fix**: Ensure the updated version addresses the vulnerability
1. **Check compatibility**: Review changelog for breaking changes
1. **Run tests**: Ensure CI passes (automatic)
1. **Merge quickly**: Security updates should be merged promptly

**Example PR**: `deps(python): Bump requests from 2.31.0 to 2.31.1 [security]`

#### For Regular Updates (Review Weekly)

Dependabot groups related updates to reduce noise:

- **Development dependencies**: Grouped minor/patch updates
- **Production dependencies**: Grouped patch updates
- **GitHub Actions**: Grouped workflow updates

**Review process**:

1. **Check the changelog**: Review what changed in each dependency
1. **Verify tests pass**: CI must be green
1. **Check for breaking changes**: Review major version bumps carefully
1. **Test locally if needed**: For significant updates, test locally
1. **Merge**: If tests pass and no issues, merge

**Automated checks**:

- ✅ All tests run automatically
- ✅ Pre-commit hooks verify code quality
- ✅ Type checking runs
- ✅ Coverage is maintained

**When to reject**:

- ❌ Tests fail
- ❌ Breaking changes without migration path
- ❌ Known issues with new version
- ❌ Requires significant refactoring

**Labels on Dependabot PRs**:

- `dependencies` - All dependency updates
- `python` - Python package updates
- `github-actions` - GitHub Actions updates
- `security` - Security-related updates (auto-added by GitHub)

**Commit message format**:

Dependabot PRs use conventional commits:

- `deps(python): Bump package from X to Y`
- `ci: Update GitHub Actions to v2`

## Common Tasks

### Adding a New Report Type

1. Create new reporter class in `src/nhl_scrabble/reports/`
1. Inherit from `BaseReporter`
1. Implement `generate()` method
1. Add to `__init__.py` exports
1. Integrate into CLI
1. Add tests
1. Update documentation

### Adding a New Configuration Option

1. Add field to `Config` dataclass in `config.py`
1. Add environment variable parsing in `from_env()`
1. Add CLI option in `cli.py`
1. Update documentation
1. Add tests

### Fixing a Bug

1. Create issue on GitHub (if not exists)
1. Write a failing test that reproduces the bug
1. Fix the bug
1. Verify test now passes
1. Add regression test
1. Submit PR referencing the issue

## Release Process

(For maintainers)

1. Update version in `src/nhl_scrabble/__init__.py` and `pyproject.toml`
1. Update `CHANGELOG.md`
1. Create git tag: `git tag -a v2.0.0 -m "Release v2.0.0"`
1. Push tag: `git push origin v2.0.0`
1. Create GitHub release with notes
1. (Optional) Publish to PyPI

## Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for questions or ideas
- Check existing issues/discussions first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

### Dependency License Policy

When adding new dependencies, ensure they use licenses compatible with our MIT license:

**Runtime Dependencies** (distributed with the package):

- ✅ **Allowed**: MIT, Apache 2.0, BSD (2-clause, 3-clause), ISC, PSF, MPL-2.0, Unlicense, Public Domain
- ❌ **Prohibited**: GPL, LGPL, AGPL (copyleft), Proprietary

**Development Dependencies** (build/test tools only):

- More flexible, but document any non-permissive licenses with justification
- LGPL is acceptable for dev-only tools (e.g., spell checkers, documentation generators)
- Must not be distributed with or statically linked into the package

**Verification**:

Before committing new dependencies, verify license compliance:

```bash
# Check all licenses
tox -e licenses

# Add to pyproject.toml
# Then update lock file
uv lock

# Re-check licenses
tox -e licenses
```

CI will automatically fail if prohibited licenses are detected in runtime dependencies.

______________________________________________________________________

Thank you for contributing to NHL Scrabble! 🏒🎯

## Using the Makefile

The project includes a comprehensive Makefile that automates common development tasks.

### Quick Reference

```bash
# Setup
make init              # Initialize development environment
make venv              # Create virtual environment only
make install-dev       # Install with dev dependencies
make install-hooks     # Install pre-commit hooks

# Development
make test              # Run all tests
make test-cov          # Run tests with coverage
make ruff-check        # Run linter
make ruff-format       # Format code
make mypy              # Type check
make check             # Run all checks before commit

# Cleaning
make clean             # Clean all artifacts
make clean-all         # Clean everything including venv

# Building
make build             # Build distribution packages
make ci                # Simulate CI pipeline locally
```

See [docs/MAKEFILE.md](docs/MAKEFILE.md) for complete documentation of all 55 targets.

### Recommended Workflow

1. **First time setup:**

   ```bash
   make init
   source .venv/bin/activate
   ```

1. **Before starting work:**

   ```bash
   make update
   ```

1. **During development:**

   ```bash
   make test-watch  # Keep running in a terminal
   ```

1. **Before committing:**

   ```bash
   make check
   ```

1. **Before creating a PR:**

   ```bash
   make ci
   ```
