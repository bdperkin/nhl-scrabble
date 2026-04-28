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

**Note:** [UV](https://docs.astral.sh/uv/) acceleration is automatic when using [tox](https://tox.wiki/) (via [tox-uv](https://github.com/tox-dev/tox-uv) plugin). See [docs/UV.md](docs/UV.md) for details.

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

See [docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) for complete details on branch protection, admin commits, and the pre-commit hook workflow.

**Required CI Checks:**

- Pre-commit hooks (67 hooks)
- Python 3.12 tests
- Python 3.13 tests
- Python 3.14 tests
- Python 3.15-dev tests (experimental, non-blocking)
- All tox environments

**Before creating a PR:**

**Option 1: Automated Pre-Flight Validation** (Recommended)

Use the `/implement-task` skill which automatically validates before pushing:

- ✅ Runs all pre-commit hooks automatically
- ✅ Runs all tox environments (py3.12-3.15, ruff, mypy, coverage)
- ✅ Only pushes if all validation passes
- ✅ Saves 10-15 minutes per PR by catching issues locally
- ✅ ~95% first-time CI pass rate

**Time investment**: 3-5 minutes

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

### Making Changes

1. **Write your code** following the [code style guidelines](docs/contributing/code-style.md)
1. **Add tests** for any new functionality (see [testing guidelines](docs/contributing/testing-guidelines.md))
1. **Update documentation** if needed
1. **Run tests** to ensure everything works (see [how to run tests](docs/how-to/run-tests.md))

### Testing

Quick reference:

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

**Detailed testing guides:**

- [How to Run Tests](docs/how-to/run-tests.md) - Test execution methods
- [How to Run Benchmarks](docs/how-to/run-benchmarks.md) - Performance testing
- [Testing Guidelines](docs/contributing/testing-guidelines.md) - Test structure and coverage
- [Flaky Tests](docs/testing/flaky-tests.md) - Handling intermittent failures

**Enhanced test features:**

- **pytest-sugar**: Real-time progress bars and colored output
- **pytest-clarity**: Clearer assertion diffs
- **pytest-timeout**: Prevents tests from hanging (10s default)
- **pytest-xdist**: Parallel execution (~2.8x faster locally)
- **pytest-randomly**: Randomizes test order to catch hidden dependencies
- **pytest-benchmark**: Performance regression tracking

### Multi-Environment Testing with Tox

Quick reference:

```bash
make tox              # Default: parallel with fail-fast dependencies
make tox-parallel     # Pure parallel (all environments)
make tox-sequential   # Sequential (for debugging)
make tox-quick        # Critical checks only (fast fail-fast)

# Run specific tier
tox -m critical       # Fast quality checks only
tox -m test          # Just tests

# Test specific Python version
tox -e py312
tox -e py315
```

See [docs/TOX.md](docs/TOX.md) for complete tox documentation and [docs/TOX-UV.md](docs/TOX-UV.md) for tox with UV acceleration (10x faster).

### Code Quality

Before committing, ensure your code passes all quality checks:

```bash
# Format code with ruff
make ruff-format

# Check for linting issues
make ruff-check

# Fix auto-fixable issues
ruff check --fix .

# Type check with mypy
make mypy

# Type check with ty (Astral's fast type checker)
make ty

# Comprehensive type checking (ty + mypy)
make type-check

# Run pre-commit hooks manually
pre-commit run --all-files
```

**Detailed guides:**

- [Code Style Guidelines](docs/contributing/code-style.md) - Python style, docstrings, type hints, class ordering
- [Commit Message Guidelines](docs/contributing/commit-messages.md) - Conventional commits format
- [Logging Guidelines](docs/contributing/logging-guidelines.md) - Proper log level usage

**Pre-commit hooks:** The project uses 67 comprehensive pre-commit hooks. See [docs/PRECOMMIT-UV.md](docs/PRECOMMIT-UV.md) for UV-accelerated pre-commit usage (9x faster).

**Code modernization tools:**

- **pyupgrade**: Modernizes Python syntax for Python 3.12+
- **refurb**: Suggests better code patterns (pathlib, comprehensions)
- **ssort**: Sorts class members automatically
- **add-trailing-comma**: Adds trailing commas for better git diffs

**HTML/Template quality:**

- **djlint**: Lints and formats HTML/Jinja2 templates

**Configuration validation:**

- **check-jsonschema**: Validates JSON/YAML configs against official schemas

**Security scanning:**

- **bandit**: Scans Python code for security vulnerabilities
- **safety**: Scans dependencies for known CVEs

## Documentation

When adding new features:

1. **Add docstrings** to all new code (100% coverage required)
1. **Regenerate API/CLI docs** after docstring or CLI changes
1. **Create how-to guide** if it solves a specific problem
1. **Update reference** docs if adding new CLI options or configuration
1. **Update CHANGELOG.md** with user-facing changes

### Building Documentation

```bash
# Build HTML documentation
make docs

# Serve with auto-rebuild (recommended for development)
make serve-docs
# Visit http://localhost:8000

# Check documentation spelling
tox -e docs -- -b spelling
```

### Regenerating Auto-Generated Documentation

**After updating docstrings:**

```bash
make docs-api  # Regenerate API reference
```

**After changing CLI commands or options:**

```bash
make docs-cli  # Regenerate CLI reference
```

**Check if docs are up-to-date:**

```bash
make docs-check  # Fails if you forgot to regenerate
```

See [docs/how-to/build-documentation.md](docs/how-to/build-documentation.md) for complete documentation build guide.

## Pull Request Process

### Before Submitting

Checklist before creating a PR:

1. ✅ All tests pass
1. ✅ Code coverage is maintained or improved
1. ✅ Code is formatted with ruff
1. ✅ No linting errors
1. ✅ Type checking passes
1. ✅ Documentation is updated
1. ✅ Commit messages are clear
1. ✅ Branch is up-to-date with main

### Submitting

1. Push your branch: `git push origin feature/your-feature-name`
1. Create pull request on GitHub
1. Fill out the PR template
1. Address review feedback

See [docs/contributing/pull-requests.md](docs/contributing/pull-requests.md) for complete PR process, review criteria, Dependabot PR handling, and stale issue/PR policy.

## Common Tasks

### Adding a New Report Type

1. Create new reporter class in `src/nhl_scrabble/reports/`
1. Inherit from `BaseReporter`
1. Implement `generate()` method
1. Add to `__init__.py` exports
1. Integrate into CLI
1. Add tests
1. Update documentation

See [docs/how-to/add-report-type.md](docs/how-to/add-report-type.md) for step-by-step guide.

### Adding a New Configuration Option

1. Add field to `Config` dataclass in `config.py`
1. Add environment variable parsing in `from_env()`
1. Add CLI option in `cli.py`
1. Update documentation
1. Add tests

See [docs/reference/configuration.md](docs/reference/configuration.md) for configuration reference.

### Fixing a Bug

1. Create issue on GitHub (if not exists)
1. Write a failing test that reproduces the bug
1. Fix the bug
1. Verify test now passes
1. Add regression test
1. Submit PR referencing the issue

### Git Branch Cleanup

After PRs are merged, clean up local branches:

```bash
# Check branch status (merged vs active)
make git-status-branches

# Prune stale remote tracking branches
make git-prune-remote-refs

# Delete local branches merged to main
make git-prune-local

# Delete branches from closed (not merged) PRs
make git-prune-closed-prs

# Standard cleanup (remote refs + merged branches)
make git-cleanup

# Complete cleanup (includes closed PR branches)
make git-cleanup-all
```

The repository uses automated branch cleanup with `git config fetch.prune true`. See [docs/MAKEFILE.md](docs/MAKEFILE.md) for complete Makefile documentation.

## Updating Dependencies

We keep dependencies up-to-date for security and features.

### Quick Start

```bash
# Check for available updates
make deps-check

# Apply updates (with tests)
make deps-update

# Apply updates with full tox validation
make deps-update-full
```

See [docs/contributing/dependency-updates.md](docs/contributing/dependency-updates.md) for complete dependency update process, schedules, and pre-commit hook automation.

## Release Process

(For maintainers)

### Automated Release Workflow

The project uses **automated PyPI publishing** via GitHub Actions. Releases are triggered by pushing version tags.

**Time Savings:**

- **Before:** 30 minutes, 9 manual steps
- **After:** 5 minutes, 2 steps (tag + push)

### Quick Release Steps

```bash
# 1. Update CHANGELOG.md with release notes
vim CHANGELOG.md

# 2. Commit changelog
git add CHANGELOG.md
git commit -m "docs(changelog): Add v2.1.0 release notes"
git push origin main

# 3. Create and push version tag
git tag -a v2.1.0 -m "Release version 2.1.0"
git push --tags

# That's it! The workflow automatically:
# ✅ Builds sdist and wheel distributions
# ✅ Verifies package metadata
# ✅ Tests installation on 3 OS × 3 Python versions
# ✅ Publishes to TestPyPI
# ✅ Publishes to PyPI
# ✅ Creates GitHub Release with artifacts
```

**Note:** This project uses **dynamic versioning** from Git tags via hatch-vcs. No manual version updates needed!

**Complete Documentation:**

- [docs/RELEASING.md](docs/RELEASING.md) - Complete release guide with troubleshooting
- [docs/contributing/release-process.md](docs/contributing/release-process.md) - Additional release details

**Workflow File:** `.github/workflows/publish.yml`

### Version Requirements

The project uses **hatch-vcs** for dynamic versioning from Git tags. A pre-commit hook (`check-version-consistency`) validates the following requirements:

**1. Auto-generated `_version.py` Not Committed**

- **Why**: hatch-vcs generates this file at build time from Git tags
- **Rule**: Never commit `src/nhl_scrabble/_version.py`
- **Fix**: `git rm --cached src/nhl_scrabble/_version.py`

**2. Dynamic Versioning in `pyproject.toml`**

- **Why**: Required for hatch-vcs to manage versions
- **Rule**: `pyproject.toml` must contain:
  ```toml
  [project]
  dynamic = ["version"]

  [tool.hatch.version]
  source = "vcs"
  ```
- **Fix**: Restore configuration if accidentally removed

**3. No Hardcoded Version Strings**

- **Why**: Defeats the purpose of dynamic versioning
- **Rule**: Don't use `__version__ = "1.2.3"` in code
- **Allowed**: `from nhl_scrabble._version import __version__`
- **Fix**: Import from `_version.py` instead of hardcoding

**4. Git Tags Follow Semantic Versioning**

- **Why**: hatch-vcs expects `vX.Y.Z` format
- **Rule**: Tags must match pattern `vX.Y.Z` (e.g., `v2.1.0`, `v1.0.0-rc1`)
- **Fix**: Delete malformed tag and create correct one:
  ```bash
  git tag -d 0.1.0           # Delete wrong tag (missing 'v' prefix)
  git tag -a v0.1.0 -m "..."  # Create correct tag
  ```

**Validation:**

The pre-commit hook runs automatically on every commit. To test manually:

```bash
python .pre-commit-hooks/check-version-consistency.py
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

### Dependency License Policy

**Runtime Dependencies** (distributed with the package):

- ✅ **Allowed**: MIT, Apache 2.0, BSD (2-clause, 3-clause), ISC, PSF, MPL-2.0, Unlicense, Public Domain
- ❌ **Prohibited**: GPL, LGPL, AGPL (copyleft), Proprietary

**Development Dependencies** (build/test tools only):

- More flexible, but document any non-permissive licenses with justification
- Must not be distributed with or statically linked into the package

**Verification**:

```bash
# Check all licenses
tox -e licenses
```

CI will automatically fail if prohibited licenses are detected in runtime dependencies.

## Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for questions or ideas
- Check existing issues/discussions first

## Using the Makefile

The project includes a comprehensive Makefile with 57 targets organized in 16 logical groupings:

### Quick Reference

```bash
# Setup
make init              # Initialize development environment
make install-dev       # Install with dev dependencies
make install-hooks     # Install pre-commit hooks

# Development
make test              # Run all tests
make test-cov          # Run tests with coverage
make ruff-check        # Run linter
make ruff-format       # Format code
make type-check        # Type check (ty + mypy)
make check             # Run all checks before commit

# Cleaning
make clean             # Clean all artifacts
make clean-all         # Clean everything including venv

# Building
make build             # Build distribution packages
make package           # Build and validate package
make ci                # Simulate CI pipeline locally
```

See [docs/MAKEFILE.md](docs/MAKEFILE.md) for complete documentation of all 57 targets.

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

______________________________________________________________________

Thank you for contributing to NHL Scrabble! 🏒🎯

## Additional Resources

- [Branch Protection Guide](docs/BRANCH_PROTECTION.md) - Protected branches and PR workflow
- [Development Guide](docs/DEVELOPMENT.md) - Comprehensive development documentation
- [Makefile Reference](docs/MAKEFILE.md) - All 57 Makefile targets documented
- [TOX Guide](docs/TOX.md) - Multi-environment testing
- [TOX-UV Guide](docs/TOX-UV.md) - UV-accelerated testing (10x faster)
- [UV Ecosystem](docs/UV-ECOSYSTEM.md) - UV configuration and philosophy
- [Pre-commit with UV](docs/PRECOMMIT-UV.md) - UV-accelerated pre-commit (9x faster)
- [How-to Guides](docs/how-to/) - Problem-oriented solutions
- [Reference Documentation](docs/reference/) - Technical specifications
- [Explanation Documentation](docs/explanation/) - Conceptual understanding
- [Tutorials](docs/tutorials/) - Learning-oriented lessons
