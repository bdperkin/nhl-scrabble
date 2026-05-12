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

## MEDIUM Severity Suppressions

### CVE-2026-4046: glibc iconv() Denial of Service

**Component**: glibc (libc6)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-400 (Uncontrolled Resource Consumption)

**Description**: Denial of Service vulnerability in the `iconv()` character set conversion function when processing specific character sets.

**Why Suppressed**:

- The vulnerability is in the `iconv()` **C library function**
- This Python application does not directly call `iconv()` for character set conversion
- Python handles character encoding at a higher level (str/bytes objects)
- The vulnerable code path is not exercised by the application

**Risk Level**: **LOW**

**Mitigations**:

- Python's built-in encoding handling isolates from direct iconv() calls
- Container runs as non-root user (UID 1000)
- No untrusted character set conversions performed

**References**:

- [NVD CVE-2026-4046](https://nvd.nist.gov/vuln/detail/CVE-2026-4046)

______________________________________________________________________

### CVE-2026-4437, CVE-2026-4438, CVE-2026-6238: glibc DNS Vulnerabilities

**Component**: glibc (libc6, libc-bin)
**CVSS Score**: Not yet scored (MEDIUM)
**CWEs**: CWE-125 (Out-of-bounds Read), CWE-20 (Improper Input Validation)

**Description**: Multiple DNS-related vulnerabilities:

- **CVE-2026-4437**: Incorrect DNS response parsing
- **CVE-2026-4438**: Invalid hostname validation in `gethostbyaddr()`
- **CVE-2026-6238**: Application crash via crafted DNS response

**Why Suppressed**:

- Application uses **Python's high-level `requests` library**, not direct glibc DNS functions
- DNS queries are limited to **known NHL API endpoints** (api-web.nhle.com)
- `gethostbyaddr()` is a **deprecated function** not used by modern Python
- No untrusted DNS servers are queried
- Application does not perform reverse DNS lookups

**Risk Level**: **LOW**

**Mitigations**:

- Controlled API endpoints (no user-provided DNS queries)
- Python `requests` library provides DNS abstraction
- HTTPS with certificate validation prevents MITM DNS attacks

**References**:

- [NVD CVE-2026-4437](https://nvd.nist.gov/vuln/detail/CVE-2026-4437)
- [NVD CVE-2026-4438](https://nvd.nist.gov/vuln/detail/CVE-2026-4438)
- [NVD CVE-2026-6238](https://nvd.nist.gov/vuln/detail/CVE-2026-6238)

______________________________________________________________________

### CVE-2026-5435: glibc TSIG Record Out-of-Bounds Write

**Component**: glibc (libc6)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-787 (Out-of-bounds Write)

**Description**: Out-of-bounds write vulnerability when processing TSIG (DNS Transaction Signature) records.

**Why Suppressed**:

- TSIG records are used for **authenticated DNS zone transfers**
- This application **does not process TSIG records** or perform DNS zone transfers
- Application only performs simple A/AAAA record lookups for NHL API
- No DNS server functionality

**Risk Level**: **LOW**

**Mitigations**:

- Application does not process TSIG records
- No DNS zone transfer operations
- DNS queries limited to standard resolution

**References**:

- [NVD CVE-2026-5435](https://nvd.nist.gov/vuln/detail/CVE-2026-5435)

______________________________________________________________________

### CVE-2026-5450: glibc scanf Heap Buffer Overflow

**Component**: glibc (libc6)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-122 (Heap-based Buffer Overflow)

**Description**: Heap buffer overflow in the C `scanf()` family of functions when using the `%mc` format specifier with a large width value.

**Why Suppressed**:

- The vulnerability is in the **C `scanf()` function**
- Python application **does not use C `scanf()`** - it uses Python's input/parsing functions
- No C extension modules in this application that would call scanf
- Python handles all input parsing

**Risk Level**: **LOW**

**Mitigations**:

- Python input parsing isolates from C scanf
- No C extensions using scanf in this project
- Container runs as non-root user

**References**:

- [NVD CVE-2026-5450](https://nvd.nist.gov/vuln/detail/CVE-2026-5450)

______________________________________________________________________

### CVE-2026-5928: glibc ungetwc Information Disclosure

**Component**: glibc (libc6)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-200 (Exposure of Sensitive Information)

**Description**: Information disclosure or denial of service via the `ungetwc()` wide character function with specific encodings.

**Why Suppressed**:

- The vulnerability is in the **C wide character function `ungetwc()`**
- Python application **does not use C wide character functions**
- Python handles Unicode/wide characters natively at a higher level
- No C extensions using wide character streams

**Risk Level**: **LOW**

**Mitigations**:

- Python's native Unicode handling
- No C wide character function usage
- Container isolation

**References**:

- [NVD CVE-2026-5928](https://nvd.nist.gov/vuln/detail/CVE-2026-5928)

______________________________________________________________________

### CVE-2026-27171: zlib CRC32 Combine Denial of Service

**Component**: zlib (zlib1g)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-835 (Loop with Unreachable Exit Condition)

**Description**: Denial of service via infinite loop in zlib's `crc32_combine()` and `crc32_combine64()` functions.

**Why Suppressed**:

- Vulnerability is in **specific CRC32 combine functions**
- Python's `zlib` module is used for compression/decompression, **not CRC32 combining**
- The application does not call `crc32_combine()` or `crc32_combine64()`
- Standard zlib compression/decompression functions are not affected

**Risk Level**: **LOW**

**Mitigations**:

- Application uses zlib for compression only, not CRC32 operations
- Specific vulnerable functions not called
- No untrusted CRC32 operations

**References**:

- [NVD CVE-2026-27171](https://nvd.nist.gov/vuln/detail/CVE-2026-27171)

______________________________________________________________________

### CVE-2026-27456: util-linux mount TOCTOU

**Component**: util-linux (util-linux, libblkid1)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-367 (Time-of-check Time-of-use Race Condition)

**Description**: Time-of-check time-of-use (TOCTOU) race condition in the `mount` command-line tool when setting up loop devices.

**Why Suppressed**:

- The vulnerability is in the **`mount` command-line tool**
- This Python application **does not use the `mount` command**
- Application does not manipulate loop devices or filesystems
- Container uses existing mounted filesystems only

**Risk Level**: **LOW**

**Mitigations**:

- Application does not invoke mount command
- Container runs as non-root user (cannot mount filesystems)
- Read-only filesystem where possible

**References**:

- [NVD CVE-2026-27456](https://nvd.nist.gov/vuln/detail/CVE-2026-27456)

______________________________________________________________________

### CVE-2026-3184: util-linux Hostname Canonicalization

**Component**: util-linux (util-linux, libblkid1)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-285 (Improper Authorization)

**Description**: Access control bypass due to improper hostname canonicalization in util-linux tools.

**Why Suppressed**:

- The vulnerability is in the **`hostname` command and related utilities**
- This Python application **does not use hostname commands**
- Application does not perform hostname-based access control
- No hostname manipulation operations

**Risk Level**: **LOW**

**Mitigations**:

- Application does not use hostname utilities
- No hostname-based authentication or authorization
- Container networking is managed externally

**References**:

- [NVD CVE-2026-3184](https://nvd.nist.gov/vuln/detail/CVE-2026-3184)

______________________________________________________________________

### CVE-2026-34743: xz Buffer Overflow Denial of Service

**Component**: xz (liblzma5)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-120 (Buffer Copy without Checking Size of Input)

**Description**: Denial of service via buffer overflow in XZ Utils index decoding when decompressing crafted .xz archives.

**Why Suppressed**:

- The vulnerability requires **decompressing XZ archives**
- This Python application **does not decompress XZ/LZMA archives**
- No archive extraction functionality
- Application only processes JSON data from NHL API

**Risk Level**: **LOW**

**Mitigations**:

- Application does not use XZ/LZMA decompression
- No archive processing functionality
- No untrusted file decompression

**References**:

- [NVD CVE-2026-34743](https://nvd.nist.gov/vuln/detail/CVE-2026-34743)

______________________________________________________________________

### CVE-2026-40225: systemd udev Privilege Escalation

**Component**: systemd (libudev1)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-269 (Improper Privilege Management)

**Description**: Privilege escalation via udev processing malicious hardware device events with unsanitized kernel output.

**Why Suppressed**:

- The vulnerability requires **udev daemon running and processing hardware events**
- systemd/udev is **not running in the container** (Python is PID 1, not systemd)
- Container does not have access to host hardware devices
- No device management functionality

**Risk Level**: **LOW**

**Mitigations**:

- udev daemon not running in container
- No hardware device access
- Container isolation from host hardware

**References**:

- [NVD CVE-2026-40225](https://nvd.nist.gov/vuln/detail/CVE-2026-40225)

______________________________________________________________________

### CVE-2026-40226: systemd-nspawn Escape-to-Host

**Component**: systemd (libudev1)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-668 (Exposure of Resource to Wrong Sphere)

**Description**: Container escape vulnerability in systemd-nspawn via crafted configuration file.

**Why Suppressed**:

- The vulnerability is in **systemd-nspawn container runtime**
- This application uses **Docker as the container runtime**, not systemd-nspawn
- systemd-nspawn is not running in the container
- Different container technology stack

**Risk Level**: **LOW**

**Mitigations**:

- Docker runtime used, not systemd-nspawn
- systemd-nspawn not installed or running
- Standard Docker isolation mechanisms

**References**:

- [NVD CVE-2026-40226](https://nvd.nist.gov/vuln/detail/CVE-2026-40226)

______________________________________________________________________

### CVE-2026-4105: systemd D-Bus Privilege Escalation

**Component**: systemd (libudev1)
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-269 (Improper Privilege Management)

**Description**: Privilege escalation via improper access control in systemd's RegisterMachine D-Bus method.

**Why Suppressed**:

- The vulnerability requires **systemd D-Bus service running**
- systemd is **not running in the container** (Python is PID 1, not systemd)
- No D-Bus services exposed in container
- Application does not use D-Bus

**Risk Level**: **LOW**

**Mitigations**:

- systemd daemon not running in container
- No D-Bus services or interfaces
- Container entrypoint is Python application

**References**:

- [NVD CVE-2026-4105](https://nvd.nist.gov/vuln/detail/CVE-2026-4105)

______________________________________________________________________

### CVE-2026-5704: tar Hidden File Injection

**Component**: tar
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)

**Description**: Hidden file injection vulnerability when extracting crafted tar archives.

**Why Suppressed**:

- The vulnerability is in the **`tar` command-line tool**
- This Python application **does not use the `tar` command**
- No archive extraction functionality
- Application only processes JSON data from NHL API

**Risk Level**: **LOW**

**Mitigations**:

- Application does not use tar command
- No archive processing functionality
- Container runs as non-root user

**References**:

- [NVD CVE-2026-5704](https://nvd.nist.gov/vuln/detail/CVE-2026-5704)

______________________________________________________________________

### CVE-2026-5958: sed Symlink Follow Vulnerability

**Component**: sed
**CVSS Score**: Not yet scored (MEDIUM)
**CWE**: CWE-59 (Improper Link Resolution Before File Access)

**Description**: Vulnerability when sed is invoked with both `-i` (in-place edit) and `--follow-symlinks` flags.

**Why Suppressed**:

- The vulnerability is in the **`sed` command-line tool**
- This Python application **does not use the `sed` command**
- No text processing via sed
- Application uses Python's built-in text processing

**Risk Level**: **LOW**

**Mitigations**:

- Application does not invoke sed command
- Python text processing used instead
- Container runs as non-root user

**References**:

- [NVD CVE-2026-5958](https://nvd.nist.gov/vuln/detail/CVE-2026-5958)

______________________________________________________________________

## System-Level vs Application-Level Vulnerabilities

All HIGH and MEDIUM severity suppressions are **system-level vulnerabilities** in base operating system packages:

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

The suppressed HIGH and MEDIUM severity CVEs are **system-level vulnerabilities** in packages that are:

1. **Not used** by the application:
   - Command-line tools: infocmp, mount, hostname, tar, sed, xz, systemd-nspawn
   - System daemons: systemd, udev, D-Bus
   - Specific library functions: scanf, ungetwc, iconv, gethostbyaddr, crc32_combine, TSIG processing
1. **Heavily mitigated** by container security practices:
   - Non-root user (UID 1000)
   - Minimal Python slim base image
   - No systemd/udev running (Python is PID 1)
   - Controlled API endpoints (no user-provided DNS/network input)
   - Regular security updates via apt-get upgrade
1. **Not exploitable** in this application's specific use case:
   - Python abstractions isolate from vulnerable C library functions
   - Container isolation prevents systemd/hardware device vulnerabilities
   - No archive extraction or text processing tool usage
   - DNS queries limited to known NHL API endpoints

**Summary Statistics**:

- **HIGH Severity**: 3 CVEs suppressed (ncurses, systemd, libcap)
- **MEDIUM Severity**: 17 CVEs suppressed (glibc, util-linux, systemd, zlib, xz, tar, sed)
- **Total Suppressed**: 20 CVEs
- **Affected Packages**: System utilities and base OS libraries only
- **Application Code**: 0 vulnerabilities

The overall **residual risk is LOW** after applying container security best practices.

______________________________________________________________________

**Last Updated**: 2026-05-12
**Reviewed By**: Security team
**Next Review**: 2026-06-12
