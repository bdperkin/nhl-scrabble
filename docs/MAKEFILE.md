# Makefile Documentation

The NHL Scrabble project includes a comprehensive, self-documenting Makefile to streamline all development tasks.

## Overview

The Makefile provides **55 documented targets** organized in **16 logical groupings** with color-coded output for better readability. All targets are self-documenting and can be viewed with `make help` (the default target). The Makefile features a dynamic pattern rule (`tox-%`) that automatically handles any tox environment, making it future-proof and maintainable.

### Key Features

✅ **Self-Documenting** - Help auto-generated from inline `## comments`
✅ **Color-Coded Output** - Blue, green, yellow, red for clarity
✅ **Smart Dependencies** - Auto-checks for virtual environment
✅ **Complete Coverage** - All development tasks automated
✅ **UV Integration** - 10-100x faster with UV ecosystem
✅ **Tox Integration** - Multi-Python testing automated
✅ **CI Simulation** - Test locally before pushing
✅ **Cross-Platform** - Uses `printf` for reliable ANSI color support

## Quick Start

```bash
# View all available commands (with beautiful color output!)
make help

# Or just
make

# Fast initialization with UV (recommended - 10-100x faster)
make uv-init

# Or traditional initialization
make init

# Run all quality checks before committing
make check
```

The `make help` command displays all 55 targets organized in 16 logical groupings with color-coded output:

- 🔵 **Blue** - Headers and informational messages
- 🟢 **Green** - Success messages and labels
- 🟡 **Yellow** - Target names and warnings
- 🔴 **Red** - Error messages

## Target Categories

The 55 Makefile targets are organized into 16 logical groupings:

1. **Setup & Installation** (6 targets)
1. **Cleaning** (6 targets)
1. **Testing** (7 targets)
1. **Tox - Multi-environment Testing** (6 targets - includes dynamic pattern rule)
1. **UV - Fast Python Package Manager** (2 targets)
1. **Code Quality** (7 targets)
1. **Security & Dependencies** (1 target)
1. **Build & Publish** (3 targets)
1. **Documentation** (2 targets)
1. **Running** (3 targets)
1. **Development** (4 targets)
1. **Release Management** (2 targets)
1. **All-in-one** (1 target)
1. **CI/CD Simulation** (1 target)
1. **Utility** (2 targets)
1. **Development workflow** (informational section)

## Installation & Setup

### Create Virtual Environment

```bash
# Traditional method (pip, virtualenv)
make venv

# Fast method with UV (6x faster)
make uv-venv
```

Creates a Python virtual environment in `.venv/` and upgrades core packages.

### Install Package

```bash
# Traditional installation
make install          # Package only
make install-dev      # With dev dependencies
make install-hooks    # Pre-commit hooks
make init             # Complete setup (~50s)

# Fast installation with UV (10-100x faster)
make uv-install       # Package only (~1s)
make uv-install-dev   # With dev dependencies (~5s)
make uv-init          # Complete setup (~5s)
```

### Sync & Update

```bash
# Update dependencies
make update           # Traditional (pip)
make uv-update        # Fast (uv)
```

### Check Tools

```bash
# Verify UV is installed
make uv-check

# Show project information
make info

# Show git and test status
make status

# Show current version
make version
```

## Testing

### Basic Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage report
make test-cov

# Run tests in watch mode (auto-rerun on file changes)
make test-watch

# Run only previously failed tests
make test-failed

# Run tests with verbose output
make test-verbose
```

After running `make test-cov`, open `htmlcov/index.html` to view the detailed coverage report.

### Tox Multi-Environment Testing

Test across Python 3.12, 3.13, 3.14, and 3.15 automatically with tox-uv (10x faster):

```bash
# Run all tox environments (uses UV automatically)
make tox

# List available tox environments (two ways)
make tox-list
make tox-envs         # Alternative command

# Run in parallel (10x faster than sequential)
make tox-parallel

# Test specific Python versions (dynamic pattern rule)
make tox-py312        # Python 3.12 (automatically handled by tox-% pattern)
make tox-py313        # Python 3.13 (automatically handled by tox-% pattern)
make tox-py314        # Python 3.14 (automatically handled by tox-% pattern)
make tox-py315        # Python 3.15 (automatically handled by tox-% pattern)
make tox-py316        # Future Python 3.16 (will work automatically!)

# Run specific checks (dynamic pattern rule)
make tox-ruff-check   # Linting (automatically handled by tox-% pattern)
make tox-mypy         # Type checking (automatically handled by tox-% pattern)
make tox-coverage     # Coverage report (automatically handled by tox-% pattern)
make tox-quality      # Quality checks (automatically handled by tox-% pattern)
make tox-ci           # CI pipeline (automatically handled by tox-% pattern)

