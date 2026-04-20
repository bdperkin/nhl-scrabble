# Add check-wheel-contents Package Validator

**GitHub Issue**: #245 - https://github.com/bdperkin/nhl-scrabble/issues/245

## Priority

**LOW** - Nice to Have (Next Quarter)

## Estimated Effort

1-2 hours

## Description

Add check-wheel-contents tool to validate Python wheel package contents before publishing to PyPI. Ensures wheels contain all required files (LICENSE, README), no unexpected files, correct file placement, and proper metadata.

## Current State

**Wheel Validation Gap:**

The project currently has:

- ✅ Package builds successfully (`python -m build`)
- ✅ PyPI publishing configured (GitHub Actions)
- ✅ Package metadata validation (validate-pyproject)
- ❌ **NO wheel content validation**
- ❌ **NO verification of included files**
- ❌ **NO detection of missing LICENSE/README**

**Current Build Process:**

```bash
# Build wheel
python -m build

# Generates:
# dist/nhl_scrabble-2.0.0-py3-none-any.whl
# dist/nhl_scrabble-2.0.0.tar.gz

# Published to PyPI without validation of wheel contents!
```

**Risk Factors:**

- LICENSE file might not be included in wheel
- README might be missing from package
- Unexpected files (tests, .pyc, __pycache__) included
- Entry points might be incorrect
- Package data might be missing

## Proposed Solution

### 1. Add check-wheel-contents to Pre-commit Hooks

**Configuration:**

```yaml
# .pre-commit-config.yaml

  # ============================================================================
  # Package Validation - Wheel Contents
  # ============================================================================

  - repo: https://github.com/jwodder/check-wheel-contents
    rev: v0.6.0
    hooks:
      - id: check-wheel-contents
        name: check wheel contents
        description: Validate Python wheel package contents
        args:
          [
            --ignore, W002,  # Ignore build number in wheel name
            --toplevel, nhl_scrabble,  # Expected top-level package
          ]
        # Only run when wheel-related files change
        files: ^(pyproject\.toml|setup\.py|MANIFEST\.in|src/.*\.py)$
        # Or manually: pre-commit run check-wheel-contents --all-files
```

**Why Pre-commit:**

- Validate wheel before commit
- Catch packaging issues early
- Fast check (< 5 seconds)
- Prevent publishing broken packages

**When to Run:**

- On changes to pyproject.toml
- On changes to package source files
- Before creating releases
- Manually before publishing

### 2. Add Configuration

**pyproject.toml:**

```toml
[tool.check-wheel-contents]
# Expected package name
package = "nhl_scrabble"

# Expected top-level modules/packages
toplevel = ["nhl_scrabble"]

# Files that must be in wheel
# (check-wheel-contents validates these automatically)
# Examples: LICENSE, README, etc.

# Ignore specific warnings
ignore = [
    "W002",  # Wheel contains a build number (acceptable)
]
```

**Common Checks:**

- **W001**: Wheel contains file in unexpected location
- **W002**: Wheel contains build number (usually acceptable)
- **W003**: Wheel is empty
- **W004**: Wheel contains multiple top-level packages
- **W005**: Wheel missing expected .dist-info directory
- **W006**: Wheel has incorrect metadata
- **W007**: Wheel missing LICENSE file
- **W008**: Wheel missing README
- **W009**: Wheel contains __pycache__ or .pyc files
- **W010**: Wheel contains .git or .svn directories

### 3. Add Tox Environment

**tox.ini:**

```ini
[testenv:check-wheel]
description = Check wheel package contents
deps =
    build
    check-wheel-contents>=0.6.0
commands =
    # Build wheel
    python -m build --wheel

    # Check wheel contents
    check-wheel-contents dist/*.whl

[testenv:package]
description = Build and validate package
deps =
    {[testenv:check-wheel]deps}
    twine
commands =
    # Build
    python -m build

    # Check wheel
    check-wheel-contents dist/*.whl

    # Check with twine
    twine check dist/*
```

**Why Tox:**

- Comprehensive package validation
- Pre-publish checks: `tox -e package`
- Clean build environment
- Automated in CI

### 4. Add GitHub Actions Check

**Update .github/workflows/package.yml:**

```yaml
name: Package Validation

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  check-wheel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install build check-wheel-contents twine

      - name: Build package
        run: python -m build

      - name: Check wheel contents
        run: |
          check-wheel-contents dist/*.whl --verbose

      - name: Check package with twine
        run: twine check dist/*

      - name: List wheel contents
        run: |
          unzip -l dist/*.whl

      - name: Upload wheel artifact
        uses: actions/upload-artifact@v4
        with:
          name: python-wheel
          path: dist/*.whl
```

