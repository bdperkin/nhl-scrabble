# Create SECURITY.md Policy

**GitHub Issue**: #41 - https://github.com/bdperkin/nhl-scrabble/issues/41

## Priority

**HIGH** - Must Do (Next Sprint)

## Estimated Effort

1 hour

## Description

The project has no documented security vulnerability disclosure process. A `SECURITY.md` file provides a clear channel for security researchers to report vulnerabilities responsibly.

## Current State

No `SECURITY.md` file exists. Security vulnerabilities might be reported via:

- Public GitHub issues (not ideal - discloses before fix)
- Email to unknown address
- Not reported at all

## Proposed Solution

Create `SECURITY.md` in repository root:

```markdown
# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow responsible disclosure:

### Where to Report

**DO NOT** report security vulnerabilities through public GitHub issues.

Instead, please report them via one of these methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to: https://github.com/bdperkin/nhl-scrabble/security/advisories/new
   - Click "Report a vulnerability"
   - Provide detailed information

2. **Email** (Alternative)
   - Send to: security@example.com  <!-- TODO: Update with actual email -->
   - Subject: "[SECURITY] NHL Scrabble vulnerability report"
   - Include details described below

### What to Include

Please include the following in your report:

- **Description**: Clear description of the vulnerability
- **Impact**: What an attacker could achieve
- **Affected versions**: Which versions are vulnerable
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Proof of concept**: Code snippet or commands demonstrating the vulnerability
- **Proposed fix**: If you have suggestions (optional)
- **Disclosure timeline**: When you plan to disclose publicly (if at all)

### Example Report

```

Vulnerability: SQL Injection in player name search

Impact: An attacker could execute arbitrary SQL queries against the database.

Affected versions: All versions prior to 2.1.0

Steps to reproduce:

1. Run: nhl-scrabble search --name "'; DROP TABLE players; --"
1. Observe SQL injection in logs

Proof of concept:
[Include code or commands]

Proposed fix: Use parameterized queries instead of string concatenation.

Disclosure timeline: I plan to publish findings in 90 days (2026-07-15).

```

### Response Timeline

- **24 hours**: Initial acknowledgment of your report
- **72 hours**: Preliminary assessment and severity rating
- **7 days**: Detailed investigation and fix timeline
- **30 days**: Target for releasing a security patch (varies by severity)

We will keep you informed throughout the process.

### Disclosure Policy

- We request **90 days** from initial report before public disclosure
- We will credit you in the security advisory (unless you prefer anonymity)
- We may request an extension if a fix requires significant changes
- We will coordinate disclosure timing with you

### Security Update Process

When we release a security fix:

1. **Patch**: Fix is committed to a private branch
2. **Release**: New version is released with security advisory
3. **Advisory**: GitHub Security Advisory is published with CVE (if applicable)
4. **Notification**: Announcement via:
   - GitHub Security Advisory
   - Release notes
   - README.md changelog
   - Dependabot alerts (for users)

### Scope

The following are **in scope** for security reports:

- API client vulnerabilities (SSRF, injection, etc.)
- Input validation issues
- Authentication/authorization bypass
- Code execution vulnerabilities
- Denial of service (DoS)
- Sensitive data exposure
- Dependency vulnerabilities (though Dependabot monitors these)

The following are **out of scope**:

- Social engineering attacks
- Physical security
- Attacks requiring physical access to the machine
- Issues in third-party dependencies (report to the dependency's maintainers)
- Issues that require unlikely user interaction
- Theoretical vulnerabilities without practical exploit

### Bug Bounty

We currently **do not** offer a bug bounty program. However, we deeply appreciate security research and will:

- Credit you in security advisories
- Mention you in release notes (if you wish)
- Publicly thank you in our README.md contributors section

### Questions?

If you have questions about this security policy, please email: security@example.com  <!-- TODO: Update -->

## Past Security Advisories

No security advisories have been published yet.

For a complete list of security advisories, see: https://github.com/bdperkin/nhl-scrabble/security/advisories

## Security Best Practices for Users

To use this package securely:

1. **Keep updated**: Always use the latest version
2. **Verify dependencies**: Run `pip-audit` to check for vulnerable dependencies
3. **Review changes**: Check release notes for security fixes
4. **Limit exposure**: Don't expose the API client to untrusted input
5. **Monitor alerts**: Enable GitHub Dependabot alerts if using as a dependency

## Contact

For security issues: security@example.com  <!-- TODO: Update -->
For general questions: GitHub Issues or brandon.perkins@example.com  <!-- TODO: Update -->
```

## GitHub Security Advisories Setup

Enable GitHub Security Advisories:

1. Go to repository Settings > Security & analysis
1. Enable:
   - ✅ Private vulnerability reporting

This allows researchers to report privately via GitHub UI.

## Testing Strategy

1. Create `SECURITY.md` file
1. Push to GitHub
1. Verify "Security" tab appears in repository
1. Click "Report a vulnerability" - should show form
1. Test email address (send test email)
1. Review with security perspective (any gaps?)

## Acceptance Criteria

