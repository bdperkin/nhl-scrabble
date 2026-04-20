# Add Bandit Security Linting for Python Code

**GitHub Issue**: #239 - https://github.com/bdperkin/nhl-scrabble/issues/239

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

1-2 hours

## Description

Add bandit security linter to detect security issues in Python code including SQL injection, hardcoded secrets, unsafe YAML loading, weak cryptography, and shell injection risks. Bandit is currently in project dependencies but NOT integrated into pre-commit hooks, tox environments, or CI workflows.

## Current State

**Security Gap:**

The project currently has:

- ✅ General linting (ruff, flake8, mypy)
- ✅ Code quality checks (vulture, unimport, pydocstyle)
- ❌ **NO security-specific Python linting**
- ❌ **NO automated detection of security vulnerabilities**

**Risk Factors:**

- Web server exposed to network (FastAPI)
- External API integration (NHL API)
- User input processing (CLI arguments, web forms)
- File I/O operations (cache, export)
- No security scanning in development workflow

**Bandit Status:**

```bash
# bandit is already installed as a dependency
$ pip list | grep bandit
bandit  1.7.5

# But NOT in pre-commit hooks
$ grep bandit .pre-commit-config.yaml
# (no results)

# And NOT in tox environments
$ grep bandit tox.ini
# (no results)
```

**Common Security Issues Bandit Detects:**

1. **B201-B299**: SQL injection (parameterized queries)
1. **B301-B399**: Hardcoded passwords and secrets
1. **B401-B499**: Weak cryptography (MD5, SHA1)
1. **B501-B599**: Shell injection (subprocess without shell=False)
1. **B601-B699**: YAML loading (yaml.load vs yaml.safe_load)
1. **B701-B799**: Use of eval(), exec(), pickle

## Proposed Solution

### 1. Add Bandit to Pre-commit Hooks

**Configuration:**

```yaml
# .pre-commit-config.yaml

  # ============================================================================
  # Python Security - Security Vulnerability Detection
  # ============================================================================

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.10
    hooks:
      - id: bandit
        name: bandit
        description: Security vulnerability detection for Python code
        args:
          [
            --configfile, pyproject.toml,
            --severity-level, medium,
            --confidence-level, medium,
          ]
        # Skip tests directory (test code uses assert, mock patterns)
        exclude: ^tests/
```

**Why Pre-commit:**

- Catch security issues before commit
- Block HIGH severity vulnerabilities
- Fast feedback loop (< 5 seconds)
- Prevent vulnerable code from entering repository

### 2. Add Bandit Configuration

**pyproject.toml:**

```toml
[tool.bandit]
# Exclude test files and virtual environments
exclude_dirs = [
    "tests",
    ".tox",
    ".venv",
    "venv",
    "build",
    "dist",
]

# Severity: low, medium, high
# Confidence: low, medium, high
# Only report medium+ severity and medium+ confidence
severity = "medium"
confidence = "medium"

# Skip specific tests (with justification)
skips = [
    "B101",  # assert_used - Used extensively in tests (excluded above)
]

# Specific tests to run (optional - leave empty to run all)
tests = []

# Paths to scan
targets = ["src/nhl_scrabble"]
```

**Skip Justifications:**

- **B101 (assert_used)**: Tests use assert statements legitimately
- Tests are excluded via `exclude_dirs` so B101 skip is redundant but explicit

### 3. Add Tox Environment

**tox.ini:**

```ini
[testenv:security]
description = Run security vulnerability scanning
deps =
    bandit[toml]>=1.7.5
commands =
    bandit -r src/ --format json --output {toxworkdir}/bandit-report.json
    bandit -r src/ --format txt
    python -c "import json; data = json.load(open('{toxworkdir}/bandit-report.json')); exit(1 if data['results'] else 0)"

[testenv:bandit]
description = Run bandit security scanner
deps = {[testenv:security]deps}
commands = bandit -r src/ --severity-level medium --confidence-level medium
```

**Why Tox:**

- Isolated environment for security scanning
- JSON report generation for CI artifacts
- Comprehensive codebase scan
- Manual security audits: `tox -e bandit`

### 4. Add GitHub Actions Workflow

**Update .github/workflows/security.yml:**

```yaml
name: Security Scanning

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  bandit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write  # For SARIF upload
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install bandit
        run: pip install bandit[toml]

      - name: Run bandit security scanner
        run: |
          bandit -r src/ \
            --format json \
            --output bandit-results.json \
            --severity-level medium \
            --confidence-level medium

      - name: Run bandit SARIF format
        run: |
          bandit -r src/ \
            --format sarif \
            --output bandit-results.sarif \
            --severity-level medium \
            --confidence-level medium

      - name: Upload bandit results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bandit-security-scan
          path: |
            bandit-results.json
            bandit-results.sarif

      - name: Upload SARIF to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: bandit-results.sarif
          category: bandit

      - name: Check for HIGH severity issues
        run: |
          python -c "
          import json
          with open('bandit-results.json') as f:
              data = json.load(f)
          high_issues = [r for r in data['results'] if r['issue_severity'] == 'HIGH']
          if high_issues:
              print(f'Found {len(high_issues)} HIGH severity issues!')
              for issue in high_issues:
                  print(f\"  - {issue['test_id']}: {issue['issue_text']} ({issue['filename']}:{issue['line_number']})\")
              exit(1)
          "
```

