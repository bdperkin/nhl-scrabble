# ============================================================================
# NHL Scrabble - Makefile
# ============================================================================
# Self-documenting makefile for NHL Scrabble Python Package
# Pattern from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help

###################
# Variables
###################

PYTHON := python3.10
VENV := .venv
BIN := $(VENV)/bin
PYTHON_VENV := $(BIN)/python
PIP := $(BIN)/pip
UV := uv
PYTEST := $(BIN)/pytest
RUFF := $(BIN)/ruff
MYPY := $(BIN)/mypy
PRE_COMMIT := $(BIN)/pre-commit

# Package info
PACKAGE := nhl_scrabble
SRC_DIR := src
TEST_DIR := tests

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

###################
# Phony Targets
###################

.PHONY: help venv install install-dev install-hooks deps clean clean-build clean-pyc clean-test clean-venv clean-all \
        test test-unit test-integration test-cov test-watch test-failed test-verbose \
        tox tox-list tox-parallel tox-clean tox-recreate tox-envs \
        uv-pip uv-check \
        ruff-check ruff-format ruff-format-check mypy quality check pre-commit pip-audit ci \
        build publish publish-test \
        docs serve-docs \
        run run-verbose run-json \
        shell watch init info status version \
        count tree all release

###################
# Help
###################

help: ## Show this help message
	@printf '$(BLUE)NHL Scrabble - Makefile Commands$(NC)\n'
	@printf '\n'
	@printf '$(GREEN)Usage:$(NC)\n'
	@printf '  make $(YELLOW)<target>$(NC)\n'
	@printf '\n'
	@awk 'BEGIN { \
		FS = " *## *"; \
		section = ""; \
	} \
	/^###################$$/ { \
		getline; \
		if ($$0 ~ /^# [A-Z]/) { \
			section = $$0; \
			sub(/^# /, "", section); \
			sections[++section_count] = section; \
		} \
	} \
	/^[a-zA-Z0-9_-]+:.*## / { \
		if (section != "") { \
			target_name = $$1; \
			sub(/:.*/, "", target_name); \
			targets[section, ++target_count[section]] = sprintf("  $(YELLOW)%-20s$(NC) %s", target_name, $$2); \
		} \
	} \
	END { \
		for (i = 1; i <= section_count; i++) { \
			sec = sections[i]; \
			if (target_count[sec] > 0) { \
				printf "\n$(GREEN)%s:$(NC)\n", sec; \
				for (j = 1; j <= target_count[sec]; j++) { \
					print targets[sec, j]; \
				} \
			} \
		} \
		printf "\n"; \
	}' $(MAKEFILE_LIST)
	@printf '$(GREEN)Development workflow:$(NC)\n'
	@printf '  1. make venv          - Create virtual environment\n'
	@printf '  2. make install-dev   - Install package with dev dependencies\n'
	@printf '  3. make install-hooks - Install pre-commit hooks\n'
	@printf '  4. make check         - Run all quality checks before commit\n'
	@printf '\n'

###################
# Setup & Installation
###################

venv: ## Create virtual environment
	@printf "$(BLUE)Creating virtual environment...$(NC)\n"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip setuptools wheel
	@printf "$(GREEN)✓ Virtual environment created at $(VENV)$(NC)\n"
	@printf "$(YELLOW)Activate with: source $(VENV)/bin/activate$(NC)\n"

install: venv ## Install package in editable mode
	@printf "$(BLUE)Installing package...$(NC)\n"
	@$(PIP) install -e .
	@printf "$(GREEN)✓ Package installed$(NC)\n"

install-dev: venv ## Install package with development dependencies
	@printf "$(BLUE)Installing package with dev dependencies...$(NC)\n"
	@$(PIP) install -e ".[dev,docs]"
	@printf "$(GREEN)✓ Package and dev dependencies installed$(NC)\n"

install-hooks: venv ## Install pre-commit hooks
	@printf "$(BLUE)Installing pre-commit hooks...$(NC)\n"
	@test -f $(PRE_COMMIT) || $(PIP) install pre-commit
	@$(PRE_COMMIT) install
	@$(PRE_COMMIT) install --hook-type commit-msg
	@printf "$(GREEN)✓ Pre-commit hooks installed$(NC)\n"

deps: install-dev ## Install all dependencies (alias for install-dev)

