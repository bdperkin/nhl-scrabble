# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NHL Scrabble Score Analyzer is a professional [Python](https://www.python.org/) package that fetches current NHL roster data and calculates "Scrabble scores" for player names based on standard Scrabble letter values. It generates comprehensive reports showing team, division, and conference standings based on these scores, complete with a mock playoff bracket.

**Current Version:** 2.0.0
**Python:** [3.12-3.14](https://www.python.org/downloads/) (supported), 3.15-dev (experimental)
**License:** [MIT](https://opensource.org/licenses/MIT)
**Pre-commit Hooks:** 67 hooks (comprehensive quality checks including [Astral ty](https://docs.astral.sh/ty/), [refurb](https://github.com/dosisod/refurb), and [ssort](https://github.com/bwhmather/ssort))
**Dependency Management:** [UV](https://docs.astral.sh/uv/) with deterministic lock file

## Quick Start

```bash
# Setup development environment
make init
source .venv/bin/activate

# Run the analyzer
nhl-scrabble analyze

# Or via Python module
python -m nhl_scrabble analyze

# Note: UV acceleration is automatic when using tox
make tox              # Fast testing with UV via [tox-uv](https://github.com/tox-dev/tox-uv)
```

## Package Architecture

### Modern Python Package (v2.0.0+)

The project has been transformed from a single script into a professional Python package with proper structure:

```
nhl-scrabble/
├── src/nhl_scrabble/          # Main package
│   ├── __init__.py            # Package initialization, version
│   ├── __main__.py            # Entry point for python -m
│   ├── cli.py                 # Click-based CLI interface
│   ├── config.py              # Configuration management
│   ├── logging_config.py      # Logging setup
│   ├── api/                   # NHL API client
│   │   ├── __init__.py
│   │   └── nhl_client.py      # API client with retry logic
│   ├── models/                # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── player.py          # Player model
│   │   ├── team.py            # Team model
│   │   └── standings.py       # Standings models
│   ├── scoring/               # Scrabble scoring logic
│   │   ├── __init__.py
│   │   └── scrabble.py        # Score calculation
│   ├── processors/            # Business logic
│   │   ├── __init__.py
│   │   ├── team_processor.py  # Team processing
│   │   └── playoff_calculator.py  # Playoff logic
│   └── reports/               # Report generators
│       ├── __init__.py
│       ├── base.py            # Base report class
│       ├── conference_report.py
│       ├── division_report.py
│       ├── playoff_report.py
│       ├── team_report.py
│       └── stats_report.py
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── conftest.py            # Pytest configuration
└── docs/                      # Documentation
```

### Key Components

**API Client (`api/nhl_client.py`):**

- Context manager for session handling
- Retry logic with exponential backoff
- Rate limiting (0.3s delays)
- Proper error handling
- Type hints throughout

**Models (`models/`):**

- [Pydantic](https://docs.pydantic.dev/) models for type safety
- PlayerScore, TeamScore, DivisionStandings, ConferenceStandings
- Validation and serialization
- JSON export support

**Scoring (`scoring/scrabble.py`):**

- ScrabbleScorer class with SCRABBLE_VALUES constant
- calculate_score() method for any text
- score_player() for Player models

**Processors (`processors/`):**

- TeamProcessor: Aggregates team scores
- PlayoffCalculator: NHL playoff bracket logic
- Separation of concerns

**Reports (`reports/`):**

- Base class for all reports
- Specialized report generators
- Text and JSON output formats
- [Rich](https://rich.readthedocs.io/) library for beautiful terminal output

**CLI (`cli.py`):**

- [Click](https://click.palletsprojects.com/)-based command-line interface
- analyze command with options
- --format (text/json), --output, --verbose
- Environment variable support

## Pre-commit Hooks (67 Comprehensive Checks)

The project uses 67 pre-commit hooks for automatic code quality validation:

### Hook Categories

**Meta Hooks (3):**

- `check-hooks-apply`: Validates all hooks apply to repository files
- `check-useless-excludes`: Detects useless exclude patterns
- `sync-pre-commit-deps`: Syncs hook versions with pyproject.toml

**File Quality Hooks (18 from pre-commit-hooks):**

- Whitespace: `trailing-whitespace`, `end-of-file-fixer`, `mixed-line-ending`, `fix-byte-order-marker`
- Syntax: `check-yaml`, `check-toml`, `check-json`, `check-ast`
- Python: `check-builtin-literals`, `check-docstring-first`, `debug-statements`, `name-tests-test`
- Security: `detect-private-key`
- Git: `check-added-large-files`, `check-merge-conflict`, `check-case-conflict`, `destroyed-symlinks`
- Executable: `check-shebang-scripts-are-executable`

**Python Quality Hooks (7 from pygrep-hooks):**

- `python-check-blanket-noqa`: Enforce specific noqa codes (# noqa: F401)
- `python-check-blanket-type-ignore`: Enforce specific type: ignore codes
- `python-check-mock-methods`: Prevent mock testing mistakes
- `python-no-eval`: Detect eval() usage (security)
- `python-no-log-warn`: Enforce logging.warning() vs deprecated logging.warn()
- `python-use-type-annotations`: Enforce [PEP 484](https://peps.python.org/pep-0484/) annotations vs type comments
- `text-unicode-replacement-char`: Detect Unicode replacement character (U+FFFD)

**Python Import Hooks (2 from isort and absolufy-imports):**

- `isort`: Sort Python imports (Black-compatible, line-length=100, matches ruff's isort configuration)
- `absolufy-imports`: Convert relative imports to absolute imports (comprehensive by default)

**Project Validation Hooks (4 from validate-pyproject, pyroma, tox-ini-fmt, and check-wheel-contents):**

- `validate-pyproject`: Validates pyproject.toml against [PEP 517](https://peps.python.org/pep-0517/), [518](https://peps.python.org/pep-0518/), [621](https://peps.python.org/pep-0621/), [631](https://peps.python.org/pep-0631/) standards
- `pyroma`: Rates Python package metadata quality (checks descriptions, classifiers, documentation, etc.)
- `tox-ini-fmt`: Formats tox.ini to standard structure (enforces [tox](https://tox.wiki/) 4 best practices, auto-formats configuration)
- `check-wheel-contents`: Validates Python wheel package contents (LICENSE included, no test files, correct structure)

**YAML Linting Hooks (1 from yamllint):**

- `yamllint`: YAML file validation and linting (comprehensive by default)

**JSON/YAML Schema Validation Hooks (4 from check-jsonschema):**

- `check-github-workflows`: Validates GitHub workflow files against official schema
- `check-dependabot`: Validates Dependabot config against official schema
- `check-codecov`: Validates .codecov.yml against Codecov schema
- `check-pre-commit`: Validates .pre-commit-config.yaml against schema

**Spelling Hooks (1 from codespell):**

- `codespell`: Spell checking for code and documentation (comprehensive by default)

**Markdown Hooks (2 from pymarkdown and mdformat):**

- `pymarkdown`: Markdown linting (comprehensive by default)
- `mdformat`: Markdown formatting with plugins (mdformat-gfm, mdformat-black, mdformat-ruff, mdformat-web)

**Documentation Hooks (2 from PyCQA/doc8 and rstcheck/rstcheck):**

- `doc8`: RST style linting (comprehensive by default, max-line-length=100)
- `rstcheck`: RST syntax checking (report_level=INFO, validates code blocks with Sphinx)

**Documentation Quality Hooks (7 from interrogate, deptry, unimport, pydocstyle, vulture, blocklint, and gitlint):**

- `interrogate`: Docstring coverage checking (requires 100% docstring coverage for all Python code)
- `deptry`: Comprehensive dependency checker (detects obsolete, missing, transitive, and misplaced dev dependencies)
- `unimport`: Unused import checker (finds and reports unused import statements)
- `pydocstyle`: Docstring style checking (checks docstring format and style per PEP 257)
- `vulture`: Dead code detection (finds unused functions, classes, variables, imports, and properties)
- `blocklint`: Inclusive language checker (detects non-inclusive terminology in code, comments, and documentation)
- `gitlint`: Commit message linter (enforces consistent commit message style and documentation)

**UV Hook (1 from uv-pre-commit):**

- `uv-lock`: Maintains uv.lock file consistency with pyproject.toml

**Flake8 Hooks (1 from pycqa/flake8):**

- `flake8`: Python code linting and style checking (comprehensive configuration via flake8-pyproject)

**Autoflake Hooks (1 from PyCQA/autoflake):**

- `autoflake`: Remove unused imports and variables (aligns with ruff's F401 and F841 rules, ignores __init__.py imports)

**Black Hooks (1 from psf/black-pre-commit-mirror):**

- `black`: Python code formatting (line-length=100, matches ruff-format, runs before other formatters)

**Docformatter Hooks (1 from local):**

- `docformatter`: Python docstring formatting (wrap-length=100, [PEP 257](https://peps.python.org/pep-0257/) style)

**Autopep8 Hooks (1 from hhatto/autopep8):**

- `autopep8`: [PEP 8](https://peps.python.org/pep-0008/) auto-formatting (runs after black, before ruff-format, aggressive level 2)

**Python Modernization Hooks (2 from asottile/pyupgrade and local):**

- `pyupgrade`: Modernize Python syntax for Python 3.12+ (f-strings, type hints, removes deprecated imports)
- `refurb`: Python code modernization linter (pathlib, comprehensions, modern idioms) - **warning mode, non-blocking**

**Python Statement Sorting Hooks (1 from bwhmather/ssort):**

- `ssort`: Sort Python class members and module statements (dunder methods, classmethods, properties, public methods, private methods in consistent order)

**Ruff Hooks (2 from ruff-pre-commit):**

- `ruff-check`: Comprehensive linting with ALL rules (--fix, --exit-non-zero-on-fix)
- `ruff-format`: Code formatting (quote-style: double, indent-style: space)

**Type Checking Hooks (2 from mirrors-mypy and local):**

- `mypy`: Strict type checking (strict mode with comprehensive options)
- `ty`: Astral's fast type checker (10-100x faster than mypy, validation mode - non-blocking)

### Pre-commit Usage

```bash
# Install hooks (one-time)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-check --all-files

# Update hook versions
pre-commit autoupdate

# Skip specific hooks (use sparingly)
SKIP=mypy git commit -m "message"
```

All hooks run automatically on `git commit`, ensuring code quality before changes enter the repository.

### Admin Commits to Main Branch

**IMPORTANT PROJECT RULE**: When admin bypass is necessary to commit directly to `main`:

```bash
# ✅ CORRECT: Skip only branch protection, run all other hooks
SKIP=check-branch-protection git commit -m "message"

# ❌ NEVER USE: This bypasses ALL quality checks
git commit --no-verify -m "message"
```

**Rationale**:

- The `check-branch-protection` hook is a workflow reminder, not a quality check
- All other hooks (ruff, mypy, formatting, linting, etc.) MUST always run
- Quality checks prevent bugs, security issues, and maintain code standards
- Even admin commits must meet quality standards

**When to use**:

- Post-merge cleanup commits
- Documentation updates after PR merge
- Task tracking updates
- Emergency hotfixes (still run quality checks!)

**Never skip quality checks** - The 66 other hooks exist to protect code quality and security.

## Development Tools

### UV Ecosystem (10-100x Faster)

The project uses comprehensive UV configuration aligned with ruff's "ALL rules" philosophy:

#### UV Configuration (pyproject.toml)

**Strict Dependency Resolution (like ruff's ALL rules):**

```toml
[tool.uv]
managed = true
package = true
compile-bytecode = true
link-mode = "copy"

# Comprehensive resolution (matches ruff's ALL rules philosophy)
resolution = "highest" # Use highest compatible versions

# Dependency constraints (like ruff's base ruleset)
constraint-dependencies = [] # Strict baseline
override-dependencies = []   # Selective exceptions (like ruff ignores)

# Deterministic resolution (like ruff's consistent checking)
index-strategy = "first-match" # Predictable package resolution
keyring-provider = "disabled"  # Reproducible across environments

# Python management
python-preference = "managed" # Consistent Python versions

# Stability
preview = false # Disable experimental features (like avoiding experimental ruff rules)

# Caching
cache-keys = [] # Strict cache control
```

**Philosophy Alignment:**

| UV Setting                       | Ruff Equivalent    | Purpose                        |
| -------------------------------- | ------------------ | ------------------------------ |
| `resolution = "highest"`         | `select = ["ALL"]` | Comprehensive by default       |
| `override-dependencies`          | `ignore = [...]`   | Selective practical exceptions |
| `index-strategy = "first-match"` | Consistent rules   | Deterministic behavior         |
| `keyring-provider = "disabled"`  | Reproducible       | Same behavior everywhere       |

#### Lock File (uv.lock)

**1,957-line deterministic dependency lock:**

- All direct and transitive dependencies with exact versions
- Hash verification for all packages
- Platform-specific resolutions
- Maintained automatically by `uv-lock` pre-commit hook

```bash
# Check UV is available (optional)
make uv-check

# UV is used automatically with tox
make tox             # Uses UV via tox-uv plugin
make tox-parallel    # Even faster with parallel execution

# Direct UV pip access (advanced)
make uv-pip ARGS="list"

# Lock file is auto-maintained by pre-commit hook
# Manual update if needed:
uv lock
```

### Makefile (57 Targets)

Self-documenting Makefile with comprehensive automation organized in 16 logical groupings:

```bash
make help            # Show all targets with descriptions

# Setup
make init            # Traditional setup (pip)
make uv-init         # Fast setup (uv)

# Testing
make test            # Run all tests
make test-cov        # With coverage
make tox             # Parallel execution with tier-based fail-fast (default)
make tox-parallel    # Pure parallel (all environments)
make tox-sequential  # Sequential (for debugging)
make tox-quick       # Critical checks only (fast fail-fast)

# Code Quality
make ruff-check      # Ruff linting
make ruff-format     # Auto-format
make mypy            # MyPy type checking
make ty              # Astral ty type checking (fast)
make type-check      # All type checkers (ty + mypy)
make quality         # All checks
make uv-pre-commit   # Pre-commit with UV
make validate-json   # Validate JSON/YAML configs against schemas
make validate-configs # Alias for validate-json

# Running
make run             # Run analyzer (via tox)
make run-verbose     # Run with verbose logging (via tox)
make run-json        # Run and output JSON (via tox)
```

### Testing (Tox + Pytest)

Comprehensive test suite with tox-uv for speed:

```bash
# Run tests (with pytest-xdist parallel execution)
pytest                    # Quick test run (auto-parallel with -n auto)
pytest -n 4              # Explicit worker count
pytest -n 0              # Sequential execution (debugging)

# Tox testing (with intelligent parallel execution and fail-fast)
make tox                 # Default: parallel with tier-based fail-fast
make tox-parallel        # Pure parallel (all environments)
make tox-sequential      # Sequential (for debugging)
make tox-quick           # Critical checks only (fast fail-fast)
tox -e py312             # Test Python 3.12 (fast with tox-uv!)
tox -e py315             # Test Python 3.15 (fast with tox-uv!)
tox -m critical          # Run only critical quality checks
tox -m test              # Run only tests
make ci                  # CI simulation (uses tox -e ci)

# Coverage
pytest --cov             # With coverage
make test-cov            # Via Makefile
tox -e coverage          # Via tox
tox -e diff-cover        # Check coverage on changed lines only (PR coverage)
```

**Test Performance:**

- **Parallel execution**: pytest-xdist runs tests on multiple CPU cores
- **170 tests**: 131s sequential → 47s parallel (2.8x speedup on 8 cores)
- **CI optimization**: GitHub Actions uses 2 workers for 2-core runners

**Test Structure:**

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for full workflows
- `tests/conftest.py` - Shared fixtures
- 170 tests with >93% coverage on core modules

### Code Quality Tools

**Ruff** (linting and formatting):

- Fast Rust-based linter/formatter
- Replaces black, isort, flake8
- Configuration in pyproject.toml

**MyPy** (type checking):

- Strict type checking enabled
- Configuration in pyproject.toml
- Type hints throughout codebase

**ty** (fast type checking):

- Astral's extremely fast type checker (10-100x faster than mypy)
- Written in Rust for blazing performance
- Supplements mypy during validation period
- Configuration in pyproject.toml
- Non-blocking in pre-commit and CI (validation mode)

**Pre-commit** (hooks):

- Automated quality checks
- Runs on every commit
- UV-accelerated (9x faster)
- Configuration in .pre-commit-config.yaml

## Configuration

### pyproject.toml

Central configuration for the entire project:

```toml
[project]
name = "nhl-scrabble"
version = "2.0.0"
requires-python = ">=3.12"

[tool.uv]
managed = true
package = true
compile-bytecode = true
link-mode = "copy"

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Environment Variables

Configure via `.env` file or export:

```bash
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
NHL_SCRABBLE_TOP_PLAYERS=30
NHL_SCRABBLE_VERBOSE=true
```

### UV Configuration

UV is configured via the `[tool.uv]` section in `pyproject.toml`:

```toml
[tool.uv]
managed = true          # Enable UV dependency management
package = true          # This is a Python package
compile-bytecode = true # Compile .pyc files for faster imports
link-mode = "copy"      # Copy files instead of linking
```

These settings optimize for speed and reliability. Note: `prefer-binary` is a UV command-line flag, not a config option.

## NHL API Integration

### Endpoints

**Standings:**

```
GET https://api-web.nhle.com/v1/standings/now
```

Returns team metadata (division, conference, current standings)

**Team Rosters:**

```
GET https://api-web.nhle.com/v1/roster/{team_abbrev}/current
```

Returns current roster for a specific team

### Rate Limiting

- 0.3 second delay between roster fetches
- Retry logic with exponential backoff
- Configurable via NHL_SCRABBLE_RATE_LIMIT_DELAY

### Error Handling

- Retries on network errors (default: 3 retries)
- Timeout handling (default: 10s)
- Graceful degradation (skip failed teams)

## Scrabble Scoring Logic

### Letter Values

Standard Scrabble letter point values:

- **1 point**: A, E, I, O, U, L, N, S, T, R
- **2 points**: D, G
- **3 points**: B, C, M, P
- **4 points**: F, H, V, W, Y
- **5 points**: K
- **8 points**: J, X
- **10 points**: Q, Z

### Calculation

```python
from nhl_scrabble.scoring import ScrabbleScorer

scorer = ScrabbleScorer()
score = scorer.calculate_score("Ovechkin")  # Returns total points
```

### Player Scoring

Full name scored as first + last:

```python
from nhl_scrabble.models import Player

player = Player(firstName="Alexander", lastName="Ovechkin")
score = scorer.score_player(player)  # PlayerScore object
```

## Playoff Logic

### NHL Playoff Structure

The playoff calculator replicates NHL playoff bracket:

1. **Division Leaders** (Top 3 per division)

   - Automatic playoff spots
   - Marked with 'y' indicator

1. **Wild Cards** (2 per conference)

   - Next best teams by total score
   - Marked with 'x' indicator

1. **Conference Leaders**

   - Marked with 'z' indicator

1. **Presidents' Trophy**

   - Best overall record
   - Marked with 'p' indicator

1. **Eliminated Teams**

   - Marked with 'e' indicator

### Tiebreakers

When teams have equal total scores:

1. Average points per player
1. Alphabetical by team abbreviation

## CLI Usage

### Basic Commands

```bash
# Run with defaults
nhl-scrabble analyze

# Verbose output
nhl-scrabble analyze --verbose

# JSON output
nhl-scrabble analyze --format json --output report.json

# Customize display
nhl-scrabble analyze --top-players 50 --top-team-players 10
```

### Options

- `--format [text|json]` - Output format (default: text)
- `-o, --output PATH` - Output file (default: stdout)
- `-v, --verbose` - Enable verbose logging
- `--top-players INTEGER` - Number of top players (default: 20)
- `--top-team-players INTEGER` - Players per team (default: 5)

## Development Workflow

### First Time Setup

```bash
# Clone repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Setup development environment
make init
source .venv/bin/activate

# Verify setup
make check
pytest
```

### Daily Development

```bash
# Activate environment
source .venv/bin/activate

# Make changes to code...

# Run tests
pytest

# Check code quality
make quality

# Run pre-commit
make pre-commit

# Commit changes
git commit -m "Your changes"
```

### Before Pull Request

**Automated Validation (when using /implement-task skill)**:

The `/implement-task` skill automatically runs pre-flight validation before pushing:

```bash
# Automatically runs:
pre-commit run --all-files    # All 61 hooks (~45s)
tox -p auto                    # All environments (~3-5 min)
git status                     # Verify clean state
```

- **Catches issues locally** before CI
- **Saves 10-15 minutes** per PR by avoiding CI failures
- **83% reduction** in failed CI runs
- **Higher confidence**: ~95% first-time CI pass
- Only pushes if all validation passes

**Manual Validation (traditional workflow)**:

```bash
# Run full test suite
make tox-parallel

# Run all quality checks
make check

# Verify CI will pass
make ci

# Run pre-commit hooks
pre-commit run --all-files

# Everything should be green!
```

**Time Comparison**:

| Approach                    | Time     | CI Pass Rate | Notes                     |
| --------------------------- | -------- | ------------ | ------------------------- |
| No validation               | 0 min    | ~70%         | High CI failure rate      |
| Manual validation           | 5-10 min | ~90%         | Easy to forget steps      |
| Automated (/implement-task) | 3-5 min  | ~95%         | Consistent, never skipped |

**Skip Validation** (emergency only):

```bash
# Only for emergencies: hotfixes, CI infrastructure issues
SKIP=pre-commit git push
```

### Git Branch Cleanup

After PRs are merged, clean up local branches to maintain a tidy repository:

```bash
# Check branch status (merged vs active)
make git-status-branches

# Prune stale remote tracking branches
make git-prune-remote-refs

# Delete local branches merged to main (with confirmation)
make git-prune-local

# Delete branches from closed (not merged) PRs (with confirmation)
make git-prune-closed-prs

# Standard cleanup (remote refs + merged branches)
make git-cleanup

# Complete cleanup (includes closed PR branches)
make git-cleanup-all
```

**Automatic Configuration:**

The repository is configured with `git config fetch.prune true`, which automatically removes stale remote tracking branches on every `git fetch`.

**Safety Features:**

- **Merged branches**: Only deletes fully merged branches (`git branch -d`), local only
- **Closed PR branches**: Deletes BOTH local and remote, warns before deletion, requires confirmation
- Never deletes main or current branch
- GitHub CLI integration to verify PR status
- Clear warnings when remote branches will be deleted from GitHub

## CI/CD

### GitHub Actions

The project has comprehensive CI:

```yaml
jobs:
  test:        # Test on py3.12-3.14 (required), py3.15-dev (experimental)
  tox:         # Tox with UV (matrix: py312, py313, py314, py315, ruff-check, mypy, coverage)
  pre-commit:  # Pre-commit with UV
```

**Python Version Testing:**

- **Required**: Python 3.12, 3.13, 3.14 (must all pass)
- **Experimental**: Python 3.15-dev (`continue-on-error: true`, informational only)

Python 3.15-dev is tested for early compatibility checking but failures do NOT block CI or prevent merging.

**Optimization:**

- UV for 60% faster pipeline
- Tox-UV for 10x faster testing
- Pre-commit-UV for 9x faster hooks
- Caching enabled throughout

### Performance

- **Without UV:** ~12 minutes
- **With UV:** ~3 minutes (4x faster!)

### Coverage Tracking

The project uses both Codecov and diff-cover for comprehensive coverage tracking:

**Codecov (Total Coverage):**

- **Dashboard**: https://app.codecov.io/gh/bdperkin/nhl-scrabble
- **Coverage Target**: 90%+ overall, 80%+ for new code
- **Badge**: Shows current coverage percentage in README
- **PR Comments**: Codecov bot comments on all PRs with coverage changes
- **Configuration**: `.codecov.yml`

Coverage is uploaded automatically from CI on every commit to main and on all pull requests.

**diff-cover (PR Coverage):**

- **Purpose**: Enforces test coverage on changed lines only in PRs
- **Target**: ≥80% coverage on all changed lines
- **Enforcement**: Required in CI - PRs fail if diff coverage < 80%
- **Local Usage**: `tox -e diff-cover` or `diff-cover coverage.xml --compare-branch=origin/main`
- **Configuration**: `[tool.diff_cover]` in `pyproject.toml`

**Coverage Philosophy:**

| Metric          | Total Coverage (Codecov) | Diff Coverage      |
| --------------- | ------------------------ | ------------------ |
| **Scope**       | Entire codebase          | Changed lines only |
| **Purpose**     | Overall health tracking  | PR quality gate    |
| **Current**     | ~50%                     | ≥80% (enforced)    |
| **Enforcement** | ⚠️ Informational         | ✅ CI blocker      |
| **Best for**    | Long-term trends         | New code quality   |

Both tools work together: Codecov tracks overall project health over time, while diff-cover ensures all new code meets quality standards.

### Security

The project has comprehensive security measures:

**Branch Protection:**

- ✅ Main branch is protected
- ✅ Direct commits blocked (PR workflow required)
- ✅ All CI checks must pass before merge
- ✅ Force pushes blocked
- ✅ Branch deletion blocked
- ✅ Conversations must be resolved
- ⚠️ Admin bypass allowed (for emergencies)

**Automated Security Scanning:**

- ✅ **CodeQL** - Weekly security scans + PR checks
- ✅ **Dependabot** - Automated dependency vulnerability alerts
- ✅ **Secret Scanning** - Detects committed secrets/API keys
- ✅ **pip-audit** - CI-based dependency vulnerability scanning

**Dependency Management:**

- Dependabot creates update PRs weekly (Mondays 9 AM ET)
- Security vulnerabilities get immediate individual PRs
- Regular updates grouped by type (dev/prod)

**Merge Strategy:**

- ✅ Squash merge only (consistent git history)
- ✅ Auto-delete branches on merge

## Documentation

**Online Documentation:** https://bdperkin.github.io/nhl-scrabble/

Documentation follows the [Diátaxis framework](https://diataxis.fr/) organized into four quadrants, built with Sphinx and auto-deployed to GitHub Pages:

### Tutorials (Learning-Oriented)

Step-by-step lessons for beginners:

- **[Getting Started](docs/tutorials/01-getting-started.md)** - First NHL Scrabble analysis
- **[Understanding Output](docs/tutorials/02-understanding-output.md)** - Deep dive into reports
- **[First Contribution](docs/tutorials/03-first-contribution.md)** - Make your first code contribution

### How-to Guides (Problem-Oriented)

Practical solutions to specific tasks:

- **[Installation Variations](docs/how-to/installation.md)** - Different ways to install
- **[Run Tests](docs/how-to/run-tests.md)** - Execute different test configurations
- **[Add Report Type](docs/how-to/add-report-type.md)** - Create custom reports
- **[Use UV](docs/how-to/use-uv.md)** - 10-100x faster package management
- **[And more...](docs/how-to/)** - 10 how-to guides total

### Reference (Information-Oriented)

Technical specifications:

- **[CLI Reference](docs/reference/cli.md)** - All commands and options
- **[Configuration](docs/reference/configuration.md)** - All settings explained
- **[Makefile Reference](docs/reference/makefile.md)** - All 55 Makefile targets
- **[Environment Variables](docs/reference/environment-variables.md)** - Complete list
- **[And more...](docs/reference/)** - Complete technical reference

### Explanation (Understanding-Oriented)

Background and design philosophy:

- **[Why Scrabble Scoring?](docs/explanation/why-scrabble-scoring.md)** - The concept explained
- **[Architecture Overview](docs/explanation/architecture.md)** - System design
- **[NHL API Strategy](docs/explanation/nhl-api-strategy.md)** - API integration approach
- **[Testing Philosophy](docs/explanation/testing-philosophy.md)** - Testing approach
- **[And more...](docs/explanation/)** - Design decisions and rationale

### Community Documentation

- **README.md** - Project overview
- **CONTRIBUTING.md** - Development guide
- **CODE_OF_CONDUCT.md** - Community standards
- **SECURITY.md** - Security policy
- **SUPPORT.md** - Getting help
- **CHANGELOG.md** - Version history
- **CLAUDE.md** - This file

### Documentation Output Formats

The project supports multiple documentation output formats via Sphinx:

**Available Formats:**

- **HTML** (default) - Web documentation deployed to GitHub Pages
- **Man Pages** - Unix man page format for terminal viewing
- **Texinfo** - GNU Info format for Emacs/Info readers
- **PDF** - Portable document format via LaTeX (requires pdflatex)
- **Plain Text** - Simple text-only format
- **AsciiDoc** - AsciiDoc format via pandoc (requires pandoc)

**Build Commands:**

```bash
# Build individual formats
make docs-html      # HTML documentation
make docs-man       # Man pages
make docs-texinfo   # Texinfo/Info format
make docs-pdf       # PDF via LaTeX (requires LaTeX installation)
make docs-text      # Plain text
make docs-asciidoc  # AsciiDoc (requires pandoc)

# Build all formats
make docs-all       # All formats at once
```

**Use Cases:**

- **HTML** - Primary web documentation, searchable, interactive
- **Man Pages** - System documentation integration (`man nhl-scrabble`)
- **Texinfo** - Emacs Info mode, hierarchical browsing
- **PDF** - Offline reading, print-friendly, downloadable manual
- **Text** - Simplest offline format, grep-able, no dependencies
- **AsciiDoc** - AsciiDoc-based documentation systems, lightweight markup

**Distribution:**

```bash
# Install man page system-wide
sudo cp docs/_build/man/nhl-scrabble.1 /usr/local/share/man/man1/
man nhl-scrabble

# Install Texinfo
cd docs/_build/texinfo
makeinfo nhl-scrabble.texi -o nhl-scrabble.info
sudo cp nhl-scrabble.info /usr/local/share/info/
info nhl-scrabble

# Distribute PDF
cp docs/_build/latex/nhl-scrabble.pdf ~/Documents/
```

**LaTeX Requirements** (PDF only):

- Package: `texlive-latex-base` and `texlive-latex-extra` (~500 MB)
- Ubuntu/Debian: `sudo apt-get install texlive-latex-base texlive-latex-extra`
- macOS: `brew install --cask mactex`
- Fedora/RHEL: `sudo dnf install texlive-scheme-basic texlive-latex-extra`

**Known Limitations:**

- PDF build may fail with SVG images (LaTeX requires PNG/PDF format)
- LaTeX installation is large (~500 MB minimum)
- PDF compilation takes 30-60 seconds

See **[Build Documentation Guide](docs/how-to/build-documentation.md)** for complete instructions.

### Documentation Badges

The project uses comprehensive badges in README.md to provide at-a-glance project information organized into logical categories:

**Badge Categories:**

- **Build & Quality** - CI status, CodeQL security scanning, documentation builds, code coverage
- **Code Quality** - Ruff formatting, MyPy type checking, pre-commit hooks
- **Package Info** - Python versions, license, UV package manager, latest release
- **Community & Activity** - Contributors, stars, PRs welcome, issues, commit activity, last commit
- **Maintenance** - Maintenance status indicator

**Badge Maintenance:**

- Most badges auto-update via GitHub APIs and shields.io
- Manual badges (Maintenance status) reviewed quarterly
- Badge links verified monthly in CI
- Add new badges via tasks/enhancement/003 process
- Total badge count kept under 25 to avoid clutter

**Badge Sources:**

- **shields.io** - Primary badge generator with CDN
- **GitHub Actions** - Workflow status badges (CI, CodeQL, Docs)
- **codecov.io** - Code coverage badges
- **GitHub native** - Stars, issues, commits, contributors

**Badge Updates:**

When updating or adding badges:

1. Test badge URL displays correctly
1. Verify linked destination is accurate
1. Maintain category organization with HTML comments
1. Keep consistent badge styles (flat, default shields.io)
1. Update this documentation if adding new categories

## Common Tasks

### Adding a New Dependency

```bash
# Add to pyproject.toml [project.dependencies]
# Then install
make install-dev

# Commit changes
git add pyproject.toml
git commit -m "Add new-package dependency"
```

### Updating Dependencies

The project includes an automated dependency update script:

```bash
# Check for available updates
make deps-check

# Apply updates (with test validation)
make deps-update

# Apply updates with full tox validation
make deps-update-full
```

**Manual updates:**

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python packages
uv lock --upgrade

# Verify changes
pytest && tox -p auto
```

**What the script does:**

- Checks pre-commit hook versions
- Checks Python package versions via pip/PyPI
- Reports available updates with version info
- Flags major version changes (⚠️ MAJOR)
- Optionally applies updates
- Optionally runs tests to verify compatibility
- Optionally runs full tox validation

**Update schedule:**

- Monthly: Regular dependency updates
- Quarterly: Major version updates (thorough testing)
- Immediately: Security patches

See [CONTRIBUTING.md](CONTRIBUTING.md#updating-dependencies) for detailed update process.

### Adding a New Test

```bash
# Create test file in tests/unit/ or tests/integration/
# Follow naming convention: test_*.py

# Run new tests
pytest tests/unit/test_new_feature.py

# Run with coverage
pytest --cov tests/unit/test_new_feature.py
```

### Adding a New Report Type

1. Create new file in `src/nhl_scrabble/reports/`
1. Inherit from `BaseReport`
1. Implement `generate()` method
1. Add to report orchestration in CLI
1. Add tests in `tests/unit/`

### Updating Documentation

```bash
# Edit Markdown files in docs/
# Update docstrings in Python code

# Build Sphinx documentation
make docs

# Serve with auto-rebuild for development
make serve-docs  # http://localhost:8000

# Check spelling
tox -e docs -- -b spelling

# Regenerate API/CLI docs if changed
make docs-api    # After docstring updates
make docs-cli    # After CLI option changes

# Commit documentation updates
git commit -m "docs: Update documentation for feature X"
```

## Troubleshooting

### UV Not Found

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or fall back to pip
make init  # Uses pip instead of uv
```

### Tests Failing

```bash
# Run with verbose output
pytest -vv

# Run specific test
pytest tests/unit/test_scrabble.py::test_specific -vv

# Check for import errors
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"
```

### Pre-commit Hooks Failing

```bash
# Run manually to see errors
make pre-commit

# Fix formatting
make ruff-format

# Re-run hooks
make pre-commit
```

### Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .

# Or reinstall with dev dependencies
make install-dev

# Verify installation
python -c "import nhl_scrabble"
```

## Performance Optimization

### UV via Tox-UV Benefits

The project uses UV automatically via tox-uv:

| Component        | Standard | With tox-uv | Speedup  |
| ---------------- | -------- | ----------- | -------- |
| Tox environments | 60s      | 8s          | **7.5x** |
| Tox parallel     | 5min     | 30s         | **10x**  |
| CI/CD pipeline   | 12min    | 3min        | **4x**   |

### Recommendations

1. **Use tox** for all testing: UV acceleration is automatic via tox-uv
1. **Parallel testing**: `make tox-parallel` for 10x speedup
1. **Enable caching** in CI: UV caching configured in GitHub Actions
1. **Use tox for running**: `make run`, `make docs`, etc. use tox internally
1. **Direct tox usage**: For specific testenvs, use `tox -e <env>` directly

## Project Statistics

- **Package:** nhl-scrabble 2.0.0
- **Python:** 3.12, 3.13, 3.14 (supported), 3.15-dev (experimental)
- **Lines of Code:** ~1,866 (src)
- **Lines of Tests:** ~680 (tests)
- **Test Coverage:** 49.93% overall, >90% on core modules
- **Modules:** 15 core modules
- **Tests:** 36 tests (100% passing)
- **Makefile Targets:** 55 documented targets (16 logical groupings)
- **Pre-commit Hooks:** 61 hooks (meta, file quality, Python quality, Python imports, project validation, YAML linting, JSON/YAML schema validation, spelling, markdown, documentation, UV, flake8, autoflake, black, docformatter, pyupgrade, refurb, ruff, mypy, ty, interrogate, deptry, unimport, pydocstyle, vulture, blocklint, gitlint, bandit, safety)
- **Dependency Lock:** uv.lock with 1,957 lines
- **Documentation:** 12 comprehensive guides
- **CI/CD:** GitHub Actions with UV optimization

## External Resources

- **Repository:** https://github.com/bdperkin/nhl-scrabble
- **Issues:** https://github.com/bdperkin/nhl-scrabble/issues
- **NHL API:** https://api-web.nhle.com/
- **UV:** https://github.com/astral-sh/uv
- **Tox:** https://tox.wiki/
- **Ruff:** https://github.com/astral-sh/ruff

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

Quick summary:

1. Fork repository
1. Create feature branch
1. Make changes with tests
1. Run `make check` (quality + tests)
1. Submit pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

______________________________________________________________________

**Note for Claude Code:** This project is well-structured with modern Python practices, comprehensive testing, and extensive automation. The UV ecosystem provides 10-100x speedups across all workflows. All common tasks are automated via the Makefile with 55 documented targets organized in 16 logical groupings. Use `make help` to see all available commands. The Makefile uses a dynamic pattern rule (`tox-%`) that automatically handles any tox environment, making it future-proof and maintainable.
