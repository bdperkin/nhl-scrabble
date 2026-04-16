---
title: 'Fix Security or Quality Finding'
read_only: false
type: 'command'
---

# Fix Security or Quality Finding

Automatically investigate, fix, test, and merge security or quality findings from GitHub's security tools (CodeQL, Dependabot, Secret Scanning, etc.).

## Process

This command automates the complete security finding remediation workflow:

1. **Identify Security Finding**

   - Review GitHub security alerts
   - Identify specific finding to remediate
   - Extract finding details:
     - Alert type (Dependabot, CodeQL, Secret Scanning, etc.)
     - Severity (Critical, High, Medium, Low)
     - Affected file(s) and line(s)
     - Vulnerability description
     - Recommended fix (if provided)
   - Validate finding is actionable

2. **Create GitHub Issue**

   - Generate descriptive issue title
   - Include finding details in issue body:
     - Alert type and severity
     - Affected components
     - Security impact
     - Remediation steps
   - Add appropriate labels:
     - `security` - For security vulnerabilities
     - `dependencies` - For Dependabot alerts
     - `bug` - For code quality issues
     - Priority label based on severity
   - Create issue using `gh issue create`
   - Extract issue number for tracking

3. **Create Feature Branch**

   - Generate branch name based on finding type:
     - Dependabot: `security/dependabot-{package}-{version}`
     - CodeQL: `security/codeql-{rule-id}`
     - Secret Scanning: `security/secret-removal-{file}`
     - Code Quality: `quality/{issue-type}`
   - Ensure main branch is up-to-date: `git pull origin main`
   - Create and checkout branch: `git checkout -b {branch-name}`
   - Verify branch creation: `git branch --show-current`

4. **Generate Fix**

   - **For Dependabot alerts**:
     - Update dependency version in `pyproject.toml`
     - Run `uv lock` to update lock file
     - Check for breaking changes in changelog
     - Update code if API changes required
   
   - **For CodeQL alerts**:
     - Analyze vulnerable code pattern
     - Implement recommended fix
     - Follow OWASP best practices
     - Add input validation/sanitization
     - Implement proper error handling
   
   - **For Secret Scanning**:
     - Remove hardcoded secrets
     - Move to environment variables
     - Update documentation
     - Add to `.gitignore` patterns
     - Rotate compromised secrets
   
   - **For Code Quality issues**:
     - Fix identified code smell
     - Improve code structure
     - Add missing type hints
     - Improve error handling

5. **Run All Tests**

   - Run full test suite: `pytest`
   - Run with coverage: `pytest --cov`
   - Run type checking: `mypy src/`
   - Run linting: `ruff check`
   - Run formatting check: `ruff format --check`
   - Ensure all tests pass before proceeding
   - If tests fail:
     - Analyze failure cause
     - Fix issues
     - Re-run tests
     - Repeat until all pass

6. **Commit Changes**

   - Stage all changes: `git add -A`
   - Review changes: `git diff --cached`
   - Create commit with conventional commit format:
     ```
     {type}({scope}): {description}
     
     {body}
     
     Fixes #{issue-number}
     Security: {finding-type} - {severity}
     ```
   - Types:
     - `security` - Security vulnerability fixes
     - `fix` - Bug fixes from quality findings
     - `build` - Dependency updates
   - Run pre-commit hooks (automatically)
   - Verify commit created: `git log -1`

7. **Push to Remote Branch**

   - Push branch: `git push -u origin {branch-name}`
   - Verify push succeeded
   - Get remote branch URL

8. **Wait for CI to Complete**

   - Poll CI status: `gh pr checks` (after PR creation)
   - Wait for all checks to pass:
     - Python version tests (3.10, 3.11, 3.12, 3.13)
     - Pre-commit hooks
     - Tox quality checks
     - Code scanning (CodeQL)
     - Security scanning
   - Maximum wait: 30 minutes
   - If checks fail:
     - Review failure logs: `gh run view --log-failed`
     - Fix issues locally
     - Commit and push fixes
     - Wait for re-run
   - If timeout: Report status and pause for manual intervention

