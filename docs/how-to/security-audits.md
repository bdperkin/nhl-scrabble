# Security Audits

How to run security audits for the NHL Scrabble project.

## Quick Start

```bash
# Run comprehensive security audit (all tools)
make security-audit

# Run individual security tools
make pip-audit    # Dependency vulnerabilities
make bandit       # Code security issues
make safety       # Vulnerability database check

# Generate detailed reports
make security-report  # Saves JSON/HTML reports to reports/
```

## Security Tools

### 1. pip-audit

Scans Python dependencies for known vulnerabilities using the PyPI Advisory Database.

**What it checks:**

- Direct dependencies
- Transitive dependencies
- Known CVEs in packages

**Usage:**

```bash
make pip-audit

# Or manually:
pip-audit --desc
```

**Example output:**

```
Found 2 known vulnerabilities in 1 package
Name     Version ID             Fix Versions
-------- ------- -------------- ------------
requests 2.25.0  PYSEC-2021-59  2.25.1,2.26.0
```

### 2. Bandit

Static analysis security linter for Python code.

**What it checks:**

- Hardcoded passwords/secrets
- SQL injection vulnerabilities
- Command injection risks
- Unsafe deserialization
- Weak cryptography
- And 100+ other security issues

**Usage:**

```bash
make bandit

# Or manually:
bandit -r src/ -ll  # Low and above severity
```

**Configuration:** `pyproject.toml` → `[tool.bandit]`

**Example output:**

```
>> Issue: [B303:blacklist] Use of insecure MD2, MD4, MD5, or SHA1 hash function.
   Severity: Medium   Confidence: High
   Location: src/example.py:42
```

### 3. Safety

Checks dependencies against a curated vulnerability database.

**What it checks:**

- Package vulnerabilities
- Security advisories
- CVE database

**Usage:**

```bash
make safety

# Or manually:
safety check
```

**Example output:**

```
+==============================================================================+
|                                                                              |
|                               /$$$$$$            /$$                         |
|                              /$$__  $$          | $$                         |
|           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           |
|          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           |
|         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           |
|          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           |
|          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           |
|         |_______/  \_______/|__/     \_______/   \___/   \____  $$           |
|                                                          /$$  | $$           |
|                                                         |  $$$$$$/           |
|  by pyup.io                                              \______/            |
|                                                                              |
+==============================================================================+
```

## Automated Security Audits

### GitHub Actions

Security audits run automatically:

- **On every push** to main branch
- **On every pull request**
- **Weekly** (Mondays at 9 AM UTC)
- **Manually** via workflow dispatch

**Workflow:** `.github/workflows/security.yml`

**Jobs:**

1. `security-audit` - pip-audit scan
1. `bandit-security-scan` - Code analysis
1. `safety-check` - Vulnerability database

**Artifacts:**

- `pip-audit-report.json`
- `bandit-report.json` and `bandit-report.html`
- `safety-report.json`

Reports are kept for 90 days.

### CI Integration

Security audits are part of the CI pipeline:

```bash
make ci  # Includes quality checks + security audits
```

## Security Reports

Generate detailed reports for security review:

```bash
make security-report
```

This creates:

- `reports/pip-audit-report.json` - Dependency vulnerabilities
- `reports/bandit-report.json` - Code security issues (JSON)
- `reports/bandit-report.html` - Code security issues (HTML)
- `reports/safety-report.json` - Vulnerability database results

**View HTML report:**

```bash
open reports/bandit-report.html
```

## Vulnerability Response

### When vulnerabilities are found

1. **Review the findings**

   ```bash
   make security-audit
   ```

1. **Check severity and impact**

   - CRITICAL/HIGH: Address immediately
   - MEDIUM: Address in next sprint
   - LOW: Address in regular maintenance

1. **Update dependencies**

   ```bash
   # Update specific package
   uv pip install --upgrade package-name

   # Update all packages
   uv pip install --upgrade -e ".[dev]"

   # Update lock file
   uv lock
   ```

1. **Verify fix**

   ```bash
   make security-audit
   ```

1. **Commit and push**

   ```bash
   git add pyproject.toml uv.lock
   git commit -m "fix(security): Update package-name to address CVE-XXXX-XXXXX"
   git push
   ```

### Dependabot Automation

Dependabot automatically:

- Monitors dependencies for vulnerabilities
- Creates pull requests with security updates
- Runs weekly (Mondays at 9 AM ET)

**Configuration:** `.github/dependabot.yml`

## False Positives

If a security finding is a false positive:

1. **Document why it's safe** in code with comments

1. **Add noqa comment** if using ruff/bandit

   ```python
   # Safe: Using random for jitter, not cryptographic purposes
   delay = random.uniform(0, 1)  # noqa: S311
   ```

1. **Update configuration** to skip specific checks

   ```toml
   [tool.bandit]
   skips = ["B311"] # Document why
   ```

## Best Practices

### Before Release

```bash
# Full security audit
make security-audit

# Generate reports for review
make security-report

# Review reports
open reports/bandit-report.html
```

### During Development

```bash
# Quick security check
make bandit

# Check new dependencies
make pip-audit
```

### Regular Maintenance

- **Weekly**: Review Dependabot PRs
- **Monthly**: Run full security audit
- **Quarterly**: Review security policy and practices

## Security Resources

- **Project Security Policy:** [SECURITY.md](../../SECURITY.md)
- **pip-audit:** https://github.com/pypa/pip-audit
- **Bandit:** https://bandit.readthedocs.io/
- **Safety:** https://github.com/pyupio/safety
- **Dependabot:** https://docs.github.com/en/code-security/dependabot
- **CodeQL:** https://codeql.github.com/

## Troubleshooting

### pip-audit fails to connect

```bash
# Use local database
pip-audit --local

# Skip index check
pip-audit --skip-editable
```

### Bandit too many false positives

```bash
# Increase confidence level
bandit -r src/ -lll  # Only high severity

# Skip specific test
bandit -r src/ -s B311
```

### Safety requires authentication

```bash
# Use free tier (limited features)
safety check

# For paid features (not required for this project)
export SAFETY_API_KEY=your-key-here
safety check
```

## See Also

- [Running Tests](run-tests.md)
- [Pre-commit Hooks](../reference/pre-commit-hooks.md)
- [CI/CD Pipeline](../explanation/ci-cd-pipeline.md)
