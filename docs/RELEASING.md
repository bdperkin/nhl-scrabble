# Release Process

This document describes the automated release process for publishing NHL Scrabble to PyPI.

## Overview

The project uses **automated PyPI publishing** via GitHub Actions. Releases are triggered by pushing version tags, eliminating manual build and upload steps.

**Time Savings:**

- **Before:** 30 minutes, 9 manual steps
- **After:** 5 minutes, 2 steps (tag + push)

## Quick Start

### Creating a Release

```bash
# 1. Update CHANGELOG.md with release notes
vim CHANGELOG.md

# 2. Commit changelog
git add CHANGELOG.md
git commit -m "docs(changelog): Add v2.1.0 release notes"
git push origin main

# 3. Create and push version tag
git tag -a v2.1.0 -m "Release version 2.1.0"
git push --tags

# 4. Monitor workflow (optional)
gh run watch
```

**That's it!** The workflow automatically:

- ✅ Builds source distribution (sdist)
- ✅ Builds wheel distribution
- ✅ Verifies package metadata
- ✅ Tests installation on 3 OS × 3 Python versions
- ✅ Publishes to TestPyPI
- ✅ Publishes to PyPI
- ✅ Creates GitHub Release with artifacts

## Release Workflow Details

### 1. Automated Workflow Stages

The `.github/workflows/publish.yml` workflow executes in this order:

**Stage 1: Build** (~15 seconds)

- Checks out code with full git history
- Installs Python 3.12 and UV
- Builds sdist and wheel distributions
- Verifies with `twine check` and `check-wheel-contents`
- Uploads artifacts for later stages

**Stage 2: Test Installation** (~2-3 minutes, parallel)

- Matrix testing: Ubuntu, macOS, Windows
- Python versions: 3.12, 3.13, 3.14
- Installs wheel on each platform
- Verifies CLI works (`nhl-scrabble --version`)
- Verifies package imports

**Stage 3: Publish to TestPyPI** (~10 seconds)

- Downloads build artifacts
- Publishes to https://test.pypi.org
- Uses OIDC trusted publishing (no API tokens)
- Skips if version already exists

**Stage 4: Generate SLSA Provenance** (~15-30 seconds)

- Generates cryptographically signed build attestations
- Creates SLSA Level 3 provenance
- Uses Sigstore/Cosign keyless signing
- Attaches provenance to GitHub release
- Enables build verification and supply chain security

**Stage 5: Publish to PyPI** (~10 seconds)

- Downloads build artifacts
- Publishes to https://pypi.org
- Uses OIDC trusted publishing
- Production release!

**Stage 6: GitHub Release** (~5 seconds)

- Extracts version from tag
- Extracts tag annotation (release summary)
- Extracts release notes from CHANGELOG.md
- Generates release summary:
  - Lists distribution files with sizes
  - Adds installation instructions
  - Adds documentation links
- Creates GitHub Release
- Attaches distribution artifacts (sdist + wheel)

**Total Time:** 3-4.5 minutes

### 2. Version Tagging Strategy