**Why GitHub Actions:**

- Validate on every PR
- Verify before releases
- Block publishes with invalid wheels
- Artifact storage for review

### 5. Add Makefile Targets

**Makefile:**

```makefile
.PHONY: build check-wheel package

build:  ## Build Python package (wheel and sdist)
	@echo "Building package..."
	python -m build

check-wheel: build  ## Build and check wheel contents
	@echo "Checking wheel contents..."
	check-wheel-contents dist/*.whl --verbose

package: check-wheel  ## Build and validate package (wheel + twine)
	@echo "Validating package with twine..."
	twine check dist/*
	@echo "✅ Package ready for publishing"
```

**Why Makefile:**

- Quick package build: `make build`
- Validate wheel: `make check-wheel`
- Full validation: `make package`
- Pre-publish workflow

### 6. Validate Current Wheel

**Check Existing Package:**

```bash
# Install dependencies
pip install build check-wheel-contents twine

# Build current wheel
python -m build --wheel

# Check wheel contents
check-wheel-contents dist/*.whl --verbose

# Common findings to fix:
# - Missing LICENSE in wheel
# - Missing README.md
# - Unexpected test files
# - __pycache__ directories
# - .pyc files

# Inspect wheel contents
unzip -l dist/nhl_scrabble-2.0.0-py3-none-any.whl

# Verify critical files:
# - LICENSE (must be included)
# - README.md (must be included)
# - src/nhl_scrabble/ (package code)
# - nhl_scrabble-2.0.0.dist-info/ (metadata)

# NOT included (good):
# - tests/ directory
# - .tox/ directory
# - __pycache__/
# - *.pyc files
```

**Fix Common Issues:**

**Missing LICENSE:**

```toml
# pyproject.toml - ensure license file included
[project]
license = {file = "LICENSE"}
```

**Missing README:**

```toml
# pyproject.toml - ensure README included
[project]
readme = "README.md"
```

**Unexpected files in wheel:**

```toml
# pyproject.toml - exclude patterns
[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*", "*.pyc", "__pycache__"]
```

## Implementation Steps

1. **Validate Current Wheel** (15 min)

   - Build current wheel: `python -m build --wheel`
   - Check contents: `check-wheel-contents dist/*.whl --verbose`
   - List files: `unzip -l dist/*.whl`
   - Identify issues (missing files, unexpected files)

1. **Fix Wheel Issues** (20 min)

   - Ensure LICENSE included
   - Ensure README included
   - Exclude test files
   - Exclude __pycache__
   - Rebuild and verify: `check-wheel-contents dist/*.whl`

1. **Add Pre-commit Hook** (10 min)

   - Update `.pre-commit-config.yaml`
   - Configure to run on packaging file changes
   - Test: `pre-commit run check-wheel-contents --all-files`

1. **Add Tox Environment** (10 min)

   - Add `[testenv:check-wheel]` to tox.ini
   - Add `[testenv:package]` for full validation
   - Test: `tox -e check-wheel`

1. **Update GitHub Actions** (15 min)

   - Create/update `.github/workflows/package.yml`
   - Add wheel validation job
   - Test on PR

1. **Add Makefile Targets** (5 min)

   - Add `build`, `check-wheel`, `package` targets
   - Test: `make check-wheel`

1. **Update Documentation** (10 min)

   - Update CONTRIBUTING.md with package building
   - Document pre-publish checklist
   - Add troubleshooting section

## Testing Strategy

### Manual Testing

```bash
# Build and check wheel
make check-wheel
# Verify: Wheel builds and passes validation

# Test with intentionally broken wheel
# Temporarily remove LICENSE from wheel
echo "exclude LICENSE" >> MANIFEST.in
python -m build --wheel
check-wheel-contents dist/*.whl
# Verify: Detects missing LICENSE (W007)
git checkout MANIFEST.in  # Restore

# Test tox environment
tox -e check-wheel
# Verify: Builds and validates successfully

# Full package validation
tox -e package
# Verify: Both check-wheel-contents and twine pass
```

### Integration Testing

```bash
# Test pre-commit hook
pre-commit run check-wheel-contents --all-files
# Verify: Builds wheel and checks contents

# Test CI workflow
git push origin feature/check-wheel
# Verify: GitHub Actions runs package validation

# Test actual wheel installation
python -m build
pip install dist/*.whl
nhl-scrabble --version
# Verify: Installs and runs correctly
pip uninstall nhl-scrabble -y
```

## Acceptance Criteria

