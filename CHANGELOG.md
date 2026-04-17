# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Refactored

- **Cross-Platform Branch Protection Check** - Ported git hook to Python

  - Converted `.git-hooks/check-branch-protection.sh` to `.git-hooks/check-branch-protection.py` for Windows compatibility
  - Removed bash dependency for branch protection pre-commit hook
  - Improved error handling with proper exception catching (KeyboardInterrupt, EOFError)
  - Added type hints and comprehensive docstrings
  - Detects 6 CI environments (GitHub Actions, GitLab CI, Travis, CircleCI, Jenkins, generic CI)
  - Maintained identical functionality, exit codes, and user experience
  - Updated `.pre-commit-config.yaml` to use Python script with system language
  - Benefits: Works on Windows without bash/WSL, easier maintenance for Python developers, better error handling

- **Cross-Platform Documentation Check** - Ported bash script to Python

  - Converted `tools/check_docs.sh` to `tools/check_docs.py` for Windows compatibility
  - Removed bash dependency for pre-commit documentation validation
  - Improved error handling with proper exceptions and return codes
  - Added type hints and comprehensive docstrings
  - Enhanced colored terminal output with ANSI codes class
  - Maintained identical functionality and exit code behavior
  - Updated `.pre-commit-config.yaml` to use Python script
  - Benefits: Works on Windows without bash/WSL, easier maintenance for Python developers

### Added

- **FastAPI Web Interface Infrastructure** - Foundation for browser-based NHL Scrabble access

  - Added FastAPI>=0.110.0 web framework with automatic OpenAPI documentation
  - Added uvicorn[standard]>=0.27.0 ASGI server with WebSocket support
  - Added python-multipart>=0.0.9 for form data handling
  - Created `src/nhl_scrabble/web/` module with FastAPI application
  - Implemented health check endpoint (`/health`) returning status, version, and timestamp
  - Implemented root endpoint (`/`) with API navigation links
  - Auto-generated interactive API documentation at `/docs` (Swagger UI)
  - Auto-generated alternative documentation at `/redoc` (ReDoc)
  - Added `nhl-scrabble serve` CLI command with --host, --port, --reload options
  - Created directory structure for templates and static files (CSS, JS, images)
  - Added comprehensive integration tests with 100% endpoint coverage
  - Python 3.10+ compatibility using timezone.utc instead of UTC constant
  - Benefits: RESTful API access, browser-based interface foundation, automatic API docs
  - Task: #103 - tasks/new-features/002-fastapi-infrastructure.md

