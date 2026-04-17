# Test Optional Dependencies

______________________________________________________________________

## title: 'Test Optional Dependencies Configuration' read_only: false type: 'command'

Verify that tests requiring optional dependencies are properly configured with conditional skipping to prevent CI failures.

## Purpose

Tests that depend on external tools or optional dependencies can fail in CI if:

1. The tool isn't installed in all tox environments
1. Tests don't skip gracefully when tool is missing
1. Dependencies are in wrong pyproject.toml section

This command validates optional dependency configuration and suggests fixes.

## Process

1. **Scan Test Files**

   - Find all test files in `tests/` directory
   - Parse imports and subprocess calls
   - Identify external tool dependencies:
     - `sphinx-build` (documentation)
     - `gh` (GitHub CLI)
     - `docker` (containerization)
     - Other CLI tools

1. **Check Tool Availability**

   - For each identified tool:
     - Check if tool exists: `shutil.which("tool-name")`
     - Check if in PATH
     - Check if in project dependencies

1. **Analyze Test Skipping**

   - Check for `pytest.mark.skipif` decorators
   - Verify skip conditions use `shutil.which()`
   - Identify tests missing skip decorators

1. **Verify Dependencies**

   - Check `pyproject.toml` structure:
     - Core dependencies in `[project.dependencies]`
     - Optional deps in `[project.optional-dependencies]`
     - Dev deps in `[project.optional-dependencies.dev]`
   - Ensure optional tools in correct section

1. **Suggest Fixes**

   - Add missing `pytest.mark.skipif` decorators
   - Move dependencies to correct section
   - Update tox environment configuration
   - Add installation instructions to docs

1. **Validate Fixes**

   - Run tests in clean environment: `tox -e py310`
   - Verify tests skip appropriately
   - Confirm no failures due to missing tools

## Usage

```bash
# Test all test files
/test-optional-dependencies

# Test specific file
/test-optional-dependencies tests/test_docs.py

# Test specific directory
/test-optional-dependencies tests/integration/

# Verbose output with all findings
/test-optional-dependencies --verbose

# Auto-fix issues (add skip decorators)
/test-optional-dependencies --fix

# Dry run (show what would be fixed)
/test-optional-dependencies --dry-run
```

## Examples

### Example 1: Missing Skip Decorator

```bash
# Run validation
/test-optional-dependencies tests/test_docs.py

# Output:
# 🔍 Analyzing: tests/test_docs.py
#
# External Dependencies Found:
#   - sphinx-build (subprocess call at line 33)
#   - sphinx-build (subprocess call at line 67)
#
# ❌ Missing Skip Decorators
#
# File: tests/test_docs.py
# Issue: Tests use sphinx-build but no module-level skipif
#
# Current code:
#   import subprocess
#   from pathlib import Path
#
#   def test_sphinx_build_succeeds():
#       result = subprocess.run(["sphinx-build", ...])
#
# Problem:
#   - Test will fail if sphinx-build not installed
#   - Tool is only in [project.optional-dependencies.docs]
#   - Not installed in test-only tox environments
#
# Recommended fix:
#   Add module-level skip decorator:
#
#   import shutil
#   import subprocess
#   from pathlib import Path
#
#   import pytest
#
#   # Skip all tests in this module if sphinx-build not available
#   pytestmark = pytest.mark.skipif(
#       shutil.which("sphinx-build") is None,
#       reason="sphinx-build not found (docs dependencies not installed)",
#   )
#
#   def test_sphinx_build_succeeds():
#       result = subprocess.run(["sphinx-build", ...])
#
# Apply this fix? [y/N]: y
#
# ✏️  Updating tests/test_docs.py...
#
# ✅ Skip decorator added
#
# 🧪 Validating fix...
# Running: tox -e py310 -- tests/test_docs.py
#
# ✅ Tests skip gracefully when sphinx-build not available
#
# Summary:
#   File: tests/test_docs.py
#   Tests: 5 functions
#   External tools: sphinx-build
#   Status: ✅ Properly configured
```

