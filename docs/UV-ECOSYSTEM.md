# UV Ecosystem Integration Guide

Complete guide to using UV throughout the NHL Scrabble project for maximum performance.

## Overview

This project leverages UV across the entire development workflow:

1. **UV Package Manager** - Fast package installation and environment management
1. **Tox-UV** - Accelerated testing across multiple Python versions
1. **Pre-commit with UV** - Faster hook installation and execution

Together, these provide **10-100x speedup** across development workflows.

## The UV Ecosystem

```
┌─────────────────────────────────────────────────────────┐
│                    UV Ecosystem                          │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │     UV      │  │   Tox-UV    │  │ Pre-commit  │    │
│  │  Package    │  │   Testing   │  │  with UV    │    │
│  │  Manager    │  │  Automation │  │   Hooks     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│       │                 │                  │            │
│       └─────────────────┴──────────────────┘            │
│                         │                               │
│                  ┌──────▼──────┐                        │
│                  │  UV Binary  │                        │
│                  │ (Rust-based)│                        │
│                  └─────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install UV

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
make uv-check
```

### 2. Setup Project

```bash
# Complete setup with UV acceleration
make uv-init

# This runs:
# - Creates virtual environment (6x faster)
# - Installs all dependencies (9x faster)
# - Installs pre-commit hooks (with UV support)
```

### 3. Daily Workflow

```bash
# Activate environment
source .venv/bin/activate

# Run tests (10x faster with tox-uv)
tox -e py310

# Run pre-commit (9x faster)
make uv-pre-commit

# Install new package (25x faster cached)
uv pip install httpx

# Update all dependencies
make uv-update
```

## Performance Summary

| Operation              | Standard | With UV | Speedup  |
| ---------------------- | -------- | ------- | -------- |
| **Package Management** |          |         |          |
| Create venv            | 3s       | 0.5s    | **6x**   |
| Install deps (cold)    | 45s      | 5s      | **9x**   |
| Install deps (cached)  | 25s      | 1s      | **25x**  |
| Resolve dependencies   | 10s      | 0.3s    | **33x**  |
| **Testing (Tox)**      |          |         |          |
| First env creation     | 60s      | 8s      | **7.5x** |
| Cached env creation    | 30s      | 2s      | **15x**  |
| All envs parallel      | 5min     | 30s     | **10x**  |
| **Pre-commit**         |          |         |          |
| First install          | 45s      | 5s      | **9x**   |
| Hook updates           | 30s      | 3s      | **10x**  |
| Cached install         | 15s      | 1s      | **15x**  |
| **CI/CD**              |          |         |          |
| Full pipeline          | 12min    | 3min    | **4x**   |

## Components

### 1. UV Package Manager

**What:** Fast Python package installer written in Rust
**Speed:** 10-100x faster than pip
**Cache:** Global package cache for efficiency

**Quick Commands:**

```bash
make uv-venv          # Create venv
make uv-install-dev   # Install dependencies
make uv-run           # Run application
```

**Documentation:** [UV.md](UV.md)

### 2. Tox-UV Plugin

**What:** Tox plugin that uses UV instead of pip
**Speed:** 10x faster test environments
**Auto:** Works automatically, no config changes

**Quick Commands:**

```bash
tox                   # All environments (with UV!)
tox -e py310          # Specific environment
tox -p auto           # Parallel (very fast)
make tox-parallel     # Via Makefile
```

**Documentation:** [TOX-UV.md](TOX-UV.md)

### 3. Pre-commit with UV

**What:** Pre-commit using UV for hook installation
**Speed:** 9x faster hook setup
**Easy:** Makefile targets handle it

**Quick Commands:**

```bash
make uv-pre-commit-install   # Install hooks
make uv-pre-commit           # Run hooks
```

**Documentation:** [PRECOMMIT-UV.md](PRECOMMIT-UV.md)

## Makefile Targets

All UV features accessible via Makefile:

### Package Management (8 targets)

```bash
make uv-check              # Verify UV installed
make uv-venv               # Create virtual environment
make uv-install            # Install package
make uv-install-dev        # Install with dev deps
make uv-update             # Update dependencies
make uv-run                # Run application
make uv-init               # Complete setup
make uv-pip                # Direct UV pip access
```

### Pre-commit (2 targets)

```bash
make uv-pre-commit-install # Install hooks
make uv-pre-commit         # Run all hooks
```

### Testing (10 tox targets via tox-uv)

```bash
make tox                   # All environments (UV-accelerated)
make tox-parallel          # Parallel execution
make tox-py310             # Python 3.10
make tox-coverage          # Coverage report
# ... all tox targets use UV automatically
```

## Configuration Files

### pyproject.toml

```toml
[tool.uv]
managed = true          # Enable UV dependency management
package = true          # This is a Python package
compile-bytecode = true # Compile .pyc files for faster imports
link-mode = "copy"      # Copy files instead of linking

[project.optional-dependencies]
dev = [
  "tox-uv>=1.0.0", # Tox with UV
  # ... other deps
]
```

