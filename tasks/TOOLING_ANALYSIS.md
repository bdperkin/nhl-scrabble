# Project-Wide Tooling Analysis and Recommendations

**Date**: 2026-04-21
**Status**: Implementation In Progress (10/10 tasks created, 2/10 complete)
**Next Steps**: Implement remaining tasks, integrate tools into pre-commit and CI/CD

## Executive Summary

Analysis of the NHL Scrabble project identified **10 high-value Python-based tools** missing from the current 57-hook pre-commit configuration. These tools address critical gaps in security scanning, Python modernization, config formatting, and multi-format linting.

**Priority Breakdown:**

- **HIGH Priority (Security)**: 2 tools - bandit, safety
- **MEDIUM Priority (Python Quality)**: 4 tools - pyupgrade (exists), refurb, add-trailing-comma, pyproject-fmt
- **MEDIUM Priority (Multi-Format)**: 2 tools - djlint (exists), check-jsonschema (extended)
- **LOW Priority (Specific)**: 2 tools - check-wheel-contents, ssort

## File Types Present in Project

The project contains diverse file types beyond Python:

| File Type  | Examples                                  | Count | Linting Status    |
| ---------- | ----------------------------------------- | ----- | ----------------- |
| Python     | `src/**/*.py`, `tests/**/*.py`            | 42+   | ✅ Comprehensive  |
| HTML       | `src/nhl_scrabble/templates/**/*.html`    | 5+    | ⚠️ Basic only     |
| CSS        | `src/nhl_scrabble/web/static/css/*.css`   | 2+    | ❌ None           |
| JavaScript | `src/nhl_scrabble/web/static/js/*.js`     | 1+    | ❌ None           |
| JSON       | `.claude/*.json`, `tests/fixtures/*.json` | 4+    | ✅ Basic (syntax) |
| YAML       | `.github/workflows/*.yml`, `.yamllint`    | 6+    | ✅ yamllint       |
| TOML       | `pyproject.toml`                          | 1     | ✅ Basic (syntax) |
| Markdown   | `*.md`, `docs/**/*.md`                    | 20+   | ✅ Comprehensive  |
| RST        | `docs/**/*.rst`                           | 5+    | ✅ Comprehensive  |
| SVG        | `docs/_static/logo.svg`                   | 1+    | ❌ None           |
| Makefile   | `docs/Makefile`                           | 1     | ❌ None           |
| INI        | None found                                | 0     | N/A               |

**Key Finding**: Strong Python/docs coverage, weak HTML/CSS/SVG coverage.

## Recommended Tools by Priority

### HIGH Priority - Security (Immediate Implementation)

#### 1. bandit - Python Security Linter