### Example 2: Dependency in Wrong Section

```bash
# Run validation
/test-optional-dependencies tests/test_api.py

# Output:
# 🔍 Analyzing: tests/test_api.py
#
# External Dependencies Found:
#   - requests-mock (import at line 5)
#
# ⚠️  Dependency Configuration Issue
#
# File: tests/test_api.py
# Issue: requests-mock in wrong dependency section
#
# Current: pyproject.toml
#   [project.dependencies]
#   requests-mock>=1.11.0  # ❌ Wrong section
#
# Problem:
#   - requests-mock is test-only dependency
#   - Should NOT be in production dependencies
#   - Bloats production installations
#
# Recommended fix:
#   Move to dev dependencies:
#
#   [project.dependencies]
#   requests>=2.31.0  # Keep production deps
#
#   [project.optional-dependencies.dev]
#   requests-mock>=1.11.0  # Move here
#   pytest>=7.4.0
#
# Apply this fix? [y/N]: y
#
# ✏️  Updating pyproject.toml...
#
# ✅ Dependency moved to dev section
#
# 🔄 Updating lock file...
# Running: uv lock
#
# ✅ Lock file updated
#
# Summary:
#   Package: requests-mock
#   Moved: [project.dependencies] → [project.optional-dependencies.dev]
#   Status: ✅ Properly configured
```

### Example 3: All Tests Properly Configured

```bash
# Run validation on all tests
/test-optional-dependencies

# Output:
# 🔍 Analyzing all test files...
#
# Files scanned: 15
# External dependencies: 3
#
# ✅ tests/test_cli.py
#   - No external dependencies
#
# ✅ tests/test_api.py
#   - Uses requests-mock (in dev deps)
#
# ✅ tests/test_docs.py
#   - Uses sphinx-build (properly skipped)
#   - Module-level pytestmark configured
#
# ✅ tests/integration/test_nhl_api.py
#   - Live API test (no external tools)
#
# ... 11 more files
#
# Summary:
#   Files analyzed: 15
#   Issues found: 0
#   External tools: 3 (sphinx-build, gh, docker)
#   All properly configured: ✅
#
# 🎉 All tests handle optional dependencies correctly!
```

## Detection Patterns

### External Tool Usage

The command detects external tools through:

#### Subprocess Calls

```python
# Detected:
subprocess.run(["sphinx-build", ...])
subprocess.run(["gh", "pr", "list"])
subprocess.Popen(["docker", "run"])

# Pattern: subprocess.* with first arg as string literal
```

#### Shutil.which Checks

```python
# Already has check (good):
if shutil.which("sphinx-build"):
    # test code

# Pattern: shutil.which("tool-name")
```

#### Import Statements

```python
# Package imports:
import sphinx
from sphinx.application import Sphinx

# Pattern: import statements for optional packages
```

### Skip Decorator Patterns

#### Module-Level Skip (Recommended)

```python
import pytest
import shutil

# Skip ALL tests in module if tool missing
pytestmark = pytest.mark.skipif(
    shutil.which("sphinx-build") is None,
    reason="sphinx-build not found (docs dependencies not installed)",
)
```

#### Function-Level Skip

```python
# Skip individual test
@pytest.mark.skipif(
    shutil.which("gh") is None,
    reason="GitHub CLI not installed",
)
def test_github_integration():
    subprocess.run(["gh", "pr", "list"])
```

#### Multiple Tools

```python
# Skip if ANY tool missing
pytestmark = pytest.mark.skipif(
    shutil.which("sphinx-build") is None or shutil.which("gh") is None,
    reason="sphinx-build or gh not found",
)
```

## Common External Tools

### Documentation Tools

```python
# Sphinx
pytestmark = pytest.mark.skipif(
    shutil.which("sphinx-build") is None,
    reason="sphinx-build not found (docs dependencies not installed)",
)

# In pyproject.toml:
[project.optional-dependencies.docs]
sphinx = ">=7.0"
```