# Clean and recreate environments
make tox-clean        # Remove .tox directory
make tox-recreate     # Rebuild all environments
```

**Dynamic Pattern Rule:** The Makefile uses a `tox-%` pattern rule that automatically handles ANY tox environment. This means:

- No need to add explicit targets for new Python versions
- Works with any custom tox environment you add to `tox.ini`
- Future-proof (Python 3.16+ will work automatically)
- Discoverable via `make tox-envs`

**Note:** Tox automatically uses UV via the tox-uv plugin for 10-100x faster package installation.

## UV Fast Package Manager

UV provides 10-100x faster package installation. UV is integrated via the tox-uv plugin and is used automatically for all tox operations.

```bash
# Verify UV installation
make uv-check

# Direct pip access (advanced usage)
make uv-pip ARGS="list"              # List packages
make uv-pip ARGS="show requests"     # Show package info
make uv-pip ARGS="install httpx"     # Install package
```

**Note:** Most UV-specific Makefile targets have been removed. UV is now integrated via the tox-uv plugin, which automatically uses UV for all tox operations (creating environments, installing packages, etc.). This provides the speed benefits of UV without needing separate UV-specific targets. For direct UV usage, use the `uv` command directly or the `make uv-pip` target for pip operations.

## Code Quality

### Linting & Formatting

```bash
# Run linting (ruff)
make ruff-check

# Format code (ruff)
make ruff-format

# Check formatting without changes
make ruff-format-check

# Run type checking (mypy)
make mypy

# Run all quality checks (ruff + mypy)
make quality

# Run comprehensive checks (format-check + quality + tests)
make check
```

### Pre-commit Hooks

```bash
# Run pre-commit on all files (traditional)
make pre-commit

# Run with UV acceleration (9x faster)
make uv-pre-commit

# Install hooks
make install-hooks            # Traditional
make uv-pre-commit-install    # With UV
```

## Security & Dependencies

```bash
# Run security audit (pip-audit)
make pip-audit
```

## Build & Publish

```bash
# Build distribution packages (via tox)
make build

# Publish to TestPyPI (via tox, for testing)
make publish-test

# Publish to PyPI (via tox, use with caution!)
make publish
```

**Note:** Build and publish targets now use tox internally, ensuring consistent environments and automatic dependency management. The tox testenvs handle all build and publish operations using standard Python packaging tools (build, twine).

## Documentation

```bash
# Build Sphinx documentation (via tox)
make docs

# Build and serve documentation locally (via tox)
make serve-docs       # Opens at http://localhost:8000
```

**Note:** Documentation targets now use tox internally (`tox -e docs`, `tox -e serve-docs`), providing consistent environment management.

## Running the Application

```bash
# Run NHL Scrabble analyzer (via tox)
make run

# Run with verbose logging (via tox)
make run-verbose

# Run and output JSON (via tox)
make run-json
```

**Note:** These targets now use tox internally (`tox -e run`, `tox -e run -- --verbose`, etc.), which provides consistent environment management and automatic UV acceleration via tox-uv.

## Development Utilities

```bash
# Open Python shell with package loaded
make shell

# Watch tests (alias for test-watch)
make watch

# Initialize development environment
make init             # Setup venv + install + hooks

# Show project information
make info

# Show git and project status
make status

# Count lines of code
make count

# Show project directory tree
make tree
```

## Release Management

```bash
# Prepare for release (run all checks)
make release

# Show current version (via tox)
make version
```

The `make release` target runs all verification checks and provides a checklist for release steps. The `make version` target uses tox internally to display the package version.

## Cleaning

```bash
# Remove all build, test, and coverage artifacts
make clean

# Remove build artifacts only
make clean-build

# Remove Python artifacts only (.pyc, __pycache__, etc.)
make clean-pyc

# Remove test artifacts only
make clean-test

# Remove virtual environment
make clean-venv

# Remove tox environments
make tox-clean

# Complete clean (everything including venv)
make clean-all
```

## All-in-One Workflows

```bash
# Complete workflow: clean, init, check, build
make all

# Simulate CI pipeline locally (traditional)
make ci

# Simulate CI pipeline with tox-uv
make tox-ci
```

## Utility Targets

```bash
# Count lines of code
make count

