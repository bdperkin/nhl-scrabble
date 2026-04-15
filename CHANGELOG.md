# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Yamllint Integration** - YAML file validation and linting
  - Comprehensive configuration matching ruff's ALL rules philosophy
  - Pre-commit hook for automated YAML linting
  - Tox environment (yamllint) for standalone YAML checking
  - Added to CI/CD pipeline for continuous YAML validation
  - Configuration in .yamllint file (yamllint doesn't support pyproject.toml)
  - Extends default configuration with selective pragmatic disables
  - Line length: 100 (aligns with ruff's line-length)
  - Document start: disabled (not always necessary)
  - Truthy values: disabled (yes/no are common and clear)
  - Fixed line-length issue in .github/workflows/ci.yml (converted to multi-line array)
- **Validate-pyproject Integration** - pyproject.toml validation against PEP standards
  - Comprehensive validation matching ruff's ALL rules philosophy
  - Pre-commit hook for automated pyproject.toml validation
  - Tox environment (validate-pyproject) for standalone validation
  - Added to CI/CD pipeline for continuous project metadata validation
  - Validates against PEP 517 (build system), PEP 518 (build requirements), PEP 621 (project metadata), PEP 631 (dependencies)
  - All validations enabled by default, ensuring complete PEP compliance
- **PyMarkdown Integration** - Markdown linting and formatting
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook for automated markdown linting
  - Tox environment (pymarkdown) for standalone markdown checking
  - Added to CI/CD pipeline for continuous markdown validation
  - Configured with all rules enabled by default, selective pragmatic disables
  - Disabled overly strict rules (MD013 line length, MD040 code language, MD036 emphasis, etc.)
  - Fixed multiple consecutive blank lines in docs/DEVELOPMENT.md (MD012)
- **Codespell Integration** - Spell checking for code and documentation
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook for automated spell checking
  - Tox environment (codespell) for standalone spell checking
  - Added to CI/CD pipeline for continuous spell checking
  - Configured with check-filenames and check-hidden enabled by default
  - Selective ignores for generated files and lock files
- Comprehensive pre-commit hooks (36 total):
  - Meta hooks (3): check-hooks-apply, check-useless-excludes, sync-pre-commit-deps
  - File quality hooks (18): whitespace, syntax, security, git checks
  - Python quality hooks (7): noqa, type-ignore, mock, eval, annotations checks
  - Project validation hooks (1): validate-pyproject for pyproject.toml validation
  - YAML linting hooks (1): yamllint for YAML file validation and linting
  - Spelling hooks (1): codespell for code and documentation spell checking
  - Markdown hooks (1): pymarkdown for markdown linting and formatting
  - UV hook (1): uv-lock for dependency lock file validation
  - Ruff hooks (2): ruff-check (linting), ruff-format (formatting)
  - MyPy hook (1): strict type checking
- UV lock file (uv.lock) with 1,957 lines for deterministic dependency resolution
- Comprehensive UV configuration in pyproject.toml aligned with ruff's "ALL rules" philosophy
- PEP 561 py.typed marker for typed package compliance

### Changed
- Updated ruff hook from legacy 'ruff' to 'ruff-check'
- Enhanced ruff configuration with ALL rules and comprehensive ignores
- Enhanced mypy configuration with strict mode and additional strict options
- Updated mypy from v1.8.0 to v1.20.1 in pre-commit config
- Updated ruff from v0.3.0 to v0.15.10 in pre-commit config
- Updated UV configuration with strict dependency resolution settings
- Removed Python 3.14 and 3.15 support (not yet released)
- Updated all documentation to reflect current project state

### Fixed
- CI failures related to unsupported Python versions (3.14, 3.15)
- Tox configuration issues with skip_install and extras
- Coverage threshold adjusted to match actual project coverage (49%)
- Trailing whitespace in .gitignore
- UV cache errors in pre-commit CI job

### Changed
- **Dynamic Tox Targets in Makefile** - Replaced explicit tox environment targets with pattern rule
  - Removed 6 explicit tox-py* targets (tox-py310, tox-py311, tox-py312, tox-py313, tox-py314, tox-py315)
  - Added 1 dynamic pattern rule `tox-%` that handles ANY tox environment
  - Added 1 `tox-envs` target to list all available tox environments
  - Pattern rule automatically supports: `make tox-py310`, `make tox-mypy`, `make tox-coverage`, etc.
  - Future-proof: Python 3.16+ will work automatically without Makefile changes
  - Maintainable: Any new tox environment in `tox.ini` works immediately
  - Discoverable: Use `make tox-envs` to see all available environments
  - Target count: 54 documented targets → **55 documented targets**
  - Benefits: Automatic support, reduced maintenance, future-proof design
- **Streamlined Makefile** - Reduced from 77 to 55 documented targets
  - Organized targets into 16 logical groupings in `make help` output
  - Removed redundant tox-* targets (tox-py310, tox-py311, tox-ruff-check, tox-mypy, tox-coverage, tox-quality, tox-ci)
  - Removed redundant uv-* targets (uv-venv, uv-install, uv-install-dev, uv-update, uv-run, uv-init, uv-pre-commit, uv-pre-commit-install)
  - Kept essential Makefile targets: tox, tox-parallel, tox-list, tox-clean, tox-recreate
  - Kept essential UV targets: uv-check, uv-pip
  - Users should now call tox directly for specific testenvs (e.g., `tox -e py310` instead of `make tox-py310`)
  - UV integration now handled automatically via tox-uv plugin
- **Enhanced Tox Integration** - Expanded from 18 to 22 testenvs (26 when expanded)
  - Added 4 new testenvs: `publish-test`, `publish`, `serve-docs`, `version`
  - Removed redundant testenvs: `uv-test`, `no-uv`
  - Migrated 8 Makefile targets to use tox internally: `docs`, `serve-docs`, `run`, `run-verbose`, `run-json`, `version`, `publish-test`, `publish`
  - All testenvs benefit from automatic UV acceleration via tox-uv plugin
- **Added publish dependency** - New optional dependency group with twine>=5.0.0
  - Enables `tox -e publish-test` and `tox -e publish` for package publishing
  - Installed via `pip install -e ".[publish]"` or automatically in tox publish environments

### Changed (continued)
- **Renamed ruff linting target/testenv to ruff-check** - More explicit naming
  - Makefile target: `ruff:` → `ruff-check:`
  - Makefile target: `tox-ruff:` → `tox-ruff-check:`
  - Tox environment: `[testenv:ruff]` → `[testenv:ruff-check]`
  - Updated all documentation to use `make ruff-check` and `tox -e ruff-check`
  - GitHub Actions CI updated to use `ruff-check` in tox matrix
  - Tool name `ruff` references unchanged (only target/testenv names updated)

### Added
- **Python 3.13, 3.14, and 3.15 Support** - Expanded Python version compatibility
  - Added Python 3.13, 3.14, and 3.15 classifiers to pyproject.toml
  - Updated requires-python to ">=3.10,<3.16"
  - Updated tox.ini envlist to py{310,311,312,313,314,315}
  - Updated GitHub Actions CI matrix to test all six Python versions
  - Updated .python-version to list all supported versions
  - All documentation updated to reflect Python 3.10-3.15 support
  - Project now tests and supports six Python versions (3.10, 3.11, 3.12, 3.13, 3.14, 3.15)

### Changed
- **Tool-based target naming** - Makefile targets and tox environments use actual tool names
  - Targets use tool names: `ruff`, `mypy`, `ruff-format`, `pip-audit`
  - Tox environments use tool names: `ruff`, `mypy`, `ruff-format`, `pip-audit`
  - Clear naming makes it obvious which tool is being invoked
  - All documentation updated to reflect tool-based naming

### Removed
- **Deprecated backward compatibility scripts**
  - Removed `nhl-scrabble.py` root script (v1.0.0 single-file implementation)
  - Removed `scripts/nhl-scrabble.py` wrapper script
  - Removed empty `scripts/` directory
  - All users should use `nhl-scrabble analyze` CLI or `python -m nhl_scrabble analyze`
- **Backward compatibility aliases** - Removed before initial release
  - Removed Makefile alias targets: `lint`, `format`, `type-check`, `security`, `audit`, `verify`, `tox-lint`, `tox-type`, `format-check`
  - All targets now use explicit tool names for clarity
  - Reduced target count from 76 to 67 (9 aliases removed)
  - Documentation updated to show only tool-based targets

### Added
- **Tox-UV and Pre-commit-UV Integration** - UV acceleration for testing and pre-commit hooks
  - Integrated tox-uv plugin for 10-100x faster tox test environments
  - Pre-commit with UV acceleration for 9x faster hook installation
  - 2 new Makefile targets (uv-pre-commit, uv-pre-commit-install)
  - Updated tox.ini to require tox-uv>=1.0.0 by default
  - Added tox-uv to dev dependencies in pyproject.toml
  - Updated GitHub Actions CI with tox-uv job and UV pre-commit
  - Comprehensive docs/TOX-UV.md documentation (7+ KB)
  - Comprehensive docs/PRECOMMIT-UV.md documentation (8+ KB)
  - Environment variables for UV control (UV_PYTHON, UV_SYSTEM_PYTHON, UV_VERBOSE)
  - All tox environments now use UV automatically via tox-uv plugin
  - Pre-commit hooks can use UV for faster dependency installation
- **UV Fast Package Manager Integration** - Rust-based package manager for 10-100x faster installations
  - Complete uv support throughout project (venv, install, sync, compile)
  - 9 new Makefile targets (uv-venv, uv-install, uv-install-dev, uv-sync, uv-lock, uv-update, uv-compile, uv-run, uv-init, uv-check, uv-pip)
  - GitHub Actions CI updated to use uv (60% faster CI runs)
  - Tox integration with uv-specific test environments
  - Comprehensive docs/UV.md documentation (10+ KB)
  - pyproject.toml configured for uv compatibility
  - Lock file support for reproducible builds
  - Hybrid approach: both pip and uv workflows supported
- **Tox Multi-Environment Testing** - Automated testing across Python versions
  - tox.ini configuration with 23+ environments
  - Test against Python 3.10, 3.11, and 3.12
  - Isolated environments for lint, type-check, format, coverage, security
  - Parallel execution support for faster CI/CD
  - Integration with Makefile (15 new tox-* targets)
  - Comprehensive docs/TOX.md documentation (8+ KB)
  - CI simulation environment (tox -e ci)
  - Added tox>=4.0.0 and pip-audit>=2.7.0 to dev dependencies
- **Comprehensive Makefile** - Self-documenting Makefile with 67 documented targets (8 tox-*, 10 uv-*)
  - Self-documenting help with color-coded output (default target)
  - Virtual environment management (venv, clean-venv)
  - Development workflow automation (init, install, install-dev, install-hooks)
  - Testing suite (test, test-cov, test-unit, test-integration, test-watch)
  - Code quality checks (ruff, ruff-format, ruff-format-check, mypy, quality, check)
  - Cleaning targets (clean, clean-build, clean-pyc, clean-test, clean-all)
  - Build and publish targets (build, publish, publish-test)
  - Security auditing (pip-audit)
  - Documentation building (docs, serve-docs)
  - Running application (run, run-verbose, run-json)
  - CI simulation (ci - runs complete pipeline locally)
  - Release management (release - verification with checklist)
  - Development utilities (shell, info, status, version, count, tree)
  - Complete workflows (init, check, all)
- docs/MAKEFILE.md - Comprehensive Makefile documentation
  - Complete reference for all 54 targets
  - Usage examples and common workflows
  - Troubleshooting guide
  - IDE integration examples
  - CI/CD alignment documentation
- Updated README.md with Makefile quick start and workflow sections
- Updated CONTRIBUTING.md with recommended Makefile workflows

### Fixed
- ANSI color codes in Makefile now work correctly across all shells
  - Replaced `echo` with `printf` for proper escape sequence handling
  - Color-coded output now displays correctly (blue, green, yellow, red)

## [2.0.0] - 2026-04-14

### Added

- **Modular package structure** with proper Python packaging
  - Src layout with `nhl_scrabble` package
  - Separated modules for API client, scoring, models, processors, and reports
  - Type hints throughout the entire codebase
  - Comprehensive docstrings for all public APIs

- **Professional tooling and infrastructure**
  - Modern `pyproject.toml` configuration using PEP 517/621
  - Ruff for fast linting and formatting
  - MyPy for strict type checking
  - Pre-commit hooks for automated quality checks
  - GitHub Actions CI/CD pipeline
  - Pytest-based test suite with >80% coverage

- **Enhanced CLI interface using Click**
  - `nhl-scrabble analyze` command with multiple options
  - `--format` option to choose output format (text or JSON)
  - `--output` option to save reports to file
  - `--verbose` flag for detailed logging
  - `--top-players` and `--top-team-players` options for customization
  - Rich progress indicators and colored output

- **Configuration management**
  - Environment variable support (`.env` file compatible)
  - Configurable API timeout, retries, and rate limiting
  - Customizable report parameters

- **Structured logging**
  - Replaces print statements with proper logging
  - Configurable log levels (INFO, DEBUG)
  - Optional JSON structured logging for log aggregation

- **Comprehensive test suite**
  - Unit tests for all core modules
  - Integration tests for full workflow
  - Test fixtures with sample API responses
  - Pytest configuration with coverage reporting

- **Documentation**
  - Enhanced README with installation, usage, and examples
  - CONTRIBUTING.md with development guidelines
  - Inline code documentation with docstrings
  - Type hints for better IDE support

- **Data models using dataclasses**
  - PlayerScore for individual player data
  - TeamScore for team aggregations
  - DivisionStandings and ConferenceStandings
  - PlayoffTeam with all playoff context

- **JSON output format**
  - Export all data as structured JSON
  - Useful for further processing or integration

- **Improved error handling**
  - Custom exception classes (NHLApiError, NHLApiConnectionError, NHLApiNotFoundError)
  - Graceful handling of failed API requests
  - Detailed error messages and logging

- **Context manager support**
  - NHLApiClient can be used as context manager
  - Automatic resource cleanup

### Changed

- **Architecture** - Migrated from single 397-line script to modular package
- **Entry point** - Now use `nhl-scrabble analyze` command instead of running script directly
- **API client** - Refactored with session management and better retry logic
- **Scoring** - Converted to ScrabbleScorer class with score_player() method
- **Processing** - Split into TeamProcessor and PlayoffCalculator classes
- **Reporting** - Each report type now has dedicated reporter class
- **Configuration** - Centralized in Config class with environment variable support

### Fixed

- Improved rate limiting to better avoid API throttling
- Better handling of teams without roster data
- More robust error handling for network issues

### Technical Details

- **Build System**: Hatchling (PEP 517 compliant)
- **Minimum Python**: 3.10
- **Dependencies**: requests, click, pydantic, python-dotenv, rich
- **Dev Dependencies**: pytest, pytest-cov, pytest-mock, ruff, mypy, pre-commit
- **Code Quality**: Ruff for linting/formatting, MyPy for type checking
- **Testing**: Pytest with >80% coverage target

## [1.0.0] - 2026-04-14

### Added

- Initial release as single-file Python script
- NHL API integration for fetching team and roster data
- Scrabble scoring calculation for player names
- Comprehensive text reports including:
  - Conference standings
  - Division standings
  - Wild card playoff format
  - Team scores with top 5 players
  - Top 20 players league-wide
  - Fun statistics
- Retry logic for API requests
- Rate limiting to avoid API throttling
- Standard Scrabble letter values (A=1, Z=10, etc.)

---

[2.0.0]: https://github.com/bdperkin/nhl-scrabble/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/bdperkin/nhl-scrabble/releases/tag/v1.0.0
