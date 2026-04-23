# Add pyproject-fmt Configuration Formatter

**GitHub Issue**: #242 - https://github.com/bdperkin/nhl-scrabble/issues/242

## Priority

**MEDIUM** - Should Do (Next Sprint)

## Estimated Effort

30 minutes - 1 hour

## Description

Add pyproject-fmt tool to auto-format and standardize pyproject.toml configuration file. The project has a large pyproject.toml (200+ lines) with manual formatting that could benefit from automatic consistent formatting, sorted arrays, and normalized structure.

## Current State

**Configuration Formatting Gap:**

The project currently has:

- ✅ Python code formatting (black, ruff-format, autopep8)
- ✅ tox.ini formatting (tox-ini-fmt)
- ✅ pyproject.toml validation (validate-pyproject)
- ❌ **NO pyproject.toml auto-formatting**
- ❌ **NO automatic section ordering**
- ❌ **NO automatic array sorting**

**Current pyproject.toml State:**

```bash
# Check file size
$ wc -l pyproject.toml
200+ pyproject.toml

# Manual formatting with potential inconsistencies:
# - Section ordering may vary
# - Arrays (dependencies, classifiers) manually sorted
# - Inconsistent spacing
# - Manual line wrapping
```

**Existing Tools:**

| Tool               | Purpose                   | pyproject.toml Coverage |
| ------------------ | ------------------------- | ----------------------- |
| validate-pyproject | Validate structure/schema | ✅ Validation only      |
| tox-ini-fmt        | Format tox.ini            | ❌ Different file       |
| black/ruff-format  | Format Python code        | ❌ Only .py files       |
| pyproject-fmt      | Format pyproject.toml     | ✅ Comprehensive        |

## Proposed Solution

### 1. Add pyproject-fmt to Pre-commit Hooks

**Configuration:**

```yaml
# .pre-commit-config.yaml

  # ============================================================================
  # Configuration Formatting - pyproject.toml
  # ============================================================================

  - repo: https://github.com/tox-dev/pyproject-fmt
    rev: v2.1.3
    hooks:
      - id: pyproject-fmt
        name: pyproject-fmt
        description: Format pyproject.toml
        # Auto-fix enabled (modifies file in place)
        # Run before validate-pyproject to ensure valid format
        additional_dependencies: []
```

**Why Pre-commit:**

- Automatic formatting on every commit
- Consistent structure across team
- Reduces merge conflicts
- Fast execution (< 1 second)

**Hook Ordering:**

- Run `pyproject-fmt` BEFORE `validate-pyproject`
- Ensures formatted file is also valid
- pyproject-fmt → validate-pyproject → pyroma

### 2. Add pyproject-fmt Configuration

**pyproject.toml (minimal configuration needed):**

```toml
[tool.pyproject-fmt]
# Column width for line wrapping
column_width = 100

# Indentation (spaces)
indent = 4

# Keep full version specifiers (don't simplify)
# Example: keep ">=1.0.0" instead of simplifying to ">=1.0"
keep_full_version = true
```

**Default Behavior (what pyproject-fmt does):**

1. **Section Ordering**: Reorders sections to PEP 621 standard order

   ```toml
   # Standard order:
   [build-system]
   [project]
   [project.optional-dependencies]
   [project.scripts]
   [project.entry-points]
   [project.urls]
   [tool.*]
   ```

1. **Array Sorting**: Alphabetically sorts arrays

   ```toml
   # Before:
   dependencies = ["click", "requests", "pydantic"]

   # After:
   dependencies = [
     "click",
     "pydantic",
     "requests",
   ]
   ```

1. **Consistent Formatting**:

   - Trailing commas in arrays
   - Consistent quote style
   - Normalized whitespace
   - Line wrapping at column_width

1. **Metadata Normalization**:

   - Consistent classifier ordering
   - Normalized URLs
   - Standardized license format

### 3. Add Tox Environment

**tox.ini:**

```ini
[testenv:pyproject-fmt]
description = Format pyproject.toml
deps = pyproject-fmt>=2.1.0
commands = pyproject-fmt pyproject.toml

[testenv:format]
description = Run all formatters
deps =
    {[testenv:pyproject-fmt]deps}
    black
    ruff
commands =
    pyproject-fmt pyproject.toml
    black src/ tests/
    ruff format src/ tests/
```