# Show project directory tree
make tree
```

## Complete Target Reference

### Setup & Installation (9 targets)

| Target          | Description                                      |
| --------------- | ------------------------------------------------ |
| `venv`          | Create virtual environment                       |
| `install`       | Install package in editable mode                 |
| `install-dev`   | Install package with dev dependencies            |
| `install-hooks` | Install pre-commit hooks                         |
| `deps`          | Alias for install-dev                            |
| `update`        | Update all dependencies                          |
| `init`          | Complete initialization (venv + install + hooks) |
| `uv-init`       | Fast initialization with UV                      |
| `uv-check`      | Verify UV is installed                           |

### Testing (7 targets)

| Target             | Description                   |
| ------------------ | ----------------------------- |
| `test`             | Run all tests                 |
| `test-unit`        | Run unit tests only           |
| `test-integration` | Run integration tests only    |
| `test-cov`         | Run tests with coverage       |
| `test-watch`       | Run tests in watch mode       |
| `test-failed`      | Run only failed tests         |
| `test-verbose`     | Run tests with verbose output |

### Tox Multi-Environment (6 targets)

| Target         | Description                                                                                |
| -------------- | ------------------------------------------------------------------------------------------ |
| `tox`          | Run all tox environments                                                                   |
| `tox-list`     | List all tox environments                                                                  |
| `tox-envs`     | List all tox environments (alternative)                                                    |
| `tox-parallel` | Run tox in parallel                                                                        |
| `tox-clean`    | Clean tox environments                                                                     |
| `tox-recreate` | Recreate tox environments                                                                  |
| `tox-%`        | **Pattern rule** - Run any tox environment (e.g., tox-py312, tox-mypy, tox-coverage, etc.) |

**Note:** The `tox-%` pattern rule dynamically handles any tox environment:

- `make tox-py312`, `make tox-py312`, ..., `make tox-py315` (current Python versions)
- `make tox-py316`, `make tox-py317` (future Python versions - automatic support!)
- `make tox-ruff-check`, `make tox-mypy`, `make tox-coverage`, `make tox-quality`, `make tox-ci`
- Any custom environment you add to `tox.ini`

### UV Package Manager (10 targets)

| Target                  | Description              |
| ----------------------- | ------------------------ |
| `uv-check`              | Check UV installation    |
| `uv-venv`               | Create venv with UV      |
| `uv-install`            | Install with UV          |
| `uv-install-dev`        | Install dev deps with UV |
| `uv-update`             | Update deps with UV      |
| `uv-run`                | Run with UV              |
| `uv-init`               | Fast initialization      |
| `uv-pip`                | Direct UV pip access     |
| `uv-pre-commit`         | Run pre-commit with UV   |
| `uv-pre-commit-install` | Install hooks with UV    |

### Code Quality (8 targets)

| Target              | Description                           |
| ------------------- | ------------------------------------- |
| `ruff-check`        | Run ruff linter                       |
| `ruff-format`       | Format code with ruff                 |
| `ruff-format-check` | Check formatting                      |
| `mypy`              | Run mypy type checker                 |
| `quality`           | All quality checks                    |
| `check`             | All checks (format + quality + tests) |
| `pre-commit`        | Run pre-commit hooks                  |
| `uv-pre-commit`     | Pre-commit with UV                    |

### Security (1 target)

| Target      | Description        |
| ----------- | ------------------ |
| `pip-audit` | Run security audit |

### Build & Publish (3 targets)

| Target         | Description                 |
| -------------- | --------------------------- |
| `build`        | Build distribution packages |
| `publish-test` | Publish to TestPyPI         |
| `publish`      | Publish to PyPI             |

### Documentation (2 targets)

| Target       | Description                |
| ------------ | -------------------------- |
| `docs`       | Build Sphinx documentation |
| `serve-docs` | Build and serve docs       |

### Running (3 targets)

| Target        | Description               |
| ------------- | ------------------------- |
| `run`         | Run NHL Scrabble analyzer |
| `run-verbose` | Run with verbose logging  |
| `run-json`    | Run and output JSON       |

### Development (4 targets)

| Target   | Description                 |
| -------- | --------------------------- |
| `shell`  | Open Python shell           |
| `watch`  | Alias for test-watch        |
| `info`   | Show project information    |
| `status` | Show git and project status |

### Release (2 targets)

| Target    | Description          |
| --------- | -------------------- |
| `release` | Prepare for release  |
| `version` | Show current version |

### Cleaning (6 targets)

| Target        | Description                |
| ------------- | -------------------------- |
| `clean`       | Remove all artifacts       |
| `clean-build` | Remove build artifacts     |
| `clean-pyc`   | Remove Python artifacts    |
| `clean-test`  | Remove test artifacts      |
| `clean-venv`  | Remove virtual environment |
| `clean-all`   | Complete clean             |

### All-in-One (2 targets)

| Target | Description          |
| ------ | -------------------- |
| `all`  | Complete workflow    |
| `ci`   | Simulate CI pipeline |

### Utility (2 targets)

| Target  | Description         |
| ------- | ------------------- |
| `count` | Count lines of code |
| `tree`  | Show directory tree |

## Common Workflows

### First Time Setup

```bash
# Fast setup (recommended)
make uv-init
source .venv/bin/activate