- [ ] check-wheel-contents pre-commit hook configured
- [ ] Current wheel passes all checks
- [ ] LICENSE file included in wheel
- [ ] README file included in wheel
- [ ] No unexpected files (tests, __pycache__) in wheel
- [ ] `tox -e check-wheel` environment working
- [ ] `tox -e package` full validation working
- [ ] GitHub Actions package validation configured
- [ ] Makefile targets (`build`, `check-wheel`, `package`) added
- [ ] Documentation updated (CONTRIBUTING.md)
- [ ] All checks pass

## Related Files

**Modified Files:**

- `.pre-commit-config.yaml` - Add check-wheel-contents hook
- `pyproject.toml` - Add `[tool.check-wheel-contents]` config, ensure license/readme included
- `tox.ini` - Add check-wheel and package environments
- `.github/workflows/package.yml` - Add wheel validation (new file)
- `Makefile` - Add build, check-wheel, package targets
- `CONTRIBUTING.md` - Document package building and validation
- `MANIFEST.in` - If needed to include/exclude files

**New Files:**

- `.github/workflows/package.yml` - Package validation workflow

## Dependencies

**Python Dependencies:**

- `build` - Already in dev dependencies
- `check-wheel-contents>=0.6.0` - Install via pip/uv
- `twine` - Already in dev dependencies

**No Task Dependencies** - Can implement independently

**Related Tasks:**

- None - Independent package validation improvement

## Additional Notes

### What check-wheel-contents Validates

**File Locations:**

- Top-level package in correct location
- .dist-info directory present
- Scripts in correct bin/ location
- Package data in correct locations

**Required Files:**

- LICENSE file (critical for open source)
- README file (provides package description)
- Entry points defined correctly

**Forbidden Files:**

- Test files (tests/ should not be in wheel)
- .pyc compiled files (distributed on installation)
- __pycache__ directories
- .git or .svn directories
- Editor backup files (.swp, .bak)

### Integration with PyPI Publishing

**Pre-publish Workflow:**

```bash
# 1. Build package
python -m build

# 2. Check wheel contents
check-wheel-contents dist/*.whl

# 3. Check with twine
twine check dist/*

# 4. Test installation
pip install dist/*.whl

# 5. Test package works
nhl-scrabble --version

# 6. Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# 7. Upload to PyPI
twine upload dist/*
```

**GitHub Actions Integration:**

On release tags (v\*):

1. Build package
1. Validate with check-wheel-contents
1. Validate with twine
1. Upload to PyPI (if all checks pass)

### Common Wheel Issues

**Missing LICENSE:**

```
W007: Wheel does not contain LICENSE file

Fix: Add to pyproject.toml:
[project]
license = {file = "LICENSE"}
```

**Test Files in Wheel:**

```
W001: Wheel contains file in unexpected location: tests/

Fix: Update pyproject.toml:
[tool.setuptools.packages.find]
where = ["src"]
exclude = ["tests*"]
```

**__pycache__ in Wheel:**

```
W009: Wheel contains __pycache__ directory

Fix: Clean build:
rm -rf build/ dist/
python -m build
```

### Wheel Content Best Practices

**Include:**

- Package source code (src/nhl_scrabble/)
- LICENSE file
- README.md
- Package metadata (.dist-info/)
- Entry point scripts
- Package data files (templates, static files)

**Exclude:**

- Test files (tests/)
- Documentation source (docs/)
- Development tools (.tox/, .venv/)
- CI configuration (.github/)
- Editor files (.vscode/, .idea/)
- Compiled Python (.pyc, __pycache__/)

### Performance Impact

- **Pre-commit hook**: +5-10 seconds (includes build)
- **Tox environment**: ~15 seconds
- **CI workflow**: ~30 seconds
- **Run only on packaging changes**: Minimal impact

### Benefits

1. **Quality Assurance**: Ensure wheel contains expected files
1. **License Compliance**: Verify LICENSE is distributed
1. **Size Optimization**: Detect unexpected files bloating wheel
1. **Professional Package**: Proper metadata and structure
1. **PyPI Compliance**: Meet PyPI package standards

### Success Metrics

- [ ] All wheels pass check-wheel-contents validation
- [ ] LICENSE and README in every published wheel
- [ ] Zero test files in production wheels
- [ ] Wheel size optimized (no bloat)
- [ ] PyPI packages install cleanly

## Implementation Notes

*To be filled during implementation:*

- Current wheel issues found (missing files, unexpected files)
- Fixes applied to pyproject.toml
- Wheel size before and after optimization
- Time spent on validation setup
- Team feedback
- Deviations from plan
- Actual effort vs estimated
