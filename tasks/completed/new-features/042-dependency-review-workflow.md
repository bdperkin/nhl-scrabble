# Enhanced Dependency Review Workflow

**GitHub Issue**: #309 - https://github.com/bdperkin/nhl-scrabble/issues/309

**Parent Task**: enhancement/022-comprehensive-github-workflows.md (#298)

## Priority

**MEDIUM** - Should Do (Next Month)

## Estimated Effort

1-2 hours

## Description

Implement enhanced dependency review workflow that automatically reviews dependency changes in PRs, checking for vulnerabilities, license compatibility, and policy violations. Provides proactive security and compliance checking.

## Current State

**Basic Dependency Management:**

Currently:

- ✅ Dependabot configured
- ✅ Security scanning exists
- ❌ No PR dependency review
- ❌ No license checking
- ❌ No policy enforcement

## Proposed Solution

Create `.github/workflows/dependency-review.yml`:

```yaml
name: Dependency Review

on:
  pull_request:
    paths:
      - pyproject.toml
      - uv.lock
      - requirements*.txt

permissions:
  contents: read
  pull-requests: write

jobs:
  dependency-review:
    name: Review Dependency Changes
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: moderate
          fail-on-scopes: runtime
          deny-licenses: GPL-3.0, AGPL-3.0
          allow-licenses: MIT, Apache-2.0, BSD-3-Clause, BSD-2-Clause, ISC
          comment-summary-in-pr: always

      - name: Check for security vulnerabilities
        run: |
          pip install pip-audit
          pip-audit --desc --format json --output vulnerabilities.json || true

      - name: Comment on PR with details
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            let vulns = [];

            try {
              vulns = JSON.parse(fs.readFileSync('vulnerabilities.json'));
            } catch (e) {
              console.log('No vulnerabilities file');
            }

            if (vulns.length > 0) {
              let comment = `## 🔒 Dependency Security Review\n\n`;
              comment += `Found ${vulns.length} vulnerabilities:\n\n`;

              for (const vuln of vulns.slice(0, 10)) {
                comment += `- **${vuln.name}** ${vuln.version}\n`;
                comment += `  - ${vuln.description}\n`;
                comment += `  - Fix: ${vuln.fix_versions}\n\n`;
              }

              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                body: comment
              });
            }
```

## Implementation Steps

1. **Create Workflow File** (30min)

   - Create `.github/workflows/dependency-review.yml`
   - Configure triggers
   - Set up dependency-review action

1. **Configure Policies** (30min)

   - Set severity thresholds
   - Define allowed licenses
   - Define denied licenses
   - Configure failure conditions

1. **Add Vulnerability Checking** (30min)

   - Integrate pip-audit
   - Add result commenting
   - Format output

1. **Test Workflow** (30min)

   - Create PR adding dependency
   - Verify review runs
   - Test license detection
   - Test vulnerability detection

1. **Update Documentation** (15min)

   - Document dependency policy
   - Add to CONTRIBUTING.md

## Testing Strategy

```bash
# Test 1: Add safe dependency
pyproject.toml: add "certifi>=2023.0.0"
gh pr create
# Expected: Pass, green check

# Test 2: Add GPL dependency
pyproject.toml: add GPL-licensed package
gh pr create
# Expected: Fail, license violation

