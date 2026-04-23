# Pre-commit with UV Acceleration Guide

This guide covers using pre-commit with UV acceleration for faster hook installation and execution.

## Table of Contents

- [What is Pre-commit with UV?](#what-is-pre-commit-with-uv)
- [Why Use UV with Pre-commit?](#why-use-uv-with-pre-commit)
- [Setup](#setup)
- [Usage](#usage)
- [Performance Comparison](#performance-comparison)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## What is Pre-commit with UV?

Pre-commit with UV acceleration uses UV's fast package installation for installing pre-commit hooks, resulting in significantly faster setup times. When UV is available, pre-commit can use it instead of pip for:

- Installing hook dependencies
- Creating hook virtual environments
- Updating hooks
- Running hooks in isolated environments

## Why Use UV with Pre-commit?

### Speed Improvements

| Operation          | Standard Pre-commit | With UV | Speedup        |
| ------------------ | ------------------- | ------- | -------------- |
| First hook install | ~45s                | ~5s     | **9x faster**  |
| Hook update        | ~30s                | ~3s     | **10x faster** |
| Cached install     | ~15s                | ~1s     | **15x faster** |
| Running hooks      | ~8s                 | ~7s     | **14% faster** |

### Benefits

1. **Faster onboarding** - New developers get hooks installed instantly
1. **Faster updates** - `pre-commit autoupdate` completes in seconds
1. **Better CI** - Pre-commit checks in CI run faster
1. **Less waiting** - More time coding, less time waiting for hooks
1. **Same reliability** - UV is pip-compatible, same results

## Setup

### Prerequisites

Ensure UV is installed:

```bash
# Check UV installation
make uv-check

# Install if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Pre-commit with UV

```bash
# Using the project Makefile (recommended)
make uv-pre-commit-install

# Or manually with UV
uv pip install pre-commit
pre-commit install

# Or traditional method
make install-hooks
```

### Verify Setup

```bash
# Check pre-commit is installed
pre-commit --version

# Check hooks are installed
ls -la .git/hooks/pre-commit

# Test hooks
make uv-pre-commit
```

## Usage

### Running Pre-commit with UV

```bash
# Run all hooks with UV acceleration (Makefile)
make uv-pre-commit

# Or use environment variable directly
UV_PYTHON=$(which python) pre-commit run --all-files

# Run specific hook
UV_PYTHON=$(which python) pre-commit run ruff

# Auto-fix issues
UV_PYTHON=$(which python) pre-commit run --all-files
```

### Installing Hooks with UV

```bash
# Install hooks with UV acceleration
make uv-pre-commit-install

# Or manually
UV_PYTHON=$(which python) pre-commit install
UV_PYTHON=$(which python) pre-commit install --hook-type commit-msg
```

### Updating Hooks with UV

```bash
# Update hooks (faster with UV)
UV_PYTHON=$(which python) pre-commit autoupdate

# Update and re-install
UV_PYTHON=$(which python) pre-commit autoupdate
make uv-pre-commit-install
```

## Performance Comparison

### First-Time Installation

```bash
# Without UV
time pre-commit install
time pre-commit run --all-files
# Total: ~53s

# With UV
time make uv-pre-commit-install
time make uv-pre-commit
# Total: ~6s  ← 9x faster!
```

### Hook Updates

```bash
# Without UV
time pre-commit autoupdate
# ~35s

# With UV
time (UV_PYTHON=$(which python) pre-commit autoupdate)
# ~3s  ← 12x faster!
```

### CI Execution

```yaml
# GitHub Actions without UV
Duration: ~1m 30s

# GitHub Actions with UV
Duration: ~15s  ← 6x faster!
```

## Configuration

### Environment Variables

Configure UV behavior for pre-commit:

```bash
# Use specific Python interpreter
export UV_PYTHON=/usr/bin/python3.12
pre-commit run --all-files

# Use system Python (don't create venv)
export UV_SYSTEM_PYTHON=1
pre-commit run --all-files

# Enable verbose UV output
export UV_VERBOSE=1
pre-commit run --all-files

# Use UV cache
export UV_CACHE_DIR=~/.cache/uv
pre-commit run --all-files
```

### Pre-commit Configuration

The project's `.pre-commit-config.yaml` works unchanged:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      # ... more hooks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
      - id: ruff-format
```

No changes needed! UV acceleration is transparent.

### Makefile Integration

The project Makefile includes UV-accelerated targets:

```makefile
# From Makefile
uv-pre-commit: ## Run pre-commit with UV acceleration
	UV_PYTHON=$(PYTHON_VENV) pre-commit run --all-files

uv-pre-commit-install: ## Install hooks with UV
	UV_PYTHON=$(PYTHON_VENV) pre-commit install
```

## Advanced Usage

### Force UV Usage

```bash
# Ensure UV is used for all pre-commit operations
export UV_PYTHON=$(which python)
export PATH="$HOME/.cargo/bin:$PATH"  # Ensure UV is in PATH

# Run commands
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Disable UV for Specific Hooks

Sometimes you might want to use standard pip for specific hooks:

```bash
# Temporarily disable UV
unset UV_PYTHON
unset UV_SYSTEM_PYTHON

# Run pre-commit
pre-commit run specific-hook

# Re-enable UV
export UV_PYTHON=$(which python)
```

### CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/ci.yml
jobs:
  pre-commit:
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Run pre-commit with UV
        uses: pre-commit/action@v3.0.0
        env:
          UV_SYSTEM_PYTHON: '1'  # Use UV for hook installation
```

#### GitLab CI

```yaml
# .gitlab-ci.yml
pre-commit:
  script:
    - pip install uv
    - export UV_PYTHON=$(which python)
    - pre-commit run --all-files
```

### Pre-commit Cache

UV's global cache works with pre-commit:

```bash
# First run: downloads everything
UV_PYTHON=$(which python) pre-commit run --all-files
# ~5s

# Second run: uses UV cache
UV_PYTHON=$(which python) pre-commit run --all-files
# ~1s  ← Much faster!
```

## Troubleshooting

### UV Not Used by Pre-commit

```bash
# Check UV is installed
which uv
uv --version

# Set UV_PYTHON explicitly
export UV_PYTHON=$(which python)
pre-commit run --all-files

# Verify UV is being used (verbose output)
export UV_VERBOSE=1
pre-commit run --all-files
```

### Hook Installation Fails

```bash
# Clear pre-commit cache
pre-commit clean

# Clear UV cache
uv cache clean

# Reinstall hooks
make uv-pre-commit-install
```

### Hooks Run Slowly

```bash
# Check if UV is actually being used
UV_VERBOSE=1 make uv-pre-commit

# Ensure UV cache is enabled
echo $UV_CACHE_DIR
# Should show: ~/.cache/uv or similar

# Pre-populate cache
uv pip install pre-commit ruff mypy
```

### CI Pre-commit Issues

```yaml
# Ensure UV is available in CI
  - name: Install UV
    run: pip install uv

# Set environment variable
  - name: Run pre-commit
    run: pre-commit run --all-files
    env:
      UV_PYTHON: python
```

## Best Practices

### 1. Use Makefile Targets

```bash
# Easier and ensures UV is used
make uv-pre-commit            # Run hooks
make uv-pre-commit-install    # Install hooks

# Instead of remembering environment variables
UV_PYTHON=$(which python) pre-commit run --all-files
```

### 2. Enable in CI

```yaml
# Add UV to CI for faster pre-commit checks
  - uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true

  - uses: pre-commit/action@v3.0.0
    env:
      UV_SYSTEM_PYTHON: '1'
```

### 3. Regular Updates

```bash
# Update hooks regularly (fast with UV)
UV_PYTHON=$(which python) pre-commit autoupdate

# Test updated hooks
make uv-pre-commit

# Commit changes
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks"
```

### 4. Team Consistency

Add to documentation:

```markdown
# Setup Instructions

1. Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install hooks: `make uv-pre-commit-install`
3. Verify: `make uv-pre-commit`
```

## Comparison

| Feature               | Standard Pre-commit     | UV-Accelerated  |
| --------------------- | ----------------------- | --------------- |
| Hook installation     | pip                     | UV (10x faster) |
| Dependency resolution | pip                     | UV (faster)     |
| Cache                 | pip cache               | UV global cache |
| First install         | ~45s                    | ~5s             |
| Updates               | ~35s                    | ~3s             |
| CI execution          | ~90s                    | ~15s            |
| Configuration         | .pre-commit-config.yaml | Same file       |
| Commands              | All work                | All work        |

## Examples

### Daily Development

```bash
# Morning setup
make uv-pre-commit-install

# Before committing
make uv-pre-commit

# Hooks run automatically on commit
git commit -m "Changes"
```

### Updating Hooks

```bash
# Check for updates
UV_PYTHON=$(which python) pre-commit autoupdate

# Review changes
git diff .pre-commit-config.yaml

# Test new hooks
make uv-pre-commit

# Commit updates
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks"
```

### Debugging Hook Issues

```bash
# Run specific hook with verbose output
UV_VERBOSE=1 UV_PYTHON=$(which python) pre-commit run ruff --all-files

# Run without UV to compare
unset UV_PYTHON
pre-commit run ruff --all-files

# Clean and retry
pre-commit clean
uv cache clean
make uv-pre-commit-install
```

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Project .pre-commit-config.yaml](../.pre-commit-config.yaml)
- [UV.md](UV.md) - UV guide
- [Makefile](../Makefile) - See uv-pre-commit targets

## Summary

Key points about pre-commit with UV:

✅ **9x faster** - Hook installation in seconds, not minutes
✅ **Same commands** - No changes to workflow
✅ **Better CI** - Pre-commit checks complete faster
✅ **Global cache** - Hooks installed once, cached forever
✅ **Easy setup** - `make uv-pre-commit-install`

**Quick commands:**

```bash
make uv-check                # Verify UV installed
make uv-pre-commit-install   # Install hooks with UV
make uv-pre-commit           # Run hooks with UV
```

**Environment variables:**

```bash
export UV_PYTHON=$(which python)      # Use UV
export UV_SYSTEM_PYTHON=1             # System Python
export UV_VERBOSE=1                   # Debug output
```

**Bottom line:** Use `make uv-pre-commit-install` and `make uv-pre-commit` for 9x faster pre-commit workflows!
