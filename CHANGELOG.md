# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2026-04-26

### Fixed

- **Output Format Validation** - Fixed CLI-Config mismatch for output formats (#366)
  - Config now accepts all 10 CLI-advertised formats: text, json, yaml, xml, html, table, markdown, csv, excel, template
  - Previously, formats like markdown, yaml, xml, table, and template were accepted by CLI but rejected by Config
  - Users no longer get confusing pydantic ValidationError when using valid CLI format options
  - Added comprehensive unit and integration tests to prevent future CLI-Config inconsistencies
- **Logging Verbosity** - Reduced excessive INFO logging during analysis
  - Suppressed verbose dicttoxml INFO logging when using XML output format
  - Changed "Active filters" message from INFO to DEBUG (already shown in console output)
  - Users now see clean, concise output without internal library debug messages

## [0.0.1] - 2026-04-20

### Added

Initial pre-release version with core NHL Scrabble functionality.

#### Core Features

- **NHL Roster Data Fetching** - Live data from NHL API

  - Fetch current rosters from NHL API
  - Support for all 32 NHL teams
  - Retry logic with exponential backoff
  - Rate limiting and error handling
  - Session management with proper cleanup

- **Scrabble Scoring Engine** - Calculate Scrabble scores for player names

  - Standard Scrabble letter values (A=1, Z=10, etc.)
  - Full name scoring (first + last)
  - Team, division, and conference aggregation
  - Playoff bracket generation

- **Multiple Output Formats** - Comprehensive reporting options

  - Text (human-readable tables)
  - JSON (structured data)
  - HTML (web pages)
  - CSV (spreadsheet import)
  - Excel (multi-sheet workbooks with formatting)
  - Markdown (documentation)
  - YAML (configuration)
  - XML (data interchange)

- **Web Interface** - FastAPI-powered web server

  - REST API endpoints
  - Web UI with interactive visualizations
  - Auto-generated OpenAPI documentation
  - Real-time data updates

- **Interactive Mode** - REPL for exploration

  - Team search and comparison
  - Player search
  - Live data refresh
  - Multiple output formats

- **Comprehensive CLI** - Rich command-line interface

  - `analyze` - Generate NHL Scrabble reports
  - `search` - Search for players/teams
  - `interactive` - Launch interactive REPL
  - `web` - Start web server
  - Short option aliases (-v, -f, -o)
  - Colorized log output
  - Progress indicators

#### Data Features

- **Unicode Normalization** - Support for international player names

  - Automatic normalization of diacritics and accents
  - NFD decomposition + diacritic removal (é → e, ř → r)
  - Transliteration of non-Latin scripts
  - Supports Czech, French-Canadian, Scandinavian players

- **Caching System** - High-performance API response caching

  - SQLite-based persistent cache (`.nhl_cache.sqlite`)
  - Configurable cache location and TTL
  - Platform-specific cache directories
  - Cache statistics and info
  - `--no-cache` option for fresh data

- **Historical Data Support** - Query past NHL seasons

  - Season parameter support
  - Historical roster data
  - Time-series analysis

#### Architecture & Quality

- **Modern Python Package** - Professional package structure

  - Python 3.12+ support (3.12, 3.13, 3.14)
  - Python 3.15-dev experimental support
  - Type hints throughout (mypy strict mode)
  - Pydantic models for data validation
  - Protocol-based dependency injection
  - Comprehensive error handling

- **Testing & Quality** - Extensive test coverage

  - 170+ tests with >93% coverage on core modules
  - Unit and integration tests
  - Pytest with xdist (parallel execution)
  - Coverage tracking (Codecov integration)
  - Diff-cover for PR validation (≥80% on new code)
  - Flaky test retry mechanisms

- **Development Tools** - Modern development workflow

  - UV package manager (10-100x faster than pip)
  - Dynamic versioning from git tags (hatch-vcs)
  - Tox for testing (multiple Python versions)
  - Pre-commit hooks (67 comprehensive checks)
  - GitHub Actions CI/CD
  - Comprehensive Makefile (57 targets)

- **Code Quality Tools** - Automated quality enforcement

  - Ruff (linting and formatting)
  - MyPy (strict type checking)
  - ty (Astral's fast type checker, validation mode)
  - refurb (code modernization)
  - interrogate (docstring coverage - 100% required)
  - bandit (security linting)
  - safety (dependency vulnerability scanning)

- **Documentation** - Comprehensive documentation system

  - Sphinx documentation with GitHub Pages
  - Diátaxis framework (tutorials, how-to, reference, explanation)
  - Multiple output formats (HTML, PDF, man pages, Texinfo)
  - Auto-generated API and CLI docs
  - Hyperlinked external resources
  - Doctest integration
  - Link validation

#### Security

- **Dependency Security** - Automated vulnerability management

  - Dependabot alerts and updates
  - pip-audit vulnerability scanning
  - CodeQL security scanning
  - Secret scanning
  - SECURITY.md policy

- **Input Validation** - Comprehensive security checks

  - CLI argument validation
  - API response validation
  - Player name sanitization
  - Path traversal protection
  - SSRF protection
  - DoS prevention mechanisms

- **Secure Coding** - Security best practices

  - SSL/TLS certificate verification
  - PII logging prevention
  - Config injection protection
  - Log sanitization for secrets

#### Configuration

- **Flexible Configuration** - Multiple configuration sources

  - Environment variables (`NHL_SCRABBLE_*`)
  - `.env` file support
  - CLI arguments
  - Sensible defaults
  - Configuration validation

- **Platform Support** - Cross-platform compatibility

  - Linux (primary)
  - macOS (supported)
  - Windows (supported)
  - Platform-specific cache directories
  - Permission checking

### Changed

- Removed deprecated CSVExporter in favor of CSVFormatter via formatters pattern
- Consolidated exporters and formatters architecture for consistency

### Dependencies

#### Core

- requests>=2.33.1 (HTTP client)
- requests-cache>=1.3.1 (API caching)
- pydantic>=2.7.3 (data validation)
- pydantic-settings>=2.7.3 (settings management)
- click (CLI framework)
- rich>=15.0.0 (terminal formatting)

#### Optional

- fastapi (web server)
- uvicorn[standard]>=0.27.0 (ASGI server)
- openpyxl (Excel export)
- prompt-toolkit>=3.0.52 (interactive mode)
- unidecode>=1.3.0 (Unicode normalization)

#### Development

- pytest (testing framework)
- pytest-cov (coverage)
- pytest-xdist (parallel testing)
- pytest-timeout (timeout protection)
- pytest-randomly (randomized execution)
- pytest-flakefinder (flaky test detection)
- mypy (type checking)
- ty (fast type checking)
- ruff (linting and formatting)
- refurb (code modernization)
- pre-commit (hooks)
- tox (multi-environment testing)
- tox-uv (UV integration)

### Technical Notes

- **Package Version**: Dynamically determined from git tags via hatch-vcs
- **Minimum Python**: 3.12
- **License**: MIT
- **Repository**: https://github.com/bdperkin/nhl-scrabble

### Known Issues

- CVE-2026-3219 (pip vulnerability) - Monitoring for patch availability (Issue #375)

[0.0.1]: https://github.com/bdperkin/nhl-scrabble/releases/tag/v0.0.1
[0.0.2]: https://github.com/bdperkin/nhl-scrabble/releases/tag/v0.0.2
[unreleased]: https://github.com/bdperkin/nhl-scrabble/compare/v0.0.2...HEAD