9. **Create Pull Request**

   - Generate PR title from issue
   - Create PR body:
     ```markdown
     ## Security Finding
     
     **Issue**: Closes #{issue-number}
     **Type**: {finding-type}
     **Severity**: {severity}
     
     ## Summary
     
     {description-of-fix}
     
     ## Changes
     
     - {change-1}
     - {change-2}
     
     ## Security Impact
     
     {impact-description}
     
     ## Testing
     
     - ✅ All tests pass
     - ✅ Security check passes
     - ✅ No new vulnerabilities introduced
     
     ## Verification
     
     - [ ] Vulnerability resolved
     - [ ] No regression issues
     - [ ] Documentation updated (if needed)
     ```
   - Create PR: `gh pr create --title "{title}" --body "{body}"`
   - Auto-link issue: Include "Closes #{issue-number}" in body
   - Extract PR number

10. **Verify CI Checks Pass**

    - Monitor PR checks: `gh pr checks {pr-number}`
    - Ensure all required checks pass:
      - ✅ All Python version tests
      - ✅ Pre-commit hooks
      - ✅ Security scans (CodeQL, etc.)
      - ✅ Quality checks (ruff, mypy)
      - ✅ Coverage requirements
    - Wait for completion (polling every 30s)
    - If any check fails:
      - Review logs
      - Fix issues
      - Push updates
      - Re-verify

11. **Merge Pull Request**

    - Verify all checks passed: `gh pr checks {pr-number}`
    - Verify PR is approved (if required)
    - Check for merge conflicts: `gh pr view {pr-number} --json mergeable`
    - If conflicts:
      - Update branch: `git pull origin main`
      - Resolve conflicts
      - Run tests again
      - Push resolution
      - Wait for CI
    - Merge PR: `gh pr merge {pr-number} --squash --delete-branch`
    - Use squash merge for clean history
    - Auto-delete remote branch
    - Verify merge succeeded

12. **Delete Local Branch**

    - Checkout main: `git checkout main`
    - Pull latest: `git pull origin main`
    - Delete local branch: `git branch -d {branch-name}`
    - Verify deletion: `git branch`

13. **Wait for CI on Main Branch**

    - Get latest workflow run: `gh run list --branch main --limit 1`
    - Wait for workflow to complete
    - Ensure all checks pass on main
    - Maximum wait: 30 minutes
    - If checks fail on main:
      - Create hotfix immediately
      - Follow same process
      - Priority: CRITICAL

14. **Close GitHub Issue**

    - Verify issue is linked to merged PR
    - Check if auto-closed by PR merge
    - If not auto-closed:
      - Add comment with resolution details:
        ```
        Resolved in PR #{pr-number}
        
        Fix: {brief-description}
        Verified: All tests passing
        Security: Vulnerability remediated
        ```
      - Close issue: `gh issue close {issue-number}`
    - Verify issue is closed: `gh issue view {issue-number}`

15. **Report Completion**

    - Display summary:
      ```
      ✅ Security Finding Remediated!
      
      Finding: {type} - {severity}
      Issue: #{issue-number}
      Branch: {branch-name} (deleted)
      PR: #{pr-number} (merged)
      
      Fix: {summary}
      
      Security Impact: {impact}
      
      Tests: All passing ✅
      CI: All checks passing ✅
      Main: Clean ✅
      ```

## Branch Naming Convention

Follow security-focused branch naming:

**Pattern**: `{category}/{type}-{identifier}`

**Categories**:
- `security/` - Security vulnerabilities
- `quality/` - Code quality issues

**Examples**:

```
Dependabot alert for requests 2.28.0 → 2.31.0
  → security/dependabot-requests-2.31.0

CodeQL alert: SQL injection in user_input.py
  → security/codeql-sql-injection

Secret scanning: API key in config.py
  → security/secret-removal-config

Code quality: Unused import in cli.py
  → quality/unused-import-cli
```

## Commit Message Format

Follow conventional commits with security focus:

```
{type}(security): {subject}

{body}

Fixes #{issue-number}
Security: {finding-type} - {severity}
CVE: {cve-id} (if applicable)

{footer}
```

**Types**:
- `security`: Security vulnerability fixes
- `fix`: Bug fixes from quality findings
- `build`: Dependency updates (Dependabot)

**Examples**:

```
security(deps): upgrade requests to 2.31.0

Update requests package to address CVE-2023-32681 (SSRF vulnerability).

Changes:
- Update requests from 2.28.0 to 2.31.0
- Update uv.lock with new dependency tree
- Verify all tests pass with new version

Fixes #83
Security: Dependabot - HIGH
CVE: CVE-2023-32681
```

