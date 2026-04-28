# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

NHL Scrabble Score Analyzer is a Python package that fetches NHL roster data and calculates "Scrabble scores" for player names, generating reports with team/division/conference standings and playoff brackets.

**Tech Stack:**

- Python 3.12-3.14 (supported), 3.15-dev (experimental)
- UV for 10-100x faster dependency management
- Pydantic models, Click CLI, Rich terminal output
- 80 pre-commit hooks (12 for Bash quality & security), comprehensive CI/CD
- Dynamic versioning from Git tags (hatch-vcs)

## Quick Start

```bash
# Setup
make init && source .venv/bin/activate

# Run
nhl-scrabble analyze

# Test
make test          # Quick pytest
make tox          # All environments (UV-accelerated)

# Quality
make quality       # All checks
make pre-commit    # Run hooks
```

## Architecture

### Package Structure

```
src/nhl_scrabble/
├── api/              # NHL API client (retry logic, rate limiting)
├── models/           # Pydantic data models
├── scoring/          # Scrabble scoring logic
├── processors/       # Business logic (team/playoff processing)
├── reports/          # Report generators (Rich output)
├── cli.py            # Click-based CLI
├── config.py         # Configuration management
└── di.py             # Protocol-based dependency injection
```

### Key Patterns

**Dependency Injection:** Protocol-based (PEP 544) for testability. Use `DependencyContainer` to create/inject dependencies.

**API Client:** Context manager with retry logic, exponential backoff, 0.3s rate limiting.

**Reports:** Inherit from `BaseReport`, implement `generate()`. Support text/JSON formats.

## Development Commands

### Essential Make Targets

```bash
make help            # All targets with descriptions

# Setup
make init            # pip setup
make uv-init         # UV setup (10-100x faster)

# Testing
make test            # pytest (parallel)
make tox             # All environments (tier-based fail-fast)
make tox-quick       # Critical checks only
make ci              # CI simulation

# Quality
make quality         # All quality checks
make ruff-check      # Linting
make ruff-format     # Formatting
make type-check      # mypy + ty

# Bash Script Quality
make bash-validate   # All Bash quality checks
make bash-fix        # Auto-format Bash scripts
make beautysh        # Format Bash scripts
make bashate         # Lint Bash scripts
make bash-docs       # Validate documentation
make bash-deps       # Check dependencies

# Maintenance
make deps-check      # Check for updates
make licenses-check  # Validate licenses
make git-cleanup     # Clean merged branches
```

### Tox Environments

```bash
tox -e py312         # Python 3.12
tox -e coverage      # Coverage report
tox -e diff-cover    # PR coverage (≥80% enforced)
tox -m critical      # Critical checks only
tox -m test          # All tests
```

## Critical Rules

### Pre-commit Hooks (80 total)

All hooks run automatically on commit. **Never bypass quality checks.**

```bash
# ✅ CORRECT: Admin commits skip only branch protection
SKIP=check-branch-protection git commit -m "message"

# ❌ NEVER: Bypasses ALL quality checks
git commit --no-verify -m "message"
```

Categories: Meta (3), file quality (18), Python quality (7), imports (2), project validation (4), YAML (1), schema validation (4), spelling (1), markdown (2), documentation (9), formatters (5), linters (4), type checking (2), version validation (1), **Bash quality & security (12)**.

See memory for details or `docs/contributing/pre-commit-hooks.md`.

### Versioning

**Dynamic versioning from Git tags** (hatch-vcs):

```bash
# Create release
git tag -a v0.1.0 -m "Release notes"
git push --tags
# CI auto-publishes to PyPI

# Version detection requires fetch-depth: 0 in CI
```

Version shows as `0.1.1.dev3+g<hash>` between releases. Never manually edit version in pyproject.toml.

### Branch Protection

**Main branch:** PRs required, all CI must pass, no force push. Admin bypass allowed for post-merge cleanup only.

### Code Quality

- **100% docstring coverage** (interrogate)
- **Strict type checking** (mypy + ty)
- **≥80% diff coverage** on PRs (enforced in CI)
- **Conventional Commits** for changelog generation
- **PEP 8** via ruff, black, autopep8

## Development Workflow

### Daily Development

```bash
source .venv/bin/activate
# Make changes...
pytest                    # Quick tests
make quality              # Check quality
git commit -m "feat: ..." # Conventional Commits
```

### Before PR

**Option 1:** Use `/implement-task` skill (95% first-time CI pass, auto-validates)

**Option 2:** Manual validation

```bash
make tox-parallel    # Full test suite
make check           # All quality checks
pre-commit run --all-files
```

### Git Cleanup

```bash
make git-status-branches    # Check branch status
make git-cleanup            # Clean merged branches
make git-cleanup-all        # Include closed PRs
```

## Configuration

### pyproject.toml

Central configuration for project, ruff, mypy, pytest, tox, coverage, etc.

### Environment Variables

```bash
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
NHL_SCRABBLE_TOP_PLAYERS=30
NHL_SCRABBLE_VERBOSE=true
```

## CI/CD

### GitHub Actions

- **Test:** py3.12-3.14 (required), py3.15-dev (experimental, non-blocking)
- **Quality:** ruff-check, mypy, coverage, pre-commit
- **Performance:** UV acceleration (12min → 3min pipeline)
- **Coverage:** Codecov (~50% total), diff-cover (≥80% on PRs)

### Security

