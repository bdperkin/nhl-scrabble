# Trivy Security Scan Suppressions

This document explains the security vulnerabilities that have been suppressed in Trivy scans and the justification for each suppression.

## Overview

The `.trivyignore` file in the repository root contains CVE suppressions for vulnerabilities that have been assessed and determined to be **not applicable** or **low risk** for this application's specific use case.

## Risk Assessment Criteria

Each suppressed CVE has been evaluated based on:

1. **Applicability**: Does the vulnerability affect code paths used by this application?
1. **Exploitability**: Can the vulnerability be exploited in the container environment?
1. **Impact**: What is the potential impact if exploited?
1. **Mitigation**: What security controls are in place to reduce risk?

## HIGH Severity Suppressions

### CVE-2025-69720: ncurses Buffer Overflow

**Component**: ncurses (libncursesw6, libtinfo6, ncurses-base, ncurses-bin)
**CVSS Score**: 7.8 (HIGH)
**CWE**: CWE-121 (Stack-based Buffer Overflow)

**Description**: Stack-based buffer overflow in the `infocmp` command-line tool's `analyze_string` function.

**Why Suppressed**:

- The vulnerability is in the `infocmp` **command-line tool**, not the ncurses library itself
- This Python application does not execute or use the `infocmp` tool
- The ncurses library functions (used by Python's terminal handling) are **not affected**
- The vulnerable code path is never exercised by this application

**Risk Level**: **LOW**

**Mitigations**:

- Container runs as non-root user (UID 1000)
- Application does not invoke shell commands that could trigger infocmp
- Read-only filesystem where possible

**References**:

- [NVD CVE-2025-69720](https://nvd.nist.gov/vuln/detail/CVE-2025-69720)
- [GitHub Security Advisory](https://github.com/Cao-Wuhui/CVE-2025-69720)

______________________________________________________________________

### CVE-2026-29111: systemd IPC API Code Execution

**Component**: systemd (libsystemd0, libudev1)
**CVSS Score**: 7.8 (HIGH)
**CWE**: CWE-269 (Improper Privilege Management)

**Description**: systemd (as PID 1) can be exploited via malicious IPC API calls with spurious data, leading to arbitrary code execution or DoS.

**Why Suppressed**:

- The vulnerability requires systemd to be **running as PID 1**
- Docker containers do **not run systemd as PID 1**
- This application uses **Python as the entrypoint** (PID 1), not systemd
- While systemd libraries (libsystemd0, libudev1) are present in the base image, the systemd daemon itself is **not running**
- The vulnerable code path (IPC API handling in systemd daemon) is never executed

**Risk Level**: **LOW**

**Mitigations**:

- systemd daemon not running in container
- Container entrypoint is Python application, not systemd
- No systemd services or IPC interfaces exposed

**References**:

- [NVD CVE-2026-29111](https://nvd.nist.gov/vuln/detail/CVE-2026-29111)
- [GitHub Security Advisory GHSA-gx6q-6f99-m764](https://github.com/systemd/systemd/security/advisories/GHSA-gx6q-6f99-m764)

______________________________________________________________________

### CVE-2026-4878: libcap TOCTOU Privilege Escalation

**Component**: libcap2
**CVSS Score**: 7.0 (HIGH)
**CWE**: CWE-367 (Time-of-check Time-of-use Race Condition)

**Description**: Local privilege escalation via TOCTOU race condition in `cap_set_file()`, allowing capabilities to be injected into or stripped from unintended executables.

**Why Suppressed**:

- The vulnerability requires **write access to a parent directory**
- Requires winning a specific **race condition** timing window
- This application **does not use file capabilities** or the `cap_set_file()` function
- Application runs as **non-root user** with limited filesystem permissions
- The vulnerable functionality (setting file capabilities) is not used by the application

**Risk Level**: **LOW**

**Mitigations**:

- Application runs as non-root user (UID 1000)
- Limited filesystem write permissions
- Read-only filesystem for application code
- File capabilities feature not used by application

**References**:

- [NVD CVE-2026-4878](https://nvd.nist.gov/vuln/detail/CVE-2026-4878)
- [GitHub Security Advisory GHSA-f78v-p5hx-m7hh](https://github.com/AndrewGMorgan/libcap_mirror/security/advisories/GHSA-f78v-p5hx-m7hh)

______________________________________________________________________

## System-Level vs Application-Level Vulnerabilities

All HIGH severity suppressions are **system-level vulnerabilities** in base operating system packages:

| Package Type         | Examples                      | Fixable by Application?          |
| -------------------- | ----------------------------- | -------------------------------- |
| **System utilities** | tar, util-linux, ncurses-bin  | ❌ No - requires OS updates      |
| **System libraries** | libcap2, libsystemd0, zlib1g  | ❌ No - requires OS updates      |
| **System daemons**   | systemd                       | ❌ No - not running in container |
| **Application code** | nhl-scrabble, Python packages | ✅ Yes - direct control          |

**Key Point**: These vulnerabilities exist in the **Debian base image**, not in the application code we control.

## Container Security Best Practices

This container follows security best practices to minimize overall risk:

### 1. Minimal Base Image

- Uses `python:3.12-slim` (Debian-based minimal image)
- Only essential packages installed
- Reduces attack surface

### 2. Non-Root User

```dockerfile
USER nhlscrabble  # UID 1000
```

- Limits privilege escalation impact
- Reduces filesystem access
- Standard security practice

### 3. Regular Updates

```dockerfile
RUN apt-get update && apt-get upgrade -y
```

- Automatically pulls latest security patches
- Applied on every build

### 4. Multi-Stage Build

- Builder stage separate from runtime
- Build tools not in final image
- Smaller attack surface

### 5. Health Checks

- Application-level health monitoring
- Quick detection of failures

## Monitoring and Review Process

### Continuous Monitoring

- Trivy scans run on every Docker build (via GitHub Actions)
- Results uploaded to GitHub Security / Code Scanning
- New vulnerabilities automatically detected

### Review Schedule

- **Weekly**: Review new Trivy findings
- **Monthly**: Re-assess suppressed CVEs
- **On base image update**: Validate suppressions still apply

### When to Un-Suppress

Suppressions should be removed when:

1. Debian releases updated packages that fix the CVE
1. Application usage patterns change (e.g., starts using systemd)
1. New information shows the vulnerability is more exploitable than assessed
1. The CVE is backported to the stable Debian release

## Upstream Tracking

Monitor these sources for security updates:

- [Debian Security Tracker](https://security-tracker.debian.org/tracker/)
- [Python Docker Official Images](https://github.com/docker-library/python)
- [Trivy Vulnerability Database](https://github.com/aquasecurity/trivy-db)

## Alternative Mitigation Strategies Considered

### ❌ Switch to Alpine Linux

- **Pros**: Smaller base image, different package ecosystem
- **Cons**:
  - musl libc incompatibility issues with some Python packages
  - Fewer security patches compared to Debian
  - Build complexity increases

### ❌ Use Distroless Images

- **Pros**: Minimal attack surface, no package manager
- **Cons**:
  - Cannot run `apt-get upgrade` for security patches
  - Debugging more difficult
  - Must rebuild entire image for any update

### ✅ Current Approach: Debian Slim + Documented Suppressions

- **Pros**:
  - Well-maintained security updates
  - Ability to patch packages
  - Standard Python compatibility
  - Clear risk assessment and documentation
- **Cons**:
  - Larger image size than Alpine/distroless
  - More packages = larger scan surface

## Conclusion

The suppressed HIGH severity CVEs are **system-level vulnerabilities** in packages that are:

1. **Not used** by the application (infocmp tool, systemd daemon)
1. **Heavily mitigated** by container security practices (non-root user, minimal image)
1. **Not exploitable** in this application's specific use case

The overall **residual risk is LOW** after applying container security best practices.

______________________________________________________________________

**Last Updated**: 2026-05-11
**Reviewed By**: Security team
**Next Review**: 2026-06-11
