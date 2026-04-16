# How to Setup Pre-commit Hooks

Configure automated code quality checks.

## Problem

You want automated code quality checks before each commit.

## Solution

### Install hooks

```bash
# After cloning repository
make init  # Automatically installs hooks

# Or manually
pre-commit install
```

### Run hooks manually

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-check --all-files

# Run on staged files only
pre-commit run
```

### Update hook versions

```bash
pre-commit autoupdate
```

### Skip hooks (when needed)

```bash
# Skip all hooks
SKIP=all git commit -m "message"

# Skip specific hook
SKIP=mypy git commit -m "message"

# Skip multiple hooks
SKIP=mypy,ruff-check git commit -m "message"
```

## Available hooks (55 total)

- **Formatting**: black, ruff-format, autopep8, docformatter
- **Linting**: ruff-check, flake8, mypy
- **Quality**: interrogate, pydocstyle, vulture
- **Documentation**: pymarkdown, mdformat, doc8
- **And 40+ more**

See `.pre-commit-config.yaml` for complete list.

## Related

- [Pre-commit Configuration](../reference/pre-commit-config.md) - Hook details
- [First Contribution Tutorial](../tutorials/03-first-contribution.md) - Using hooks