- **CodeQL:** Weekly scans + PR checks
- **Dependabot:** Weekly updates (Mondays 9 AM ET)
- **Dependency Review:** Automated PR checks for vulnerabilities and license compliance
- **pip-audit:** Dependency vulnerability scanning
- **Secret scanning:** Detects committed secrets
- **SBOM Generation:** Automated Software Bill of Materials for supply chain transparency

**Dependency Review Workflow:**

- Triggers on PRs modifying `pyproject.toml`, `uv.lock`, or `requirements*.txt`
- Scans for security vulnerabilities (fails on moderate+ severity)
- Validates license compliance (allows: MIT, Apache-2.0, BSD, ISC, Python-2.0; denies: GPL-3.0, AGPL-3.0)
- Posts detailed findings as PR comments
- Enforces security and compliance policies before merge

**SBOM Workflow:**

- Generates CycloneDX (JSON/XML) and SPDX (JSON) formats
- Triggers: Weekly (Mondays 6 AM UTC), releases, dependency changes, manual
- Includes complete dependency tree with license information
- Vulnerability scanning with Grype
- Artifacts retained 90 days, attached to releases permanently
- Location: GitHub Actions artifacts and release assets

**Benchmark Workflow:**

- Automated performance regression testing on PRs
- Compares PR performance vs main branch baseline
- Posts detailed comparison comment on PRs
- Highlights regressions (>10% slower) and improvements (>10% faster)
- Fails CI on significant regressions (>20% slower)
- Stores baseline from main branch (90-day retention)
- Triggers: PRs/pushes affecting `src/**/*.py`, `tests/benchmarks/**`, `pyproject.toml`
- Uses pytest-benchmark with 5+ rounds and warmup
- Results uploaded as artifacts for historical tracking

### Publishing

Triggered by version tags (`v*`):

- Auto-builds sdist/wheel
- Tests on 3 OS × 3 Python versions
- Publishes to PyPI via OIDC (no tokens)
- Generates CHANGELOG.md with git-cliff
- Creates GitHub release

## Documentation

**Online:** https://bdperkin.github.io/nhl-scrabble/

Organized via Diátaxis framework:

- **Tutorials:** Getting started, understanding output, first contribution
- **How-to:** Installation, testing, benchmarks, UV usage
- **Reference:** CLI, configuration, Makefile, environment variables
- **Explanation:** Architecture, design decisions, philosophy

```bash
make docs           # Build Sphinx docs
make serve-docs     # http://localhost:8000
make docs-api       # Regenerate API docs
```

## Common Tasks

### Add Dependency

```bash
# Edit pyproject.toml [project.dependencies]
make install-dev
git commit pyproject.toml -m "feat: add dependency"
```

### Update Dependencies

```bash
make deps-check        # Check updates
make deps-update       # Apply with test validation
make deps-update-full  # Apply with tox validation
```

### Add Test

```bash
# Create tests/unit/test_feature.py or tests/integration/test_feature.py
pytest tests/unit/test_feature.py --cov
```

### Add Report Type

1. Create `src/nhl_scrabble/reports/new_report.py`
1. Inherit from `BaseReport`
1. Implement `generate()` method
1. Add to CLI orchestration
1. Add tests

## NHL API Integration

**Endpoints:**

- Standings: `https://api-web.nhle.com/v1/standings/now`
- Roster: `https://api-web.nhle.com/v1/roster/{team_abbrev}/current`

**Handling:** Retry logic, exponential backoff, 0.3s rate limiting, graceful degradation.

## Scrabble Scoring

Standard Scrabble letter values (A=1, E=1, ..., Q=10, Z=10). Full name scored as first + last.

```python
from nhl_scrabble.scoring import ScrabbleScorer

scorer = ScrabbleScorer()
score = scorer.calculate_score("Ovechkin")
```

## Playoff Logic

Replicates NHL playoff structure:

- Top 3 per division (automatic)
- 2 wild cards per conference
- Indicators: y (division leader), x (wild card), z (conference leader), p (Presidents' Trophy), e (eliminated)

Tiebreaker: Average points per player, then alphabetical.

## Performance

**UV Benefits (via tox-uv):**

- Tox environments: 60s → 8s (7.5x)
- Tox parallel: 5min → 30s (10x)
- CI pipeline: 12min → 3min (4x)

**Test Performance:**

- 170 tests: 131s sequential → 47s parallel (2.8x on 8 cores)
- pytest-xdist with `-n auto` for parallel execution

## Project Stats

- ~1,866 lines of code, ~680 lines of tests
- 49.93% overall coverage, >90% on core modules
- 170 tests, 100% passing
- 117+ Makefile targets in 19 groupings (Shell Scripting section added)
- 80 pre-commit hooks (12 for Bash quality & security)
- 1,957-line uv.lock file

## Resources

- **Repo:** https://github.com/bdperkin/nhl-scrabble
- **Issues:** https://github.com/bdperkin/nhl-scrabble/issues
- **Docs:** https://bdperkin.github.io/nhl-scrabble/
- **PyPI:** https://pypi.org/project/nhl-scrabble/
- **Coverage:** https://app.codecov.io/gh/bdperkin/nhl-scrabble

## Contributing

See `CONTRIBUTING.md` and `docs/contributing/` for detailed guidelines.

Quick: Fork → feature branch → changes + tests → `make check` → PR

______________________________________________________________________

**Note for Claude:** Project uses modern Python practices with extensive automation. UV provides 10-100x speedups. Use `make help` for all commands. Pre-commit hooks and tox are UV-accelerated. Bash scripts have comprehensive quality tooling (beautysh formatting, bashate linting, security patterns, documentation validation). Check memory for detailed workflow/configuration information.