**Status**: ✅ Complete (Task: security/009, Issue #239, PR #268)

**Purpose**: Detect security issues in Python code

**What It Checks**:

- SQL injection vulnerabilities
- Hardcoded passwords and secrets
- Unsafe YAML loading (yaml.load vs yaml.safe_load)
- Weak cryptography
- Shell injection risks
- Use of `exec()`, `eval()`, `pickle`

**Why Critical**:

- Project has web server (FastAPI) exposed to network
- Handles NHL API data (external input)
- Currently NO security-focused Python linting
- High-severity vulnerabilities easily missed in code review

**Gap It Fills**: Project has ruff (general linting) and flake8, but NO security-specific linting for Python code.

**Integration Points**:

1. **Pre-commit hook** (blocking) - Fail commit on HIGH severity issues
1. **Tox environment** (`tox -e security`) - Run full security scan
1. **GitHub Actions** (`security.yml`) - Run on all PRs
1. **Configuration** - `pyproject.toml` with custom rules

**Estimated Effort**: 1-2 hours
**Category**: security
**Complexity**: LOW - Well-established tool, clear configuration

**Status**: ⚠️ bandit is in dependencies but NOT in pre-commit hooks or tox environments!

#### 2. safety - Dependency Vulnerability Scanner

**Status**: ✅ Complete (Task: security/010, Issue #240, PR #269)

**Purpose**: Check dependencies against CVE databases

**What It Checks**:

- Known vulnerabilities in installed packages
- Outdated packages with security issues
- Severity levels (critical, high, medium, low)
- CVE references and remediation advice

**Why Critical**:

- Project has 50+ dependencies (requests, FastAPI, pydantic, click, etc.)
- Web-facing components (FastAPI server)
- No current dependency vulnerability scanning
- Dependencies change frequently (Dependabot updates)

**Gap It Fills**: Project has deptry (dependency usage), but NO vulnerability scanning for known CVEs.

**Integration Points**:

1. **Pre-commit hook** (warning) - Alert on new vulnerable deps
1. **Tox environment** (`tox -e security`) - Full scan
1. **GitHub Actions** (`security.yml`) - Run weekly + on dependency changes
1. **CI reporting** - Upload results as artifacts

**Estimated Effort**: 1-2 hours
**Category**: security
**Complexity**: LOW - Single command, minimal configuration

**Alternative**: pip-audit (similar functionality, faster)

### MEDIUM Priority - Python Quality (Next Sprint)

#### 3. refurb - Python Code Modernization Linter

**Status**: ✅ Task Created (Task: refactoring/014, Issue #241)

**Purpose**: Detect code that can be simplified using modern Python features

**What It Checks**:

- Use of `dict.get()` vs `dict | {key: value}`
- List comprehension opportunities
- `pathlib` vs `os.path`
- Modern f-string usage
- Type hint improvements
- Dataclass opportunities

**Why Valuable**:

- Project supports Python 3.10-3.14 but may have legacy patterns
- Catches modernization opportunities ruff/flake8 miss
- Complements pyupgrade (already planned in task refactoring/004)
- Improves readability and performance

**Gap It Fills**: pyupgrade (syntax), ruff (linting), but NO semantic code modernization linter.

**Integration Points**:

1. **Pre-commit hook** (blocking or warning) - Suggest improvements
1. **Tox environment** (`tox -e quality`) - Full codebase scan
1. **GitHub Actions** - Run on PRs, allow failures initially
1. **Configuration** - `pyproject.toml` to ignore false positives

**Estimated Effort**: 2-3 hours
**Category**: refactoring
**Complexity**: MEDIUM - May produce false positives requiring configuration

#### 4. pyproject-fmt - pyproject.toml Formatter

**Status**: ✅ Task Created (Task: refactoring/015, Issue #242)

**Purpose**: Auto-format and standardize pyproject.toml

**What It Checks**:

- Consistent section ordering
- Sorted arrays (dependencies, classifiers)
- Normalized formatting
- Removed trailing commas
- Consistent quotes

**Why Valuable**:

- Project has `tox-ini-fmt` for tox.ini but NO formatter for pyproject.toml
- Large pyproject.toml (200+ lines) with manual formatting
- Consistency across team contributions
- Easier git diffs

**Gap It Fills**: Project has validate-pyproject (validation), but NO auto-formatter for pyproject.toml.

**Integration Points**:

1. **Pre-commit hook** (auto-fix) - Format on every commit
1. **CI check** - Verify formatting in GitHub Actions
1. **Configuration** - Minimal (mostly conventions)

**Estimated Effort**: 30min-1 hour
**Category**: refactoring
**Complexity**: LOW - Simple formatter, auto-fix

#### 5. add-trailing-comma - Python Formatter Helper

**Status**: ✅ Task Created (Task: refactoring/016, Issue #243)

**Purpose**: Ensure trailing commas in multi-line Python structures

**What It Checks**:

- Multi-line function arguments
- Multi-line list/dict/set literals
- Multi-line imports
- Multi-line class inheritance

**Why Valuable**:

- Better git diffs (adding item = single line change)
- Prevents merge conflicts
- Complements black/ruff-format
- Python 3.6+ standard practice

**Gap It Fills**: black/ruff-format don't enforce trailing commas.

**Integration Points**:

1. **Pre-commit hook** (auto-fix) - Add commas automatically
1. **Run after black** - Ensure compatibility
1. **Minimal configuration** - Works out of box

**Estimated Effort**: 30min-1 hour
**Category**: refactoring
**Complexity**: LOW - Simple formatter, rare conflicts

### MEDIUM Priority - Multi-Format (Next Month)

#### 6. check-jsonschema (Extended) - JSON/YAML Schema Validation

**Status**: ✅ Task Created (Task: refactoring/017, Issue #244)

**Purpose**: Validate JSON/YAML files against schemas

**What It Checks**:

- GitHub Actions workflow schemas
- Dependabot config schema
- Codecov config schema (`.codecov.yml`)
- Custom JSON schemas for project files

**Why Valuable**:

- Project already uses check-jsonschema for workflows/dependabot
- Missing schema validation for codecov.yml, other configs
- Catch config errors before runtime
- Schema-driven documentation

**Gap It Fills**: Partial coverage - extend to more config files.

**Integration Points**:

1. **Pre-commit hook** (blocking) - Add more check-jsonschema hooks
1. **Multiple hooks** - One per schema type
1. **Custom schemas** - For project-specific JSON files

**Estimated Effort**: 1-2 hours
**Category**: refactoring
**Complexity**: LOW - Extend existing configuration

#### 7. djlint - Jinja2/HTML Template Linter

**Purpose**: Lint HTML and Jinja2 templates

**What It Checks**:

- HTML5 validity
- Jinja2 syntax correctness
- Accessibility (ARIA attributes)
- Indentation and formatting
- Deprecated HTML tags

**Why Valuable**:

- Project has 5+ HTML templates (web interface, reports)
- Uses Jinja2 templating
- NO current HTML linting
- Accessibility compliance

**Gap It Fills**: No HTML/template linting at all.

**Integration Points**:

1. **Pre-commit hook** (auto-fix for formatting, block for errors)
1. **Tox environment** (`tox -e quality`) - Full scan
1. **CI check** - GitHub Actions
1. **Configuration** - `.djlintrc` for project rules

**Estimated Effort**: 1-2 hours
**Category**: refactoring
**Complexity**: LOW - Well-documented, clear rules

**Status**: ⚠️ Already tracked in task refactoring/005!

### LOW Priority - Specific Formats (Next Quarter)

#### 8. check-wheel-contents - Python Wheel Validator

**Status**: ✅ Task Created (Task: refactoring/018, Issue #245)

**Purpose**: Validate Python wheel package contents

**What It Checks**:

- Wheel metadata correctness
- Missing required files (LICENSE, README)
- Unexpected files in wheel
- Correct file placement (scripts, data)
- Duplicate files

**Why Valuable**:

- Project publishes to PyPI
- Prevent packaging mistakes before upload
- Ensure LICENSE is included
- Validate entry points

**Gap It Fills**: No wheel validation before publishing.

**Integration Points**:

1. **Pre-commit hook** (blocking on pyproject.toml/setup.py changes)
1. **Tox environment** (`tox -e package`) - Pre-publish check
1. **CI check** - Before release
1. **Manual run** - `python -m check_wheel_contents dist/*.whl`

**Estimated Effort**: 1-2 hours
**Category**: refactoring
**Complexity**: LOW - Single check, minimal configuration

#### 9. ssort - Python Statement Sorter

**Status**: ✅ Task Created (Task: refactoring/019, Issue #246)

**Purpose**: Auto-sort Python class members and functions

**What It Checks**:

- Sort order: dunder methods, class methods, properties, regular methods
- Consistent member ordering within classes
- Alphabetical sorting within categories
- Separation of public vs private

**Why Valuable**:

- Consistent class structure across codebase
- Easier to find methods
- Complements isort (import sorting)
- Reduces bike-shedding on member order

**Gap It Fills**: isort sorts imports, ssort sorts everything else.

**Integration Points**:

1. **Pre-commit hook** (auto-fix)
1. **Configuration** - May need to disable for some classes
1. **Risk** - May conflict with intentional ordering

**Estimated Effort**: 2-3 hours
**Category**: refactoring
**Complexity**: MEDIUM - May produce unwanted changes, requires careful configuration

**Warning**: Can be opinionated, may conflict with manual ordering preferences.

### Deprioritized - Out of Scope

These tools were considered but deprioritized:

**Node.js-based (excluded per requirements)**:

- eslint (JavaScript linting) - Requires Node.js
- stylelint (CSS linting) - Requires Node.js
- prettier (multi-format formatting) - Requires Node.js

**System-based (excluded per requirements)**:

- checkmake (Makefile linting) - Not Python-based
- shellcheck (Shell script linting) - Not Python-based

**Limited Value**:

- cssbeautifier (CSS formatting) - Only 2 CSS files, rarely edited
- validate-ini (INI validation) - No INI files in project
- XML linting (SVG validation) - Only 1 SVG file, static asset

**Already Covered**:

- pyupgrade - Task refactoring/004 exists
- djlint - Task refactoring/005 exists

## Implementation Recommendations

### Phase 1 (Immediate - Security)

1. **bandit** - Security scanning (1-2h)
1. **safety** - Dependency vulnerabilities (1-2h)

**Total Effort**: 2-4 hours
**Impact**: HIGH - Critical security coverage

### Phase 2 (Next Sprint - Python Quality)

3. **refurb** - Code modernization (2-3h)
1. **pyproject-fmt** - Config formatting (30min-1h)
1. **add-trailing-comma** - Formatter helper (30min-1h)

**Total Effort**: 3-5 hours
**Impact**: MEDIUM - Code quality improvements

### Phase 3 (Next Month - Multi-Format)

6. **check-jsonschema** - Extended validation (1-2h)
1. **djlint** - HTML/Jinja2 linting (1-2h) [Task exists]

**Total Effort**: 2-4 hours
**Impact**: MEDIUM - Config and template quality

### Phase 4 (Next Quarter - Specific)

8. **check-wheel-contents** - Package validation (1-2h)
1. **ssort** - Statement sorting (2-3h)

**Total Effort**: 3-5 hours
**Impact**: LOW - Nice to have refinements

**Grand Total Effort**: 10-18 hours across all phases

## Integration Architecture

Each tool should be integrated across ALL applicable frameworks:

### 1. Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
# Security Tools
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.x
    hooks:
      - id: bandit
        args: [--severity-level, high]

  - repo: local
    hooks:
      - id: safety
        name: safety check
        entry: safety
        args: [check, --json]
        language: system
        pass_filenames: false
```

### 2. Tox Environments (`tox.ini`)

```ini
[testenv:security]
description = Run security checks
deps =
    bandit[toml]
    safety
commands =
    bandit -r src/ --format json -o {toxworkdir}/bandit-report.json
    safety check --json --output {toxworkdir}/safety-report.json

[testenv:quality]
description = Run all quality checks
deps =
    refurb
    {[testenv:security]deps}
commands =
    refurb src/
    {[testenv:security]commands}
```

### 3. GitHub Actions (`.github/workflows/security.yml`)

```yaml
name: Security Scanning

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install bandit[toml] safety
      - name: Run bandit
        run: bandit -r src/ -f json -o bandit-results.json
      - name: Run safety
        run: safety check --json --output safety-results.json
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-results
          path: |
            bandit-results.json
            safety-results.json
```

### 4. Configuration Files (`pyproject.toml`)

```toml
[tool.bandit]
skips = ["B101"]                             # Skip assert_used (used in tests)
exclude_dirs = ["tests/", ".tox/", ".venv/"]

[tool.refurb]
enable_all = true
ignore = [
  "FURB101", # Example: ignore specific rule if needed
]

[tool.pyproject-fmt]
column_width = 100
indent = 4
keep_full_version = true
```

### 5. Makefile Targets (`Makefile`)

```makefile
.PHONY: security quality

security:  ## Run security checks (bandit + safety)
	tox -e security

quality:  ## Run all quality checks
	tox -e quality

bandit:  ## Run bandit security scanner
	bandit -r src/

safety:  ## Run safety dependency checker
	safety check
```

## Success Metrics

**For Each Tool:**

- [ ] Pre-commit hook configured and passing
- [ ] Tox environment created and tested
- [ ] CI workflow updated (if applicable)
- [ ] Configuration in pyproject.toml
- [ ] Makefile target added
- [ ] Documentation updated
- [ ] All existing code passes (or exceptions documented)

**Overall:**

- [ ] Zero HIGH-severity bandit findings (or all documented/fixed)
- [ ] Zero critical/high safety vulnerabilities
- [ ] All tools running in CI
- [ ] Team trained on new tools
- [ ] False positives documented and ignored

## Implementation Status

| Tool                   | Priority | Task ID | Issue | Status          | PR   | Notes                   |
| ---------------------- | -------- | ------- | ----- | --------------- | ---- | ----------------------- |
| bandit                 | HIGH     | 009     | #239  | ✅ Complete     | #268 | Integrated & deployed   |
| safety                 | HIGH     | 010     | #240  | ✅ Complete     | #269 | Integrated & deployed   |
| refurb                 | MEDIUM   | 014     | #241  | ✅ Task Created | -    | Ready for impl          |
| pyproject-fmt          | MEDIUM   | 015     | #242  | ✅ Task Created | -    | Ready for impl          |
| add-trailing-comma     | MEDIUM   | 016     | #243  | ✅ Task Created | -    | Ready for impl          |
| check-jsonschema (ext) | MEDIUM   | 017     | #244  | ✅ Task Created | -    | Extension to existing   |
| djlint                 | MEDIUM   | 005     | #127  | ✅ Task Created | -    | HTML template linting   |
| check-wheel-contents   | LOW      | 018     | #245  | ✅ Task Created | -    | Ready for impl          |
| ssort                  | LOW      | 019     | #246  | ✅ Task Created | -    | Requires team consensus |
| codecov migration      | MEDIUM   | 020     | #285  | ✅ Task Created | -    | CI/CD maintenance       |

**Progress**: 10/10 tasks created (100%), 2/10 implemented (20%)

**Completion Timeline**:

- ✅ **Phase 1** (Security): Complete (2/2 tasks)
- 🔄 **Phase 2** (Python Quality): Ready for implementation (4 tasks, ~7.5-12h)
- 🔄 **Phase 3** (Multi-Format): Ready for implementation (2 tasks, ~2-3h)
- 🔄 **Phase 4** (Specific Tools): Ready for implementation (2 tasks, ~3-5h)

## Next Steps

### Completed ✅

- [x] Create individual task files (10/10 created)
- [x] Create GitHub issues (10/10 created)
- [x] Update tasks/README.md (all 10 tasks indexed)
- [x] Implement HIGH priority security tools (2/2 complete)

### In Progress 🔄

- [ ] Implement MEDIUM priority tools (6 tasks remaining):
  - refactoring/014: refurb (2-3h)
  - refactoring/015: pyproject-fmt (30-60min)
  - refactoring/016: trailing-comma (30-60min)
  - refactoring/017: jsonschema extended (1-2h)
  - refactoring/005: djlint (30-60min)
  - refactoring/020: codecov migration (30-60min)

### Remaining ❌

- [ ] Implement LOW priority tools (2 tasks):
  - refactoring/018: check-wheel-contents (1-2h)
  - refactoring/019: ssort (2-3h, requires team consensus)
- [ ] Verify all tools compatible with project
- [ ] Run initial scans to identify issues
- [ ] Document false positives and exceptions
- [ ] Add tools to CLAUDE.md documentation

## References

- **bandit**: https://bandit.readthedocs.io/
- **safety**: https://pyup.io/safety/
- **refurb**: https://github.com/dosisod/refurb
- **pyproject-fmt**: https://pyproject-fmt.readthedocs.io/
- **add-trailing-comma**: https://github.com/asottile/add-trailing-comma
- **check-jsonschema**: https://check-jsonschema.readthedocs.io/
- **djlint**: https://djlint.com/
- **check-wheel-contents**: https://github.com/jwodder/check-wheel-contents
- **ssort**: https://github.com/bwhmather/ssort