### GitHub CLI

```python
# gh command
pytestmark = pytest.mark.skipif(
    shutil.which("gh") is None,
    reason="GitHub CLI not installed",
)

# Installation docs:
# Linux: apt install gh
# Mac: brew install gh
# Windows: choco install gh
```

### Docker

```python
# Docker tests
pytestmark = pytest.mark.skipif(
    shutil.which("docker") is None,
    reason="Docker not installed",
)

# Installation docs:
# https://docs.docker.com/get-docker/
```

### Other Tools

```python
# Git (usually available, but check in CI)
pytestmark = pytest.mark.skipif(
    shutil.which("git") is None,
    reason="Git not installed",
)

# Pandoc (document conversion)
pytestmark = pytest.mark.skipif(
    shutil.which("pandoc") is None,
    reason="Pandoc not installed",
)
```

## Dependency Sections in pyproject.toml

### Production Dependencies

```toml
[project.dependencies]
# Only packages needed to run the application
requests = ">=2.31.0"
pydantic = ">=2.0"
click = ">=8.0"

# ❌ DO NOT include:
# - Test tools (pytest, coverage)
# - Documentation tools (sphinx)
# - Development tools (ruff, mypy)
```

### Optional Documentation Dependencies

```toml
[project.optional-dependencies.docs]
# Packages for building documentation
sphinx = ">=7.0"
sphinx-rtd-theme = ">=2.0"
myst-parser = ">=2.0"

# Install with: pip install -e ".[docs]"
```

### Optional Development Dependencies

```toml
[project.optional-dependencies.dev]
# Packages for development and testing
pytest = ">=7.4.0"
pytest-cov = ">=4.1.0"
ruff = ">=0.1.0"
mypy = ">=1.7.0"

# Install with: pip install -e ".[dev]"
```

### All Optional Dependencies

```toml
[project.optional-dependencies.all]
# Meta-dependency for installing everything
nhl-scrabble = [
    "nhl-scrabble[docs]",
    "nhl-scrabble[dev]",
]

# Install with: pip install -e ".[all]"
```

## Tox Environment Configuration

### Test-Only Environment

```ini
[testenv:py310]
# Only installs test dependencies
deps =
    pytest>=7.4.0
    pytest-cov>=4.1.0
commands =
    pytest {posargs}

# Does NOT install docs dependencies
# Tests requiring sphinx-build will skip
```

### Docs Environment

```ini
[testenv:docs]
# Installs docs dependencies
extras = docs
commands =
    sphinx-build -b html docs docs/_build/html

# Tests in tests/test_docs.py will run here
```

### All Environment

```ini
[testenv:all]
# Installs ALL dependencies
extras = all
commands =
    pytest {posargs}

# All tests run (nothing skips)
```

## Pre-Flight Validation Integration

Use this command in Pre-Flight Validation before pushing:

```bash
# 1. Make changes to tests
# 2. Check optional dependencies
/test-optional-dependencies

# 3. Run tests in clean environment
tox -e py310

# 4. Verify tests skip appropriately
# 5. Commit and push
```

This ensures tests won't fail in CI due to missing tools.

## Best Practices

### When Adding New Test

1. ✅ Identify external dependencies
1. ✅ Add skip decorator if needed
1. ✅ Test in clean environment: `tox -e py310`
1. ✅ Document tool requirements in docstring

### When Adding External Tool

1. ✅ Add to correct pyproject.toml section
1. ✅ Update tox environment if needed
1. ✅ Add skip decorators to tests
1. ✅ Document installation in README

### Skip Decorator Placement

**Use Module-Level** (`pytestmark`) when:

- Multiple tests use same tool
- Entire test file depends on tool
- Cleaner than repeating decorator

**Use Function-Level** (`@pytest.mark.skipif`) when:

- Only one test uses tool
- Mixed dependencies in same file
- Different skip conditions per test

## Error Handling