**Why GitHub Actions:**

- Automated security scanning on every PR
- Weekly scheduled scans (catch new vulnerabilities)
- SARIF upload to GitHub Security tab
- Block merges with HIGH severity issues
- Artifact storage for audit trails

### 5. Add Makefile Target

**Makefile:**

```makefile
.PHONY: security bandit bandit-report

security: bandit  ## Run all security checks

bandit:  ## Run bandit security scanner
	@echo "Running bandit security scanner..."
	bandit -r src/ --severity-level medium --confidence-level medium

bandit-report:  ## Generate detailed bandit security report
	@echo "Generating bandit security report..."
	bandit -r src/ --format html --output bandit-report.html
	@echo "Report saved to: bandit-report.html"
```

**Why Makefile:**

- Convenient local execution: `make bandit`
- Consistent command across team
- Generate HTML reports for detailed review
- Part of quality workflow: `make quality`

### 6. Handle Existing Issues

**Initial Scan:**

```bash
# Run bandit on existing codebase
bandit -r src/ --severity-level medium --confidence-level medium

# Review any findings:
# - Fix HIGH severity issues immediately
# - Document MEDIUM severity issues
# - Add skip comments for false positives
```

**False Positive Handling:**

```python
# Example: Skip specific line (with justification)
password = get_password_from_env()  # nosec B105 - password from env, not hardcoded

# Example: Skip entire function
def use_shell_command():
    """Run shell command with user-validated input."""
    # nosec B602 - shell=True required, input validated
    subprocess.run(command, shell=True, check=True)
```

**Document Exceptions:**

Create `.bandit_baseline` for known issues:

```bash
# Generate baseline of current issues
bandit -r src/ --format json --output .bandit_baseline

# In pyproject.toml:
[tool.bandit]
baseline = ".bandit_baseline"
```

## Implementation Steps

1. **Add Pre-commit Hook** (15 min)

   - Update `.pre-commit-config.yaml` with bandit hook
   - Configure to fail on HIGH severity
   - Exclude tests directory
   - Test hook: `pre-commit run bandit --all-files`

1. **Add Bandit Configuration** (10 min)

   - Add `[tool.bandit]` section to `pyproject.toml`
   - Configure exclude_dirs, severity, confidence
   - Document skip justifications
   - Test config: `bandit -r src/ --configfile pyproject.toml`

1. **Run Initial Scan** (15 min)

   - Run bandit on entire codebase
   - Review and categorize findings
   - Fix HIGH severity issues immediately
   - Document MEDIUM/LOW issues
   - Create baseline if needed

1. **Add Tox Environment** (10 min)

   - Add `[testenv:security]` to tox.ini
   - Add `[testenv:bandit]` for quick scans
   - Test: `tox -e bandit`
   - Verify JSON report generation

1. **Update GitHub Actions** (15 min)

   - Update `.github/workflows/security.yml`
   - Add bandit scanning job
   - Configure SARIF upload
   - Add artifact upload
   - Test workflow on PR

1. **Add Makefile Targets** (5 min)

   - Add `bandit` and `bandit-report` targets
   - Update `security` target
   - Test: `make bandit`
   - Generate HTML report: `make bandit-report`

1. **Update Documentation** (10 min)

   - Update CONTRIBUTING.md with security scanning
   - Document how to run bandit locally
   - Add troubleshooting for common issues
   - Update README badges (optional)

## Testing Strategy

### Manual Testing

```bash
# Test pre-commit hook
pre-commit run bandit --all-files
# Verify: Scans all Python files, reports issues

# Test tox environment
tox -e bandit
# Verify: Runs successfully, generates report

# Test Makefile target
make bandit
# Verify: Runs bandit with correct arguments

# Test with known vulnerability
echo "password = 'hardcoded_secret'" >> src/nhl_scrabble/test.py
pre-commit run bandit --files src/nhl_scrabble/test.py
# Verify: Detects hardcoded password (B105)
git checkout src/nhl_scrabble/test.py  # Cleanup
```

### CI Testing

```bash
# Trigger CI workflow
git push origin feature/add-bandit

# Verify in GitHub Actions:
# - bandit job runs successfully
# - SARIF uploaded to Security tab
# - Artifacts uploaded
# - No HIGH severity issues block merge
```

### Security Issue Examples

Test bandit detects common issues:

```python
# B201 - SQL injection
cursor.execute("SELECT * FROM users WHERE id = " + user_id)  # Vulnerable

# B301 - Hardcoded password
PASSWORD = "admin123"  # Vulnerable

# B401 - Weak crypto
import md5  # Vulnerable

# B602 - Shell injection
subprocess.call(user_input, shell=True)  # Vulnerable

# B506 - YAML load
yaml.load(user_data)  # Vulnerable (should use yaml.safe_load)
```

