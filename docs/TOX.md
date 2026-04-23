# Tox Testing Guide

This guide covers using [tox](https://tox.wiki/) for automated testing across multiple Python environments.

## Table of Contents

- [What is Tox?](#what-is-tox)
- [Quick Start](#quick-start)
- [Available Environments](#available-environments)
- [Common Usage Patterns](#common-usage-patterns)
- [Makefile Integration](#makefile-integration)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

## What is Tox?

Tox is a command-line tool that automates and standardizes testing in Python. It:

- **Tests across multiple Python versions** (3.10, 3.11, 3.12, 3.13, 3.14, 3.15)
- **Creates isolated environments** for each test run
- **Automates quality checks** (linting, type checking, formatting)
- **Simulates CI/CD pipelines** locally before pushing code
- **Manages dependencies** consistently across environments

## Quick Start

### Installation

Tox is included in the development dependencies:

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or install tox separately
pip install tox
```

### Basic Usage

```bash
# Run all default test environments
tox

# List all available environments
tox list

# Run in parallel (faster!)
tox -p auto

# Run specific environment
tox -e py310
```

## Available Environments

### Default Environments (11)

These run when you execute `tox` without arguments:

| Environment   | Python Version | Description                       |
| ------------- | -------------- | --------------------------------- |
| `py310`       | 3.10           | Run tests with Python 3.10        |
| `py311`       | 3.11           | Run tests with Python 3.11        |
| `py312`       | 3.12           | Run tests with Python 3.12        |
| `py313`       | 3.13           | Run tests with Python 3.13        |
| `py314`       | 3.14           | Run tests with Python 3.14        |
| `py315`       | 3.15           | Run tests with Python 3.15        |
| `ruff-check`  | (any)          | Run ruff linter                   |
| `mypy`        | (any)          | Run mypy type checker             |
| `ruff-format` | (any)          | Check code formatting with ruff   |
| `coverage`    | (current)      | Run tests with coverage reporting |
| `pip-audit`   | (any)          | Run security audit with pip-audit |

**Total: 11 default testenvs**

### Additional Environments (15)

These are available but don't run by default:

| Environment       | Description                   | Command                  |
| ----------------- | ----------------------------- | ------------------------ |
| `unit`            | Run unit tests only           | `tox -e unit`            |
| `integration`     | Run integration tests only    | `tox -e integration`     |
| `ruff-format-fix` | Auto-format code with ruff    | `tox -e ruff-format-fix` |
| `check`           | Run all checks before commit  | `tox -e check`           |
| `docs`            | Build Sphinx documentation    | `tox -e docs`            |
| `serve-docs`      | Build and serve docs locally  | `tox -e serve-docs`      |
| `clean`           | Remove build artifacts        | `tox -e clean`           |
| `build`           | Build distribution packages   | `tox -e build`           |
| `run`             | Run the NHL Scrabble analyzer | `tox -e run`             |
| `ci`              | Simulate full CI pipeline     | `tox -e ci`              |
| `fast`            | Quick test run (no coverage)  | `tox -e fast`            |
| `watch`           | Run tests in watch mode       | `tox -e watch`           |
| `publish-test`    | Publish to TestPyPI           | `tox -e publish-test`    |
| `publish`         | Publish to PyPI (caution!)    | `tox -e publish`         |
| `version`         | Display package version       | `tox -e version`         |

**Total: 15 additional testenvs**

**Grand Total: 26 testenvs** (11 default + 15 additional)

## Common Usage Patterns

### Pre-Commit Workflow

Before committing code, verify everything works:

```bash
# Option 1: Run quality checks and tests
tox -e quality,py310

# Option 2: Use the comprehensive check environment
tox -e check

# Option 3: Simulate full CI pipeline
tox -e ci
```

### Testing Across Python Versions

```bash
# Test against all Python versions
tox -e py310,py311,py312,py313,py314,py315

# Test in parallel (much faster!)
tox -p auto -e py310,py311,py312,py313,py314,py315

# Test specific version only
tox -e py310
tox -e py315
```

### Code Quality Checks

```bash
# Run linter only
tox -e ruff-check

# Run type checker only
tox -e mypy

# Check code formatting
tox -e ruff-format

# Run all quality checks together
tox -e quality

# Auto-fix formatting issues
tox -e format-fix
```

### Coverage Reporting

```bash
# Generate coverage report
tox -e coverage

# View in browser (opens htmlcov/index.html)
# The coverage command prints the file:// URL at the end
```

### Running the Application

```bash
# Run the analyzer through tox
tox -e run

# Run with arguments
tox -e run -- --verbose
tox -e run -- --format json --output report.json
```

### Cleaning and Rebuilding

```bash
# Clean all tox environments
tox -e clean

# Recreate environments (useful after dependency changes)
tox -r

# Recreate specific environment
tox -e py310 -r

# Remove .tox directory entirely
rm -rf .tox/
```

## Makefile Integration

All tox commands are available through the Makefile for convenience. The Makefile now uses a **dynamic pattern rule** (`tox-%`) that automatically handles any tox environment.

### Basic Testing

```bash
make tox              # Run all default environments
make tox-parallel     # Run in parallel
make tox-list         # List all environments
make tox-envs         # List all environments (alternative)
```

### Python Version Testing

The Makefile uses a dynamic pattern rule that automatically handles any Python version:

```bash
# Via Makefile (dynamic pattern rule - automatically handled)
make tox-py310        # Test Python 3.10
make tox-py311        # Test Python 3.11
make tox-py312        # Test Python 3.12
make tox-py313        # Test Python 3.13
make tox-py314        # Test Python 3.14
make tox-py315        # Test Python 3.15
make tox-py316        # Future Python 3.16 (will work automatically!)

# Or use tox directly:
tox -e py310          # Test Python 3.10
tox -e py311          # Test Python 3.11
tox -e py312          # Test Python 3.12
tox -e py313          # Test Python 3.13
tox -e py314          # Test Python 3.14
tox -e py315          # Test Python 3.15
```

### Quality Checks

Quality check targets are now handled by the dynamic pattern rule:

```bash
# Via Makefile (dynamic pattern rule - automatically handled)
make tox-ruff-check   # Run linter
make tox-mypy         # Run type checker
make tox-coverage     # Generate coverage report
make tox-quality      # All quality checks

# Or use tox directly:
tox -e ruff-check     # Run linter
tox -e mypy           # Run type checker
tox -e coverage       # Generate coverage report
```

### CI Simulation

```bash
make ci               # Simulate CI pipeline (traditional)
make tox-ci           # Simulate CI with tox (via dynamic pattern rule)
# Or use tox directly:
tox -e ci             # Simulate full CI pipeline
```

### Maintenance

```bash
make tox-clean        # Clean tox environments
make tox-recreate     # Recreate all environments
```

### Dynamic Pattern Rule Benefits

The `tox-%` pattern rule provides:

- **Automatic support** for any tox environment
- **Future-proof** - new Python versions work automatically
- **No maintenance** - add environments to `tox.ini`, Makefile works automatically
- **Discoverable** - use `make tox-envs` to see all available environments

## Configuration

### tox.ini

The tox configuration is in `tox.ini` at the project root. Key sections:

```ini
[tox]
# Python versions to test
envlist = py{310,311,312,313,314,315}, ruff-check, mypy, ruff-format, coverage, pip-audit

# Shared settings
minversion = 4.0
isolated_build = true
skip_missing_interpreters = true
```

### Customizing Environments

To modify an environment, edit `tox.ini`:

```ini
[testenv:coverage]
description = Run tests with coverage reporting
deps = {[testenv]deps}
commands =
    pytest --cov=nhl_scrabble --cov-fail-under=80
```

### Adding New Environments

Add a new section to `tox.ini`:

```ini
[testenv:myenv]
description = My custom environment
deps =
    pytest
commands =
    pytest -k my_test
```

## Troubleshooting

### Python Version Not Available

If you see "InterpreterNotFound":

```bash
# Check which Python versions are installed
python3.10 --version
python3.11 --version
python3.12 --version
python3.13 --version
python3.14 --version
python3.15 --version

# Skip missing interpreters (configured by default)
tox --skip-missing-interpreters

# Or test only available versions
tox -e py310  # If you only have 3.10
tox -e py315  # If you only have 3.15
```

### Dependency Conflicts

If you encounter dependency issues:

```bash
# Recreate the environment
tox -e py310 -r

# Or recreate all environments
tox -r

# Or delete and rebuild from scratch
rm -rf .tox/
tox
```

### Out of Date Environments

After changing dependencies in `pyproject.toml`:

```bash
# Recreate all environments
tox -r

# Or for specific environment
tox -e py310 -r
```

### Slow Test Runs

Speed up testing:

```bash
# Use parallel mode
tox -p auto

# Run only fast checks
tox -e fast

# Run specific environments
tox -e ruff-check,mypy  # Skip actual test runs
```

### Debugging Test Failures

```bash
# Run with verbose output
tox -e py310 -- -v

# Run with very verbose output
tox -e py310 -- -vv

# Run with output capture disabled
tox -e py310 -- -s

# Run specific test
tox -e py310 -- tests/unit/test_scrabble.py::test_specific
```

## CI/CD Integration

### GitHub Actions

Example workflow using tox:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13', '3.14', '3.15']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install tox
        run: pip install tox
      - name: Run tests
        run: tox -e py$(echo ${{ matrix.python-version }} | tr -d .)
```

### GitLab CI

Example `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.10
  script:
    - pip install tox
    - tox -p auto
```

### Local CI Simulation

Test exactly what CI will run:

```bash
# Simulate full CI pipeline
make tox-ci

# Or directly
tox -e ci
```

## Advanced Usage

### Running with Specific Options

Pass arguments to underlying commands:

```bash
# Pass pytest options
tox -e py310 -- -k test_scrabble -v

# Pass mypy options
tox -e mypy -- --strict

# Pass ruff options
tox -e ruff-check -- --fix
```

### Environment Variables

Set environment variables for tox:

```bash
# Pass to specific environment
TOX_SKIP_ENV="py311|py312" tox

# Set environment variable for tests
tox -e py310 -- --env-var=NHL_SCRABBLE_VERBOSE=true
```

### Combining Environments

Run multiple environments in sequence:

```bash
# Run quality checks then tests
tox -e quality,coverage

# Run for multiple Python versions
tox -e py310,py311,py312,py313,py314,py315
```

### Parallel Execution

```bash
# Auto-detect number of CPUs
tox -p auto

# Specify number of parallel workers
tox -p 4

# Parallel with specific environments
tox -p auto -e py310,py311,py312,py313,py314,py315,ruff-check,mypy
```

## Best Practices

### Daily Development

```bash
# Quick iteration during development
pytest  # Fast, use pytest directly

# Before committing
make tox-quality  # Check code quality

# Before pushing
make tox-ci  # Full CI simulation
```

### Pre-Release Checklist

```bash
# 1. Run all tests across all Python versions
make tox-parallel

# 2. Check code quality
make tox-quality

# 3. Generate coverage report
make tox-coverage

# 4. Run security audit
tox -e security

# 5. Build distribution
tox -e build
```

### Continuous Integration

- Use `tox -p auto` for faster CI runs
- Cache the `.tox` directory to speed up subsequent runs
- Run `tox -e ci` which includes all checks

## Resources

- [Tox Documentation](https://tox.wiki/)
- [Tox Configuration Reference](https://tox.wiki/en/latest/config.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Project Contributing Guide](../CONTRIBUTING.md)
- [Makefile Reference](MAKEFILE.md)

## Summary

Key commands to remember:

```bash
# Quick reference
tox                   # Run all default environments
tox -p auto           # Run in parallel (fastest)
tox -e ci             # Simulate CI pipeline
tox -e py310          # Test specific Python version
tox -e quality        # Run code quality checks
tox -e ruff-check     # Run linter
tox -e mypy           # Run type checker
tox -e coverage       # Generate coverage report
tox -r                # Recreate environments
tox list              # List all available environments
```

For daily development, use the Makefile shortcuts:

```bash
make tox-parallel     # Fastest multi-environment testing
make tox-ci           # Pre-push verification (via dynamic pattern rule)
make tox-quality      # Code quality checks (via dynamic pattern rule)
make tox-ruff-check   # Run linter (via dynamic pattern rule)
make tox-mypy         # Run type checker (via dynamic pattern rule)
make tox-envs         # List all available tox environments
```

**Note:** Tox environments use tool-based names (ruff-check, mypy, ruff-format, pip-audit) for clarity.

**Dynamic Pattern Rule:** The Makefile uses a `tox-%` pattern rule that automatically handles any tox environment, making it future-proof and maintainable. Any environment you add to `tox.ini` will automatically work with `make tox-<envname>`.