### .python-version

```
3.10
```

UV (and pyenv/asdf) will use this file to select the Python version for the project.

### tox.ini

```ini
[tox]
requires = tox-uv>=1.0.0  # Enable tox-uv plugin
```

## Workflows

### First Time Setup

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone project
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# 3. Setup with UV (blazing fast!)
make uv-init
source .venv/bin/activate

# Total time: ~5 seconds vs ~50 seconds with pip
```

### Daily Development

```bash
# Morning
source .venv/bin/activate

# Add dependency
uv pip install new-package

# Run tests (fast!)
tox -e py310

# Pre-commit check (fast!)
make uv-pre-commit

# Commit
git commit -m "Changes"
```

### Before PR

```bash
# Update dependencies
make uv-update

# Run all tests (parallel, fast!)
make tox-parallel

# Run all checks
make uv-pre-commit

# Everything passes in minutes, not hours!
```

### CI/CD

```yaml
# .github/workflows/ci.yml
  - name: Install UV
    uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true

  - name: Install dependencies
    run: uv pip install -e ".[dev]" --system

  - name: Run tests
    run: tox -p auto
```

## Environment Variables

Control UV behavior:

```bash
# UV Package Manager
export UV_CACHE_DIR=~/.cache/uv      # Cache location
export UV_VERBOSE=1                   # Verbose output
export UV_NO_CACHE=1                  # Disable cache
export UV_OFFLINE=1                   # Offline mode

# Pre-commit with UV
export UV_PYTHON=$(which python)      # Python for hooks
export UV_SYSTEM_PYTHON=1             # Use system Python

# Tox-UV
export UV_LINK_MODE=hardlink          # Fast installs
export UV_COMPILE_BYTECODE=1          # Pre-compile .pyc
```

## Troubleshooting

### UV Not Found

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Verify
make uv-check
```

### Tox-UV Not Working

```bash
# Check tox-uv installed
pip list | grep tox-uv

# Verify in tox.ini
grep "requires.*tox-uv" tox.ini

# Reinstall
uv pip install --force-reinstall tox-uv
```

### Pre-commit Not Using UV

```bash
# Set environment variable
export UV_PYTHON=$(which python)

# Or use Makefile target
make uv-pre-commit
```

### Cache Issues

```bash
# Clear UV cache
uv cache clean

# Clear tox environments
tox -r

# Clear pre-commit
pre-commit clean

# Start fresh
make uv-init
```

## Best Practices

### 1. Always Use UV for New Environments

```bash
# Good (fast)
make uv-venv

# Old (slow)
python -m venv .venv
```

### 2. Enable UV in CI

```yaml
# Always use UV in CI for speed
  - uses: astral-sh/setup-uv@v4
    with:
      enable-cache: true
```

### 4. Use Makefile Targets

```bash
# Good (easy, consistent)
make uv-install-dev

# Works (but verbose)
uv pip install -e ".[dev]"
```

### 5. Regular Cache Maintenance

```bash
# Monthly: check cache size
uv cache clean --dry-run

# Clean if > 5GB
uv cache clean
```

## Migration Checklist

Moving from pip/virtualenv to UV:

- [ ] Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Verify: `make uv-check`
- [ ] Create env: `make uv-venv`
- [ ] Install deps: `make uv-install-dev`
- [ ] Test: `tox -e py310` (uses tox-uv automatically)
- [ ] Pre-commit: `make uv-pre-commit-install`
- [ ] Update CI: Add `astral-sh/setup-uv@v4`
- [ ] Document: Update team docs

## Resources

### Documentation

- [UV.md](UV.md) - Complete UV guide
- [TOX-UV.md](TOX-UV.md) - Tox-UV integration
- [PRECOMMIT-UV.md](PRECOMMIT-UV.md) - Pre-commit with UV
- [UV-QUICKREF.md](UV-QUICKREF.md) - Quick reference

### External Links

- [UV GitHub](https://github.com/astral-sh/uv)
- [Tox-UV GitHub](https://github.com/tox-dev/tox-uv)
- [Pre-commit Docs](https://pre-commit.com/)

### Project Files

- [pyproject.toml](../pyproject.toml) - Dependencies and UV config ([tool.uv])
- [.python-version](../.python-version) - Python version selection
- [tox.ini](../tox.ini) - Tox configuration
- [Makefile](../Makefile) - All commands

## Summary

The UV ecosystem in this project provides:

✅ **10-100x faster** package installation
✅ **7-15x faster** test environments
✅ **9x faster** pre-commit hooks
✅ **4x faster** CI/CD pipelines
✅ **Zero config** - works out of the box
✅ **Easy opt-out** - pip still works
✅ **Production ready** - used in CI

**Quick start:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
make uv-init
source .venv/bin/activate
```

**Daily use:**

```bash
make uv-install-dev    # Install deps
tox -e py310           # Run tests
make uv-pre-commit     # Check code
```

**Result:** Development workflows that are 10-100x faster!
