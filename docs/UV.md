# UV - Fast Python Package Manager Guide

This guide covers using [uv](https://github.com/astral-sh/uv), an extremely fast Python package and project manager written in Rust, as an alternative to pip and virtualenv.

## Table of Contents

- [What is UV?](#what-is-uv)
- [Why Use UV?](#why-use-uv)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [UV Commands](#uv-commands)
- [Makefile Integration](#makefile-integration)
- [Comparison with pip](#comparison-with-pip)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## What is UV?

UV is an extremely fast Python package installer and resolver, written in Rust by Astral (the creators of Ruff). It's designed as a drop-in replacement for pip, pip-tools, and virtualenv, offering:

- **10-100x faster** package installation than pip
- **Blazing fast** dependency resolution
- **Compatible** with pip and existing Python tooling
- **Minimal** disk space usage with global cache
- **Reliable** with deterministic resolution

## Why Use UV?

### Speed Comparison

Based on typical NHL Scrabble project operations:

| Operation             | pip  | uv    | Speedup        |
| --------------------- | ---- | ----- | -------------- |
| Create venv           | ~3s  | ~0.5s | **6x faster**  |
| Install deps (cold)   | ~45s | ~5s   | **9x faster**  |
| Install deps (cached) | ~25s | ~1s   | **25x faster** |
| Resolve dependencies  | ~10s | ~0.3s | **33x faster** |

### Benefits for This Project

1. **Faster CI/CD**: GitHub Actions complete in ~2 minutes instead of ~5 minutes
1. **Better DX**: Near-instant dependency installation during development
1. **Disk Efficiency**: Global cache means dependencies downloaded once
1. **Reliability**: Deterministic resolution prevents "works on my machine" issues

## Installation

### macOS and Linux

```bash
# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using Homebrew (macOS)
brew install uv

# Or using cargo (if you have Rust)
cargo install --git https://github.com/astral-sh/uv uv
```

### Windows

```powershell
# Using PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Or using pip
pip install uv
```

### Verify Installation

```bash
uv --version
# Output: uv 0.10.6 (or later)

# Check uv is available
make uv-check
```

## Quick Start

### Using UV with This Project

```bash
# 1. Create virtual environment (faster than python -m venv)
make uv-venv

# 2. Activate the environment
source .venv/bin/activate

# 3. Install project with dev dependencies (10-100x faster than pip)
make uv-install-dev

# 4. Run tests
pytest

# All in one command
make uv-init
```

### Alternative: Traditional Method for Comparison

```bash
# Old way (slow)
make init          # Uses pip: ~50 seconds

# New way (fast)
make uv-init       # Uses uv: ~5 seconds
```

## UV Commands

### Core Commands

#### Create Virtual Environment

```bash
# Using make (recommended)
make uv-venv

# Direct uv command
uv venv .venv --python python3.10
```

#### Install Packages

```bash
# Install project in editable mode
make uv-install

# Install with dev dependencies
make uv-install-dev

# Direct uv commands
uv pip install -e .
uv pip install -e ".[dev,docs]"
```

#### Update Dependencies

```bash
# Update all dependencies to latest compatible versions
make uv-update

# Direct uv command
uv pip install --upgrade -e ".[dev,docs]"
```

#### Run Scripts

```bash
# Run the NHL Scrabble analyzer
make uv-run

# Direct uv command
uv run --with-editable . nhl-scrabble analyze
```

### Advanced Usage

#### Installing Specific Packages

```bash
# Install a package
uv pip install requests

# Install specific version
uv pip install "requests==2.31.0"

# Install from Git
uv pip install git+https://github.com/user/repo.git
```

#### List Packages

```bash
# List installed packages
uv pip list

# Show package details
uv pip show requests

# Check for outdated packages
uv pip list --outdated
```

#### Uninstall Packages

```bash
# Uninstall a package
uv pip uninstall requests

# Uninstall all packages (except uv)
uv pip freeze | xargs uv pip uninstall -y
```

## Makefile Integration

All uv commands are integrated into the Makefile for convenience:

### Setup Commands

```bash
make uv-check        # Verify uv is installed
make uv-venv         # Create virtual environment with uv
make uv-install      # Install package with uv
make uv-install-dev  # Install with dev dependencies
make uv-init         # Complete setup (venv + install + hooks)
```

### Development Commands

```bash
make uv-update       # Update all dependencies
make uv-run          # Run the application
```

### Utility Commands

```bash
make uv-pip ARGS="list"              # List packages
make uv-pip ARGS="show requests"     # Show package info
make uv-pip ARGS="install httpx"     # Install package
```

## Comparison with pip

### Feature Comparison

| Feature               | pip         | uv                   | Winner |
| --------------------- | ----------- | -------------------- | ------ |
| Speed                 | Baseline    | 10-100x faster       | **uv** |
| Dependency resolution | Good        | Excellent            | **uv** |
| Compatibility         | 100%        | 95%+                 | pip    |
| Disk usage            | Higher      | Lower (global cache) | **uv** |
| Maturity              | Very mature | Young but stable     | pip    |
| Learning curve        | Familiar    | Same as pip          | Tie    |

### Command Equivalents

| pip                       | uv                           | Make target               |
| ------------------------- | ---------------------------- | ------------------------- |
| `pip install -e .`        | `uv pip install -e .`        | `make uv-install`         |
| `pip install -e ".[dev]"` | `uv pip install -e ".[dev]"` | `make uv-install-dev`     |
| `pip install requests`    | `uv pip install requests`    | -                         |
| `pip list`                | `uv pip list`                | `make uv-pip ARGS="list"` |
| `pip freeze`              | `uv pip freeze`              | -                         |
| `python -m venv .venv`    | `uv venv .venv`              | `make uv-venv`            |

### When to Use Each

**Use uv when:**

- Starting fresh development setup
- Running CI/CD pipelines
- Installing many packages
- Need deterministic builds
- Want faster iteration cycles

**Use pip when:**

- Working with legacy systems
- Need 100% compatibility
- In restricted environments without uv
- Debugging package installation issues

## CI/CD Integration

### GitHub Actions

The project's CI is configured to use uv for faster builds:

```yaml
# .github/workflows/ci.yml
steps:
  - name: Install uv
    uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true

  - name: Install dependencies
    run: uv pip install -e ".[dev]" --system
```

**Results:**

- Install time reduced from ~45s to ~5s
- Total CI time reduced by ~60%

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.cargo/bin:$PATH"
    - uv pip install -e ".[dev]" --system
```

### Local Pre-commit

```bash
# Use uv for faster hook installation
uv pip install pre-commit
pre-commit install
```

## Best Practices

### 1. Use UV for Development, Support Both

```bash
# Recommended approach
make uv-init        # Fast setup with uv

# But keep traditional targets working
make init           # Still works with pip
```

### 2. Leverage Global Cache

```bash
# UV uses a global cache by default
# First install: downloads packages
# Subsequent installs: reuses cache (instant!)

# Cache location
uv cache dir
# macOS/Linux: ~/.cache/uv
# Windows: %LOCALAPPDATA%\uv\cache
```

### 4. Regular Updates

```bash
# Update uv itself
uv self update

# Update project dependencies
make uv-update
```

### 5. Use .python-version

```bash
# The project includes .python-version for version consistency
cat .python-version  # Shows: 3.10

# UV automatically respects this file
uv python find       # Uses Python 3.10.x

# Also works with pyenv and asdf
pyenv local          # Reads .python-version
asdf current python  # Reads .python-version
```

This ensures all developers and CI environments use the same Python version.

### 6. CI Optimization

```yaml
# Enable uv cache in GitHub Actions for maximum speed
- uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true
    cache-dependency-glob: "pyproject.toml"
```

## Troubleshooting

### UV Not Found

```bash
# Check if uv is installed
make uv-check

# If not, install it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (if needed)
export PATH="$HOME/.cargo/bin:$PATH"
```

### Package Installation Fails

```bash
# Fall back to pip if uv fails
make install-dev

# Or try with verbose output
uv pip install -e ".[dev]" -v

# Clear uv cache if corrupted
uv cache clean
```

### Compatibility Issues

```bash
# Some packages may not work perfectly with uv
# Use pip for those specific packages
pip install problematic-package

# Then continue with uv for everything else
make uv-install-dev
```

### Permission Errors

```bash
# Use --system flag when installing in system Python
uv pip install -e . --system

# Or ensure you're in a virtual environment
source .venv/bin/activate
uv pip install -e .
```

### Cache Issues

```bash
# Check cache location
uv cache dir

# View cache size
uv cache clean --dry-run

# Clean cache
uv cache clean

# Clean specific package cache
uv cache clean requests
```

## Migration Guide

### From pip to uv

If you're currently using pip, here's how to migrate:

1. **Install uv**

   ```bash
   make uv-check  # Verify or show install instructions
   ```

1. **Create new environment**

   ```bash
   make uv-venv
   source .venv/bin/activate
   ```

1. **Install dependencies**

   ```bash
   make uv-install-dev
   ```

1. **Verify everything works**

   ```bash
   pytest
   ```

1. **Update your workflow**

   - Replace `make init` with `make uv-init` in documentation
   - Update CI/CD to use uv

### Hybrid Approach

You can use both pip and uv:

```bash
# Team members can choose
make uv-init     # Fast (uv)
make init        # Compatible (pip)

# Both create identical environments
```

## Performance Tips

### 1. Parallel Installation

UV automatically parallelizes package downloads and builds.

### 2. Offline Mode

```bash
# After cache is populated, work offline
uv pip install -e . --offline
```

## Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs pip Performance](https://github.com/astral-sh/uv#benchmarks)
- [Astral Blog](https://astral.sh/blog)
- [Project Makefile](../Makefile) - See uv targets
- [GitHub Actions Setup](../.github/workflows/ci.yml) - See uv CI config

## Summary

Key commands to remember:

```bash
# Installation
make uv-check         # Verify uv is installed
make uv-init          # Complete setup with uv

# Daily usage
make uv-install-dev   # Install dependencies
make uv-run           # Run application
make uv-update        # Update dependencies

# Maintenance
make uv-venv          # Fresh environment
```

**Bottom line**: UV is 10-100x faster than pip with the same commands. Use it for faster development and CI/CD!