### Tool Not in PATH

```
⚠️  Warning: sphinx-build found in dependencies but not in PATH

Location: [project.optional-dependencies.docs]
Package: sphinx>=7.0

Problem:
  - Package is installed
  - But sphinx-build command not available
  - May be virtual environment issue

Recommendations:
1. Verify virtual environment activated
2. Reinstall package: pip install --force-reinstall sphinx
3. Check PATH includes venv bin directory
4. Test manually: which sphinx-build
```

### Missing Dependency Declaration

```
❌ Error: requests-mock imported but not in pyproject.toml

File: tests/test_api.py
Import: import requests_mock

Problem:
  - Test imports package
  - Package not declared anywhere in pyproject.toml
  - Tests will fail when dependencies installed fresh

Recommended fix:
  Add to pyproject.toml:

  [project.optional-dependencies.dev]
  requests-mock = ">=1.11.0"

Apply this fix? [y/N]
```

### Overly Broad Skip

```
⚠️  Warning: Module-level skip may be too broad

File: tests/test_api.py
Skip: pytestmark = pytest.mark.skipif(shutil.which("sphinx-build") is None, ...)

Analysis:
  - Only 1 of 15 tests uses sphinx-build
  - Other 14 tests skip unnecessarily
  - Users without sphinx-build miss test coverage

Recommendation:
  Move skip decorator to specific test:

  @pytest.mark.skipif(
      shutil.which("sphinx-build") is None,
      reason="sphinx-build not found",
  )
  def test_sphinx_integration():
      ...

Apply this fix? [y/N]
```

## Output Formats

### Standard Output

```
🔍 Analyzing: tests/test_docs.py
❌ Missing skip decorator for sphinx-build
✅ Fix suggested
⏭️  Apply fix? [y/N]
```

### Verbose Output

```
🔍 Analyzing: tests/test_docs.py

File: tests/test_docs.py
Lines: 189
Functions: 6
Imports: shutil, subprocess, Path, pytest

External Dependencies:
  Line 33: subprocess.run(["sphinx-build", "-b", "html", ...])
    Tool: sphinx-build
    Available: No (shutil.which returned None)

  Line 67: subprocess.run(["sphinx-build", "-b", "linkcheck", ...])
    Tool: sphinx-build
    Available: No

  Line 101: subprocess.run(["sphinx-build", "-b", "coverage", ...])
    Tool: sphinx-build
    Available: No

Skip Decorators:
  Module-level: None ❌
  Function-level: None ❌

Pyproject.toml:
  [project.optional-dependencies.docs]
    sphinx>=7.0 ✅ Declared

Issue:
  Tests depend on sphinx-build but don't skip when unavailable

Recommended fix:
  Add module-level skip decorator (see below)

Fix details:
  [... detailed fix code ...]
```

## Integration with Other Skills

### With /implement-task

```bash
# In Pre-Flight Validation:
1. /test-optional-dependencies tests/
2. Run tox: make tox
3. Verify tests skip appropriately
4. Commit changes
```

### With /validate-pre-commit-hook

```bash
# Both validate different aspects:
/test-optional-dependencies      # Checks test configuration
/validate-pre-commit-hook pytest  # Checks pytest hook passes
```

### With /update-docs

```bash
# After adding documentation tests:
/test-optional-dependencies tests/test_docs.py
/update-docs  # Add tool installation to docs
```

## Related Commands

- `/implement-task` - Uses this in Pre-Flight Validation
- `/validate-pre-commit-hook` - Complementary validation
- `/gh:wait-for-ci` - Shows failures this prevents
- `/update-docs` - Document tool requirements

## Notes

- **Time Saved**: 10-15 minutes per CI failure prevented
- **When to Run**: Before pushing tests with external dependencies
- **Exit Codes**: 0 = all good, 1 = issues found, 2 = critical error
- **Auto-fix**: Adds skip decorators automatically with `--fix`
- **Dry Run**: Use `--dry-run` to preview without changes
