# Add GitHub Dependabot Configuration

**GitHub Issue**: #39 - https://github.com/bdperkin/nhl-scrabble/issues/39

## Priority

**CRITICAL** - Must Do (Next Sprint)

## Estimated Effort

30 minutes

## Description

The project currently has no automated dependency vulnerability scanning. GitHub Dependabot can automatically detect security vulnerabilities in dependencies and create pull requests to update them.

## Current State

No `.github/dependabot.yml` file exists. Dependencies are manually managed and only checked via `pip-audit` during CI runs.

**Gap**: No proactive alerts for new vulnerabilities between CI runs.

## Proposed Solution

Create `.github/dependabot.yml` with comprehensive configuration:

```yaml
# GitHub Dependabot Configuration
# Automatically checks for dependency updates and security vulnerabilities

version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "America/New_York"
    open-pull-requests-limit: 10
    reviewers:
      - "bdperkin"
    assignees:
      - "bdperkin"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "python"
    # Only auto-update patch and minor versions
    versioning-strategy: increase-if-necessary
    # Group updates to reduce PR noise
    groups:
      development-dependencies:
        dependency-type: "development"
        update-types:
          - "minor"
          - "patch"
      production-dependencies:
        dependency-type: "production"
        update-types:
          - "patch"
    # Priority for security updates
    allow:
      - dependency-type: "all"
    # Ignore specific dependencies if needed
    ignore:
      # Example: ignore major version bumps for specific packages
      # - dependency-name: "requests"
      #   update-types: ["version-update:semver-major"]

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "America/New_York"
    open-pull-requests-limit: 5
    reviewers:
      - "bdperkin"
    commit-message:
      prefix: "ci"
    labels:
      - "dependencies"
      - "github-actions"
```

## Additional Configuration

Enable GitHub Security Advisories and Dependabot alerts in repository settings:

1. Go to repository Settings > Security & analysis
1. Enable:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Grouped security updates

## Testing Strategy

1. Create `.github/dependabot.yml` file
1. Push to GitHub
1. Check "Insights > Dependency graph > Dependabot" tab
1. Verify Dependabot runs weekly
1. Test by manually triggering: "Insights > Dependency graph > Dependabot > Check for updates"
1. Verify PR is created for any outdated dependencies
1. Review PR format, labels, commit message

## Acceptance Criteria

- [ ] `.github/dependabot.yml` file created and pushed
- [ ] Dependabot runs weekly on Mondays
- [ ] Security updates are prioritized
- [ ] PRs are properly labeled and assigned
- [ ] Commit messages follow conventional format
- [ ] Updates are grouped to reduce noise
- [ ] GitHub Actions are also monitored
- [ ] Documentation updated with Dependabot information

## Related Files

- `.github/dependabot.yml` (new)
- `README.md` (add Security section)
- `CONTRIBUTING.md` (add Dependabot PR review process)

## Dependencies

None - GitHub feature

## Benefits

- **Proactive**: Alerts for new vulnerabilities immediately
- **Automated**: Pull requests created automatically
- **Prioritized**: Security updates separate from regular updates
- **Grouped**: Reduces PR noise by batching related updates
- **Comprehensive**: Covers Python dependencies and GitHub Actions

## Additional Notes

**Dependabot vs pip-audit**:

- Dependabot: Proactive alerts + automated PRs
- pip-audit: Point-in-time check during CI
- **Both are needed**: Dependabot for ongoing monitoring, pip-audit for gate-keeping

**Example Dependabot PR**:

```
Title: deps(python): Bump requests from 2.31.0 to 2.31.1

Updates `requests` from 2.31.0 to 2.31.1

Changelog:
- Fix CVE-2023-XXXXX: Security vulnerability in ...

Labels: dependencies, python
Reviewers: @bdperkin
```

**Weekly Schedule Rationale**:

- Monday morning: Start of work week
- Weekly: Balances timeliness with noise
- Security updates: Immediate PRs regardless of schedule

**Grouping Strategy**:

- Development dependencies: Group minor/patch updates
- Production dependencies: Only group patch updates (review minor separately)
- Security updates: Never grouped (always individual PRs for visibility)