update: ## Update all dependencies
	@printf "$(BLUE)Updating dependencies...$(NC)\n"
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install --upgrade -e ".[dev,docs]"
	@$(PRE_COMMIT) autoupdate
	@printf "$(GREEN)✓ Dependencies updated$(NC)\n"

###################
# Cleaning
###################

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts
	@printf "$(GREEN)✓ All artifacts cleaned$(NC)\n"

clean-build: ## Remove build artifacts
	@printf "$(BLUE)Cleaning build artifacts...$(NC)\n"
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	@printf "$(BLUE)Cleaning Python artifacts...$(NC)\n"
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove test and coverage artifacts
	@printf "$(BLUE)Cleaning test artifacts...$(NC)\n"
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache
	@rm -fr .mypy_cache
	@rm -fr .ruff_cache
	@rm -f coverage.xml

clean-venv: ## Remove virtual environment
	@printf "$(BLUE)Removing virtual environment...$(NC)\n"
	@rm -rf $(VENV)
	@printf "$(GREEN)✓ Virtual environment removed$(NC)\n"

clean-all: clean clean-venv ## Remove everything including virtual environment
	@printf "$(GREEN)✓ Complete clean finished$(NC)\n"

###################
# Testing
###################

test: check-venv ## Run all tests
	@printf "$(BLUE)Running all tests...$(NC)\n"
	@$(BIN)/tox -e fast

test-unit: check-venv ## Run unit tests only
	@printf "$(BLUE)Running unit tests...$(NC)\n"
	@$(BIN)/tox -e unit

test-integration: check-venv ## Run integration tests only
	@printf "$(BLUE)Running integration tests...$(NC)\n"
	@$(BIN)/tox -e integration

test-cov: check-venv ## Run tests with coverage report
	@printf "$(BLUE)Running tests with coverage...$(NC)\n"
	@$(BIN)/tox -e coverage

test-watch: check-venv ## Run tests in watch mode (requires pytest-watch)
	@printf "$(BLUE)Running tests in watch mode...$(NC)\n"
	@$(BIN)/tox -e watch

test-failed: check-venv ## Run only failed tests from last run
	@printf "$(BLUE)Running previously failed tests...$(NC)\n"
	@$(BIN)/tox -e fast -- --lf -v

test-verbose: check-venv ## Run tests with verbose output
	@printf "$(BLUE)Running tests with verbose output...$(NC)\n"
	@$(BIN)/tox -e fast -- -vv -s

###################
# Tox - Multi-environment Testing
###################

tox: check-venv ## Run tox tests across all environments
	@printf "$(BLUE)Running tox across all environments...$(NC)\n"
	@$(BIN)/tox

tox-list: check-venv ## List all tox environments
	@printf "$(BLUE)Available tox environments:$(NC)\n"
	@$(BIN)/tox list

tox-parallel: check-venv ## Run tox tests in parallel
	@printf "$(BLUE)Running tox in parallel mode...$(NC)\n"
	@$(BIN)/tox -p auto

tox-clean: ## Clean tox environments
	@printf "$(BLUE)Cleaning tox environments...$(NC)\n"
	@rm -rf .tox/
	@printf "$(GREEN)✓ Tox environments cleaned$(NC)\n"

tox-recreate: check-venv ## Recreate tox environments
	@printf "$(BLUE)Recreating tox environments...$(NC)\n"
	@$(BIN)/tox -r

tox-envs: check-venv ## List all available tox environments
	@printf "$(BLUE)Available tox environments:$(NC)\n"
	@$(BIN)/tox list

# Dynamic pattern rule: Automatically handles any tox-* target
# Usage: make tox-<envname> (e.g., make tox-py310, make tox-coverage, make tox-mypy)
# This provides automatic support for all tox environments without explicit targets
tox-%: check-venv
	@printf "$(BLUE)Running tox -e $*...$(NC)\n"
	@$(BIN)/tox -e $*

###################
# UV - Fast Python Package Manager
###################

uv-pip: ## Access uv pip directly (e.g., make uv-pip ARGS="list")
	@$(UV) pip $(ARGS) --python $(PYTHON_VENV)

uv-check: ## Check if uv is installed
	@command -v uv >/dev/null 2>&1 || { \
		printf "$(RED)✗ uv is not installed$(NC)\n"; \
		printf "$(YELLOW)Install with: curl -LsSf https://astral.sh/uv/install.sh | sh$(NC)\n"; \
		exit 1; \
	}
	@printf "$(GREEN)✓ uv is installed: $$(uv --version)$(NC)\n"