**Why Tox:**

- Manual formatting: `tox -e pyproject-fmt`
- Part of format workflow
- Consistent with other formatters

### 4. Add GitHub Actions Check

**Update .github/workflows/quality.yml:**

```yaml
name: Code Quality

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  formatting:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install pyproject-fmt
        run: pip install pyproject-fmt

      - name: Check pyproject.toml formatting
        run: |
          # Run pyproject-fmt in check mode
          pyproject-fmt --check pyproject.toml

      - name: Show diff if formatting needed
        if: failure()
        run: |
          echo "pyproject.toml needs formatting. Run: pyproject-fmt pyproject.toml"
          pyproject-fmt --diff pyproject.toml
```

**Why GitHub Actions:**

- Verify formatting in CI
- Catch unformatted commits
- Show diff in PR

### 5. Add Makefile Target

**Makefile:**

```makefile
.PHONY: fmt-pyproject format-pyproject

fmt-pyproject:  ## Format pyproject.toml
	@echo "Formatting pyproject.toml..."
	pyproject-fmt pyproject.toml

format-pyproject: fmt-pyproject  ## Alias for fmt-pyproject
```

**Why Makefile:**

- Quick local formatting: `make fmt-pyproject`
- Part of overall format workflow
- Team consistency

### 6. Initial Formatting

**Run Initial Format:**

```bash
# Install pyproject-fmt
pip install pyproject-fmt

# Show what would change (dry run)
pyproject-fmt --diff pyproject.toml

# Apply formatting
pyproject-fmt pyproject.toml

# Verify file is still valid
tox -e validate

# Review changes
git diff pyproject.toml

# Commit formatted file
git add pyproject.toml
git commit -m "style: Format pyproject.toml with pyproject-fmt"
```

**Expected Changes:**

1. **Section reordering** to PEP 621 standard
1. **Dependency sorting** alphabetically
1. **Array formatting** with trailing commas
1. **Consistent indentation** (4 spaces)
1. **Line wrapping** at 100 characters
1. **Classifier sorting** in standard order

## Implementation Steps

1. **Add Pre-commit Hook** (5 min)

   - Update `.pre-commit-config.yaml` with pyproject-fmt hook
   - Position before validate-pyproject
   - Test hook: `pre-commit run pyproject-fmt --all-files`
   - Verify auto-fix behavior

1. **Add Configuration** (5 min)

   - Add `[tool.pyproject-fmt]` to pyproject.toml
   - Set column_width, indent, keep_full_version
   - Test config: `pyproject-fmt pyproject.toml`

1. **Run Initial Format** (10 min)

   - Show diff: `pyproject-fmt --diff pyproject.toml`
   - Review changes carefully
   - Apply formatting: `pyproject-fmt pyproject.toml`
   - Verify validity: `tox -e validate`
   - Commit formatted file

1. **Add Tox Environment** (5 min)

   - Add `[testenv:pyproject-fmt]` to tox.ini
   - Add to `[testenv:format]` workflow
   - Test: `tox -e pyproject-fmt`

1. **Update GitHub Actions** (5 min)

   - Add formatting check to quality.yml
   - Test check mode: `pyproject-fmt --check pyproject.toml`
   - Verify workflow passes

1. **Add Makefile Target** (2 min)

   - Add `fmt-pyproject` target
   - Test: `make fmt-pyproject`

1. **Update Documentation** (3 min)

   - Update CONTRIBUTING.md with pyproject-fmt usage
   - Note: "pyproject.toml automatically formatted on commit"

## Testing Strategy

### Manual Testing

```bash
# Test pre-commit hook
pre-commit run pyproject-fmt --all-files
# Verify: Formats file automatically

# Test tox environment
tox -e pyproject-fmt
# Verify: Formats successfully

# Test Makefile target
make fmt-pyproject
# Verify: Formats pyproject.toml

# Test check mode
pyproject-fmt --check pyproject.toml
# Verify: Returns 0 if formatted, 1 if needs formatting

# Test diff mode
pyproject-fmt --diff pyproject.toml
# Verify: Shows changes without modifying file
```

### Validation Testing

