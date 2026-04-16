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

- Pre-commit hooks (55 hooks)
- Python 3.10 tests
- Python 3.11 tests
- Python 3.12 tests
- Python 3.13 tests
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
- All 54 other hooks (ruff, mypy, black, security checks, etc.) **MUST always run**
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

# Run pre-commit hooks manually
pre-commit run --all-files
```

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