###################
# Code Quality
###################

ruff-check: check-venv ## Linting - check code quality (ruff check)
	@printf "$(BLUE)Running ruff linter...$(NC)\n"
	@$(BIN)/tox -e ruff-check

ruff-format: check-venv ## Formatting - auto-fix code style (ruff format)
	@printf "$(BLUE)Formatting code with ruff...$(NC)\n"
	@$(BIN)/tox -e ruff-format-fix

ruff-format-check: check-venv ## Formatting - check code style without changes
	@printf "$(BLUE)Checking code format...$(NC)\n"
	@$(BIN)/tox -e ruff-format

mypy: check-venv ## Type checking - verify type hints (mypy)
	@printf "$(BLUE)Running mypy type checker...$(NC)\n"
	@$(BIN)/tox -e mypy

quality: check-venv ## Quality - run all checks (ruff-check + mypy)
	@printf "$(BLUE)Running quality checks...$(NC)\n"
	@$(BIN)/tox -m quality

check: check-venv ## Run all checks (format, quality, tests)
	@printf "$(BLUE)Running all checks...$(NC)\n"
	@$(BIN)/tox -e check

pre-commit: ## Run pre-commit hooks on all files
	@printf "$(BLUE)Running pre-commit hooks...$(NC)\n"
	@$(PRE_COMMIT) run --all-files

###################
# Security & Dependencies
###################

pip-audit: check-venv ## Security - scan for vulnerabilities (pip-audit)
	@printf "$(BLUE)Running security audit...$(NC)\n"
	@$(BIN)/tox -e pip-audit

###################
# Build & Publish
###################

build: clean check-venv ## Build distribution packages
	@printf "$(BLUE)Building distribution packages...$(NC)\n"
	@$(BIN)/tox -e build
	@printf "$(GREEN)✓ Build complete: dist/$(NC)\n"
	@ls -lh dist/

publish-test: build ## Publish to TestPyPI
	@printf "$(BLUE)Publishing to TestPyPI...$(NC)\n"
	@$(BIN)/tox -e publish-test

publish: build ## Publish to PyPI (use with caution!)
	@printf "$(RED)Publishing to PyPI...$(NC)\n"
	@$(BIN)/tox -e publish

###################
# Documentation
###################

docs: check-venv ## Build documentation with Sphinx
	@printf "$(BLUE)Building documentation...$(NC)\n"
	@$(BIN)/tox -e docs

serve-docs: check-venv ## Build and serve documentation locally
	@printf "$(BLUE)Serving documentation at http://localhost:8000$(NC)\n"
	@$(BIN)/tox -e serve-docs

docs-api: check-venv ## Generate API reference documentation (auto-generated from docstrings)
	@printf "$(BLUE)Generating API reference documentation...$(NC)\n"
	@mkdir -p docs/reference/api
	@pdoc nhl_scrabble -o docs/reference/api -d markdown
	@printf "$(GREEN)✓ API docs generated: docs/reference/api/$(NC)\n"

docs-cli: check-venv ## Generate CLI reference documentation (auto-generated from Click)
	@printf "$(BLUE)Generating CLI reference documentation...$(NC)\n"
	@$(PYTHON_VENV) tools/generate_cli_docs.py
	@printf "$(GREEN)✓ CLI docs generated: docs/reference/cli-generated.md$(NC)\n"

docs-gen: docs-api docs-cli ## Generate all automated documentation (API + CLI)
	@printf "$(GREEN)✓ All automated documentation generated$(NC)\n"

docs-check: docs-gen ## Check if generated docs are up-to-date (fails if out of date)
	@printf "$(BLUE)Checking if generated docs are up-to-date...$(NC)\n"
	@git diff --exit-code docs/reference/api/ docs/reference/cli-generated.md > /dev/null 2>&1 || \
		(printf "$(RED)✗ Generated docs are out of date! Run 'make docs-gen'$(NC)\n" && exit 1)
	@printf "$(GREEN)✓ Generated docs are up-to-date$(NC)\n"

###################
# Running
###################

run: check-venv ## Run the NHL Scrabble analyzer
	@printf "$(BLUE)Running NHL Scrabble analyzer...$(NC)\n"
	@$(BIN)/tox -e run