```bash
# Ensure formatted file is still valid
pyproject-fmt pyproject.toml
tox -e validate
# Verify: validate-pyproject passes

# Ensure file is still valid Python package metadata
pip install -e .
# Verify: Installation succeeds

# Ensure tools still read configuration
ruff check src/
mypy src/
# Verify: Tools read config correctly
```

## Acceptance Criteria

- [ ] pyproject-fmt pre-commit hook configured
- [ ] `[tool.pyproject-fmt]` configuration in pyproject.toml
- [ ] Initial formatting applied and committed
- [ ] `tox -e pyproject-fmt` environment working
- [ ] GitHub Actions check configured
- [ ] Makefile target (`fmt-pyproject`) added
- [ ] File validates with validate-pyproject after formatting
- [ ] All tools still read configuration correctly
- [ ] Documentation updated (CONTRIBUTING.md)
- [ ] All pre-commit hooks pass

## Related Files

**Modified Files:**

- `.pre-commit-config.yaml` - Add pyproject-fmt hook
- `pyproject.toml` - Add `[tool.pyproject-fmt]` config, apply initial format
- `tox.ini` - Add pyproject-fmt environment
- `.github/workflows/quality.yml` - Add formatting check
- `Makefile` - Add fmt-pyproject target
- `CONTRIBUTING.md` - Document pyproject-fmt usage

**No New Files** - All configuration in existing files

## Dependencies

**Python Dependencies:**

- `pyproject-fmt>=2.1.0` - Install via pip/uv

**No Task Dependencies** - Can implement independently

**Related Tasks:**

- refactoring/014 - Add refurb (code modernization)
- refactoring/016 - Add trailing comma (formatter helper)

## Additional Notes

### pyproject-fmt Features

**Auto-sorting Arrays:**

```toml
# Before:
dependencies = [
  "click>=8.0",
  "requests>=2.31.0",
  "pydantic>=2.0",
]

# After (alphabetically sorted):
dependencies = [
  "click>=8.0",
  "pydantic>=2.0",
  "requests>=2.31.0",
]
```

**Section Ordering:**

Follows PEP 621 standard order:

1. `[build-system]`
1. `[project]`
1. `[project.*]` subsections
1. `[tool.*]` sections (alphabetically)

**Classifier Ordering:**

```toml
# Classifiers sorted by category then alphabetically
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
]
```

### Integration with Existing Tools

**With validate-pyproject:**

- pyproject-fmt runs BEFORE validate-pyproject
- Ensures formatted file is also valid
- Both in pre-commit workflow

**With tox-ini-fmt:**

- Similar tool for tox.ini
- Consistent formatting philosophy
- Both auto-format config files

**With black/ruff-format:**

- Complementary formatters
- pyproject-fmt for config files
- black/ruff for Python code
- All run in pre-commit

### Breaking Changes

**None Expected** - pyproject-fmt preserves semantics:

- Only formatting changes
- No functional changes
- All tools continue to work
- Validates after formatting

### Performance Impact

- **Pre-commit hook**: < 1 second
- **Tox environment**: ~2 seconds
- **CI check**: ~5 seconds
- **Negligible impact**

### Benefits

1. **Consistency**: Same format across all commits
1. **Merge Conflicts**: Fewer conflicts in pyproject.toml
1. **Readability**: Easier to read and review
1. **Maintainability**: Standard structure
1. **Automation**: Zero manual effort

### Common Changes

After initial formatting, expect to see:

1. **Dependency arrays** sorted alphabetically
1. **Classifiers** reordered to standard categories
1. **Tool sections** reordered alphabetically
1. **Trailing commas** added to arrays
1. **Line wrapping** at column_width (100)
1. **Consistent indentation** (4 spaces)

### False Positives

None expected - pyproject-fmt is well-tested and follows PEP 621 standard.

### Success Metrics

- [ ] pyproject.toml automatically formatted on every commit
- [ ] Zero manual formatting needed
- [ ] Git diffs easier to review
- [ ] Merge conflicts reduced
- [ ] Team satisfied with formatting

## Implementation Notes

*To be filled during implementation:*

- Size of initial formatting changes (lines modified)
- Sections reordered (which ones)
- Arrays sorted (dependencies, classifiers, etc.)
- Time spent on initial formatting
- Issues encountered (if any)
- Team feedback
- Deviations from plan
- Actual effort vs estimated