```
security(api): fix SQL injection in query builder

Implement parameterized queries to prevent SQL injection attacks
identified by CodeQL scanning.

Changes:
- Replace string concatenation with parameterized queries
- Add input validation for user-provided values
- Add tests for injection attempts
- Update documentation with security best practices

Fixes #84
Security: CodeQL - CRITICAL
CWE: CWE-89 (SQL Injection)
```

## Pull Request Template

Standard PR body for security fixes:

```markdown
## Security Finding

**Issue**: Closes #{issue-number}
**Type**: {Dependabot|CodeQL|Secret Scanning|Code Quality}
**Severity**: {Critical|High|Medium|Low}
**CVE**: {cve-id} (if applicable)

## Summary

{brief-description-of-vulnerability}

## Fix Implementation

{detailed-description-of-fix}

## Changes

- {change-1}
- {change-2}
- {change-3}

## Security Impact

**Before**: {vulnerability-description}
**After**: {mitigated-state}

**Risk Reduced**: {impact-description}

## Testing

- ✅ All existing tests pass
- ✅ New security tests added
- ✅ Manual security verification performed
- ✅ No new vulnerabilities introduced
- ✅ Code scanning passes
- ✅ Dependency scanning passes

## Verification

- [x] Vulnerability is resolved
- [x] No regression in functionality
- [x] Documentation updated (if applicable)
- [x] Security advisory reviewed
- [x] Breaking changes documented (if any)

## Additional Notes

{any-additional-context}
```

## Finding Type Handling

### Dependabot Alerts

**Identification**:
- Navigate to GitHub Security → Dependabot alerts
- Review open alerts
- Prioritize by severity (Critical → High → Medium → Low)

**Fix Process**:
1. Update dependency in `pyproject.toml`
2. Run `uv lock` to update lock file
3. Review changelog for breaking changes
4. Update code if API changes required
5. Run full test suite
6. Verify no new issues introduced

**Example**:
```bash
# Before: pyproject.toml
dependencies = [
    "requests>=2.28.0",
]

# After: pyproject.toml  
dependencies = [
    "requests>=2.31.0",
]

# Update lock file
uv lock

# Test
pytest
```

### CodeQL Alerts

**Identification**:
- Navigate to GitHub Security → Code scanning
- Review CodeQL findings
- Analyze affected code and data flow

**Fix Process**:
1. Understand vulnerability pattern
2. Review CodeQL recommendation
3. Implement fix following OWASP guidelines
4. Add input validation/sanitization
5. Add security tests
6. Verify fix with CodeQL re-scan

**Common Patterns**:

- **SQL Injection**: Use parameterized queries
- **XSS**: Sanitize user input, escape output
- **Path Traversal**: Validate file paths
- **Command Injection**: Avoid shell=True, validate input
- **SSRF**: Validate URLs, use allowlists

### Secret Scanning Alerts

**Identification**:
- Navigate to GitHub Security → Secret scanning
- Review detected secrets
- Verify if secret is real or false positive

**Fix Process**:
1. Remove hardcoded secret from code
2. Add secret to environment variables
3. Update documentation
4. Add pattern to `.gitignore`
5. **CRITICAL**: Rotate the exposed secret immediately
6. Verify secret is not in git history

**Example**:
```python
# Before (INSECURE):
API_KEY = "sk_live_1234567890abcdef"

# After (SECURE):
import os
API_KEY = os.getenv("NHL_API_KEY")
if not API_KEY:
    raise ValueError("NHL_API_KEY environment variable not set")
```

### Code Quality Issues

**Identification**:
- Review code scanning results
- Check for code smells
- Identify maintainability issues

**Fix Process**:
1. Fix identified issue
2. Improve code quality
3. Add type hints if missing
4. Improve error handling
5. Add tests if coverage gaps

## Safety Considerations

**Before Making Changes**:

- ✅ Understand the vulnerability completely
- ✅ Review security advisory details
- ✅ Check for known exploits
- ✅ Review recommended fix
- ✅ Consider security impact of fix

**During Implementation**:

- ✅ Follow security best practices
- ✅ Don't introduce new vulnerabilities
- ✅ Test fix thoroughly
- ✅ Verify no regression
- ✅ Document security considerations

**Before Merging**:

- ✅ All security scans pass
- ✅ All tests pass
- ✅ Code review approved
- ✅ Security advisory addressed
- ✅ Documentation updated

**After Merging**:

- ✅ Verify vulnerability is resolved
- ✅ Monitor for any issues
- ✅ Update security documentation
- ✅ Consider disclosure timeline

**CRITICAL Security Findings**:

- Drop everything and fix immediately
- Notify team of active vulnerability
- Create hotfix branch from main
- Expedite review and merge
- Monitor for exploitation attempts

## Error Handling

### Missing Security Finding

```
🔴 Error: No security finding specified

Please provide:
- Finding type (Dependabot, CodeQL, Secret, Quality)
- Alert URL or identifier
- Affected component

Usage: /fix-security-finding {finding-url-or-description}
```

### Fix Generation Failed

```
🔴 Error: Unable to generate fix

Finding: {type} - {severity}

Possible reasons:
- Complex vulnerability requiring manual analysis
- Insufficient information in alert
- Breaking changes in dependency update

Recommendation:
1. Review security advisory manually
2. Research fix approaches
3. Implement fix manually
4. Run: /fix-security-finding --manual
```

### Tests Failed After Fix

```
🔴 Error: Tests failed after applying fix

Finding: {type}
Failed tests: {count}

Failures:
- {test-1}
- {test-2}

Options:
1. Review test failures
2. Adjust fix implementation
3. Update tests if behavior changed correctly
4. Continue with: --force (not recommended)
```

### CI Failed

```
🔴 Error: CI checks failed

PR: #{pr-number}

Failed checks:
- {check-1}
- {check-2}

Options:
1. Review failure logs: gh run view --log-failed
2. Fix issues locally
3. Push fixes
4. CI will re-run automatically
```

### Merge Conflicts

```
🔴 Error: Merge conflicts detected

PR: #{pr-number}

Conflicting files:
- {file-1}
- {file-2}

Resolution:
1. Update branch: git pull origin main
2. Resolve conflicts
3. Run tests: pytest
4. Commit resolution
5. Push: git push
```

## Usage

```bash
# From Dependabot alert URL
/fix-security-finding https://github.com/owner/repo/security/dependabot/1

# From CodeQL alert URL
/fix-security-finding https://github.com/owner/repo/security/code-scanning/42

# From alert description
/fix-security-finding "Dependabot: Update requests to 2.31.0 (CVE-2023-32681)"

# Manual mode (you implement fix, automation handles workflow)
/fix-security-finding {finding} --manual

# Dry run (show plan without executing)
/fix-security-finding {finding} --dry-run

# Skip CI wait (for urgent fixes)
/fix-security-finding {finding} --no-wait

# Auto-merge on CI success
/fix-security-finding {finding} --auto-merge
```

## Example Workflows

### Example 1: Dependabot Alert

```
Input: /fix-security-finding https://github.com/bdperkin/nhl-scrabble/security/dependabot/15

Process:
1. ✅ Identify: Dependabot alert for requests 2.28.0 → 2.31.0 (CVE-2023-32681)
2. ✅ Create issue: #85 "Security: Update requests to 2.31.0"
3. ✅ Create branch: security/dependabot-requests-2.31.0
4. ✅ Update pyproject.toml: requests>=2.31.0
5. ✅ Run uv lock: Updated dependencies
6. ✅ Run tests: All passing (131/131)
7. ✅ Commit: "security(deps): upgrade requests to 2.31.0"
8. ✅ Push to remote: security/dependabot-requests-2.31.0
9. ✅ Wait for CI: All checks passing
10. ✅ Create PR: #86 "Security: Update requests to 2.31.0"
11. ✅ CI on PR: All checks passing
12. ✅ Merge PR: Squash merged to main
13. ✅ Delete branches: Local and remote deleted
14. ✅ CI on main: All checks passing
15. ✅ Close issue: #85 closed

Result: CVE-2023-32681 remediated in 5 minutes!
```

### Example 2: CodeQL Alert