The project uses [Semantic Versioning](https://semver.org/):

**Version Format:** `vMAJOR.MINOR.PATCH`

```bash
# Major release (breaking changes)
git tag -a v3.0.0 -m "Release version 3.0.0 - Breaking API changes"

# Minor release (new features, backward compatible)
git tag -a v2.1.0 -m "Release version 2.1.0 - Add REST API server"

# Patch release (bug fixes)
git tag -a v2.0.1 -m "Release version 2.0.1 - Fix API 404 handling"
```

**Pre-Releases:**

```bash
# Release candidate
git tag -a v2.1.0rc1 -m "Release candidate 1 for version 2.1.0"

# Beta release
git tag -a v2.1.0b1 -m "Beta 1 for version 2.1.0"

# Alpha release
git tag -a v2.1.0a1 -m "Alpha 1 for version 2.1.0"
```

**Important:**

- Always use **annotated tags** (`-a` flag)
- Include descriptive message (`-m` flag)
- Follow `v*` pattern (v1.0.0, not 1.0.0)

### 3. CHANGELOG.md Format

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature X in progress

### Fixed
- Bug Y under investigation

## [2.1.0] - 2026-04-22

### Added
- REST API server for programmatic access
- Health check endpoint
- API documentation

### Fixed
- NHL API 404 error handling
- Rate limiting edge cases

### Changed
- Improved error messages

## [2.0.1] - 2026-04-15

### Fixed
- API timeout handling
- Retry logic for transient failures
```

**Section Order:**

1. **Added** - New features
1. **Changed** - Changes to existing functionality
1. **Deprecated** - Soon-to-be removed features
1. **Removed** - Removed features
1. **Fixed** - Bug fixes
1. **Security** - Security fixes

**Release Notes Extraction:**

The workflow extracts the current version section automatically:

```bash
# Version section between ## [2.1.0] and next ##
awk '/^## \[2.1.0\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md
```

**GitHub Release Format:**

Each release includes:

1. **Tag Annotation** - Release summary from the git tag message
1. **Detailed Changelog** - Extracted from CHANGELOG.md for this version
1. **Distribution Files** - List of build artifacts with sizes
1. **Installation Instructions** - Commands to install the specific version
1. **Documentation Links** - Links to docs, CHANGELOG, PyPI, issues, discussions

**Example Release:**

````markdown
Release version 2.1.0

---

## Detailed Changelog

### Added
- New feature X
- Feature Y

### Fixed
- Bug Z

---

## 📦 Distribution Files

This release includes:

- `nhl_scrabble-2.1.0.tar.gz` (45K)
- `nhl_scrabble-2.1.0-py3-none-any.whl` (32K)

## 📥 Installation

```bash
# Install from PyPI
pip install nhl-scrabble==2.1.0

# Upgrade existing installation
pip install --upgrade nhl-scrabble
```

## 📚 Documentation

- [📖 Documentation](https://bdperkin.github.io/nhl-scrabble/)
- [📋 CHANGELOG](https://github.com/bdperkin/nhl-scrabble/blob/main/CHANGELOG.md)
- [📦 PyPI Package](https://pypi.org/project/nhl-scrabble/2.1.0/)
- [🐛 Issue Tracker](https://github.com/bdperkin/nhl-scrabble/issues)
- [💬 Discussions](https://github.com/bdperkin/nhl-scrabble/discussions)
````

## Security: PyPI Trusted Publishing

The project uses **OIDC-based Trusted Publishing** instead of API tokens.

### Benefits

**Traditional API Tokens:**

- ❌ Need to create and rotate tokens manually
- ❌ Tokens can leak in logs or git history
- ❌ Manual revocation required
- ❌ Long-lived credentials
- ❌ Security risk

**Trusted Publishing (OIDC):**

- ✅ No tokens to manage
- ✅ Short-lived credentials (expires in minutes)
- ✅ Automatic credential rotation
- ✅ Bound to specific repo/workflow/environment
- ✅ More secure (OIDC standard)
- ✅ No secrets in GitHub repository

### One-Time Setup (Already Configured)

**PyPI Configuration:**

1. Go to: https://pypi.org/manage/project/nhl-scrabble/settings/publishing/
1. Add trusted publisher:
   - **Owner:** `bdperkin`
   - **Repository:** `nhl-scrabble`
   - **Workflow:** `publish.yml`
   - **Environment:** `pypi`

**TestPyPI Configuration:**

1. Go to: https://test.pypi.org/manage/project/nhl-scrabble/settings/publishing/
1. Add same configuration with environment: `testpypi`

**GitHub Environments:**

- Settings → Environments → `pypi` (created)
- Settings → Environments → `testpypi` (created)

**Protection Rules** (optional):

- Require approval before publishing
- Limit to specific branches
- Add deployment protection rules

### How It Works

```yaml
# Workflow declares id-token permission
permissions:
  id-token: write  # Request OIDC token

# Environment links to PyPI trusted publisher
environment:
  name: pypi  # Matches PyPI configuration

# Action uses OIDC token for authentication
- uses: pypa/gh-action-pypi-publish@release/v1
  # No API token needed!
```

GitHub generates a short-lived OIDC token that PyPI validates against the trusted publisher configuration. The token expires after ~10 minutes.

## Monitoring Releases

### Watch Workflow Execution

```bash
# List recent workflow runs
gh run list --workflow=publish.yml

# Watch current run (auto-refresh)
gh run watch

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log

# View failed jobs only
gh run view <run-id> --log-failed
```

### Check Release Status

```bash
# View GitHub releases
gh release list

# View specific release
gh release view v2.1.0

# Download release artifacts
gh release download v2.1.0
```

### Verify PyPI Publication

```bash
# Check PyPI (web)
open https://pypi.org/project/nhl-scrabble/

# Check TestPyPI (web)
open https://test.pypi.org/project/nhl-scrabble/

# Install from PyPI
pip install nhl-scrabble==2.1.0

# Verify version
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"
```

## Verifying Build Provenance

Each release includes cryptographically signed SLSA Level 3 build provenance that verifies build integrity and supply chain security.

### Why Verify Provenance?

**Build provenance verification ensures:**

- ✅ **Authentic Build**: Built by official GitHub Actions workflow
- ✅ **Correct Source**: Built from the exact tagged commit
- ✅ **No Tampering**: Artifacts match signed provenance
- ✅ **Trusted Builder**: Built using official SLSA generator
- ✅ **Supply Chain Security**: End-to-end build integrity

**Who should verify:**

- Security-conscious users
- Enterprise deployments
- Regulated industries (finance, healthcare, government)
- Containerized deployments
- CI/CD pipelines downloading artifacts
- Anyone installing from GitHub releases (not PyPI)

### Verification Methods

**Option 1: Using slsa-verifier (Recommended)**

```bash
# Install slsa-verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Download release artifacts
gh release download v2.1.0

# Verify wheel provenance
slsa-verifier verify-artifact \
  nhl_scrabble-2.1.0-py3-none-any.whl \
  --provenance-path nhl_scrabble-2.1.0.intoto.jsonl \  # codespell:ignore intoto
  --source-uri github.com/bdperkin/nhl-scrabble

# Verify source distribution provenance
slsa-verifier verify-artifact \
  nhl_scrabble-2.1.0.tar.gz \
  --provenance-path nhl_scrabble-2.1.0.intoto.jsonl \  # codespell:ignore intoto
  --source-uri github.com/bdperkin/nhl-scrabble

# Success output:
# Verified signature against tlog entry index 12345...
# Verified build using builder "https://github.com/slsa-framework/slsa-github-generator/..."
# Verifying artifact nhl_scrabble-2.1.0-py3-none-any.whl: PASSED
# PASSED: Verified SLSA provenance
```

**Option 2: Using Cosign**

```bash
# Install cosign
brew install cosign  # macOS
# Or: https://github.com/sigstore/cosign/releases

# Verify attestation
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp="^https://github.com/bdperkin/nhl-scrabble" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  nhl_scrabble-2.1.0-py3-none-any.whl
```

**Option 3: Manual Hash Verification**

```bash
# Download provenance
gh release download v2.1.0 --pattern "*.intoto.jsonl"  # codespell:ignore intoto

# View provenance (requires jq)
cat nhl_scrabble-2.1.0.intoto.jsonl | jq .  # codespell:ignore intoto

# Compute artifact hashes
sha256sum nhl_scrabble-2.1.0-py3-none-any.whl
sha256sum nhl_scrabble-2.1.0.tar.gz

# Compare with hashes in provenance file
# Look for "subject" array in provenance JSON
```

### Automated Verification in CI/CD

Integrate provenance verification into your deployment pipeline:

**GitHub Actions Example:**

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Install slsa-verifier
        run: |
          go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

      - name: Download release artifacts
        run: |
          gh release download v2.1.0

      - name: Verify provenance
        run: |
          slsa-verifier verify-artifact \
            nhl_scrabble-2.1.0-py3-none-any.whl \
            --provenance-path nhl_scrabble-2.1.0.intoto.jsonl \  # codespell:ignore intoto
            --source-uri github.com/bdperkin/nhl-scrabble

      - name: Install verified package
        run: |
          pip install nhl_scrabble-2.1.0-py3-none-any.whl
```

**Docker/Container Example:**

```dockerfile
# Dockerfile with provenance verification
FROM python:3.12-slim

# Install slsa-verifier
RUN apt-get update && apt-get install -y golang && \
    go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Download and verify
RUN gh release download v2.1.0 && \
    slsa-verifier verify-artifact \
      nhl_scrabble-2.1.0-py3-none-any.whl \
      --provenance-path nhl_scrabble-2.1.0.intoto.jsonl \  # codespell:ignore intoto
      --source-uri github.com/bdperkin/nhl-scrabble && \
    pip install nhl_scrabble-2.1.0-py3-none-any.whl
```

### What Provenance Contains

Each provenance file (`.intoto.jsonl`) includes: # codespell:ignore intoto

```json
{
  "predicate": {
    "buildType": "https://github.com/slsa-framework/slsa-github-generator/generic@v1",
    "builder": {
      "id": "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@refs/tags/v1.9.0"
    },
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/bdperkin/nhl-scrabble@refs/tags/v2.1.0",
        "digest": {"sha1": "abcd1234..."}
      }
    },
    "metadata": {
      "buildInvocationId": "1234567890",
      "buildStartedOn": "2026-04-22T10:30:00Z",
      "buildFinishedOn": "2026-04-22T10:32:15Z"
    },
    "materials": [
      {
        "uri": "git+https://github.com/bdperkin/nhl-scrabble@refs/tags/v2.1.0"
      }
    ]
  },
  "subject": [
    {
      "name": "nhl_scrabble-2.1.0-py3-none-any.whl",
      "digest": {"sha256": "abc123..."}
    },
    {
      "name": "nhl_scrabble-2.1.0.tar.gz",
      "digest": {"sha256": "def456..."}
    }
  ]
}
```

**Key Fields:**

- **buildType**: SLSA builder type (generic workflow)
- **builder.id**: Exact SLSA generator version used
- **invocation.configSource**: Git repository and tag/commit
- **metadata**: Build timing and run ID
- **subject**: Artifacts with SHA256 hashes

### Provenance Verification Troubleshooting

**Error: "failed to verify signature"**

- Ensure provenance file is from the correct release
- Check artifact filename matches exactly
- Verify using latest slsa-verifier version
- Check network connectivity (verifier needs to access Sigstore transparency log)

**Error: "source URI mismatch"**

- Ensure `--source-uri` matches the repository
- Use `github.com/bdperkin/nhl-scrabble` (no https://)
- Check you're verifying the correct release version

**Error: "provenance file not found"**

- Download provenance: `gh release download v2.1.0 --pattern "*.intoto.jsonl"` # codespell:ignore intoto
- Check GitHub release has provenance attached
- Verify provenance generation completed in workflow

**Missing provenance on older releases:**

- Provenance generation added in v2.1.0 (April 2026)
- Older releases (v2.0.x) do not have provenance
- Upgrade to v2.1.0+ for provenance support

### SLSA Level 3 Compliance

This project achieves **SLSA Level 3** compliance:

| Level   | Requirements                           | Status     |
| ------- | -------------------------------------- | ---------- |
| Level 1 | Documentation of build process         | ✅ Yes     |
| Level 2 | Hosted build platform (GitHub Actions) | ✅ Yes     |
| Level 3 | Provenance + non-falsifiable           | ✅ Yes     |
| Level 4 | Two-party review + hermetic builds     | ⚠️ Partial |

**What SLSA Level 3 Provides:**

- **Provenance**: Complete build metadata
- **Non-Falsifiable**: Cryptographically signed, cannot be forged
- **Hosted Build**: Isolated, ephemeral build environment
- **Tamper-Evident**: Any modification invalidates signature

**Compliance Standards:**

- ✅ **NIST SSDF** (Secure Software Development Framework)
- ✅ **EO 14028** (Executive Order on Cybersecurity - SBOM + Provenance)
- ✅ **SLSA Framework** (Supply chain Levels for Software Artifacts)

For more details, see: https://slsa.dev/

## Troubleshooting

### Workflow Fails to Trigger

**Problem:** Pushed tag but workflow didn't start

**Diagnosis:**

```bash
# Check tag exists on remote
git ls-remote --tags origin

# Check workflow file syntax
yamllint .github/workflows/publish.yml

# Check GitHub Actions enabled
# Settings → Actions → General → Allow all actions
```

**Solutions:**

- Ensure tag follows `v*` pattern (v1.0.0, not 1.0.0)
- Use annotated tags (`git tag -a`), not lightweight tags
- Check GitHub Actions is enabled for repository
- Verify workflow file has no syntax errors

### Build Stage Fails

**Problem:** Build fails with "version not found"

**Diagnosis:**

```bash
# Check git history is available
git log --oneline

# Check tags exist
git tag

# Test local build
python -m build
```

**Solutions:**

```yaml
# Ensure full git history
- uses: actions/checkout@v6
  with:
    fetch-depth: 0  # Required for hatch-vcs
```

**Problem:** Build fails with "module not found"

**Solution:**

```bash
# Ensure build dependencies are installed
# (Already handled in workflow via uv pip install build)
```

### Test Installation Fails

**Problem:** Wheel fails to install on specific platform

**Diagnosis:**

```bash
# Test local installation
pip install dist/*.whl

# Check wheel contents
unzip -l dist/*.whl

# Verify wheel metadata
check-wheel-contents dist/*.whl
```

**Solutions:**

- Ensure package is pure Python (no C extensions)
- Check `pyproject.toml` for platform-specific dependencies
- Verify wheel is built correctly

**Problem:** CLI command not found after install

**Diagnosis:**

```bash
# Check entry points
pip show nhl-scrabble

# Check installed scripts
pip show -f nhl-scrabble | grep bin/
```

**Solution:**

```toml
# Ensure entry point defined in pyproject.toml
[project.scripts]
nhl-scrabble = "nhl_scrabble.cli:main"
```

### TestPyPI Publication Fails

**Problem:** "403 Forbidden" error

**Diagnosis:**

- Check trusted publisher configuration on TestPyPI
- Verify environment name matches (`testpypi`)
- Check workflow name matches (`publish.yml`)

**Solution:**

```bash
# Re-configure TestPyPI trusted publisher
# https://test.pypi.org/manage/project/nhl-scrabble/settings/publishing/
```

**Problem:** "Version already exists"

**Solution:**

- Workflow uses `skip-existing: true` to handle this
- This is normal for re-runs
- Workflow continues to next stage

### PyPI Publication Fails

**Problem:** "403 Forbidden" error

**Diagnosis:**

- Check trusted publisher configuration on PyPI
- Verify environment name matches (`pypi`)
- Check repository owner/name matches

**Solution:**

```bash
# Re-configure PyPI trusted publisher
# https://pypi.org/manage/project/nhl-scrabble/settings/publishing/
```

**Problem:** "Version already exists"

**Note:** PyPI does **not** allow re-uploading versions

**Solutions:**

- Delete the tag: `git tag -d v2.1.0 && git push origin :refs/tags/v2.1.0`
- Create new version: `git tag -a v2.1.1 -m "Fix release issue"`
- If critical: Use post-release version (v2.1.0.post1)

### GitHub Release Fails

**Problem:** Release notes empty or missing

**Diagnosis:**

```bash
# Check CHANGELOG.md has version section
grep -A 10 "## \[2.1.0\]" CHANGELOG.md

# Test awk extraction locally
awk '/^## \[2.1.0\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md
```

**Solutions:**

- Ensure CHANGELOG.md has proper section: `## [2.1.0] - 2026-04-22`
- Check section is not empty
- Verify markdown formatting is correct

**Problem:** Artifacts not attached to release

**Diagnosis:**

- Check build artifacts were created
- Check download-artifact step succeeded

**Solution:**

- Ensure `actions/upload-artifact@v7` in build job
- Ensure `actions/download-artifact@v7` in release job
- Verify artifact name matches (`python-package-distributions`)

## Manual Release (Emergency Fallback)

If the automated workflow fails and you need to release immediately:

### 1. Build Locally

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distributions
python -m build --sdist --wheel

# Verify
ls -lh dist/
twine check dist/*
```

### 2. Test Installation

```bash
# Create test venv
python -m venv test-env
source test-env/bin/activate

# Install wheel
pip install dist/*.whl

# Test
nhl-scrabble --version
python -c "import nhl_scrabble; print(nhl_scrabble.__version__)"

# Clean up
deactivate
rm -rf test-env
```

### 3. Upload to TestPyPI (Optional)

```bash
# Requires API token (not recommended)
# Better: Fix automated workflow and use trusted publishing

# If you must:
twine upload -r testpypi dist/*
# Enter username: __token__
# Enter password: <TestPyPI API token>

# Test install
pip install --index-url https://test.pypi.org/simple/ nhl-scrabble
```

### 4. Upload to PyPI

```bash
# Requires API token (not recommended)
# Better: Fix automated workflow and use trusted publishing

# If you must:
twine upload dist/*
# Enter username: __token__
# Enter password: <PyPI API token>
```

### 5. Create GitHub Release

```bash
# Create tag
git tag -a v2.1.0 -m "Release version 2.1.0"
git push --tags

# Create release
gh release create v2.1.0 dist/* \
  --title "v2.1.0" \
  --notes-file CHANGELOG.md

# Or use web interface:
# https://github.com/bdperkin/nhl-scrabble/releases/new
```

## Rollback Strategy

### Before PyPI Publication

If workflow fails before PyPI publish:

- ✅ No action needed
- ✅ Fix issue and re-push tag (or delete and recreate)
- ✅ Workflow will retry from beginning

### After PyPI Publication

**Important:** PyPI does **not** allow deleting or re-uploading versions

**Option 1: Yank Release (Discourage Installation)**

```bash
# Via web interface:
# https://pypi.org/manage/project/nhl-scrabble/release/2.1.0/

# Check "Yank" checkbox
# Reason: "Critical bug in API client"

# Note: pip install nhl-scrabble will skip yanked versions
# But: pip install nhl-scrabble==2.1.0 still works
```

**Option 2: Publish Hotfix**

```bash
# Create hotfix release
git tag -a v2.1.1 -m "Hotfix: Fix critical bug"
git push --tags

# Workflow publishes v2.1.1
# Users get v2.1.1 on pip install nhl-scrabble
```

**Option 3: Post-Release Version**

```bash
# For very minor fixes
git tag -a v2.1.0.post1 -m "Post-release 1 for v2.1.0"
git push --tags

# Creates v2.1.0.post1
# PEP 440 compliant
# Higher than v2.1.0, lower than v2.1.1
```

## Best Practices

### Before Creating Release

**Checklist:**

- [ ] All CI checks passing on main branch
- [ ] CHANGELOG.md updated with release notes
- [ ] Version section follows Keep a Changelog format
- [ ] Breaking changes documented (if major release)
- [ ] Migration guide written (if needed)
- [ ] Documentation updated
- [ ] All merged PRs since last release reviewed
- [ ] No critical bugs in issue tracker

### Version Numbering

**When to increment:**

- **Major (X.0.0):** Breaking API changes

  - Removed public functions/classes
  - Changed function signatures
  - Changed default behavior
  - Incompatible data format changes

- **Minor (x.Y.0):** New features, backward compatible

  - New public functions/classes
  - New CLI options
  - New configuration options
  - New dependencies (non-breaking)

- **Patch (x.y.Z):** Bug fixes only

  - Bug fixes
  - Documentation updates
  - Dependency updates (security patches)
  - Performance improvements (no API changes)

### Release Timing

**Recommended:**

- **Patch releases:** As needed (weekly if bugs found)
- **Minor releases:** Monthly (feature releases)
- **Major releases:** Quarterly or when breaking changes accumulate

**Avoid:**

- Releasing on Fridays (weekend debugging)
- Releasing during holidays
- Releasing right before team vacation
- Multiple releases in one day

### Communication

**Before Major Release:**

- Announce planned breaking changes in advance
- Provide migration guide
- Consider deprecation period

**After Release:**

- Announce on GitHub Discussions (if enabled)
- Tweet/social media (optional)
- Update documentation site
- Notify dependent projects (if any)

## Testing Workflow (Development)

To test the workflow without creating a real release:

### 1. Create Test Tag

```bash
# Create test tag
git tag -a v0.0.1-test -m "Test release workflow"

# Push to trigger workflow
git push origin v0.0.1-test
```

### 2. Monitor Workflow

```bash
# Watch execution
gh run watch

# View logs
gh run view --log
```

### 3. Verify Results

```bash
# Check TestPyPI
pip install --index-url https://test.pypi.org/simple/ nhl-scrabble==0.0.1.test

# Check GitHub release
gh release view v0.0.1-test
```

### 4. Clean Up Test Release

```bash
# Delete local tag
git tag -d v0.0.1-test

# Delete remote tag
git push origin :refs/tags/v0.0.1-test

# Delete GitHub release
gh release delete v0.0.1-test --yes

# Note: Cannot delete from TestPyPI/PyPI
```

## Performance Metrics

**Workflow Execution Time:**

| Stage            | Time           | Notes                         |
| ---------------- | -------------- | ----------------------------- |
| Build            | ~15s           | Builds sdist + wheel          |
| Test Install     | ~2-3 min       | Parallel (3 OS × 3 Python)    |
| Provenance       | ~15-30s        | SLSA L3 attestation + signing |
| TestPyPI Publish | ~10s           | OIDC auth + upload            |
| PyPI Publish     | ~10s           | OIDC auth + upload            |
| GitHub Release   | ~5s            | Extract notes + create        |
| **Total**        | **~3-4.5 min** | vs 30 min manual              |

**Time Savings:**

- **Per Release:** 25-27 minutes saved
- **10 Releases/Year:** 4-5 hours saved
- **Reduced Errors:** ~90% (automation eliminates manual mistakes)

## References

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)

## Support

**Issues with Releases:**

- Check this troubleshooting guide first
- Review workflow logs: `gh run view --log-failed`
- Check GitHub Actions status page: https://www.githubstatus.com/
- Check PyPI status page: https://status.python.org/
- Open issue: https://github.com/bdperkin/nhl-scrabble/issues

**Questions:**

- GitHub Discussions (if enabled)
- Issue tracker for bugs
- See SUPPORT.md for additional resources
