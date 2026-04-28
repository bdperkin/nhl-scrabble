<p align="center">
  <img src="https://raw.githubusercontent.com/bdperkin/nhl-scrabble/main/.github/logo.png" alt="NHL Scrabble Logo" width="256">
</p>

<h1 align="center">NHL Scrabble Score Analyzer</h1>

<p align="center">

<!-- Build & Quality -->

[![CI](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/ci.yml)
[![CodeQL](https://github.com/bdperkin/nhl-scrabble/actions/workflows/codeql.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/codeql.yml)
[![SBOM](https://github.com/bdperkin/nhl-scrabble/actions/workflows/sbom.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/sbom.yml)
[![Docs](https://github.com/bdperkin/nhl-scrabble/actions/workflows/docs.yml/badge.svg)](https://github.com/bdperkin/nhl-scrabble/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/bdperkin/nhl-scrabble/branch/main/graph/badge.svg)](https://codecov.io/gh/bdperkin/nhl-scrabble)

<!-- Code Quality -->

[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/bdperkin/nhl-scrabble/main.svg)](https://results.pre-commit.ci/latest/github/bdperkin/nhl-scrabble/main)
[![interrogate](https://raw.githubusercontent.com/bdperkin/nhl-scrabble/main/interrogate_badge.svg)](https://interrogate.readthedocs.io/)

<!-- Package Info -->

[![PyPI version](https://img.shields.io/pypi/v/nhl-scrabble.svg)](https://pypi.org/project/nhl-scrabble/)
[![PyPI downloads](https://img.shields.io/pypi/dm/nhl-scrabble.svg)](https://pypi.org/project/nhl-scrabble/)
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

- 🏒 **Live NHL Data** - Fetches current roster data from the official [NHL API](https://gitlab.com/dword4/nhlapi)
- 🌐 **Web Interface** - [FastAPI](https://fastapi.tiangolo.com/)-powered server with interactive dashboard
  - Interactive dashboard with real-time analysis
  - [Chart.js](https://www.chartjs.org/) visualizations and graphs
  - REST API with [OpenAPI](https://www.openapis.org/) documentation
  - Mobile-friendly responsive design (WCAG 2.1 AA)
- 📊 **Comprehensive Reports** - Conference/division standings, playoff brackets, team scores, statistics
- 📈 **Progress Tracking** - Real-time progress bars for long operations
- 🎯 **Flexible Output** - Text, JSON, or HTML format
- 🎨 **Colorized Logging** - Color-coded log levels with TTY detection and NO_COLOR support
- 🧪 **Well-Tested** - >90% coverage on core modules with 170+ tests
- ⚡ **Lightning Fast** - [UV](https://docs.astral.sh/uv/) support for 10-100x faster installation
- 🔒 **Production-Ready** - Security headers, CORS, caching, deployment guides

## Screenshots

### Web Interface

The NHL Scrabble web interface provides a modern, interactive experience:

- **Main Dashboard** - Clean, responsive design with one-click analysis
- **Analysis Results** - Sortable tables, standings, playoff brackets, statistics
- **Interactive Features** - Chart.js visualizations, export (JSON/CSV/PDF), table sorting
- **API Documentation** - Swagger UI (`/docs`) and ReDoc (`/redoc`)

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

**JSON Output** - Machine-readable format for integrations

**HTML Output** - Fully styled browser report with embedded CSS

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

For detailed usage, see the [CLI Tutorial](docs/tutorials/using-the-cli.md).

## Usage

### CLI Commands

```bash
# Basic analysis
nhl-scrabble analyze

# Verbose output with colorized logging
nhl-scrabble analyze -v

# JSON output to file
nhl-scrabble analyze -f json -o report.json

# HTML output
nhl-scrabble analyze -f html -o report.html

# Customize display
nhl-scrabble analyze --top-players 50 --top-team-players 10
```

### Web Server

```bash
# Start web server (default port 8000)
nhl-scrabble serve

# Custom host and port with auto-reload
nhl-scrabble serve --host 0.0.0.0 --port 5000 --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### Interactive Dashboard

```bash
# Launch terminal dashboard
nhl-scrabble dashboard

# Filter by division/conference
nhl-scrabble dashboard --divisions Atlantic --conferences Eastern

# Static snapshot (no live updates)
nhl-scrabble dashboard --static
```

**Complete Usage Documentation:**

- [CLI Tutorial](docs/tutorials/using-the-cli.md) - Step-by-step CLI guide
- [CLI Reference](docs/reference/cli.md) - All commands and options
- [Configuration Guide](docs/reference/configuration.md) - Environment variables and settings

## How It Works

The analyzer uses standard English Scrabble letter point values (A=1, Z=10, etc.) to score player names. It fetches live NHL data, calculates scores, aggregates by team/division/conference, and generates comprehensive reports with playoff brackets.

**Learn More:**

- [Why Scrabble Scoring?](docs/explanation/why-scrabble-scoring.md) - The concept explained
- [How Scrabble Scoring Works](docs/explanation/how-scrabble-scoring-works.md) - Detailed scoring logic
- [Architecture Overview](docs/explanation/architecture.md) - System design
- [NHL API Strategy](docs/explanation/nhl-api-strategy.md) - API integration approach

## Development

### Quick Start

```bash
# Clone and setup
git clone https://github.com/bdperkin/nhl-scrabble.git
cd nhl-scrabble
make init
source .venv/bin/activate

# View all available commands (57 targets)
make help
```

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Multi-version testing with tox
make tox              # Test Python 3.12, 3.13, 3.14
make tox-parallel     # Faster parallel execution
```

### Code Quality

```bash
# Format and lint
make ruff-format
make ruff-check

# Type checking
make mypy

# Run all quality checks
make quality

# Full validation (format + quality + tests)
make check
```

### Pre-commit Hooks

The project uses 67 comprehensive pre-commit hooks for automatic code quality validation:

```bash
# Install hooks (one-time)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**Complete Development Documentation:**

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines and workflow
- [Makefile Reference](docs/reference/makefile.md) - All 57 Makefile targets
- [Testing Guide](docs/how-to/run-tests.md) - Test execution and configuration
- [UV Package Manager](docs/how-to/use-uv.md) - 10-100x faster installation

## Project Structure

```
nhl-scrabble/
├── src/nhl_scrabble/          # Main package
│   ├── api/                   # NHL API client
│   ├── scoring/               # Scrabble scoring logic
│   ├── models/                # Data models (Pydantic)
│   ├── processors/            # Business logic
│   ├── reports/               # Report generators
│   ├── cli.py                 # CLI interface (Click)
│   └── config.py              # Configuration management
├── tests/                     # Test suite (170+ tests)
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                      # Documentation (Diátaxis framework)
├── pyproject.toml             # Project & UV configuration
└── uv.lock                    # Dependency lock file (1,957 lines)
```

See [Architecture Overview](docs/explanation/architecture.md) for detailed system design.

## Documentation

**Online Documentation:** https://bdperkin.github.io/nhl-scrabble/

Documentation follows the [Diátaxis framework](https://diataxis.fr/):

- **[Tutorials](docs/tutorials/)** - Step-by-step lessons for beginners
  - [Getting Started](docs/tutorials/01-getting-started.md)
  - [Understanding Output](docs/tutorials/02-understanding-output.md)
  - [First Contribution](docs/tutorials/03-first-contribution.md)
- **[How-to Guides](docs/how-to/)** - Practical solutions to specific tasks
  - [Installation Variations](docs/how-to/installation.md)
  - [Run Tests](docs/how-to/run-tests.md)
  - [Add Report Type](docs/how-to/add-report-type.md)
  - [Use UV Package Manager](docs/how-to/use-uv.md)
- **[Reference](docs/reference/)** - Technical specifications
  - [CLI Reference](docs/reference/cli.md)
  - [Configuration](docs/reference/configuration.md)
  - [Makefile Reference](docs/reference/makefile.md)
  - [Environment Variables](docs/reference/environment-variables.md)
  - [Project Stats](docs/reference/project-stats.md)
- **[Explanation](docs/explanation/)** - Design philosophy and concepts
  - [Why Scrabble Scoring?](docs/explanation/why-scrabble-scoring.md)
  - [Architecture Overview](docs/explanation/architecture.md)
  - [NHL API Strategy](docs/explanation/nhl-api-strategy.md)

**Community:**

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [SECURITY.md](SECURITY.md) - Security policy
- [SUPPORT.md](SUPPORT.md) - Getting help
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CLAUDE.md](CLAUDE.md) - Project overview for Claude Code

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick Overview:**

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/amazing-feature`)
1. Make your changes with tests
1. Run quality checks (`make check`)
1. Commit your changes (`git commit -m 'Add amazing feature'`)
1. Push to the branch (`git push origin feature/amazing-feature`)
1. Open a Pull Request

## Security

This project takes security seriously with comprehensive automated scanning:

- **[Dependabot](https://docs.github.com/en/code-security/dependabot)** - Automated dependency updates and security alerts
- **[pip-audit](https://pypi.org/project/pip-audit/)** - CI vulnerability scanning
- **[CodeQL](https://codeql.github.com/)** - Weekly security scans
- **Pre-commit hooks** - 67 comprehensive quality and security checks

**Reporting Vulnerabilities:** See [SECURITY.md](SECURITY.md) for responsible disclosure guidelines. Do **not** report security vulnerabilities through public GitHub issues.

## Support

- **Documentation**: https://bdperkin.github.io/nhl-scrabble/
- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/bdperkin/nhl-scrabble/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/bdperkin/nhl-scrabble/discussions)

See [SUPPORT.md](SUPPORT.md) for detailed support information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

All runtime dependencies use permissive licenses compatible with MIT (Apache, BSD, ISC, etc.). See [LICENSES.md](LICENSES.md) for the complete list.

To verify license compliance:

```bash
tox -e licenses
```

## Project Statistics

- **Test Coverage**: 49.93% overall, >90% on core modules
- **Tests**: 170+ tests (100% passing)
- **Modules**: 15 core modules
- **Makefile Targets**: 57 documented targets
- **Pre-commit Hooks**: 67 comprehensive quality checks
- **CI/CD**: GitHub Actions on Python 3.12, 3.13, 3.14 (required), 3.15-dev (experimental)

See [Project Stats](docs/reference/project-stats.md) for complete metrics.

## Acknowledgments

- NHL API for providing roster data
- Scrabble is a trademark of Hasbro, Inc.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

______________________________________________________________________

Made with ❤️ for hockey and word games