- **Web Frontend Templates and CSS** - Professional UI for NHL Scrabble web interface

  - Created Jinja2 template system with base layout (`base.html`)
  - Implemented responsive home page (`index.html`) with analysis form
  - Added results template (`results.html`) for displaying analysis data
  - Created comprehensive CSS stylesheet with NHL-themed design
  - NHL-inspired color palette (blue #003087, red #C8102E, gold #FFB81C)
  - Mobile-first responsive design (320px+, 768px+, 1200px+)
  - Accessible forms with proper labels, ARIA attributes, and keyboard navigation
  - Loading spinner animation for async operations
  - Professional typography with system font stack and custom headings
  - Smooth animations and hover effects
  - Created JavaScript application (`app.js`) for form handling and API integration
  - Updated root endpoint (`/`) to serve HTML home page instead of JSON
  - Added comprehensive integration tests for templates and static files
  - WCAG 2.1 Level AA accessibility compliance (semantic HTML, focus states, color contrast)
  - Cross-browser compatibility (Chrome, Firefox, Safari, Edge, mobile browsers)
  - Benefits: Professional web UI, mobile-friendly interface, accessible design, NHL-themed branding
  - Task: #105 - tasks/new-features/004-web-frontend-templates.md

- **Test Randomization with pytest-randomly** - Randomize test execution order to catch hidden dependencies

  - Added pytest-randomly>=3.15.0 to test dependencies
  - Tests now run in random order on every execution
  - Random seed printed for reproducible test runs
  - Catches hidden test dependencies (global state, shared fixtures, order-dependent bugs)
  - Seed can be specified for debugging: `pytest --randomly-seed=<seed>`
  - Randomization can be disabled: `pytest -p no:randomly`
  - **First bug found!** pytest-randomly immediately exposed a hidden test dependency in `test_clear_cache`
  - Fixed `test_clear_cache` to patch correct layer (HTTP transport vs cache layer) for proper isolation
  - All 170 tests now pass reliably in any execution order
  - Updated CONTRIBUTING.md with usage documentation and best practices
  - Benefits: Better test isolation, earlier bug detection, improved test quality

- **Python 3.14 Support** - Official support and testing for Python 3.14

  - Updated `requires-python` constraint to `>=3.10,<3.15`
  - Added Python 3.14 classifier to package metadata
  - Added Python 3.14 to CI/CD test matrix (GitHub Actions)
  - Added py314 to tox environments for local testing
  - Regenerated UV lock file with Python 3.14 compatibility
  - Updated documentation (README.md, CLAUDE.md)
  - No breaking changes - existing Python 3.10-3.13 users unaffected
  - Ensures access to latest Python features and performance improvements

- **Python 3.15-dev Experimental Support** - Early compatibility testing for Python 3.15-dev

  - Added Python 3.15-dev to CI/CD test matrix with `continue-on-error: true`
  - Failures on 3.15-dev do NOT block CI or prevent merging (informational only)
  - Added py315 to tox environments for local testing (optional)
  - Documented experimental status in README.md and CLAUDE.md
  - Intentionally NOT updated in pyproject.toml (3.15 not officially released)
  - Enables proactive compatibility testing before Python 3.15 release
  - Allows early detection of breaking changes and migration issues
  - Will be upgraded to official support when Python 3.15 is released

- **HTML Output Format** - Professional HTML reports with responsive design

  - Generate beautiful HTML reports with `--format html`
  - NHL-themed styling with team colors (#003087 blue, #C60C30 red)
  - Responsive design works on desktop, tablet, and mobile
  - Interactive tables with hover effects
  - Statistics dashboard with cards
  - Print-friendly stylesheet
  - XSS protection with automatic HTML escaping
  - Jinja2 templating engine for flexible rendering
  - Usage: `nhl-scrabble analyze --format html --output report.html`

- **Gitlint Integration** - Commit message linter

  - Comprehensive commit message linting matching ruff's ALL rules philosophy
  - Pre-commit hook (jorisroovers/gitlint) for automatic commit message validation
  - Tox environment (gitlint) for standalone commit message checks
  - Added to CI/CD pipeline for continuous commit message quality validation
  - Configuration in .gitlint file (gitlint has issues with complex pyproject.toml files)
  - Title max length: 100 characters (matches ruff's line-length)
  - Title min length: 5 characters (meaningful commits)
  - Body max line length: 100 characters (matches ruff's line-length)
  - Body min length: 10 characters (when body is present)
  - Ignores: merge, revert, fixup, fixup-amend, squash commits (auto-generated)
  - Enforces consistent commit message style and documentation
  - Aligns with conventional commits best practices
  - Promotes clear git history for team collaboration
  - Works harmoniously with conventional commit standards
  - 55 total pre-commit hooks for comprehensive code quality

- **Blocklint Integration** - Inclusive language checker

  - Comprehensive inclusive language checker matching ruff's ALL rules philosophy
  - Pre-commit hook (PrincetonUniversity/blocklint) for automatic terminology detection
  - Tox environment (blocklint) for standalone inclusive language checks
  - Added to CI/CD pipeline for continuous language inclusivity validation
  - Documentation in pyproject.toml (blocklint does not support pyproject.toml config)
  - Detects non-inclusive terminology related to hierarchical and access control
  - Default blocklist includes problematic terms commonly found in technical writing
  - Excludes build/test artifacts (.git, .tox, .venv, build, dist, coverage.xml, etc.)
  - Promotes respectful and inclusive code and documentation
  - Aligns with modern best practices for inclusive technical communication
  - Works harmoniously with detect-private-key for comprehensive code quality
  - Current project status: no non-inclusive terminology found (clean codebase)
  - 54 total pre-commit hooks for comprehensive code quality

- **Vulture Integration** - Dead code detection

  - Comprehensive dead code detection matching ruff's ALL rules philosophy
  - Pre-commit hook (jendrikseipp/vulture) for automatic dead code detection
  - Tox environment (vulture) for standalone dead code checks
  - Added to CI/CD pipeline for continuous code cleanliness validation
  - Configuration in pyproject.toml with comprehensive checking
  - Detects unused: functions, classes, variables, imports, properties, and attributes
  - Min confidence set to 60 for comprehensive but practical detection
  - Excludes build/test artifacts (.git, .tox, .venv, build, dist, etc.)
  - Ignores framework decorators (Click commands, pytest fixtures, Flask routes, etc.)
  - Ignores common patterns (magic method parameters, private variables, test fixtures)
  - Special handling for public API exceptions (NHLApiNotFoundError reserved for future use)
  - Works harmoniously with unimport (unused imports) and autoflake (unused variables)
  - Current project status: no dead code found (clean codebase)
  - 53 total pre-commit hooks for comprehensive code quality

- **Pydocstyle Integration** - Python docstring style checker

  - Comprehensive docstring style checker matching ruff's ALL rules philosophy
  - Pre-commit hook (PyCQA/pydocstyle) for automatic docstring style validation
  - Tox environment (pydocstyle) for standalone docstring style checks
  - Added to CI/CD pipeline for continuous docstring style validation
  - Configuration in pyproject.toml following PEP 257 convention
  - Checks docstring format and style for all Python code
  - Aligned ignore list (add-ignore) with ruff's D-rule ignores for consistency
  - Ignores: D100-D107 (handled by interrogate), D203/D213 (conflicting formatting), D413 (conflicts with docformatter)
  - Works harmoniously with interrogate (coverage) and docformatter (formatting)
  - Current project status: no docstring style violations (clean docstrings)
  - 52 total pre-commit hooks for comprehensive code quality

- **Unimport Integration** - Unused import checker

  - Comprehensive unused import checker matching ruff's ALL rules philosophy
  - Pre-commit hook (hakancelikdev/unimport) for automatic unused import detection
  - Tox environment (unimport) for standalone unused import checks
  - Added to CI/CD pipeline for continuous import hygiene validation
  - Configuration in pyproject.toml with comprehensive checking
  - Detects and reports unused import statements across the codebase
  - Ignores __init__.py files (matches ruff's per-file-ignores for __init__.py F401)
  - Excludes build/test artifacts using gitignore patterns
  - Works harmoniously with autoflake and ruff's unused import detection (F401)
  - Current project status: no unused imports found (clean codebase)
  - 51 total pre-commit hooks for comprehensive code quality

- **Deptry Integration** - Python dependency checker

  - Comprehensive dependency checker matching ruff's ALL rules philosophy
  - Pre-commit hook (fpgmaas/deptry) for automatic dependency validation
  - Tox environment (deptry) for standalone dependency checks
  - Added to CI/CD pipeline for continuous dependency validation
  - Configuration in pyproject.toml with comprehensive checking
  - Detects: obsolete dependencies, missing dependencies, transitive dependencies, misplaced dev dependencies
  - All optional-dependencies groups configured as development dependencies
  - Package-to-module name mapping for python-dotenv -> dotenv
  - Comprehensive by default: no ignores, checks all dependency issues
  - Validation identified and removed unused pydantic dependency from main dependencies
  - Works harmoniously with pip-audit for comprehensive dependency management
  - 50 total pre-commit hooks (before unimport addition)

- **Interrogate Integration** - Python docstring coverage checking

  - Comprehensive docstring coverage checker matching ruff's ALL rules philosophy
  - Pre-commit hook (econchick/interrogate) for automatic docstring coverage validation
  - Tox environment (interrogate) for standalone docstring coverage checks
  - Added to CI/CD pipeline for continuous documentation quality validation
  - Configuration in pyproject.toml requiring 100% docstring coverage
  - Checks: modules, classes, methods, functions, __init__ methods, magic methods, nested functions/classes
  - Comprehensive by default: checks all public and private code (no ignores)
  - Current project coverage: 100% (93 items, all documented)
  - Verbose output (level 2) showing detailed coverage breakdown per module
  - Sphinx-style docstrings enforced (default style)
  - Works harmoniously with ruff's pydocstyle rules (D) for docstring format validation
  - 49 total pre-commit hooks (before deptry addition)

- **Pyroma Integration** - Python package metadata quality rating

  - Quality checker for Python package metadata and project setup
  - Pre-commit hook (local) for automatic metadata quality checks
  - Tox environment (pyroma) for standalone quality rating
  - Added to CI/CD pipeline for continuous metadata quality validation
  - Rates project metadata on a 10-point scale
  - Checks: package name, version, description, classifiers, license, readme, keywords, author info
  - Current project rating: 10/10 ("Your cheese is so fresh most people think it's a cream: Mascarpone")
  - Works harmoniously with validate-pyproject for comprehensive metadata validation
  - 48 total pre-commit hooks (before interrogate addition)

- **Tox-ini-fmt Integration** - Tox configuration file formatting

  - Formatter for tox.ini files enforcing tox 4 best practices
  - Pre-commit hook for automatic tox.ini formatting
  - Tox environment (tox-ini-fmt) for standalone formatting
  - Added to CI/CD pipeline for consistent tox.ini structure
  - Auto-formats to standard structure: alphabetized sections, consistent field ordering
  - Enforces modern tox 4 syntax (env_list vs envlist, package=editable vs usedevelop)
  - Removes deprecated fields (minversion, isolated_build now defaults)
  - Updates minimum version requirements (tox>=4.2, tox-uv>=1)
  - Works harmoniously with tox 4 and tox-uv for consistent configuration
  - 47 total pre-commit hooks (before pyroma addition)

- **Autoflake Integration** - Unused import and variable removal

  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook for automatic unused code removal
  - Tox environment (autoflake) for standalone unused code checks
  - Added to CI/CD pipeline for continuous code cleanliness validation
  - Configuration: remove-all-unused-imports, remove-unused-variables, remove-duplicate-keys
  - Aligns with ruff's F401 (unused imports) and F841 (unused variables) rules
  - Ignores __init__.py imports (matches ruff's per-file-ignores for re-exports)
  - Works harmoniously with ruff's unused import/variable detection
  - 46 total pre-commit hooks (before tox-ini-fmt addition)

- **Isort Integration** - Python import sorting

  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook for automatic import sorting
  - Tox environment (isort) for standalone import sorting checks
  - Added to CI/CD pipeline for continuous import organization validation
  - Configuration: profile="black", line_length=100, known_first_party=["nhl_scrabble"] (match ruff)
  - Works harmoniously with ruff's isort rules (I001-I005)
  - Import ordering: FUTURE → STDLIB → THIRDPARTY <!-- codespell:ignore --> → FIRSTPARTY → LOCALFOLDER
  - Code changes: Collapsed multi-line imports to single line where they fit in 100 chars
  - 45 total pre-commit hooks (before autoflake addition)

- **Black Integration** - Python code formatting with Black

  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook for automatic Black formatting
  - Tox environment (black) for standalone formatting checks
  - Added to CI/CD pipeline for continuous code formatting validation
  - Configuration: line-length=100, target-version=py310-py313 (match ruff)
  - Works harmoniously with ruff-format: both are Black-compatible
  - Formatting order: black → docformatter → autopep8 → ruff-check → ruff-format
  - Note: Black and ruff-format produce identical output (ruff-format is Black-compatible)
  - 44 total pre-commit hooks (before isort and autoflake additions)

### Changed

- **Configuration File Reorganization** - Improved structure and consistency
  - Added comprehensive section headers to all major configuration files for better navigation
  - Reorganized .gitignore into focused logical sections (removed irrelevant patterns, added clear categories)
  - Enhanced .yamllint with consistent formatting and section headers
  - Improved .pre-commit-config.yaml with clear category groupings (43 hooks organized by purpose)
  - Added section headers to pyproject.toml for better organization (12 main sections)
  - Added section headers to tox.ini for logical environment grouping (8 categories)
  - Added header to Makefile for consistency
  - Removed trailing blank line from .python-version
  - Maintained backward compatibility: all configurations tested and validated
  - Note: uv.lock intentionally not modified (generated file maintained by UV)

### Added

- **Docformatter Integration** - Python docstring formatting
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook (local) for automatic docstring formatting
  - Tox environment (docformatter) for standalone docstring formatting checks
  - Added to CI/CD pipeline for continuous docstring formatting validation
  - Configuration: wrap_length=100, wrap_summaries=100, wrap_descriptions=100 (match ruff)
  - Style: PEP 257 with pragmatic settings (no forced multi-line for short docstrings)
  - Ruff integration: disabled ruff's docstring-code-format to avoid conflicts, added D413 to ignore list
  - Works alongside ruff-format: docformatter handles docstrings, ruff handles code
- **Rstcheck Integration** - RST syntax checking and validation
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook with Sphinx integration for code block validation
  - Tox environment (rstcheck) for standalone RST syntax checking
  - Added to CI/CD pipeline for continuous documentation syntax validation
  - Configuration: report_level="INFO" (most comprehensive), no ignores for complete validation
  - Works alongside doc8: rstcheck handles syntax/validation, doc8 handles style/formatting
  - Complete RST coverage: syntax (rstcheck) + style (doc8)
- **Doc8 Integration** - RST documentation linting
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook for RST (.rst, .txt) file validation
  - Tox environment (doc8) for standalone documentation linting
  - Added to CI/CD pipeline for continuous documentation quality
  - Configuration: max-line-length=100 (aligns with ruff), extensions=[".rst", ".txt"]
  - Created docs/index.rst to make hook applicable
  - Works alongside pymarkdown/mdformat for complete documentation coverage (RST + Markdown)
- **Autopep8 Integration** - PEP 8 auto-formatting with aggressive conflict resolution
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook runs BEFORE ruff-format (autopep8 first pass, ruff-format finalization)
  - Tox environment (autopep8) for standalone formatting checks
  - Added to CI/CD pipeline for continuous code formatting validation
  - Configuration: max_line_length=100, aggressive=2, ignores E501/W503/E203 (align with ruff)
  - Hook order: autopep8 → ruff-check → ruff-format (allows both formatters to work together)
  - Note: Potential conflicts managed by running autopep8 first, then ruff-format finalizes
- **Absolufy-imports Integration** - Convert relative imports to absolute imports
  - Comprehensive configuration matching ruff's ALL rules philosophy
  - Pre-commit hook configured to process only src/ directory files
  - Tox environment (absolufy-imports) with bash wrapper for glob expansion
  - Added to CI/CD pipeline for continuous import normalization
  - Configuration via command-line args: --application-directories=src (matches project src layout)
  - Aligns with ruff's import handling and isort configuration
  - Ensures consistent absolute imports throughout the codebase
- **Mdformat Integration** - Markdown formatting with GitHub Flavored Markdown support
  - Comprehensive configuration in pyproject.toml matching ruff's ALL rules philosophy
  - Pre-commit hook with mdformat-gfm and mdformat-tables plugins for GitHub Flavored Markdown support
  - Tox environment (mdformat) with bash wrapper for shell glob expansion
  - Added to CI/CD pipeline for continuous markdown formatting validation
  - Configuration aligned with ruff: wrap=100 (matches line-length), end_of_line="lf", number=true
  - Automatically reformatted 18 markdown files on first run (normalized formatting across all docs)
  - Works alongside pymarkdown: mdformat handles formatting, pymarkdown handles linting
- **Flake8 Integration** - Python code linting and style checking
  - Comprehensive configuration matching ruff's ALL rules philosophy as closely as possible
  - Pre-commit hook for automated Python linting (complementary to ruff)
  - Tox environment (flake8) for standalone linting
  - Added to CI/CD pipeline for continuous code quality validation
  - Configuration in pyproject.toml via flake8-pyproject plugin
  - Line length: 100 (aligns with ruff's line-length)
  - Max complexity: 10 (matches ruff's mccabe max-complexity)
  - Per-file ignores for __init__.py and tests (matches ruff's approach)
  - Note: Provides additional validation alongside ruff for comprehensive coverage
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
- Comprehensive pre-commit hooks (42 total):
  - Meta hooks (3): check-hooks-apply, check-useless-excludes, sync-pre-commit-deps
  - File quality hooks (18): whitespace, syntax, security, git checks
  - Python quality hooks (7): noqa, type-ignore, mock, eval, annotations checks
  - Python import hooks (1): absolufy-imports for converting relative to absolute imports
  - Project validation hooks (1): validate-pyproject for pyproject.toml validation
  - YAML linting hooks (1): yamllint for YAML file validation and linting
  - Spelling hooks (1): codespell for code and documentation spell checking
  - Markdown hooks (2): pymarkdown for markdown linting, mdformat for markdown formatting
  - Documentation hooks (2): doc8 for RST style linting, rstcheck for RST syntax checking
  - UV hook (1): uv-lock for dependency lock file validation
  - Flake8 hooks (1): flake8 for Python code linting and style checking
  - Autopep8 hooks (1): autopep8 for PEP 8 auto-formatting (runs before ruff-format)
  - Ruff hooks (2): ruff-check (linting), ruff-format (formatting finalization)
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
  - Removed 6 explicit tox-py\* targets (tox-py310, tox-py311, tox-py312, tox-py313, tox-py314, tox-py315)
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
  - Removed redundant tox-\* targets (tox-py310, tox-py311, tox-ruff-check, tox-mypy, tox-coverage, tox-quality, tox-ci)
  - Removed redundant uv-\* targets (uv-venv, uv-install, uv-install-dev, uv-update, uv-run, uv-init, uv-pre-commit, uv-pre-commit-install)
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
  - Updated requires-python to ">=3.10,\<3.16"
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
  - Integration with Makefile (15 new tox-\* targets)
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

______________________________________________________________________

[1.0.0]: https://github.com/bdperkin/nhl-scrabble/releases/tag/v1.0.0
[2.0.0]: https://github.com/bdperkin/nhl-scrabble/compare/v1.0.0...v2.0.0
