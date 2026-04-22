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
      - 'pyproject.toml'
      - 'uv.lock'
      - 'requirements*.txt'

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

- [ ] Workflow file created
- [ ] Runs on dependency changes
- [ ] Checks for vulnerabilities
- [ ] Checks license compatibility
- [ ] Fails on moderate+ vulnerabilities
- [ ] Fails on denied licenses
- [ ] Comments on PRs with details
- [ ] Policy documented
- [ ] Test PRs verified

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

*To be filled during implementation:*

- Policies finalized:
- First violation caught:
