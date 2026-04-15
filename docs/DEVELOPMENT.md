# Development Guide

This guide covers development workflows, best practices, and conventions for the NHL Scrabble project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Testing](#testing)
4. [Code Quality](#code-quality)
5. [UV Ecosystem](#uv-ecosystem)
6. [Documentation](#documentation)
7. [Release Process](#release-process)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

- **Python 3.10-3.15** - Required
- **Git** - Version control
- **Make** - For using the Makefile
- **UV** - Optional but recommended for 10-100x speedup

### Install UV (Recommended)

UV provides 10-100x faster package installation:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version

# Or check via Makefile
make uv-check
```

See [UV.md](UV.md) for complete UV documentation.

### Initial Setup

#### Fast Setup with UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Fast initialization (~5 seconds!)
make uv-init

# Activate virtual environment
source .venv/bin/activate
```

#### Traditional Setup

```bash
# Clone the repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Traditional initialization (~50 seconds)
make init

# Activate virtual environment
source .venv/bin/activate
```

The initialization commands will:
1. Create a virtual environment in `.venv/`
2. Install the package with development dependencies
3. Install pre-commit hooks

### Python Version

The project supports Python 3.10-3.15 as specified in `.python-version`:

```bash
# View the supported Python versions
cat .python-version  # Shows: 3.10, 3.11, 3.12, 3.13, 3.14, 3.15

# UV, pyenv, and asdf will automatically use these versions
# Ensure you have a supported Python version installed
python --version  # Should show 3.10.x - 3.15.x
```

### Verify Setup

```bash
# Run all checks
make check

# Should see:
# ✓ Format check passed
# ✓ Linting passed
# ✓ Type checking passed
# ✓ All tests passed

# Verify UV integration (if using UV)
make uv-check
tox --version  # Should show tox-uv plugin
```

## Development Workflow

### Daily Development

1. **Start your work session**
   ```bash
   # Pull latest changes
   git pull

   # Update dependencies if needed (fast with UV)
   make uv-update
   # or traditional
   make update

   # Create a feature branch
   git checkout -b feature/your-feature-name
   ```

2. **During development**
   ```bash
   # Run tests in watch mode (automatically rerun on changes)
   make test-watch

   # Or manually run tests
   make test

   # Or test across all Python versions (fast with tox-uv!)
   tox -e py310
   ```

3. **Before committing**
   ```bash
   # Run all checks
   make check

   # Or use pre-commit with UV acceleration
   make uv-pre-commit

   # If checks pass, commit
   git add .
   git commit -m "Your descriptive commit message"
   ```

4. **Before creating a PR**
   ```bash
   # Test across all Python versions in parallel (10x faster!)
   make tox-parallel

   # Simulate full CI pipeline
   make tox-ci

   # Push your branch
   git push origin feature/your-feature-name
   ```

### Makefile Commands

The project uses a comprehensive Makefile with **55 targets** organized in **16 logical groupings**. View all available commands:

```bash
make help
```

#### Key Commands

**Setup:**
- `make init` - Traditional setup (~50s)
- `make uv-init` - Fast setup (~5s)

**Testing:**
- `make test` - Run all tests
- `make tox-parallel` - Test all Python versions (10x faster!)
- `make test-cov` - With coverage report

**Code Quality:**
- `make check` - All quality checks
- `make ruff-format` - Auto-format code
- `make ruff-check` - Lint code
- `make mypy` - Type check
- `make uv-pre-commit` - Pre-commit with UV (9x faster!)

**Cleaning:**
- `make clean` - Remove artifacts
- `make tox-clean` - Clean tox environments

**CI:**
- `make tox-ci` - Simulate CI pipeline
- `make ci` - Traditional CI simulation

See [MAKEFILE.md](MAKEFILE.md) for complete documentation of all 55 targets.

## Testing

### Running Tests

#### Quick Testing

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# With coverage report
make test-cov

# Watch mode (auto-rerun)
make test-watch

# Previously failed tests only
make test-failed
```

#### Multi-Environment Testing with Tox

Test across Python 3.10, 3.11, 3.12, 3.13, 3.14, and 3.15 automatically with tox-uv (10x faster):

```bash
# Test all environments (uses UV automatically via tox-uv!)
tox

# Test in parallel (10x faster than sequential)
make tox-parallel
# or
tox -p auto

# Test specific Python versions (using dynamic pattern rule)
make tox-py310        # Python 3.10 (automatically handled)
make tox-py311        # Python 3.11 (automatically handled)
make tox-py312        # Python 3.12 (automatically handled)
make tox-py313        # Python 3.13 (automatically handled)
make tox-py314        # Python 3.14 (automatically handled)
make tox-py315        # Python 3.15 (automatically handled)

# Run specific checks (using dynamic pattern rule)
make tox-ruff-check   # Linting only (automatically handled)
make tox-mypy         # Type checking only (automatically handled)
make tox-coverage     # Coverage report (automatically handled)

# Simulate full CI pipeline (using dynamic pattern rule)
make tox-ci           # Automatically handled

# List all available tox environments
make tox-envs
```

**Performance:** With tox-uv, environments are created 7-15x faster!

See [TOX.md](TOX.md) and [TOX-UV.md](TOX-UV.md) for complete documentation.

### Writing Tests

Tests are located in `tests/` directory:
- `tests/unit/` - Unit tests for individual modules
- `tests/integration/` - Integration tests for complete workflows
- `tests/conftest.py` - Pytest configuration and fixtures

#### Example Test

```python
# tests/unit/test_mymodule.py
import pytest
from nhl_scrabble.mymodule import MyClass

class TestMyClass:
    """Tests for MyClass."""

    def test_basic_functionality(self) -> None:
        """Test basic functionality."""
        obj = MyClass()
        assert obj.method() == expected_result

    def test_error_handling(self) -> None:
        """Test error handling."""
        obj = MyClass()
        with pytest.raises(ValueError):
            obj.method(invalid_input)
```

### Test Coverage

Aim for:
- **Overall coverage:** >80%
- **Core modules:** >90%
- **New features:** >85%

View coverage report:
```bash
make test-cov
open htmlcov/index.html
```

Or via tox:
```bash
make tox-coverage
```

## Code Quality

### Formatting

Code is formatted with [Ruff](https://github.com/astral-sh/ruff):

```bash
# Auto-format code
make ruff-format

# Check formatting without changes
make ruff-format-check
```

### Linting

Linting is done with Ruff:

```bash
# Run linter
make ruff-check

# Via tox
make tox-ruff-check
```

Ruff checks for:
- PEP 8 compliance
- Common bugs and anti-patterns
- Import organization
- Code complexity
- And much more!

### Type Checking

Type checking with [MyPy](http://mypy-lang.org/):

```bash
# Run type checker
make mypy

# Via tox
make tox-mypy
```

All code should have type hints:

```python
def process_data(items: list[str]) -> dict[str, int]:
    """Process data and return counts.

    Args:
        items: List of items to process

    Returns:
        Dictionary mapping items to their lengths
    """
    return {item: len(item) for item in items}
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

#### Installation

```bash
# Traditional installation
make install-hooks

# With UV acceleration (9x faster!)
make uv-pre-commit-install
```

#### Running Hooks

```bash
# Run manually on all files (traditional)
make pre-commit

# Run with UV acceleration (9x faster!)
make uv-pre-commit
```

#### What Hooks Check

- Trailing whitespace
- File endings
- YAML/TOML syntax
- Large files
- Merge conflicts
- Code formatting (ruff)
- Linting (ruff)
- Type checking (mypy)

See [PRECOMMIT-UV.md](PRECOMMIT-UV.md) for complete pre-commit documentation.

### Complete Quality Check

Run all quality checks before committing:

```bash
make check
```

This runs:
1. Format check (ruff format --check)
2. Linting (ruff check)
3. Type checking (mypy)
4. All tests (pytest)

Or via tox:
```bash
make tox-quality  # Lint + type + format checks
```

## UV Ecosystem

The project uses UV throughout for 10-100x performance improvements:

### Components

1. **UV Package Manager** - Fast package installation
2. **Tox-UV** - Fast test environments
3. **Pre-commit-UV** - Fast hook installation

### Performance Benefits

| Operation | Standard | With UV | Speedup |
|-----------|----------|---------|---------|
| Create venv | 3s | 0.5s | **6x** |
| Install deps | 45s | 5s | **9x** |
| Tox env creation | 60s | 8s | **7.5x** |
| Pre-commit install | 45s | 5s | **9x** |
| Full CI pipeline | 12min | 3min | **4x** |

### Quick Commands

```bash
# Package management
make uv-init          # Fast setup
make uv-install-dev   # Install dependencies
make uv-update        # Update dependencies

# Testing
tox                   # Uses tox-uv automatically
make tox-parallel     # 10x faster

# Pre-commit
make uv-pre-commit-install  # 9x faster hook install
make uv-pre-commit          # 9x faster hook execution
```

### Documentation

- [UV.md](UV.md) - Complete UV package manager guide
- [UV-QUICKREF.md](UV-QUICKREF.md) - Quick reference card
- [TOX-UV.md](TOX-UV.md) - Tox with UV acceleration
- [PRECOMMIT-UV.md](PRECOMMIT-UV.md) - Pre-commit with UV
- [UV-ECOSYSTEM.md](UV-ECOSYSTEM.md) - Complete ecosystem guide

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def calculate_score(name: str) -> int:
    """Calculate the Scrabble score for a given name.

    Args:
        name: The name to score

    Returns:
        The total Scrabble score

    Raises:
        ValueError: If name is empty

    Examples:
        >>> calculate_score("ALEX")
        11
    """
    if not name:
        raise ValueError("Name cannot be empty")
    # ... implementation
```

### Documentation Files

**User Documentation:**
- `README.md` - Project overview, quick start, usage
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history

**Developer Documentation:**
- `docs/MAKEFILE.md` - Complete Makefile reference (55 targets)
- `docs/DEVELOPMENT.md` - This file
- `docs/TOX.md` - Tox testing guide
- `docs/TOX-UV.md` - Tox with UV acceleration
- `docs/UV.md` - UV package manager guide
- `docs/UV-QUICKREF.md` - UV quick reference
- `docs/UV-ECOSYSTEM.md` - Complete UV ecosystem
- `docs/PRECOMMIT-UV.md` - Pre-commit with UV
- `CLAUDE.md` - Architecture and AI assistant guide

### Building Documentation

```bash
# Build Sphinx docs (when set up)
make docs

# Serve docs locally
make serve-docs
```

## Release Process

### Preparing a Release

1. **Run full verification**
   ```bash
   make release
   ```

2. **Update version**
   - Edit `src/nhl_scrabble/__init__.py`
   - Update `__version__ = "X.Y.Z"`

3. **Update CHANGELOG**
   - Edit `CHANGELOG.md`
   - Move items from `[Unreleased]` to `[X.Y.Z]`
   - Add release date

4. **Commit changes**
   ```bash
   git add .
   git commit -m "Release vX.Y.Z"
   ```

5. **Create git tag**
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```

6. **Push changes**
   ```bash
   git push
   git push --tags
   ```

7. **Build and publish**
   ```bash
   make build
   make publish  # Or publish-test for TestPyPI
   ```

### Versioning

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

## Troubleshooting

### Virtual Environment Issues

```bash
# Remove and recreate (traditional)
make clean-venv
make venv
make install-dev

# Or with UV (faster)
make clean-venv
make uv-venv
make uv-install-dev
```

### Test Failures

```bash
# Run with verbose output
make test-verbose

# Run specific test
pytest tests/unit/test_specific.py -v

# Run with debugging
pytest tests/unit/test_specific.py -vv -s

# Via tox
tox -e py310 -- -vv
```

### Import Errors

```bash
# Reinstall package in editable mode (traditional)
make install-dev

# Or with UV (faster)
make uv-install-dev

# Verify installation
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"
```

### Pre-commit Hook Failures

```bash
# Update hooks
make update

# Run manually to see issues
make uv-pre-commit

# Fix formatting
make ruff-format

# Re-run hooks
make uv-pre-commit

# Skip hooks temporarily (not recommended)
git commit --no-verify
```

### Tox Issues

```bash
# Clean and recreate tox environments
make tox-clean
make tox-recreate

# Or completely remove and rebuild
rm -rf .tox/
tox

# Verify tox-uv is working
tox --version  # Should show tox-uv plugin
```

### UV Issues

```bash
# Check UV is installed
make uv-check

# Install UV if missing
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clear UV cache if corrupted
uv cache clean

# Fall back to traditional pip if needed
make init  # Uses pip instead of UV
```

### Build Issues

```bash
# Clean everything and rebuild (with UV)
make clean-all
make uv-init
make build

# Or traditional
make clean-all
make init
make build
```

### Dependency Conflicts

```bash
# Update all dependencies (with UV)
make uv-update

# Or traditional
make update
```

## Best Practices

### Code Style

1. **Follow PEP 8** - Enforced by ruff
2. **Use type hints** - Required for all public APIs
3. **Write docstrings** - For all public modules, classes, functions
4. **Keep functions small** - Single responsibility principle
5. **Avoid complexity** - Keep cyclomatic complexity low

### Git Workflow

1. **Create feature branches** - Don't commit directly to main
2. **Write descriptive commits** - Explain why, not what
3. **Keep commits atomic** - One logical change per commit
4. **Run checks before pushing** - Use `make check` or `make tox-ci`
5. **Keep history clean** - Squash commits if needed

### Testing

1. **Write tests first** - TDD when possible
2. **Test behavior, not implementation** - Focus on outcomes
3. **Use descriptive test names** - `test_calculates_score_for_empty_string`
4. **One assertion per test** - When practical
5. **Use fixtures** - Keep tests DRY
6. **Aim for >85% coverage** - On new features

### Documentation

1. **Document public APIs** - Comprehensive docstrings
2. **Keep README updated** - Reflect current state
3. **Update CHANGELOG** - Document all changes
4. **Add examples** - Show usage in docstrings
5. **Link related docs** - Cross-reference when helpful

### Performance

1. **Use UV for all operations** - 10-100x faster
2. **Use tox-uv for testing** - Already configured
3. **Use pre-commit-uv** - 9x faster hooks
4. **Enable parallel testing** - `make tox-parallel`
5. **Leverage caching** - UV caches globally

## Quick Reference

### Daily Commands

```bash
# Setup (first time)
make uv-init

# Development
source .venv/bin/activate
# ... make changes ...
make test
make uv-pre-commit

# Before commit
make check

# Before PR
make tox-parallel
make tox-ci
```

### Common Workflows

```bash
# Fix formatting
make ruff-format

# Run all checks
make check

# Test all Python versions
make tox-parallel

# Update dependencies
make uv-update

# Clean everything
make clean-all
```

## Resources

### External Links

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Tox Documentation](https://tox.wiki/)
- [Ruff Documentation](https://github.com/astral-sh/ruff)

### Project Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [MAKEFILE.md](MAKEFILE.md) - Complete Makefile reference
- [UV-ECOSYSTEM.md](UV-ECOSYSTEM.md) - UV integration guide
- [TOX-UV.md](TOX-UV.md) - Tox with UV
- [PRECOMMIT-UV.md](PRECOMMIT-UV.md) - Pre-commit with UV
- [CLAUDE.md](../CLAUDE.md) - Architecture guide

## Getting Help

- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Check [MAKEFILE.md](MAKEFILE.md) for command reference
- Check [UV-ECOSYSTEM.md](UV-ECOSYSTEM.md) for UV help
- Open an issue on GitHub for bugs or questions
- Review existing issues and discussions

## Summary

This project features:
- ✅ **55 Makefile targets** - Complete automation (16 logical groupings)
- ✅ **Dynamic tox pattern rule** - Automatic support for any tox environment
- ✅ **UV ecosystem** - 10-100x faster workflows
- ✅ **Tox-UV** - Multi-Python testing (10x faster)
- ✅ **Pre-commit-UV** - Fast hooks (9x faster)
- ✅ **Comprehensive tests** - >80% coverage
- ✅ **Modern tooling** - Ruff, MyPy, Pytest
- ✅ **Professional structure** - Best practices throughout
- ✅ **Python 3.10-3.15** - Support for latest Python versions
- ✅ **Tool-based naming** - Clear targets using actual tool names (ruff-check, mypy, ruff-format, pip-audit)

**Quick start:**
```bash
make uv-init          # Fast setup (5s)
make tox-parallel     # Fast testing (30s)
make check            # Pre-commit verification
```

---

Happy coding! 🏒🎯
