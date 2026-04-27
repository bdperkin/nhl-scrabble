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

**Note:** [UV](https://docs.astral.sh/uv/) acceleration is automatic when using [tox](https://tox.wiki/) (via [tox-uv](https://github.com/tox-dev/tox-uv) plugin).

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

### Python Version Support

The project supports [Python](https://www.python.org/) 3.12 through 3.14. We also test against Python 3.15-dev to ensure forward compatibility, but this version is experimental and may fail CI checks without blocking merges.

**Local Development:**

Use Python 3.14 for local development (see `.python-version`). To test other versions, use tox:

```bash
tox -e py312  # Test Python 3.12
tox -e py313  # Test Python 3.13
tox -e py314  # Test Python 3.14
tox -e py315  # Test Python 3.15-dev (experimental)
```

**CI Testing:**

All PRs are tested on Python 3.12-3.14 (required to pass). Python 3.15-dev tests run but failures don't block merges.

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

- Pre-commit hooks (60 hooks)
- Python 3.12 tests
- Python 3.13 tests
- Python 3.14 tests
- Python 3.15-dev tests (experimental, non-blocking)
- All tox environments (32 environments)

**Before creating a PR:**

**Option 1: Automated Pre-Flight Validation** (Recommended)

Use the `/implement-task` skill which automatically validates before pushing:

- ✅ Runs all 65 pre-commit hooks automatically
- ✅ Runs all tox environments (py3.12-3.15, ruff, mypy, coverage)
- ✅ Only pushes if all validation passes
- ✅ Provides clear success/failure reporting
- ✅ Saves 10-15 minutes per PR by catching issues locally
- ✅ ~95% first-time CI pass rate

**Time investment**: 3-5 minutes
**Time saved**: 10-15 minutes per avoided CI failure cycle

**Option 2: Manual Validation** (Traditional)

1. Ensure all tests pass locally: `pytest`
1. Run pre-commit hooks: `pre-commit run --all-files`
1. Check type hints: `mypy src`
1. Verify code quality: `make check`
1. Run tox environments: `tox -p auto`

**Option 3: Quick Push** (High Risk)

Push without validation - **NOT recommended** as ~30% of PRs fail CI on first run.

**Comparison**:

| Approach      | Time     | CI Pass Rate | Notes                   |
| ------------- | -------- | ------------ | ----------------------- |
| Automated     | 3-5 min  | ~95%         | Recommended, consistent |
| Manual        | 5-10 min | ~90%         | Easy to forget steps    |
| No validation | 0 min    | ~70%         | High failure rate       |

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
- All 59 other hooks (ruff, mypy, black, bandit, security checks, pyupgrade, etc.) **MUST always run**
- Quality checks prevent bugs, security issues, and maintain code standards
- Even admin commits must meet the same quality standards as PR commits

**Use cases for admin bypass**:

- Post-merge documentation updates
- Task tracking file updates
- Emergency hotfixes (quality checks still required!)

**Rule**: NEVER use `--no-verify` - Always run pre-commit hooks.

### Git Branch Cleanup

The repository uses automated branch cleanup to maintain a clean git state and reduce clutter in branch listings.

**Automatic Remote Pruning:**

The repository is configured with `git config fetch.prune true`, which means every `git fetch` automatically removes stale remote tracking branches (branches that were deleted on GitHub).

**Manual Local Branch Cleanup:**

After a PR is merged, the remote branch is automatically deleted by GitHub, but your local branch remains. Use the Makefile targets to clean up:

```bash
# Check branch status (merged vs active)
make git-status-branches

# Prune local merged branches (with confirmation)
make git-prune-local

# Prune remote tracking refs
make git-prune-remote-refs

# Prune branches from closed (not merged) PRs (with confirmation)
make git-prune-closed-prs

# Standard cleanup (remote refs + merged branches)
make git-cleanup

# Complete cleanup (remote refs + merged branches + closed PRs)
make git-cleanup-all
```

**Two Types of Branch Cleanup:**

1. **Merged Branches** (`make git-prune-local`)

   - Branches fully merged to main
   - Safe deletion with `git branch -d`
   - No work is lost (already in main)

1. **Closed PR Branches** (`make git-prune-closed-prs`)

   - Branches from PRs that were closed without merging
   - Work may have been redone in another PR
   - Deletes BOTH local branches (`git branch -D`) AND remote branches (`git push origin --delete`)
   - **Warning**: Permanently deletes unmerged work from local AND remote

**Typical Workflow After PR Merge:**

1. GitHub auto-deletes remote branch (when PR merged)
1. Run `git fetch --prune` to update local refs (automatic with fetch.prune = true)
1. Run `make git-prune-local` to delete local merged branch
1. Or run `make git-cleanup` for complete cleanup

**Typical Workflow for Closed PRs:**

1. PR closed without merging (work abandoned or redone elsewhere)
1. Remote branch may still exist on GitHub
1. Run `make git-prune-closed-prs` to delete BOTH local and remote orphaned branches
1. Verify you don't need any changes before confirming deletion (deletes from GitHub!)

**Safety Features:**

- **Merged branches**: Only deletes fully merged branches (`git branch -d`), local only
- **Closed PR branches**: Warns before force deletion, requires confirmation, deletes BOTH local and remote
- Never deletes the main branch
- Never deletes your current branch
- Confirmation prompts before all deletions
- GitHub CLI integration to verify PR status
- Clear warnings when remote branches will be deleted from GitHub

**Recommended Cleanup Schedule:**

- **After each PR merge**: `git fetch --prune` (happens automatically)
- **Weekly**: `make git-status-branches` to check status
- **Monthly**: `make git-cleanup` for full cleanup
- **Before releases**: Full repository cleanup

**Recovery from Accidental Deletion:**

If you accidentally delete a branch, you can recover it within 30 days:

```bash
# Find the commit hash
git reflog

# Recreate the branch
git branch branch-name <commit-hash>
```

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

The project includes [pytest-sugar](https://github.com/Teemu/pytest-sugar) for improved test output with real-time progress bars, instant failure display, and colored results:

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

The project includes [pytest-clarity](https://github.com/darrenburns/pytest-clarity) for improved assertion error output with better diff formatting and clearer visualization:

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

The project uses [pytest-timeout](https://github.com/pytest-dev/pytest-timeout) to prevent tests from hanging indefinitely and wasting CI resources:

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

The project uses [pytest-xdist](https://pytest-xdist.readthedocs.io/) to run tests in parallel across multiple CPU cores, significantly speeding up test execution:

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
  "-n",
  "auto", # Auto-detect CPU cores for parallel execution
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

The project uses [pytest-randomly](https://github.com/pytest-dev/pytest-randomly) to randomize test execution order and catch hidden test dependencies:

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

The project uses tox with intelligent parallel execution and fail-fast behavior:

#### Default Behavior

```bash
make tox  # Parallel execution with tier-based dependencies
```

Execution tiers:

1. **Fast quality checks** (ruff, flake8) - fail immediately if code quality issues
1. **Type checking** (mypy, isort, interrogate) - only runs if tier 1 passes
1. **Tests** (py312-314) - parallel across Python versions, only if tier 2 passes
1. **Coverage** - only runs if all tests pass

#### Execution Modes

```bash
make tox              # Default: parallel with fail-fast dependencies
make tox-parallel     # Pure parallel (all environments)
make tox-sequential   # Sequential (for debugging)
make tox-quick        # Critical checks only (fast fail-fast)

# Run specific tier
tox -m critical       # Fast quality checks only
tox -m quality        # All quality checks
tox -m test          # Just tests
tox -m coverage      # Coverage only

# Test specific Python version
tox -e py312
tox -e py315

# Run specific tools
tox -e ruff-check
tox -e mypy
tox -e ruff-format
```

#### Fail-Fast Behavior

- **Local**: Dependencies ensure tier-based fail-fast
- **CI**: GitHub Actions fail-fast stops all jobs if one fails
- **Debugging**: Use `make tox-sequential` to see all failures

See [docs/TOX.md](docs/TOX.md) for complete tox documentation and [docs/TOX-UV.md](docs/TOX-UV.md) for tox with UV acceleration.

### Performance Benchmarking

The project uses [pytest-benchmark](https://pytest-benchmark.readthedocs.io/) to track performance and prevent performance regressions in critical code paths:

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

# Type check with ty (Astral's fast type checker - validation mode)
make ty
# or directly: ty check src

# Comprehensive type checking (ty + mypy)
make type-check

# Format pyproject.toml configuration file
make pyproject-fmt
# or via tox: tox -e pyproject-fmt
# or directly: pyproject-fmt pyproject.toml
# Note: pyproject.toml is automatically formatted on commit via pre-commit hook

# Modernize Python syntax with pyupgrade
tox -e pyupgrade
# or directly: pyupgrade --py312-plus $(find src tests -name "*.py")

# Sort Python class members and statements
make ssort-check
# or via tox: tox -e ssort
# Apply sorting: make ssort-apply or tox -e ssort-apply

# Validate JSON/YAML files against schemas
make validate-json
# or via tox: tox -e check-jsonschema
# or directly: check-jsonschema --schemafile "https://json.schemastore.org/github-workflow.json" .github/workflows/*.yml

# Lint and format HTML/Jinja2 templates with djlint
make djlint
# or via tox: tox -e djlint (check + reformat)
# or via tox: tox -e djlint-check (check only, no formatting)
# or directly: djlint src/ --profile=jinja --lint --check
# Apply formatting: djlint src/ --profile=jinja --reformat

# Run pre-commit hooks manually
pre-commit run --all-files

# Security scanning with bandit
make bandit
# or via tox: tox -e bandit

# Generate security reports
make security-report
# Reports saved to reports/ directory
```

### Python Syntax Modernization

The project uses **[pyupgrade](https://github.com/asottile/pyupgrade)** to automatically modernize Python syntax to leverage features from Python 3.12+ (our minimum supported version):

```bash
# Check and modernize syntax (via tox)
tox -e pyupgrade

# Run directly on all Python files
pyupgrade --py312-plus $(find src tests -name "*.py")

# Pre-commit hook runs automatically
pre-commit run pyupgrade --all-files
```

**What pyupgrade does:**

- **PEP 604**: `Optional[str]` → `str | None`, `Union[int, str]` → `int | str`
- **PEP 585**: `List[int]` → `list[int]`, `Dict[str, int]` → `dict[str, int]`
- **String formatting**: `"{}".format(x)` → `f"{x}"`
- **Remove unnecessary imports**: Obsolete `from typing import List, Dict, Optional, Union`
- **Clean up**: Remove unnecessary `__future__` imports for Python 3.12+

**Example transformation:**

```python
# Before
from typing import Optional, Union, List, Dict


def get_player(name: str) -> Optional[Dict[str, Union[int, str]]]:
    players: List[str] = fetch_players()
    return players.get(name)


# After (pyupgrade --py312-plus)
def get_player(name: str) -> dict[str, int | str] | None:
    players: list[str] = fetch_players()
    return players.get(name)
```

**Benefits:**

- ✅ **Cleaner syntax**: Modern Python idioms are more readable
- ✅ **Fewer imports**: No need for `typing.List`, `Dict`, `Optional`, `Union`
- ✅ **Automatic**: Runs on every commit via pre-commit hook
- ✅ **Safe**: Only syntax changes, no logic changes
- ✅ **Educational**: Learn modern Python patterns automatically

**Integration:**

- **Pre-commit**: Runs on every commit (configured in `.pre-commit-config.yaml`)
- **Tox**: `tox -e pyupgrade` for manual runs
- **CI**: Runs on all PRs via GitHub Actions

**Why Python 3.12+ syntax?**

The project requires Python 3.12+ (`requires-python = ">=3.12"`), so we can safely use all Python 3.12+ features. pyupgrade ensures our codebase consistently uses the latest syntax patterns available in our minimum Python version.

### Python Code Modernization

The project uses **[refurb](https://github.com/dosisod/refurb)** to detect Python code that can be simplified or modernized using Python 3.12+ features. While pyupgrade handles **syntax** modernization, refurb handles **semantic** modernization - suggesting better ways to structure code:

```bash
# Run refurb to see modernization suggestions
make refurb

# Generate detailed modernization reports
make refurb-report

# Pre-commit hook runs automatically (warning mode - non-blocking)
pre-commit run refurb --all-files

# Via tox
tox -e refurb
```

**What refurb detects:**

- **pathlib usage**: `os.path.join()` → `Path() / ...`, `open().read()` → `Path().read_text()`
- **Modern f-strings**: More readable string formatting patterns
- **Dictionary merging**: `{**a, **b}` → `a | b` (Python 3.9+)
- **List comprehensions**: Replace append loops with comprehensions
- **contextlib.suppress()**: Replace empty try-except with `with suppress(...)`
- **operator.itemgetter()**: Replace lambda with itemgetter for sorting
- **Tuple vs list in membership tests**: `in [x, y]` → `in (x, y)` (faster)
- **Chained assignments**: Simplify repeated assignments
- **Dataclass opportunities**: Suggest @dataclass for simple data containers

**Example transformations:**

```python
# Before
import os

path = os.path.join("dir", "file.txt")
with open(path) as f:
    content = f.read()

# After (refurb suggestion)
from pathlib import Path

path = Path("dir") / "file.txt"
content = path.read_text()

# ---

# Before
result = []
for item in items:
    if condition(item):
        result.append(transform(item))

# After (refurb suggestion)
result = [transform(item) for item in items if condition(item)]

# ---

# Before
try:
    do_something()
except ValueError:
    pass

# After (refurb suggestion)
from contextlib import suppress

with suppress(ValueError):
    do_something()
```

**Benefits:**

- ✅ **Better patterns**: Learn modern Python idioms
- ✅ **More readable**: pathlib and comprehensions are clearer
- ✅ **Better performance**: Tuples in membership tests are faster than lists
- ✅ **Educational**: See suggestions on every commit (warning mode)
- ✅ **Non-blocking**: Currently in warning mode - doesn't prevent commits

**Integration:**

- **Pre-commit**: Shows suggestions on every commit (warning mode, non-blocking)
- **Tox**: `tox -e refurb` for detailed scanning
- **CI**: Runs on all PRs (experimental, non-blocking)
- **Makefile**: `make refurb` and `make refurb-report` for reports

**Warning Mode:**

refurb is currently in **warning mode** - it shows modernization suggestions but doesn't block commits. This allows the team to learn modern patterns without pressure. Use suggestions as learning opportunities.

**When to ignore refurb suggestions:**

- **Performance-critical code**: pathlib has slight overhead vs os.path
- **External API requirements**: Some APIs require string paths, not Path objects
- **Complex logic**: Some patterns are clearer without comprehensions
- **Intentional patterns**: Sometimes explicit is better than implicit

**Complementary to pyupgrade:**

| Tool      | Focus                      | Example                                           |
| --------- | -------------------------- | ------------------------------------------------- |
| pyupgrade | **Syntax** modernization   | `Optional[str]` → `str \| None`                   |
| refurb    | **Semantic** modernization | `os.path.join()` → `Path() / ...`                 |
| ruff      | **Linting** & style        | Code quality, PEP 8, best practices               |
| mypy      | **Type checking**          | Verify type hints are correct                     |
| ty        | **Fast type checking**     | Same as mypy but 10-100x faster (validation mode) |

All tools work together to maintain high code quality!

### HTML/Template Linting and Formatting

The project uses **[djlint](https://github.com/Riverside-Healthcare/djLint)** to lint and format HTML templates with Jinja2 syntax, ensuring consistent formatting and catching template errors before runtime:

```bash
# Lint templates (check only)
djlint src/ --profile=jinja --lint --check

# Format templates (reformat)
djlint src/ --profile=jinja --reformat

# Via tox (recommended)
tox -e djlint-check  # Check only (CI-friendly)
tox -e djlint        # Check + reformat

# Pre-commit hooks run automatically
pre-commit run djlint-jinja --all-files            # Check only
pre-commit run djlint-reformat-jinja --all-files   # Reformat
```

**What djlint does:**

- **Template syntax validation**: Ensures Jinja2 syntax is correct
- **HTML structure validation**: Validates HTML5 structure (W3C rules)
- **Consistent formatting**: Auto-formats HTML and embedded CSS/JS
- **Accessibility checks**: Detects missing alt text, ARIA issues
- **Error prevention**: Catches template errors before runtime

**Example output:**

```bash
$ djlint src/nhl_scrabble/templates/report.html --profile=jinja --lint

Linting report.html
--------------------
H006 5:4 Img tag without alt attribute.
T001 12:8 Variables should be wrapped in whitespace. {{ var }}

2 files linted, 2 errors found.
```

**Configuration** (in `pyproject.toml`):

```toml
[tool.djlint]
profile = "jinja"               # Jinja2 template syntax
indent = 4                      # Match Python indentation
max_line_length = 120           # Reasonable line length
format_css = true               # Format <style> blocks
format_js = true                # Format <script> blocks
ignore = "H021,J004,J018,T003"  # Project-specific exceptions
```

**Ignored rules** (with justification):

| Rule | Description                | Why Ignored                              |
| ---- | -------------------------- | ---------------------------------------- |
| H021 | Inline styles              | Acceptable for single-file templates     |
| H023 | Entity references (©)      | Standard HTML entities are readable      |
| J004 | Static URLs - url_for()    | Not using Flask's static helper          |
| J018 | Internal links - url_for() | Direct URLs are intentional              |
| T003 | Endblock names             | Optional style, blocks are small & clear |
| T028 | Spaceless tags             | Minor style preference, no functionality |

**Benefits:**

- ✅ **Runtime error prevention**: Catch template errors before they render
- ✅ **Consistent formatting**: All templates follow same style
- ✅ **Accessibility**: Automated detection of accessibility issues
- ✅ **Fast**: Lints 100 templates in ~1 second
- ✅ **Automatic**: Runs on every commit via pre-commit hook

**Integration:**

- **Pre-commit**: Runs on every commit (`.pre-commit-config.yaml`)
- **Tox**: `tox -e djlint-check` for CI, `tox -e djlint` for development
- **CI**: Runs on all PRs via GitHub Actions (via tox)

**When to use:**

- Before committing template changes
- When adding new HTML templates
- To enforce consistent template style
- To catch accessibility issues early

**Template file patterns:**

djlint automatically detects files matching: `*.html`, `*.jinja`, `*.jinja2`

### JSON/YAML Schema Validation

The project uses **[check-jsonschema](https://github.com/python-jsonschema/check-jsonschema)** to validate configuration files against official JSON schemas, ensuring all configs are syntactically correct and follow best practices:

```bash
# Validate all JSON/YAML configuration files
make validate-json

# Or via tox
tox -e check-jsonschema

# Validate specific files directly
check-jsonschema --schemafile https://json.schemastore.org/codecov.json .codecov.yml
check-jsonschema --schemafile https://json.schemastore.org/pre-commit-config.json .pre-commit-config.yaml
```

**Files Validated:**

| File                      | Schema                   | Purpose                        |
| ------------------------- | ------------------------ | ------------------------------ |
| `.github/workflows/*.yml` | `github-workflow.json`   | GitHub Actions workflows       |
| `.github/dependabot.yml`  | `dependabot-2.0.json`    | Dependabot configuration       |
| `.codecov.yml`            | `codecov.json`           | Codecov coverage configuration |
| `.pre-commit-config.yaml` | `pre-commit-config.json` | Pre-commit hooks configuration |

**Benefits:**

- ✅ **Early Error Detection**: Catch config errors before they cause CI failures
- ✅ **IDE Support**: Many IDEs use schemas for autocomplete and inline validation
- ✅ **Documentation**: Schema provides authoritative reference for valid config options
- ✅ **Type Checking**: Validates field types (string vs number, required vs optional)
- ✅ **Prevents Typos**: Field names validated against schema

**Common Schema Errors:**

```yaml
# Error: Missing required field
repos: []  # Required for .pre-commit-config.yaml

# Error: Invalid field type
coverage:
  minimum_coverage: "90%"  # Should be number, not string
# Fix:
coverage:
  minimum_coverage: 90

# Error: Unknown field
unknown_field: value  # Not in schema
# Fix: Remove unknown field or check schema documentation
```

**Integration:**

- **Pre-commit**: Validates on every commit (4 hooks in `.pre-commit-config.yaml`)
- **Tox**: `tox -e check-jsonschema` for manual validation
- **Makefile**: `make validate-json` for quick validation
- **CI**: Runs on all PRs via GitHub Actions

**Troubleshooting:**

If schema validation fails:

1. Read the error message carefully - it shows the field and issue
1. Check the schema documentation at [schemastore.org](https://schemastore.org/json/)
1. Validate locally: `make validate-json` to see detailed errors
1. Fix the config file based on schema requirements
1. Re-run validation to confirm fix

**Schema Sources:**

All schemas from [SchemaStore.org](https://schemastore.org/json/) - community-maintained JSON schemas for 700+ configuration file formats.

### Security Scanning

The project uses two complementary security tools:

#### Bandit - Code Security Scanning

**[Bandit](https://bandit.readthedocs.io/)** scans Python source code for security vulnerabilities:

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

**[Safety](https://pyup.io/safety/)** scans installed packages against CVE databases for known vulnerabilities:

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
    - id: '51457'
      package: py
      reason: DISPUTED CVE - ReDoS in test-only dependency, not in production
      expires: '2026-07-20'  # Quarterly review
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

Write clear, descriptive commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat(reports): Add CSV export functionality

Implement CSVReporter class with support for team and player data export.
Add --format csv CLI option and comprehensive tests for CSV generation.
Update documentation with CSV export examples.

Closes #123
```

**Format Requirements** (enforced by gitlint):

- **Title**: 5-100 characters, format: `type(scope): description`
  - Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`
  - Scope: Optional module/component (e.g., `api`, `cli`, `reports`)
  - Description: Clear summary of the change
- **Body**: Minimum 10 characters total, max 100 characters per line
  - Explain WHY the change was made, not just WHAT changed
  - Include motivation, context, and implementation details
  - Reference related issues with `Closes #123` or `Fixes #456`
- **Present tense**: "Add feature" not "Added feature"

**Good Examples**:

```
✅ feat(api): Add caching to NHL API client

Implement request-level caching with 1-hour TTL to reduce API calls
and improve performance. Cache is stored in memory and cleared on
process restart.

Closes #42
```

```
✅ fix(cli): Validate output path before writing

Check that output directory exists and is writable before attempting
to write report files. Prevents cryptic IOError messages.

Fixes #87
```

```
✅ docs: Update installation instructions

Add UV installation instructions and update Python version requirements
to reflect 3.12+ support.
```

**Bad Examples**:

```
❌ "fix" - Title too short (< 5 characters)

❌ "Add support for multiple output formats including JSON, CSV, Excel, HTML, and XML with comprehensive formatting options"
   - Title too long (> 100 characters)

❌ "feat: Add feature" - Body missing (non-trivial change needs explanation)
```

**Note**: Commit messages are validated by [gitlint](https://jorisroovers.com/gitlint/) in pre-commit hooks and CI.
Bot commits may need `SKIP=gitlint git commit` if gitlint conflicts with automated formats.

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [type hints](https://docs.python.org/3/library/typing.html) for all function signatures
- Maximum line length: 100 characters
- Use descriptive variable names
- Add [docstrings](https://peps.python.org/pep-0257/) to all public modules, classes, and functions

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

### Class Member Ordering

The project uses [ssort](https://github.com/bwhmather/ssort) to automatically sort class members and module-level statements for consistency:

**Standard Order:**

1. **Dunder methods** (special methods like `__init__`, `__repr__`)
1. **Class methods** (`@classmethod` decorated)
1. **Static methods** (`@staticmethod` decorated)
1. **Properties** (`@property` decorated)
1. **Public methods** (regular methods, alphabetically)
1. **Private methods** (leading underscore, alphabetically)

**Example:**

```python
class Example:
    """Example class with proper member ordering."""

    def __init__(self, value: int):
        """Initialize with value."""
        self.value = value

    def __repr__(self) -> str:
        """String representation."""
        return f"Example({self.value})"

    @classmethod
    def from_string(cls, s: str) -> "Example":
        """Create instance from string."""
        return cls(int(s))

    @property
    def doubled(self) -> int:
        """Return doubled value."""
        return self.value * 2

    def increment(self) -> None:
        """Increment value."""
        self.value += 1

    def _internal_helper(self) -> int:
        """Private helper method."""
        return self.value + 1
```

**Usage:**

```bash
# Check what would change (dry run)
make ssort-check

# Apply sorting
make ssort-apply

# Or use tox
tox -e ssort         # Check mode
tox -e ssort-apply   # Apply sorting
```

**Note:** ssort runs automatically in pre-commit hooks. Files in `tests/fixtures/` and `migrations/` are excluded.

### Trailing Commas

The project uses [add-trailing-comma](https://github.com/asottile/add-trailing-comma) to automatically add trailing commas to multi-line Python structures. This improves git diffs by making adding/removing items single-line changes and reduces merge conflicts.

**Benefits:**

- **Better Git Diffs**: Adding an item = 1 line changed (not 2)
- **Fewer Merge Conflicts**: Independent changes merge cleanly
- **Consistent Style**: All multi-line structures have trailing commas

**Examples:**

```python
# Multi-line function call
result = function_name(
    arg1,
    arg2,
    arg3,  # Trailing comma added automatically
)

# Multi-line list
items = [
    "item1",
    "item2",
    "item3",  # Trailing comma added automatically
]

# Multi-line dict
config = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",  # Trailing comma added automatically
}
```

**Usage:**

```bash
# Check/apply trailing commas
make trailing-comma

# Or use tox
tox -e add-trailing-comma
```

**Note:** Trailing commas are automatically added by pre-commit hooks. No manual management needed!

## Logging Guidelines

Proper logging levels help maintain clean user output while providing detailed diagnostics for debugging.

### Log Level Criteria

**DEBUG** - Diagnostic information for developers (only shown with `--verbose`):

- Internal state changes ("Created dependencies", "Cache initialized")
- Configuration details ("Pool size: 10", "Timeout: 30s")
- Successful completion of internal operations ("Fetched 32 teams", "Processed team XYZ")
- Performance metrics ("Processed in 2.3s", "Cache hit rate: 95%")
- Cache hits/misses
- Detailed API request/response info
- Progress indicators for internal operations

**INFO** - User-facing, actionable information (always visible):

- Application lifecycle ("Starting analysis", "Processing complete")
- User configuration choices ("Using custom config", "Active filters")
- Output locations ("Report written to file.xlsx")
- Feature activation ("Interactive mode enabled")
- Important user decisions
- Confirmation of user-initiated actions

**WARNING** - Recoverable issues requiring user attention:

- Validation failures (with fallback behavior)
- API errors (with retry logic)
- Missing optional features
- Deprecation notices
- Data quality issues

**ERROR** - Unrecoverable issues preventing operation:

- Fatal errors preventing operation
- Configuration errors
- Permission errors
- Missing required resources
- API failures after retries

**CRITICAL** - System-level failures:

- Application crash scenarios
- Security violations
- Data corruption
- Unrecoverable system errors

### Decision Tree

When adding a log statement, ask:

1. **Is this about the user's action or result?**

   - YES → `INFO` (e.g., "Report written to file.xlsx")
   - NO → Continue to #2

1. **Is this about internal operation details?**

   - YES → `DEBUG` (e.g., "Fetched 32 teams from API")
   - NO → Continue to #3

1. **Is this a recoverable problem?**

   - YES → `WARNING` (e.g., "Invalid player name, using fallback")
   - NO → Continue to #4

1. **Is this a fatal error?**

   - YES → `ERROR` (e.g., "Cannot write output file")
   - NO → `DEBUG` (default for uncertain cases)

### Examples

**DEBUG** (diagnostic, verbose only):

```python
logger.debug("Created ScrabbleScorer with 26 letter values")
logger.debug(f"API request to {url} completed in {elapsed:.2f}s")
logger.debug(f"Cache hit for key {cache_key}")
logger.debug("Connection pool initialized with 10 connections")
logger.debug(f"Processed team {team_abbrev} (15/32)")
```

**INFO** (user-facing, always visible):

```python
logger.info(f"Starting NHL Scrabble analysis v{version}")
logger.info(f"Using custom scoring config from: {config_path}")
logger.info(f"Active filters: divisions=[Atlantic, Metropolitan]")
logger.info(f"Report written to {output_path}")
logger.info("Analysis complete: 32 teams, 700 players processed")
```

**WARNING** (issues with fallback):

```python
logger.warning(f"Invalid player name '{name}', using 'Unknown'")
logger.warning("API rate limit exceeded, retrying in 60s")
logger.warning("Cache expired, fetching fresh data")
logger.warning(f"Team {abbrev} roster unavailable, skipping")
```

**ERROR** (fatal issues):

```python
logger.error(f"Cannot write to {path}: Permission denied")
logger.error("API authentication failed: Invalid credentials")
logger.error("Required dependency 'requests' not installed")
logger.error(f"Failed to fetch team {abbrev} after {retries} attempts")
```

### Testing Your Logs

Before committing, test that log levels are appropriate:

```bash
# Non-verbose output should be clean (5-10 INFO messages)
nhl-scrabble analyze 2>&1 | tee /tmp/info-logs.txt
grep -c INFO /tmp/info-logs.txt  # Expect: 5-10 lines

# Verbose output should include diagnostics (50-100 messages)
nhl-scrabble analyze --verbose 2>&1 | tee /tmp/debug-logs.txt
grep -c DEBUG /tmp/debug-logs.txt  # Expect: 50-100 lines

# INFO messages should be user-facing
grep INFO /tmp/info-logs.txt  # Review: Are these all actionable for users?

# DEBUG messages should be diagnostic
grep DEBUG /tmp/debug-logs.txt  # Review: Are these internal details?
```

### Code Review Checklist

When reviewing logging statements:

- [ ] User-facing information uses `INFO`
- [ ] Internal diagnostics use `DEBUG`
- [ ] Recoverable issues use `WARNING`
- [ ] Fatal errors use `ERROR`
- [ ] Non-verbose output is clean (\<10 INFO messages for typical runs)
- [ ] Verbose output provides useful debugging details
- [ ] Log messages are clear and actionable
- [ ] Sensitive information is not logged (API keys, passwords, etc.)

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

### Flaky Test Retry Mechanisms

The project uses **[pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures)** to automatically retry flaky tests that may fail intermittently due to external dependencies, timing issues, or resource contention.

**When to Mark a Test as Flaky:**

Use the `@pytest.mark.flaky` decorator for tests that:

- Call external APIs or services
- Check external resources (links, files)
- Have timing-sensitive operations
- Involve database race conditions
- Depend on network conditions

**Retry Configuration:**

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

**When NOT to Use Retry:**

- Tests failing due to logic errors (fix the test instead)
- Tests with wrong assertions (fix expectations)
- Tests with import/syntax errors (fix the code)

**Documentation:**

- Always add a note in the test docstring explaining why it's marked flaky
- Add entry to `docs/testing/flaky-tests.md`
- Create issue for root cause fix if appropriate

See [Flaky Tests Tracker](docs/testing/flaky-tests.md) for current flaky tests and monitoring guidelines.

### Diff Coverage (PR-Specific Coverage)

The project uses **[diff-cover](https://github.com/Bachmann1234/diff_cover)** to enforce test coverage on changed lines only in pull requests. This ensures new code is well-tested without requiring 100% coverage on existing code.

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

Build and view [Sphinx](https://www.sphinx-doc.org/) documentation locally:

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

### Hyperlinking Guidelines

When adding documentation, follow these guidelines for hyperlinks:

**DO Link:**

- ✅ First mention of a tool/technology per document
- ✅ Official documentation sites (use HTTPS only)
- ✅ Standards and specifications ([PEPs](https://peps.python.org/), RFCs)
- ✅ Key concepts that benefit from explanation
- ✅ External tools users will need to install

**DON'T Link:**

- ❌ Every occurrence (only first or important mentions)
- ❌ Common knowledge in developer docs (git, GitHub)
- ❌ Internal file references (use relative paths instead)
- ❌ Unstable or unofficial resources
- ❌ Code blocks (keep code as plain text)

**Link Format:**

```markdown
# Inline links (preferred for readability)
[Tool Name](https://official-site.com/)

# Reference-style links (for repeated or long URLs)
[Tool Name][tool-link]
...
[tool-link]: https://very-long-url.com/path/to/docs
```

**Link Reference Library:**

Use the centralized link reference in `docs/LINK_REFERENCE.md` for commonly referenced tools and technologies to ensure consistency across documentation.

**Examples:**

```markdown
# Good:
Learn more about [ruff's linting rules](https://docs.astral.sh/ruff/rules/)

# Bad:
Click [here](https://docs.astral.sh/ruff/rules/) to see ruff rules
```

**Accessibility:**

- Use descriptive link text for screen readers
- Don't rely on color alone to indicate links
- Ensure sufficient contrast for link text

**Link Checking:**

All links are automatically checked in CI using the link-check GitHub Action. Broken links will cause CI to fail. Test your links locally before pushing:

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check specific file
markdown-link-check README.md

# Check all markdown files
find . -name "*.md" -not -path "./node_modules/*" -exec markdown-link-check {} \;
```

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

This project uses [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot) to automatically create PRs for dependency updates. When reviewing Dependabot PRs:

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

Dependabot PRs use [conventional commits](https://www.conventionalcommits.org/):

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

## Updating Dependencies

We keep dependencies up-to-date for security and features.

### Automated Dependency Management

The project includes an automated dependency update script at `scripts/update_dependencies.py`.

#### Quick Start

```bash
# Check for available updates
make deps-check

# Apply updates (with tests)
make deps-update

# Apply updates with full tox validation
make deps-update-full
```

#### Manual Usage

```bash
# Check for updates (dry run)
python scripts/update_dependencies.py --check

# Apply updates interactively
python scripts/update_dependencies.py --apply

# Apply with test validation
python scripts/update_dependencies.py --apply --test

# Apply with full tox validation
python scripts/update_dependencies.py --apply --test --tox
```

### What Gets Updated

The script updates:

- **Pre-commit hooks**: Updates all hooks in `.pre-commit-config.yaml` to latest stable versions
- **Python packages**: Updates packages in `uv.lock` to latest compatible versions

### Update Process

1. **Check**: Script scans for available updates
1. **Report**: Displays available updates with version changes
1. **Confirm**: Asks for confirmation before applying
1. **Apply**: Updates configurations and lock files
1. **Test**: Optionally runs tests to verify compatibility
1. **Validate**: Optionally runs full tox validation

### Update Schedule

Recommended update frequency:

- **Monthly**: Pre-commit hooks and Python packages
- **Quarterly**: Major version updates (with thorough testing)
- **Immediately**: Security patches and vulnerability fixes
- **Weekly**: Automated check (CI)

### Breaking Changes

The script flags major version changes with `⚠️  MAJOR` warning:

```
  mypy    1.13.0  →  2.0.0  ⚠️  MAJOR
```

For major updates:

1. Review package CHANGELOG for breaking changes
1. Check migration guides
1. Test thoroughly with full tox suite
1. Update code if needed

### Manual Updates

For manual updates without the script:

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python packages
uv lock --upgrade

# Verify updates
pytest
tox -p auto
```

### Pre-commit Hook Updates

Hook versions are automatically updated by [pre-commit.ci](https://pre-commit.ci).

- **Schedule**: Weekly (every Monday)
- **Process**: Automated PRs created when updates available
- **Review**: Maintainer reviews and merges PRs
- **Manual update**: Run `pre-commit autoupdate` if urgent

**When pre-commit.ci creates an update PR:**

1. Review version changes and changelogs
1. Ensure all CI checks pass
1. Test locally for major version bumps
1. Merge PR to apply updates

**Manual updates between automation cycles:**

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Update specific hook
pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit

# Test updated hooks
pre-commit run --all-files

# Commit if tests pass
git commit -am "chore(deps): Update pre-commit hooks"
```

### Rollback

If updates cause issues:

```bash
# Revert changes
git checkout HEAD -- .pre-commit-config.yaml uv.lock

# Or revert commit
git revert <commit-hash>
```

## Release Process

(For maintainers)

### Pre-Release Package Validation

Before creating a release, validate the package:

```bash
# Build and validate package
make package

# Or run individual steps:
make build          # Build wheel and sdist
make check-wheel    # Validate wheel contents
```

This runs comprehensive package validation:

- **Build**: Creates wheel and source distribution
- **check-wheel-contents**: Validates wheel structure
  - ✅ LICENSE included
  - ✅ README metadata present
  - ✅ No test files
  - ✅ No `__pycache__` or `.pyc` files
  - ✅ Correct package structure
- **twine check**: Validates package metadata for PyPI

**Common Issues:**

- Missing LICENSE: Ensure `LICENSE` file exists in root
- Test files in wheel: Check `.gitignore` and `pyproject.toml` excludes
- `__pycache__` in wheel: Run `make clean` before building

### Release Steps

**Note:** This project uses **dynamic versioning** from Git tags via [hatch-vcs](https://github.com/ofek/hatch-vcs). Version numbers are automatically determined from Git tags—no manual version updates needed!

1. **Update Changelog**

   - Update `CHANGELOG.md` with release notes
   - Document all changes since last release

1. **Ensure Clean State**

   ```bash
   git checkout main
   git pull origin main
   make test  # Ensure all tests pass
   ```

1. **Validate Package**

   ```bash
   make package  # Build and validate
   ```

1. **Create Git Tag** (This sets the version!)

   ```bash
   # Tag format: vX.Y.Z (Semantic Versioning)
   git tag -a v2.1.0 -m "Release v2.1.0"

   # The tag becomes the package version automatically
   # v2.1.0 → Package version 2.1.0
   # v2.1.0-rc1 → Package version 2.1.0rc1
   ```

1. **Push Tag**

   ```bash
   git push --tags  # Triggers CI/CD release workflow
   ```

1. **Create GitHub Release**

   - Create release from tag with changelog notes

1. **Publish to PyPI** (Optional)

   ```bash
   # Test on TestPyPI first
   make publish-test

   # Verify installation from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ nhl-scrabble

   # If successful, publish to PyPI
   make publish
   ```

### Package Validation in CI

The package validation workflow runs automatically on:

- All pull requests to `main`
- All pushes to `main`
- All release tags (`v*`)

The workflow:

1. Builds wheel and source distribution
1. Validates with `check-wheel-contents`
1. Validates with `twine check`
1. Verifies LICENSE is included
1. Verifies no test files in wheel
1. Verifies no `__pycache__` in wheel
1. Uploads artifacts (wheel and sdist)

**CI Failure Troubleshooting:**

If package validation fails in CI:

1. Check the workflow logs for specific errors
1. Run `make package` locally to reproduce
1. Fix identified issues
1. Commit and push changes
1. CI will re-run validation

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
make mypy              # Type check (mypy)
make ty                # Type check (Astral ty - fast)
make type-check        # Type check (ty + mypy comprehensive)
make check             # Run all checks before commit

# Cleaning
make clean             # Clean all artifacts
make clean-all         # Clean everything including venv

# Building
make build             # Build distribution packages
make check-wheel       # Build and validate wheel contents
make package           # Build and validate package (wheel + twine)
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