# Or traditional setup
make init
source .venv/bin/activate
```

### Daily Development

```bash
source .venv/bin/activate
# ... make code changes ...
make test           # Quick test
make quality        # Check code quality
```

### Before Committing

```bash
make check          # Format + quality + tests
# or
make uv-pre-commit  # Run hooks with UV
```

### Before Pull Request

```bash
make tox-parallel   # Test all Python versions (fast!)
make check          # Final verification
```

### CI Simulation

```bash
make tox-ci         # Full CI pipeline locally
```

### Release Preparation

```bash
make release        # Runs all checks, shows checklist
make version        # Verify version
make build          # Build packages
```

## Environment Variables

The Makefile uses these variables (can be customized):

```makefile
PYTHON := python3.12        # Python executable
VENV := .venv               # Virtual environment directory
UV := uv                    # UV executable
```

## Tips & Tricks

### 1. Use UV for Speed

```bash
# Instead of:
make init           # ~50 seconds

# Use:
make uv-init        # ~5 seconds (10x faster!)
```

### 2. Parallel Testing

```bash
# Instead of:
make tox            # ~5 minutes

# Use:
make tox-parallel   # ~30 seconds (10x faster!)
```

### 3. Pre-commit with UV

```bash
# Instead of:
make pre-commit     # ~45 seconds first run

# Use:
make uv-pre-commit  # ~5 seconds (9x faster!)
```

### 4. Chain Commands

```bash
# Clean and rebuild
make clean-all && make uv-init

# Full verification
make clean && make check && make build
```

### 5. Pass Arguments to Tools

```bash
# Pass args to UV pip
make uv-pip ARGS="list --outdated"
make uv-pip ARGS="show requests"
```

## Troubleshooting

### Make Command Not Found

The Makefile requires GNU Make. On some systems:

```bash
# macOS
brew install make

# Ubuntu/Debian
sudo apt-get install make

# Verify
make --version
```

### Virtual Environment Issues

```bash
# Clean and recreate
make clean-venv
make uv-venv  # or make venv
```

### UV Not Found

```bash
# Check if UV is installed
make uv-check

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use traditional pip workflow
make init  # Falls back to pip
```

### Colors Not Showing

The Makefile uses ANSI color codes. If colors aren't displaying:

- Ensure your terminal supports ANSI colors
- On Windows, use Windows Terminal or WSL
- The Makefile uses `printf` for cross-platform compatibility

## Resources

- **Project README**: [../README.md](../README.md)
- **Contributing Guide**: [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **UV Documentation**: [UV.md](UV.md)
- **Tox Documentation**: [TOX.md](TOX.md) and [TOX-UV.md](TOX-UV.md)
- **Makefile Source**: [../Makefile](../Makefile)

## Summary

The Makefile provides **55 documented targets** organized in **16 logical groupings** covering all development needs:

- ✅ **6** Setup & Installation targets
- ✅ **6** Cleaning targets
- ✅ **7** Testing targets
- ✅ **6** Tox multi-environment targets (includes dynamic pattern rule)
- ✅ **2** UV fast package manager targets
- ✅ **7** Code quality targets
- ✅ **1** Security target
- ✅ **3** Build & publish targets
- ✅ **2** Documentation targets
- ✅ **3** Running targets
- ✅ **4** Development utility targets
- ✅ **2** Release management targets
- ✅ **1** All-in-one workflow target
- ✅ **1** CI/CD simulation target
- ✅ **2** Utility targets
- ✅ **1** Development workflow (informational section)

**Quick commands:**

```bash
make help           # View all 55 targets in 16 logical groupings
make init           # Setup development environment
make tox-parallel   # Fast testing (30s with tox-uv)
make tox-envs       # List all available tox environments
make tox-py312      # Test Python 3.12 (via dynamic pattern rule)
make tox-coverage   # Coverage report (via dynamic pattern rule)
make check          # Pre-commit verification
make ci             # CI simulation
```

**Dynamic Pattern Rule:** The `tox-%` pattern rule automatically handles any tox environment:

- Supports all current Python versions (3.12-3.15)
- Future-proof for new Python versions (3.16+)
- Works with any custom tox environment
- No maintenance needed for new environments

**Note:** The Makefile uses tool-based names (ruff-check, mypy, ruff-format, pip-audit) for clarity. Many targets now use tox internally for consistent environment management and automatic UV acceleration via tox-uv.

**Result:** Complete automation of the entire development workflow with 10-100x speedup via tox-uv integration, plus future-proof dynamic tox environment support!