# Test 3: Add vulnerable dependency
pyproject.toml: add old vulnerable version
gh pr create
# Expected: Fail or warn, vulnerability detected
```

## Acceptance Criteria

- [x] Workflow file created
- [x] Runs on dependency changes
- [x] Checks for vulnerabilities
- [x] Checks license compatibility
- [x] Fails on moderate+ vulnerabilities
- [x] Fails on denied licenses
- [x] Comments on PRs with details
- [x] Policy documented
- [ ] Test PRs verified (will test after merge)

## Related Files

**New Files:**

- `.github/workflows/dependency-review.yml`

**Modified Files:**

- `CONTRIBUTING.md` - Add dependency policy
- `CLAUDE.md` - Document workflow

## Dependencies

**Tool Dependencies:**

- `actions/dependency-review-action@v4`
- `pip-audit` - Vulnerability scanning

## Additional Notes

### Allowed Licenses

Permissive licenses:

- MIT
- Apache-2.0
- BSD-3-Clause
- BSD-2-Clause
- ISC
- Python-2.0

### Denied Licenses

Copyleft licenses:

- GPL-3.0
- AGPL-3.0
- LGPL (optional)

### Severity Levels

- **Critical**: Always fail
- **High**: Always fail
- **Moderate**: Fail (configurable)
- **Low**: Warn only

## Implementation Notes

**Implemented**: 2026-04-28
**Branch**: new-features/042-dependency-review-workflow
**PR**: #414 - https://github.com/bdperkin/nhl-scrabble/pull/414
**Commits**: 1 commit (85548e8)

### Actual Implementation

Followed the proposed solution closely with complete implementation:

**Workflow Configuration:**

- Created `.github/workflows/dependency-review.yml`
- Configured dependency-review-action v4 with policy settings
- Integrated pip-audit for vulnerability scanning
- Implemented PR commenting with github-script v7
- Added summary reports for job results

**License Policy:**

- **Allowed**: MIT, Apache-2.0, BSD-3-Clause, BSD-2-Clause, ISC, Python-2.0
- **Denied**: GPL-3.0, AGPL-3.0
- Enforced at PR level with fail-on-scopes: runtime

**Severity Policy:**

- **fail-on-severity**: moderate
- Critical/High/Moderate: Fails CI
- Low: Warning only

**Documentation:**

- Added comprehensive "Automated Dependency Review" section to CONTRIBUTING.md
- Updated CLAUDE.md Security section with workflow details
- Documented severity levels, triggers, and troubleshooting

### Challenges Encountered

**YAML Line Length:**

- yamllint enforces 100-character line limit
- Fixed long lines in JavaScript code blocks by:
  - Breaking ternary operators across lines
  - Splitting string concatenations
  - Using backslash continuation in shell commands

**Pre-commit Validation:**

- All 68 hooks passed successfully
- No issues with workflow YAML syntax
- Documentation formatting validated

### Deviations from Plan

**Minor Enhancements:**

- Added `Python-2.0` to allowed licenses list (common in Python packages)
- Enhanced PR comment formatting with better structure
- Added vulnerability count to summary report
- Included fix version information in PR comments

**Implementation Time:**

- Faster than estimated due to clear task specification
- YAML line length fixes added 10 minutes

### Actual vs Estimated Effort

- **Estimated**: 1-2 hours
- **Actual**: ~1.5 hours
- **Breakdown**:
  - Workflow file creation: 30 min
  - YAML line length fixes: 10 min
  - Documentation updates: 20 min
  - Pre-commit validation: 10 min
  - PR creation and task updates: 20 min

### Related PRs

- #414 - Main implementation

### Lessons Learned

**YAML Best Practices:**

- Check line length constraints early (yamllint)
- Break long lines in JavaScript/shell blocks proactively
- Use YAML multiline syntax for readability

**Workflow Development:**

- Test workflow syntax with pre-commit hooks before commit
- Document all policy decisions clearly
- Provide user-friendly error messages in PR comments

**Task Implementation:**

- Clear task specifications significantly speed up implementation
- Pre-flight validation catches issues early
- Conventional commit format improves changelog generation

### Future Enhancements

**Potential Improvements:**

- Add support for custom license exceptions with justification
- Implement caching for pip-audit results
- Add trending analysis for dependency vulnerabilities
- Create dashboard for dependency health metrics
- Add automatic issue creation for critical vulnerabilities

### Test Coverage

**Pre-implementation Testing:**

- ✅ Pre-commit hooks: All 68 passed
- ✅ YAML syntax: Validated by yamllint and check-github-workflows
- ✅ Documentation: Formatted and validated

**Post-implementation Testing:**

- ⏳ Will create test PRs after merge:
  1. Safe dependency (certifi)
  2. GPL-licensed dependency
  3. Vulnerable dependency version

**CI/CD:**

- ⏳ Waiting for CI checks on PR #414
- Expected: All checks pass (no code changes, only workflow + docs)
