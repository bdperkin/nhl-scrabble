<p align="center">
  <img src=".github/logo.png" alt="NHL Scrabble Logo" width="256">
</p>

<h1 align="center">NHL Scrabble Score Analyzer</h1>

<p align="center">

<!-- Build & Quality -->

[![CI](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml)
[![CodeQL](https://github.com/bdperkin/nhl-scrabble/actions/workflows/codeql.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/codeql.yml)
[![Docs](https://github.com/bdperkin/nhl-scrabble/actions/workflows/docs.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg)](https://codecov.io/gh/bdperkin/nhl-scrabble)

<!-- Code Quality -->

[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![interrogate](./interrogate_badge.svg)](https://interrogate.readthedocs.io/)

<!-- Package Info -->

[![Python 3.12-3.14](https://img.shields.io/badge/python-3.12--3.14-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by UV](https://img.shields.io/badge/powered%20by-uv-black?logo=astral)](https://github.com/astral-sh/uv)
[![Latest Release](https://img.shields.io/github/v/release/bdperkin/nhl-scrabble?include_prereleases)](https://github.com/bdperkin/nhl-scrabble/releases)

<!-- Community & Activity -->

[![Contributors](https://img.shields.io/github/contributors/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/graphs/contributors)
[![GitHub stars](https://img.shields.io/github/stars/bdperkin/nhl-scrabble?style=social)](https://github.com/bdperkin/nhl-scrabble/stargazers)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/bdperkin/nhl-scrabble/pulls)
[![GitHub issues](https://img.shields.io/github/issues/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/issues)
[![Commit Activity](https://img.shields.io/github/commit-activity/m/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)
[![GitHub last commit](https://img.shields.io/github/last-commit/bdperkin/nhl-scrabble)](https://github.com/bdperkin/nhl-scrabble/commits/main)

<!-- Maintenance -->

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bdperkin/nhl-scrabble/graphs/commit-activity)

</p>

A [Python](https://www.python.org/) application that fetches current NHL roster data and calculates "Scrabble scores" for player names based on standard Scrabble letter values. Generate comprehensive reports showing team, division, and conference standings complete with playoff brackets!

## Features

- 🏒 **Live NHL Data** - Fetches current roster data directly from the official [NHL API](https://gitlab.com/dword4/nhlapi)
- 🌐 **Web Interface** - [FastAPI](https://fastapi.tiangolo.com/)-powered web server with auto-generated API documentation
  - **Interactive Dashboard** - Modern, responsive UI with real-time analysis
  - **Data Visualizations** - [Chart.js](https://www.chartjs.org/)-powered graphs and charts
  - **HTMX Integration** - [HTMX](https://htmx.org/)-powered dynamic updates without page reloads
  - **REST API** - Programmatic access with [OpenAPI](https://www.openapis.org/) documentation
  - **Mobile-Friendly** - Fully responsive design for all devices
  - **Accessibility** - WCAG 2.1 AA compliant with keyboard navigation and screen reader support
- 📊 **Comprehensive Reports** - Multiple report types including:
  - Conference standings with total and average scores
  - Division standings breakdown
  - NHL-style playoff bracket (wild card format)
  - Team scores with top players
  - League-wide statistics and fun facts
- 📈 **Progress Tracking** - Real-time progress bars show operation status (API fetching, scoring, report generation)
- 🎯 **Flexible Output** - Text, JSON, or HTML format output with responsive design
- 🎨 **Colorized Logging** - Color-coded log levels (DEBUG=cyan, INFO=green, WARNING=yellow, ERROR=red) with automatic TTY detection and NO_COLOR support
- ⚙️ **Configurable** - Customize via environment variables or command-line options
- 🧪 **Well-Tested** - Comprehensive test suite with >90% coverage on core modules, including full web interface integration tests
- 📦 **Modern Python** - Uses type hints, dataclasses, and follows best practices
- 🛠️ **Developer-Friendly** - Self-documenting Makefile with 55 targets for all development tasks
- ⚡ **Lightning Fast** - Optional uv support for 10-100x faster package installation
- 🔒 **Production-Ready** - Security headers, CORS configuration, caching, and deployment guides for nginx, Docker, and cloud platforms

## Screenshots

### Web Interface

The NHL Scrabble web interface provides a modern, interactive experience for analyzing player name scores.

**Main Dashboard**

- Clean, responsive design with intuitive navigation
- One-click analysis with configurable options (top players, team players, caching)
- Real-time loading indicators during NHL API fetching (~30 seconds)
- Mobile-friendly hamburger menu for smaller screens

**Analysis Results**

- **Top Players Table** - Sortable table showing highest-scoring players across all teams with click-to-sort functionality
- **Team Standings** - Complete team rankings with total scores, averages, and player counts
- **Division Standings** - Teams grouped by division (Atlantic, Metropolitan, Central, Pacific)
- **Conference Standings** - Eastern vs Western conference breakdown
- **Playoff Bracket** - Mock playoff matchups based on Scrabble scores with seed indicators (y, x, z, p, e)
- **Statistics Summary** - Overall stats including total players, highest/lowest scores, team leaders

**Interactive Features**

- **Data Visualizations** - Chart.js charts showing score distribution, team comparison, and conference breakdown
- **Export Options** - Download results as JSON, CSV, or PDF
- **Table Sorting** - Click any column header to sort (name, score, team)
- **Responsive Charts** - Interactive tooltips and legends on all visualizations

**API Documentation**

- **Swagger UI** (`/docs`) - Interactive API explorer with try-it-now functionality
- **ReDoc** (`/redoc`) - Clean, organized API reference documentation
- **Health Check** (`/health`) - JSON endpoint showing service status and version

### CLI Output

**Text Output** (Default)

```
🏒 NHL SCRABBLE SCORE ANALYSIS 🏒

TOP 20 PLAYERS BY SCRABBLE SCORE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Alexander Ovechkin (WSH)    45 points
2. Zdeno Chara (BOS)           42 points
...
```

**JSON Output** (Machine-Readable)

```json
{
  "top_players": [...],
  "team_standings": [...],
  "division_standings": {...},
  "conference_standings": {...},
  "playoff_bracket": {...},
  "stats": {...}
}
```

**HTML Output** (Browser)

- Fully styled HTML report with embedded CSS
- Printable format for sharing
- Same comprehensive data as text output

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

- **Supported**: [Python](https://www.python.org/) 3.12, 3.13, 3.14
- **Experimental**: Python 3.15-dev (CI testing only, may have issues)
- Dependencies: [`requests`](https://requests.readthedocs.io/), [`click`](https://click.palletsprojects.com/), [`pydantic`](https://docs.pydantic.dev/), [`python-dotenv`](https://saurabh-kumar.com/python-dotenv/), [`rich`](https://rich.readthedocs.io/), [`fastapi`](https://fastapi.tiangolo.com/), [`uvicorn`](https://www.uvicorn.org/), [`jinja2`](https://jinja.palletsprojects.com/)
- Note: [UV](https://docs.astral.sh/uv/) acceleration is automatic when using [tox](https://tox.wiki/) (via [tox-uv](https://github.com/tox-dev/tox-uv) plugin)

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
# Run analysis with default settings (shows progress bars)
nhl-scrabble analyze

# Show version
nhl-scrabble -V               # Short option
nhl-scrabble --version        # Long option

# Show help
nhl-scrabble -h               # Short option
nhl-scrabble --help           # Long option
nhl-scrabble analyze -h       # Command help

# Enable verbose logging (with colorized output in terminal)
nhl-scrabble analyze -v       # Short option
nhl-scrabble analyze --verbose # Long option

# Disable colorized output (NO_COLOR standard)
NO_COLOR=1 nhl-scrabble analyze -v

# Suppress progress bars (useful for scripting/automation)
nhl-scrabble analyze -q       # Short option
nhl-scrabble analyze --quiet  # Long option

# Save output to a file
nhl-scrabble analyze -o report.txt        # Short option
nhl-scrabble analyze --output report.txt  # Long option

# Generate JSON output
nhl-scrabble analyze -f json -o report.json           # Short options
nhl-scrabble analyze --format json --output report.json # Long options

# Generate HTML output (opens in browser)
nhl-scrabble analyze -f html -o report.html # Short options
nhl-scrabble analyze --format html --output report.html

# Customize number of top players shown
nhl-scrabble analyze --top-players 50 --top-team-players 10

# Mix short and long options (both work!)
nhl-scrabble analyze -f json --output report.json -v
```

### Web Interface

Start the web server for browser-based access:

```bash
# Start web server on default port (8000)
nhl-scrabble serve

# Start with auto-reload for development
nhl-scrabble serve --reload

# Custom host and port
nhl-scrabble serve --host 0.0.0.0 --port 5000
```

Once started, visit:

- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

The web interface provides:

- ✅ RESTful API endpoints for programmatic access
- 📚 Auto-generated OpenAPI documentation
- 🩺 Health check endpoint for monitoring

### Interactive Dashboard

Launch an interactive terminal dashboard with real-time statistics and visualizations:

```bash
# Launch dashboard
nhl-scrabble dashboard

# Filter by division
nhl-scrabble dashboard --divisions Atlantic

# Filter by conference
nhl-scrabble dashboard --conferences Eastern

# Run for 30 seconds then exit
nhl-scrabble dashboard --duration 30

# Display static snapshot (no live updates)
nhl-scrabble dashboard --static

# Combine filters
nhl-scrabble dashboard --divisions Metropolitan --conferences Eastern
```

The dashboard displays:

- 🏆 Top teams by total Scrabble score
- ⭐ Top players by individual score
- 📊 Division standings with statistics
- 🏟️ Conference standings overview
- 🎨 Rich visualizations with tables and panels
- ⚡ Live updates (configurable refresh rate)

Press `Ctrl+C` to exit the dashboard.

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
  -q, --quiet               Suppress progress bars
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

The project supports testing across multiple Python versions using [tox](https://tox.wiki/) with [pytest](https://docs.pytest.org/):

```bash
# Test across all Python versions (3.12, 3.13, 3.14)
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
make tox-py312      # Test Python 3.12 (handled by pattern rule)
make tox-py313      # Test Python 3.13 (handled by pattern rule)
make tox-py314      # Test Python 3.14 (handled by pattern rule)
make tox-coverage   # Coverage report (handled by pattern rule)
make tox-ruff-check # Linting (handled by pattern rule)
make tox-mypy       # Type checking (handled by pattern rule)
make tox-ci         # Simulate full CI pipeline (handled by pattern rule)

# Or use tox directly:
tox -e py312        # Test Python 3.12
tox -e py313        # Test Python 3.13
tox -e py314        # Test Python 3.14
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
tox -e py312
tox -e py313
tox -e py314
tox -e ruff-check
tox -e mypy
tox -e coverage

# Recreate environments (useful after dependency changes)
tox -r
```

See [docs/TOX.md](docs/TOX.md) for complete tox documentation and [docs/TOX-UV.md](docs/TOX-UV.md) for tox with UV acceleration (10-100x faster).

### Fast Package Management with UV

The project uses [UV](https://docs.astral.sh/uv/) via the [tox-uv](https://github.com/tox-dev/tox-uv) plugin, providing 10-100x faster package management automatically when using [tox](https://tox.wiki/):

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

The project uses comprehensive [pre-commit](https://pre-commit.com/) hooks (55 total) for automatic code quality checks:

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
- **Python imports** (2): Import sorting and absolute imports ([isort](https://pycqa.github.io/isort/), absolufy-imports)
- **Project validation** (1): pyproject.toml validation against [PEP](https://peps.python.org/) standards (validate-pyproject)
- **Python formatting** (2): [Black](https://black.readthedocs.io/) formatting and [PEP 8](https://peps.python.org/pep-0008/) auto-formatting ([autopep8](https://github.com/hhatto/autopep8))
- **Docstring formatting** (1): Python docstring formatting ([docformatter](https://docformatter.readthedocs.io/))
- **YAML linting** (1): YAML file validation and linting ([yamllint](https://yamllint.readthedocs.io/))
- **Spelling** (1): Code and documentation spell checking ([codespell](https://github.com/codespell-project/codespell))
- **Markdown** (2): Markdown linting ([pymarkdown](https://github.com/jackdewinter/pymarkdown)) and formatting ([mdformat](https://mdformat.readthedocs.io/))
- **Documentation** (2): RST style linting ([doc8](https://doc8.readthedocs.io/)) and syntax checking ([rstcheck](https://rstcheck.readthedocs.io/))
- **UV** (1): Dependency lock file validation (uv-lock)
- **Flake8** (1): Python code linting and style checking ([flake8](https://flake8.pycqa.org/))
- **Ruff** (2): Comprehensive linting and formatting ([ruff](https://docs.astral.sh/ruff/))
- **MyPy** (1): Strict type checking ([mypy](https://mypy-lang.org/))

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
# Format code with ruff
ruff format .

# Lint code with ruff
ruff check .

# Type check with mypy
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
├── .python-version            # Python versions (3.12-3.14)
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

### Dependency Licenses

All runtime dependencies use permissive licenses compatible with MIT (Apache, BSD, ISC, etc.). See [LICENSES.md](LICENSES.md) for the complete list of all dependency licenses.

To verify license compliance:

```bash
tox -e licenses
```

## Acknowledgments

- NHL API for providing roster data
- Scrabble is a trademark of Hasbro, Inc.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Documentation

Documentation is organized by purpose following the [Diátaxis framework](https://diataxis.fr/):

### 📚 [Tutorials](docs/tutorials/) - Learning-oriented lessons

Step-by-step guides for beginners:

- [Getting Started](docs/tutorials/01-getting-started.md) - Your first NHL Scrabble analysis
- [Understanding Output](docs/tutorials/02-understanding-output.md) - Deep dive into reports
- [First Contribution](docs/tutorials/03-first-contribution.md) - Make your first code contribution

### 🛠️ [How-to Guides](docs/how-to/) - Problem-oriented recipes

Practical solutions to specific tasks:

- [Installation Variations](docs/how-to/installation.md) - Different ways to install
- [Run Tests](docs/how-to/run-tests.md) - Execute different test configurations
- [Add Report Type](docs/how-to/add-report-type.md) - Create custom reports
- [Use UV Package Manager](docs/how-to/use-uv.md) - 10-100x faster installation
- [And more...](docs/how-to/)

### 📖 [Reference](docs/reference/) - Technical specifications

Complete API and configuration documentation:

- [CLI Reference](docs/reference/cli.md) - All commands and options
- [Configuration](docs/reference/configuration.md) - All settings explained
- [Makefile Reference](docs/reference/makefile.md) - All 55 Makefile targets
- [And more...](docs/reference/)

### 💡 [Explanation](docs/explanation/) - Conceptual understanding

Background and design philosophy:

- [Why Scrabble Scoring?](docs/explanation/why-scrabble-scoring.md) - The concept explained
- [Architecture Overview](docs/explanation/architecture.md) - System design
- [NHL API Strategy](docs/explanation/nhl-api-strategy.md) - API integration approach
- [And more...](docs/explanation/)

### Community Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [SECURITY.md](SECURITY.md) - Security policy
- [SUPPORT.md](SUPPORT.md) - Getting help
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CLAUDE.md](CLAUDE.md) - Project overview for Claude Code

## Security

This project takes security seriously and uses multiple tools to ensure dependencies are safe and up-to-date:

- **[Dependabot](https://docs.github.com/en/code-security/dependabot)**: Automated dependency updates and security alerts
  - Runs weekly (Mondays 9:00 AM ET)
  - Monitors Python dependencies and [GitHub Actions](https://docs.github.com/en/actions)
  - Creates PRs for security vulnerabilities immediately
  - Groups non-security updates to reduce noise
- **[pip-audit](https://pypi.org/project/pip-audit/)**: Scans dependencies for known vulnerabilities in CI
- **[Pre-commit hooks](https://pre-commit.com/)**: 55 comprehensive quality and security checks

### Reporting Security Vulnerabilities

If you discover a security vulnerability, please review our [Security Policy](SECURITY.md) for responsible disclosure guidelines. Do **not** report security vulnerabilities through public GitHub issues.

### Dependency Updates

Dependabot automatically creates pull requests for:

- **Security updates**: Immediate PRs for any vulnerable dependencies
- **Development dependencies**: Weekly grouped PRs for minor/patch updates
- **Production dependencies**: Weekly grouped PRs for patch updates only
- **GitHub Actions**: Weekly updates for workflow dependencies

All Dependabot PRs are automatically labeled, assigned, and follow [conventional commit](https://www.conventionalcommits.org/) format (`deps(scope): description`).

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/bdperkin/nhl-scrabble/issues)

## Development Stats

- **Lines of Code**: ~1,866 (src)
- **Lines of Tests**: ~680 (tests)
- **Test Coverage**: 49.93% overall, >90% on core modules
- **Python Modules**: 15 core modules
- **Tests**: 36 tests (100% passing)
- **Makefile Targets**: 55 documented targets
- **Pre-commit Hooks**: 54 hooks ([pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks), [pygrep-hooks](https://github.com/pre-commit/pygrep-hooks), [isort](https://pycqa.github.io/isort/), [interrogate](https://interrogate.readthedocs.io/), [deptry](https://deptry.com/), [unimport](https://unimport.hakancelik.dev/), [pydocstyle](http://www.pydocstyle.org/), [vulture](https://github.com/jendrikseipp/vulture), [blocklint](https://github.com/PrincetonUniversity/blocklint), [gitlint](https://jorisroovers.com/gitlint/), absolufy-imports, [validate-pyproject](https://validate-pyproject.readthedocs.io/), [pyroma](https://github.com/regebro/pyroma), [tox-ini-fmt](https://github.com/tox-dev/tox-ini-fmt), [yamllint](https://yamllint.readthedocs.io/), [codespell](https://github.com/codespell-project/codespell), [pymarkdown](https://github.com/jackdewinter/pymarkdown), [mdformat](https://mdformat.readthedocs.io/), [doc8](https://doc8.readthedocs.io/), [rstcheck](https://rstcheck.readthedocs.io/), [uv](https://docs.astral.sh/uv/), [flake8](https://flake8.pycqa.org/), autoflake, [black](https://black.readthedocs.io/), docformatter, [ruff](https://docs.astral.sh/ruff/), [mypy](https://mypy-lang.org/))
- **Dependency Lock**: [uv.lock](https://docs.astral.sh/uv/) with 1,957 lines (deterministic builds)
- **CI/CD**: [GitHub Actions](https://docs.github.com/en/actions) on [Python](https://www.python.org/) 3.12, 3.13, 3.14 (required), 3.15-dev (experimental)

______________________________________________________________________

Made with ❤️ for hockey and word games