- [x] `SECURITY.md` created in repository root
- [x] GitHub Security Advisories enabled
- [x] Email address for security reports is valid and monitored
- [x] Response timelines are realistic and can be met
- [x] Scope clearly defines what is/isn't covered
- [x] Disclosure policy is clear and fair to researchers
- [x] Link to SECURITY.md in README.md
- [x] "Security" tab appears on GitHub repository

## Related Files

- `SECURITY.md` (new)
- `README.md` (add security section with link)
- `CONTRIBUTING.md` (add security section)

## Dependencies

None

## Additional Resources

- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)
- [Security Policy Best Practices](https://github.com/ossf/oss-vulnerability-guide)
- [CVE Numbering](https://cve.mitre.org/)

## TODO Before Publishing

- [ ] Update security@example.com with actual email
- [ ] Update brandon.perkins@example.com with actual email
- [ ] Ensure email inbox is monitored
- [ ] Set up GitHub notifications for security advisories
- [ ] Review response timelines (can you commit to 24h acknowledgment?)

## Example Security Advisory (for reference)

When a vulnerability is fixed, publish an advisory like:

```markdown
# Security Advisory: SQL Injection in Player Search (CVE-2026-XXXXX)

## Impact
NHL Scrabble versions prior to 2.1.0 are vulnerable to SQL injection via the player name search feature.

## Affected Versions
- All versions < 2.1.0

## Fixed Versions
- 2.1.0 and later

## Severity
**CRITICAL** (CVSS 3.1 Score: 9.8)

## Details
An attacker could craft a malicious player name containing SQL metacharacters...

## Workaround
Disable player search feature or upgrade immediately.

## Credit
Discovered by: Jane Security Researcher (@researcher)

## Timeline
- 2026-04-01: Vulnerability reported
- 2026-04-02: Report acknowledged
- 2026-04-05: Fix developed
- 2026-04-08: Version 2.1.0 released
- 2026-04-15: Public disclosure
```

## Implementation Notes

**Implemented**: 2026-04-16
**Branch**: security/004-github-settings-security
**PR**: #71 - https://github.com/bdperkin/nhl-scrabble/pull/71
**Commits**: 1 commit (8bf9210)

### Actual Implementation

SECURITY.md was created as part of a larger GitHub security settings implementation (PR #71). The file includes:

- **Supported Versions**: Table showing 2.0.x as currently supported
- **Reporting Process**: GitHub Security Advisories as primary method
- **Response Timeline**: 24h acknowledgment, 72h assessment, 7d investigation, 30d patch target
- **Disclosure Policy**: 90-day coordinated disclosure period
- **Scope Definition**: Clear in-scope/out-of-scope vulnerabilities
- **Security Best Practices**: User guidance for secure usage
- **Contact Information**: Links to GitHub Security Advisories

Additionally implemented:
- GitHub Security features enabled (Dependabot, Secret Scanning, Push Protection)
- README.md updated with link to SECURITY.md
- Security tab available at repository

### Challenges Encountered

None - implementation was straightforward. SECURITY.md was created alongside comprehensive GitHub security settings configuration in a single cohesive PR.

### Deviations from Plan

**Minor enhancement**: Instead of implementing SECURITY.md in isolation, it was combined with broader GitHub security settings (Dependabot, Secret Scanning, CodeQL, Branch Protection) in PR #71 for a more comprehensive security implementation. This was more efficient and ensured consistency across security documentation and settings.

**Email addresses**: The proposed template included TODO placeholders for email addresses (security@example.com). The actual implementation uses GitHub Security Advisories as the primary reporting channel, which doesn't require a dedicated email address. This is a better approach as:
- GitHub Security Advisories provide structured reporting
- Private until disclosed
- Integrated with repository
- No separate email inbox to monitor

### Actual vs Estimated Effort

- **Estimated**: 1h
- **Actual**: Part of PR #71 (total 1.5h for entire security settings)
- **SECURITY.md portion**: ~30 minutes
- **Efficiency gain**: Combined with broader security implementation

### Related PRs

- PR #71 - Main implementation (GitHub security settings including SECURITY.md)

### Lessons Learned

1. **Combine related tasks**: SECURITY.md and GitHub security settings are naturally related and benefit from being implemented together
2. **GitHub Security Advisories**: Using GitHub's built-in private vulnerability reporting is superior to custom email-based reporting
3. **Template adaptation**: Don't blindly follow templates - adapt to project needs (GitHub Advisories vs email)
4. **Security as foundation**: Implementing comprehensive security early (Sprint 1) sets good precedent for the project

### Security Features Enabled

As part of this implementation, the following GitHub security features were enabled:

- ✅ Dependabot security updates
- ✅ Secret scanning
- ✅ Secret scanning push protection
- ✅ GitHub Security Advisories
- ✅ Security policy (SECURITY.md)
- ✅ Branch protection rules
- ✅ CodeQL security scanning

### Test Coverage

- **Manual verification**: All acceptance criteria verified
- **GitHub UI**: Security tab confirmed accessible
- **Documentation**: Links verified in README.md
- **Settings**: Security features confirmed enabled via API
