# NHL Scrabble Score Analyzer

[![CI](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml)
[![Python 3.10-3.13](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Powered by UV](https://img.shields.io/badge/powered%20by-uv-black?logo=astral)](https://github.com/astral-sh/uv)
[![GitHub stars](https://img.shields.io/github/stars/bdperkin/nhl-scrabble?style=social)](https://github.com/bdperkin/nhl-scrabble/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/commits/main)

A Python application that fetches current NHL roster data and calculates "Scrabble scores" for player names based on standard Scrabble letter values. Generate comprehensive reports showing team, division, and conference standings complete with playoff brackets!

## Features

- 🏒 **Live NHL Data** - Fetches current roster data directly from the official NHL API
- 📊 **Comprehensive Reports** - Multiple report types including:
  - Conference standings with total and average scores
  - Division standings breakdown
  - NHL-style playoff bracket (wild card format)
  - Team scores with top players
  - League-wide statistics and fun facts
- 🎯 **Flexible Output** - Text or JSON format output
- ⚙️ **Configurable** - Customize via environment variables or command-line options
- 🧪 **Well-Tested** - Comprehensive test suite with >90% coverage on core modules
- 📦 **Modern Python** - Uses type hints, dataclasses, and follows best practices
- 🛠️ **Developer-Friendly** - Self-documenting Makefile with 55 targets for all development tasks
- ⚡ **Lightning Fast** - Optional uv support for 10-100x faster package installation

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Install in development mode
make init

# Or manually with pip
pip install -e ".[dev]"
```

### Requirements

- Python 3.10-3.13
- Dependencies: `requests`, `click`, `pydantic`, `python-dotenv`, `rich`
- Note: UV acceleration is automatic when using tox (via tox-uv plugin)

## Quick Start

Run the analysis with default settings:

```bash
nhl-scrabble analyze
```

Or use the Python module directly:

```bash
python -m nhl_scrabble analyze
```

## Usage

### Basic Usage

```bash
# Run analysis with default settings
nhl-scrabble analyze

# Enable verbose logging
nhl-scrabble analyze --verbose

# Save output to a file
nhl-scrabble analyze --output report.txt

# Generate JSON output
nhl-scrabble analyze --format json --output report.json

# Customize number of top players shown
nhl-scrabble analyze --top-players 50 --top-team-players 10
```

### Configuration

Configure via environment variables:

```bash
export NHL_SCRABBLE_API_TIMEOUT=15
export NHL_SCRABBLE_API_RETRIES=5
export NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
export NHL_SCRABBLE_TOP_PLAYERS=30
export NHL_SCRABBLE_VERBOSE=true

nhl-scrabble analyze
```

Or create a `.env` file:

```env
NHL_SCRABBLE_API_TIMEOUT=15
NHL_SCRABBLE_API_RETRIES=5
NHL_SCRABBLE_RATE_LIMIT_DELAY=0.5
NHL_SCRABBLE_TOP_PLAYERS=30
NHL_SCRABBLE_VERBOSE=true
```

### Command-Line Options

```
Options:
  --format [text|json]      Output format (default: text)
  -o, --output PATH         Output file path (default: stdout)
  -v, --verbose             Enable verbose logging
  --top-players INTEGER     Number of top players to show (default: 20)
  --top-team-players INTEGER
                           Number of top players per team (default: 5)
  --help                   Show this message and exit
```

## How It Works

### Scrabble Letter Values

The analyzer uses standard English Scrabble letter point values:

- **1 point**: A, E, I, O, U, L, N, S, T, R
- **2 points**: D, G
- **3 points**: B, C, M, P
- **4 points**: F, H, V, W, Y
- **5 points**: K
- **8 points**: J, X
- **10 points**: Q, Z

### Workflow

1. **Fetch Teams** - Retrieves all NHL teams with division/conference info from the standings endpoint
1. **Get Rosters** - Fetches current roster for each team (with retry logic and rate limiting)
1. **Calculate Scores** - Sums Scrabble letter values for each player's name
1. **Aggregate Data** - Computes team, division, and conference totals
1. **Generate Reports** - Creates comprehensive reports with multiple views of the data

### NHL API Endpoints

- Standings: `https://api-web.nhle.com/v1/standings/now`
- Team rosters: `https://api-web.nhle.com/v1/roster/{team_abbrev}/current`

## Example Output

```
🏒 NHL Roster Scrabble Score Analyzer 🏒
================================================================================

🌎 CONFERENCE SCRABBLE SCORES
================================================================================

#1 Eastern
   Total: 15247 points
   Teams: 16 (BOS, BUF, CAR, CBJ, DET, FLA, MTL, NJD, NYI, NYR, OTT, PHI, PIT, TBL, TOR, WSH)
   Players: 512
   Avg per team: 952.9

...

🎰 WILD CARD PLAYOFF STANDINGS (Scrabble Edition)
================================================================================
Top 3 from each division + 2 wild cards per conference
...

📊 TEAM SCRABBLE SCORES (Sorted by Total Score)
================================================================================

#1 TOR (Atlantic): 1523 points (28 players)
   1. Alexander Ovechkin: 87 (Alexander=45, Ovechkin=42)
   2. Connor McDavid: 65 (Connor=32, McDavid=33)
   ...
```

## Development

### Setup Development Environment

The project includes a comprehensive Makefile for all development tasks:

```bash
# Clone the repository
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

# Initialize development environment
make init           # Creates venv, installs deps, sets up hooks

# Activate virtual environment
source .venv/bin/activate

# View all available commands
make help
```

Or manually:

```bash
# Clone and install with dev dependencies
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

Using Make (recommended):

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run all quality checks (format, lint, type-check, tests)
make check
```

Or directly with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration -m integration
```

### Multi-Environment Testing with Tox

The project supports testing across multiple Python versions using [tox](https://tox.wiki/):

```bash
# Test across all Python versions (3.10, 3.11, 3.12, 3.13)
make tox

# Run in parallel for faster results
make tox-parallel

# Clean and recreate environments
make tox-clean
make tox-recreate

# List all available tox environments
make tox-list
make tox-envs       # Alternative way to list environments

# Use dynamic pattern rule for any tox environment:
make tox-py310      # Test Python 3.10 (handled by pattern rule)
make tox-py313      # Test Python 3.13 (handled by pattern rule)
make tox-coverage   # Coverage report (handled by pattern rule)
make tox-ruff-check # Linting (handled by pattern rule)
make tox-mypy       # Type checking (handled by pattern rule)
make tox-ci         # Simulate full CI pipeline (handled by pattern rule)

# Or use tox directly:
tox -e py310        # Test Python 3.10
tox -e py313        # Test Python 3.13
tox -e coverage     # Coverage report
tox -e ruff-check   # Linting
tox -e mypy         # Type checking
tox -e ci           # Simulate full CI pipeline
```

Or use tox directly:

```bash
# Run all default environments
tox

# Run in parallel
tox -p auto

# Run specific environment
tox -e py310
tox -e py313
tox -e ruff-check
tox -e mypy
tox -e coverage

# Recreate environments (useful after dependency changes)
tox -r
```

See [docs/TOX.md](docs/TOX.md) for complete tox documentation and [docs/TOX-UV.md](docs/TOX-UV.md) for tox with UV acceleration (10-100x faster).

### Fast Package Management with UV

The project uses [uv](https://github.com/astral-sh/uv) via the tox-uv plugin, providing 10-100x faster package management automatically when using tox:

```bash
# UV acceleration is automatic with tox
make tox              # Uses UV automatically
make tox-parallel     # Even faster with parallel execution

# Check if uv is available (optional)
make uv-check

# Direct UV pip access (advanced usage)
make uv-pip ARGS="list"
```

**Note:** Individual uv-\* Makefile targets have been removed. UV is now integrated via tox-uv and works automatically with all tox commands. See [docs/TOX-UV.md](docs/TOX-UV.md) for complete tox-uv documentation.

### Pre-commit Hooks

The project uses comprehensive pre-commit hooks (38 total) for automatic code quality checks:

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**Hook Categories:**

- **Meta hooks** (3): Configuration validation (check-hooks-apply, check-useless-excludes, sync-pre-commit-deps)
- **File quality** (18): Formatting, syntax, security (trailing-whitespace, check-yaml, detect-private-key, etc.)
- **Python quality** (7): Code patterns (blanket-noqa, mock-methods, eval, type-annotations, etc.)
- **Project validation** (1): pyproject.toml validation against PEP standards (validate-pyproject)
- **YAML linting** (1): YAML file validation and linting (yamllint)
- **Spelling** (1): Code and documentation spell checking (codespell)
- **Markdown** (2): Markdown linting (pymarkdown) and formatting (mdformat)
- **UV** (1): Dependency lock file validation (uv-lock)
- **Flake8** (1): Python code linting and style checking (flake8)
- **Ruff** (2): Comprehensive linting and formatting (ruff-check, ruff-format)
- **MyPy** (1): Strict type checking

All hooks run automatically on commit, ensuring code quality before changes are committed.

### Code Quality

Using Make (recommended):

```bash
# Format code
make ruff-format

# Check formatting (no changes)
make ruff-format-check

# Lint code
make ruff-check

# Type check
make mypy

# Run all quality checks
make quality

# Run everything (format-check + quality + tests)
make check
```

Or directly:

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src
```

### Project Structure

```
nhl-scrabble/
├── src/nhl_scrabble/          # Main package
│   ├── api/                   # NHL API client
│   ├── scoring/               # Scrabble scoring logic
│   ├── models/                # Data models
│   ├── processors/            # Business logic
│   ├── reports/               # Report generators
│   ├── cli.py                 # CLI interface
│   ├── config.py              # Configuration
│   ├── logging_config.py      # Logging setup
│   └── py.typed               # PEP 561 type marker
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test fixtures
├── docs/                      # Documentation
├── pyproject.toml             # Project & UV configuration
├── uv.lock                    # Dependency lock file (1,957 lines)
├── .pre-commit-config.yaml    # Pre-commit hooks (32 hooks)
├── .python-version            # Python versions (3.10-3.13)
└── tox.ini                    # Testing automation
```

## Development Workflow

The Makefile provides a streamlined development workflow with 55 documented targets:

```bash
# View all available commands
make help               # Self-documenting help with color output

# First time setup
make init               # Creates venv, installs deps, sets up hooks

# Daily development
make test-watch         # Run tests automatically on file changes

# Before committing
make check              # Run all checks (format, ruff, mypy, tests)

# Simulate CI pipeline
make ci                 # Run the full CI pipeline locally

# Other useful targets
make clean              # Remove all build/test artifacts
make ruff-format        # Auto-format code with ruff
make build              # Build distribution packages
make run                # Run the NHL Scrabble analyzer
```

### Makefile Quick Reference

| Category      | Targets                                             | Description         |
| ------------- | --------------------------------------------------- | ------------------- |
| **Setup**     | `init`, `venv`, `install-dev`, `install-hooks`      | Environment setup   |
| **Testing**   | `test`, `test-cov`, `test-unit`, `test-integration` | Run tests           |
| **Quality**   | `ruff-check`, `ruff-format`, `mypy`, `check`        | Code quality        |
| **Cleaning**  | `clean`, `clean-all`                                | Remove artifacts    |
| **Building**  | `build`, `publish`                                  | Build and publish   |
| **Running**   | `run`, `run-verbose`, `run-json`                    | Run the application |
| **Utilities** | `info`, `status`, `version`, `count`                | Project info        |

See [docs/MAKEFILE.md](docs/MAKEFILE.md) for complete documentation of all 55 targets.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
1. Make your changes
1. Run tests and linting
1. Commit your changes (`git commit -m 'Add amazing feature'`)
1. Push to the branch (`git push origin feature/amazing-feature`)
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NHL API for providing roster data
- Scrabble is a trademark of Hasbro, Inc.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Documentation

- [README.md](README.md) - This file, project overview
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [docs/MAKEFILE.md](docs/MAKEFILE.md) - Complete Makefile reference
- [docs/TOX.md](docs/TOX.md) - Tox testing guide
- [docs/TOX-UV.md](docs/TOX-UV.md) - Tox with UV acceleration guide
- [docs/UV.md](docs/UV.md) - UV fast package manager guide
- [docs/UV-ECOSYSTEM.md](docs/UV-ECOSYSTEM.md) - Complete UV ecosystem integration
- [docs/PRECOMMIT-UV.md](docs/PRECOMMIT-UV.md) - Pre-commit with UV acceleration
- [CLAUDE.md](CLAUDE.md) - Architecture documentation

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/bdperkin/nhl-scrabble/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/bdperkin/nhl-scrabble/discussions)

## Development Stats

- **Lines of Code**: ~1,866 (src)
- **Lines of Tests**: ~680 (tests)
- **Test Coverage**: 49.93% overall, >90% on core modules
- **Python Modules**: 15 core modules
- **Tests**: 36 tests (100% passing)
- **Makefile Targets**: 55 documented targets
- **Pre-commit Hooks**: 38 hooks (meta, pre-commit-hooks, pygrep-hooks, validate-pyproject, yamllint, codespell, pymarkdown, mdformat, uv, flake8, ruff, mypy)
- **Dependency Lock**: uv.lock with 1,957 lines (deterministic builds)
- **CI/CD**: GitHub Actions on Python 3.10, 3.11, 3.12, 3.13

______________________________________________________________________

Made with ❤️ for hockey and word games
