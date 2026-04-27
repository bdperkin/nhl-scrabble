# Pre-commit Hooks

Complete guide to the project's 67 comprehensive pre-commit hooks.

## Overview

The project uses [pre-commit](https://pre-commit.com/) for automatic code quality validation. All hooks run automatically on `git commit`, ensuring code quality before changes enter the repository.

**Total hooks**: 67 comprehensive quality checks

## Installation

### First-Time Setup

```bash
# Install pre-commit hooks (one-time)
pre-commit install

# Verify installation
pre-commit --version
```

### Quick Start

```bash
# Hooks run automatically on commit
git commit -m "Your changes"

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-check --all-files
```

## Hook Categories

### Meta Hooks (3)

Configuration validation and maintenance:

- **check-hooks-apply** - Validates all hooks apply to repository files
- **check-useless-excludes** - Detects useless exclude patterns in configuration
- **sync-pre-commit-deps** - Syncs hook versions with pyproject.toml dependencies

### File Quality Hooks (18)

Basic file formatting, syntax, and security:

**Whitespace:**

- `trailing-whitespace` - Remove trailing whitespace
- `end-of-file-fixer` - Ensure files end with newline
- `mixed-line-ending` - Fix mixed line endings (LF vs CRLF)
- `fix-byte-order-marker` - Remove UTF-8 byte order marker

**Syntax:**

- `check-yaml` - Validate YAML syntax
- `check-toml` - Validate TOML syntax
- `check-json` - Validate JSON syntax
- `check-ast` - Validate Python AST (syntax errors)

**Python:**

- `check-builtin-literals` - Enforce builtin literals (`list()` → `[]`)
- `check-docstring-first` - Ensure docstring is first statement
- `debug-statements` - Detect `pdb`/`ipdb` debug statements
- `name-tests-test` - Ensure test files start with `test_`

**Security:**

- `detect-private-key` - Detect committed private keys

**Git:**

- `check-added-large-files` - Prevent committing large files (>500KB)
- `check-merge-conflict` - Detect merge conflict markers
- `check-case-conflict` - Detect case conflicts (macOS/Windows)
- `destroyed-symlinks` - Detect broken symlinks

**Executable:**

- `check-shebang-scripts-are-executable` - Ensure scripts with shebangs are executable

### Python Quality Hooks (7)

Python-specific code patterns:

- **python-check-blanket-noqa** - Enforce specific `noqa` codes (`# noqa: F401` not `# noqa`)
- **python-check-blanket-type-ignore** - Enforce specific `type: ignore` codes
- **python-check-mock-methods** - Prevent mock testing mistakes
- **python-no-eval** - Detect `eval()` usage (security risk)
- **python-no-log-warn** - Enforce `logging.warning()` vs deprecated `logging.warn()`
- **python-use-type-annotations** - Enforce PEP 484 annotations vs type comments
- **text-unicode-replacement-char** - Detect Unicode replacement character (U+FFFD)

### Python Import Hooks (2)

Import organization:

- **isort** - Sort Python imports (Black-compatible, line-length=100)
- **absolufy-imports** - Convert relative imports to absolute imports

### Project Validation Hooks (4)

Project configuration validation:

- **validate-pyproject** - Validates `pyproject.toml` against PEP 517/518/621/631 standards
- **pyroma** - Rates Python package metadata quality
- **tox-ini-fmt** - Formats `tox.ini` to standard structure
- **check-wheel-contents** - Validates Python wheel package contents

### YAML Linting Hooks (1)

- **yamllint** - YAML file validation and linting

### JSON/YAML Schema Validation Hooks (4)

Validate configuration files against official schemas:

- **check-github-workflows** - Validates GitHub workflow files
- **check-dependabot** - Validates Dependabot config
- **check-codecov** - Validates `.codecov.yml`
- **check-pre-commit** - Validates `.pre-commit-config.yaml`

### Spelling Hooks (1)

- **codespell** - Spell checking for code and documentation

### Markdown Hooks (2)

- **pymarkdown** - Markdown linting
- **mdformat** - Markdown formatting with plugins (GFM, black, ruff, web)

### Documentation Hooks (2)

- **doc8** - RST style linting (max-line-length=100)
- **rstcheck** - RST syntax checking (validates code blocks with Sphinx)

### Documentation Quality Hooks (7)

- **interrogate** - Docstring coverage checking (requires 100% coverage)
- **deptry** - Dependency checker (obsolete, missing, transitive, misplaced dev deps)
- **unimport** - Unused import checker
- **pydocstyle** - Docstring style checking (PEP 257)
- **vulture** - Dead code detection (unused functions, classes, variables)
- **blocklint** - Inclusive language checker
- **gitlint** - Commit message linter

### UV Hook (1)

- **uv-lock** - Maintains `uv.lock` file consistency with `pyproject.toml`

### Flake8 Hooks (1)

- **flake8** - Python code linting and style checking

### Autoflake Hooks (1)

- **autoflake** - Remove unused imports and variables

### Black Hooks (1)

- **black** - Python code formatting (line-length=100)

### Docformatter Hooks (1)

- **docformatter** - Python docstring formatting (wrap-length=100, PEP 257 style)

### Autopep8 Hooks (1)

- **autopep8** - PEP 8 auto-formatting (aggressive level 2)

### Python Modernization Hooks (2)

- **pyupgrade** - Modernize Python syntax for Python 3.12+ (f-strings, type hints)
- **refurb** - Python code modernization linter (pathlib, comprehensions, modern idioms)

### Python Statement Sorting Hooks (1)

- **ssort** - Sort Python class members and module statements

### Ruff Hooks (2)

- **ruff-check** - Comprehensive linting with ALL rules (`--fix`, `--exit-non-zero-on-fix`)
- **ruff-format** - Code formatting (quote-style: double, indent-style: space)

### Type Checking Hooks (2)

- **mypy** - Strict type checking (strict mode)
- **ty** - Astral's fast type checker (10-100x faster, validation mode - non-blocking)

### Security Hooks (2)

- **bandit** - Security vulnerability scanner
- **safety** - Dependency vulnerability checker

## Usage

### Running Hooks

```bash
# All hooks run automatically on commit
git commit -m "Your changes"

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-check
pre-commit run mypy
pre-commit run black

# Run on specific files
pre-commit run --files src/nhl_scrabble/cli.py

# Run hooks on staged files only
pre-commit run
```

### Updating Hooks

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Update specific hook
pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit

# Test updated hooks
pre-commit run --all-files
```

### Skipping Hooks

**Use sparingly!** Only skip when absolutely necessary:

```bash
# Skip all hooks (emergency only)
git commit --no-verify -m "Emergency fix"

# Skip specific hook
SKIP=mypy git commit -m "WIP: type annotations"

# Skip multiple hooks
SKIP=mypy,ruff-check git commit -m "WIP"
```

### Troubleshooting

**Hook failure:**

```bash
# View detailed error output
pre-commit run ruff-check --verbose

# Clean pre-commit cache
pre-commit clean

# Reinstall hooks
pre-commit uninstall
pre-commit install
```

**Hook modification loops:**

Some hooks modify files (black, ruff-format, mdformat). If they modify your staged files:

1. Hook runs and modifies files
1. You see "files were modified by this hook" message
1. Run `git add -u` to stage the modifications
1. Commit again - hooks will pass

## Automated Hook Updates

Pre-commit hooks are automatically updated via [pre-commit.ci](https://pre-commit.ci):

- **Schedule**: Weekly (every Monday)
- **Process**: Automated PRs created when updates available
- **Review**: Maintainer reviews and merges PRs
- **Manual update**: Run `pre-commit autoupdate` if urgent

### Reviewing pre-commit.ci PRs

1. Check version changes (patch, minor, major)
1. Review release notes for breaking changes
1. Verify CI passes with new versions
1. Test locally for major updates:
   ```bash
   git fetch origin
   git checkout pre-commit-ci-update-config
   pre-commit run --all-files
   ```
1. Merge if all checks pass

## UV Acceleration

Pre-commit hooks can be accelerated with UV for 9x faster execution:

```bash
# Install pre-commit with UV support
pip install pre-commit-uv

# Hooks automatically use UV when available
pre-commit run --all-files  # 9x faster with UV
```

See [PRECOMMIT-UV.md](../PRECOMMIT-UV.md) for complete UV acceleration guide.

## Admin Commits to Main Branch

**IMPORTANT PROJECT RULE**: When admin bypass is necessary to commit directly to `main`:

```bash
# ✅ CORRECT: Skip only branch protection, run all other hooks
SKIP=check-branch-protection git commit -m "message"

# ❌ NEVER USE: This bypasses ALL quality checks
git commit --no-verify -m "message"
```

**Rationale:**

- The `check-branch-protection` hook is a workflow reminder, not a quality check
- All other hooks (ruff, mypy, formatting, linting, etc.) MUST always run
- Quality checks prevent bugs, security issues, and maintain code standards
- Even admin commits must meet quality standards

**When to use:**

- Post-merge cleanup commits
- Documentation updates after PR merge
- Task tracking updates
- Emergency hotfixes (still run quality checks!)

**Never skip quality checks** - The 66 other hooks exist to protect code quality and security.

## Hook Configuration

Hooks are configured in `.pre-commit-config.yaml`. Key configuration sections:

### Default Settings

```yaml
default_install_hook_types: [pre-commit, commit-msg]
default_stages: [pre-commit]
fail_fast: false  # Run all hooks even if one fails
```

### Per-Hook Configuration

Example configurations:

```yaml
# Ruff with ALL rules
- id: ruff-check
  args: [--fix, --exit-non-zero-on-fix, --config=pyproject.toml]

# MyPy strict mode
- id: mypy
  args: [--strict, --config-file=pyproject.toml]

# Black with line length
- id: black
  args: [--line-length=100]
```

## Common Workflows

### Before Committing

```bash
# 1. Stage your changes
git add .

# 2. Run hooks manually to preview
pre-commit run

# 3. Fix any issues
# (hooks may auto-fix some issues)

# 4. Re-stage fixed files
git add -u

# 5. Commit (hooks run automatically)
git commit -m "Your message"
```

### After Hook Failure

```bash
# 1. Review the error message
# 2. Fix the issues in your code
# 3. Re-stage the fixes
git add -u

# 4. Try committing again
git commit -m "Your message"
```

### For New Contributors

```bash
# Install hooks first
pre-commit install

# Run hooks before committing
pre-commit run --all-files

# If hooks pass, you're good to commit
git commit -m "First contribution"
```

## See Also

- [Code Style Guidelines](code-style.md) - Python coding standards
- [Commit Message Guidelines](commit-messages.md) - Commit message format
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Complete contribution guide
- [PRECOMMIT-UV.md](../PRECOMMIT-UV.md) - UV acceleration guide

## Reference

- [pre-commit documentation](https://pre-commit.com/)
- [pre-commit hooks repository](https://github.com/pre-commit/pre-commit-hooks)
- [pre-commit.ci](https://pre-commit.ci/)
