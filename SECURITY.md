# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of NHL Scrabble seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** discuss the vulnerability publicly until it has been addressed

### Please Do

1. **Email**: Send details to the repository owner via GitHub private security advisory

   - Go to: https://github.com/bdperkin/nhl-scrabble/security/advisories/new
   - Or email the maintainer directly (see GitHub profile)

1. **Include**:

   - Type of issue (e.g., SQL injection, XSS, path traversal)
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue (what an attacker could do)

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
1. **Investigation**: We will investigate the issue and determine its severity
1. **Fix Development**: We will work on a fix and keep you informed of progress
1. **Disclosure**: We will coordinate disclosure timing with you
1. **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

### Security Update Process

1. Security patch is developed privately
1. New version is released with security fix
1. Security advisory is published on GitHub
1. CHANGELOG.md is updated with security fix details

## Security Best Practices for Users

### Installation

- Install from trusted sources (PyPI or official GitHub repository)
- Verify package integrity when possible
- Use virtual environments to isolate dependencies

### Configuration

- **Do not** commit `.env` files or credentials to version control
- Use environment variables for sensitive configuration
- Review and understand all configuration options

### API Access

- **NHL API**: This project uses the public NHL API - no authentication required
- Be mindful of rate limiting to avoid being blocked
- The application includes rate limiting (0.3s delay between requests)

## Known Security Considerations

### Data Sources

- **NHL API**: Data is fetched from `https://api-web.nhle.com/`
- All API calls are read-only (GET requests)
- No authentication or personal data is transmitted

### Dependencies

- **Automated Vulnerability Scanning**: Dependabot alerts enabled
- **Automated Security Updates**: Dependabot creates PRs for security fixes
- **Weekly Dependency Updates**: Automated checks every Monday at 9 AM ET
- **CI Security Checks**: pip-audit runs on every PR and main branch push
- Pre-commit hooks include security checks:
  - `detect-private-key` - Prevents committing private keys
  - `check-added-large-files` - Prevents large file commits
  - `blocklint` - Detects non-inclusive language

### Safe Defaults

- **Timeouts**: API requests have 10-second timeout (configurable)
- **Retries**: Limited retry logic with exponential backoff
- **Rate Limiting**: 0.3-second delay between API requests
- **Input Validation**: CLI arguments validated via Click framework
- **Output Sanitization**: File paths validated before writing

## Security Tools in Use

### Automated Security Scanning

- **CodeQL**: GitHub Advanced Security code scanning
  - Runs on every PR and push to main
  - Weekly scheduled scans (Mondays 6 AM UTC)
  - Detects 100+ security vulnerability patterns
  - Results in Security → Code scanning alerts
- **Dependabot Alerts**: Automated dependency vulnerability detection
  - Real-time alerts for known vulnerabilities
  - Automatic security update PRs
  - Email notifications enabled
- **Secret Scanning**: Detects accidentally committed secrets
  - Scans for 200+ secret patterns (API keys, tokens, passwords)
  - Partner alerts to notify service providers
  - Results in Security → Secret scanning alerts
- **pip-audit**: Python dependency vulnerability scanner
  - Runs in CI on every PR and main branch push
  - Checks against PyPI advisory database

### Code Quality and Security

- **MyPy**: Static type checking in strict mode
- **Ruff**: Linting with comprehensive rule set including security rules
- **Pre-commit**: 55 hooks including security checks
- **GitHub Actions**: Automated testing on all PRs
- **Branch Protection**: Main branch requires all CI checks to pass

### Repository Security

- **Protected Main Branch**: Direct commits blocked, PR workflow required
- **Required Status Checks**: All CI tests must pass before merge
- **Squash Merge Only**: Consistent git history, easier reverts
- **Auto-delete Branches**: Reduces clutter and stale branches

## Disclosure Policy

- **Private Disclosure Period**: Minimum 90 days before public disclosure
- **Coordinated Disclosure**: We will work with reporters to coordinate disclosure
- **Public Advisory**: Published on GitHub Security Advisories
- **CVE**: We will request CVE if applicable

## Contact

For security issues, please use GitHub Security Advisories or contact the maintainer directly via GitHub.

For general questions, see [SUPPORT.md](SUPPORT.md).

## Acknowledgments

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

- (None yet - be the first!)

## Version History

- **2024-04-16**: Initial security policy published (v2.0.0)