run-verbose: check-venv ## Run with verbose logging
	@printf "$(BLUE)Running NHL Scrabble analyzer (verbose)...$(NC)\n"
	@$(BIN)/tox -e run -- --verbose

run-json: check-venv ## Run and output JSON
	@printf "$(BLUE)Running NHL Scrabble analyzer (JSON output)...$(NC)\n"
	@$(BIN)/tox -e run -- --format json --output report.json
	@printf "$(GREEN)✓ Report saved to report.json$(NC)\n"

###################
# Development
###################

shell: ## Open Python shell with package loaded
	@printf "$(BLUE)Opening Python shell...$(NC)\n"
	@$(PYTHON_VENV)

watch: test-watch ## Watch tests (alias for test-watch)

init: venv install-dev install-hooks ## Initialize development environment (venv + install + hooks)
	@printf "$(GREEN)✓ Development environment ready!$(NC)\n"
	@printf "$(YELLOW)Run 'source $(VENV)/bin/activate' to activate the environment$(NC)\n"

info: ## Show project information
	@printf "$(BLUE)NHL Scrabble Project Information$(NC)\n"
	@printf "$(GREEN)Package:$(NC)        $(PACKAGE)\n"
	@printf "$(GREEN)Python:$(NC)         $(PYTHON)\n"
	@printf "$(GREEN)Virtual env:$(NC)    $(VENV)\n"
	@printf "$(GREEN)Source dir:$(NC)     $(SRC_DIR)\n"
	@printf "$(GREEN)Test dir:$(NC)       $(TEST_DIR)\n"
	@printf "\n"
	@printf "$(GREEN)Installed packages:$(NC)\n"
	@$(PIP) list 2>/dev/null | head -20 || printf "Virtual environment not created yet\n"

status: ## Show git and project status
	@printf "$(BLUE)Git Status:$(NC)\n"
	@git status --short
	@printf "\n"
	@printf "$(BLUE)Recent commits:$(NC)\n"
	@git log --oneline -5
	@printf "\n"
	@printf "$(BLUE)Test status:$(NC)\n"
	@$(PYTEST) --collect-only -q 2>/dev/null | tail -1 || printf "Tests not available\n"

###################
# Release Management
###################

release: ci ## Prepare for release (run all checks)
	@printf "$(GREEN)✓ Project verified and ready for release!$(NC)\n"
	@printf "$(YELLOW)Next steps:$(NC)\n"
	@printf "  1. Update version in src/$(PACKAGE)/__init__.py\n"
	@printf "  2. Update CHANGELOG.md\n"
	@printf "  3. Commit changes: git commit -am 'Release vX.Y.Z'\n"
	@printf "  4. Create tag: git tag -a vX.Y.Z -m 'Release vX.Y.Z'\n"
	@printf "  5. Push: git push && git push --tags\n"
	@printf "  6. Build: make build\n"
	@printf "  7. Publish: make publish\n"

version: check-venv ## Show current version
	@printf "$(BLUE)Current version:$(NC)\n"
	@$(BIN)/tox -e version

###################
# All-in-one
###################

all: clean init check build ## Run complete workflow (clean, init, check, build)
	@printf "$(GREEN)✓ Complete workflow finished!$(NC)\n"

###################
# CI/CD Simulation
###################

ci: check-venv ## Simulate CI pipeline locally
	@printf "$(BLUE)Simulating CI pipeline...$(NC)\n"
	@$(BIN)/tox -e ci

###################
# Utility
###################

count: ## Count lines of code
	@printf "$(BLUE)Lines of code:$(NC)\n"
	@find $(SRC_DIR) -name '*.py' | xargs wc -l | tail -1
	@printf "$(BLUE)Lines of test code:$(NC)\n"
	@find $(TEST_DIR) -name '*.py' | xargs wc -l | tail -1

tree: ## Show project directory tree
	@tree -I '__pycache__|*.pyc|*.egg-info|.venv|.git|htmlcov|.pytest_cache|.mypy_cache|.ruff_cache' -L 3

# Check if virtual environment exists for targets that need it
check-venv:
	@test -d $(VENV) || (printf "$(RED)Virtual environment not found. Run 'make venv' first.$(NC)\n" && exit 1)

# Make targets depend on check-venv when needed
install install-dev install-hooks version run shell: check-venv
