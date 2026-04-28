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
- **SSRF Protection**: Comprehensive Server-Side Request Forgery (SSRF) protection prevents unauthorized requests to internal networks, cloud metadata endpoints, and non-NHL domains

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
- **SSRF Protection**: Multi-layer protection against Server-Side Request Forgery attacks

### SSRF Protection

The application implements comprehensive Server-Side Request Forgery (SSRF) protection to prevent unauthorized network requests:

#### Protected Resources

- **Private Networks (RFC 1918)**:
  - 10.0.0.0/8
  - 172.16.0.0/12
  - 192.168.0.0/16
- **Localhost**: 127.0.0.0/8, ::1
- **Link-Local**: 169.254.0.0/16 (includes cloud metadata endpoints)
- **Special Use Ranges**: Broadcast, multicast, reserved ranges
- **IPv6 Private**: fc00::/7, fe80::/10, ff00::/8

#### Cloud Metadata Endpoints Blocked

- AWS EC2: http://169.254.169.254/latest/meta-data/
- Azure: http://169.254.169.254/metadata/instance
- GCP: http://169.254.169.254/computeMetadata/v1/
- Oracle Cloud: http://169.254.169.254/opc/v1/instance/

#### Allowed Domains (Allowlist)

Only these domains are permitted for API requests:

- api-web.nhle.com (primary NHL API)
- api.nhle.com (alternative NHL API)

To add a new domain, it must be explicitly added to `ALLOWED_DOMAINS` in `src/nhl_scrabble/security/ssrf_protection.py`.

#### Blocked Ports

Common internal service ports are blocked:

- 22 (SSH), 23 (Telnet)
- 25 (SMTP)
- 3306 (MySQL), 5432 (PostgreSQL)
- 6379 (Redis)
- 8080 (Proxy/Admin), 8443 (HTTPS Alt)
- 9200 (Elasticsearch), 27017 (MongoDB)

#### Validation Layers

1. **URL Scheme**: Only HTTP/HTTPS allowed
1. **Domain Allowlist**: Hostname must be in allowed domains list
1. **DNS Resolution**: Hostname resolved to IPs before validation
1. **IP Blocklist**: All resolved IPs checked against blocked ranges
1. **Port Blocklist**: Request port checked against blocked ports
1. **HTTPS Enforcement**: API base URL must use HTTPS

#### Attack Scenarios Prevented

- ✅ **Internal Network Scanning**: Cannot access 192.168.x.x, 10.x.x.x
- ✅ **Cloud Metadata Access**: Cannot access 169.254.169.254
- ✅ **Localhost Services**: Cannot access 127.0.0.1, ::1
- ✅ **DNS Rebinding**: DNS resolution happens before validation
- ✅ **Port Scanning**: Common internal service ports blocked
- ✅ **Non-NHL Domains**: Only official NHL domains allowed

#### Configuration

The API base URL can be configured via environment variable:

```bash
# Valid - Official NHL API
export NHL_SCRABBLE_API_BASE_URL="https://api-web.nhle.com/v1"

# Blocked - Private IP
export NHL_SCRABBLE_API_BASE_URL="https://192.168.1.1"
# Error: Invalid API base URL: Hostname '192.168.1.1' not in allowed domains list

# Blocked - Localhost
export NHL_SCRABBLE_API_BASE_URL="http://localhost:8080"
# Error: Invalid API base URL: Hostname 'localhost' not in allowed domains list

# Blocked - Cloud metadata
export NHL_SCRABBLE_API_BASE_URL="http://169.254.169.254"
# Error: Invalid API base URL: Hostname '169.254.169.254' not in allowed domains list
```

#### Reporting SSRF Bypasses

If you discover a way to bypass SSRF protection:

1. **Do not** exploit it or test against production systems
1. Follow the vulnerability reporting process above
1. Include:
   - Exact URL that bypasses protection
   - Steps to reproduce
   - Expected vs actual behavior
   - Potential impact

We treat SSRF vulnerabilities as **HIGH** severity and will prioritize fixes.

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

### Software Bill of Materials (SBOM)

- **Automated SBOM Generation**: Weekly generation of dependency inventory
  - **CycloneDX** format (JSON and XML) - Industry standard for tool integration
  - **SPDX** format (JSON) - Linux Foundation standard for compliance
  - Generated on:
    - Every release (attached to GitHub releases)
    - Weekly schedule (Mondays at 6 AM UTC)
    - Dependency changes (pyproject.toml, uv.lock)
    - Manual trigger via workflow_dispatch
  - Includes:
    - Complete dependency tree
    - License information for all components
    - Package URLs (purl) for each component
    - Build metadata (timestamp, commit, ref)
  - **Location**: GitHub Actions artifacts and release attachments
  - **Retention**: 90 days for artifacts, permanent for releases
  - **Vulnerability Scanning**: SBOM used for automated vulnerability detection with Grype

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

## Known Vulnerabilities and Monitoring

### Active CVE Tracking

The project actively monitors and tracks known vulnerabilities:

**CVE-2026-3219** (pip)

- **Status**: No fix available (as of April 2026)
- **Severity**: MEDIUM
- **Description**: pip handles concatenated tar and ZIP files as ZIP files regardless of filename
- **Impact**: Could result in confusing installation behavior
- **Mitigation**: Temporarily ignored in pip-audit workflow (`.github/workflows/security.yml`)
- **Tracking**: Issue #375
- **Action Plan**:
  1. Monitor pip releases monthly for security patches
  1. Remove `--ignore-vuln CVE-2026-3219` flag when fix is available
  1. Verify resolution with pip-audit
  1. Close tracking issue

### CVE Monitoring Process

When vulnerabilities are discovered with no immediate fix:

1. **Create Tracking Issue**: GitHub issue created with CVE details
1. **Add Mitigation**: Temporary workaround implemented (e.g., ignore flag)
1. **Document**: CVE added to this SECURITY.md file
1. **Monitor**: Regular checks for patches (weekly for CRITICAL/HIGH, monthly for MEDIUM/LOW)
1. **Resolve**: Apply fix when available, remove workarounds, close issue
1. **Verify**: Run security scans to confirm resolution

### Security Monitoring Resources

- **PyPI pip releases**: https://pypi.org/project/pip/#history
- **pip changelog**: https://pip.pypa.io/en/stable/news/
- **pip security advisories**: https://github.com/pypa/pip/security/advisories
- **CVE database**: https://cve.mitre.org/
- **GitHub Dependabot**: Automated monitoring for all dependencies

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