```
Input: /fix-security-finding https://github.com/bdperkin/nhl-scrabble/security/code-scanning/7

Process:
1. ✅ Identify: CodeQL - SQL injection in api/nhl_client.py:142
2. ✅ Create issue: #87 "Security: Fix SQL injection vulnerability"
3. ✅ Create branch: security/codeql-sql-injection
4. ✅ Analyze: String concatenation in SQL query
5. ✅ Fix: Implement parameterized queries
6. ✅ Add tests: Test injection attempts
7. ✅ Run tests: All passing (135/135, 4 new)
8. ✅ Commit: "security(api): fix SQL injection in query builder"
9. ✅ Push: security/codeql-sql-injection
10. ✅ CI: All checks passing, CodeQL clean
11. ✅ Create PR: #88 "Security: Fix SQL injection vulnerability"
12. ✅ Merge PR: Squash merged
13. ✅ Cleanup: Branches deleted
14. ✅ Verify: CodeQL re-scan shows vulnerability resolved
15. ✅ Close: #87 closed

Result: Critical SQL injection vulnerability fixed!
```

### Example 3: Secret Scanning Alert

```
Input: /fix-security-finding "Secret scanning: API key in config.py"

Process:
1. ✅ Identify: Hardcoded API key in src/nhl_scrabble/config.py:15
2. ✅ Create issue: #89 "Security: Remove hardcoded API key"
3. ✅ Create branch: security/secret-removal-config
4. ✅ Remove secret: Replace with os.getenv()
5. ✅ Add to .env.example: Document required env var
6. ✅ Update docs: Add environment variable documentation
7. ✅ Rotate secret: Generate new API key
8. ✅ Run tests: All passing (with env var set)
9. ✅ Commit: "security(config): remove hardcoded API key"
10. ✅ Push: security/secret-removal-config
11. ✅ CI: All checks passing
12. ✅ PR: #90 created
13. ✅ Merge: Squash merged
14. ✅ Cleanup: Complete
15. ✅ Close: #89 closed

Result: Exposed secret removed and rotated!
```

## Integration with Existing Tools

**GitHub CLI (`gh`)**:
- View alerts: `gh api /repos/:owner/:repo/dependabot/alerts`
- View code scanning: `gh api /repos/:owner/:repo/code-scanning/alerts`
- View secret scanning: `gh api /repos/:owner/:repo/secret-scanning/alerts`

**Pre-commit Hooks**:
- Security checks run automatically on commit
- Includes: bandit, safety, secrets detection

**CI/CD**:
- CodeQL runs on all PRs
- Dependabot checks run daily
- Secret scanning is continuous

## Best Practices

**Prioritization**:

1. **CRITICAL** - Fix immediately (within hours)
   - Active exploits
   - Data exposure
   - Authentication bypass

2. **HIGH** - Fix within 1 week
   - Remote code execution
   - SQL injection
   - XSS vulnerabilities

3. **MEDIUM** - Fix within 1 month
   - Moderate impact vulnerabilities
   - Dependencies with known CVEs

4. **LOW** - Fix when convenient
   - Code quality issues
   - Minor dependency updates

**Security Workflow**:

- ✅ Review all security alerts weekly
- ✅ Prioritize by severity and exploitability
- ✅ Test fixes thoroughly
- ✅ Never bypass security checks
- ✅ Document security decisions
- ✅ Monitor for new vulnerabilities

**Communication**:

- Notify team of critical vulnerabilities
- Document fix approach in issue
- Update security documentation
- Consider security advisory if public-facing

## Metrics to Track

As security findings are resolved, track:

- **Mean Time to Remediate (MTTR)**: Target \<7 days for HIGH
- **Open Vulnerabilities**: Target 0 CRITICAL/HIGH
- **Security Debt**: Trend should be decreasing
- **False Positive Rate**: Track and report
- **Re-opened Vulnerabilities**: Should be rare

## Related Documentation

- **SECURITY.md** - Security policy and reporting
- **CONTRIBUTING.md** - Development guidelines
- **.github/workflows/** - CI/CD security checks
- **GitHub Security** - Security advisories and alerts

---

**Last Updated**: 2026-04-16
**Version**: 1.0.0

**Notes**:
- This command requires GitHub CLI (`gh`) to be installed and authenticated
- All security fixes follow responsible disclosure practices
- Critical vulnerabilities are handled with elevated priority
- Always verify fixes don't introduce new vulnerabilities