## Acceptance Criteria

- [ ] Bandit pre-commit hook configured and passing
- [ ] `[tool.bandit]` configuration in pyproject.toml
- [ ] `tox -e bandit` environment working
- [ ] GitHub Actions security workflow updated
- [ ] SARIF results uploaded to GitHub Security tab
- [ ] Makefile targets (`bandit`, `bandit-report`) added
- [ ] All HIGH severity issues fixed or documented
- [ ] Documentation updated (CONTRIBUTING.md)
- [ ] Initial security scan completed
- [ ] Baseline created (if needed)
- [ ] All pre-commit hooks pass
- [ ] CI workflow passes
- [ ] Team trained on using bandit

## Related Files

**Modified Files:**

- `.pre-commit-config.yaml` - Add bandit hook
- `pyproject.toml` - Add `[tool.bandit]` configuration
- `tox.ini` - Add security and bandit environments
- `.github/workflows/security.yml` - Add bandit scanning
- `Makefile` - Add bandit targets
- `CONTRIBUTING.md` - Document security scanning
- `.gitignore` - Add `bandit-report.html` (generated reports)

**New Files:**

- `.bandit_baseline` - Baseline of existing issues (optional)
- `bandit-results.json` - CI artifact (gitignored)
- `bandit-results.sarif` - CI artifact (gitignored)

## Dependencies

**Python Dependencies:**

- `bandit[toml]>=1.7.5` - Already in dev dependencies

**No Task Dependencies** - Can implement independently

**Related Tasks:**

- security/010 - Add safety vulnerability scanning (complementary)
- refactoring/014 - Add refurb modernization (code quality)

## Additional Notes

### Bandit vs Ruff Security Rules

**Bandit** (specialized security linter):

- Deeper security analysis (AST-based)
- Security-specific expertise
- More detailed severity/confidence levels
- SARIF/JSON reporting for CI
- Focuses only on security

**Ruff** (general linter with some security rules):

- Fast general linting
- Some security rules (S001-S999)
- Part of broader linting suite
- Less detailed security analysis

**Recommendation**: Use BOTH - ruff for fast general checks, bandit for deep security analysis.

### Security Best Practices

**Development Workflow:**

1. **Pre-commit**: Bandit catches issues before commit
1. **Local testing**: `make bandit` before pushing
1. **CI**: Automated scanning on all PRs
1. **Weekly**: Scheduled scans catch new vulnerabilities
1. **Audit**: Manual review of bandit reports

**Issue Severity Handling:**

- **HIGH**: Fix immediately, block merge
- **MEDIUM**: Fix before release, document if deferred
- **LOW**: Review and fix opportunistically

**False Positive Management:**

- Use `# nosec` sparingly with justification
- Document why skip is needed
- Prefer fixing code over skipping checks
- Review skips during security audits

### GitHub Security Integration

Bandit SARIF upload integrates with GitHub Security:

1. **Security Tab**: View all findings in GitHub UI
1. **Code Scanning**: Inline annotations on code
1. **Alerts**: Email notifications for new issues
1. **Trending**: Track security posture over time
1. **Export**: Download findings for compliance

### Common Issues and Solutions

**Issue**: Bandit reports B101 (assert_used) in src code

```python
# Solution: Don't use assert for business logic
# Bad:
assert user.is_authenticated, "User must be authenticated"

# Good:
if not user.is_authenticated:
    raise PermissionError("User must be authenticated")
```

**Issue**: Bandit reports B603/B607 (subprocess without shell)

```python
# Solution: Use list form, avoid shell=True
# Bad:
subprocess.run(f"ls {user_dir}", shell=True)  # B602, B607

# Good:
subprocess.run(["ls", user_dir], check=True)  # Safe
```

**Issue**: Bandit reports B506 (YAML load)

```python
# Solution: Use yaml.safe_load()
# Bad:
config = yaml.load(file)  # B506

# Good:
config = yaml.safe_load(file)  # Safe
```

### Performance Impact

- **Pre-commit hook**: +2-5 seconds per commit (acceptable)
- **Tox environment**: ~10 seconds for full scan
- **CI workflow**: ~20 seconds for scan + upload
- **Minimal impact**: Worth the security benefits

### Success Metrics

- [ ] Zero HIGH severity issues in codebase
- [ ] All security findings documented/fixed
- [ ] Security scans running in CI (100% of PRs)
- [ ] GitHub Security tab shows bandit findings
- [ ] Team aware of security scanning process
- [ ] Security issues caught before merge

## Implementation Notes

*To be filled during implementation:*

- Number of issues found in initial scan
- HIGH severity issues (count and resolution)
- MEDIUM severity issues (count and status)
- LOW severity issues (count and status)
- False positives added to baseline
- Time spent on fixes
- Deviations from plan
- Actual effort vs estimated
