# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **QA Automation Framework** (#311) - **COMPLETED**

  - Comprehensive end-to-end testing infrastructure for web interface
  - **Framework**: Playwright with Page Object Model architecture
  - **40+ comprehensive tests** across 4 test categories
  - **Infrastructure Setup** (#312, #313)
    - `qa/` directory structure with modular organization
    - Playwright framework configuration
    - Page Object Model for all web pages
    - Reusable fixtures and test utilities
  - **Functional Testing** (#316)
    - 15 tests covering user workflows, navigation, interactions
    - Form submission validation and error handling tests
    - Data display verification across all pages
  - **Visual Regression Testing** (#317)
    - 10 snapshot comparison tests using pytest-playwright-snapshot
    - Cross-browser visual consistency validation
    - Automated baseline generation and diff reporting
  - **Performance Testing** (#314)
    - 8 tests for page load times and API response benchmarks
    - Locust load testing for concurrent user simulation
    - Performance threshold validation
  - **Accessibility Testing** (#318)
    - 7 tests for WCAG 2.1 AA compliance using axe-playwright
    - Keyboard navigation validation
    - Screen reader compatibility checks
  - **CI/CD Integration** (#315, #436)
    - Cross-browser testing matrix: Chromium, Firefox, WebKit
    - Parallel test execution (~5-7 minutes total)
    - Nightly scheduled runs at 2 AM UTC
    - Manual workflow dispatch with test suite and browser selection
    - Artifact management: test reports (XML/HTML/JSON), screenshots, visual diffs, performance metrics
    - PR commenting with test summary and failure details
    - GitHub Actions job summary for quick test result overview
    - Automated server startup/shutdown with health checks
    - Workflow file: `.github/workflows/qa-automation.yml`
  - **Documentation**: Comprehensive guides in `qa/README.md` and `qa/web/README.md`
  - **Makefile Integration**: 8 QA targets (qa-install, qa-test, qa-functional, qa-visual, qa-performance, qa-accessibility, etc.)

## [0.0.5] - 2026-04-27

### Added

- **Automated PyPI Publishing Workflow** (#405)

  - Implemented GitHub Actions workflow for automated package publishing on version tags
  - 5-stage automated pipeline: Build → Test → TestPyPI → PyPI → GitHub Release
  - Multi-platform testing: 3 operating systems × 3 Python versions (Ubuntu, macOS, Windows on Python 3.12-3.14)
  - OIDC-based trusted publishing (no API tokens required)
  - Automated GitHub Release creation with distribution artifacts
  - Release notes auto-extracted from CHANGELOG.md
  - Workflow file: `.github/workflows/publish.yml`

- **Comprehensive Release Documentation** (#405)

  - Created `docs/RELEASING.md` (785 lines) - Complete release workflow guide
  - Version tagging strategy and semantic versioning guidelines
  - CHANGELOG.md format guidelines (Keep a Changelog)
  - PyPI Trusted Publishing setup instructions
  - Troubleshooting guide with common failure patterns and solutions
  - Rollback strategies for failed releases
  - Manual release fallback process
  - Best practices and release timing recommendations
  - Performance metrics and time savings documentation

### Changed

- **PyPI Package Metadata** (#407)

  - Homepage URL now points to documentation site (https://bdperkin.github.io/nhl-scrabble/)
  - Added explicit Documentation link to PyPI project links
  - Added Changelog link for easy access to release history
  - Improved user experience for PyPI package discovery

- **Release Process Improvements**

  - Release time reduced from 30 minutes (manual) to ~5 minutes (automated)
  - Time savings: 6x faster release process
  - Automated verification: builds, tests, and publishes with zero manual steps
  - Consistent builds across all releases
  - Eliminated manual errors in release process

### Fixed

- **PyPI Package Page** (#406)

  - Fixed broken logo image (changed from relative to absolute GitHub URL)
  - Fixed broken interrogate badge (changed from relative to absolute GitHub URL)
  - Images now display correctly on https://pypi.org/project/nhl-scrabble/

### Security

- **OIDC Trusted Publishing** (#405)
  - Replaced API token-based authentication with OIDC (OpenID Connect)
  - Short-lived credentials that expire in minutes
  - Automatic credential rotation
  - Credentials bound to specific repository, workflow, and environment
  - Eliminated security risks from long-lived API tokens

### Documentation

- **Release Process**
  - CONTRIBUTING.md: Updated with automated release workflow
  - CLAUDE.md: Added "Automated Package Publishing" section with workflow details
  - README.md: Added PyPI version and downloads badges
  - Complete documentation ensures smooth releases for all contributors

## [0.0.4] - 2026-04-27

### Added

- **Documentation Refactoring** (#400)

  - Created 8 detailed contributing guides in `docs/contributing/`
  - New guides: code-style.md, commit-messages.md, dependency-updates.md, logging-guidelines.md, pre-commit-hooks.md, pull-requests.md, release-process.md, testing-guidelines.md
  - Created comprehensive how-scrabble-scoring-works.md (483 lines) with technical implementation details
  - Created using-the-cli.md tutorial (369 lines) for complete CLI usage
  - Created run-benchmarks.md how-to guide (134 lines) for performance testing
  - Created project-stats.md reference (412 lines) with comprehensive project metrics
  - Moved manual-testing-checklist.md to `docs/testing/` for better organization

- **License Management Automation** (#400)

  - Automated license tracking with `scripts/update_licenses.py` (408 lines)
  - Automatic license generation using pip-licenses
  - Deduplication logic for clean license reports
  - Prohibited license validation for runtime dependencies
  - Makefile targets: `licenses-check`, `licenses-update`, `licenses-validate`
  - Tox environments for CI integration
  - LICENSES.md automatically maintained

### Changed

- **Documentation Structure** (#400)

  - Refactored README.md from ~1,200 to ~400 lines with no content loss
  - Refactored CONTRIBUTING.md from ~2,500 to ~300 lines with links to detailed guides
  - Consolidated duplicate documentation across files
  - Added authoritative Scrabble references (Wikipedia links)
  - Improved documentation discoverability following Diátaxis framework

- **Task Documentation Synchronization**

  - Synchronized task counts across all tracking systems
  - Updated tasks/README.md with accurate counts (57 active, 135 completed)
  - Regenerated tasks/IMPLEMENTATION_SEQUENCE.md with optimal task ordering
  - Simplified implementation sequence (reduced from 637 to 119 lines)
  - Removed 889 lines of outdated documentation
  - Moved completed task 037 from active to completed directory
  - Improved completion rate: 69.8% → 70.3%

### Fixed

- **Web Interface Improvements** (#400)

  - Fixed favicon 404 errors (added PNG and SVG favicons)
  - Fixed robots.txt 404 errors
  - Fixed CSP blocking Swagger UI/ReDoc (exempted API documentation endpoints)
  - Fixed invisible analysis results (scroll animation re-initialization)
  - Fixed blank team names in Division Standings (added team name field to data pipeline)
  - Improved stats card layout with two-line display (score + context)
  - Added Documentation and ReDoc links to navigation

- **Security**

  - Dismissed 3 CodeQL false positives (Protocol method docstrings in interfaces.py)
  - All security scans now clean with no open alerts

### Dependencies

- **GitHub Actions Updates**
  - Bumped actions/upload-artifact from 5 to 7 (#403)
  - Bumped actions/github-script from 7 to 9 (#402)
  - Bumped actions/stale from 9 to 10 (#401)
  - All CI workflows now use latest action versions

### Documentation

- Total new documentation: ~2,500 lines across 12 new files
- Total documentation removed: ~3,000 lines of duplicates (consolidated)
- Net improvement in documentation quality and organization
- All documentation follows Diátaxis framework (Tutorials, How-to, Reference, Explanation)

## [0.0.3] - 2026-04-27

### Added

- **First-Time Contributor Welcome Workflow** (#397)

  - Automated welcome messages for first-time PR contributors
  - Automated welcome messages for first-time issue reporters
  - Friendly onboarding with links to CONTRIBUTING.md and documentation
  - Clear next steps for contribution process
  - Only triggers once per contributor (no duplicate messages)
  - Safe implementation using `pull_request_target` for fork permissions

- **Automated Stale Issue/PR Management** (#395)

  - Daily workflow to mark inactive issues (60 days) and PRs (30 days) as stale
  - Auto-closes stale items after 7-day warning period
  - Exempt labels: `keep-open`, `pinned`, `security`, `good-first-issue`, `help-wanted`, `enhancement`, `bug`, `work-in-progress`, `wip`
  - Manual trigger available via workflow_dispatch
  - Keeps issue tracker clean and relevant

- **Automated Documentation Link Validation** (#394)

  - Weekly scheduled link checking in all Markdown documentation
  - PR-triggered link validation for changed documentation
  - Automatic issue creation for broken links (scheduled runs)
  - PR comments for broken links in pull requests
  - Soft-fail for flaky external links (e.g., sphinx-build)
  - Prevents documentation rot

- **Pre-commit.ci GitHub Automation** (#393)

  - Automated pre-commit hook updates via pre-commit.ci bot
  - Weekly autoupdate checks for all 67+ hooks
  - Auto-fix and commit for fixable issues
  - PR creation for hook updates
  - Reduces manual maintenance overhead

### Fixed

- **Pre-commit.ci Compatibility** - Fixed multiple hook compatibility issues for CI environment
  - Skip `safety` hook in pre-commit.ci (requires authentication)
  - Skip `mdformat` in pre-commit.ci (platform-specific issues)
  - Skip JSON schema validation hooks in CI (network dependency)
  - Skip `check-wheel-contents` in pre-commit.ci (build environment required)
  - Skip `pyroma` in pre-commit.ci (package metadata access issues)
  - Force Python 3.12 for `unimport` hook (version compatibility)
  - All hooks now work correctly in both local and CI environments

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
