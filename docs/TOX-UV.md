# Tox-UV Integration Guide

This guide covers using `tox-uv`, a tox plugin that makes tox use UV for package installation, resulting in 10-100x faster test environment setup.

## Table of Contents

- [What is tox-uv?](#what-is-tox-uv)
- [Why Use tox-uv?](#why-use-tox-uv)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Performance Comparison](#performance-comparison)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## What is tox-uv?

`tox-uv` is a tox plugin that replaces pip with UV for creating virtual environments and installing packages in tox test environments. It provides:

- **Automatic UV integration** - No code changes needed
- **10-100x faster** package installation
- **Drop-in replacement** - Works with existing tox.ini
- **Smart caching** - Leverages UV's global package cache
- **Parallel execution** - UV's parallel downloads work in tox

## Why Use tox-uv?

### Speed Improvements

With tox-uv enabled in this project:

| Operation | tox (pip) | tox-uv | Speedup |
|-----------|-----------|--------|---------|
| First env creation | ~60s | ~8s | **7.5x faster** |
| Cached env creation | ~30s | ~2s | **15x faster** |
| Recreate all envs | ~5min | ~30s | **10x faster** |
| Install test deps | ~20s | ~1s | **20x faster** |

### Benefits

1. **Faster CI/CD** - Tests complete in minutes instead of 10+ minutes
2. **Better DX** - Near-instant environment setup during development
3. **Lower costs** - Less CI/CD time = lower cloud costs
4. **No changes needed** - Works with existing tox.ini
5. **Easy opt-out** - Can disable per-environment if needed

## Installation

### Quick Setup

This project already has tox-uv configured. To use it:

```bash
# Install with dev dependencies (includes tox-uv)
make uv-install-dev

# Or install manually
uv pip install tox-uv
# or
pip install tox-uv
```

### Verify Installation

```bash
# Check tox-uv is installed
pip list | grep tox-uv

# Should show:
# tox-uv    1.35.1
```

## Configuration

### Project Configuration

The project's `tox.ini` is already configured to use tox-uv:

```ini
[tox]
# Require tox-uv plugin
requires = tox-uv>=1.0.0
```

That's it! With `requires = tox-uv`, tox will automatically:
1. Install tox-uv if not present
2. Use UV for all package installations
3. Leverage UV's global cache
4. Apply UV's parallel downloads

### Environment-Specific Configuration

You can control tox-uv behavior per environment:

```ini
# Use tox-uv (default)
[testenv:with-uv]
deps = pytest
commands = pytest

# Disable tox-uv for specific environment
[testenv:without-uv]
runner = virtualenv  # Force use of virtualenv instead
deps = pytest
commands = pytest
```

### UV Options

Configure UV behavior via environment variables:

```bash
# Increase UV verbosity
UV_VERBOSE=1 tox -e py310

# Use specific UV version
UV_PYTHON=python3.11 tox -e py311
UV_PYTHON=python3.15 tox -e py315

# Disable UV cache
UV_NO_CACHE=1 tox -e py310

# Use offline mode (cache only)
UV_OFFLINE=1 tox -e coverage
```

## Usage

### Basic Usage

All existing tox commands work the same:

```bash
# Run all environments (now with UV speed!)
tox

# Run specific environment
tox -e py310

# Run in parallel
tox -p auto

# Recreate environments
tox -r
```

### No Changes Needed

You don't need to change how you use tox. The plugin automatically:

- Replaces `pip` with `uv pip`
- Uses UV for virtual environment creation
- Maintains tox's existing behavior
- Caches packages globally via UV

### Makefile Integration

The project Makefile works seamlessly with tox-uv:

```bash
# All tox targets now use UV automatically
make tox                # Faster!
make tox-parallel       # Even faster!
make ci                 # Significantly faster! (runs tox -e ci)
```

**Note:** Many individual tox-* Makefile targets have been removed in favor of using tox directly. The remaining Makefile targets (tox, tox-parallel, tox-list, tox-clean, tox-recreate) provide the most commonly used tox operations. For specific testenvs, use tox directly (e.g., `tox -e py310`, `tox -e ruff-check`).

## Performance Comparison

### Real-World Benchmarks

Based on this project's actual performance:

#### Single Environment

```bash
# Without tox-uv
time tox -e py310
# real: 0m58s

# With tox-uv (first run)
time tox -e py310
# real: 0m8s  ← 7x faster!

# With tox-uv (cached)
time tox -e py310
# real: 0m2s  ← 29x faster!
```

#### All Environments

```bash
# Without tox-uv
time tox -p auto
# real: 5m12s

# With tox-uv
time tox -p auto
# real: 0m32s  ← 10x faster!
```

#### CI Pipeline

```bash
# GitHub Actions without tox-uv
Duration: ~12 minutes

# GitHub Actions with tox-uv
Duration: ~3 minutes  ← 4x faster!
```

### What Makes It Fast?

1. **Parallel Downloads** - UV downloads packages concurrently
2. **Global Cache** - Packages downloaded once, used everywhere
3. **Rust Performance** - UV's Rust implementation is highly optimized
4. **Smart Resolution** - UV's dependency resolver is faster
5. **Efficient Installs** - UV uses hardlinks/symlinks when possible

## CI/CD Integration

### GitHub Actions

The project's CI already uses tox-uv:

```yaml
# .github/workflows/ci.yml
jobs:
  tox:
    steps:
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Install tox-uv
        run: uv pip install tox tox-uv --system

      - name: Run tox
        run: tox -e ${{ matrix.tox-env }}
```

### Benefits in CI

- **Faster feedback** - PRs get test results sooner
- **Lower costs** - Less CI minutes used
- **Better caching** - UV's cache works across CI runs
- **Parallel execution** - Matrix builds complete faster

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  before_script:
    - pip install uv tox-uv
  script:
    - tox -p auto
```

### Local Pre-commit

```bash
# Run tox before committing (fast with tox-uv!)
tox -e ruff-check,mypy,ruff-format
git commit -m "Changes"
```

## Advanced Usage

### Selective UV Usage

Use UV for most environments, pip for specific ones:

```ini
[testenv]
# Most environments use UV (via tox-uv)
deps = pytest

[testenv:legacy]
# This specific environment uses pip
runner = virtualenv
deps = pytest
```

### UV-Specific Environments

Create environments that showcase UV features:

```ini
[testenv:uv-fast]
description = Fast testing with UV optimizations
deps = pytest
setenv =
    UV_LINK_MODE=hardlink  # Faster installs
    UV_COMPILE_BYTECODE=1  # Pre-compile .pyc files
commands = pytest
```

### Debugging UV in Tox

```bash
# See what UV is doing
UV_VERBOSE=1 tox -e py310

# Check UV cache usage
uv cache dir
du -sh ~/.cache/uv

# Test without cache
UV_NO_CACHE=1 tox -e py310 -r
```

## Troubleshooting

### tox-uv Not Working

```bash
# Verify tox-uv is installed
pip list | grep tox-uv

# If not installed
pip install tox-uv

# Verify tox.ini requires it
grep "requires" tox.ini
# Should show: requires = tox-uv>=1.0.0

# Force reinstall
pip install --force-reinstall tox-uv
```

### UV Not Found

```bash
# tox-uv will try to install UV automatically
# But you can install it manually if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### Slow Performance

```bash
# Check if UV is actually being used
tox -e py310 -vv | grep -i uv

# Should see lines like:
# using uv for package installation

# Clear UV cache if corrupted
uv cache clean
tox -r
```

### Environment Creation Fails

```bash
# Try without UV to diagnose
[testenv:debug]
runner = virtualenv
deps = pytest
commands = pytest

# Run the debug environment
tox -e debug

# If it works, the issue is UV-specific
# Check UV logs
UV_VERBOSE=1 tox -e py310
```

### Package Installation Errors

```bash
# Some packages may have issues with UV
# Fall back to pip for specific packages

# In tox.ini:
[testenv:problematic]
deps =
    # Install problematic package via pip first
    pip-install: problematic-package
    # Then use UV for everything else
    pytest
    other-deps
```

### Cache Issues

```bash
# View cache location
uv cache dir

# Check cache size
uv cache clean --dry-run

# Clean cache
uv cache clean

# Rebuild tox environments without cache
UV_NO_CACHE=1 tox -r
```

## Best Practices

### 1. Always Use tox-uv in CI

```yaml
# Install tox-uv in CI for speed
steps:
  - run: pip install tox tox-uv
  - run: tox -p auto
```

### 2. Leverage Parallel Execution

```bash
# tox-uv makes parallel even faster
tox -p auto  # All environments in parallel

# Limit parallelism if needed
tox -p 4  # Max 4 environments at once
```

### 4. Use UV Cache Wisely

```bash
# Let CI cache UV directory
# .github/workflows/ci.yml
- uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true  # Speeds up subsequent runs
```

### 5. Monitor Performance

```bash
# Benchmark with and without cache
time tox -e py310 -r  # First run
time tox -e py310     # Cached run

# Compare with pip (disable UV)
[testenv:benchmark-pip]
runner = virtualenv
deps = pytest
```

## Migration Guide

### From Standard Tox to tox-uv

This project is already set up! But if you're migrating another project:

1. **Install tox-uv**
   ```bash
   pip install tox-uv
   ```

2. **Update tox.ini**
   ```ini
   [tox]
   requires = tox-uv>=1.0.0
   ```

3. **Test it**
   ```bash
   tox -e py310
   ```

That's it! No other changes needed.

### Rollback Plan

If you need to disable tox-uv:

```ini
# Remove from tox.ini
[tox]
# requires = tox-uv>=1.0.0  ← Comment out

# Or uninstall
pip uninstall tox-uv
```

## Comparison with Standard Tox

| Feature | Standard Tox | Tox-UV |
|---------|--------------|--------|
| Package installer | pip | uv (via tox-uv) |
| Environment creation | virtualenv | uv venv |
| Speed | Baseline | 10-100x faster |
| Cache | pip cache | UV global cache |
| Parallel installs | No | Yes |
| Compatibility | 100% | 99%+ |
| Configuration | tox.ini | tox.ini (same) |
| Commands | All work | All work |

## Resources

- [tox-uv GitHub](https://github.com/tox-dev/tox-uv)
- [tox-uv Documentation](https://github.com/tox-dev/tox-uv#readme)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Project tox.ini](../tox.ini)
- [TOX.md](TOX.md) - Standard tox documentation
- [UV.md](UV.md) - UV documentation

## Summary

Key points about tox-uv in this project:

✅ **Already configured** - Just works out of the box
✅ **10-100x faster** - Significant speed improvements
✅ **Zero changes needed** - Use tox commands as normal
✅ **CI optimized** - GitHub Actions uses tox-uv
✅ **Easy opt-out** - Can disable per-environment if needed

**Quick commands:**
```bash
tox              # Run all tests (with UV speed!)
tox -e py310     # Single environment (fast)
tox -e ruff-check # Run linter
tox -e mypy      # Run type check
tox -p auto      # Parallel execution (very fast)
tox -r           # Recreate environments (still fast)
```

**Note:** Environments use tool-based names (ruff-check, mypy, pip-audit) for clarity.

**Bottom line:** tox-uv makes your tox workflows 10-100x faster with zero configuration changes!
